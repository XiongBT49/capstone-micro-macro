"""Offline comparison of three external baselines with frozen tender cases.

Run:  python -m scripts.compare_external_baselines_20261123

Reads the 28 frozen cases under validation/benchmark_ge3_compact and writes
results/experiments/external_baseline_comparison_20261123/. Historical files
are not modified. No model is called.

1. pymcdm TOPSIS ranks each package from the frozen price, the frozen duration
   when every bid states one, and the percentage weights already written in the
   case. Declared weights with no numeric attribute are left unused.
2. Each frozen bid document is scored with the countable levels of the bid
   rubric. The same tender text and bidder facts are written out as the packet
   a bid-document generator would receive. No external document is invented,
   so that side has no rubric score.
3. One formed consortium is translated into an LLM-Deliberation game. Secret
   scores come only from package requirement stems that already appear in a
   member's company file. The frozen agreement is then scored against those
   scores. The negotiation itself is not re-run.
"""
from __future__ import annotations

import json
import re
import warnings
from collections import Counter
from pathlib import Path

import numpy as np
from pymcdm.methods import TOPSIS

warnings.filterwarnings("ignore", module=r"pymcdm\.validators")

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "validation/benchmark_ge3_compact/results/final_28_20260817/cases"
OUT = ROOT / "results/experiments/external_baseline_comparison_20261123"

WEIGHT_PATTERN = re.compile(
    r"(工程造价|承揽造价|施工期|工作计划|施工经验及质量)\s*(\d+(?:\.\d+)?)\s*%"
)
WEIGHT_IDS = {
    "工程造价": "price",
    "承揽造价": "price",
    "施工期": "duration",
    "工作计划": "work_plan",
    "施工经验及质量": "experience_quality",
}
NUMERIC_CRITERIA = {"price": "cost", "duration": "cost"}
TOTAL_DURATION = re.compile(
    r"(?:总工期|设计总工期|设计周期|承诺总工期|交货期|交付周期)"
    r"[^。\n]{0,16}?"
    r"(\d+(?:\.\d+)?)\s*(周|个月|月)"
)
FALLBACK_DURATION = re.compile(
    r"(?:合同签订后|合同生效后|开工后)\s*(\d+(?:\.\d+)?)\s*(周|个月|月)内"
)
STEM_WORDS = ("能力", "设计", "协调", "编制", "服务")
RUBRIC_PATH = "config/micro_org_rubric.json"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def declared_weights(constraints: list[str]) -> dict[str, float] | None:
    hint = next((row for row in constraints if str(row).startswith("评标标准提示")), "")
    if "无法获取" in hint or "%" not in hint:
        return None
    found: dict[str, float] = {}
    for label, raw in WEIGHT_PATTERN.findall(hint):
        criterion = WEIGHT_IDS[label]
        if criterion in found:
            return None
        found[criterion] = float(raw)
    if "price" not in found or not found:
        return None
    return found


def parse_duration(text: str) -> tuple[float, str] | None:
    matches = [(float(n), "月" if unit == "个月" else unit) for n, unit in TOTAL_DURATION.findall(text or "")]
    if not matches:
        matches = [(float(n), "月" if unit == "个月" else unit) for n, unit in FALLBACK_DURATION.findall(text or "")]
    unique = {(n, unit) for n, unit in matches}
    if len(unique) != 1:
        return None
    return unique.pop()


def disqualified(opening: list[dict]) -> set[str]:
    found = set()
    for package in opening or []:
        for item in package.get("disqualified_bids") or []:
            if isinstance(item, dict):
                found.update(value for value in (item.get("bid_id"), item.get("bidder_id")) if value)
            elif isinstance(item, str):
                found.add(item)
    return found


def topsis_groups(matrix: list[list[float]], weights: list[float], types: list[int]) -> list[list[int]]:
    preference = TOPSIS()(np.asarray(matrix, dtype=float), np.asarray(weights, dtype=float), np.asarray(types, dtype=int))
    rounded = [round(float(value), 8) for value in preference]
    order = sorted(range(len(rounded)), key=lambda index: -rounded[index])
    groups: list[list[int]] = []
    for index in order:
        if groups and rounded[index] == rounded[groups[-1][0]]:
            groups[-1].append(index)
        else:
            groups.append([index])
    return groups


