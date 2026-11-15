# 业务结果评价规范v2

本目录是[研究实验方案v2](../../2026-11-12_Capstone研究实验方案_v2_业务结果导向.md)的测量补充，未修改已冻结的CP运行准备包，也不是运行授权。

已准备4个维度、14项具体测量，以及新增24项目的48个情景卡：252项业务因素、192首轮对应1008个事项评分槽位；另有12个旧组织过程块、144个原生主体槽位、36个D3／S4配对槽位和72链项目后果槽位。

所有内容评分和未来业务结果均为空。项目名、角色、原条件、已给档案及原生初态预算属于输入，可预先填入；没有填入模型决定、授标、实际模拟成本或来源事件。

| 文件 | 用途 |
|---|---|
| [metrics.json](metrics.json) | 每项指标的定义、公式、单位、分母、数据来源、主次定位和解释范围 |
| [task_cards.json](task_cards.json) | 每题可接受行动、职责、已给/未知资料、未决条件、事项及充分处理判据 |
| [rubric.json](rubric.json) | 适当性、事项覆盖、可行性和权衡评分；条件性方案可以得到高分 |
| [response_ratings_template.json](response_ratings_template.json) | 全192首轮的事项与行为评分空表；D3/D4细评分范围按原CP02固定96份选择 |
| [discussion_template.json](discussion_template.json) | 固定12过程块的事项、输入依据、最终回应与质量差；旧材料新增评分属探索性 |
| [organization_task_cards.json](organization_task_cards.json) | 旧12任务各5项、共60项判据；按原资格／伙伴／成本／人员／核查状态窗口评分，不追溯套新任务字段 |
| [native_decision_template.json](native_decision_template.json) | 原生行动、策略、报价及独立声明成本，不从opaque ID差异推断策略差异 |
| [native_D3_S4_pairs.json](native_D3_S4_pairs.json) | 同项目、重复块、主体的36主配对，未填写结果 |
| [project_outcomes_template.json](project_outcomes_template.json) | 初始预算及未来授标、合同、成本、进度、里程碑槽位 |
| [feedback_design.json](feedback_design.json) | 应变与两个应不变控制层；未来窗口需在重放前固定输入规则参照 |
| [evaluation_addendum.json](evaluation_addendum.json) | 父协议哈希、研究优先级修订、旧目标保留与新指标使用边界 |
| [preparation_summary.json](preparation_summary.json) | 数量及零调用准备状态，实际评分数0 |
| [manifest.json](manifest.json) | 文件、构建脚本与父输入哈希；防止看过新结果后无记录地改变判据 |

复现命令（仅生成同内容的评价定义和空模板，无模型／宏观执行）：

```powershell
.\.venv-integration\Scripts\python.exe -X utf8 scripts/prepare_capstone_business_metrics_20261112.py
```

生成器只读取已固定输入与样本映射，网络及付费客户端构造被封锁。它检查48情景的角色分布、252事项、1008评分槽位、36主体对、原文件读取前后哈希及空值；输出内容不同则停止，不覆盖已有评价文件。无法判断记不可判断，事项分母0记N/A，不能用程序accepted或一次重复高分自动回填。

作者辅助AI评阅和数值／正式事件复算分别报告。组织质量不由模型“协调效率”替代；模拟成本受合同价计算影响，不单独推断施工生产率。详细失败、重试和接口记录仍在执行包中，正文不以这些指标为重点。
