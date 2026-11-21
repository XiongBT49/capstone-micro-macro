"""Score stored replies offline. Keep non-returned and non-JSON cases visible."""
import json
from collections import Counter
from decimal import Decimal
from pathlib import Path

root = Path(__file__).resolve().parent
read = lambda p: json.loads(p.read_text(encoding="utf8"))
plan = read(root/"plan.json")
jobs = plan["jobs"]
markers = {(r["window_id"],r["step"]):r["marker"] for r in read(root/"topic_markers.json")}
records = {}
usage = Counter()
for j in jobs:
    d = root/"jobs"/j["job_id"]
    if not (d/"response.json").exists():
        continue
    reply = read(d/"response.json")
    u = reply["metadata"]["response_metadata"]["token_usage"]
    usage.update({k:v for k,v in u.items() if type(v)==int})
    try:
        content = json.loads(reply["raw_content"])
        if isinstance(content,dict):
            records[j["job_id"]] = content
    except ValueError:
        pass


def correct_ids(answer,state):
    keys = ("unresolved_condition_ids","verified_condition_ids")
    return all(isinstance(answer.get(k),list) and sorted(answer[k])==sorted(state[k]) for k in keys)


def outward(answer, token):
    fields = ("reason","content","technical_proposal","implementation_plan","quotation_breakdown",
              "schedule_commitment","owner_control_response","risk_response","submission_summary","bid_assumptions")
    return any(token in json.dumps(answer.get(k),ensure_ascii=False) for k in fields)


scored = []
for j in jobs:
    key, w, arm, kind = j["job_id"], j["window_id"], j["arm"], j["ablation_kind"]
    identity = records.get(w+"__identity_"+arm)
    curr = records.get(key)
    row = dict(job=key,window=w,arm=arm,kind=kind,valid_json=curr is not None)
    if curr is not None:
        row.update(ids_correct=correct_ids(curr,j["expected"]),decision=curr.get("decision"),quotation=curr.get("quotation"))
    ref = read(root/"jobs"/key/"historical.json") if kind.startswith("identity") else identity
    if ref is not None and curr is not None:
        row.update(reference_decision=ref.get("decision"),reference_quotation=ref.get("quotation"))
        if ref.get("decision") is not None and curr.get("decision") is not None:
            row["change_intent"] = ref["decision"] != curr["decision"]
        if kind.startswith("dropout"):
            term = markers[w,int(kind[-1])]
            historical = read(root/"jobs"/(w+"__identity_D3")/"historical.json")
            row.update(marker=term,reference_mentions=outward(ref,term),variant_mentions=outward(curr,term),
                       historical_mentions=outward(historical,term))
    scored.append(row)


def ratio(rows, field):
    v = [r[field] for r in rows if field in r]
    return f"{sum(v)}/{len(v)}"


lines = ["# 最终采购决策中的岗位意见消融与条件变更", "",
         "本实验复用 CP07 的 8 个冻结决策窗口。承建商、供应商、设计方和监理方各占两个窗口。D3 为多岗位讨论，S4 为同角色多轮推敲。每个窗口的终稿独立生成，岗位发言沿用历史记录。", "",
         "离线重建的 56 条原始请求均与组员提交的哈希一致。正式运行采用 v2 协议，其中 24 条删除意见和 16 条调整顺序请求直接复用原设计，16 条条件变更请求额外同步更新主机状态和条件登记。另有 16 条保持原输入的同期对照，两组每个窗口各一条。72 条请求按固定种子打乱，最多并发 2，模型为 deepseek-flash，非思考模式，温度 0.2。", "",
         "## 主要结果", "",
         "意向变化按结构化 decision 字段比较。6 个窗口输出投标意向，2 个供应商窗口输出报价文件。同期原样组与历史原样输出比较，其他变体与同窗口同组织方式的同期原样组比较。登记正确要求所有已核实和未核实 ID 均与该变体的预期集合一致。", "",
         "| 干预 | 有效 JSON / 计划 | 投标意向改变 / 可比意向 | 条件集合完全正确 / 有效输出 |",
         "|---|---:|---:|---:|"]
for title,prefix in [("D3 原样重跑","identity_D3"),("S4 原样重跑","identity_S4"),("D3 删除一条意见","dropout"),("D3 调换顺序","order_perm"),("D3 核实一个条件","bitflip_gate_D3"),("S4 核实一个条件","bitflip_gate_S4")]:
    group=[r for r in scored if r["kind"].startswith(prefix)]
    lines.append(f"| {title} | {ratio(group,'valid_json')} | {ratio(group,'change_intent')} | {ratio(group,'ids_correct')} |")
drop = [r for r in scored if "reference_mentions" in r]
lost = [r for r in drop if r["reference_mentions"] and not r["variant_mentions"]]
retained = [r for r in drop if r["reference_mentions"] and r["variant_mentions"]]
appeared = [r for r in drop if not r["reference_mentions"] and r["variant_mentions"]]
lines.extend(["","## 岗位意见的文本变化","",
              f"在生成前为 24 条岗位意见各选了一个原文已有的词，核对对外理由、方案与假设等字段。可配对的 {len(drop)} 条中，原样回答提到该词的有 {len(lost)+len(retained)} 条。删除岗位发言后，其中 {len(lost)} 条不再出现该词，{len(retained)} 条仍保留。另有 {len(appeared)} 条在删减后才出现。词面变化可能源于改写或其他岗位意见重叠，无法凭此给文本的风险质量打分。",""])
