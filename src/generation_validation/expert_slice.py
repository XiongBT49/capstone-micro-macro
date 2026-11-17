"""Thin external-credibility expert slice: stratified sample + packets."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable

from src.generation_validation.blinding import blind_single_answer_packet
from src.generation_validation.common import sha256_json, stable_hash_int
from src.generation_validation.score_sheet import blank_score_sheet


def sample_expert_slice(
    universe: Iterable[dict],
    *,
    target_n: int = 36,
    seed: str = "20261117",
    role_key: str = "role",
    id_key: str = "response_id",
) -> dict[str, Any]:
    """Sample ~24–48 answers stratified by role with a fixed hash seed."""
    rows = list(universe)
    if target_n < 24 or target_n > 48:
        raise ValueError("Expert slice target_n must be in [24, 48]")
    by_role: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_role[row.get(role_key) or "unknown"].append(row)
    roles = sorted(by_role)
    if not roles:
        return {
            "schema_version": "expert-slice.v1",
            "seed": seed,
            "target_n": target_n,
            "selected": [],
            "count": 0,
            "note": "empty_universe",
        }
    base = target_n // len(roles)
    remainder = target_n % len(roles)
    selected = []
    for index, role in enumerate(roles):
        quota = base + (1 if index < remainder else 0)
        ranked = sorted(
            by_role[role],
            key=lambda r: stable_hash_int(role, str(r.get(id_key)), seed=seed),
        )
        take = ranked[:quota]
        for row in take:
            selected.append({**row, "slice_role_quota": quota})
    # If some roles are thin, backfill from remaining pool by hash.
    selected_ids = {str(r.get(id_key)) for r in selected}
    if len(selected) < target_n:
        rest = [
            r
            for r in rows
            if str(r.get(id_key)) not in selected_ids
        ]
        rest = sorted(rest, key=lambda r: stable_hash_int("backfill", str(r.get(id_key)), seed=seed))
        for row in rest:
            if len(selected) >= target_n:
                break
            selected.append({**row, "slice_role_quota": "backfill"})
            selected_ids.add(str(row.get(id_key)))
    payload = {
        "schema_version": "expert-slice.v1",
        "seed": seed,
        "target_n": target_n,
        "count": len(selected),
        "roles": roles,
        "per_role_counts": {
            role: sum(1 for r in selected if (r.get(role_key) or "unknown") == role)
            for role in roles
        },
        "selected": selected,
        "protocol": [
            "Experts use the same citation score-sheet schema.",
            "Compare expert labels to existing AI-assisted labels; report agreement and divergences.",
            "Do not replace frozen official grades; store expert labels under a new path.",
            "This slice supports external credibility, not full re-score.",
        ],
    }
    payload["selection_sha256"] = sha256_json(
        {k: v for k, v in payload.items() if k != "selection_sha256"}
    )
    return payload


def build_expert_packet(
    *,
    item: dict,
    task_card: dict,
    outward: dict,
    mechanical_gates: dict | None = None,
    detailed_required: bool = False,
) -> dict[str, Any]:
    public_input = {
        k: task_card.get(k)
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
        if k in task_card
    }
    answer_id = str(item.get("response_id") or item.get("window_id") or "item")
    blinded = blind_single_answer_packet(
        answer_id=answer_id,
        task_card_public=public_input,
        outward=outward,
    )
    sheet = blank_score_sheet(
        response_ref={
            "response_id": answer_id,
            "cohort": item.get("cohort"),
            "window_id": item.get("window_id"),
        },
        task_card=task_card,
        mechanical_gates=mechanical_gates,
        detailed_required=detailed_required,
    )
    # Expert sheet uses adjudication slot only; draft remains unused.
    sheet["state"] = (
        "gates_failed_hold_for_triage"
        if mechanical_gates and not mechanical_gates.get("eligible_for_business_scoring", True)
        else "awaiting_draft"
    )
    sheet["adjudication"]["reviewer"] = "external_domain_expert"
    sheet["adjudication"]["independent_expert"] = True
    sheet["adjudication"]["blinded_presentation"] = True
    return {
        "schema_version": "expert-packet.v1",
        "blinded_presentation": blinded,
        "score_sheet": sheet,
        "ai_assisted_grade_ref": item.get("existing_grade_path"),
        "limitations": [
            "Packet hides arm/version labels where possible; style may still leak.",
            "Expert labels are stored separately from frozen AI-assisted grades.",
        ],
    }
