---
name: pcs-presales-orch
---

# PCS 售前全流程编排（pcs-presales-orch）

| 字段 | 值 |
|---|---|
| **description** | PCS 售前全流程编排 - 触发条件：用户发起一个新的 PCS 售前项目（云迁移/Landing Zone/多云比选），需要从客户信息收集到报价/SOW/WBS 售前交付物串联整个流程时触发（例如"帮我把这个客户从头做一遍售前"）；完成判据：决策树走到终点分支（售前交付物齐套并通过同源一致性自检，或在某一步升级）。只覆盖售前阶段；交付执行（割接切换/数据同步/LLD 详细设计）不在本 skill 范围，属交付域（`mig-cutover-*`/`mig-datasync`/`mig-lld`）。本 skill 不调用其他编排 skill（无嵌套）；description 与下面所有叶子 skill 的触发条件不重叠——叶子 skill 都要求"已有某个具体输入"才触发，本 skill 的触发条件是"项目刚开始、什么都还没有"。 |
| **风险等级** | 低风险写（本身不执行任何系统变更，仅按决策树调度叶子 skill；实际风险等级取决于被调用的叶子 skill） |
| **输入参数** | 客户背景信息（项目类型/当前云/目标云/约束，用于启动 `pcs-factsheet`）；用户希望走到哪一步（仅 Fact Sheet？还是要报价/SOW/WBS/全套？）；项目类型（通用迁移/Landing Zone 专项/大数据迁移，决定 WBS 与 LZ 分支选择） |
| **依赖工具** | aicc.execute_skill（间接，通过调用下面的叶子 skill） |
| **编排** | pcs-factsheet, pcs-quotation, pcs-sow, pcs-sow-lz, pcs-wbs-std, pcs-wbs-migration, pcs-wbs-bigdata, pcs-hld, pcs-arch-6r, pcs-arch-selection, pcs-lz-estimate, pcs-lz-discovery, pcs-compliance-check, pcs-risk-assessment, pcs-risk-register, pcs-cost-optimization, pcs-meeting-minutes |
| **版本** | 2026-10-29.001 |

来源：AICC 平台售前相关能力（`backend/app/ai/skills/builtin.py` 的 22 个内置 skill 中售前向的
17 个）+ 1 个本编排 skill，构成 PCS（售前咨询）在 axon 平台的完整售前技能域。
对齐 PCS 全周期流程（`/workspace/.claude/skills/pcs-full-cycle/`）的售前阶段：
**刊例/报价 → SOW 确认 → 合同确认**（交付执行阶段属其他域）。

## 决策树（正文）

```
START
 └─ 项目是否已有 Fact Sheet？
     ├─ 否 → 调用 pcs-factsheet
     │        ├─ 升级（必填信息缺失）→ 本 skill 升级退出，原因="pcs-factsheet 升级，缺少项目基础信息"
     │        └─ 成功 → 继续
     └─ 是 → 直接使用已有 Fact Sheet，继续

 目标云是否已定？
     ├─ 否（仍在多云比选阶段） → 调用 pcs-arch-selection（多云选型/POC 规划）
     │                          → 完成后回到"目标云是否已定"重新判断
     └─ 是 → 继续

 项目是否为 Landing Zone 专项？
     ├─ 是 → pcs-lz-discovery（发现阶段调研问卷，先行）
     │        → pcs-lz-estimate（LZ 人天/成本估算）
     │        → pcs-sow-lz（Landing Zone 专版 SOW；注意不是 pcs-sow）
     └─ 否（通用迁移/大数据迁移） → 继续

 用户需要哪些售前交付物？（可多选，各分支独立）
     ├─ 报价单 → 调用 pcs-quotation
     ├─ SOW → 调用 pcs-sow（LZ 专项已在上一节点走 pcs-sow-lz，不重复）
     ├─ WBS → 按项目类型选 pcs-wbs-std / pcs-wbs-migration / pcs-wbs-bigdata（三者互斥，见各自 description）
     ├─ 架构方案 → pcs-hld（高级架构设计）；若需 6R 迁移策略 → pcs-arch-6r
     ├─ 风险/合规/成本 → pcs-compliance-check / pcs-risk-assessment（安全类）、
     │                   pcs-risk-register（综合项目风险登记册）、pcs-cost-optimization（云成本优化）
     └─ 会议纪要结构化 → pcs-meeting-minutes（独立分支，不依赖 Fact Sheet）

 售前收口（报价/SOW/WBS 三个都已产出的分支时执行）：
     同源一致性自检——
       a) 报价单与 SOW 的工作范围逐条对应（SOW 范围 ⊆ 报价 Workstream 覆盖）；
       b) SOW 交付物清单与 WBS 交付物列一一对应；
       c) WBS 总人天与报价单总人天一致（不一致 = 有人改了其一没改其他）。
     ├─ 全部一致 → END，汇总所有叶子 skill 的结构化 JSON 输出为一份售前交付物清单
     └─ 有不一致 → 列出差异项，suggested_action = "人工确认以哪份为准后修正重跑对应分支"
```

## 判断逻辑补充

- 各分支之间除标注"互斥"的以外，可并行调用（如报价单与 SOW 可同时进行，都依赖同一份 Fact Sheet）。
- 任一叶子 skill 返回其自身的"升级"结果时，视为该分支的合法终点（不是本编排的错误），
  本 skill 记录该分支状态为"已升级，等待人工介入"，**不阻塞其他独立分支继续执行**。
- 同源一致性自检只做"交叉比对与差异报告"，不擅自修改任何一份已产出的交付物。

## 输出双形态

结构化 JSON：
```json
{
  "conclusion": "PCS 售前流程执行完毕，N 个分支成功，M 个分支升级待人工介入",
  "confidence": "取决于各叶子 skill 的平均 confidence",
  "suggested_action": "...",
  "escalation_reason": null,
  "branches": [
    {"skill": "pcs-factsheet", "status": "success|escalated", "step": "...", "output_ref": "..."}
  ],
  "consistency_check": {"checked": true, "diffs": []}
}
```
人类可读：按分支罗列各叶子 skill 的人类可读产出链接/摘要 + 一致性自检结果表。

## 自身升级出口

- **触发条件**：任一处于决策树关键路径（即其他分支依赖其输出）的叶子 skill 升级且无备选路径——
  典型如 `pcs-factsheet` 升级（后续几乎所有分支都依赖 Fact Sheet）。
- **升级打包**（必须记录完整链路）：
  - 哪个叶子 skill：如 `pcs-factsheet`；
  - 在哪一步：决策树的具体节点（如"项目是否已有 Fact Sheet"分支的"否"路径）；
  - 当时状态：该叶子 skill 升级时打包的"已排除/剩余假设/建议先看哪里"原样向上传递；
  - 本编排层补充：哪些独立分支（不依赖该叶子）仍然正常完成，避免人工误以为整个流程全部失败。
