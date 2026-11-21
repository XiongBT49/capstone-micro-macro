import asyncio
import hashlib
import json
import os
import random
import sys
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import httpx

HERE = Path(__file__).resolve().parent
CLONE = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(CLONE / "scripts"))
import run_org_ablation_sensitivity_20261119 as upstream
from src.llm_client import OpenAICompatibleClient, load_env_file


def save(path, data):
    with path.open("x", encoding="utf8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def digest(messages):
    return hashlib.sha256(json.dumps(messages, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def register(messages):
    text = messages[1]["content"].splitlines()
    i = text.index("Host-derived current disposition (IDs, not new evidence):") + 1
    j = text.index("Complete condition register (not truncated):") + 1
    return text, i, j, json.loads(text[i]), json.loads(text[j])


def correct_register(messages, target):
    text, i, j, state, rows = register(messages)
    entry, = [r for r in rows if r["condition_id"] == target]
    assert target in state["unresolved_condition_ids"] and target not in state["verified_condition_ids"]
    state["unresolved_condition_ids"].remove(target)
    state["verified_condition_ids"].append(target)
    if target in state["active_submission_prerequisite_ids"]:
        state["active_submission_prerequisite_ids"].remove(target)
    entry.update(status="verified", evidence={"source":"synthetic_host_ablation_fixture",
                 "condition_id":target, "scope":"this fictional replay only", "question":entry["question"]})
    text[i] = json.dumps(state, ensure_ascii=False)
    text[j] = json.dumps(rows, ensure_ascii=False)
    messages[1]["content"] = "\n".join(text)


def prepare():
    p = upstream.load_protocol()
    ledger = upstream.read_json(upstream.EXP / "dry_run_ledger.json")["jobs"]
    hashes = {j["job_id"]: j["prompt_sha256"] for j in ledger}
    assert len(hashes) == 56
    cases = {w["window_id"]:w for w in p["windows"]}
    jobs = list(p["jobs"])
    for window in cases:
        for arm in ("D3","S4"):
            name = "identity_" + arm
            jobs.append(dict(job_id=window+"__"+name,window_id=window,arm=arm,ablation_kind=name))
    random.Random(20261119).shuffle(jobs)
    locked = []
    for job in jobs:
        w = cases[job["window_id"]]
        arm = job["arm"]
        kind = job["ablation_kind"]
        home = CLONE / w[arm.lower()+"_job"]
        frozen = upstream.read_json(home / "request-step-4.json")
        raw = upstream.read_json(home / "step-4.json")["parsed"]
        d = HERE / "jobs" / job["job_id"]
        d.mkdir(parents=True)
        target = None
        if kind.startswith("identity"):
            req = deepcopy(frozen)
            save(d/"historical.json",raw)
        else:
            req = upstream.build_ablation_request(w,kind)
            assert digest(req["messages"]) == hashes[job["job_id"]]
            if kind.startswith("bitflip"):
                target = req["ablation"]["bitflip"]["condition_id"]
                correct_register(req["messages"], target)
        save(d/"request.json",req)
        state = register(req["messages"])[3]
        locked.append({**job,"hash":digest(req["messages"]),"original_hash":digest(frozen["messages"]),
                       "target":target,"expected":state,"task_role":w["role"]})
    assert len(locked)==len({v["job_id"] for v in locked})==72
    for window in cases:
        flips = [v for v in locked if v["window_id"]==window and v["target"]]
        assert len(flips)==2 and flips[0]["target"]==flips[1]["target"] and flips[0]["expected"]==flips[1]["expected"]
    save(HERE/"plan.json",dict(version="v2-72", commit="fe23c377c50e58c1b84d5f9562f74b74db46c7d0",
         base_hashes_verified=56,seed=20261119,concurrency=2,model="deepseek-flash",temperature=0.2,
         max_completion_tokens=4096,thinking=False,request_limit=72,locked_at=datetime.now(timezone.utc).isoformat(),
         outcomes=["paired decision field changes for six intention windows","quoted amounts separately for two supplier drafts",
                   "exact agreement of unresolved and verified ID sets compared with expected register; all unrelated IDs preserved",
                   "presence of frozen topic markers in the outward answer; literal proxy, not a quality score"],
         comparison="compare each altered D3/S4 final against its same-window same-arm fresh identity; also compare identities against historical outputs to measure variability",
         jobs=locked))
    return locked


def balance(client):
    r = httpx.get("https://api.deepseek.com/user/balance",headers={"Authorization":"Bearer "+client.config.api_key},timeout=20)
    r.raise_for_status()
    return next(v["total_balance"] for v in r.json()["balance_infos"] if v["currency"]=="CNY")


async def run(jobs):
    assert os.environ.get("ORG_ABLATION_ALLOW_LIVE")=="1" and "--i-authorize-live-calls" in sys.argv
    load_env_file(CLONE.parent / ".env")
    client = OpenAICompatibleClient.from_env(model="deepseek-flash")
    assert client.config.provider=="deepseek" and urlparse(client.config.base_url).hostname=="api.deepseek.com"
    save(HERE/"opening.json",{"CNY":balance(client)})
    gate = asyncio.Semaphore(2)
    async def one(job):
        async with gate:
            d = HERE/"jobs"/job["job_id"]
            q = upstream.read_json(d/"request.json")
            assert digest(q["messages"])==job["hash"]
            save(d/"attempt.json",{"started":datetime.now(timezone.utc).isoformat()})
            try:
                reply = await client._chat_model.ainvoke(client._lc_messages(q["messages"]),
                        **client._invoke_kwargs(0.2),max_completion_tokens=4096)
                v=client._response(reply)
                save(d/"response.json",{"raw_content":v.content,"metadata":v.metadata})
            except Exception as e:
                save(d/"error.json",{"type":type(e).__name__,"message":str(e)[:500]})
    await asyncio.gather(*(one(job) for job in jobs))
    save(HERE/"closing.json",{"CNY":balance(client)})


if __name__=="__main__":
    jobs = prepare()
    print("Verified 56 upstream hashes; locked 72 prompts.",flush=True)
    asyncio.run(run(jobs))
