---
name: pcs-arch-selection
---

# 售前多云架构选型（pcs-arch-selection）

| 字段 | 值 |
|---|---|
| **description** | 售前多云架构选型与 POC 规划 - 触发条件：**目标云尚未选定**，客户在阿里云/华为云/腾讯云/AWS/Azure 之间比选，需要多云技术选型对比表+POC 验证计划+架构草案时触发；完成判据：架构概述+网络+安全+高可用灾备+多云选型对比表+POC 计划+风险成本均产出。目标云一旦选定，后续设计改用 `pcs-hld`（单云 HLD）和 `pcs-arch-6r`（6R 迁移策略），本 skill 不再适用——这是本 skill 与两者的互斥边界。 |
| **风险等级** | 低风险写 |
| **输入参数** | 必填：`project_type`/`target_cloud`（即便是比选阶段，`target_cloud` 也需填候选云之一或"多云对比"标记）；选填：`current_cloud`/`vm_count`/`database_count`/`region_count`/`account_count`/`security_level` |
| **依赖工具** | aicc.execute_skill |
| **版本** | 2026-10-29.001 |

对应 AICC 后端内置能力 `PreSales-Architect`。

## 触发条件 / 完成判据

触发：处于售前比选阶段，`project_type` 已知。完成：架构概述与设计原则、网络架构、安全与合规架构、
高可用与灾备方案、多云技术选型对比表（功能/价格/迁移成本差异）、POC 验证计划（目标/范围/成功标准）、
预估架构风险与成本，七项均产出。

## 判断逻辑（正文）

1. 输入检查：`project_type`/`target_cloud` 缺失 → 交互模式反问；无头模式终止并升级。
2. 调用 `aicc.execute_skill("PreSales-Architect", {project_type, current_cloud, target_cloud, vm_count, database_count, region_count, account_count, security_level})`。
3. `llm_used=false` → confidence 低，提示人工核对多云选型对比表的价格差异数据（mock 容易用过时/
   虚构的刊例价，必须对照 `/workspace/pcs-presales` 等真实报价刊例人工核实）。

## 输出双形态

结构化 JSON：`{conclusion, confidence, suggested_action, escalation_reason, overview, network, security, ha_dr, tech_comparison, poc_plan, risks}`。
人类可读：AICC 后端生成的 DOCX。

## 升级契约

触发：`project_type`/`target_cloud` 缺失且无法反问；工具不可达。
打包：已排除（是否已确认客户仍处于比选阶段）、剩余假设（哪些云厂商的价格数据是 mock 非真实刊例）、
建议先看 tech_comparison 表里的价格列。
