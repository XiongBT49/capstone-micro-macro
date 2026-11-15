# 组员接手与完整克隆检查

本仓库按完整项目交接整理。组员需要Git、Git LFS、Python 3.12及uv；无需原作者的虚拟环境或旧 `codedemo_v2` 目录。

```powershell
git lfs install
git -c core.longpaths=true clone https://github.com/XiongBT49/capstone-micro-macro.git
cd capstone-micro-macro
git lfs pull
uv sync --locked
uv run python capstone.py doctor
uv run python capstone.py data
uv run python capstone.py results
uv run pytest tests -q
uv run python capstone.py micro-demo
uv run python capstone.py macro-demo
```

`doctor` 应显示空的missing和asset_errors列表，以及 `independent_root: true`。数据应为352条项目记录、904条企业记录，另有两份499行的关系/匹配CSV。`results` 应能找到已索引的原始文件。

宏观数据库应是约2GB的真实SQLite文件，不能是百余字节的Git LFS指针文本。`macro-demo` 使用新的可写数据库副本并在第1步保存检查点；完整48步入口为 `macro-demo --full`，耗时更长。

两个demo均采用离线模式，不需要模型密钥，不能用作新的研究效果结果。真实模型实验需要组员自行配置本地 `.env`；密钥不会随仓库分发，暂停的旧实验不会自动恢复。

迁移时的原始完整工作区检查见[历史验收](verification.md)。本次远程克隆的实际验收记录将在检查完成后补充。
