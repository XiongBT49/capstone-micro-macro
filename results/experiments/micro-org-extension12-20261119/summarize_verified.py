"""Recompute pooled paired scores from the two archived batches and this batch."""
import json
import sys
import zipfile
from collections import defaultdict
from pathlib import Path
from statistics import fmean

sys.path.insert(0, str(Path.cwd()))
from scripts.micro_org_judge import bootstrap_case_ci

batch = Path(__file__).resolve().parent
experiments = Path("results/experiments")


def read_file(path):
    return json.loads(path.read_text(encoding="utf8"))


def read_scores(units_file, scores_file):
    scores = defaultdict(dict)
    for line in scores_file:
        row = json.loads(line)
        if "scores" in row:
            values = {v["criterion"]: v["score"] for v in row["scores"]}
            assert set(values) == {f"R{i}" for i in range(1, 7)}
            scores[row["unit_id"]][row["order"]] = values
    pairs = defaultdict(dict)
    for line in units_file:
        u = json.loads(line)
        orders = scores[u["unit_id"]]
        if set(orders) != {"forward", "reverse"}:
            continue
        assert not u["degraded"]
        averages = {k: fmean(order[k] for order in orders.values()) for k in orders["forward"]}
        averages["overall"] = fmean(averages.values())
        key = (u["case_id"], u["pair_id"], u["unit_type"])
        assert u["arm"] not in pairs[key]
        pairs[key][u["arm"]] = averages
    return pairs


def stats(data, baseline, criterion="overall", stage=None):
    grouped = defaultdict(list)
    for (case_id, _, kind), arms in data.items():
        if (stage is None or kind == stage) and baseline in arms and "multi" in arms:
            grouped[case_id].append(arms["multi"][criterion] - arms[baseline][criterion])
    diffs = [x for group in grouped.values() for x in group]
    # Six integer ratings in each of two orders give scores in twelfths.
    def exact_mean(values):
        return sum(round(x * 12) for x in values) / (12 * len(values))
    case_means = {c: exact_mean(v) for c, v in grouped.items()}
    return dict(n=len(diffs), tasks=exact_mean(diffs), projects=fmean(case_means.values()),
                positive=sum(x > 0 for x in case_means.values()), cases=case_means,
                ci=bootstrap_case_ci(grouped))


def verify(data, summary):
    assert {k[0] for k in data} == set(summary["settings"]["cases"])
    for base in ("single", "solo"):
        result = stats(data, base)
        original = summary["pointwise_paired"][f"multi_minus_{base}"]["all"]["overall"]
        assert result["n"] == original["pairs"] and abs(result["tasks"] - original["mean_diff"]) < .00051


old = {}
for name in ("micro-org-1118", "micro-org-replication-20261119"):
    previous = experiments / name
    with zipfile.ZipFile(previous / "full_run.zip") as z:
        with z.open("judge/units.jsonl") as u, z.open("judge/pointwise.jsonl") as s:
            records = read_scores(u, s)
    verify(records, read_file(previous / "summary.json"))
    assert not ({k[0] for k in old} & {k[0] for k in records})
    old.update(records)
with (batch/"judge/units.jsonl").open(encoding="utf8") as u, (batch/"judge/pointwise.jsonl").open(encoding="utf8") as s:
    new = read_scores(u, s)
summary = read_file(batch/"judge/summary.json")
verify(new, summary)
assert {k[0] for k in new} == set(read_file(batch/"plan.json")["cases"])
assert not ({k[0] for k in old} & {k[0] for k in new})
all_pairs = old | new
assert len({k[0] for k in all_pairs}) == 12
out = ["# 十二例微观采购评分对照", "",
       "本批在运行前锁定深圳前海国际会议中心（CASE-0145）、珠海横琴创新方（CASE-0089）和深圳南山区平山综合整治项目（CASE-0202）。三例分别补充商业与办公、文旅与酒店、综合开发三类项目。原九例直接采用归档结果。", "",
       "两种单 agent 基线分别为一次决策和同角色多轮自审。三组使用同一阶段输入、每类两家候选和相同的五分量表，生成与评审模型都是 deepseek-flash。主指标取同一任务两次评分的均值，再对六个维度等权平均，报告多岗位组减去相应基线的配对分差。", "",
       "| 批次 | 对照基线 | 任务对数 | 任务平均分差 | 项目等权平均分差 | 项目重抽样 95% 区间 | 项目平均分差为正 |",
       "|---|---|---:|---:|---:|---|---:|"]