def award_comparison(cases: list[Path]) -> dict:
    packages = []
    excluded = []
    for case_dir in cases:
        checkpoint = read_json(case_dir / "workflow_checkpoint.json")
        weights = declared_weights(checkpoint["state"]["project_idea"].get("constraints") or [])
        bids = read_json(case_dir / "bid_documents.json")
        opening = read_json(case_dir / "opening_record.json") if (case_dir / "opening_record.json").exists() else []
        blocked = disqualified(opening)
        awards = {row["package_id"]: row for row in read_json(case_dir / "simulated_award_result.json").get("package_awards") or []}
        evaluations = {row["package_id"]: row for row in read_json(case_dir / "evaluation_report.json")}
        by_package: dict[str, list[dict]] = {}
        for bid in bids:
            by_package.setdefault(bid["package_id"], []).append(bid)
        for package_id, rows in sorted(by_package.items()):
            identity = {"case_id": case_dir.name, "package_id": package_id}
            eligible = [
                bid for bid in rows
                if isinstance(bid.get("quotation"), (int, float)) and bid["quotation"] > 0
                and bid.get("bid_id") not in blocked and bid.get("bidder_id") not in blocked
            ]
            if weights is None:
                excluded.append({**identity, "reason": "no declared percentage weights"})
                continue
            if len(eligible) < 2:
                excluded.append({**identity, "reason": "fewer than two priced eligible bids", "eligible_bids": len(eligible)})
                continue
            durations = [parse_duration(bid.get("schedule_commitment") or "") for bid in eligible]
            applied = ["price"]
            unused = {key: value for key, value in weights.items() if key not in NUMERIC_CRITERIA}
            duration_note = None
            if "duration" in weights:
                if all(item is not None for item in durations) and len({item[1] for item in durations}) == 1:
                    applied.append("duration")
                else:
                    unused["duration"] = weights["duration"]
                    duration_note = "duration weight unused because a bid has no single total duration, or the bids use different units"
            applied_sum = sum(weights[key] for key in applied)
            used_weights = [weights[key] / applied_sum for key in applied]
            matrix = []
            bidders = []
            for bid, duration in zip(eligible, durations):
                row = [float(bid["quotation"])]
                if "duration" in applied:
                    row.append(float(duration[0]))
                matrix.append(row)
                bidders.append({
                    "bid_id": bid["bid_id"],
                    "bidder_id": bid["bidder_id"],
                    "bidder_name": bid.get("bidder_name"),
                    "price": float(bid["quotation"]),
                    "duration": None if duration is None else {"value": duration[0], "unit": duration[1]},
                })
            groups = topsis_groups(matrix, used_weights, [-1] * len(applied))
            ranking = [[bidders[index]["bidder_id"] for index in group] for group in groups]
            award = awards.get(package_id) or {}
            winner = award.get("selected_bidder_id")
            in_matrix = winner in {bidder["bidder_id"] for bidder in bidders}
            top = set(ranking[0])
            packages.append({
                **identity,
                "declared_weights_percent": weights,
                "applied_criteria": applied,
                "applied_weights": {key: used_weights[pos] for pos, key in enumerate(applied)},
                "unused_declared_weights_percent": unused,
                "duration_note": duration_note,
                "bidders": bidders,
                "topsis_ranking_high_to_low": ranking,
                "award_winner": winner,
                "evaluation_recommended_winner": (evaluations.get(package_id) or {}).get("recommended_winner"),
                "winner_in_matrix": in_matrix,
                "winner_in_top_group": bool(in_matrix and winner in top),
                "top_group_is_unique": len(top) == 1,
            })
    comparable = [row for row in packages if row["winner_in_matrix"]]
    unique = [row for row in comparable if row["top_group_is_unique"]]
    price_only = [row for row in comparable if row["applied_criteria"] == ["price"]]
    with_duration = [row for row in comparable if "duration" in row["applied_criteria"]]
    return {
        "method": "pymcdm TOPSIS. Price and duration are cost criteria. Higher preference ranks first. Equal preferences stay in one group.",
        "model_calls": 0,
        "packages_ranked": len(packages),
        "packages_with_award_winner_in_matrix": len(comparable),
        "winner_in_top_group": sum(row["winner_in_top_group"] for row in comparable),
        "unique_top_packages": len(unique),
        "unique_top_winner_match": sum(row["winner_in_top_group"] for row in unique),
        "packages_using_duration": len(with_duration),
        "duration_winner_in_top_group": sum(row["winner_in_top_group"] for row in with_duration),
        "packages_price_only": len(price_only),
        "price_only_winner_in_top_group": sum(row["winner_in_top_group"] for row in price_only),
        "price_only_top_is_lowest_price": sum(
            min(row["bidders"], key=lambda bidder: bidder["price"])["bidder_id"] in row["topsis_ranking_high_to_low"][0]
            for row in price_only
        ),
        "excluded": excluded,
        "packages": packages,
    }


def r2_level(specific: int, name_only: int) -> int:
    present = specific + name_only
    if specific == 7:
        return 5
    if specific == 6 and name_only + (7 - present) == 1:
        return 4
    if specific == 5 or (present >= 6 and name_only >= 2):
        return 3
    if specific + name_only >= 3:
        return 2
    return 1


def r3_level(passed: int) -> int:
    if passed >= 5:
        return 5
    if passed == 4:
        return 4
    if passed == 3:
        return 3
    if passed >= 1:
        return 2
    return 1


def _specific_text(text: str, minimum: int = 40) -> str:
    stripped = (text or "").strip()
    if not stripped:
        return "missing"
    return "specific" if len(stripped) >= minimum else "name_only"


