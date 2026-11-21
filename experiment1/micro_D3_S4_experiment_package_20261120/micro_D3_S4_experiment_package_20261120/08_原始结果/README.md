# 结果副本说明

本目录保留原目录名称，内容现为删减版。部分说明、协议及汇总已按当前展示范围编辑，因此不能将本目录整体称为逐字节原始归档。完整原始结果保存在资料包之外。

自动质量评分、置信区间、缺失和失败、过程记录、匿名材料、Token费用继续保留；没有因删减而重新评分或调用模型。

来源表同时记录原文件哈希和当前副本哈希，copy_status区分原样副本与编辑节选。

|文件|内容|
|---|---|
|[ablation_quality_summary.json](ablation_quality_summary.json)|60条G3/D3严格消融。|
|[acceptance.json](acceptance.json)|全量4690次调用、926终稿、986评分的工程验收和预算。|
|[analysis_source_provenance.json](analysis_source_provenance.json)|主审计及secondary不同执行版源码的哈希与追加断言记录。|
|[data_optimization_summary.json](data_optimization_summary.json)|事实无损整理审计：5196候选槽位、来源ID、已知/未知，事实修改及新增均0。|
|[failure_analysis.md](failure_analysis.md)|上一轮可读失效诊断与历史排序锚定解释。|
|[human_blind_packets.json](human_blind_packets.json)|供将来人工评分的匿名材料，目前尚未进行专家评分。|
|[human_fixed_rubric.json](human_fixed_rubric.json)|人工复核使用的相同五维评分锚点。|
|[human_private_mapping.json](human_private_mapping.json)|匿名材料映射，仅供研究管理。|
|[human_score_sheet.csv](human_score_sheet.csv)|尚未填写的人工评分表。|
|[human_scoring_guide.md](human_scoring_guide.md)|真实人工复核的操作说明。|
|[independent_ablation_summary.json](independent_ablation_summary.json)|独立重算的G3/D3消融统计。|
|[independent_audit.json](independent_audit.json)|全部4690 HTTP、输入、账本、回退、原归档和主统计独立审计。|
|[independent_failure_diagnostics.json](independent_failure_diagnostics.json)|独立计算的早期无效、终稿修复、错误类型和Top1变更。|
|[independent_intermediate_summary.json](independent_intermediate_summary.json)|独立步骤统计，只累计valid步骤的有效依据/引用等贡献。|
|[independent_quality_summary.json](independent_quality_summary.json)|独立重算的S4/D3严格均分、分组置信区间和缺失。|
|[independent_review.md](independent_review.md)|上一轮独立复核的可读结论与解释边界。|
|[intermediate_metrics.csv](intermediate_metrics.csv)|3704步过程数量表。|
|[intermediate_metrics.json](intermediate_metrics.json)|3704步（含G3）完整请求、原输出、解析与状态。|
|[interpretation.md](interpretation.md)|上一轮可读总体解读；本包03进一步整理表格与研究口径。|
|[interpretation_metrics.json](interpretation_metrics.json)|保留的质量、消融与过程汇总。|
|[judge_length_sensitivity_secondary.json](judge_length_sensitivity_secondary.json)|原理由长度敏感性及原评分凭证。|
|[migration.json](migration.json)|40→60预算续跑迁移、旧3590调用复用和未付费失败保留。|
|[migration_independent_audit.json](migration_independent_audit.json)|迁移后SQL、原始凭证、费用一次计入的独立核对。|
|[protocol.json](protocol.json)|实验协议的当前展示节选，非完整原始协议。|
|[quality_summary.json](quality_summary.json)|S4/D3严格质量评分、配对、维度、缺失及区间。|
|[report.md](report.md)|原程序输出报告，保留完整JSON统计，不是新生成的逐条解释。|
|[secondary_independent_audit.json](secondary_independent_audit.json)|986顺序的辅助长度恢复、原分数/引用不变及主结果未改的独立核验。|
|[split_manifest.json](split_manifest.json)|433条记录的新开发/验证/测试分组及G3入选标记。|
|[status.json](status.json)|原运行最终状态快照，已完成；不构成重新调用授权。|
|[status.md](status.md)|原运行最终状态的可读版本。|
|[summary.json](summary.json)|原自动导出的质量、消融、工程与费用综合JSON。|
|[token_cost_per_call.csv](token_cost_per_call.csv)|4690次实际调用的Token与费用。|
|[token_cost_summary.json](token_cost_summary.json)|实际调用及分组费用。|
