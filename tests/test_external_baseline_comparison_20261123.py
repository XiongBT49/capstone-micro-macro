"""Checks for the offline external-baseline comparison."""
from scripts.compare_external_baselines_20261123 import (
    award_publication_metrics,
    declared_weights,
    median_value,
    parse_duration,
    r2_level,
    r3_level,
    requirement_stems,
    score_bid_document,
    score_observed_agreement,
    supports,
    topsis_groups,
)


def test_declared_weights_keep_only_written_percentages():
    weights = declared_weights(["评标标准提示：工程造价 50%  施工期 15%  工作计划 15%  施工经验及质量 20%"])
    assert weights == {"price": 50.0, "duration": 15.0, "work_plan": 15.0, "experience_quality": 20.0}
    assert declared_weights(["评标标准提示：无法获取（仅有开标结果）"]) is None


def test_duration_uses_one_stated_total_and_rejects_a_conflict():
    assert parse_duration("总工期14周，自开工令下达之日起计算。") == (14.0, "周")
    assert parse_duration("设计周期为22周，自合同生效起计算。") == (22.0, "周")
    assert parse_duration("合同签订后12周内完成全部材料交付。") == (12.0, "周")
    assert parse_duration("总工期14周。另一处写总工期16周。") is None


def test_topsis_ranks_the_lower_price_first_when_price_is_a_cost():
    groups = topsis_groups([[100.0], [200.0]], [1.0], [-1])
    assert groups[0] == [0]
    assert groups[1] == [1]


def test_bid_rubric_counts_follow_the_published_levels():
    assert r2_level(7, 0) == 5
    assert r2_level(6, 1) == 4
    assert r2_level(5, 0) == 3
    assert r2_level(3, 0) == 2
    assert r2_level(2, 0) == 1
    assert r3_level(5) == 5
    assert r3_level(0) == 1
    bid = {
        "bid_id": "b1",
        "bidder_id": "c1",
        "technical_proposal": "针对本包排放管改道的施工方案，包含管线保护、交通导改和污水厂运行保障，并说明各工序的做法。",
        "implementation_plan": "阶段一于第2周完成管线探测、保护和交通导改方案报批。阶段二于第8周完成管道安装、试压和闭水试验。",
        "quotation": 100.0,
        "quotation_breakdown": [{"item": "管道", "amount": 100, "basis": "按清单"}],
        "schedule_commitment": "总工期10周。",
        "compliance_statement": "第4周向业主提交审查节点所需的施工方案、检验记录和整改回复。",
        "risk_response": "若施工中发现未知管线，由项目经理负责停工、通知业主并组织抢修。",
        "submission_summary": "报价假设材料价格在签订时锁定。",
    }
    scored = score_bid_document(bid)
    assert scored["R2"] == 5
    assert scored["R3"] == 5
    assert scored["R6"] is None
    assert scored["price_lines_closed"] is True
    assert scored["R1"] is None
    bid["quotation_breakdown"] = [{"item": "管道", "amount": 40, "basis": "按清单"}]
    assert score_bid_document(bid)["R6"] == 2


def test_consortium_preferences_ignore_the_agreement_text():
    assert requirement_stems("结构协调能力") == ["结构"]
    assert supports(["结构"], "具备结构设计能力")
    assert not supports(["结构"], "具备交通工程经验")
    selected = {
        "consortium": {
            "status": "formed",
            "role_split": {"A": "负责结构", "B": "负责文档"},
        }
    }
    issues = [
        {"requirement": "结构协调能力", "stems": ["结构"], "supported_by": ["A"]},
        {"requirement": "文档编制能力", "stems": ["文档"], "supported_by": ["B"]},
    ]
    scored = score_observed_agreement(selected, issues, ["A", "B"])
    assert scored["agreement_success"] is True
    assert scored["utility"] == {"A": 15, "B": 15}
    assert scored["each_party_clears_threshold"] == {"A": True, "B": True}
    partial = score_observed_agreement(
        {"consortium": {"status": "formed", "role_split": {"A": "负责结构", "B": "配合"}}},
        issues,
        ["A", "B"],
    )
    assert partial["utility"] == {"A": 10, "B": 5}
    assert partial["each_party_clears_threshold"] == {"A": False, "B": False}
    assert partial["agreement_success"] is False
    selected["consortium"]["role_split"] = {"A": "负责全部未点名的工作", "B": "配合"}
    missed = score_observed_agreement(selected, issues, ["A", "B"])
    assert missed["agreement_success"] is False
    assert missed["utility"] == {"A": 0, "B": 0}


def _package(case_id, package_id, winner, groups, prices):
    return {
        "case_id": case_id,
        "package_id": package_id,
        "winner_in_matrix": True,
        "winner_in_top_group": winner in groups[0],
        "top_group_is_unique": len(groups[0]) == 1,
        "topsis_ranking_high_to_low": groups,
        "award_winner": winner,
        "bidders": [{"bidder_id": bidder, "price": price} for bidder, price in prices.items()],
    }


def test_case_equal_award_metrics_average_cases_before_packages():
    packages = [
        _package("c1", "a", "A", [["A"], ["B"]], {"A": 10, "B": 20}),
        _package("c1", "b", "B", [["A"], ["B"]], {"A": 10, "B": 20}),
        _package("c2", "a", "A", [["A", "B"]], {"A": 10, "B": 10}),
    ]
    metrics = award_publication_metrics(packages, draws=20, seed=1)
    assert metrics["cases"] == 2
    assert metrics["top_group_agreement"]["estimate"] == 0.75
    assert metrics["chance_top_group_rate"] == 0.75
    assert metrics["agreement_minus_chance"]["estimate"] == 0
    assert metrics["mean_reciprocal_rank"]["estimate"] == 0.875
    assert metrics["relative_award_price"]["median"] == 0.5
    assert median_value([0.0, 1.0]) == 0.5
    again = award_publication_metrics(packages, draws=20, seed=1)
    assert metrics["top_group_agreement"]["ci95"] == again["top_group_agreement"]["ci95"]
