#!/usr/bin/env python3
"""Offline CLI for generation-validation enhancements (items 1–6).

No provider clients, no paid calls, no overwrites of frozen business_review grades.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.generation_validation.anchors import (
    DEFAULT_ANCHORS_PATH,
    default_discrimination_set,
    load_discrimination_anchors,
    score_anchor_sheet,
)
from src.generation_validation.blinding import (
    blind_pair_packet,
    blind_single_answer_packet,
    select_order_swap_pairs,
)
from src.generation_validation.common import RESULTS_DIR, RESEARCH_DIR, read_json, write_json
from src.generation_validation.coverage import build_coverage_matrix
from src.generation_validation.expert_slice import build_expert_packet, sample_expert_slice
from src.generation_validation.mechanical_gates import run_mechanical_gates
from src.generation_validation.score_sheet import (
    blank_score_sheet,
    draft_adjudication_agreement,
    validate_score_sheet,
)


def cmd_init_assets(_: argparse.Namespace) -> None:
    anchors = default_discrimination_set()
    write_json(DEFAULT_ANCHORS_PATH, anchors)
    write_json(
        RESEARCH_DIR / "schemas" / "mechanical_gate_result.schema.json",
        {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": "mechanical-gates.v1",
            "type": "object",
            "required": [
                "schema_version",
                "assigns_business_grades",
                "readable",
                "blocking_codes",
                "eligible_for_business_scoring",
            ],
            "properties": {
                "schema_version": {"const": "mechanical-gates.v1"},
                "assigns_business_grades": {"const": False},
                "readable": {"type": "boolean"},
                "blocking_codes": {"type": "array", "items": {"type": "string"}},
                "eligible_for_business_scoring": {"type": "boolean"},
            },
        },
    )
    write_json(
        RESEARCH_DIR / "schemas" / "score_sheet.schema.json",
        {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": "score-sheet.v1",
            "type": "object",
            "required": ["schema_version", "state", "draft", "adjudication"],
            "properties": {
                "schema_version": {"const": "score-sheet.v1"},
                "state": {"type": "string"},
                "draft": {"type": "object"},
                "adjudication": {"type": "object"},
            },
        },
    )
    write_json(
        RESEARCH_DIR / "schemas" / "draft_adjudication.schema.json",
        {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": "draft-adjudication-agreement.v1",
            "type": "object",
            "required": ["identity"],
            "properties": {
                "identity": {
                    "const": "draft_adjudicator_agreement_not_inter_rater"
                }
            },
        },
    )
    print(
        json.dumps(
            {
                "anchors_path": str(DEFAULT_ANCHORS_PATH.relative_to(ROOT)),
                "anchor_count": len(anchors["anchors"]),
                "schemas": "research/generation_validation/schemas/",
            },
            ensure_ascii=False,
        )
    )


def cmd_gates(args: argparse.Namespace) -> None:
    response = read_json(args.response)
    card = read_json(args.task_card) if args.task_card else None
    if isinstance(card, list):
        window_id = args.window_id
        card = next(c for c in card if c.get("window_id") == window_id)
    result = run_mechanical_gates(response, task_card=card, role=args.role)
    if args.out:
        write_json(args.out, result)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_sheet(args: argparse.Namespace) -> None:
    response = read_json(args.response)
    cards = read_json(args.task_card)
    card = cards if isinstance(cards, dict) else next(
        c for c in cards if c.get("window_id") == args.window_id
    )
    gates = run_mechanical_gates(response, task_card=card)
    sheet = blank_score_sheet(
        response_ref={
            "response_path": str(Path(args.response).as_posix()),
            "window_id": card.get("window_id"),
            "cohort": args.cohort,
        },
        task_card=card,
        mechanical_gates=gates,
        detailed_required=args.detailed,
    )
    if args.out:
        write_json(args.out, sheet)
    print(json.dumps({"state": sheet["state"], "eligible": gates["eligible_for_business_scoring"],
                      "blocking": gates["blocking_codes"], "out": str(args.out) if args.out else None},
                     ensure_ascii=False))


def cmd_validate_sheet(args: argparse.Namespace) -> None:
    sheet = read_json(args.sheet)
    result = validate_score_sheet(sheet, stage=args.stage)
    if args.agreement:
        result["agreement"] = draft_adjudication_agreement(sheet)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result["ok"]:
        raise SystemExit(2)


def cmd_coverage(args: argparse.Namespace) -> None:
    cards = read_json(args.task_cards)
    matrix = build_coverage_matrix(cards)
    out = Path(args.out) if args.out else RESULTS_DIR / "coverage_matrix.json"
    write_json(out, matrix)
    print(
        json.dumps(
            {
                "out": str(out.relative_to(ROOT)),
                "n": matrix["n_task_cards"],
                "acceptance_gate": matrix["acceptance_gate"],
                "claim_gate": matrix["claim_gate"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def cmd_order_swap(args: argparse.Namespace) -> None:
    candidates = read_json(args.candidates)
    selected = select_order_swap_pairs(
        candidates,
        seed=args.seed,
        per_role=None if args.all_pairs else args.per_role,
        all_pairs=args.all_pairs,
    )
    out = Path(args.out) if args.out else RESULTS_DIR / "order_swap_selection_enhanced.json"
    write_json(out, selected)
    print(json.dumps({"out": str(out.relative_to(ROOT)), "count": selected["count"],
                      "mode": selected["mode"]}, ensure_ascii=False))


def cmd_blind_single(args: argparse.Namespace) -> None:
    card = read_json(args.task_card)
    if isinstance(card, list):
        card = next(c for c in card if c.get("window_id") == args.window_id)
    outward = read_json(args.outward) if args.outward else read_json(args.response).get("parsed")
    public_input = {
        k: card.get(k)
        for k in [
            "role",
            "assessment_stage",
            "business_objective",
            "project_facts",
            "scope_basis",
            "provided_company_fields",
            "not_supplied",
            "ordinary_support",
            "conditions",
            "case_specific_attention",
            "factors",
            "common_scoring_rules",
        ]
        if k in card
    }
    packet = blind_single_answer_packet(
        answer_id=args.answer_id or card.get("window_id") or "A",
        task_card_public=public_input,
        outward=outward,
        length_budget=args.length_budget,
    )
    if args.out:
        write_json(args.out, packet)
    print(json.dumps({"leaks": packet["suspected_identity_leak_flags"],
                      "length": packet["length"],
                      "out": str(args.out) if args.out else None}, ensure_ascii=False))


def cmd_blind_pair(args: argparse.Namespace) -> None:
    payload = read_json(args.pair_spec)
    sealed = blind_pair_packet(
        pair_id=payload["pair_id"],
        task_card_public=payload["input"],
        answers=payload["answers"],
        display_order=payload["display_order"],
        length_budget=args.length_budget,
    )
    if args.out:
        write_json(args.out, sealed)
    print(json.dumps({"pair_id": payload["pair_id"], "out": str(args.out) if args.out else None},
                     ensure_ascii=False))


def cmd_expert_slice(args: argparse.Namespace) -> None:
    universe = read_json(args.universe)
    selected = sample_expert_slice(universe, target_n=args.n, seed=args.seed)
    out = Path(args.out) if args.out else RESULTS_DIR / "expert_slice_selection.json"
    write_json(out, selected)
    print(json.dumps({"out": str(out.relative_to(ROOT)), "count": selected["count"],
                      "per_role_counts": selected.get("per_role_counts")}, ensure_ascii=False))


def cmd_expert_packet(args: argparse.Namespace) -> None:
    item = read_json(args.item)
    card = read_json(args.task_card)
    if isinstance(card, list):
        card = next(c for c in card if c.get("window_id") == item.get("window_id"))
    response = read_json(args.response)
    outward, _ = __import__(
        "src.generation_validation.common", fromlist=["content_view"]
    ).content_view(response)
    assert isinstance(outward, dict)
    gates = run_mechanical_gates(response, task_card=card)
    packet = build_expert_packet(
        item=item,
        task_card=card,
        outward=outward,
        mechanical_gates=gates,
        detailed_required=args.detailed,
    )
    if args.out:
        write_json(args.out, packet)
    print(json.dumps({"response_id": item.get("response_id"), "out": str(args.out) if args.out else None},
                     ensure_ascii=False))


def cmd_check_anchors(args: argparse.Namespace) -> None:
    anchors = load_discrimination_anchors(args.anchors)
    judgments = read_json(args.judgments)
    by_id = {j["anchor_id"]: j for j in judgments}
    rows = []
    for anchor in anchors["anchors"]:
        if anchor["anchor_id"] not in by_id:
            continue
        rows.append(score_anchor_sheet(anchor, by_id[anchor["anchor_id"]]))
    summary = {
        "checked": len(rows),
        "all_match": all(r["all_match"] for r in rows) if rows else False,
        "mismatches": [r["anchor_id"] for r in rows if not r["all_match"]],
        "rows": rows,
        "identity": "anchor_discrimination_check_not_accuracy",
    }
    if args.out:
        write_json(args.out, summary)
    print(json.dumps({k: summary[k] for k in ("checked", "all_match", "mismatches")},
                     ensure_ascii=False, indent=2))
    if rows and not summary["all_match"]:
        raise SystemExit(3)


def cmd_freeze_demo(args: argparse.Namespace) -> None:
    """Build offline demo artifacts under results/experiments/... without model calls."""
    cmd_init_assets(args)
    cards_path = ROOT / "Capstone报告/验证体系/实验/2026-11-13_CP08全量微观扩样/task_cards.json"
    cards = read_json(cards_path)
    matrix = build_coverage_matrix(cards)
    write_json(RESULTS_DIR / "coverage_matrix.json", matrix)

    # Demo universe from first card per role (no response bodies required for selection).
    universe = []
    seen = set()
    for card in cards:
        role = card["role"]
        if role in seen:
            continue
        seen.add(role)
        universe.append(
            {
                "response_id": f"demo-{card['window_id']}",
                "window_id": card["window_id"],
                "role": role,
                "cohort": "CP08",
            }
        )
        if len(universe) >= 4:
            # replicate to allow stratified n=36 demo selection from a tiny pool via backfill rules
            break
    # Expand synthetic demo universe for sampler mechanics only.
    demo_universe = []
    for i in range(48):
        base = universe[i % len(universe)]
        demo_universe.append(
            {
                **base,
                "response_id": f"{base['response_id']}-r{i}",
                "role": ["contractor", "supplier", "designer", "supervisor"][i % 4],
            }
        )
    slice_sel = sample_expert_slice(demo_universe, target_n=36, seed="20261117")
    write_json(RESULTS_DIR / "expert_slice_selection_demo.json", slice_sel)

    candidates = [
        {
            "pair_key": f"demo-pair-{i}",
            "role": ["contractor", "supplier", "designer", "supervisor"][i % 4],
            "arms": ["v2_4", "v2_5"],
            "window_id": f"DEMO-{i:03d}",
        }
        for i in range(40)
    ]
    swaps = select_order_swap_pairs(candidates, seed="20261117", per_role=3)
    write_json(RESULTS_DIR / "order_swap_selection_enhanced_demo.json", swaps)
    swaps_all = select_order_swap_pairs(candidates, seed="20261117", all_pairs=True)
    write_json(RESULTS_DIR / "order_swap_selection_all_pairs_demo.json", swaps_all)

    # Mechanical gate demo on a real retained response if present.
    sample_response = ROOT / (
        "Capstone报告/验证体系/实验/2026-11-12_CP零调用准备/CP01/"
        "continuation-001/run/jobs/EXPAND-01-full-v2_5-r1/attempt-1.json"
    )
    demo_artifacts: list[str] = []
    if sample_response.exists():
        cp01_cards = read_json(
            ROOT / "Capstone报告/验证体系/指标补充/2026-11-12_业务结果评价规范_v2/task_cards.json"
        )
        card = next(c for c in cp01_cards if c.get("window_id") == "EXPAND-01-full")
        response = read_json(sample_response)
        gates = run_mechanical_gates(response, task_card=card)
        write_json(RESULTS_DIR / "mechanical_gates_demo_EXPAND-01-full-v2_5.json", gates)
        sheet = blank_score_sheet(
            response_ref={
                "response_path": str(sample_response.relative_to(ROOT)).replace("\\", "/"),
                "window_id": "EXPAND-01-full",
                "cohort": "CP01",
            },
            task_card=card,
            mechanical_gates=gates,
            detailed_required=True,
        )
        write_json(RESULTS_DIR / "score_sheet_blank_demo_EXPAND-01-full-v2_5.json", sheet)
        public_input = {
            k: card.get(k)
            for k in [
                "role",
                "assessment_stage",
                "business_objective",
                "project_facts",
                "scope_basis",
                "provided_company_fields",
                "not_supplied",
                "ordinary_support",
                "conditions",
                "case_specific_attention",
                "factors",
                "common_scoring_rules",
            ]
            if k in card
        }
        from src.generation_validation.common import content_view

        outward, _ = content_view(response)
        packet = blind_single_answer_packet(
            answer_id="EXPAND-01-full-demo",
            task_card_public=public_input,
            outward=outward,
        )
        write_json(RESULTS_DIR / "blind_single_demo_EXPAND-01-full-v2_5.json", packet)
        demo_artifacts.extend(
            [
                "mechanical_gates_demo_EXPAND-01-full-v2_5.json",
                "score_sheet_blank_demo_EXPAND-01-full-v2_5.json",
                "blind_single_demo_EXPAND-01-full-v2_5.json",
            ]
        )

    index = {
        "experiment_id": "generation_validation_enhancement_20261117",
        "implements": [
            "1_mechanical_gates",
            "2_structured_score_sheets_and_draft_adjudication",
            "3_discrimination_anchors",
            "4_blinding_and_order_swap",
            "5_coverage_matrix",
            "6_expert_slice",
        ],
        "new_model_calls": 0,
        "does_not": [
            "overwrite_frozen_business_review_grades",
            "auto_assign_D1_D4",
            "claim_independent_blind_or_inter_rater_reliability",
        ],
        "artifacts": {
            "protocol": "research/generation_validation/README.md",
            "anchors": "research/generation_validation/anchors/discrimination_set_v1.json",
            "coverage_matrix": "results/experiments/generation_validation_enhancement_20261117/coverage_matrix.json",
            "expert_slice_demo": "results/experiments/generation_validation_enhancement_20261117/expert_slice_selection_demo.json",
            "order_swap_demo": "results/experiments/generation_validation_enhancement_20261117/order_swap_selection_enhanced_demo.json",
            "demo_response_artifacts": demo_artifacts,
        },
        "coverage_acceptance_gate": matrix["acceptance_gate"],
        "demo": {"new_model_calls": 0, "artifacts": demo_artifacts},
    }
    write_json(RESULTS_DIR / "index.json", index)
    readme = """# Generation validation enhancement (2026-11-17)

