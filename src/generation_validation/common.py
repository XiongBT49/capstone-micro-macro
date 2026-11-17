from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
RESEARCH_DIR = ROOT / "research" / "generation_validation"
RESULTS_DIR = ROOT / "results" / "experiments" / "generation_validation_enhancement_20261117"

PRIVATE_FIELDS = frozenset({"thoughts", "company_assessment"})

ROLE_REQUIRED_PUBLIC_FIELDS = {
    "contractor": [
        "technical_proposal",
        "implementation_plan",
        "quotation",
        "schedule_commitment",
        "risk_response",
        "submission_summary",
        "task_role",
    ],
    "supplier": [
        "technical_proposal",
        "implementation_plan",
        "quotation",
        "schedule_commitment",
        "risk_response",
        "submission_summary",
        "task_role",
    ],
    "designer": [
        "technical_proposal",
        "implementation_plan",
        "schedule_commitment",
        "risk_response",
        "submission_summary",
        "task_role",
    ],
    "supervisor": [
        "technical_proposal",
        "implementation_plan",
        "schedule_commitment",
        "risk_response",
        "submission_summary",
        "task_role",
    ],
}

ROLE_FACTOR_PREFIX = {
    "contractor": "C",
    "supplier": "S",
    "designer": "D",
    "supervisor": "V",
}

D1_REASON_CODES = (
    "ungrounded_promise",
    "ungrounded_refuse",
    "scope_overrun",
    "fake_threshold",
    "role_mismatch",
    "other",
)

CHALLENGE_CLASSES = (
    "grounded_conditional_plan",
    "ungrounded_commitment",
    "grounded_deferral",
    "empty_wait_or_laundry_list",
    "grounded_refuse_with_boundary",
    "partial_d2_with_contradiction",
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def sha256_json(value: Any) -> str:
    return sha256_text(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")))


def read_json(path: Path | str) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write_json(path: Path | str, value: Any) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def flatten_strings(value: Any) -> list[str]:
    out: list[str] = []
    if value is None:
        return out
    if isinstance(value, str):
        out.append(value)
    elif isinstance(value, dict):
        for item in value.values():
            out.extend(flatten_strings(item))
    elif isinstance(value, list):
        for item in value:
            out.extend(flatten_strings(item))
    else:
        out.append(str(value))
    return out


def public_text(payload: dict | None) -> str:
    if not isinstance(payload, dict):
        return ""
    public = {k: v for k, v in payload.items() if k not in PRIVATE_FIELDS}
    return "\n".join(flatten_strings(public))


def content_view(data: dict) -> tuple[dict | None, dict]:
    """Mirror review_capstone_all content_view without importing scripts."""
    payload = data.get("parsed")
    if isinstance(payload, dict):
        return {k: v for k, v in payload.items() if k not in PRIVATE_FIELDS}, {
            "mode": "original_parsed_public_fields"
        }
    raw = data.get("raw_content", "")
    if not isinstance(raw, str) or not raw.strip():
        return None, {"mode": "no_raw_answer"}
    decoder, offset, objects = json.JSONDecoder(), 0, []
    try:
        while offset < len(raw):
            while offset < len(raw) and raw[offset].isspace():
                offset += 1
            if offset == len(raw):
                break
            start = offset
            obj, offset = decoder.raw_decode(raw, offset)
            if not isinstance(obj, dict):
                return None, {"mode": "non_object_or_ambiguous_raw"}
            public = {k: v for k, v in obj.items() if k not in PRIVATE_FIELDS}
            objects.append({"public": public, "start": start, "end": offset})
    except (ValueError, TypeError):
        return None, {"mode": "unparsed_raw_needs_manual_review"}
    candidates = [(i, obj) for i, obj in enumerate(objects) if obj["public"]]
    if len(candidates) != 1:
        return None, {
            "mode": "multiple_or_no_public_objects_not_merged",
            "top_level_object_count": len(objects),
        }
    index, selected = candidates[0]
    return selected["public"], {
        "mode": "unique_public_object_content_read_only",
        "top_level_object_count": len(objects),
        "selected_object_index": index,
        "raw_object_start": selected["start"],
        "raw_object_end": selected["end"],
        "original_program_status_unchanged": True,
    }


def stable_hash_int(*parts: str, seed: str = "20261117") -> int:
    material = "|".join([seed, *parts])
    return int(sha256_text(material)[:16], 16)


_WS = re.compile(r"\s+")


def normalize_ws(text: str) -> str:
    return _WS.sub(" ", text).strip()
