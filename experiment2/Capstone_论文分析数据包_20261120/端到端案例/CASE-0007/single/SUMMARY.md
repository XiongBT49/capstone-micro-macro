# 端到端运行摘要：single

项目 CASE-0007 澳氹第四条跨海大桥起止点周边路网建造工程 - 北安区连接线；模型 `deepseek-flash`；状态 **completed**（项目已关闭），共 42 个宏观时间步。

模型调用 9 次，输入 57,366 tokens，输出 7,785 tokens。

## 各采购包

| 包 | 类型 | 预算 | 轮次 | 投标/放弃 | 递交投标 | 中标人 | 合同价 | 合同价/预算 | 签约修订稿 | 结果 |
|---|---|---|---|---|---|---|---|---|---|---|
| design | design | 4,500,000 | 1 | 2/0 | 2 | COMP-0286 招商局重庆交通科研设计院有限公司 | 4,450,000 | 98.9% | 1 | committed |
| cost | cost_consulting | 2,250,000 | 1 | 2/0 | 2 | COMP-0185 中建三局第二建设工程有限责任公司 | 2,000,000 | 88.9% | 1 | committed |
| construction-1 | construction | 82,875,000 | 1 | 3/0 | 3 | COMP-0153 中交第一航务工程局有限公司 | 82,875,000 | 100.0% | 1 | committed |
| supply-1 | supply | 23,205,000 | 1 | 2/0 | 2 | COMP-0154 中交第二公路工程局有限公司 | 23,205,000 | 100.0% | 1 | committed |
| construction-2 | construction | 44,625,000 | 1 | 1/2 | 1 | COMP-0153 中交第一航务工程局有限公司 | 44,585,000 | 99.9% | 1 | committed |
| supply-2 | supply | 12,495,000 | 1 | 2/0 | 2 | COMP-0154 中交第二公路工程局有限公司 | 11,720,000 | 93.8% | 1 | committed |

## 宏观结果（GBA 规则引擎）

- 项目阶段：closed；进度 100%；延误 7 天。
- 业主直接签约合同价合计 133,910,000（材料包已含在施工包内，不重复计入）；情景总预算 150,000,000；宏观登记的施工合同额 127,460,000。
- 宏观记录的实际成本 170,039,704，为总预算的 113.4%。
- 选定单位：设计 COMP-0286，造价 COMP-0185，施工 COMP-0153，供应 COMP-0154。

| 指标 | 数值 |
|---|---|
| project_completion_rate | 1.0 |
| average_delay_days | 7.0 |
| average_cost_overrun | 0.2698 |
| average_quality_score | 0.7814 |
| approval_pass_rate | 1.0 |
| tender_failure_rate | 0.0 |
| construction_failure_rate | 0.0 |
| claim_frequency | 0.0 |
| variation_frequency | 0.0 |
| inspection_failure_rate | 1.0 |
| project_failure_risk_average | 0.1917 |
| performance.planned_progress | 0.9167 |
| performance.actual_progress | 1.0 |
| performance.progress_deviation | 0.0833 |
| performance.design_quality | 0.8648 |
| performance.material_quality | 0.8 |
| performance.construction_quality | 0.7257 |
| performance.overall_quality | 0.7814 |
| performance.defect_rate | 0.2186 |
| performance.detected_defect_rate | 0.1093 |
| performance.planned_cost | 140700000.0 |
| performance.actual_cost | 170039703.7693 |
| performance.cost_overrun_ratio | 0.2698 |
| performance.planned_duration | 24 |
| performance.elapsed_time | 22 |
| performance.delay_days | 7 |
| performance.safety_risk | 0.285 |
| performance.compliance_risk | 0.1752 |
| performance.inspection_pass_probability | 0.6792 |
| performance.coordination_efficiency | 0.7 |
| performance.information_quality | 0.7989 |
| performance.decision_delay_risk | 0.0 |
| performance.material_availability | 1.0 |
| performance.supply_delay_risk | 0.07 |
| performance.variation_risk | 0.1955 |
| performance.claim_risk | 0.2866 |
| performance.dispute_risk | 0.2784 |
| performance.project_failure_risk | 0.1917 |

宏观事件共 188 条：

| 事件类型 | 次数 |
|---|---|
| construction_progress_updated | 44 |
| project_state_updated | 41 |
| payment_requested | 36 |
| inspection_passed | 14 |
| stage_transition | 10 |
| agent_engaged | 9 |
| payment_delayed | 9 |
| agent_released | 7 |
| package_contract_committed | 6 |
| regulatory_review_decision | 2 |
| inspection_failed | 2 |
| approval_approved | 1 |
| agent_standby | 1 |
| mobilization_completed | 1 |
| completion_inspection_started | 1 |
| project_completed | 1 |
| final_account_dispute_session_started | 1 |
| final_account_review_started | 1 |
| final_account_settled | 1 |
