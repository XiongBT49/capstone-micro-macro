"""Blinding helpers that reduce label leakage; not true independent blind review."""

from __future__ import annotations

import hashlib
from copy import deepcopy
from typing import Any, Iterable

from src.generation_validation.common import normalize_ws, sha256_json, stable_hash_int

IDENTITY_LEAK_MARKERS = (
    "v2_4",
    "v2_5",
    "CP01",
    "CP08",
    "CP07",
    "机制",
    "原生成",
    "当前生成",
    "S4",
    "D3审议",
)


def _strip_identity_fields(obj: Any) -> Any:
    if isinstance(obj, dict):
        banned = {
            "arm",
            "version",
            "mechanism",
            "model_name",
            "model_provider",
            "cohort",
            "call_id",
            "job",
            "attempt",
            "seconds",
            "metadata",
            "grade_path",
            "response_path",
        }
        return {k: _strip_identity_fields(v) for k, v in obj.items() if k not in banned}
    if isinstance(obj, list):
        return [_strip_identity_fields(v) for v in obj]
    return obj


def _length_stats(text: str) -> dict:
    return {"chars": len(text), "approx_tokens_chars_div4": (len(text) + 3) // 4}


def _maybe_length_normalize(text: str, budget: int | None) -> tuple[str, dict]:
    stats = _length_stats(text)
    if budget is None or len(text) <= budget:
        return text, {**stats, "truncated": False, "budget": budget}
    return text[:budget] + "…", {**stats, "truncated": True, "budget": budget, "displayed_chars": budget}


def detect_identity_leak(text: str) -> list[str]:
    hits = []
    lowered = text.lower()
    for marker in IDENTITY_LEAK_MARKERS:
        if marker.lower() in lowered:
            hits.append(marker)
    return hits


def blind_single_answer_packet(
    *,
    answer_id: str,
    task_card_public: dict,
    outward: dict,
    length_budget: int | None = None,
) -> dict[str, Any]:
    """One-answer packet for scoring before any pairwise preference."""
    outward_public = _strip_identity_fields(outward)
    raw = normalize_ws(
        "\n".join(str(v) for v in outward_public.values() if not isinstance(v, (dict, list)))
    )
    display_text, length_meta = _maybe_length_normalize(
        "\n".join(
            f"{k}: {v}" if not isinstance(v, (dict, list)) else f"{k}: {v!s}"
            for k, v in outward_public.items()
        ),
        length_budget,
    )
    leaks = detect_identity_leak(display_text)
    packet = {
        "schema_version": "blind-single-answer.v1",
        "answer_id": answer_id,
        "presentation": "single_answer_before_pairwise",
        "input": _strip_identity_fields(task_card_public),
        "outward": outward_public,
        "display_text": display_text,
        "length": length_meta,
        "suspected_identity_leak_flags": leaks,
        "limitations": [
            "Stripping labels reduces cueing but cannot create true blind or independent review.",
            "Style and prompt habits may still leak mechanism identity.",
        ],
    }
    packet["packet_sha256"] = sha256_json({k: v for k, v in packet.items() if k != "packet_sha256"})
    return packet


def blind_pair_packet(
    *,
    pair_id: str,
    task_card_public: dict,
    answers: dict[str, dict],
    display_order: list[str],
    length_budget: int | None = None,
) -> dict[str, Any]:
    assert set(display_order) == set(answers)
    labeled = []
    for label, arm in zip(["A", "B"], display_order):
        single = blind_single_answer_packet(
            answer_id=f"{pair_id}-{label}",
            task_card_public=task_card_public,
            outward=answers[arm],
            length_budget=length_budget,
        )
        labeled.append(
            {
                "label": label,
                "outward": single["outward"],
                "display_text": single["display_text"],
                "length": single["length"],
                "suspected_identity_leak_flags": single["suspected_identity_leak_flags"],
            }
        )
    packet = {
        "schema_version": "blind-pair.v1",
        "pair_id": pair_id,
        "presentation": "pairwise_after_single_scores",
        "input": _strip_identity_fields(task_card_public),
        "answers_in_display_order": labeled,
        "hidden_source_order": display_order,
        "limitations": [
            "Hidden source order must stay in the sealed mapping, not the rater-facing packet.",
            "Order-swap checks same-assistant sensitivity only.",
        ],
    }
    # Rater-facing copy must not include hidden_source_order.
    rater_facing = deepcopy(packet)
    rater_facing.pop("hidden_source_order", None)
    rater_facing["packet_sha256"] = sha256_json(
        {k: v for k, v in rater_facing.items() if k != "packet_sha256"}
    )
    sealed = {
        "rater_facing": rater_facing,
        "sealed_mapping": {
            "pair_id": pair_id,
            "display_order_arms": display_order,
            "label_to_arm": {"A": display_order[0], "B": display_order[1]},
        },
    }
    sealed["sealed_sha256"] = sha256_json(sealed)
    return sealed


def select_order_swap_pairs(
    candidates: Iterable[dict],
    *,
    seed: str = "20261117",
    per_role: int | None = 3,
    all_pairs: bool = False,
    role_key: str = "role",
    id_key: str = "pair_key",
) -> dict[str, Any]:
    """Select order-swap pairs by fixed hash. all_pairs=True keeps the full set."""
    rows = list(candidates)
    if all_pairs:
        selected = sorted(rows, key=lambda r: (r.get(role_key) or "", r.get(id_key) or ""))
        mode = "all_version_or_org_pairs"
    else:
        by_role: dict[str, list[dict]] = {}
        for row in rows:
            by_role.setdefault(row.get(role_key) or "unknown", []).append(row)
        selected = []
        for role, group in sorted(by_role.items()):
            ranked = sorted(
                group,
                key=lambda r: stable_hash_int(role, str(r.get(id_key)), seed=seed),
            )
            take = ranked if per_role is None else ranked[:per_role]
            selected.extend(take)
        mode = f"stratified_per_role_{per_role}"
    pairs = []
    for index, row in enumerate(selected, 1):
        arms = list(row.get("arms") or ["v2_4", "v2_5"])
        assert len(arms) == 2
        flip = stable_hash_int("order", str(row.get(id_key)), seed=seed) % 2
        first = arms if flip == 0 else list(reversed(arms))
        pairs.append(
            {
                "pair_id": f"SWAP-{index:03d}",
                "selection": deepcopy(row),
                "first_presentation_order": first,
                "second_presentation_order": list(reversed(first)),
                "state": "selected_not_judged",
            }
        )
    material = sha256_json({"seed": seed, "mode": mode, "pair_ids": [p["pair_id"] for p in pairs]})
    return {
        "schema_version": "order-swap-selection.v1",
        "seed": seed,
        "mode": mode,
        "count": len(pairs),
        "pairs": pairs,
        "selection_sha256": material,
        "limitations": [
            "Fixed-hash selection; do not refilter by preference after seeing outcomes.",
            "Reports same-assistant order sensitivity, not independent expert agreement.",
        ],
    }


def preference_after_swap(first_pref: str, second_pref: str) -> dict[str, Any]:
    """Map A/B preferences across swapped presentation into arm-stable outcome."""
    return {
        "first_preference_label": first_pref,
        "second_preference_label": second_pref,
        "label_flip": first_pref in {"A", "B"}
        and second_pref in {"A", "B"}
        and first_pref != second_pref,
        "stable_if_second_is_complement": first_pref in {"A", "B"}
        and second_pref == ({"A": "B", "B": "A"}[first_pref]),
    }
