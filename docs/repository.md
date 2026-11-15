# 完整协作仓库

用户要求组员能够接手完整项目，当前提交包含微观代码、第三方宏观运行包、规范资源、完整场景配置、原始项目/企业数据、选定实验输入与结果、评分和基线、研究附件及汇报材料。原始工作区不回写。

当前远程地址为 `https://github.com/XiongBT49/capstone-micro-macro`。仓库可见性由用户管理；上传未授予或转授第三方开源许可，`vendor/gba/NOTICE.md` 与原协作约定继续适用。

## 不提交的本地内容

凭据与 `.env`、虚拟环境、缓存、`runs/`、`.migration/`、课程个人行政资料 `research/admin/` 不提交。现有实验暂停状态不变，不能把旧GOAL或预算当作恢复运行指令。

## 大文件与克隆

宏观数据库及20MB以上的选定文件通过Git LFS管理；`.gitattributes` 保留原始字节，避免自动换行改变冻结哈希。请执行：

```powershell
git lfs install
git -c core.longpaths=true clone https://github.com/XiongBT49/capstone-micro-macro.git
cd capstone-micro-macro
git lfs pull
uv sync --locked
uv run python capstone.py doctor
```

克隆需要数GB磁盘及下载空间。宏观示例还会在 `runs/` 创建独立可写数据库，每次约额外2GB。不要把LFS指针文本误认为已下载的数据库。

宏观发布包自己的 `.gitignore` 默认忽略数据库；本仓库只为确定的运行数据库显式纳入跟踪，不强制纳入其他忽略内容。

## 后续维护

新实验输出先写入 `runs/`。验收后将需要长期保存的输入、响应、评分、日志和摘要冻结到 `results/experiments/<实验标识>/`，更新索引；新增大文件须补LFS规则。不要覆盖历史评分、未知请求或原始输入。

完整运行和检查方式见[运行指南](quickstart.md)，历史迁移检查见[验收记录](verification.md)。
