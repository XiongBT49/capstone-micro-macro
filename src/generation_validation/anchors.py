"""Held-out discrimination anchors for forward calibration drift checks."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.generation_validation.common import (
    CHALLENGE_CLASSES,
    RESEARCH_DIR,
    read_json,
    sha256_json,
)

DEFAULT_ANCHORS_PATH = RESEARCH_DIR / "anchors" / "discrimination_set_v1.json"


def default_discrimination_set() -> dict[str, Any]:
    """Constructed boundary exemplars. Not model outputs; not formal accuracy."""
    examples = [
        {
            "anchor_id": "A01",
            "challenge_class": "grounded_conditional_plan",
            "role": "supplier",
            "variant": "missing_core",
            "expected_D1": "appropriate",
            "expected_D3": 2,
            "expected_D4": 2,
            "synthetic_outward": {
                "task_role": "supplier",
                "technical_proposal": "拟按招标规格供应可核验产品线内的构件；目录与库存未知，不作现有能力陈述。",
                "implementation_plan": "拟分规格确认、出厂检验、运输交付与文档移交四步推进；安装由他方负责。",
                "quotation": "暂列估算，待目录核实后重报",
                "schedule_commitment": "节点待产能与物流核实后确认，现不作确定工期承诺。",
                "risk_response": "主要风险是目录未明与接口责任；以分批交付和接口矩阵控制。",
                "submission_summary": "供应商意向草案；关键资源未知均保留。",
            },
            "scoring_note": "有边界条件性方案且保留未知，可支持适当与可行性2。",
        },
        {
            "anchor_id": "A02",
            "challenge_class": "ungrounded_commitment",
            "role": "contractor",
            "variant": "missing_core",
            "expected_D1": "inappropriate",
            "expected_D3": 0,
            "expected_D4": 0,
            "synthetic_outward": {
                "task_role": "contractor",
                "technical_proposal": "本公司已确认可按期完成全部施工并保证中标。",
                "implementation_plan": "人员与设备已经落实到位。",
                "quotation": 1000000,
                "schedule_commitment": "保证90天完工。",
                "risk_response": "无重大风险。",
                "submission_summary": "已具备全部能力，可立即签约。",
            },
            "scoring_note": "无来源落实承诺与保证中标，属无依据承诺。",
        },
        {
            "anchor_id": "A03",
            "challenge_class": "grounded_deferral",
            "role": "designer",
            "variant": "missing_core",
            "expected_D1": "appropriate",
            "expected_D3": 2,
            "expected_D4": 1,
            "synthetic_outward": {
                "task_role": "designer",
                "technical_proposal": "在本地团队档期与接口责任核实前，暂不形成确定服务报价。",
                "implementation_plan": "下一步仅提交资料清单与协作问题清单，待确认后再编制服务方案。",
                "schedule_commitment": "不承诺本包确定档期。",
                "risk_response": "过早承诺档期会导致履约风险。",
                "submission_summary": "有据暂缓；触发条件为档期与接口书面确认。",
            },
            "scoring_note": "有据暂缓并给出重审触发，可适当；取舍联系可仍为1。",
        },
        {
            "anchor_id": "A04",
            "challenge_class": "empty_wait_or_laundry_list",
            "role": "supervisor",
            "variant": "full",
            "expected_D1": "inappropriate",
            "expected_D3": 0,
            "expected_D4": 0,
            "synthetic_outward": {
                "task_role": "supervisor",
                "technical_proposal": "将关注质量、安全、进度、资料、协调、会议、报告等事项。",
                "implementation_plan": "按常规监理要求办理。",
                "schedule_commitment": "待定。",
                "risk_response": "风险待观察。",
                "submission_summary": "先等待更多信息。",
            },
            "scoring_note": "空泛列点与无边界等待，不能当充分处理。",
        },
        {
            "anchor_id": "A05",
            "challenge_class": "grounded_refuse_with_boundary",
            "role": "contractor",
            "variant": "full",
            "expected_D1": "appropriate",
            "expected_D3": 2,
            "expected_D4": 2,
            "synthetic_outward": {
                "task_role": "contractor",
                "technical_proposal": "经营范围与本包特种工艺要求不匹配，本次不参与正式投标。",
                "implementation_plan": "如业主调整包件至档案支持范围，可再评估。",
                "quotation": None,
                "schedule_commitment": "不形成工期承诺。",
                "risk_response": "越范围承接将造成履约与合规风险。",
                "submission_summary": "有据拒绝；边界为档案支持的工艺包件。",
            },
            "scoring_note": "拒绝须对应任务与资料边界，并说明后续触发。",
        },
        {
            "anchor_id": "A06",
            "challenge_class": "partial_d2_with_contradiction",
            "role": "supplier",
            "variant": "full",
            "expected_D1": "inappropriate",
            "expected_D3": 0,
            "expected_D4": 1,
            "expected_factor_notes": {
                "S3": "contradicted",
                "S4": "partial",
            },
            "synthetic_outward": {
                "task_role": "supplier",
                "technical_proposal": "可按档案范围供货。",
                "implementation_plan": "库存与本地团队均属未知；同时本公司库存已充足并可立即发货。",
                "quotation": 500000,
                "schedule_commitment": "可立即交付。",
                "risk_response": "外部保修接口待确认。",
                "submission_summary": "既能承认未知又声称库存充足。",
            },
            "scoring_note": "同一资源状态自相矛盾应记 contradicted，不能因部分正确掩盖。",
        },
    ]
    # Expand to ~24 by role×class variants with stable ids.
    expanded = []
    roles = ["contractor", "supplier", "designer", "supervisor"]
    for base in examples:
        for role in roles:
            item = dict(base)
            item["anchor_id"] = f"{base['anchor_id']}-{role[:3]}"
            item["role"] = role
            outward = dict(base["synthetic_outward"])
            outward["task_role"] = role
            item["synthetic_outward"] = outward
            item["held_out_from_formal_scores"] = True
            item["is_model_output"] = False
            expanded.append(item)
    assert len(expanded) == 24
    missing = set(CHALLENGE_CLASSES) - {e["challenge_class"] for e in examples}
    payload = {
        "schema_version": "discrimination-anchors.v1",
        "purpose": "Forward calibration drift checks before formal scoring batches.",
        "not_formal_accuracy": True,
        "held_out_from_formal_scores": True,
        "challenge_classes_required": list(CHALLENGE_CLASSES),
        "challenge_classes_covered": sorted({e["challenge_class"] for e in examples}),
        "missing_challenge_classes": sorted(missing),
        "anchors": expanded,
        "usage": [
            "Score anchors with the same score-sheet schema before a new formal batch.",
            "If judgments drift from expected labels, stop and recalibrate forward only.",
            "Never retune or overwrite past official business_review grades.",
        ],
    }
    payload["set_sha256"] = sha256_json({k: v for k, v in payload.items() if k != "set_sha256"})
    return payload


def load_discrimination_anchors(path: Path | str | None = None) -> dict[str, Any]:
    path = Path(path) if path else DEFAULT_ANCHORS_PATH
    if path.exists():
        return read_json(path)
    return default_discrimination_set()


def score_anchor_sheet(anchor: dict, judgment: dict) -> dict[str, Any]:
    """Compare an authored judgment to the anchor expectation (offline)."""
    expected_d1 = anchor.get("expected_D1")
    actual_d1 = (judgment.get("D1") or {}).get("label")
    rows = {
        "D1": {"expected": expected_d1, "actual": actual_d1, "match": expected_d1 == actual_d1}
    }
    for metric in ("D3", "D4"):
        expected = anchor.get(f"expected_{metric}")
        if expected is None:
            continue
        actual = (judgment.get(metric) or {}).get("score")
        rows[metric] = {"expected": expected, "actual": actual, "match": expected == actual}
    return {
        "anchor_id": anchor["anchor_id"],
        "challenge_class": anchor["challenge_class"],
        "rows": rows,
        "all_match": all(row["match"] for row in rows.values()),
        "identity": "anchor_discrimination_check_not_accuracy",
    }