def score_bid_document(bid: dict) -> dict:
    """Apply the bid rubric levels that count items. Judgment levels stay unscored."""
    breakdown = bid.get("quotation_breakdown") or []
    lines_ok = bool(breakdown) and all(
        isinstance(row, dict) and isinstance(row.get("amount"), (int, float)) and str(row.get("basis") or "").strip()
        for row in breakdown
    )
    duration = parse_duration(bid.get("schedule_commitment") or "")
    assumptions = bid.get("bid_assumptions") or []
    assumption_text = " ".join(assumptions) if isinstance(assumptions, list) else str(assumptions)
    has_assumption = bool(str(assumption_text).strip()) or bool(re.search(r"假设|除外|前提", json.dumps(bid, ensure_ascii=False)))
    items = {
        "技术方案": _specific_text(bid.get("technical_proposal") or ""),
        "实施计划": "specific" if re.search(r"阶段|里程碑|第\d+", bid.get("implementation_plan") or "") and len(bid.get("implementation_plan") or "") >= 40 else _specific_text(bid.get("implementation_plan") or ""),
        "报价分项": "specific" if isinstance(bid.get("quotation"), (int, float)) and lines_ok else ("name_only" if bid.get("quotation") else "missing"),
        "工期承诺": "specific" if duration else _specific_text(bid.get("schedule_commitment") or "", 8),
        "业主控制响应": _specific_text(bid.get("compliance_statement") or "", 20),
        "风险应对": _specific_text(bid.get("risk_response") or "", 20),
        "假设或除外": "specific" if has_assumption else "missing",
    }
    specific = sum(value == "specific" for value in items.values())
    name_only = sum(value == "name_only" for value in items.values())
    plan = bid.get("implementation_plan") or ""
    compliance = bid.get("compliance_statement") or ""
    risk = bid.get("risk_response") or ""
    aspects = {
        "计划有阶段和时间": bool(re.search(r"阶段|里程碑", plan) and re.search(r"周|月|第\d+", plan)),
        "分项有金额和依据": lines_ok,
        "工期是一个明确期限": duration is not None,
        "审查响应写了提交物或时限": bool(re.search(r"审查", compliance) and re.search(r"提交|节点|周|月|时限|天", compliance)),
        "风险写了触发或责任方": bool(re.search(r"触发|若|如果|负责|承担|责任", risk)),
    }
    closed = None
    if lines_ok:
        closed = abs(sum(float(row["amount"]) for row in breakdown) - float(bid["quotation"])) < 1
    plan_duration = parse_duration(plan)
    duration_conflict = bool(duration and plan_duration and duration != plan_duration)
    r6 = None
    if closed is False:
        r6 = 2
    elif closed and duration_conflict:
        r6 = 3
    return {
        "bid_id": bid.get("bid_id"),
        "bidder_id": bid.get("bidder_id"),
        "rubric": RUBRIC_PATH,
        "rubric_section": "bid",
        "scored_by": "mechanical counts from the published level text",
        "R1": None,
        "R2": r2_level(specific, name_only),
        "R3": r3_level(sum(aspects.values())),
        "R4": None,
        "R5": None,
        "R6": r6,
        "R2_items": items,
        "R3_aspects": aspects,
        "price_lines_closed": closed,
        "duration_conflict": duration_conflict,
        "unscored": ["R1", "R4", "R5"] + ([] if r6 is not None else ["R6"]),
        "unscored_reason": "Those levels ask whether the scheme fits the firm, whether the tradeoff is real, and whether a stated fact was invented. A keyword count does not decide them.",
    }


def company_blob(company: dict) -> str:
    parts = [company.get("profile") or "", company.get("capacity") or ""]
    for key in ("qualifications", "strengths", "weaknesses", "risk_signals"):
        parts.extend(company.get(key) or [])
    return "\n".join(str(part) for part in parts if part)


def requirement_stems(requirement: str) -> list[str]:
    text = requirement
    for word in STEM_WORDS:
        text = text.replace(word, " ")
    return [token for token in text.split() if len(token) >= 2]


def bidder_facts(bid: dict, companies: dict[str, dict], consortiums: list[dict]) -> dict:
    if bid.get("bidder_type") == "consortium":
        consortium = next((row for row in consortiums if row.get("consortium_id") == bid.get("bidder_id")), None)
        member_ids = (consortium or {}).get("member_company_ids") or []
        return {
            "bidder_id": bid.get("bidder_id"),
            "bidder_type": "consortium",
            "members": [
                {"company_id": member_id, "company_name": (companies.get(member_id) or {}).get("company_name"),
                 "facts": company_blob(companies[member_id])}
                for member_id in member_ids if member_id in companies
            ],
        }
    company = companies.get(bid.get("bidder_id")) or {}
    return {
        "bidder_id": bid.get("bidder_id"),
        "bidder_type": bid.get("bidder_type"),
        "company_name": company.get("company_name") or bid.get("bidder_name"),
        "facts": company_blob(company),
    }


def tender_text(package: dict, weight_hint: str) -> str:
    lines = [
        f"包编号: {package.get('package_id')}",
        f"包名称: {package.get('package_name')}",
        f"范围: {package.get('scope')}",
        "能力要求:",
        *[f"- {item}" for item in package.get("qualification_requirements") or []],
        "投标文件要求:",
        *[f"- {item}" for item in package.get("proposal_requirements") or []],
        "评比要点:",
        *[f"- {item}" for item in package.get("evaluation_criteria") or []],
        f"报价要求: {package.get('pricing_requirements') or ''}",
        f"评标权重提示: {weight_hint}",
    ]
    return "\n".join(lines).strip() + "\n"


