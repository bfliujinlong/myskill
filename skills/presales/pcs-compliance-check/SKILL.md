---
name: pcs-compliance-check
---

# 安全合规自评检查（pcs-compliance-check）

| 字段 | 值 |
|---|---|
| **description** | 云架构安全合规自评 - 触发条件：目标云与合规标准清单已知，需要按等保2.0/SOC2/ISO27001/GDPR 等条款产出合规自评表时触发；完成判据：控制项清单（编号/描述/当前状态/差距/整改建议/责任人建议）+ compliance_score + critical_gaps 均产出。本 skill 只做自评，不做实际合规整改（整改执行超出边界，需人工/另行变更流程）。 |
| **风险等级** | 只读 |
| **输入参数** | 必填：`target_cloud`/`compliance_standards`；选填：`business_systems`/`data_sensitivity` |
| **依赖工具** | aicc.execute_skill |
| **版本** | 2026-10-29.001 |

对应 AICC 后端内置能力 `Security-Compliance-Check`。

## 触发条件 / 完成判据

触发：`target_cloud`/`compliance_standards` 已知。完成：按标准条款的控制项清单（控制项编号/描述/
当前状态：合规/部分合规/不合规/差距描述/整改建议/责任人建议）+ compliance_score + critical_gaps。

## 判断逻辑（正文）

1. 输入检查：`target_cloud`/`compliance_standards` 缺失 → 交互模式反问；无头模式终止并升级
   （合规标准不能替用户假设，等保 2.0 与 GDPR 的条款完全不同）。
2. 调用 `aicc.execute_skill("Security-Compliance-Check", {target_cloud, compliance_standards, business_systems, data_sensitivity})`。
3. `llm_used=false` → confidence 低，**此类 skill 的降级结果尤其不可直接交付**：合规自评涉及
   客户合规风险，mock 数据可能产出错误的"合规"判定，`suggested_action` 必须强制包含
   "本次结果仅为降级模板，合规状态列必须由安全合规专家人工复核后才能对外输出"。

## 输出双形态

结构化 JSON：`{conclusion, confidence, suggested_action, escalation_reason, controls, compliance_score, critical_gaps}`。
人类可读：AICC 后端生成的 DOCX。

## 升级契约

触发：`target_cloud`/`compliance_standards` 缺失且无法反问；工具不可达；`llm_used=false`
（降级结果因合规风险，必须升级而非直接采用——这是本 skill 与多数"低风险写"skill 不同的、更严格的升级门槛）。
打包：已排除（无真实 LLM 校验）、剩余假设（哪些条款状态是模板默认"部分合规"）、
建议先看 critical_gaps 列表，逐条由合规专家确认。
