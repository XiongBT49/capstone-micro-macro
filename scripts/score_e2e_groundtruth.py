"""Compare finished procurement contracts against historical case-role-company links."""
import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

from integration.catalog import DEFAULT_SOURCE


HISTORICAL_ROLE = {
    "design": "设计",
    "construction": "施工/总承包",
    "cost_consulting": "造价/工料测量",
    "supply": "供应/制造",
}


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def observed_contracts(path):
    status = read(path / "status.json")
    if status["status"] != "completed" or any(p["stage"] != "closed" for p in status["projects"]):
        raise ValueError(f"Incomplete run: {path}")
    packages = read(path / "shared_input.json")["packages"]
    outcomes = defaultdict(dict)
    simulation = read(path / "result.json")["simulation"]
    events = {e["data"]["package_id"]: e["data"]
              for project in simulation["project_results"] for e in project["event_log"]
              if e["event_type"] == "package_contract_committed"}
    for package in packages:
        key = package["package_id"]
        outcomes[HISTORICAL_ROLE[package["kind"]]][key] = {
            "candidates": package["candidate_ids"],
            "signed_members": events.get(key, {}).get("members", []),
            "price": events.get(key, {}).get("price"),
            "currency": package["currency"],
        }
    return (status["settings"]["case_id"], status["live_switches"]["organization_mode"]), outcomes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, nargs="+", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    predictions = {}
    for path in args.run:
        key, data = observed_contracts(path)
        if key in predictions:
            raise ValueError(f"Multiple runs for the same case and arm: {key}")
        predictions[key] = data
    truth = DEFAULT_SOURCE / "hidden_benchmark_project_enterprises.csv"
    with truth.open(encoding="utf-8-sig", newline="") as f:
        labels = list(csv.DictReader(f))
    rows = []
    for line, label in enumerate(labels, start=2):
        for arm in ("single", "multi"):
            key = (label["case_id"], arm)
            role = label["company_role_original"]
            contracts = predictions.get(key, {}).get(role, {})
            company = label["company_id"]
            candidates = [k for k,v in contracts.items() if company in v["candidates"]]
            awards = [k for k,v in contracts.items() if company in v["signed_members"]]
            if key not in predictions:
                status = "awaiting_completed_run"
            elif not role or not company:
                status = "missing_role_or_company"
            elif not contracts:
                status = "no_comparable_package_role"
            elif awards:
                status = "historical_company_signed"
            elif candidates:
                status = "historical_candidate_did_not_sign"
            else:
                status = "historical_company_outside_candidate_pool"
            rows.append({**label, "truth_source_line": line, "arm": arm, "comparison_status": status,
                         "matching_candidate_packages": "|".join(candidates),
                         "matching_signed_packages": "|".join(awards),
                         "simulated_contracts_for_role": json.dumps(contracts, ensure_ascii=False)})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(".tmp")
    with temporary.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(args.output)


if __name__ == "__main__":
    main()
