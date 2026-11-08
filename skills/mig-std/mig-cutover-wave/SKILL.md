---
name: mig-cutover-wave
---

# 切换波次计划生成（资源清单级，mig-cutover-wave）

| 字段 | 值 |
|---|---|
| **description** | 基于具体资源清单的切换波次计划生成 - 触发条件：迁移资源已细化为**具体清单**（VM/数据库实例等资源列表 `resources`），需要按业务依赖关系产出分波次切换步骤/检查清单/回滚方案时触发；完成判据：3-5 波划分+每波步骤+检查清单（含数据库一致性/应用探活/DNS 切换）+回滚方案+风险点。与 `mig-cutover-plan` 互斥：范围仍是叙述性描述、未细化到资源清单时改用 `mig-cutover-plan`。 |
| **风险等级** | 低风险写（本 skill 仅产出计划文档，实际切换执行不在边界内，执行属于高危变更，需人工在计划基础上另行操作） |
| **输入参数** | 必填：`resources`（迁移资源清单）/`target_cloud`；选填：`cutover_window` |
| **依赖工具** | aicc.execute_skill |
| **版本** | 2026-10-28.001 |

对应 AICC 后端内置能力 `Migration-Cutover`。

## 触发条件 / 完成判据

触发：`resources`（具体资源清单）/`target_cloud` 已知。完成：3-5 波划分（按业务依赖关系）、
每波 pre-cutover/cutover/post-cutover 步骤、检查清单、回滚方案（每波都要有）、风险点与应急联系人。

## 判断逻辑（正文）

1. 输入检查：`resources`/`target_cloud` 缺失 → 交互模式反问；无头模式终止并升级。
2. 调用 `aicc.execute_skill("Migration-Cutover", {resources, target_cloud, cutover_window})`。
3. `llm_used=false` → confidence 低，提示人工核对检查清单是否覆盖数据库一致性校验和 DNS 切换这两项
   高风险点（mock 容易遗漏）。
4. **边界强调**：本 skill 产出的是计划，不执行实际切换操作；若用户要求"直接执行切换"，
   应升级为人工确认后再操作，不在本 skill 内自动化执行。

## 输出双形态

结构化 JSON：`{conclusion, confidence, suggested_action, escalation_reason, waves, checklist, rollback_plan, risk_points}`。
人类可读：AICC 后端生成的 DOCX。

## 升级契约

触发：`resources`/`target_cloud` 缺失且无法反问；工具不可达；用户要求本 skill 直接执行切换
（超出本 skill 的"只产出计划"边界）。
打包：已排除（是否已确认 resources 是具体清单而非叙述）、剩余假设（哪些资源缺少依赖关系信息，
波次划分靠经验估算）、建议先看回滚方案是否每波齐全。
