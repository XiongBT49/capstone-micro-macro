# 精选六例全生命周期对照

每例使用相同的初始输入、模型 deepseek-flash、full 配置、随机种子 42 和完整业主拆包。每组运行一次。费用统计仅含本批新增调用；之前中断尝试的调用另存于原目录。CASE-0206 和 CASE-0315 的两组均使用新版输入前缀布局。

| 案例 | 单 agent 状态 | 多 agent 状态 | 签约包数 单 / 多 | 成本变化（多减单，同项目币种） | 延误天数 单 / 多 |
|---|---|---|---|---:|---|
| CASE-0003 | completed | completed | 6 / 8 | -4,228,227 MOP | 7 / 20 |
| CASE-0005 | completed | completed | 6 / 6 | +3,563,960 MOP | 7 / 7 |
| CASE-0014 | completed | completed | 6 / 6 | +10,078,144 MOP | 7 / 7 |
| CASE-0049 | completed | completed | 6 / 6 | -136,319 CNY | 7 / 7 |
| CASE-0206 | completed | completed | 6 / 6 | -6,693,609 MOP | 7 / 7 |
| CASE-0315 | business_stopped | business_stopped | 1 / 1 | 无两组结算值 | 21 / 21 |

[逐组指标及来源](paired_results.csv) · [与历史企业的逐条对照](groundtruth.csv)

completed 表示项目关闭并完成结算；business_stopped 表示由业务决策触发停工。停工时的账面成本只反映已执行阶段，不能用于比较完工总成本。

## 调用与复用

CASE-0014 和 CASE-0049 复用两组既有结果。CASE-0003 和 CASE-0005 复用单 agent，补跑此前中断的多 agent。CASE-0206 和 CASE-0315 各新增两组。
六个新增组记录到 3,105 次有 token 回执的 DeepSeek 调用，按缓存命中、未命中和输出 token 分项估算合计 ¥46.28。此金额仅涵盖本批新增调用。

## 历史签约企业对照

按案例、企业及原始角色逐条核对历史记录。可比样本取两组均结算、同角色且历史企业在候选池中的记录。

| 组别 | 可比历史记录 | 实际签约命中 |
|---|---:|---:|
| single | 0 | 0 |
| multi | 0 | 0 |

这里的命中表示历史企业在相同角色下实际签约。另一个微观实验的 Top-3 指标衡量从 24 家候选中选出的前三名是否包含历史企业，两项结果需分别报告。
