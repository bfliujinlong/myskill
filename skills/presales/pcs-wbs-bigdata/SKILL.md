---
name: pcs-wbs-bigdata
---

# 大数据迁移 WBS 生成（pcs-wbs-bigdata）

| 字段 | 值 |
|---|---|
| **description** | 大数据平台迁移 WBS 生成 - 触发条件：迁移对象明确是大数据组件（MaxCompute/Hive/Spark/DataWorks 等），已知目标大数据平台，需要产出覆盖"评估→集群准备→元数据迁移→数据迁移→任务迁移→调度迁移→校验对账→试运行切换"八阶段 WBS 时触发；完成判据：八阶段 Phase 列表 + 总工期 + 关键风险。与 `pcs-wbs-migration`（通用 VM/数据库迁移，无大数据组件清单输入）互斥。 |
| **风险等级** | 低风险写 |
| **输入参数** | 必填：`target_platform`；选填：`data_volume_tb`/`task_count`/`source_platform`/`components` |
| **依赖工具** | aicc.execute_skill |
| **版本** | 2026-10-29.001 |

对应 AICC 后端内置能力 `BigData-Migration-WBS`。

## 触发条件 / 完成判据

触发：`target_platform` 已知且迁移对象明确含大数据组件。完成：八阶段（大数据评估/集群准备/元数据迁移/
数据迁移/任务迁移/调度迁移/数据校验与对账/试运行与切换）Phase 列表 + total_days + key_risks。

## 判断逻辑（正文）

1. 输入检查：`target_platform` 缺失 → 交互模式反问；无头模式若上下文明确是大数据项目但平台未定，
   **终止并升级**（平台选型本身是前置决策，不能替用户假设）。
2. 调用 `aicc.execute_skill("BigData-Migration-WBS", {data_volume_tb, task_count, source_platform, target_platform, components})`。
3. `llm_used=false` → confidence 低，提示人工核对"任务迁移"阶段（跨平台 SQL/作业语义转换通常低估工时）。

## 输出双形态

结构化 JSON：`{conclusion, confidence, suggested_action, escalation_reason, phases, total_days, key_risks}`。
人类可读：AICC 后端生成的 DOCX。

## 升级契约

触发：`target_platform` 缺失且无法反问；工具不可达。
打包：已排除（是否已确认迁移对象含大数据组件）、剩余假设（components 缺失时按常见组件集默认估算）、
建议先看任务迁移与调度迁移两个阶段的工时。
