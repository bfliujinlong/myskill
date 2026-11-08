---
name: pcs-wbs-migration
---

# 迁移项目 WBS 生成（pcs-wbs-migration）

| 字段 | 值 |
|---|---|
| **description** | 迁移项目工作分解结构生成 - 触发条件：已知迁移资源规模（vm_count/database_count/数据量）且目标云明确，需要产出覆盖"评估设计→LZ准备→数据迁移→应用迁移→切割切换→验证运维交接"六阶段的 WBS 时触发；完成判据：六阶段 task 列表 + 总工期 + 关键路径。与 `pcs-wbs-std`（通用项目，无迁移资源规模输入）互斥；与 `pcs-wbs-bigdata`（大数据平台专项）互斥。 |
| **风险等级** | 低风险写 |
| **输入参数** | 必填：`vm_count`/`target_cloud`；选填：`database_count`/`current_cloud`/`data_volume_tb` |
| **依赖工具** | aicc.execute_skill |
| **版本** | 2026-10-29.001 |

对应 AICC 后端内置能力 `Migration-WBS`。

## 触发条件 / 完成判据

触发：`vm_count` 与 `target_cloud` 已知。完成：六阶段 Phase（评估与设计/Landing Zone 准备/数据迁移/
应用迁移/切割切换/验证与运维交接）均有 task 列表，含 duration_days/role/dependencies/deliverable。

## 判断逻辑（正文）

1. 输入检查：`vm_count`/`target_cloud` 缺失一项即无法估算 → 交互模式反问；无头模式查上游 `pcs-factsheet`
   输出里的 `infrastructure`/`architecture` 段是否含这两项，否则终止升级。
2. 调用 `aicc.execute_skill("Migration-WBS", {vm_count, database_count, current_cloud, target_cloud, data_volume_tb})`。
3. `llm_used=false` → confidence 低，提示人工核对六阶段的人天分配是否匹配实际资源量级。

## 输出双形态

结构化 JSON：`{conclusion, confidence, suggested_action, escalation_reason, phases, total_days, critical_path}`。
人类可读：AICC 后端生成的 DOCX。

## 升级契约

触发：`vm_count`/`target_cloud` 缺失且无法反问；工具不可达。
打包：已排除（是否查过 pcs-factsheet 输出）、剩余假设（data_volume_tb 缺失时按 Phase 3 工期取默认值）、
建议先看切割切换阶段（通常是关键路径瓶颈）。
