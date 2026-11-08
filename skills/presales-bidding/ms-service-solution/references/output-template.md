# 服务方案

> 本文是服务方案工作稿。SLA 数字均引用 Company KB 权威值或标记"待商务/交付确认"，本文不自造 SLA 数字。
> 服务范围与应标策略取舍一致，不擅自扩大。治理频率与 RFP 强制要求保持一致（月度不改季度）。

---

## 1. 基本信息

| 字段 | 内容 |
|------|------|
| 客户名称 | {{customer_name}} |
| 机会 | {{opportunity_name}} |
| 服务类型 | {{engagement_type}} |
| 日期 | {{date}} |
| 策略来源 | {{strategy_ref}} |

---

## 2. 方案概述与应标策略（赢单主线 · 步骤 0.52 内化）

- 方案概述：{{overview}}

**2.1 Win Theme（赢单主线一句话）**：{{win_theme}}
> 基于机会事实与判断，独立成立，不照抄 RFP 条目。

**2.2 差异化**：{{differentiator}}
> 主张 + 依据 + 性质（能力事实 / 方案建议）。

**2.3 关键取舍**：做什么 → {{do_scope}}；本次不做·暂不覆盖 → {{not_do_scope}}
> "本次不做"直接作为 §3.1 Confirmed In-Scope 锁定依据——策略取舍与范围锚定必须一致。

**2.4 显式假设**：{{assumption_1}}
> 全部标"假设，待验证"。

**2.5 不承诺项清单**：{{non_commitment_1}}
> 本阶段明确不作出的承诺（具体 SLA 数字 / 固定价格 / 交付工期 / 退出机制等）逐条列出；退出机制只写建议或待确认，不写"已明确"。

---

## 3. 服务设计（五段强制拆分）

**3.1 Confirmed In Scope（已确认服务范围）：**
- {{in_scope_1}}

**3.2 Confirmed Out of Scope（已确认排除 — 仅放客户/策略/合同明确排除的服务项）：**
- {{out_scope_1}}

> 仅放有明确来源的排除项（如安全托管、应用代码维护有客户或策略明确排除记录）。**资质、客户案例不属于此栏**（见 3.3）。

**3.3 Candidate Exclusion（候选排除项 — 待内部及客户确认）：**
- 非标准变更：{{nonstd_change}}（候选排除项，待内部及客户确认）
- 高风险变更：{{highrisk_change}}（候选排除项，待内部及客户确认）
- 架构变更：{{arch_change}}（候选排除项，待内部及客户确认）

> 以上为候选排除项，未获得客户或合同明确排除确认。**不得**将 Candidate Exclusion 升级为 Confirmed Out of Scope。
> 只有客户或合同明确排除时，才能将对应项移至 3.2 Confirmed Out of Scope。

**3.4 应标证据待补充：**
- 资质证明：{{qualification_evidence}}（待补充）
- 客户案例：{{case_evidence}}（待补充）

> 资质与案例是应标证据待补充项，不得写入 Confirmed Out of Scope 或 Candidate Exclusion。

**3.5 候选设计 / 待确认：**
- 监控平台：{{monitoring_platform}}（候选，待确认）
- Agent 部署：{{agent_deploy}}（候选，待确认）
- 并行验证：{{parallel_validation}}（候选，待确认）

> 未确认项一律标"候选，待确认"，不得写成已定范围。

**3.6 SLA 与授权缺口：**
- {{sla_gap_1}}
- 授权缺口：{{authority_gap_1}}

---
## 3b. 合同义务状态声明

| 要求 | RFP 状态 | 方案状态 | 合同状态 | 说明 |
|------|----------|----------|----------|------|
| {{req_1}} | mandatory_in_rfp | proposed_solution | pending | 是否纳入最终合同及具体条款待确认 |

> **合同状态取值**：`pending`（默认，无合同输入）/ `candidate_contract_term`（候选）/ `confirmed_contractual`（有确认记录）/ `signed_contractual`（已签署）。
> **禁止**：无合同输入时不得写 confirmed_contractual 或 signed_contractual。
> **一致性检查**：全篇同一要求不得出现 RFP/合同状态冲突。

---

## 4. 责任模型（RACI 框架）

| 活动 | 安畅 | 客户 | 说明 |
|------|------|------|------|
| {{activity_1}} | {{raci_a_1}} | {{raci_c_1}} | {{raci_note_1}} |

> 无来源 Owner 写"相关内部责任方待确认"，不指定客户成功/交付/商务等部门。

---

## 5. 服务运营与治理

> 频率必须与 RFP 强制要求一致。RFP 要求月度报告/月度回顾时，本节保持**月度**。

- 服务报告频率：**月度**（与 RFP 一致）
- 服务回顾会议频率：**月度**（与 RFP 一致）
- {{governance_1}}
- 额外候选：{{quarterly_optional}}（如建议季度治理，仅为额外候选机制，不替代月度要求）

---

## 6. SLA 引用（不自造数字）

| 指标 | 值 | 来源 |
|------|-----|------|
| {{sla_metric_1}} | {{sla_value_1}} | {{sla_source_1}} |

> 每个 SLA 值必须注明来源：`Company KB <条目>` 或 `待商务/交付确认`。禁止本文编造数字。

---

## 7. 接管（Mobilization）与服务接管

- {{mobilization_1}}

---

## 8. 持续改进

> 仅当输入明确要求 AI / AIOps / 智能运维时，才可在此展开相关主题；否则不主动加入 AI 章节。

- {{improvement_1}}

---

## 9. 假设与依赖

- 假设：{{assumption_1}}
- 客户依赖：{{dependency_1}}

---

## 10. 来源与使用边界

- 来源：应标策略{{rfp_ref_line}}
- 使用边界：
  - SLA 数字不由本文承诺；
  - 只使用显式能力输入，不自动读取/推断 Company KB；
  - 不写入报价/SOW 目录；
  - 不写入 Company KB。
