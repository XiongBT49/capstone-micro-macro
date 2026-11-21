# 端到端运行摘要：multi

项目 CASE-0006 澳氹第四条跨海大桥起止点周边路网建造工程 - A区东轴线 - 第1期工程；模型 `deepseek-flash`；状态 **completed**（项目已关闭），共 42 个宏观时间步。

模型调用 436 次，输入 3,483,510 tokens，输出 246,622 tokens。

## 各采购包

| 包 | 类型 | 预算 | 轮次 | 投标/放弃 | 递交投标 | 中标人 | 合同价 | 合同价/预算 | 签约修订稿 | 结果 |
|---|---|---|---|---|---|---|---|---|---|---|
| design | design | 4,500,000 | 1 | 2/0 | 2 | COMP-0169 中国建筑第五工程局有限公司 | 4,150,000 | 92.2% | 3 | committed |
| cost | cost_consulting | 2,250,000 | 1 | 2/0 | 2 | COMP-0286 招商局重庆交通科研设计院有限公司 | 2,250,000 | 100.0% | 3 | committed |
| construction-1 | construction | 82,875,000 | 1 | 3/0 | 3 | COMP-0153 中交第一航务工程局有限公司 | 72,300,000 | 87.2% | 2 | committed |
| supply-1 | supply | 23,205,000 | 1 | 2/0 | 2 | COMP-0191 中建八局第二建设有限公司 | 19,715,000 | 85.0% | 2 | committed |
| construction-2 | construction | 44,625,000 | 1 | 3/0 | 3 | COMP-0494 得寶國際-得寶建築合作經營 | 40,250,000 | 90.2% | 2 | committed |
| supply-2 | supply | 12,495,000 | 1 | 2/0 | 2 | COMP-0154 中交第二公路工程局有限公司 | 12,350,000 | 98.8% | 2 | committed |

## 宏观结果（GBA 规则引擎）

- 项目阶段：closed；进度 100%；延误 7 天。
- 业主直接签约合同价合计 118,950,000（材料包已含在施工包内，不重复计入）；情景总预算 150,000,000；宏观登记的施工合同额 112,550,000。
- 宏观记录的实际成本 150,917,177，为总预算的 100.6%。
- 选定单位：设计 COMP-0169，造价 COMP-0286，施工 COMP-0153，供应 COMP-0154, COMP-0191。

| 指标 | 数值 |
|---|---|
| project_completion_rate | 1.0 |
| average_delay_days | 7.0 |
| average_cost_overrun | 0.2687 |
| average_quality_score | 0.7817 |
| approval_pass_rate | 1.0 |
| tender_failure_rate | 0.0 |
| construction_failure_rate | 0.0 |
| claim_frequency | 0.0 |
| variation_frequency | 0.0 |
| inspection_failure_rate | 1.0 |
| project_failure_risk_average | 0.1914 |
| performance.planned_progress | 0.9167 |
| performance.actual_progress | 1.0 |
| performance.progress_deviation | 0.0833 |
| performance.design_quality | 0.8684 |
| performance.material_quality | 0.8 |
| performance.construction_quality | 0.7239 |
| performance.overall_quality | 0.7817 |
| performance.defect_rate | 0.2183 |
| performance.detected_defect_rate | 0.1091 |
| performance.planned_cost | 140400000.0 |
| performance.actual_cost | 150917176.6702 |
| performance.cost_overrun_ratio | 0.2687 |
| performance.planned_duration | 24 |
| performance.elapsed_time | 22 |
| performance.delay_days | 7 |
| performance.safety_risk | 0.285 |
| performance.compliance_risk | 0.1748 |
| performance.inspection_pass_probability | 0.6807 |
| performance.coordination_efficiency | 0.7 |
| performance.information_quality | 0.8011 |
| performance.decision_delay_risk | 0.0 |
| performance.material_availability | 1.0 |
| performance.supply_delay_risk | 0.083 |
| performance.variation_risk | 0.1941 |
| performance.claim_risk | 0.2866 |
| performance.dispute_risk | 0.2783 |
| performance.project_failure_risk | 0.1914 |

宏观事件共 190 条：

| 事件类型 | 次数 |
|---|---|
| construction_progress_updated | 44 |
| project_state_updated | 41 |
| payment_requested | 36 |
| inspection_passed | 14 |
| stage_transition | 10 |
| agent_engaged | 9 |
| agent_released | 9 |
| payment_delayed | 9 |
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