Implements validation process items 1–6 as offline tooling and frozen assets.

- Mechanical gates triage readable/schema/section/pattern issues without assigning D1–D4.
- Structured score sheets separate second-model draft from adjudication.
- Discrimination anchors: 24 held-out constructed exemplars.
- Blinding + order-swap selection (stratified or all pairs).
- Coverage matrix over CP08 task cards with claim acceptance gate.
- Expert slice sampler for a 24–48 answer external credibility set.

`new_model_calls: 0`. Does not overwrite frozen `business_review` grades.

CLI: `uv run python scripts/enhance_generation_validation_20261117.py --help`
"""
    (RESULTS_DIR / "README.md").write_text(readme, encoding="utf-8")
    print(json.dumps({"frozen": str(RESULTS_DIR.relative_to(ROOT)), "new_model_calls": 0,
                      "coverage_pass": matrix["acceptance_gate"]["pass"]}, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    sp = p.add_subparsers(dest="cmd", required=True)

    s = sp.add_parser("init-assets", help="Write schemas and discrimination anchors")
    s.set_defaults(func=cmd_init_assets)

    s = sp.add_parser("gates", help="Run mechanical gates on one response JSON")
    s.add_argument("--response", type=Path, required=True)
    s.add_argument("--task-card", type=Path)
    s.add_argument("--window-id")
    s.add_argument("--role")
    s.add_argument("--out", type=Path)
    s.set_defaults(func=cmd_gates)

    s = sp.add_parser("sheet", help="Create a blank structured score sheet")
    s.add_argument("--response", type=Path, required=True)
    s.add_argument("--task-card", type=Path, required=True)
    s.add_argument("--window-id", required=True)
    s.add_argument("--cohort", default="CP08")
    s.add_argument("--detailed", action="store_true")
    s.add_argument("--out", type=Path)
    s.set_defaults(func=cmd_sheet)

    s = sp.add_parser("validate-sheet", help="Validate draft or adjudication completeness")
    s.add_argument("--sheet", type=Path, required=True)
    s.add_argument("--stage", choices=["draft", "adjudication"], default="adjudication")
    s.add_argument("--agreement", action="store_true")
    s.set_defaults(func=cmd_validate_sheet)

    s = sp.add_parser("coverage", help="Build role×materials×condition×tradeoff coverage matrix")
    s.add_argument("--task-cards", type=Path, required=True)
    s.add_argument("--out", type=Path)
    s.set_defaults(func=cmd_coverage)

    s = sp.add_parser("order-swap", help="Select order-swap pairs by fixed hash")
    s.add_argument("--candidates", type=Path, required=True)
    s.add_argument("--seed", default="20261117")
    s.add_argument("--per-role", type=int, default=3)
    s.add_argument("--all-pairs", action="store_true")
    s.add_argument("--out", type=Path)
    s.set_defaults(func=cmd_order_swap)

    s = sp.add_parser("blind-single", help="Build a blinded single-answer packet")
    s.add_argument("--task-card", type=Path, required=True)
    s.add_argument("--window-id")
    s.add_argument("--response", type=Path)
    s.add_argument("--outward", type=Path)
    s.add_argument("--answer-id")
    s.add_argument("--length-budget", type=int)
    s.add_argument("--out", type=Path)
    s.set_defaults(func=cmd_blind_single)

    s = sp.add_parser("blind-pair", help="Build blinded pair packet with sealed mapping")
    s.add_argument("--pair-spec", type=Path, required=True)
    s.add_argument("--length-budget", type=int)
    s.add_argument("--out", type=Path)
    s.set_defaults(func=cmd_blind_pair)

    s = sp.add_parser("expert-slice", help="Sample stratified expert credibility slice")
    s.add_argument("--universe", type=Path, required=True)
    s.add_argument("--n", type=int, default=36)
    s.add_argument("--seed", default="20261117")
    s.add_argument("--out", type=Path)
    s.set_defaults(func=cmd_expert_slice)

    s = sp.add_parser("expert-packet", help="Build one expert review packet")
    s.add_argument("--item", type=Path, required=True)
    s.add_argument("--task-card", type=Path, required=True)
    s.add_argument("--response", type=Path, required=True)
    s.add_argument("--detailed", action="store_true")
    s.add_argument("--out", type=Path)
    s.set_defaults(func=cmd_expert_packet)

    s = sp.add_parser("check-anchors", help="Compare authored judgments to anchor expectations")
    s.add_argument("--anchors", type=Path)
    s.add_argument("--judgments", type=Path, required=True)
    s.add_argument("--out", type=Path)
    s.set_defaults(func=cmd_check_anchors)

    s = sp.add_parser("freeze-demo", help="Write offline demo artifacts into results/experiments")
    s.set_defaults(func=cmd_freeze_demo)
    return p


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
