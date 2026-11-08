---
name: pcs-wbs-std
---

# 通用项目 WBS 生成（pcs-wbs-std）

| 字段 | 值 |
|---|---|
| **description** | 通用项目工作分解结构生成 - 触发条件：已有 Fact Sheet，需要按 Phase 产出通用项目 WBS（角色/工期/依赖/交付物/关键路径）时触发；完成判据：产出 Phase 列表 + 总工期 + 起止日期 + 关键路径。仅用于**通用项目**场景；若项目明确是云迁移类（有 vm_count/database_count 等迁移资源规模），改用 `pcs-wbs-migration`；大数据平台迁移改用 `pcs-wbs-bigdata`。三者互斥，不可同时触发。 |
| **风险等级** | 低风险写 |
| **输入参数** | `facts`（Fact Sheet 结构化对象，必填） |
| **依赖工具** | aicc.execute_skill |
| **版本** | 2026-10-29.001 |

对应 AICC 后端内置能力 `Generate-WBS`。

## 触发条件 / 完成判据

触发：有 Fact Sheet，且项目不属于迁移/大数据迁移专项（否则应路由到 `pcs-wbs-migration`/`pcs-wbs-bigdata`）。
完成：按 Phase 1-N 组织的 task 列表（含 name/duration_days/role/dependencies/deliverable/level），
以及 total_days/start_date/end_date/关键路径标识。

## 判断逻辑（正文）

1. 输入检查：`facts` 缺失 → 交互模式反问，无头模式检查上游 `pcs-factsheet` 是否有输出，否则终止升级。
2. 调用 `aicc.execute_skill("Generate-WBS", {"facts": facts})`。
3. `llm_used=false` → confidence 低，提示人工核对 Phase 划分与工期估算是否贴合实际项目规模。

## 输出双形态

结构化 JSON：`{conclusion, confidence, suggested_action, escalation_reason, phases, total_days, start_date, end_date}`。
人类可读：AICC 后端生成的 DOCX。

## 升级契约

触发：`facts` 缺失且无法反问；工具不可达。
打包：已排除（是否已有 Fact Sheet）、剩余假设（哪些 Phase 工期是模板默认值）、建议先看关键路径上的 task。