def document_comparison(cases: list[Path], shared: dict | None) -> dict:
    scores = []
    for case_dir in cases:
        checkpoint = read_json(case_dir / "workflow_checkpoint.json")
        packages = {row["package_id"]: row for row in checkpoint["state"].get("tender_packages") or []}
        companies = {row["company_id"]: row for row in read_json(case_dir / "companies.json")}
        consortiums = read_json(case_dir / "consortiums.json")
        hint = next((row for row in checkpoint["state"]["project_idea"].get("constraints") or [] if str(row).startswith("评标标准提示")), "")
        for bid in read_json(case_dir / "bid_documents.json"):
            package = packages.get(bid["package_id"]) or {}
            score = score_bid_document(bid)
            score.update({"case_id": case_dir.name, "package_id": bid["package_id"]})
            scores.append(score)
            if shared and case_dir.name == shared["case_id"] and bid["package_id"] == shared["package_id"]:
                packet = OUT / "bid_documents" / "shared_tender_packet"
                write_text(packet / "招标文件" / "package.txt", tender_text(package, hint))
                facts = bidder_facts(bid, companies, consortiums)
                write_text(packet / "投标人资料" / f"{bid['bidder_id']}.txt", json.dumps(facts, ensure_ascii=False, indent=2) + "\n")
    histogram = lambda key: {str(level): sum(row[key] == level for row in scores) for level in (1, 2, 3, 4, 5)}
    gaps = Counter()
    for row in scores:
        for name, state in row["R2_items"].items():
            if state != "specific":
                gaps[f"{name}:{state}"] += 1
    return {
        "rubric": RUBRIC_PATH,
        "model_calls": 0,
        "bids_scored": len(scores),
        "R2_levels": histogram("R2"),
        "R3_levels": histogram("R3"),
        "R6_levels": {str(level): sum(row["R6"] == level for row in scores) for level in (2, 3)},
        "R2_not_specific": dict(gaps),
        "R6_unscored_because_lines_closed_without_a_further_contradiction": sum(row["R6"] is None and row["price_lines_closed"] for row in scores),
        "price_lines_closed": sum(row["price_lines_closed"] is True for row in scores),
        "price_lines_not_closed": sum(row["price_lines_closed"] is False for row in scores),
        "shared_packet": None if shared is None else {
            "case_id": shared["case_id"],
            "package_id": shared["package_id"],
            "path": "bid_documents/shared_tender_packet",
            "framework_bids_scored": sum(
                row["case_id"] == shared["case_id"] and row["package_id"] == shared["package_id"] for row in scores
            ),
            "bid_gen_documents_scored": 0,
            "bid_gen_status": "No bid-gen document was generated. Its planning step needs a live model, and this comparison does not call one. A missing document has no rubric score.",
        },
        "scores": scores,
    }


def supports(stems: list[str], blob: str) -> bool:
    return any(stem and stem in blob for stem in stems)


def choose_consortium(cases: list[Path]) -> dict | None:
    best = None
    for case_dir in cases:
        checkpoint = read_json(case_dir / "workflow_checkpoint.json")
        packages = {row["package_id"]: row for row in checkpoint["state"].get("tender_packages") or []}
        companies = {row["company_id"]: row for row in read_json(case_dir / "companies.json")}
        for consortium in read_json(case_dir / "consortiums.json"):
            if consortium.get("status") != "formed" or len(consortium.get("member_company_ids") or []) < 2:
                continue
            package = packages.get(consortium["package_id"])
            if not package:
                continue
            member_blobs = {member: company_blob(companies[member]) for member in consortium["member_company_ids"] if member in companies}
            if len(member_blobs) < 2:
                continue
            supported = 0
            for requirement in package.get("qualification_requirements") or []:
                stems = requirement_stems(requirement)
                if any(supports(stems, blob) for blob in member_blobs.values()):
                    supported += 1
            # Most stems stated in a member file, then the earliest case and package.
            # The agreement text is not part of this key.
            key = (-supported, case_dir.name, consortium["package_id"], consortium.get("consortium_id") or "")
            if best is None or key < best[0]:
                best = (key, {
                    "case_dir": case_dir,
                    "case_id": case_dir.name,
                    "package": package,
                    "consortium": {key: value for key, value in consortium.items() if key not in {"formation_reason", "agreement_summary"}},
                    "companies": {member: companies[member] for member in member_blobs},
                    "supported_requirements": supported,
                })
    return None if best is None else best[1]


def consortium_game(selected: dict) -> dict:
    members = sorted(selected["companies"])
    issues = []
    excluded_issues = []
    for requirement in selected["package"].get("qualification_requirements") or []:
        stems = requirement_stems(requirement)
        covered = {member: supports(stems, company_blob(selected["companies"][member])) for member in members}
        if any(covered.values()):
            issues.append({"requirement": requirement, "stems": stems, "supported_by": sorted(member for member, ok in covered.items() if ok)})
        else:
            excluded_issues.append({"requirement": requirement, "stems": stems, "reason": "no member file contains the requirement stem"})
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    deal_codes = []
    p1 = min(members, key=lambda member: (-sum(member in issue["supported_by"] for issue in issues), member))
    for index, issue in enumerate(issues):
        own = [member for member in members if member in issue["supported_by"]]
        favorite = p1 if p1 in own else own[0]
        deal_codes.append(f"{letters[index]}{members.index(favorite) + 1}")
    game = OUT / "consortium" / "games_descriptions" / f"{selected['case_id']}_{selected['package']['package_id']}"
    names = ", ".join(f'"{member}"' for member in members)
    issue_lines = []
    for index, issue in enumerate(issues):
        options = "\n".join(
            f'{letters[index]}{pos + 1} "{member}" takes "{issue["requirement"]}".'
            for pos, member in enumerate(members)
        )
        issue_lines.append(f'Issue {letters[index]}: "{issue["requirement"]}"\n{options}\n')
    global_text = (
        f'Project package "{selected["package"]["package_id"]}" from {selected["case_id"]}.\n'
        f'Scope: {selected["package"].get("scope")}\n\n'
        f'The parties are: {names}.\n'
        "Each party is one firm. The negotiation decides which firm takes each listed capability. "
        "One option is chosen for each issue.\n\n"
        + "\n".join(issue_lines)
    )
    write_text(game / "global_instructions.txt", global_text)
    write_text(game / "initial_deal.txt", ",".join(deal_codes) + "\n")
    for member in members:
        scores = []
        for issue in issues:
            row = []
            for option in members:
                if option not in issue["supported_by"]:
                    row.append(0)
                elif option == member:
                    row.append(10)
                else:
                    row.append(5)
            scores.append(", ".join(str(value) for value in row))
        threshold = 5 * len(issues)
        scores.append(str(threshold))
        write_text(game / "scores_files" / f"{member}.txt", "\n".join(scores) + "\n")
        company = selected["companies"][member]
        write_text(
            game / "individual_instructions" / "cooperative" / f"{member}.txt",
            (
                f'You are "{member}" ({company.get("company_name")}). Your incentive is cooperative: '
                f"a deal at or above your minimum score of {threshold} is acceptable, and a deal below it is not.\n"
                "Your secret scores are in the scores file. They were fixed from your company file before the agreement was read. "
                "An option scores 10 when you take a capability your own file states, 5 when another firm whose file states it takes that capability, and 0 otherwise.\n\n"
                "Company file:\n"
                f"{company_blob(company)}\n"
            ),
        )
    # p2 must be one of the non-p1 members. Rebuild roles in a stable way.
    others = [member for member in members if member != p1]
    config = [f"{p1},{p1},p1,cooperative,not-executed"]
    for pos, member in enumerate(others):
        role = "p2" if pos == 0 else "player"
        config.append(f"{member},{member},{role},cooperative,not-executed")
    write_text(game / "config.txt", "\n".join(config) + "\n")
    observed = score_observed_agreement(selected, issues, members)
    observed.update({
        "case_id": selected["case_id"],
        "package_id": selected["package"]["package_id"],
        "consortium_id": selected["consortium"]["consortium_id"],
        "selection_rule": "Formed consortium whose member files state the most package-requirement stems. Ties break by case id, then package id.",
        "supported_requirement_count": selected["supported_requirements"],
        "issues_in_game": [issue["requirement"] for issue in issues],
        "excluded_issues": excluded_issues,
        "p1": p1,
        "threshold_rule": "5 points times the number of issues in the game. A party reaches it only when every included capability is given to a firm whose own file states that capability.",
        "model_calls": 0,
        "dialogue_run": False,
        "game_dir": str(game.relative_to(OUT)),
    })
    return observed


