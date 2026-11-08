---
name: pcs-risk-assessment
---

# 安全风险评估（pcs-risk-assessment）

| 字段 | 值 |
|---|---|
| **description** | 云架构安全风险评估 - 触发条件：已有架构摘要（文本描述），需要识别安全风险并给出风险等级与缓解措施时触发；完成判据：风险登记册（编号/描述/等级/影响范围/缓解措施/责任人）产出。专注**安全**风险；项目管理类综合风险（进度/成本/人员等）用 `pcs-risk-register`，两者互斥。 |
| **风险等级** | 只读 |
| **输入参数** | `architecture`（架构摘要文本，必填） |
| **依赖工具** | aicc.execute_skill |
| **版本** | 2026-10-29.001 |

对应 AICC 后端内置能力 `Security-Risk-Assessment`。

## 触发条件 / 完成判据

触发：`architecture` 非空。完成：风险登记册，每条含风险编号/描述/风险等级（高/中/低）/影响范围/
缓解措施/责任人。

## 判断逻辑（正文）

1. 输入检查：`architecture` 缺失 → 交互模式请用户提供架构摘要（可取自 `pcs-hld`/`lz-hld` 输出）；
   无头模式若上游有 HLD 产出直接取用，否则终止并升级。
2. 调用 `aicc.execute_skill("Security-Risk-Assessment", {"architecture": architecture})`。
3. `llm_used=false` → confidence 低，`suggested_action` 必须包含"高等级风险条目需安全专家人工复核"
   （同 `pcs-compliance-check`，安全类评估的降级结果门槛更高）。

## 输出双形态

结构化 JSON：`{conclusion, confidence, suggested_action, escalation_reason, risks, risk_summary}`。
人类可读：AICC 后端生成的 DOCX。

## 升级契约

触发：`architecture` 缺失且无法反问；工具不可达；`llm_used=false` 且存在"高"等级风险条目
（高风险判定不能仅靠 mock，必须升级人工确认）。
打包：已排除（无真实 LLM 校验）、剩余假设（哪些风险等级是模板默认值）、
建议先看等级为"高"的风险条目。
