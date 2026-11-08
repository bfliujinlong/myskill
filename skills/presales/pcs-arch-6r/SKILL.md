---
name: pcs-arch-6r
---

# 迁移架构方案设计（pcs-arch-6r）

| 字段 | 值 |
|---|---|
| **description** | 迁移架构方案设计 - 触发条件：目标云已定（非多云对比阶段），需要产出 6R 策略划分/迁移工具选型/网络方案/数据迁移方案/应用迁移策略/风险评估时触发；完成判据：六项均产出。与 `pcs-arch-selection`（多云对比+POC，目标云尚未定）互斥；与 `pcs-hld`（账号/网络/安全等基础设施层设计）是互补关系——本 skill 专注"怎么迁"，`pcs-hld` 专注"迁过去落在什么架构上"。 |
| **风险等级** | 低风险写 |
| **输入参数** | `facts`（Fact Sheet 结构化对象，必填，`target_cloud` 必须已确定） |
| **依赖工具** | aicc.execute_skill |
| **版本** | 2026-10-29.001 |

对应 AICC 后端内置能力 `Migration-Architecture`。

## 触发条件 / 完成判据

触发：`facts` 已就位且目标云已定。完成：6R 策略划分（Rehost/Replatform/Refactor/Repurchase/Retain/Retire，
按资源类型分类）、迁移工具选型（SMS/DTS/DMS）、网络方案、数据迁移方案、应用迁移策略、风险评估均产出。

## 判断逻辑（正文）

1. 输入检查：`facts` 缺失或目标云未定 → 交互模式反问；无头模式若目标云未定，路由建议改走
   `pcs-arch-selection`，本 skill 终止并升级。
2. 调用 `aicc.execute_skill("Migration-Architecture", {"facts": facts})`。
3. `llm_used=false` → confidence 低，提示人工核对 6R 分类是否合理（mock 容易把所有资源都归为
   Rehost，实际应按资源类型/改造成本差异化）。

## 输出双形态

结构化 JSON：`{conclusion, confidence, suggested_action, escalation_reason, strategy_6r, tools, network_plan, data_migration, app_migration, risks}`。
人类可读：AICC 后端生成的 DOCX。

## 升级契约

触发：`facts` 缺失或目标云未定且无法反问；工具不可达。
打包：已排除（是否已确认目标云）、剩余假设（6R 分类是否按真实资源类型区分还是统一模板）、
建议先看 6R 策略划分表。
