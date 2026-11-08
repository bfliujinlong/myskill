---
name: pcs-sow-lz
---

# Landing Zone SOW 生成（pcs-sow-lz）

| 字段 | 值 |
|---|---|
| **description** | Landing Zone 项目工作说明书生成 - 触发条件：已有 LZ 项目的 Fact Sheet，需要产出 LZ 专属 SOW（范围/交付物/假设/里程碑/责任/验收等 14 章）时触发；完成判据：14 章节+scope+deliverables+assumptions+risks+timeline+team 均产出。专用于 Landing Zone 项目；通用迁移项目 SOW 用 `pcs-sow`，两者互斥（按项目是否为 LZ 专项区分）。 |
| **风险等级** | 低风险写 |
| **输入参数** | `facts`（Fact Sheet 结构化对象，必填） |
| **依赖工具** | aicc.execute_skill |
| **版本** | 2026-10-29.001 |

对应 AICC 后端内置能力 `LZ-SOW`。

## 触发条件 / 完成判据

触发：`facts` 已就位且项目为 Landing Zone 专项。完成：14 章节（项目背景/范围/交付物/假设与前提/
工作说明/里程碑/双方责任/变更管理/验收标准/付款条款/知识产权/保密/违约/其它）+ scope/deliverables/
assumptions/risks/timeline/team 结构化字段均产出。

## 判断逻辑（正文）

1. 输入检查：`facts` 缺失 → 交互模式反问；无头模式查上游 Fact Sheet 产出，仍无则终止并升级。
2. 调用 `aicc.execute_skill("LZ-SOW", {"facts": facts})`。
3. `llm_used=false` → confidence 低，提示人工改写验收标准章节（LZ 项目的验收标准通常是具体的
   账号/网络/安全基线检查项，mock 容易产出过于笼统的验收描述）。

## 输出双形态

结构化 JSON：`{conclusion, confidence, suggested_action, escalation_reason, chapters, scope, deliverables, assumptions, risks, timeline, team}`。
人类可读：AICC 后端生成的 DOCX。

## 升级契约

触发：`facts` 缺失且无法反问；工具不可达。
打包：已排除（是否已确认项目为 LZ 专项而非通用迁移）、剩余假设（哪些章节是模板占位）、
建议先看验收标准章节。