def score_observed_agreement(selected: dict, issues: list[dict], members: list[str]) -> dict:
    role_split = selected["consortium"].get("role_split") or {}
    assignments = []
    utilities = {member: 0 for member in members}
    for issue in issues:
        hits = []
        for member in members:
            text = str(role_split.get(member) or "")
            hit_count = sum(stem in text for stem in issue["stems"])
            if hit_count:
                hits.append((hit_count, member))
        hits.sort(reverse=True)
        assignee = None
        if len(hits) == 1 or (len(hits) > 1 and hits[0][0] > hits[1][0]):
            assignee = hits[0][1]
        for member in members:
            if assignee is None or assignee not in issue["supported_by"]:
                gained = 0
            elif assignee == member:
                gained = 10
            else:
                gained = 5
            utilities[member] += gained
        assignments.append({
            "requirement": issue["requirement"],
            "stems": issue["stems"],
            "supported_by": issue["supported_by"],
            "assignee": assignee,
            "assignee_is_supported": bool(assignee in issue["supported_by"]) if assignee else False,
        })
    threshold = 5 * len(issues)
    complete = bool(issues) and all(row["assignee_is_supported"] for row in assignments)
    clears = {member: complete and utilities[member] >= threshold for member in members} if issues else {}
    return {
        "status": selected["consortium"].get("status"),
        "assignments": assignments,
        "utility": utilities,
        "threshold": threshold,
        "each_party_clears_threshold": clears,
        "agreement_success": bool(issues) and selected["consortium"].get("status") == "formed" and all(clears.values()) and all(
            row["assignee_is_supported"] for row in assignments
        ),
    }


def median_value(values: list[float]) -> float:
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return float(ordered[middle])
    return float(ordered[middle - 1] + ordered[middle]) / 2


def percentile_interval(samples: list[float]) -> list[float]:
    low, high = np.quantile(np.asarray(samples, dtype=float), [0.025, 0.975])
    return [float(low), float(high)]


def _award_case_records(packages: list[dict]) -> dict[str, dict]:
    grouped: dict[str, list[dict]] = {}
    for row in packages:
        if row.get("winner_in_matrix"):
            grouped.setdefault(row["case_id"], []).append(row)
    records = {}
    for case_id, rows in grouped.items():
        premiums = []
        for row in rows:
            if not row["top_group_is_unique"]:
                continue
            prices = {bidder["bidder_id"]: bidder["price"] for bidder in row["bidders"]}
            top = row["topsis_ranking_high_to_low"][0][0]
            premiums.append((prices[row["award_winner"]] - prices[top]) / prices[top])
        records[case_id] = {
            "top_group_agreement": sum(bool(row["winner_in_top_group"]) for row in rows) / len(rows),
            "chance": sum(len(row["topsis_ranking_high_to_low"][0]) / len(row["bidders"]) for row in rows) / len(rows),
            "mrr": sum(1 / next(index + 1 for index, group in enumerate(row["topsis_ranking_high_to_low"]) if row["award_winner"] in group) for row in rows) / len(rows),
            "premiums": premiums,
            "packages": len(rows),
        }
    return records


