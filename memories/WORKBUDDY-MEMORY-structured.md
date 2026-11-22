# WorkBuddy 云端记忆 · 结构化梳理版

> 导出时间：2026-09-06
> 说明：对 `MEMORY-full.md` 原文的结构化重写，信息不增不减，仅改为便于维护与检索的形式。
> 保真版本见 `MEMORY-full.md`（可直接粘回任何 Agent）。

---

## 1. 身份画像

| 项 | 值 |
|---|---|
| 角色 | 阿里云/数据迁移方向技术顾问、合伙人 |
| 公司 | 安畅 Anchnet |
| 驻地 | 中国上海 |
| 语言 | 中文第一语言，**所有回复必须用中文** |
| 本地环境 | Windows（用户名 `bXfyalongx`）+ WSL（用户名 `Manju`） |
| 邮箱 | liujinlong@outlook.com |
| 工作目录 | `D:\Work\日常\上云迁移\` |

## 2. 交付方法论与商务基准

| 项 | 值 |
|---|---|
| 交付方法论 | cloud-migration-pm（Landing Zone 八领域 + Well-Architected） |
| 定价模型 | AC-MIG |
| 标准人天单价 | **$350 / 人天** |
| SOW 结构 | 标准 14 章 |
| 报价迭代模式 | 基线版 → 对齐参考模板 → 分别输出中英双版 |
| 交付物格式 | 对外 Word(.docx)；讲解用 PPT；内部测算 Excel |
| 文档协作 | Feishu(Lark) wiki / sheets / drive |

## 3. 项目台账

| 项目 | 编号/标识 | 内容 | 状态 |
|---|---|---|---|
| QY-DubaiFintech | QY 业务线 | AWS → 阿里云迪拜 me-east-1；76 EC2 / 27 DB / 45 Redis / 51TB / 5 源区；目标 2AZ 双活 | 报价冲刺中 |
| 汤臣倍健 DataWorks | 0621 批次 | Trino → Spark 双跑迁移 | **754 已修 / 722"空日志"待解** |
| 美年体检 AI 数据中台 | MJ-AI-DW-2026-001 | 108 人天，10 章 LLD；MaxCompute/Hologres/RDS PG/OSS | LLD 阶段 |
| Tapestry Landing Zone | — | HLD 23 页 8 领域 | HLD 完成，LLD PPT 待做 |
| 远景能源 | Envision Energy | 云迁移调研 | 推进中 |
| AICCP | 自有平台 | AI Cloud Consulting Platform | 收尾中 |

### 汤臣倍健 0621 错误分类明细（1561 失败实例 / 571 任务 / 16 类）

| 类别 | 任务数 | 细分 |
|---|---|---|
| Trino→Spark 迁移失败 | 137 | DDL 不兼容 114、目录命名 14、函数差异 9 |
| DataWorks DI 配置问题 | 175 | 生产数据源缺失 29、环境未绑定 19、字段未映射 22 |
| Serverless 资源组缺包 | 102 | Python 自定义镜像缺依赖 46 |

团队分工：潘超胜、刘家君、丁宇文、陈铭

## 4. 技术栈与架构约束

| 层 | 选型 | 约束 |
|---|---|---|
| 前端 | Vue 3 | — |
| 后端 | FastAPI | Controller / Service / Repository 三层 |
| 数据库 | PostgreSQL 16 | **主键一律 UUID** |
| 缓存 / 存储 | Redis / MinIO | — |
| 部署 | Docker 5 容器 | 腾讯云 ECS Ubuntu 24.04 |
| 权限 | RBAC | 不在接口散落判断 |

**不可违反：**
- AI 能力必须走 `Skill → Prompt → LLM → Structured Output`，禁止裸调 LLM
- Fact Sheet First：涉及项目/资源/价格/进度，先核实事实再推理
- 数据不确定必须标注"未核实"

## 5. 环境与凭证位置

| 项 | 位置 / 值 |
|---|---|
| 腾讯云 ECS | Ubuntu 24.04，`8.153.152.218` |
| GitHub 仓库 | `bfliujinlong/AI-CCP`（GitHub Actions SSH 部署） |
| OCI ARM | 免费 A1，`eu-frankfurt-1` |
| GCP | `us-central1-f` 免费 e2-micro（`free-ubuntu-vm`，Ubuntu 24.04） |
| ali CLI profile | `liujinlong`(cn-shanghai)、`tc_bigdata`(cn-shenzhen)、`anchang`(cn-hangzhou) |
| SSH 私钥 | 本地文件（如 `kimtestkey.pem`），**不进对话** |
| Claude Code | 腾讯云 Coding Plan（`sk-sp-***REDACTED***`，WorkBuddy/Anthropic 兼容端点） |
| WorkBuddy 积分 | 12,288.9，封闭生态，仅能在 WorkBuddy/CodeBuddy CLI 内消耗 |

## 6. Hermes Agent

| 项 | 值 |
|---|---|
| 版本 | v0.10.0 |
| 部署位置 | OCI ARM A1（eu-frankfurt-1）+ 阿里云 ECS 8GB，双线 |
| 集成 | Telegram / DashScope |
| 抢实例工具 | `oracle-arm-grab-toolkit`，目标 10 分钟内抢到 |

## 7. 协作偏好（重要）

| 维度 | 要求 |
|---|---|
| 输出结构 | 表格 + 有序步骤 + 状态符号 `✅ 完成 / ⚠️ 风险或未验证 / ❌ 失败或阻塞` |
| 提问风格 | 用户提问极简（1–3 词），**先推断上下文再答**，不要反问澄清 |
| 续接 | **从断点继续**，不重头复述背景 |
| 韧性 | "不解决不要停"——核心问题未解决不中断；自试 3 种思路再求助 |
| 求助方式 | 带"已试 A/B/C，现象 X/Y/Z"，不说"失败了" |
| 验证 | 配置/部署后**必须实测验证**，贴出命令与输出 |
| 凭证 | 写入本地文件，回复只给路径，不粘贴内容 |
| 去 AI 味 | 禁用"赋能/一站式/数字化浪潮/深度融合"等填充词 |
| 截图 | 常分享截图要求解读，并期待给出下一步操作建议 |

## 8. 时间线

| 日期 | 事件 |
|---|---|
| 2026-06-03 | 确立 AICCP 技术栈与架构约束（三层、Fact Sheet First、UUID PK、RBAC）；强制 AI 四段式调用 |
| 2026-06-20 | 确认 AICCP 部署方案（ECS + Docker 5 容器） |
| 2026-06-25 | 汤臣倍健 0621 深度剖析完成，16 类错误分类，团队分配 |
| 2026-07 | Claude Code 切腾讯云 Coding Plan 替代智谱 GLM-5；ali CLI 区域调至 cn-shanghai |
| 2026-08-11 | AICCP 通过 GitHub Actions SSH 部署至 ECS |
| 2026-08 | 美年 LLD 推进；远景能源调研启动；OCI 部署 Hermes v0.10.0；Tapestry HLD 完成 |
| 2026-08 | 汤臣倍健 754 已修/722 待解；GCP 免费 VM 创建；OCI 抢实例脚本优化 |
| 2026-08 | QY-DubaiFintech 报价立项，确定 cloud-migration-pm + AC-MIG @ $350/人天 |
| **2026-09-06** | **完成 WorkBuddy 全量资产盘点与导出：50 个技能（42 Linux + 8 macOS 隔离）、云端记忆 5774 字、4 份分类规则、跨 Agent 同步脚本 v2** |
| **2026-09-06** | **修正跨 Agent 同步路径错误（skills/ ≠ 配置目录），验证 CRLF、rsync 缺失、pipefail SIGPIPE 三个坑** |
| **2026-09-06** | **确认沙箱 22 端口被网络层封锁且出网白名单，无法直连 OCI；改用 GitHub Actions 作为同步跳板** |
