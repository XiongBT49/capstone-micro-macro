"""Offline tests for generation-validation enhancements (items 1–6)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.generation_validation.anchors import (
    default_discrimination_set,
    score_anchor_sheet,
)
from src.generation_validation.blinding import (
    blind_pair_packet,
    blind_single_answer_packet,
    preference_after_swap,
    select_order_swap_pairs,
)
from src.generation_validation.coverage import build_coverage_matrix
from src.generation_validation.expert_slice import sample_expert_slice
from src.generation_validation.mechanical_gates import run_mechanical_gates
from src.generation_validation.score_sheet import (
    blank_score_sheet,
    draft_adjudication_agreement,
    validate_score_sheet,
)

ROOT = Path(__file__).resolve().parents[1]


def _card(role: str = "supplier", variant: str = "full") -> dict:
    return {
        "window_id": "TEST-01-full",
        "project_group": "pg",
        "role": role,
        "variant": variant,
        "case_id": "CASE-0001",
        "not_supplied": ["inventory/local-team records"],
        "conditions": [
            {
                "condition_id": "condition_x",
                "status": "requested",
                "question": "渠道审核是否通过",
            }
        ],
        "factors": [
            {
                "factor_id": "S1",
                "label": "供货范围与产品依据",
                "input_pointers": ["/facts"],
                "adequate_handling": "有边界方案",
                "handling_for_supported_defer_or_decline": "有据等待",
                "states": ["correct", "partial", "missing", "contradicted", "not_judgable"],
            },
            {
                "factor_id": "S5",
                "label": "项目针对性与取舍",
                "input_pointers": ["/facts"],
                "adequate_handling": "说明取舍",
                "handling_for_supported_defer_or_decline": "有据拒绝",
                "states": ["correct", "partial", "missing", "contradicted", "not_judgable"],
            },
        ],
        "business_objective": "形成有依据方案并说明取舍",
    }


def test_mechanical_gates_pass_on_complete_supplier_payload():
    response = {
        "status": "accepted",
        "parsed": {
            "technical_proposal": "拟供应档案支持范围内产品，目录未知。",
            "implementation_plan": "规格确认、检验、交付、文档。",
            "quotation": 1,
            "schedule_commitment": "节点待核实。",
            "risk_response": "目录未明。",
            "submission_summary": "意向草案。",
            "task_role": "supplier",
            "verified_condition_ids": [],
            "unresolved_condition_ids": ["condition_x"],
        },
    }
    result = run_mechanical_gates(response, task_card=_card())
    assert result["assigns_business_grades"] is False
    assert result["passed_mechanical_gates"] is True
    assert result["eligible_for_business_scoring"] is True


def test_mechanical_gates_block_unreadable_and_flag_patterns():
    bad = {"status": "invalid_json", "raw_content": '{"decision":"a"}\n{"decision":"b"}'}
    blocked = run_mechanical_gates(bad, task_card=_card())
    assert blocked["passed_mechanical_gates"] is False
    assert "unreadable_or_ambiguous" in blocked["blocking_codes"]

    compact = {
        "status": "accepted",
        "parsed": {
            "decision": "bid",
            "reason": "拟议条件性供货方案，目录未知。",
            "content": "保留未决条件，不作已核实能力陈述。",
            "task_role": "supplier",
            "verified_condition_ids": [],
        },
    }
    alt = run_mechanical_gates(compact, task_card=_card())
    assert alt["eligible_for_business_scoring"] is True
    assert "required_sections_incomplete_alternate_schema" in alt["soft_codes"]

    promise = {
        "status": "accepted",
        "parsed": {
            "technical_proposal": "本公司已经落实全部资源并保证中标。",
            "implementation_plan": "承担整包施工责任。",
            "quotation": 1,
            "schedule_commitment": "保证完工。",
            "risk_response": "无。",
            "submission_summary": "已确认审核已通过。",
            "task_role": "supplier",
            "verified_condition_ids": ["condition_x"],
        },
    }
    flagged = run_mechanical_gates(promise, task_card=_card())
    codes = {hit["code"] for hit in flagged["pattern_flags"] + flagged["invented_fact_flags"]}
    assert "ungrounded_promise" in codes or "scope_overrun" in codes
    assert "marks_unresolved_condition_verified" in codes


def test_score_sheet_validation_and_agreement():
    sheet = blank_score_sheet(
        response_ref={"response_path": "x.json"},
        task_card=_card(),
        mechanical_gates={"eligible_for_business_scoring": True, "blocking_codes": []},
        detailed_required=True,
    )
    assert sheet["state"] == "awaiting_draft"
    draft = sheet["draft"]
    draft["action"] = "conditional_proposal"
    draft["D1"] = {
        "label": "appropriate",
        "quote": "目录未知",
        "reason": "保留未知",
        "reason_codes": [],
    }
    draft["factors"][0].update(
        {"rating": "correct", "quote": "有边界方案", "reason": "ok"}
    )
    draft["factors"][1].update(
        {"rating": "partial", "quote": "取舍", "reason": "联系不足"}
    )
    draft["D3"] = {"score": 2, "quote": "连贯", "reason": "条件性方案"}
    draft["D4"] = {"score": 1, "quote": "取舍", "reason": "联系不足"}
    draft["completed"] = True
    assert validate_score_sheet(sheet, stage="draft")["ok"] is True

    adj = sheet["adjudication"]
    adj["action"] = "conditional_proposal"
    adj["D1"] = {
        "label": "appropriate",
        "quote": "目录未知",
        "reason": "保留未知",
        "reason_codes": [],
    }
    adj["factors"][0].update(
        {"rating": "correct", "quote": "有边界方案", "reason": "ok"}
    )
    adj["factors"][1].update(
        {"rating": "correct", "quote": "取舍已连到行动", "reason": "升级"}
    )
    adj["D3"] = {"score": 2, "quote": "连贯", "reason": "条件性方案"}
    adj["D4"] = {"score": 2, "quote": "取舍", "reason": "已联系"}
    adj["completed"] = True
    agreement = draft_adjudication_agreement(sheet)
    assert agreement["comparable"] is True
    assert agreement["D1_match"] is True
    assert agreement["identity"] == "draft_adjudicator_agreement_not_inter_rater"
    assert "S5" in agreement["disagreement_clusters"]


def test_discrimination_anchors_cover_required_classes():
    payload = default_discrimination_set()
    assert len(payload["anchors"]) == 24
    assert payload["not_formal_accuracy"] is True
    assert not payload["missing_challenge_classes"]
    anchor = payload["anchors"][0]
    check = score_anchor_sheet(
        anchor,
        {
            "D1": {"label": anchor["expected_D1"]},
            "D3": {"score": anchor["expected_D3"]},
            "D4": {"score": anchor["expected_D4"]},
        },
    )
    assert check["all_match"] is True


def test_blinding_strips_identity_and_order_swap_is_deterministic():
    outward = {"technical_proposal": "拟议方案", "arm": "v2_5", "version": "leak"}
    packet = blind_single_answer_packet(
        answer_id="A1",
        task_card_public={"role": "supplier", "business_objective": "x"},
        outward=outward,
    )
    assert "arm" not in packet["outward"]
    sealed = blind_pair_packet(
        pair_id="P1",
        task_card_public={"role": "supplier"},
        answers={"v2_4": {"technical_proposal": "A"}, "v2_5": {"technical_proposal": "B"}},
        display_order=["v2_5", "v2_4"],
    )
    assert "hidden_source_order" not in sealed["rater_facing"]
    assert sealed["sealed_mapping"]["label_to_arm"]["A"] == "v2_5"
    candidates = [
        {"pair_key": f"k{i}", "role": ["contractor", "supplier", "designer", "supervisor"][i % 4], "arms": ["v2_4", "v2_5"]}
        for i in range(20)
    ]
    a = select_order_swap_pairs(candidates, seed="20261117", per_role=2)
    b = select_order_swap_pairs(candidates, seed="20261117", per_role=2)
    assert a["selection_sha256"] == b["selection_sha256"]
    assert a["count"] == 8
    all_pairs = select_order_swap_pairs(candidates, seed="20261117", all_pairs=True)
    assert all_pairs["count"] == 20
    flip = preference_after_swap("A", "B")
    assert flip["label_flip"] is True
    assert flip["stable_if_second_is_complement"] is True


def test_coverage_matrix_claim_gate_on_cp08_if_present():
    path = ROOT / "Capstone报告/验证体系/实验/2026-11-13_CP08全量微观扩样/task_cards.json"
    if not path.exists():
        pytest.skip("CP08 task cards not present")
    cards = json.loads(path.read_text(encoding="utf-8-sig"))
    matrix = build_coverage_matrix(cards)
    assert matrix["n_task_cards"] == 464
    assert matrix["acceptance_gate"]["pass"] is True
    assert "grounded_conditional_plan" in matrix["claim_gate"]["may_claim_challenge_class"]


def test_expert_slice_stratified_bounds():
    universe = [
        {"response_id": f"r{i}", "role": ["contractor", "supplier", "designer", "supervisor"][i % 4]}
        for i in range(80)
    ]
    selected = sample_expert_slice(universe, target_n=36, seed="20261117")
    assert selected["count"] == 36
    assert sum(selected["per_role_counts"].values()) == 36
    again = sample_expert_slice(universe, target_n=36, seed="20261117")
    assert selected["selection_sha256"] == again["selection_sha256"]
    with pytest.raises(ValueError):
        sample_expert_slice(universe, target_n=10)
