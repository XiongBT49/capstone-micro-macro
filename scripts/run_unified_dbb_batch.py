"""Prepare paired inputs for all cases and run selected cases from the frozen manifest."""
import argparse
import csv
import hashlib
import json
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

from integration.benchmark_lifecycle_batch import supported
from integration.bootstrap import enable_gba_imports
from integration.catalog import SharedCatalog


def prepare(directory):
    inputs = directory / "inputs"
    inputs.mkdir(parents=True, exist_ok=False)
    catalog = SharedCatalog(directory / "catalog.sqlite")
    catalog.import_inputs()
    enable_gba_imports()
    records = []
    for source in catalog.list_projects():
        case = source["case_id"]
        baseline = supported(source)
        data = catalog.scenario(case, unified_dbb=not baseline)
        data.macro_request(120, 42)
        project = data.projects[case]
        raw = json.dumps(data.payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
        (inputs / f"{case}.json").write_bytes(raw)
        records.append(dict(case_id=case, source_location=source["location"], source_type=source["project_type"],
                            source_mode=source["delivery_mode"], scenario_mode=project["delivery_mode"],
                            scenario_type=project["project_type"], scenario_region=project["region"],
                            currency=project["currency"], initial_sha256=hashlib.sha256(raw).hexdigest(),
                            cohort="validated_scope" if baseline else "standardized_scenario"))
    with (directory / "manifest.csv").open("x", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)


def run_arm(directory, row, arm):
    case = row["case_id"]
    source = directory / "inputs" / f"{case}.json"
    if hashlib.sha256(source.read_bytes()).hexdigest() != row["initial_sha256"]:
        raise ValueError(f"Frozen scenario changed for {case}")
    out = directory / "live" / case / arm
    if (out / "status.json").exists():
        return (case, arm, json.loads((out / "status.json").read_text(encoding="utf-8"))["status"])
    out.mkdir(parents=True, exist_ok=False)
    with TemporaryDirectory(prefix=f"{case}-{arm}-", dir=directory) as tmp:
        db = Path(tmp) / "macro.sqlite"
        vendor = enable_gba_imports()
        shutil.copyfile(vendor / "data/processed/agent_database.sqlite", db)
        with (out / "console.log").open("xb") as log:
            result = subprocess.run([sys.executable, "-m", "scripts.run_unified_dbb_batch", str(directory),
                                     "--worker", case, arm, str(db)], stdout=log, stderr=subprocess.STDOUT)
    return (case, arm, result.returncode)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--prepare", action="store_true")
    modes.add_argument("--cases", nargs="+", help="Explicit case IDs, or 'remaining' for the standardized cohort")
    modes.add_argument("--worker", nargs=3, help=argparse.SUPPRESS)
    parser.add_argument("--parallel", type=int, default=4)
    args = parser.parse_args()
    directory = args.directory.resolve()
    if args.prepare:
        prepare(directory)
        return
    if args.worker:
        case, arm, scratch = args.worker
        enable_gba_imports()
        from gba_construction_sim.backend.storage import agent_database as storage
        storage.agent_database = storage.AgentDatabase(db_path=Path(scratch))
        from scripts.run_e2e_case import main as run_case
        sys.argv = ["run_e2e_case", "--case", case, "--organization-mode", arm, "--profile", "full",
                    "--initial-input", str(directory / "inputs" / f"{case}.json"),
                    "--database", str(directory / "catalog.sqlite"), "--output", str(directory / "live" / case / arm)]
        run_case()
        return
    from src.llm_client import load_env_file
    load_env_file(Path(__file__).resolve().parents[2] / ".env")
    if os.getenv("LLM_PROVIDER") != "deepseek" or os.getenv("DEEPSEEK_MODEL") != "deepseek-flash":
        raise ValueError("Paired study requires the configured deepseek-flash model")
    os.environ.setdefault("LLM_TIMEOUT", "180")
    os.environ["PYTHONUTF8"] = "1"
    with (directory / "manifest.csv").open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    if args.cases == ["remaining"]:
        selected = [r for r in rows if r["cohort"] == "standardized_scenario"]
    else:
        selected = [r for r in rows if r["case_id"] in args.cases]
        if {r["case_id"] for r in selected} != set(args.cases):
            raise ValueError("Unknown case in batch request")
    with ThreadPoolExecutor(max_workers=args.parallel) as workers:
        # Schedule one pair at a time per available pair slot. Finish running arms
        # when a pair hits a technical error and retain every partial result.
        for offset in range(0, len(selected), max(1, args.parallel // 2)):
            block = selected[offset:offset + max(1, args.parallel // 2)]
            pending = [workers.submit(run_arm, directory, row, arm) for row in block for arm in ("single", "multi")]
            outcomes = [job.result() for job in pending]
            print(json.dumps(outcomes), flush=True)
            for case, arm, _ in outcomes:
                state = json.loads((directory / "live" / case / arm / "status.json").read_text(encoding="utf-8"))
                if state["status"] not in {"completed", "business_stopped", "tick_limit"}:
                    raise SystemExit(f"Technical interruption in {case}/{arm}: {state['status']}")


if __name__ == "__main__":
    main()
