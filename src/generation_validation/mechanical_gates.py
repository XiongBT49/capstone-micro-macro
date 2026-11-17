"""Mechanical gates that never assign D1–D4 business grades."""

from __future__ import annotations

import re
from typing import Any

from src.generation_validation.common import (
    ROLE_REQUIRED_PUBLIC_FIELDS,
    content_view,
    normalize_ws,
    public_text,
    sha256_json,
)

# Heuristic surface patterns only. Hits are gate codes for human/AI adjudication,
# not automatic appropriateness labels.
PATTERN_SPECS = (
    {
        "code": "ungrounded_promise",
        "patterns": [
            r"已(经)?(核实|确认|批准|落实|签订|中标)",
            r"保证(中标|签约|通过审核)",
            r"已经具备(全部|所有).*(能力|资源|资质)",
        ],
    },
    {
        "code": "ungrounded_refuse",
        "patterns": [
            r"因(缺乏|没有|不具备).*(能力|资格|经验).*(拒绝|不参与|放弃)",
            r"明确拒绝.{0,20}(但未说明|无理由)",
        ],
    },
    {
        "code": "scope_overrun",
        "patterns": [
            r"承担整包(施工|设计采购施工|EPC)责任",
            r"作为(总承包|施工总承包)完成全部工程",
        ],
    },
    {
        "code": "fake_threshold",
        "patterns": [
            r"必须先完成.{0,30}才能提交(意向|草案|草稿)",
            r"未完成审核不得形成(草案|意向)",
        ],
    },
)

INVENTED_FACT_SPECS = (
    {
        "code": "claims_verified_while_unresolved",
        "patterns": [
            r"(核查|审核|条件).{0,12}(已通过|已确认|已解决)",
            r"verified_condition",
        ],
    },
    {
        "code": "claims_known_resource_while_unknown",
        "patterns": [
            r"(库存|本地团队|实际派驻|已确认档期).{0,8}(已就绪|充足|落实)",
            r"现有产品目录齐全",
        ],
    },
)


def _match_codes(text: str, specs: tuple[dict, ...]) -> list[dict]:
    hits = []
    for spec in specs:
        for pattern in spec["patterns"]:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                hits.append(
                    {
                        "code": spec["code"],
                        "pattern": pattern,
                        "span": match.group(0),
                        "start": match.start(),
                        "end": match.end(),
                    }
                )
                break
    return hits


def _section_presence(payload: dict, role: str | None) -> dict:
    required = ROLE_REQUIRED_PUBLIC_FIELDS.get(role or "", [])
    present = []
    missing = []
    empty = []
    for field in required:
        if field not in payload:
            missing.append(field)
            continue
        value = payload[field]
        if value is None or value == "" or value == [] or value == {}:
            empty.append(field)
        else:
            present.append(field)
    return {
        "role": role,
        "required_fields": required,
        "present": present,
        "missing": missing,
        "empty": empty,
        "all_required_nonempty": not missing and not empty,
    }


def _invented_fact_flags(payload: dict, task_card: dict | None) -> list[dict]:
    text = public_text(payload)
    flags = _match_codes(text, INVENTED_FACT_SPECS)
    if not isinstance(task_card, dict):
        return flags
    not_supplied = {normalize_ws(str(x)).lower() for x in task_card.get("not_supplied") or []}
    unresolved = {
        c.get("condition_id")
        for c in (task_card.get("conditions") or [])
        if isinstance(c, dict) and c.get("status") in {"requested", "unresolved", "pending"}
    }
    verified_ids = set(payload.get("verified_condition_ids") or [])
    leaked = sorted(verified_ids & unresolved)
    if leaked:
        flags.append(
            {
                "code": "marks_unresolved_condition_verified",
                "pattern": "verified_condition_ids ∩ unresolved task conditions",
                "span": ",".join(leaked),
                "start": None,
                "end": None,
            }
        )
    joined = text.lower()
    for item in not_supplied:
        if not item:
            continue
        # Only flag when the answer asserts availability of an explicitly unsupplied resource class.
        if item in joined and re.search(rf"{re.escape(item)}.{{0,20}}(已|齐全|落实|确认)", joined):
            flags.append(
                {
                    "code": "asserts_not_supplied_as_available",
                    "pattern": item,
                    "span": item,
                    "start": None,
                    "end": None,
                }
            )
    return flags


def run_mechanical_gates(
    response: dict,
    *,
    task_card: dict | None = None,
    role: str | None = None,
) -> dict[str, Any]:
    """Return gate codes only. Does not score D1–D4."""
    payload, view = content_view(response)
    role = role or (task_card or {}).get("role") or (payload or {}).get("task_role")
    readable = isinstance(payload, dict)
    sections = _section_presence(payload, role) if readable else {
        "role": role,
        "required_fields": ROLE_REQUIRED_PUBLIC_FIELDS.get(role or "", []),
        "present": [],
        "missing": ROLE_REQUIRED_PUBLIC_FIELDS.get(role or "", []),
        "empty": [],
        "all_required_nonempty": False,
    }
    text = public_text(payload) if readable else ""
    pattern_flags = _match_codes(text, PATTERN_SPECS) if readable else []
    invented_flags = _invented_fact_flags(payload, task_card) if readable else []
    blocking = []
    if not readable:
        blocking.append("unreadable_or_ambiguous")
    if readable and not sections["all_required_nonempty"]:
        blocking.append("required_sections_incomplete")
    soft = []
    if pattern_flags:
        soft.append("d1_taxonomy_pattern_hits")
    if invented_flags:
        soft.append("possible_invented_fact_hits")
    result = {
        "schema_version": "mechanical-gates.v1",
        "assigns_business_grades": False,
        "program_status_retained": response.get("status"),
        "content_review_read_view": view,
        "readable": readable,
        "role": role,
        "section_presence": sections,
        "pattern_flags": pattern_flags,
        "invented_fact_flags": invented_flags,
        "blocking_codes": blocking,
        "soft_codes": soft,
        "passed_mechanical_gates": not blocking,
        "eligible_for_business_scoring": readable and not blocking,
        "notes": [
            "Gate failures are structured codes for triage.",
            "Soft pattern hits never auto-set D1 inappropriate/appropriate.",
            "Business D1–D4 remain author-assisted judgments with citations.",
        ],
    }
    result["result_sha256"] = sha256_json(
        {k: v for k, v in result.items() if k != "result_sha256"}
    )
    return result