def award_publication_metrics(packages: list[dict], draws: int = 10000, seed: int = 20261123) -> dict:
    """Case-equal award metrics. The bootstrap resamples cases, not packages."""
    records = _award_case_records(packages)
    case_ids = sorted(records)
    rows = [row for row in packages if row.get("winner_in_matrix")]

    def mean_of(selected, key: str) -> float:
        return sum(records[case_id][key] for case_id in selected) / len(selected)

    def pooled_median(selected) -> float | None:
        premiums = [value for case_id in selected for value in records[case_id]["premiums"]]
        return None if not premiums else median_value(premiums)

    point_ids = case_ids
    rng = np.random.default_rng(seed)
    sampled = [rng.choice(case_ids, size=len(case_ids), replace=True) for _ in range(draws)]
    tga = [mean_of(draw, "top_group_agreement") for draw in sampled]
    delta = [mean_of(draw, "top_group_agreement") - mean_of(draw, "chance") for draw in sampled]
    mrr = [mean_of(draw, "mrr") for draw in sampled]
    premium = [value for draw in sampled if (value := pooled_median(draw)) is not None]
    by_type: dict[str, list[int]] = {}
    ranks: dict[str, int] = {}
    for row in rows:
        counts = by_type.setdefault(row["package_id"], [0, 0])
        counts[1] += 1
        counts[0] += int(bool(row["winner_in_top_group"]))
        rank = next(index + 1 for index, group in enumerate(row["topsis_ranking_high_to_low"]) if row["award_winner"] in group)
        ranks[str(rank)] = ranks.get(str(rank), 0) + 1
    unique_premiums = [value for case_id in case_ids for value in records[case_id]["premiums"]]
    disagree = [value for value in unique_premiums if value != 0]
    return {
        "estimand": "Cases in the frozen 28-case set that publish percentage weights and have at least two priced bids. Each such case contributes one rate. Packages inside a case are averaged first.",
        "uncertainty": "Percentile cluster bootstrap, cases drawn with replacement, 10000 draws, seed 20261123.",
        "cases": len(case_ids),
        "packages": len(rows),
        "case_top_group_agreement": {case_id: records[case_id]["top_group_agreement"] for case_id in case_ids},
        "top_group_agreement": {
            "estimate": mean_of(point_ids, "top_group_agreement"),
            "ci95": percentile_interval(tga),
        },
        "chance_top_group_rate": mean_of(point_ids, "chance"),
        "agreement_minus_chance": {
            "estimate": mean_of(point_ids, "top_group_agreement") - mean_of(point_ids, "chance"),
            "ci95": percentile_interval(delta),
        },
        "mean_reciprocal_rank": {
            "estimate": mean_of(point_ids, "mrr"),
            "ci95": percentile_interval(mrr),
            "definition": "Rank is the 1-based TOPSIS group that contains the awarded bidder. Tied bidders share a group.",
        },
        "package_pooled_top_group_agreement": sum(bool(row["winner_in_top_group"]) for row in rows) / len(rows),
        "award_rank_counts": {key: ranks[key] for key in sorted(ranks, key=int)},
        "relative_award_price": {
            "definition": "(awarded price - unique TOPSIS-top price) / unique TOPSIS-top price. Ties for the top group are omitted.",
            "packages": len(unique_premiums),
            "median": pooled_median(point_ids),
            "median_ci95": percentile_interval(premium),
            "median_when_they_differ": None if not disagree else median_value(disagree),
            "differing_packages": len(disagree),
        },
        "top_group_agreement_by_package_type": {
            package_id: {"matches": counts[0], "packages": counts[1]} for package_id, counts in sorted(by_type.items())
        },
    }


def document_publication_metrics(scores: list[dict], draws: int = 10000, seed: int = 20261123) -> dict:
    grouped: dict[str, list[dict]] = {}
    for row in scores:
        grouped.setdefault(row["case_id"], []).append(row)
    case_ids = sorted(grouped)

    def case_means(case_id: str) -> dict[str, float]:
        rows = grouped[case_id]
        return {
            "R2": sum(row["R2"] for row in rows) / len(rows),
            "R3": sum(row["R3"] for row in rows) / len(rows),
            "checklist": sum(sum(state == "specific" for state in row["R2_items"].values()) / 7 for row in rows) / len(rows),
            "closure": sum(row["price_lines_closed"] is True for row in rows) / len(rows),
            "duration_conflict": sum(bool(row["duration_conflict"]) for row in rows) / len(rows),
        }

    means = {case_id: case_means(case_id) for case_id in case_ids}

    def average(selected, key: str) -> float:
        return sum(means[case_id][key] for case_id in selected) / len(selected)

    rng = np.random.default_rng(seed)
    sampled = [rng.choice(case_ids, size=len(case_ids), replace=True) for _ in range(draws)]
    return {
        "estimand": "Case-equal mean of bid-level mechanical rubric scores. This is the framework arm only.",
        "uncertainty": "Percentile cluster bootstrap over cases, 10000 draws, seed 20261123.",
        "cases": len(case_ids),
        "bids": len(scores),
        "R2": {"estimate": average(case_ids, "R2"), "ci95": percentile_interval([average(draw, "R2") for draw in sampled])},
        "R3": {"estimate": average(case_ids, "R3"), "ci95": percentile_interval([average(draw, "R3") for draw in sampled])},
        "checklist_specific_share": {
            "estimate": average(case_ids, "checklist"),
            "ci95": percentile_interval([average(draw, "checklist") for draw in sampled]),
            "definition": "Share of the seven R2 checklist items that have specific content.",
        },
        "price_line_closure": {
            "estimate": average(case_ids, "closure"),
            "ci95": percentile_interval([average(draw, "closure") for draw in sampled]),
        },
        "duration_conflict_rate": {
            "estimate": average(case_ids, "duration_conflict"),
            "ci95": percentile_interval([average(draw, "duration_conflict") for draw in sampled]),
        },
        "paired_external_contrast": {
            "definition": "On one shared tender packet, the mean of framework minus external rubric level, computed separately for R2 and for R3.",
            "status": "not estimated",
            "reason": "The external arm has no document, so the difference is undefined.",
        },
    }


