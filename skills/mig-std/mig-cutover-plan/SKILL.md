---
name: mig-cutover-plan
---

# 切换计划生成（通用，mig-cutover-plan）

| 字段 | 值 |
|---|---|
| **description** | 通用切换计划生成 - 触发条件：迁移范围仍以**叙述性描述**（如"3个业务系统，含2个数据库"）表达、尚未细化到具体资源清单，需要先出一份切换波次/步骤/回滚方案的规划稿时触发；完成判据：波次划分+每波步骤+检查清单+回滚方案+风险点。与 `mig-cutover-wave` 互斥：当迁移范围已经是**具体资源清单**（VM 列表/数据库实例列表）时改用 `mig-cutover-wave`，不再用本 skill。 |
| **风险等级** | 低风险写 |
| **输入参数** | 必填：`scope`（迁移范围叙述）/`target_cloud`；选填：`cutover_window`（切换窗口，小时） |
| **依赖工具** | aicc.execute_skill |
| **版本** | 2026-10-28.001 |

对应 AICC 后端内置能力 `Generate-CutoverPlan`。

## 触发条件 / 完成判据

触发：`scope`/`target_cloud` 已知，迁移范围仍是叙述性描述。完成：3-5 波切换划分、每波
pre-cutover/cutover/post-cutover 步骤、检查清单、回滚方案、风险点与应急联系人。

## 判断逻辑（正文）

1. 输入检查：`scope`/`target_cloud` 缺失 → 交互模式反问；无头模式终止并升级。
2. **路由检查**：若用户/上游已经给出具体资源清单（VM 名单/数据库实例清单）而非叙述性描述，
   应改路由到 `mig-cutover-wave`，本 skill 不处理。
3. 调用 `aicc.execute_skill("Generate-CutoverPlan", {scope, target_cloud, cutover_window})`。
4. `llm_used=false` → confidence 低，提示人工核对回滚方案是否每波都有（mock 容易漏掉）。

## 输出双形态

结构化 JSON：`{conclusion, confidence, suggested_action, escalation_reason, waves, checklist, rollback_plan, risk_points}`。
人类可读：AICC 后端生成的 DOCX。

## 升级契约

触发：`scope`/`target_cloud` 缺失且无法反问；工具不可达。
打包：已排除（是否已确认范围仍为叙述性而非清单）、剩余假设（cutover_window 缺失时按默认窗口估算）、
建议先看 rollback_plan 是否每波都齐全。
