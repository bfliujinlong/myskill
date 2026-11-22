# WorkBuddy 云端记忆 · 完整原文

> 导出时间：2026-09-06
> 来源：WorkBuddy 云端记忆库（系统提示 `<memory>` 段，5774 字符）
> 用途：可直接整段粘回任何 Agent 的记忆/系统提示中，语义完全保真，无任何改写。

---

**工作背景**
用户是阿里云/数据迁移方向的技术顾问与合伙人，就职安畅（Anchnet），采用 cloud-migration-pm 交付方法论与 AC-MIG 定价模型，标准 SOW 14 章结构，统一报价人天单价 $350/人天；业务线 QY 覆盖中东方向售前与交付，面向迪拜 Fintech 等海外客户。负责交付、SOW、客户方案讲解与报价输出，工作目录 D:\Work\日常\上云迁移\ 下含服务流程、汤臣倍健 DataWorks 等子项目。当前主导构建 AI Cloud Consulting Platform (AICCP)，技术栈采用 Vue3/FastAPI/Docker(5容器)，存储层 PostgreSQL 16/Redis/MinIO，使用 UUID 主键和 RBAC 权限控制，严格遵循 Service/Repository/Controller 三层设计，AI 能力实现必须通过 Skill→Prompt→LLM→Structured Output 流程调用，禁止直接 LLM 交互；生产部署在腾讯云 ECS（Ubuntu 24.04, 8.153.152.218），GitHub Actions SSH 部署，仓库 bfliujinlong/AI-CCP，ali CLI profile 包含 liujinlong(cn-shanghai)、tc_bigdata(cn-shenzhen)、anchang(cn-hangzhou)。主导交付项目包括：汤臣倍健 DataWorks 双跑迁移（754 已修/722"空日志"待解）、美年体检 AI 数据中台（MJ-AI-DW-2026-001，108 人天 10 章 LLD）、Tapestry 阿里云 Landing Zone（HLD 23 页 8 领域已完，LLD PPT 待做）、远景能源（Envision Energy）云迁移调研。Hermes Agent v0.10.0 同时部署在 Oracle Cloud 免费 Arm A1（eu-frankfurt-1）与阿里云 ECS 8GB 环境，集成 Telegram/DashScope。Claude Code 已切换至腾讯云 Coding Plan（sk-sp-***REDACTED***，WorkBuddy/Anthropic 兼容端点）。

**个人背景**
用户基于中国上海（本地 Windows 用户名 bXfyalongx，邮箱 liujinlong@outlook.com，WSL 用户名 Manju），中文为第一语言，所有回复必须使用中文；技术细节表达要求结构化、逻辑清晰，偏好表格、可执行步骤、状态符号（✅⚠️❌）的简洁技术输出，标点空格风格随意，提问极简（1-3 词或短语）依赖共同上下文期待助手推断。报价交付物偏好中英双语自然专业，整体外交付物偏好 Word/docx 格式。会话常以闲聊问候（hi/在吗/早上好/nih）开场请求状态检查，常分享截图请求解读并期待给出下一步操作建议。期望助手从前次断点继续而非重头开始，习惯根据分析结果将任务分类拆分并分配团队成员（汤臣倍健团队：潘超胜、刘家君、丁宇文、陈铭）。坚持"不解决不要停"的工作风格，核心问题未彻底解决不中断；配置完成后常要求助手验证测试。敏感凭证（API key、SSH 密钥 kimtestkey.pem 等）写入本地文件而非聊天发送。Bash 工具有沙箱限制，默认不能 SSH 外部服务器，需 dangerouslyDisableSandbox。WorkBuddy 积分（12,288.9）为封闭生态，仅能在 WorkBuddy/CodeBuddy CLI 内消耗。报价文档迭代模式：先生成基线版本 → 按参考模板对齐 → 分别输出中英双版；Feishu(Lark) wiki/sheets/drive 用于项目文档与报价模板管理。

**当前关注**
聚焦 AICCP 平台收尾，严格执行三层架构与 Skill-Prompt-LLM-Output 调用规范，完善 GitHub Actions 自动化发布与腾讯云 ECS Docker 部署。全力冲刺 QY-DubaiFintech 云迁移报价交付（项目号 QY-DubaiFintech，AWS→阿里云迪拜 me-east-1，76 EC2/27 DB/45 Redis/51TB/5 源区，目标 2AZ 双活架构），严格按参考模板格式与 AC-MIG 定价逻辑生成中英双语报价，避免 AI 感。同步处理汤臣倍健 0621 文件夹失败数据深度排查（1561 失败实例/571 任务/16 类错误）：Trino→Spark 迁移失败 137 任务（DDL 不兼容 114、目录命名 14、函数差异 9）、DataWorks DI 配置问题 175 任务（生产数据源缺失 29、环境未绑定 19、字段未映射 22）、Serverless 资源组缺包 102 任务（Python 自定义镜像缺依赖 46）；已修 754 任务，722"空日志"问题待解，并基于分析分类拆分分配团队。美年体检 LLD 设计落地、Tapestry LLD PPT 输出、远景能源调研持续推进。Hermes Agent v0.10.0 双线部署已完成，OCI ARM 免费资源抢取脚本（oracle-arm-grab-toolkit）持续优化，目标 10 分钟内抢到实例；GCP us-central1-f 免费 e2-micro VM（free-ubuntu-vm, Ubuntu 24.04）已创建并 SSH 连接，遇配置疑问倾向截图反馈并要求逐步核对 Always Free 条件。

**近期动态**
- 2026-06-03：明确 AICCP 技术栈（Vue3/FastAPI/PG/Redis/MinIO）与核心架构约束（三层架构、Fact Sheet First、UUID PKs、RBAC）；确立 AI 开发规范，强制 Skill→Prompt→LLM→Structured Output 调用流程。
- 2026-06-20：确认 AICCP 部署方案（腾讯云 ECS 8.153.152.218 + Docker 5 容器）。
- 2026-06-25：汤臣倍健 0621 数据深度剖析完成，16 类错误分类清晰，修复任务团队内部分配。
- 2026-07：Claude Code 切换腾讯云 Coding Plan（WorkBuddy 凭证）替代智谱 GLM-5；ali CLI 'liujinlong' 区域调至 cn-shanghai。
- 2026-08-11：AICCP 通过 GitHub Actions SSH 部署至腾讯云 ECS，docker-compose.prod.yml。
- 2026-08：美年体检 AI 数据中台 LLD 推进 MaxCompute/Hologres/RDS PG/OSS 架构；启动远景能源云迁移调研；OCI 注册并部署 Hermes Agent v0.10.0（Telegram/DashScope）；确认 WorkBuddy 积分封闭无法导出；Tapestry Landing Zone HLD 23 页 8 领域完成。
- 2026-08：汤臣倍健 DataWorks 双跑迁移 754 已修/722"空日志"待解；GCP 免费 e2-micro VM 创建并 SSH 连接；OCI ARM 抢实例脚本优化中（oracle-arm-grab-toolkit）。
- 2026-08：QY-DubaiFintech 报价立项，资源评估与定价方法论确定（cloud-migration-pm + AC-MIG，$350/人天）。
