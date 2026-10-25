---
name: fde-toolkit
description: FDE全栈交付工具包。整合fdeops/fdestack/openfde/fde-guide，触发FDE交付。
---

# FDE Toolkit — 全栈交付方法论

> 核心原则: **用 Skills 管流程执行，用仓库管业务记忆**

## 四大支柱

| 支柱 | 来源 | 核心能力 |
|------|------|----------|
| **fdeops** | suboss87/fdeops | 阶段化交付 CLI (land→discover→plan→ship→outcome) |
| **fdestack** | Dan-Cleary/fdestack | 8 个客户生命周期 Skills (triage→context→discovery→scope→value→poc→integrate→retro) |
| **openfde** | memovai/openfde | 本地优先记忆工作区 (ontology facts + task state machine + evals) |
| **fde-guide** | davidahmann/fde-guide | 方法论 Playbooks (现场发现 / 方案设计 / 运维规模化) |

---

## 1. 交付阶段模型 (fdeops)

```
land → discover → plan → ship → outcome
 ↓         ↓          ↓       ↓         ↓
brief   interview   sequence  staging   ledger
access  reality     done-criteria  live   promised→measured→accepted
```

### 各阶段检查点

| 阶段 | 入口条件 | 出口条件 |
|------|----------|----------|
| **Land** | 客户名称已知 | 签署人(brief owner)已确认、done 已定义 |
| **Discover** | 有 brief | 现实 vs brief 差异已命名、下一步已同意 |
| **Plan** | 有成功标准 | 顺序/首个可见变化/done 已上记录 |
| **Ship** | staging 就绪 | staging 已验证、回滚已跑、上线检查已记录 |
| **Outcome** | 有承诺指标 | promised→measured→accepted 三拍账本已对齐 |

### 关键铁律
- **Never tell the human to type the CLI** — Agent 自己跑 `fde resume`
- **Do not invent** — 缺事实标 `unknown - ask: <question>`
- **Confirm before write to `.fde/`**
- **A number nobody signed is claimed, not delivered**

---

## 2. 客户生命周期 Skills (fdestack)

8 个 Skills 形成闭环：

```
triage → customer-context → discovery → scope → value-frame → poc → integrate → retro
 ↓              ↓               ↓          ↓         ↓           ↓        ↓           ↓
优先级        session brief    真实问题    二元标准    CFO 杠杆    一次性    生产级     复盘
```

### Skill 速查

| Skill | 输入 | 输出 |
|-------|------|------|
| `/triage` | — | 活跃客户排序 (urgency = blockers×3 + unknowns×1 + within-7d×5) |
| `/customer-context` | 客户名 | 上轮决策 / 漂移 / 阻塞 / 学到的 |
| `/discovery` | 会议转录 | 新利益方 / 真实问题 vs 陈述问题 / HIGH unknowns |
| `/scope` | 目标陈述 | 二元成功标准 (模糊项→unknowns.md HIGH) |
| `/value-frame` | 延迟/损失场景 | 资本杠杆 /  headline $X/yr / 敏感度区间 |
| `/poc --purpose` | feasibility/performance | 一次性验证 + Step 9 "学到了什么" → stack.md |
| `/integrate` | — | 从零重建 (禁读 POC 代码) |
| `/engagement-retro` | — | Shipped/Stuck/Learned/Next + 周一 HIGH unknowns |

### 第二客户问题
> 第一个 engagement 感觉魔法般因为一切在脑中，第二个崩溃因为什么都没留下。
> **解法**: git history IS the engagement. 笔记像代码一样 commit。

---

## 3. 记忆与任务系统 (openfde)

### 核心循环 (Agent 执行)

```
1. openfde task list --status ready    → 找活
2. openfde task claim <id>             → 认领
3. openfde context <id>                → 拉弹药包 (约束先行!)
4. openfde task start <id>             → 开工
5. openfde remember "fact" --source X  → 发现即记录 (source 必填)
6. openfde task done <id>              → 提交评审
```

### 记忆规则
- **Provenance is mandatory** — 无 source URI 的写入被拒绝
- **Bi-temporal** — 矛盾事实替代而非删除，`recall --mode handoff` 回放时间线
- **LLM-free read path** — 检索毫秒级 (BM25 + entity graph + rank fusion)
- **Ontology-constrained** — 固定领域本体 (goals/workflows/decisions/constraints/data sources/pain points)

### 任务状态机
```
ready → claimed → in-progress → done → accepted
                  ↓
              blocked
```

### CLI 速查

