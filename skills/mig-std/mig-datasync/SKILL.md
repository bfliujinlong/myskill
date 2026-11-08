---
name: mig-datasync
---

# 数据同步方案设计（mig-datasync）

| 字段 | 值 |
|---|---|
| **description** | 数据同步方案设计 - 触发条件：数据库类型/数量与目标端已知，需要产出全量同步策略/增量同步策略/数据一致性校验/回滚方案时触发；完成判据：四项均产出，并给出风险点和性能预期。专注数据库/对象存储层面的同步方案，不覆盖应用迁移策略（见 `mig-architecture` 的 `app_migration`）。 |
| **风险等级** | 低风险写（方案文档，不触达真实数据库；实际同步任务配置属于另行的运维变更，不在本 skill 边界内） |
| **输入参数** | 必填：`db_types`/`target`；选填：`data_volume_tb`/`source`/`downtime_window` |
| **依赖工具** | aicc.execute_skill |
| **版本** | 2026-10-28.001 |

对应 AICC 后端内置能力 `Migration-DataSync`。

## 触发条件 / 完成判据

触发：`db_types`/`target` 已知。完成：全量同步策略（停机/不停机）、增量同步策略（DTS/OGG/原生工具）、
数据一致性校验方案、回滚方案均产出，并给出风险点与性能预期。

## 判断逻辑（正文）

1. 输入检查：`db_types`/`target` 缺失 → 交互模式反问；无头模式终止并升级（数据库类型未知时无法
   判断同步工具选型，不能靠猜测）。
2. 调用 `aicc.execute_skill("Migration-DataSync", {db_types, data_volume_tb, source, target, downtime_window})`。
3. `llm_used=false` → confidence 低，提示人工核对增量同步工具选型是否与实际数据库引擎兼容
   （DTS/OGG 对不同引擎支持程度不同，mock 容易选错）。

## 输出双形态

结构化 JSON：`{conclusion, confidence, suggested_action, escalation_reason, full_sync_strategy, incremental_sync, consistency_check, rollback_plan, risks}`。
人类可读：AICC 后端生成的 DOCX。

## 升级契约

触发：`db_types`/`target` 缺失且无法反问；工具不可达。
打包：已排除（是否已确认数据库引擎版本）、剩余假设（downtime_window 缺失时默认按不停机方案估算）、
建议先看增量同步工具选型是否兼容实际引擎。
