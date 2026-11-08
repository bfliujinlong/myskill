---
name: mig-startup-orch
description: 云迁移项目启动阶段编排。触发条件：需要端到端走完 项目立项→资源评估→报价/SOW，或上游产物已完成需决定下一个调用谁。能力边界：只做阶段路由、产物流转与升级汇聚，不直接采集云资源、不生成报告正文、不计算价格；具体工作交给叶子 skill。
风险等级: 只读
输入参数: 项目的源材料（背景材料/系统清单/只读凭据/期望产出），可选指定起始阶段
依赖工具: []
版本: 2026-10-27.001
编排: [mig-project-intake, mig-resource-assessment, mig-quotation, mig-sow-generator]

**叶子身份说明**：`mig-cloud-adapter` **不是**本编排的直接叶子。它是 `mig-resource-assessment` 内部调用的采集能力层，无结构化 JSON 输出、无置信度/授权/工具触发、不参与 `chain`。本编排不直接调度它，也不把它列为升级来源——采集能力的问题一律由 `mig-resource-assessment` 收敛后再升级到本编排。
---

# mig-startup-orch

项目启动阶段的**唯一路由入口**。本身不产出业务内容，只决定调用哪个叶子 skill、校验上游产物是否满足下游入参、汇聚叶子升级。

## 决策树

```
入口：拿到项目材料与期望产出
  │
  ├─ 期望产出 = 报价单/人天明细？
  │    └─ 有资源规模数据？ ── 否 ─→ mig-resource-assessment
  │                        └─ 是 ─→ mig-quotation（RTO/RPO 未确认时标注\"预报价\"，见阶段表）
  │
  ├─ 期望产出 = SOW？
  │    └─ 有项目信息 + 资源评估？ ── 是 ─→ mig-sow-generator
  │                              └─ 否 ─→ 只缺项目信息表 → mig-project-intake
  │                                        只缺资源评估 → mig-resource-assessment
  │                                        两者都缺 → 先 mig-project-intake，完成后再 mig-resource-assessment（顺序固定，不得颠倒）
  │
  ├─ 期望产出 = 项目信息表？
  │    └─ mig-project-intake
  │
  └─ 未明确期望产出 ─→ mig-project-intake（先立项，再按上表继续）
```

**阶段顺序**（不满足前序产物不得跳步）：

| 阶段 | 叶子 skill | 产物 | 下游入参校验 |
| --- | --- | --- | --- |
| 1 | `mig-project-intake` | 项目信息表 | 必填齐备或进待确认，缺失项须有"待确认"标记 |
| 2 | `mig-resource-assessment` | 资源评估报告 | 需要只读凭据；无凭据则先走降级或升级 |
| 3a | `mig-quotation` | 报价单 + 人天明细 | 入参需资源规模；RTO/RPO 未确认只能出"预报价" |
| 3b | `mig-sow-generator` | SOW docx（14 章） | 入参需项目信息 + 资源评估，缺一即断链 |

3a 与 3b 并列，可并行；都依赖阶段 2 产物。

## 叶子升级处理（可捕获分支）

叶子 skill 升级时**不终止整条流水线**，按下表选路：

| 升级来源 | 备选路径 | 无备选时本编排的出口 |
| --- | --- | --- |
| `mig-project-intake` 缺材料 | 交互模式向人提问补全；无头模式降级为"待确认清单"，且**仅当**缺失项不影响 assessment 入参（系统清单仍可用）时才继续 | 升级给人：输出已完成阶段产物 + 链路升级包，**不继续调 assessment**（系统清单缺失时 assessment 无必需入参，不可执行） |
| `mig-resource-assessment` 覆盖率 < 80% | 按清单估算，标注"未采集" | 升级给人（附差异项） |
| `mig-quotation` 校验不通过 | 调整 WBS 重算 | 升级给人（附测算明细与不符项） |
| `mig-sow-generator` 模板缺失 | 无 | 升级给人（构成断链） |

**置信度阈值**：任意叶子 `confidence < 0.6` 或累计降级扣分使链路置信度 < 0.6 → 整链升级，不交付终版产物，只交付已完成的中间产物 + 升级包。

**出口规则**：叶子升级且上表无备选路径时，本编排自身升级，出口产物为「已完成阶段的产物 + 链路升级包」，不得静默跳过该阶段继续往下走。

## 输入缺失处理

| 缺失项 | 交互模式 | 无头模式 |
| --- | --- | --- |
| 背景材料 | 向人提问，或按已有材料降级立项 | 降级为"待确认清单"，标注来源缺失 |
| 系统清单 | 向人提问索要 | **终止本阶段并升级**（assessment 无入参，不可执行） |
| 只读凭据 | 向人提问，或降级为人工提供采集结果 | 降级为人工提供采集结果，置信度 -0.2 |
| 期望产出 | 向人确认 | 默认走 `mig-project-intake` 立项，再按决策树继续 |

## 自身升级契约

**触发**：
- **置信度 < 0.6**：任意叶子升级扣除后链路置信度低于 0.6 → 整链升级，不交付终版产物
- **风险等级与授权不匹配**：链路中任一环节要求调用 create/update/delete 类云 API，超出本编排与叶子 skill 的 `风险等级`（只读）与租户授权范围 → 立即终止并升级
- **工具不可用**：叶子依赖的脚本缺失或执行失败且无备选路径（如 `mig-sow-generator` 的 `templates/SOW模板.md` 缺失）→ 升级
- 叶子升级且备选路径表中无可用备选
- 阻塞材料（系统清单）缺失且无法补全

**出口产物**：已完成阶段的产物 + 链路升级包（三件套：`已排除什么` / `剩余假设` / `建议先看哪`），不静默跳过阶段继续往下走。

## 输出

结构化 JSON（管线消费）：

```json
{
  "skill": "mig-startup-orch",
  "conclusion": "",
  "confidence": 0.0,
  "stages_completed": [],
  "current_stage": "",
  "next_skill": "",
  "artifacts": {},
  "suggested_actions": [],
  "escalation": {
    "required": false,
    "reason": "",
    "ruled_out": [],
    "remaining_hypotheses": [],
    "first_checks": [],
    "chain": {
      "leaf_skill": "",
      "step": "",
      "state_at_escalation": ""
    }
  }
}
```

## 升级包链路（必填）

叶子升级时，`chain` 三段必须填满，不得留空：

- `leaf_skill`：哪个叶子 skill 升级的
- `step`：走到该 skill 的哪一步（对应其正文步骤编号或名称）
- `state_at_escalation`：当时的状态（已完成的阶段、已拿到的产物、置信度、降级项）

人类可读形态：按 `templates/orch-progress.md` 渲染阶段进展表 + 降级升级记录 + 升级包，供人阅读与推送飞书。JSON 是唯一数据源，模板是其投影，不反向读取。

## 不做

- 不直接调云 MCP 采集资源（属 `mig-cloud-adapter`）
- 不写评估报告、SOW 正文、报价明细（属对应叶子 skill）
- 不嵌套调用另一个编排 skill
- 不在叶子升级且无备选路径时自行继续后续阶段
