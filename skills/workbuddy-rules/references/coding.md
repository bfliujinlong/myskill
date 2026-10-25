---
description: 编码与技术栈规范。适用于所有代码编写、架构设计、AI 能力开发场景。
---

# 编码规范

## AI 能力调用（硬性）
任何 AI 功能必须走 **Skill → Prompt → LLM → Structured Output** 四段式：
1. Skill 定义任务边界与输出 schema
2. Prompt 模板化，变量外置，不硬编码在业务代码里
3. LLM 调用统一走封装层，带超时、重试、兜底
4. 输出必须是结构化（JSON/Pydantic Model），**禁止直接把 LLM 原始文本当结果用**

**禁止**在业务代码里裸调 LLM。

## AICCP 平台技术栈
| 层 | 选型 | 约束 |
|---|---|---|
| 前端 | Vue 3 | Composition API |
| 后端 | FastAPI | 严格三层：Controller / Service / Repository |
| 数据库 | PostgreSQL 16 | **主键一律 UUID**，禁用自增 int |
| 缓存 | Redis | |
| 对象存储 | MinIO | |
| 部署 | Docker (5 容器) + GitHub Actions SSH | 目标腾讯云 ECS 8.153.152.218 |

### 不可违反
- **Controller 不写业务逻辑**，只做参数校验与响应封装。
- **Repository 不写业务规则**，只做数据访问。
- 业务逻辑全部落在 Service 层。
- 权限控制统一走 **RBAC**，不在接口里散落判断。
- 写操作必须有事务边界；跨服务调用不用分布式事务，用补偿或幂等。

## 通用工程
- 提交前跑通 lint + 类型检查；测试用 pytest（Python）/ vitest（前端）。
- 环境差异用 `.env` + 配置类，禁止硬编码地址、端口、密钥。
- 数据库变更用迁移工具（Alembic），**禁止手工改表结构**。
- 新增接口同步更新 API 文档。

## 事实优先（Fact Sheet First）
- 涉及具体项目、资源、价格、进度的回答，**先核实事实再推理**。
- 数据不确定时明确标注"未核实"，不要为了让答案完整而编造数字。
- 资源清单类输出必须标注采集时间与来源环境（源端/目标端/哪个账号哪个 region）。
