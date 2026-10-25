# 全局公约

我是技术顾问，做云迁移交付、方案设计与售前报价。以下是所有 Agent 会话都要遵守的约定。

## 身份与工作背景
- 云迁移方向技术顾问 / 合伙人，就职安畅（Anchnet）。
- 交付方法论：Landing Zone 八领域 + Well-Architected；定价模型 **AC-MIG**，标准人天单价 **$350/人天**。
- 标准交付物：HLD（20–30 页）、LLD、SOW（14 章结构）。
- 自有平台 **AICCP**（AI Cloud Consulting Platform）：Vue3 + FastAPI + PostgreSQL 16 + Redis + MinIO，Docker 5 容器，部署于腾讯云 ECS。

## 进行中的项目
| 项目 | 内容 | 状态 |
|---|---|---|
| QY-DubaiFintech | AWS → 阿里云迪拜 me-east-1，76 EC2/27 DB/45 Redis/51TB，目标 2AZ 双活 | 报价阶段 |
| 汤臣倍健 DataWorks | Trino → Spark 双跑迁移 | 754 已修 / 722"空日志"待解 |
| 美年体检 AI 数据中台 | MJ-AI-DW-2026-001，108 人天，MaxCompute/Hologres/RDS PG/OSS | LLD 阶段 |
| Tapestry Landing Zone | HLD 23 页 8 领域已完 | LLD PPT 待做 |
| 远景能源 | 云迁移调研 | 推进中 |
| Hermes Agent v0.10.0 | 自有 Agent，OCI ARM (eu-frankfurt-1) + 阿里云 ECS 双线部署 | 运行中 |

## 不可违反的边界
- **回复一律用简体中文**，技术术语保留英文。
- **凭证不进对话**：API Key、SSH 私钥写入本地文件，回复中只给路径。
- **不编造数字**：资源量、价格、进度必须核实；不确定就标注"未核实"。
- **AI 能力必须走 Skill → Prompt → LLM → Structured Output**，禁止裸调 LLM。
- **外部动作先确认**：发邮件、推生产、公开提交；内部动作（读文件、分析、建本地文件）直接做。
- **核心问题没解决不中断**，先自试 3 种思路再求助，求助时带上已尝试清单。

## 详细规则
分类规则见 rules 目录，按需展开：

- `rules/output-style.md` —— 语言、结构、状态符号、交付物格式
- `rules/coding.md` —— 技术栈、三层架构、UUID 主键、RBAC、事实优先
- `rules/cloud-msp.md` —— 迁移五阶段、Landing Zone 八领域、AC-MIG 定价、SOW 14 章
- `rules/selling.md` —— 报价结构、中英双语、去 AI 味、客户沟通

## 环境备注
- 本地 Windows，工作目录 `D:\Work\日常\上云迁移\`，WSL 可用。
- 服务器：腾讯云 ECS 8.153.152.218（Ubuntu 24.04）；OCI ARM 免费实例（eu-frankfurt-1）。
- ali CLI profile：`liujinlong`(cn-shanghai)、`tc_bigdata`(cn-shenzhen)、`anchang`(cn-hangzhou)。
- 项目文档与报价模板托管在 Feishu(Lark) wiki / sheets。
