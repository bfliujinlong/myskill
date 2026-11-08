---
name: intake-orch
description: 统一入口路由编排。触发条件：收到任意新需求/一句话任务，需要判定意图并分派到对应 team/agent 执行时触发（如"报个价""做个方案""迁移启动""帮我排期""分活"）；完成判据：输出结构化路由结果（目标 agent + 下游编排 skill + 入参校验 + 是否需要升级），或把多步任务拆成有序可执行序列。本 skill 不产出业务内容，只做意图识别、team/agent 路由与多步任务编排；具体方案/报价/代码由下游叶子 agent/skill 产出。
风险等级: 只读
输入参数: 用户的一句话需求（原始文本）；可选：已确认的客户/项目背景
依赖工具: []
版本: 2026-11-02.001
编排: [team-agent-binding, presales/pcs-presales-orch, mig-std/mig-startup-orch, mig-std/mig-delivery-orch, presales/pcs-quotation, mig-std/mig-quotation]
---

# 统一入口路由编排（intake-orch）

团队的统一入口 agent（`intake`，team=coordinator）的路由大脑。本身不写方案、不算价、不碰云，只把需求落到正确的人/编排上，并跟踪多步任务。下游叶子编排（`pcs-presales-orch` / `mig-startup-orch` / `mig-delivery-orch`）各自保留业务判断，本 skill 只做"分活"与"串活"。

## 决策树（意图 -> 路由）

```
入口：一句话需求
  │
  ├─ 含 报价/人天/费用/价单/多少钱？
  │    └─ 售前报价 → presales-architect → pcs-presales-orch（或 mig-std/mig-quotation）
  │
  ├─ 含 方案/选型/HLD/6R/SOW/架构？
  │    └─ 售前方案 → presales-architect → pcs-presales-orch
  │
  ├─ 含 迁移/上云/切换/立项/资源评估？
  │    └─ 迁移启动 → arch-migration → mig-std/mig-startup-orch
  │
  ├─ 含 实施/割接/排期/看板/任务编排？
  │    └─ 实施交付 → delivery-lead → mig-std/mig-delivery-orch
  │
  ├─ 含 计划/WBS/排期/风险/里程碑？
  │    └─ 项目管理 → pm
  │
  ├─ 含 运维/监控/值守/告警？
  │    └─ 运维 → arch-ops / ops-senior / ops-junior
  │
  ├─ 含 初级交付/初级工程师/GitHub任务/代码issue/代码审查？
  │    └─ 初级交付 → eng-junior
  │
  ├─ 含 基础监控/告警值守/初级巡检？
  │    └─ 监控值守 → ops-junior
  │
  ├─ 含 财务/回款/毛利/成本？
  │    └─ 财务 → finance / cfo
  │
  ├─ 含 商务/折扣/付款/合同商务条件？
  │    └─ 商务 → bd
  │
  ├─ 含 合同/责任/合规/资质/法务？
  │    └─ 合规 → legal
  │
  ├─ 含 经营/复盘/决策/优先级？
  │    └─ 经营 → ceo
  │
  ├─ 含 人事/招聘/行政？
  │    └─ 人事/行政 → hr / admin
  │
  ├─ 含 AI/中台/智能体？
  │    └─ AI → arch-ai / platform-eng
  │
  ├─ 含 数据/数仓/大数据？
  │    └─ 数据 → arch-data
  │
  ├─ 含 开发/代码/数据库/PR？
  │    └─ 开发 → arch-dev
  │
  └─ 无法判定 / 跨域歧义 → 降级为「待确认清单」，升级给人（刘金龙）
```

## 多步任务编排（固定顺序）

当用户给出多步意图（如「报价 → PM 立计划 → 架构师出方案 → 评审」），按依赖串行：

| 顺序 | 阶段 | 负责 agent | 下游编排/skill | 闸门 |
|---|---|---|---|---|
| 1 | 报价 | presales-architect | pcs-presales-orch / mig-quotation | verify_gate |
| 2 | 立计划 | pm | project-manager / pcs-wbs-std | — |
| 3 | 出方案 | presales-architect | pcs-presales-orch / pcs-hld | — |
| 4 | 评审 | intake 汇聚 | review_gate（三件一致性） | review_gate |

每一步产物作为下一步入参；任一 gate 不通过即阻塞当前步并升级，不静默继续。

## 输出双形态

结构化 JSON：
```json
{
  "intent": "报价+多步交付",
  "route": [
    {"step": 1, "agent": "presales-architect", "skill": "pcs-presales-orch", "gate": "verify_gate"},
    {"step": 2, "agent": "pm", "skill": "project-manager", "gate": null},
    {"step": 3, "agent": "presales-architect", "skill": "pcs-hld", "gate": null},
    {"step": 4, "agent": "intake", "skill": "review_gate", "gate": "review_gate"}
  ],
  "escalation": null
}
```

人类可读：列出「分给谁 / 为什么 / 下一步入参 / 是否需要升级」。

## 升级契约

- 意图无法判定 → 输出待确认清单 + 升级给人（刘金龙，飞书 open_id `ou_0864b8895ec112ec236f5295a6330c36`）
- 下游 agent 升级 → 汇聚已完成阶段产物 + 链路升级包，不得静默跳过
