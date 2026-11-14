# 安装与运行

使用Python 3.12，在仓库根目录执行：

```powershell
uv sync --locked
uv run pytest tests
uv run python capstone.py results
```

公开测试限定为纯方法、组织授权和领域契约三个测试文件，使用合成输入，不调用模型或宏观数据库。原完整工作区的512项核验覆盖更多本地资源依赖测试，不能等同于公开克隆的测试范围。

## 完整本地工作区

完整工作区可执行 `capstone.py doctor`、`data`、`micro-demo` 和 `macro-demo`。运行资源包括：授权宏观包及数据库 `vendor/gba/`、契约规范 `zwtnew/`、完整 `config/`、原始 `data/`，以及当前运行代码明确读取的本地冻结基线。它们未随公开仓库发布。

已有 `D:/hkura/codedemo_v2/new_sum` 中的资源继续保留；在其他机器上使用前，应通过项目授权渠道取得资源，放到对应目录，再运行 `doctor`。不要为绕过缺失检查伪造数据或替换冻结事实。

宏观默认示例保留48步输入，通过原生检查点在第1步停止；`capstone.py macro-demo --full` 运行48步，耗时明显更长。宏观示例在 `runs/` 中复制独立可写数据库，约额外占2GB；示例禁止外网，允许Windows事件循环需要的本机连接。

真实模型凭据只放本地 `.env`，参考 `.env.example`。已有实验的停止状态保留，公开上传不恢复任何模型任务。
