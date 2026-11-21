# 端到端运行摘要：multi

项目 CASE-0019 新城填海区A区至澳门半岛之间的连接通道-改善工程 (行人隧道)；模型 `deepseek-flash`；状态 **completed**（项目已关闭），共 42 个宏观时间步。

模型调用 663 次，输入 5,636,851 tokens，输出 387,085 tokens。

## 各采购包

| 包 | 类型 | 预算 | 轮次 | 投标/放弃 | 递交投标 | 中标人 | 合同价 | 合同价/预算 | 签约修订稿 | 结果 |
|---|---|---|---|---|---|---|---|---|---|---|
| design | design | 4,500,000 | 1 | 2/0 | 2 | COMP-0286 招商局重庆交通科研设计院有限公司 | 3,536,000 | 78.6% | 2 | committed |
| cost | cost_consulting | 2,250,000 | 1 | 2/0 | 2 | COMP-0208 中铁武汉大桥工程咨询监理有限公司 | 2,150,000 | 95.6% | 2 | committed |
| construction-1 | construction | 70,125,000 | 1 | 3/0 | 3 | COMP-0191 中建八局第二建设有限公司 | 70,125,000 | 100.0% | 3 | committed |
| supply-1 | supply | 19,635,000 | 1 | 2/0 | 2 | COMP-0167 中国建筑第三工程局有限公司 | 15,325,000 | 78.0% | 2 | committed |
| construction-2 | construction | 38,250,000 | 1 | 3/0 | 3 | COMP-0153 中交第一航务工程局有限公司 | 36,730,000 | 96.0% | 3 | committed |
| supply-2 | supply | 10,710,000 | 1 | 2/0 | 2 | COMP-0154 中交第二公路工程局有限公司 | 10,358,000 | 96.7% | 2 | committed |
| construction-3 | construction | 19,125,000 | 1 | 3/0 | 3 | COMP-0494 得寶國際-得寶建築合作經營 | 18,720,000 | 97.9% | 2 | committed |
| supply-3 | supply | 5,355,000 | 1 | 2/0 | 2 | COMP-0154 中交第二公路工程局有限公司 | 4,769,000 | 89.1% | 2 | committed |

## 宏观结果（GBA 规则引擎）

- 项目阶段：closed；进度 100%；延误 20 天。
- 业主直接签约合同价合计 131,261,000（材料包已含在施工包内，不重复计入）；情景总预算 150,000,000；宏观登记的施工合同额 125,575,000。
- 宏观记录的实际成本 168,434,149，为总预算的 112.3%。
- 选定单位：设计 COMP-0286，造价 COMP-0208，施工 COMP-0191，供应 COMP-0154, COMP-0167。

| 指标 | 数值 |
|---|---|
| project_completion_rate | 1.0 |
| average_delay_days | 20.0 |
| average_cost_overrun | 0.2832 |
| average_quality_score | 0.7832 |
| approval_pass_rate | 1.0 |
| tender_failure_rate | 0.0 |
| construction_failure_rate | 0.0 |
| claim_frequency | 0.0 |
| variation_frequency | 0.0 |
| inspection_failure_rate | 1.0 |
| project_failure_risk_average | 0.2041 |
| performance.planned_progress | 0.9167 |
| performance.actual_progress | 1.0 |
| performance.progress_deviation | 0.0833 |
| performance.design_quality | 0.8678 |
| performance.material_quality | 0.8 |
| performance.construction_quality | 0.7269 |
| performance.overall_quality | 0.7832 |
| performance.defect_rate | 0.2168 |
| performance.detected_defect_rate | 0.1084 |
| performance.planned_cost | 140700000.0 |
| performance.actual_cost | 168434148.8485 |
| performance.cost_overrun_ratio | 0.2832 |
| performance.planned_duration | 24 |
| performance.elapsed_time | 22 |
| performance.delay_days | 20 |
| performance.safety_risk | 0.285 |
| performance.compliance_risk | 0.1749 |
| performance.inspection_pass_probability | 0.6805 |
| performance.coordination_efficiency | 0.7 |
| performance.information_quality | 0.8007 |
| performance.decision_delay_risk | 0.0 |
| performance.material_availability | 0.955 |
| performance.supply_delay_risk | 0.111 |
| performance.variation_risk | 0.1944 |
| performance.claim_risk | 0.3062 |
| performance.dispute_risk | 0.2881 |
| performance.project_failure_risk | 0.2041 |

宏观事件共 250 条：

| 事件类型 | 次数 |
|---|---|
| construction_progress_updated | 66 |
| payment_requested | 54 |
| project_state_updated | 41 |
| inspection_passed | 21 |
| payment_delayed | 13 |
| agent_engaged | 11 |
| stage_transition | 10 |
| agent_released | 10 |
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