def consortium_publication_metrics(consortium: dict) -> dict:
    issues = consortium["assignments"]
    utilities = consortium["utility"]
    threshold = consortium["threshold"]
    assigned = sum(bool(row["assignee_is_supported"]) for row in issues)
    cleared = sum(bool(value) for value in consortium["each_party_clears_threshold"].values())
    normalized = [value / threshold for value in utilities.values()] if threshold else []
    return {
        "estimand": "One pre-specified consortium, scored under preferences fixed from the company files. These are descriptions of that deal, not a sample rate.",
        "cases": 1,
        "issues_in_game": len(issues),
        "issue_assignment_rate": assigned / len(issues) if issues else None,
        "party_clearance_rate": cleared / len(utilities) if utilities else None,
        "mean_normalized_utility": sum(normalized) / len(normalized) if normalized else None,
        "minimum_normalized_utility": min(normalized) if normalized else None,
        "agreement_success": consortium["agreement_success"],
    }


def _fmt(value: float) -> str:
    return f"{value:.3f}"


def _ci(interval: list[float]) -> str:
    return f"{_fmt(interval[0])} to {_fmt(interval[1])}"


def render_summary(award: dict, documents: dict, consortium: dict, metrics: dict) -> str:
    compared = award["packages_with_award_winner_in_matrix"]
    matched = award["winner_in_top_group"]
    unique = award["unique_top_packages"]
    unique_match = award["unique_top_winner_match"]
    shared = documents["shared_packet"]
    return "\n".join([
        "# External baseline comparison",
        "",
        "Three comparisons were run on the frozen 28-case tender set. No model was called, and the historical awards, bids, and scores were not changed. The three results are separate.",
        "",
        "## Award ranking (pymcdm TOPSIS)",
        "",
        "TOPSIS was applied to every package that has declared percentage weights and at least two priced bids. It used price, and duration only when every eligible bid stated one total duration in the same unit. Work-plan, experience, and quality weights were left unused because the frozen bids have no numeric score for them. Technical-fit scores were not filled in.",
        "",
        f"Packages ranked: {award['packages_ranked']}. Packages whose awarded bidder is in that matrix: {compared}. The awarded bidder is in the TOPSIS top group on {matched} of {compared}. Where the top group is a single bidder ({unique} packages), the winner matches on {unique_match}.",
        "",
        f"Price was the only applied criterion on {award['packages_price_only']} packages. On each of those, the top group is the lowest price ({award['price_only_top_is_lowest_price']} of {award['packages_price_only']}), and the awarded bidder is in that group on {award['price_only_winner_in_top_group']}. Duration was applied with price on {award['packages_using_duration']} packages, and the awarded bidder is in the top group on {award['duration_winner_in_top_group']} of those.",
        "",
        "A match means the owner's awarded bidder is in the highest TOPSIS group. The owner record does not publish a full order, so there is no second ranking to compare beyond the winner.",
        "",
        "## Bid documents (framework rubric)",
        "",
        f"The countable bid-rubric levels were applied to {documents['bids_scored']} frozen bid documents. R2 follows the seven-item checklist. R3 follows the five executable aspects. R6 is 2 when the price lines do not add up to the total, and 3 when they add up but the plan states a different duration. R1, R4, and R5 are blank: those levels need a reader to judge fit, tradeoff, and invented facts.",
        "",
        f"R2 levels: {documents['R2_levels']}. The bids that are not level 5 miss a checklist item here: {documents['R2_not_specific']}. R3 levels: {documents['R3_levels']}. Price lines add up on {documents['price_lines_closed']} bids and fail to add up on {documents['price_lines_not_closed']}.",
        "",
        f"The shared tender packet is {shared['case_id']} {shared['package_id']} ({shared['path']}). It contains the package text and each bidder's company file, which is the input a bid-document generator would be given. Framework bids scored for that packet: {shared['framework_bids_scored']}. Bid-gen documents scored: {shared['bid_gen_documents_scored']}. {shared['bid_gen_status']}",
        "",
        "## Consortium agreement (LLM-Deliberation scores)",
        "",
        f"The translated game is {consortium['case_id']} {consortium['package_id']} ({consortium['consortium_id']}). {consortium['selection_rule']} Member files state {consortium['supported_requirement_count']} of the package requirements. Issues placed in the game: {len(consortium['issues_in_game'])}. Requirements that no member file states were left out of the scores.",
        "",
        f"Secret scores were written before the agreement text was used. A party scores 10 for taking a capability its own file states, and 5 when another firm whose file states it takes that capability. The minimum score is {consortium['threshold']}. The frozen role split was then read only to see which firm the agreement names for each issue.",
        "",
        f"Agreement success under that rule: {consortium['agreement_success']}. Utilities: {consortium['utility']}. A party clears the minimum only when every included issue is given to a firm whose file states it. Assignments: {consortium['assignments']}. Where an assignee is empty, the role text does not contain the requirement stem. The dialogue was not run.",
        "",
        "## What these numbers are",
        "",
        "The award figure is winner overlap on the numeric criteria the files already contain. The document figure is a checklist score of this framework's own bids. The consortium figure is whether one frozen agreement meets preferences written from the company files. They are not one combined baseline score, and none of them is a project-cost or project-quality result.",
        "",
        "## Metrics for reporting",
        "",
        "The unit for the award and document metrics is the case. Packages or bids inside a case are averaged first, then the cases are averaged. The interval resamples those cases. The consortium figures describe the one translated deal and have no interval.",
        "",
        _metric_lines(metrics),
        "",
    ])