for r in lost:
    lines.append(f"- {r['job']} 的同期原样回答出现“{r['marker']}”，删减后的对外字段未再出现该词。")
shared = [r for r in drop if r["reference_mentions"]]
lines.extend(["", f"用同样词项和同一分母对照，以上同期原样回答出现该词的 {len(shared)} 个窗口与词项组合中，历史原样回答有 {sum(not r['historical_mentions'] for r in shared)} 个未出现。每窗口三个词共用一份原样输出。"])
lines.extend(["","## 条件变更及报价","",
             "8 个窗口中，有 4 个核实了唯一有效的提交前置条件，2 个窗口仍保留另一项前置条件，另有 2 个供应商窗口更新的是普通待核实条件。结构化 ID 正确表示模型在输出中准确更新了状态。投标意向与正式提交分属不同业务动作。","",
             "| 供应商窗口 | 组别 | 历史报价（MOP） | 同期原样报价（MOP） | 条件变更报价（MOP） |",
             "|---|---|---:|---:|---:|"])
for r in scored:
    if not r["kind"].startswith("identity") or r.get("reference_quotation") is None:
        continue
    flip=records.get(r["window"]+"__bitflip_gate_"+r["arm"],{})
    lines.append(f"| {r['window']} | {r['arm']} | {r['reference_quotation']:,} | {r.get('quotation')} | {flip.get('quotation','缺失')} |")
lines.extend(["", "| D3 供应商窗口 | 删意见后的报价范围（MOP） | 调顺序后的报价范围（MOP） |","|---|---:|---:|"])
for w in sorted({r["window"] for r in scored if r.get("quotation") is not None}):
    ranges = []
    for prefix in ("dropout","order_perm"):
        values=[r["quotation"] for r in scored if r["window"]==w and r["kind"].startswith(prefix)
                and isinstance(r.get("quotation"),(int,float))]
        ranges.append(f"{min(values):,} 至 {max(values):,}" if values else "缺失")
    lines.append(f"| {w} | {ranges[0]} | {ranges[1]} |")
lines.extend(["","这些数字是仿真草案的暂定报价。同一提示本身可能产生不同金额，金额差异只能描述本次重放。"])
example = "CP00-EXPAND-17-missing_core"
target = "condition_2dc6df77a06660ee2229"
if all(records.get(example+"__identity_"+a,{}).get("unresolved_condition_ids")==[target]
       and records.get(example+"__bitflip_gate_"+a,{}).get("verified_condition_ids")==[target]
       and records[example+"__identity_"+a].get("decision")==records[example+"__bitflip_gate_"+a].get("decision")=="bid"
       for a in ("D3","S4")):
    lines.extend(["", "在设计方窗口 CP00-EXPAND-17-missing_core，两组的原样回答均有投标意向，但仍将指定岗位档期列为未核实。主机在受控情景中核实该条件后，两组都保留投标意向，把该条件转入已核实清单，并在理由中说明它已解除提交阻碍。这个窗口可用于区分投标意向和提交条件的变化。"])
opening,closing = (Decimal(read(root/f)["CNY"]) for f in ("opening.json","closing.json"))
assert usage["prompt_tokens"]==usage["prompt_cache_hit_tokens"]+usage["prompt_cache_miss_tokens"]
metered = (Decimal("0.02")*usage["prompt_cache_hit_tokens"] + usage["prompt_cache_miss_tokens"] + 4*usage["completion_tokens"]) / 1000000
lines.extend(["","## 用量与边界","",
              f"共有 {len(list((root/'jobs').glob('*/attempt.json')))} 次发起记录、{len(list((root/'jobs').glob('*/response.json')))} 份供应商回执和 {len(records)} 份可解析的 JSON 对象。回执合计输入 {usage['prompt_tokens']:,} token、输出 {usage['completion_tokens']:,} token。运行前后账户余额分别为 ¥{opening} 与 ¥{closing}，查询差额 ¥{opening-closing}。","",
              f"本批在北京时间晚间执行。按 DeepSeek Flash 空闲时段价格及回执中的输入缓存命中、未命中和输出 token 估算，调用金额约 ¥{metered:.2f}。账户差额为两个时间点的读数，可能受扣费入账时间影响。[官方计价](https://api-docs.deepseek.com/zh-cn/quick_start/pricing/)","",
              "样本单位为 8 个窗口。同一窗口内不同变体共享材料及基线，且每种变体只生成一次。范围限于最终决策对输入的响应。十二例微观评分和本实验使用不同样本与指标，分别报告。","",
              "逐请求结果见 [metrics.json](metrics.json)。归档中的 plan.json 包含请求哈希与预期条件，jobs 目录保留输入、原始回执和 16 份历史基线，topic_markers.json 保存运行前固定的词。"])
(root/"REPORT.md").write_text("\n".join(lines)+"\n",encoding="utf8")
(root/"metrics.json").write_text(json.dumps(dict(usage=usage,account_change_cny=str(opening-closing),metered_estimate_cny=str(metered),rows=scored),ensure_ascii=False,indent=2),encoding="utf8")
