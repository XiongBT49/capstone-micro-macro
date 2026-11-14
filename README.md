# Capstone: Micro Decisions and Macro Validation

本仓库公开Capstone的微观业务代码、宏观衔接代码、研究设计和汇总结果。**第三方宏观引擎、原始企业/项目数据、原始模型回答、实验数据库及汇报模板未公开上传。** 完整本地工作区仍保留这些资源。

研究问题是：相同业务事实下，个体判断、同角色复核和多岗位审议如何影响决策质量，这些决定能否传导到模拟项目后果和后轮反馈。

## 阅读入口

| 内容 | 入口 |
|---|---|
| 研究目的、比较设计与指标 | [研究主线](research/PLAN.md) |
| 后续研究任务 | [后续计划](research/NEXT_STEPS.md) |
| 系统结构与实现边界 | [架构说明](docs/architecture.md) |
| 已有结果及完成度 | [结果汇总](results/README.md) |
| 数据边界 | [数据说明](data/README.md) |
| 安装与公开代码验证 | [运行指南](docs/quickstart.md) |
| 独立副本的实际检查范围 | [公开代码验证](docs/public_validation.md) |
| 公开范围与本地完整资源 | [发布说明](docs/repository.md) |

## 公开目录

```text
src/          微观动作、纯方法、组织机制、来源约束及模型客户端
integration/  宏观接口、业务宿主、场景构建和结果分析代码
config/roles/ 通用岗位配置
prompts/      业务提示模板
skills/       角色动作技能资源
scripts/      实验准备与分析工具源码
tests/        不依赖原始数据或宏观包的合成测试
research/     当前研究主线和后续计划
results/      汇总说明与本地证据路径索引
```

## 安装与验证

需要Python 3.12及uv：

```powershell
uv sync --locked
uv run pytest tests
uv run python capstone.py results
```

以上公开测试使用合成输入，不请求真实模型，不需要原始数据库。`capstone.py doctor` 可检查完整运行资源是否已在本地提供；公开克隆缺少这些资源时会报告缺失。

完整微观数据工作流和宏观连续链需要另行取得合法授权的本地资源。不能仅凭公开代码宣称完整端到端运行已复现。已有完整工作区可继续使用，公开排除没有删除其中的资料。

本仓库未为第三方宏观包授予或转授开源许可。公开代码也未在本次上传中新增许可证。