for title, data in [("原九例", old), ("本批三例", new), ("全部十二例", all_pairs)]:
    for base, label in [("single", "一次决策"), ("solo", "多轮自审")]:
        a = stats(data, base)
        low, high = a["ci"]
        out.append(f"| {title} | {label} | {a['n']} | {a['tasks']:+.3f} | {a['projects']:+.3f} | [{low:+.3f}, {high:+.3f}] | {a['positive']} / {len(a['cases'])} |")
out += ["", "## 十二例逐项目分差", "", "| 案例 | 多岗位减一次决策 | 多岗位减多轮自审 |", "|---|---:|---:|"]
single = stats(all_pairs, "single")["cases"]
solo = stats(all_pairs, "solo")["cases"]
for case in sorted(single):
    out.append(f"| {case} | {single[case]:+.3f} | {solo[case]:+.3f} |")
out += ["", "## 各维度与任务类型", "", "各维度使用同任务配对分差。每类任务行报告该类任务的六项均分之差。", "",
        "| 指标 | 新三例对一次决策 | 十二例对一次决策 | 新三例对多轮自审 | 十二例对多轮自审 |", "|---|---:|---:|---:|---:|"]
criteria = ["决策适当性", "关键事项覆盖", "可执行性", "风险与权衡", "证据忠实", "内部一致与约束遵守"]
items = [(name, f"R{i}", None) for i,name in enumerate(criteria, 1)]
for stage, name in [("owner_brief","业主招标策划"),("participation","企业投标决策"),("bid","投标文件"),("evaluation_award","评标与定标")]:
    items.append((name, "overall", stage))
for name, criterion, stage in items:
    values = [stats(src, base, criterion, stage)["tasks"] for base in ("single","solo") for src in (new, all_pairs)]
    out.append(f"| {name} | " + " | ".join(f"{v:+.3f}" for v in values) + " |")
out.extend(["", "## 运行记录与解释范围", "",
            f"本批有 {summary['units']} 份输出，{sum(row['all']['n'] for row in summary['pointwise_mean_scores'].values())} 份具有完整逐份评分。"
            f"各组共记录 {sum(v['degraded_units'] for v in summary['hard_checks'].values())} 份降级输出，评审重试后失败 {summary['judge_reliability']['judge_call_failures']} 次。阶段原始输出、审计记录和每次评审均已留存。", "",
            "分差反映微观采购文本的模型评分。评审尚未经人工校准，同一项目内的任务相关，项目区间按项目重抽样。三组计算用量不同。固定的下游输入来自多岗位组的上游产物。", "",
            "[本批评分全表](REPORT.md) · [抽样及停止规则](plan.json) · [费用记录](balance.json)"])
out += ["", "用两次评分的整数分子复核胜平负，CASE-0002 的多岗位组与多轮自审组正好持平。十二例两组的项目比较为 10 胜、1 平、1 负。先前九例的正向项目计数相应为 7 胜、1 平、1 负。浮点舍入不影响三位小数的平均分差。"]
bill = read_file(batch/"balance.json")
out.append(f"\n本批运行前后账户余额减少 ¥{bill['account_delta_cny']}，当时余额为 ¥{bill['closing_cny']}。")
(batch/"十二例评分汇总_核定.md").write_text("\n".join(out)+"\n",encoding="utf8")
