# 端到端运行摘要：multi

项目 CASE-0003 九澳水库扩容建造工程；模型 `deepseek-flash`；状态 **completed**（项目已关闭），共 42 个宏观时间步。

模型调用 1078 次，输入 9,110,452 tokens，输出 677,617 tokens。

## 各采购包

| 包 | 类型 | 预算 | 轮次 | 投标/放弃 | 递交投标 | 中标人 | 合同价 | 合同价/预算 | 签约修订稿 | 结果 |
|---|---|---|---|---|---|---|---|---|---|---|
| design | design | 4,500,000 | 1 | 1/1 | 1 | COMP-0169 中国建筑第五工程局有限公司 | 4,500,000 | 100.0% | 3 | committed |
| cost | cost_consulting | 2,250,000 | 1 | 2/0 | 2 | COMP-0208 中铁武汉大桥工程咨询监理有限公司 | 2,052,000 | 91.2% | 2 | committed |
| construction-1 | construction | 63,750,000 | 1 | 3/0 | 3 | COMP-0025 得宝国际有限公司 | 60,710,000 | 95.2% | 2 | committed |
| supply-1 | supply | 17,850,000 | 1 | 2/0 | 2 | COMP-0191 中建八局第二建设有限公司 | 17,850,000 | 100.0% | 2 | committed |
| construction-2 | construction | 38,250,000 | 1 | 3/0 | 3 | COMP-0153 中交第一航务工程局有限公司 | 36,290,000 | 94.9% | 3 | committed |
| supply-2 | supply | 10,710,000 | 1 | 2/0 | 2 | COMP-0191 中建八局第二建设有限公司 | 10,455,000 | 97.6% | 3 | committed |
| construction-3 | construction | 25,500,000 | 1 | 2/1 | 2 | COMP-0493 得宝建筑集团有限公司 | 24,250,000 | 95.1% | 3 | committed |
| supply-3 | supply | 7,140,000 | 1 | 2/0 | 2 | COMP-0191 中建八局第二建设有限公司 | 6,540,000 | 91.6% | 3 | committed |

## 宏观结果（GBA 规则引擎）

- 项目阶段：closed；进度 100%；延误 20 天。
- 业主直接签约合同价合计 127,802,000（材料包已含在施工包内，不重复计入）；情景总预算 150,000,000；宏观登记的施工合同额 121,250,000。
- 宏观记录的实际成本 163,720,814，为总预算的 109.1%。
- 选定单位：设计 COMP-0169，造价 COMP-0208，施工 COMP-0025，供应 COMP-0191。

| 指标 | 数值 |
|---|---|
| project_completion_rate | 1.0 |
| average_delay_days | 20.0 |
| average_cost_overrun | 0.2811 |
| average_quality_score | 0.7816 |
| approval_pass_rate | 1.0 |
| tender_failure_rate | 0.0 |
| construction_failure_rate | 0.0 |
| claim_frequency | 0.0 |
| variation_frequency | 0.0 |
| inspection_failure_rate | 1.0 |
| project_failure_risk_average | 0.2039 |
| performance.planned_progress | 0.9167 |
| performance.actual_progress | 1.0 |
| performance.progress_deviation | 0.0833 |
| performance.design_quality | 0.8648 |
| performance.material_quality | 0.8 |
| performance.construction_quality | 0.7262 |
| performance.overall_quality | 0.7816 |
| performance.defect_rate | 0.2184 |
| performance.detected_defect_rate | 0.1092 |
| performance.planned_cost | 140700000.0 |
| performance.actual_cost | 163720813.6897 |
| performance.cost_overrun_ratio | 0.2811 |
| performance.planned_duration | 24 |
| performance.elapsed_time | 22 |
| performance.delay_days | 20 |
| performance.safety_risk | 0.285 |
| performance.compliance_risk | 0.1752 |
| performance.inspection_pass_probability | 0.6792 |
| performance.coordination_efficiency | 0.7 |
| performance.information_quality | 0.7989 |
| performance.decision_delay_risk | 0.0 |
| performance.material_availability | 0.955 |
| performance.supply_delay_risk | 0.11 |
| performance.variation_risk | 0.1957 |
| performance.claim_risk | 0.3065 |
| performance.dispute_risk | 0.2883 |
| performance.project_failure_risk | 0.2039 |

宏观事件共 249 条：

| 事件类型 | 次数 |
|---|---|
| construction_progress_updated | 66 |
| payment_requested | 54 |
| project_state_updated | 41 |
| inspection_passed | 21 |
| payment_delayed | 13 |
| agent_engaged | 11 |
| stage_transition | 10 |
| agent_released | 9 |
| package_contract_committed | 8 |
| inspection_failed | 3 |
| supply_delay | 3 |
| regulatory_review_decision | 2 |
| approval_approved | 1 |
| agent_standby | 1 |
| mobilization_completed | 1 |
| completion_inspection_started | 1 |
| project_completed | 1 |
| final_account_dispute_session_started | 1 |
| final_account_review_started | 1 |
| final_account_settled | 1 |
