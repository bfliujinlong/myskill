---
name: pcs-meeting-minutes
---

# 会议纪要结构化（pcs-meeting-minutes）

| 字段 | 值 |
|---|---|
| **description** | 会议纪要结构化 - 触发条件：已有会议文字稿（转写文本），需要结构化为摘要/决策/行动项/风险/下次议程时触发；完成判据：五段结构化内容全部产出，`action_items` 每条含责任人与 due_date。不负责会议转写本身（ASR/录音转文字不在边界内，需用户或上游工具先产出 `transcript`）。 |
| **风险等级** | 只读（仅结构化已有文字稿，不产生新决策，不触达任何系统） |
| **输入参数** | 必填：`transcript`；选填：`topic`/`time`/`attendees` |
| **依赖工具** | aicc.execute_skill |
| **版本** | 2026-10-29.001 |

对应 AICC 后端内置能力 `Generate-MeetingMinutes`。

## 触发条件 / 完成判据

触发：`transcript` 非空。完成：`summary`（200字内）/`decisions`/`action_items`（含责任人/due_date）/
`risks`/`next_agenda` 五段均产出。

## 判断逻辑（正文）

1. 输入检查：`transcript` 为空 → 交互模式请用户粘贴文字稿；无头模式直接**终止并升级**
   （没有转写文本，任何"结构化"都是编造）。
2. 调用 `aicc.execute_skill("Generate-MeetingMinutes", {topic, time, attendees, transcript})`。
3. `llm_used=false` → confidence 低，`action_items` 的责任人/due_date 字段若 mock 填充的是占位值，
   必须在 suggested_action 里提示"责任人/日期需人工从文字稿原文核对，不可直接采信"。

## 输出双形态

结构化 JSON：`{conclusion, confidence, suggested_action, escalation_reason, summary, decisions, action_items, risks, next_agenda}`。
人类可读：AICC 后端生成的 DOCX。

## 升级契约

触发：`transcript` 为空；工具不可达。
打包：已排除（无）、剩余假设（降级时 action_items 的责任人是否为真实值）、
建议先看 action_items 里责任人字段是否为占位。
