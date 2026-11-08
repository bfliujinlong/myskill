---
name: team-agent-binding
description: >
  团队岗位 -> 可执行 Agent -> MCP -> Skill 四层绑定方法论（文档型）。当用户要求"把团队岗位落成 agent"
  "按角色最小授权""配置 team/agent/mcp/skill 绑定""理清 team 与报价能力如何串起来"时激活。
  本 skill 不执行命令，只给出可复制的绑定表、目录结构与红线；报价引擎本体在 mig-quotation / brand-doc-kit。
version: 2026-11-01.001
status: active
allowed-tools: Read, Write
---

# Team -> Agent -> MCP -> Skill 四层绑定方法论

> 来源实测：team_agent_mcp_skill.md（2026-10-31 本机实测）。所有结论基于实测，未实测标「待确认」。
> 这是一份**方法论 skill**：它只描述"怎么绑"，真实跑量产物由 mig-quotation / brand-doc-kit 提供。

## 0. 两条硬约束（写进每个 agent）

1. **零费用**：MCP 一律只读起步；Azure 只读、不自动停资源；绝不刷信用卡。
2. **最小授权**：agent 只拿本岗位必需的 MCP/skill。全员全开 = 凭据泄露面 + 上下文污染。

## 1. 目录结构（四层各落一处）

```
~/.hermes/
├── teams/                      # 第 1 层：Team 定义（岗位 -> agent 映射）
│   └── <team>.md
├── agents/                     # 第 2 层：Agent 定义（唯一枢纽，本次主体）
│   └── <agent>.md              # 内含 mcp:[] 与 skills:[] 白名单
├── config.yaml                 # 第 3 层：MCP 实例（改 enabled: true）
├── skills/<team>/              # 第 4 层：Skill（按团队域归置）
└── learning/<team>/            # 知识库（各 agent 独占）
```

**agent 是唯一枢纽**：向上声明归属 team，向下用白名单锁 MCP + skill。
三条单向依赖 Team -> Agent -> {MCP, Skill}，改 skill 不动 agent，改 agent 不动 team。

## 2. Agent 定义模板（每个 agent 一份）

```markdown
---
name: presales-architect
team: presales
role: 售前架构师
---

# 售前架构师

## 职责边界
- 负责：RFP 应答、方案设计、6R 定级、报价输入
- 不负责：合同条款（-> legal）、开票（-> finance）、割接执行（-> delivery）

## 绑定 MCP（白名单）
- feishu-mcp（文档/消息）
- aws-pricing（报价比价；当前 disabled，按需启用）

## 绑定 Skill（白名单）
- presales/pcs-presales-orch
- presales/pcs-arch-6r
- presales/pcs-quotation
```

## 3. 岗位 -> Agent -> MCP -> Skill 绑定表（实测存在）

### A. 经营与职能
| 岗位 | Agent | MCP | Skill |
|---|---|---|---|
| CEO | ceo | feishu-mcp | consulting-report-forge, week-report-write, archify, diagram-design |
| 法务 | legal | feishu-mcp | grounded-citations, ocr-and-documents, pdf, docx（缺合同审查 skill） |
| 财务 | finance | feishu-mcp | roles-finance, spreadsheet-delivery, xlsx |
| 人事 | hr | feishu-mcp | hr-hire（career-ops 空壳） |

### B. 业务线
| 岗位 | Agent | MCP | Skill |
|---|---|---|---|
| 商务 | bd | feishu-mcp | sales, business-development, fde-client-discovery-questions |
| 项目经理 | pm | feishu-mcp | project-manager, landing-zone-pm, cloud-migration-pm |
| 售前 | presales-architect | feishu-mcp, aws-pricing | presales/pcs-* 全部 18 个 |

### C. 架构师（4 子域，不压扁）
| 子域 | Agent | MCP | Skill |
|---|---|---|---|
| 大数据云迁移 | arch-migration | alicloud, aws, azure(只读), huaweicloud×5 | cloud-migration, roles-bigdata, hive/hdfs/oss/redis/oracle/sql 迁移评估 |
| 开发 | arch-dev | feishu-mcp | roles-database, tdd, github-pr-workflow, github-code-review |
| AI | arch-ai | alicloud | ai-demo-builder, adp-app-builder, strands-agents, llm-wiki |
| Ops | arch-ops | alicloud, azure(只读) | cloud-vm-monitoring, oci-always-free-ops, server-hardening |

### D. 交付 / 运维
| 岗位 | Agent | MCP | Skill |
|---|---|---|---|
| 交付·中级 | eng-senior | alicloud, aws, huaweicloud×5 | solution-delivery, fde-toolkit, mig-cutover-plan, mig-lld |
| 交付·初级 | eng-junior | alicloud | github-auth, github-issues, spike, codebase-inspection |
| 运维 | ops-senior | alicloud, azure(只读) | systematic-debugging, node-inspect-debugger, python-debugpy |

## 4. MCP 启用策略（分批次，不一次性全开）

| 批次 | MCP | 理由 | 风险 |
|---|---|---|---|
| P0（立即） | feishu-mcp | 已启用，全岗位通用 | 无 |
| P1（有项目时） | alicloud | 售前/架构/交付/运维主干 | 只读 AK |
| P2（按需） | aws, aws-pricing | 源云 AWS 的迁移/比价 | 只读 |
| P3（谨慎） | azure | 只读红线，绝不自动停资源 | 高，需单独审批 |
| P4（低频） | huaweicloud×5 | 华为云项目才开 | 5 进程占用 |

## 5. 报价能力落点（与本 skill 配套）

`team-agent-binding` 只管"岗位怎么绑 agent"；**报价产物**由如下两个 skill 提供（同包内）：

- `mig-quotation` — 离线确定性报价引擎（calc_total / validate_pricing / xlsx_from_md），无后端依赖。
- `brand-doc-kit` — 厂家色系单一事实源（alibaba/tencent/anchnet/aws/azure），生成变体模板 + 渲染 docx + 开箱核验。

代理岗位（如 presales-architect）的 Skill 白名单应包含这两者，使"出报价单"成为可路由能力。

## 6. 红线（继承自 AGENTS.md）

- 零费用，绝不刷信用卡；MCP 一律只读起步。
- Azure 只读、不自动停资源；不碰客户生产变更。
- 不在 docx/方案虚构人员·案例·证书（废标风险）；未核实写「待确认」。
- 调研报告不含价格/人天/月费；报价是独立产物，物理隔离。
- API Key chmod 600，不进聊天、不进文档。
- 抓不到就说抓不到，不伪造数据（失败写 fetch_failed）。
- **最小授权**：非必需岗位不开云 MCP（如 HR 不需要 alicloud）。
