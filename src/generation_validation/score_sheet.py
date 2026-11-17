"""Structured score sheets and draft→adjudication agreement (no auto grades)."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from src.generation_validation.common import D1_REASON_CODES, sha256_json

D1_LABELS = {"appropriate", "inappropriate", "not_judgable"}
FACTOR_RATINGS = {"correct", "partial", "missing", "contradicted", "not_judgable"}
ORDINAL = {0, 1, 2, "not_judgable"}
SHEET_STATES = {
    "awaiting_mechanical_gates",
    "gates_failed_hold_for_triage",
    "awaiting_draft",
    "draft_complete_awaiting_adjudication",
    "adjudicated",
    "frozen_official_do_not_replace",
}


def blank_score_sheet(
    *,
    response_ref: dict,
    task_card: dict,
    mechanical_gates: dict | None = None,
    detailed_required: bool = False,
) -> dict[str, Any]:
    factors = []
    for factor in task_card.get("factors") or []:
        factors.append(
            {
                "id": factor["factor_id"],
                "label": factor.get("label"),
                "rating": None,
                "quote": None,
                "reason": None,
                "input_pointers": list(factor.get("input_pointers") or []),
                "criterion": factor.get("adequate_handling"),
                "defer_decline_criterion": factor.get("handling_for_supported_defer_or_decline"),
                "evidence": None,
            }
        )
    gates = mechanical_gates or {}
    if gates and not gates.get("eligible_for_business_scoring", True):
        state = "gates_failed_hold_for_triage"
    elif gates:
        state = "awaiting_draft"
    else:
        state = "awaiting_mechanical_gates"
    sheet = {
        "schema_version": "score-sheet.v1",
        "state": state,
        "response_ref": deepcopy(response_ref),
        "task_card_ref": {
            "window_id": task_card.get("window_id"),
            "project_group": task_card.get("project_group"),
            "role": task_card.get("role"),
            "variant": task_card.get("variant"),
            "case_id": task_card.get("case_id"),
        },
        "mechanical_gates": deepcopy(gates) if gates else None,
        "draft": {
            "reviewer_model_family": None,
            "reviewer_note": "Second-model draft only; never official. Adjudicator decides.",
            "action": None,
            "D1": {"label": None, "quote": None, "reason": None, "reason_codes": []},
            "factors": deepcopy(factors),
            "D3": {"score": None, "quote": None, "reason": None} if detailed_required else None,
            "D4": {"score": None, "quote": None, "reason": None} if detailed_required else None,
            "completed": False,
        },
        "adjudication": {
            "reviewer": "author_assisted_adjudicator",
            "independent_expert": False,
            "blinded_presentation": False,
            "action": None,
            "D1": {"label": None, "quote": None, "reason": None, "reason_codes": []},
            "factors": deepcopy(factors),
            "D3": {"score": None, "quote": None, "reason": None} if detailed_required else None,
            "D4": {"score": None, "quote": None, "reason": None} if detailed_required else None,
            "completed": False,
            "disagreements_with_draft": [],
        },
        "official_grade_path": None,
        "limitations": [
            "Draft–adjudicator agreement is not inter-rater reliability.",
            "Do not overwrite frozen business_review grades; append revisions only.",
            "Mechanical gates do not set D1–D4.",
        ],
    }
    sheet["sheet_sha256"] = sha256_json({k: v for k, v in sheet.items() if k != "sheet_sha256"})
    return sheet


def _require_evidence(block: dict, *, allow_missing_quote: bool = False) -> list[str]:
    errors = []
    if not isinstance(block.get("reason"), str) or not block["reason"].strip():
        errors.append("reason_required")
    quote = block.get("quote")
    if not quote and not allow_missing_quote:
        errors.append("quote_required")
    return errors


def validate_score_sheet(sheet: dict, *, stage: str = "adjudication") -> dict[str, Any]:
    """Validate draft or adjudication completeness against the sheet schema."""
    assert stage in {"draft", "adjudication"}
    errors: list[str] = []
    if sheet.get("schema_version") != "score-sheet.v1":
        errors.append("unsupported_schema_version")
    if sheet.get("state") not in SHEET_STATES:
        errors.append("invalid_state")
    body = sheet.get(stage) or {}
    d1 = body.get("D1") or {}
    if d1.get("label") not in D1_LABELS:
        errors.append(f"{stage}.D1.label_invalid")
    else:
        errors.extend(f"{stage}.D1.{e}" for e in _require_evidence(d1))
    for code in d1.get("reason_codes") or []:
        if code not in D1_REASON_CODES:
            errors.append(f"{stage}.D1.reason_code_invalid:{code}")
    factors = body.get("factors") or []
    expected = (sheet.get("draft") or {}).get("factors") or []
    if len(factors) != len(expected):
        errors.append(f"{stage}.factors_count_mismatch")
    for factor, expected_factor in zip(factors, expected):
        fid = factor.get("id")
        if fid != expected_factor.get("id"):
            errors.append(f"{stage}.factor_id_mismatch:{fid}")
        if factor.get("rating") not in FACTOR_RATINGS:
            errors.append(f"{stage}.factor_rating_invalid:{fid}")
        else:
            allow_missing = factor.get("rating") in {"missing", "not_judgable"}
            errors.extend(
                f"{stage}.factor_{fid}.{e}"
                for e in _require_evidence(factor, allow_missing_quote=allow_missing)
            )
    for metric in ("D3", "D4"):
        value = body.get(metric)
        if value is None:
            continue
        if value.get("score") not in ORDINAL:
            errors.append(f"{stage}.{metric}.score_invalid")
        else:
            errors.extend(f"{stage}.{metric}.{e}" for e in _require_evidence(value))
    if not body.get("action"):
        errors.append(f"{stage}.action_required")
    return {
        "ok": not errors,
        "stage": stage,
        "errors": errors,
        "sheet_state": sheet.get("state"),
    }


def draft_adjudication_agreement(sheet: dict) -> dict[str, Any]:
    """Report draft vs adjudication agreement. Not inter-rater kappa."""
    draft = sheet.get("draft") or {}
    adj = sheet.get("adjudication") or {}
    if not draft.get("completed") or not adj.get("completed"):
        return {
            "comparable": False,
            "reason": "draft_or_adjudication_incomplete",
            "identity": "draft_adjudicator_agreement_not_inter_rater",
        }
    d1_match = (draft.get("D1") or {}).get("label") == (adj.get("D1") or {}).get("label")
    factor_rows = []
    for d_factor, a_factor in zip(draft.get("factors") or [], adj.get("factors") or []):
        factor_rows.append(
            {
                "id": d_factor.get("id"),
                "draft": d_factor.get("rating"),
                "adjudication": a_factor.get("rating"),
                "match": d_factor.get("rating") == a_factor.get("rating"),
            }
        )
    factor_matches = sum(1 for row in factor_rows if row["match"])
    detailed = {}
    for metric in ("D3", "D4"):
        d_val = draft.get(metric)
        a_val = adj.get(metric)
        if d_val is None and a_val is None:
            continue
        detailed[metric] = {
            "draft": None if d_val is None else d_val.get("score"),
            "adjudication": None if a_val is None else a_val.get("score"),
            "match": (None if d_val is None else d_val.get("score"))
            == (None if a_val is None else a_val.get("score")),
        }
    return {
        "comparable": True,
        "identity": "draft_adjudicator_agreement_not_inter_rater",
        "D1_match": d1_match,
        "factor_agreement_rate": (factor_matches / len(factor_rows)) if factor_rows else None,
        "factor_rows": factor_rows,
        "detailed": detailed,
        "disagreement_clusters": [
            row["id"] for row in factor_rows if not row["match"]
        ]
        + (["D1"] if not d1_match else [])
        + [m for m, row in detailed.items() if not row["match"]],
    }