def _metric_lines(metrics: dict) -> str:
    award = metrics["award"]
    documents = metrics["documents"]
    consortium = metrics["consortium"]
    price = award["relative_award_price"]
    types = ", ".join(
        f"{name} {counts['matches']}/{counts['packages']}"
        for name, counts in award["top_group_agreement_by_package_type"].items()
    )
    return "\n".join([
        "### Award: owner decision against pymcdm TOPSIS",
        "",
        f"Case-equal top-group agreement is {_fmt(award['top_group_agreement']['estimate'])} "
        f"(95% interval {_ci(award['top_group_agreement']['ci95'])}), "
        f"from {award['cases']} cases and {award['packages']} packages. "
        f"The package-pooled count is {_fmt(award['package_pooled_top_group_agreement'])}.",
        "",
        f"A uniform draw among the eligible bidders would land in the top group at a case-equal rate of {_fmt(award['chance_top_group_rate'])}. "
        f"Agreement minus that chance rate is {_fmt(award['agreement_minus_chance']['estimate'])} "
        f"(95% interval {_ci(award['agreement_minus_chance']['ci95'])}).",
        "",
        f"Case-equal mean reciprocal rank of the awarded bidder is {_fmt(award['mean_reciprocal_rank']['estimate'])} "
        f"(95% interval {_ci(award['mean_reciprocal_rank']['ci95'])}). "
        f"Across packages, the award's TOPSIS rank counts are {award['award_rank_counts']}. "
        "Rank 1 is the top group, and bidders in the same group share that rank.",
        "",
        f"Where the top group is one bidder ({price['packages']} packages), the median relative price of the award versus that bidder is {_fmt(price['median'])} "
        f"(95% interval {_ci(price['median_ci95'])}). "
        f"Where they differ ({price['differing_packages']} packages), the median relative price is {_fmt(price['median_when_they_differ'])}. "
        "A positive value means the awarded price is higher than the TOPSIS top price.",
        "",
        f"Matches by package type, pooled across cases: {types}.",
        "",
        "### Bid document: framework checklist, external arm not estimated",
        "",
        f"Case-equal mean R2 is {_fmt(documents['R2']['estimate'])} (95% interval {_ci(documents['R2']['ci95'])}). "
        f"Case-equal mean R3 is {_fmt(documents['R3']['estimate'])} (95% interval {_ci(documents['R3']['ci95'])}). "
        f"The share of the seven checklist items with specific content is {_fmt(documents['checklist_specific_share']['estimate'])} "
        f"(95% interval {_ci(documents['checklist_specific_share']['ci95'])}). "
        f"Price lines close on {_fmt(documents['price_line_closure']['estimate'])} of bids at the case-equal rate. "
        f"The plan and the schedule state different durations on {_fmt(documents['duration_conflict_rate']['estimate'])}.",
        "",
        "The paired contrast is the mean, on the shared tender packet, of the framework rubric level minus the external rubric level, separately for R2 and R3. "
        "That contrast is not estimated: the external arm has no document.",
        "",
        "### Consortium: one deal under LLM-Deliberation scores",
        "",
        f"Supported issues named by the role text: {_fmt(consortium['issue_assignment_rate'])} ({consortium['issues_in_game']} issues). "
        f"Parties at or above the pre-written minimum: {_fmt(consortium['party_clearance_rate'])}. "
        f"Mean utility divided by that minimum: {_fmt(consortium['mean_normalized_utility'])}. "
        f"Lowest utility divided by that minimum: {_fmt(consortium['minimum_normalized_utility'])}. "
        f"Deal success: {consortium['agreement_success']}.",
    ])


def main() -> None:
    cases = sorted(path for path in CASES.iterdir() if path.is_dir())
    award = award_comparison(cases)
    ranked = [row for row in award["packages"] if row["winner_in_matrix"]]
    shared = None
    if ranked:
        shared = sorted(ranked, key=lambda row: (-len(row["bidders"]), row["case_id"], row["package_id"]))[0]
    documents = document_comparison(cases, shared)
    selected = choose_consortium(cases)
    consortium = consortium_game(selected)
    metrics = {
        "award": award_publication_metrics(award["packages"]),
        "documents": document_publication_metrics(documents["scores"]),
        "consortium": consortium_publication_metrics(consortium),
    }
    write_json(OUT / "publication_metrics.json", metrics)
    write_json(OUT / "award_pymcdm" / "summary.json", {key: value for key, value in award.items() if key != "packages"})
    write_json(OUT / "award_pymcdm" / "packages.json", award["packages"])
    write_json(OUT / "award_pymcdm" / "excluded.json", award["excluded"])
    write_json(OUT / "bid_documents" / "summary.json", {key: value for key, value in documents.items() if key != "scores"})
    write_json(OUT / "bid_documents" / "scores.json", documents["scores"])
    write_json(OUT / "consortium" / "agreement_score.json", consortium)
    write_text(OUT / "SUMMARY.md", render_summary(award, documents, consortium, metrics))
    print(json.dumps({
        "award_winner_in_top_group": f"{award['winner_in_top_group']}/{award['packages_with_award_winner_in_matrix']}",
        "bids_scored": documents["bids_scored"],
        "bid_gen_documents_scored": documents["shared_packet"]["bid_gen_documents_scored"],
        "agreement_success": consortium["agreement_success"],
        "model_calls": 0,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
