---
name: pcs-lz-discovery
---

# Landing Zone 发现问题清单生成（pcs-lz-discovery）

| 字段 | 值 |
|---|---|
| **description** | Landing Zone 项目发现阶段问题清单生成 - 触发条件：项目类型与目标云已知，项目仍处于发现/调研前期，需要产出治理/网络/安全/IAM/合规/监控运维六大领域的调研问题清单时触发；完成判据：六领域各 3-5 个问题，每个问题标注 priority 与 purpose。产出的是"要问客户什么"，不是架构设计本身（设计见 `lz-hld`）。 |
| **风险等级** | 只读（仅生成问题清单，不做任何设计决策） |
| **输入参数** | 必填：`project_type`/`target_cloud`；选填：`current_cloud`/`account_count`/`region_count`/`security_level`/`industry` |
| **依赖工具** | aicc.execute_skill |
| **版本** | 2026-10-29.001 |

对应 AICC 后端内置能力 `LZ-Discovery`（输出文档格式 PDF）。

## 触发条件 / 完成判据

触发：`project_type`/`target_cloud` 已知，项目处于发现阶段。完成：六大领域（治理/网络/安全/IAM/合规/
监控运维）各 3-5 个问题，每个问题标注 priority（high/medium/low）和 purpose。

## 判断逻辑（正文）

1. 输入检查：`project_type`/`target_cloud` 缺失 → 交互模式反问；无头模式终止并升级。
2. 调用 `aicc.execute_skill("LZ-Discovery", {project_type, current_cloud, target_cloud, account_count, region_count, security_level, industry})`。
3. `llm_used=false` → confidence 低，提示人工核对合规领域问题是否覆盖客户所在行业的实际合规要求
   （`industry` 缺失时 mock 容易产出通用合规问题，不够精准）。

## 输出双形态

结构化 JSON：`{conclusion, confidence, suggested_action, escalation_reason, categories}`。
人类可读：AICC 后端生成的 PDF。

## 升级契约

触发：`project_type`/`target_cloud` 缺失且无法反问；工具不可达。
打包：已排除（无）、剩余假设（industry 缺失时合规问题按通用模板生成）、建议先看合规领域问题
是否需要按行业改写。