| 命令 | 作用 |
|------|------|
| `engagement create/list/use` | 管理客户项目 |
| `ingest <files>` | 摄入材料 (text/markdown/PDF/image) |
| `extract` | 本体约束提取 |
| `recall <query>` | 混合检索 (cited) |
| `whoknows <topic>` | 谁是专家 (evidence-cited) |
| `task create/claim/start/done/accept` | 任务状态机 |
| `context <task>` | 任务弹药包 |
| `research <query>` | 带引用的网络调研 |
| `eval <task> --input <file>` | 评分卡判定 |
| `report` | 执行摘要 (4 问题) |
| `serve` | 本地工作区 (:4517) |
| `share` | 只读 LAN 链接 (给老板看) |

---

## 4. 方法论 Playbooks (fde-guide)

### 4.1 现场发现与重构 (Field Engagement)

**现场循环**:
```
inherit story → find knowers → observe case → compare claims
→ expose conflict → propose reframe → get disposition → next move
```

**五角色分离** (一人可兼多角色，但各有证据基础):

| 角色 | 问题 |
|------|------|
| Sponsor | 谁想要结果/出资? |
| Process knower | 谁解释代表性和异常案例如何流转? |
| Operator | 谁执行/审核/接收工作? |
| Disposition authority | 谁可接受/拒绝/推迟/约束? |
| Verifier | 谁能独立确定结果是否发生? |

**硬性区分**: sold ≠ stated ≠ observed ≠ system-enforced ≠ policy-authorized

### 4.2 发现与价值工程 (Discovery & Value)

**资格硬门** (任一不满足即淘汰):
- 无负责运营 owner
- 无有界的决策/行动/工作产物
- 无可测量结果或无基线计划
- 无负担得起的验证者
- 必要上下文无法合法访问
- 首个有用发布需不可逆高风险效果
- 无采用路径
- 无团队支持事件响应

**运营需求最小句**:
```
[user] uses [surface] to make [decision]
from [inputs], then performs [action]
so that [outcome] changes [metric].
```

### 4.3 方案设计与交付 (Solution & Delivery)

**设计单元 = 运营决策** (不是模型调用)

**交付单元 = 最小端到端切片** (可证明结果 + 代表数据 + 真实控制 + 可用界面)

**智能选择阶梯** (按序评估):
1. 确定性软件
2. 优化/约束求解器
3. 经典 ML/统计模型
4. 搜索与检索
5. 单次模型调用 (typed I/O)
6. 编码工作流 + 模型辅助步
7. 有界 agent (tools + stop conditions)
8. 多 worker (仅当真正的上下文/权限/专业化边界)
9. 人工审核 (弱可验证或高风险)

### 4.4 运维与规模化 (Operate & Scale)

**服务合同** (上线前命名):
- 5 类 owner (operational/technical/risk/service/on-call)
- 支持段 / 自治级别 / 工具包 / 排除工作
- 接受结果 / 主价值指标 / 护栏 / SLO
- 依赖清单 + 变更通知
- 支持小时 / 升级路径 / 严重度 / 响应 / 恢复
- 发布权限 / 回滚权限 / 杀开关

**运营节奏**:
| 节奏 | 审查 | 决策 |
|------|------|------|
| 持续 | 禁止效果 / 授权拒绝 / 数据新鲜度 / 杀开关 | 遏制/降级/继续 |
| 每日 | 事件 / 失败运行 / 审核积压 / SLO 消耗 | 分拥有者/调和/暂停 |
| 每周 | 行为簇 / eval 失败 / 覆盖 / 放弃 / 支持主题 | 修/重放/重构/接受债 |

**权限阶梯**: observe → recommend → act with approval → bounded autonomous (按段和效果类分别推进)

---

## 5. 实操路径建议

### 推荐采用顺序

```
Step 1: fde-guide → 建立分工与框架认知
Step 2: fdestack → 规范推进流程 (8 skills)
Step 3: fdeops → 阶段化 CLI 执行
Step 4: openfde → 记忆底座 + 任务系统
```

### 单兵 OPC+FDE 适配

| 原设计 | 单兵适配 |
|--------|----------|
| 多角色分离 | Hermes 用 Skill 切换角色视角 |
| 客户仓库 | `~/.hermes/engagements/<slug>/` |
| Git 备份 | 已有 GitHub backup cron |
| 团队交接 | session_search + memory 检索 |
| 共享工作区 | Telegram/飞书交付物 |

### 与 Anchnet 交付体系的映射

| FDE 概念 | Anchnet 对应 |
|----------|-------------|
| Engagement | 项目 (明道/飞书记录) |
| Discovery | BasicInfo 收集表 |
| Scope | SOW 14 章 |
| POC | 技术方案验证 |
| Outcome | SLA 分档 (To Business/Customer/IoT) |
| Operate | SmartCare 运维 |
| Retro | 项目复盘 |

**集成点**: FDE skill 调用 presales-architect / cloud-migration / spreadsheet-delivery 产出正式交付物。
