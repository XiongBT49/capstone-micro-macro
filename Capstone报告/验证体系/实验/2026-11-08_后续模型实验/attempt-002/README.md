# 冻结配置与运行入口

状态：**两批真实调用及120份首轮内容评阅均已完成，共194/240次请求**。账本、冻结文件、引文与源哈希核对通过，两份重试单列。修复确认的改善对报价依据解释口径敏感；组织对照核心性质持平，D3约4.11倍tokens。见[运行完成记录](运行完成记录.md)及[内容核对JSON](content_review_summary.json)。论文和最终图表暂缓，下方真实启动命令仅保留为历史记录，不可重复执行。

后续版本说明：源码已在独立的[V2.2修复批次](../../2026-11-08_V2_2_最小修复与稳健性/README.md)前进；本目录仍是V2.1时期的原始调用与评分。冻结源码核对须使用该批保存的V2.1快照，不能用当前V2.2源码直接比较旧冻结哈希。原194次请求和旧分数未覆盖。

- [样本清单](sample_manifest.json)：12个项目组、8个历史输入＋4个合成控制任务，企业重叠如实记录。
- [冻结输入](windows.json)、[内容评价目标](measurement_targets.json)、[执行协议](protocol.json)、[选择记录](selection_record.json)。原样本、旧输出和失败未修改。
- [离线预检](preflight.json)：两版事实／条件相同、岗位真实且属于自身企业、两种组织模式共享初始资料、48个合成接口探针通过、预算预留／释放检查、语法检查及零网络请求。
- [入口测试](preflight_tests.xml)：6项通过；覆盖无预算不构建客户端、公共算术与不同输出契约、有效核查／其他未决条件、评论失败不冒称完整组织、保留首轮及有界重试、provider失败计费与脱敏。
- `review_packets/`保存全部120个首轮评阅包；其中模板仍为未评分占位，不覆盖实际的[AI辅助评阅](ai_review_annotations.json)。实际评分均有引文与理由，评价者非盲评、非独立专家。

预检阶段、任何模型请求之前，仅补记运行入口直接导入的准备模块哈希；修改前协议保存在 `revisions/`。输入、内容目标、任务清单及预算均未变化。

每个阶段的 `accepted` 仅表示相应契约校验通过；不是公共内容评分或历史企业命中率。组织评论失败时，保留技术失败槽位，最终判断可使用其余意见，但整条组织试验标记为不完整，不充作三条有效评论的完成结果。

以下命令已按用户240次新授权执行，现仅为历史记录，勿重新运行：

```powershell
# 两批合计最多240次：确认96、组织144，各自包含最多24次最终回答重试。
.\.venv-integration\Scripts\python.exe -X utf8 scripts/run_capstone_followup_20261108.py run --batch all --authorize-max-calls 240

# 若仅授权先跑修复确认，使用这一条；不能同时运行上面的命令。
.\.venv-integration\Scripts\python.exe -X utf8 scripts/run_capstone_followup_20261108.py run --batch confirmation --authorize-max-calls 96
```

运行后输出到本目录 `confirmation/`、`organization/`，分别有预算SQLite、逐请求审计、首轮／重试响应和逐任务状态。执行入口拒绝自动重启已有或状态未知的模型请求。组织评论不重试；完成所有首轮最终回答后，只对最终JSON／契约失败进行一次有界重试。提供方失败不重试。

准备命令已经执行；冻结后不重新筛选：

```powershell
.\.venv-integration\Scripts\python.exe -X utf8 scripts/preflight_capstone_followup_20261108.py
.\.venv-integration\Scripts\python.exe -X utf8 -m pytest tests/test_capstone_followup.py -q
```

已知首轮提示字符数约为确认139万、组织235万（尚不含生成评论及重试输入），不是token计费数量或金额。每请求输出上限4096；240次的理论输出上限983,040 tokens，不含输入tokens。所有实际输入／输出tokens、缓存和耗时以provider元数据保存；无账单不编造货币费用。
