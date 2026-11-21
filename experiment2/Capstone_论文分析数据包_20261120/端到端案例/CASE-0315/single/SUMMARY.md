# 端到端运行摘要：single

项目 CASE-0315 香港葛量洪医院；模型 `deepseek-flash`；状态 **business_stopped**（项目因业务决定或宏观条件停止），共 4 个宏观时间步。

模型调用 59 次，输入 276,743 tokens，输出 41,604 tokens。

## 各采购包

| 包 | 类型 | 预算 | 轮次 | 投标/放弃 | 递交投标 | 中标人 | 合同价 | 合同价/预算 | 签约修订稿 | 结果 |
|---|---|---|---|---|---|---|---|---|---|---|
| design | design | 4,500,000 | 3 | 0/2 | 0 | —  | — | — | 0 | no_contract |
| cost | cost_consulting | 2,250,000 | 1 | 2/0 | 2 | COMP-0169 中国建筑第五工程局有限公司 | 2,200,000 | 97.8% | 1 | committed |
| CASE-0315/construction-1 | construction | 82,500,000 | 0 | | | | | | | 未开始 |
| CASE-0315/supply-1 | supply | 23,100,000 | 0 | | | | | | | 未开始 |
| CASE-0315/construction-2 | construction | 45,000,000 | 0 | | | | | | | 未开始 |
| CASE-0315/supply-2 | supply | 12,600,000 | 0 | | | | | | | 未开始 |

## 宏观结果（GBA 规则引擎）

- 项目阶段：suspended；进度 0%；延误 21 天。
- 业主直接签约合同价合计 2,200,000（材料包已含在施工包内，不重复计入）；情景总预算 150,000,000；宏观登记的施工合同额 尚未登记。
- 宏观记录的实际成本 2,200,000，为总预算的 1.5%。
- 选定单位：设计 None，造价 COMP-0169，施工 None，供应 。

| 指标 | 数值 |
|---|---|
| project_completion_rate | 0.0 |
| average_delay_days | 21.0 |
| average_cost_overrun | 0.0 |
| average_quality_score | 1.0 |
| approval_pass_rate | 0.0 |
| tender_failure_rate | 0.0 |
| construction_failure_rate | 0.0 |
| claim_frequency | 0.0 |
| variation_frequency | 0.0 |
| inspection_failure_rate | 0.0 |
| project_failure_risk_average | 0.0096 |
| performance.planned_progress | 0.0 |
| performance.actual_progress | 0.0 |
| performance.progress_deviation | 0.0 |
| performance.design_quality | 0.0 |
| performance.material_quality | 1.0 |
| performance.construction_quality | 1.0 |
| performance.overall_quality | 1.0 |
| performance.defect_rate | 0.0 |
| performance.detected_defect_rate | 0.0 |
| performance.planned_cost | 0.0 |
| performance.actual_cost | 2200000.0 |
| performance.cost_overrun_ratio | 0.0 |
| performance.planned_duration | 24 |
| performance.elapsed_time | 0 |
| performance.delay_days | 21 |
| performance.safety_risk | 0.0 |
| performance.compliance_risk | 0.0 |
| performance.inspection_pass_probability | 1.0 |
| performance.coordination_efficiency | 1.0 |
| performance.information_quality | 1.0 |
| performance.decision_delay_risk | 0.0 |
| performance.material_availability | 1.0 |
| performance.supply_delay_risk | 0.0 |
| performance.variation_risk | 0.0 |
| performance.claim_risk | 0.0 |
| performance.dispute_risk | 0.0 |
| performance.project_failure_risk | 0.0096 |

宏观事件共 8 条：

| 事件类型 | 次数 |
|---|---|
| project_state_updated | 3 |
| procurement_round_rejected | 3 |
| agent_engaged | 1 |
| package_contract_committed | 1 |
