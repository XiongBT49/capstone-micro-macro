"""Role × materials × condition × tradeoff coverage before more formal scoring."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any, Iterable

from src.generation_validation.common import CHALLENGE_CLASSES, sha256_json

TRADEOFF_MARKERS = (
    "取舍",
    "权衡",
    "代价",
    "备选",
    "边界",
    "tradeoff",
    "trade-off",
)


def _condition_bucket(card: dict) -> str:
    conditions = card.get("conditions") or []
    if not conditions:
        return "no_conditions"
    statuses = [c.get("status") for c in conditions if isinstance(c, dict)]
    if any(s in {"requested", "unresolved", "pending"} for s in statuses):
        return "has_unresolved_conditions"
    if statuses and all(s in {"verified", "resolved", "waived"} for s in statuses):
        return "all_resolved_or_waived"
    return "mixed_or_other_conditions"


def _tradeoff_signal(card: dict) -> str:
    blobs = []
    for factor in card.get("factors") or []:
        blobs.append(str(factor.get("label") or ""))
        blobs.append(str(factor.get("adequate_handling") or ""))
    blobs.append(str(card.get("business_objective") or ""))
    text = "\n".join(blobs)
    if any(marker in text for marker in TRADEOFF_MARKERS):
        return "tradeoff_prompted_in_card"
    # Role factor tails C5/S5/D5/V5 are project-specific tradeoff slots in this corpus.
    ids = {f.get("factor_id") for f in card.get("factors") or []}
    if ids & {"C5", "S5", "D5", "V5"}:
        return "role_tail_tradeoff_factor_present"
    return "no_explicit_tradeoff_signal"


def _challenge_coverage_from_card(card: dict) -> dict[str, bool]:
    """Input-side opportunity for discrimination — not whether answers exhibited it."""
    variant = card.get("variant")
    cond = _condition_bucket(card)
    tradeoff = _tradeoff_signal(card)
    return {
        "grounded_conditional_plan": variant in {"full", "missing_core"},
        "ungrounded_commitment": True,  # always scorable failure mode
        "grounded_deferral": variant == "missing_core" or cond == "has_unresolved_conditions",
        "empty_wait_or_laundry_list": True,
        "grounded_refuse_with_boundary": True,
        "partial_d2_with_contradiction": True,
        "tradeoff_discrimination_possible": tradeoff != "no_explicit_tradeoff_signal",
        "materials_discrimination_slot": variant in {"full", "missing_core"},
        "condition_discrimination_slot": cond == "has_unresolved_conditions",
    }


def build_coverage_matrix(task_cards: Iterable[dict]) -> dict[str, Any]:
    cards = list(task_cards)
    cell_counts: Counter = Counter()
    challenge_counts: Counter = Counter()
    role_variant = Counter()
    examples: dict[str, list[str]] = defaultdict(list)

    for card in cards:
        role = card.get("role") or "unknown"
        variant = card.get("variant") or "unknown"
        cond = _condition_bucket(card)
        tradeoff = _tradeoff_signal(card)
        cell = f"{role}|{variant}|{cond}|{tradeoff}"
        cell_counts[cell] += 1
        role_variant[f"{role}|{variant}"] += 1
        if len(examples[cell]) < 3:
            examples[cell].append(card.get("window_id") or card.get("case_id") or "")
        for key, present in _challenge_coverage_from_card(card).items():
            if present:
                challenge_counts[key] += 1

    required_roles = ["contractor", "supplier", "designer", "supervisor"]
    required_variants = ["full", "missing_core"]
    missing_role_variant = [
        f"{role}|{variant}"
        for role in required_roles
        for variant in required_variants
        if role_variant[f"{role}|{variant}"] == 0
    ]
    uncovered_challenges = [
        name for name in CHALLENGE_CLASSES if challenge_counts.get(name, 0) == 0
    ]
    claim_gate = {
        "may_claim_challenge_class": sorted(
            name for name in CHALLENGE_CLASSES if challenge_counts.get(name, 0) > 0
        ),
        "must_narrow_or_not_claim": uncovered_challenges,
        "rule": "If a challenge class has zero covered tasks, narrow the paper claim; do not hunt discriminating items after seeing outcomes.",
    }
    matrix = {
        "schema_version": "coverage-matrix.v1",
        "n_task_cards": len(cards),
        "cells": [
            {
                "role": key.split("|")[0],
                "variant": key.split("|")[1],
                "condition_bucket": key.split("|")[2],
                "tradeoff_signal": key.split("|")[3],
                "count": count,
                "example_window_ids": examples[key],
            }
            for key, count in sorted(cell_counts.items())
        ],
        "role_variant_counts": dict(sorted(role_variant.items())),
        "missing_role_variant_slots": missing_role_variant,
        "challenge_class_input_coverage_counts": dict(sorted(challenge_counts.items())),
        "claim_gate": claim_gate,
        "acceptance_gate": {
            "pass": not missing_role_variant and not uncovered_challenges,
            "missing_role_variant_slots": missing_role_variant,
            "uncovered_challenge_classes": uncovered_challenges,
        },
    }
    matrix["matrix_sha256"] = sha256_json({k: v for k, v in matrix.items() if k != "matrix_sha256"})
    return matrix
