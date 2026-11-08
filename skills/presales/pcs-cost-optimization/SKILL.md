---
name: pcs-cost-optimization
---

# 云成本优化方案生成（pcs-cost-optimization）

| 字段 | 值 |
|---|---|
| **description** | 云成本优化方案生成 - 触发条件：目标云已知，且有月度云支出或资源利用率数据，需要识别闲置/超配资源并给出预留实例/存储优化/弹性方案时触发；完成判据：当前成本分析+优化机会识别表+短期优化(1-30天)+中长期优化(1-6月)+预估节省+ROI 均产出。本 skill 只产出优化建议，实际执行降配/升配属于高危变更，不在边界内，需人工确认后另行操作。 |
| **风险等级** | 只读（仅分析现状并给建议，不改任何云资源配置） |
| **输入参数** | 必填：`target_cloud`；选填：`vm_count`/`database_count`/`monthly_cost`/`utilization` |
| **依赖工具** | aicc.execute_skill |
| **版本** | 2026-10-29.001 |

对应 AICC 后端内置能力 `Cost-Optimization`。

## 触发条件 / 完成判据

触发：`target_cloud` 已知。完成：当前成本分析（按服务分类）、优化机会识别表（项目/当前成本/
优化后成本/节省比例）、短期优化（闲置清理/存储降配/带宽优化）、中长期优化（预留实例/Savings Plans/
弹性伸缩）、预估总节省金额与 ROI 均产出。

## 判断逻辑（正文）

1. 输入检查：`target_cloud` 缺失 → 交互模式反问；无头模式终止并升级。
2. 调用 `aicc.execute_skill("Cost-Optimization", {target_cloud, vm_count, database_count, monthly_cost, utilization})`。
3. `llm_used=false` → confidence 低，提示人工核对 `monthly_cost`/`utilization` 缺失时的节省估算
   是否仅为模板占位（没有真实用量数据，ROI 数字不可直接采信）。
4. **边界强调**：输出是建议，不是执行指令；若用户要求"直接执行降配"，需升级为人工确认后操作。

## 输出双形态

结构化 JSON：`{conclusion, confidence, suggested_action, escalation_reason, cost_analysis, optimizations, short_term_actions, long_term_actions, estimated_savings, roi}`。
人类可读：AICC 后端生成的 DOCX。

## 升级契约

触发：`target_cloud` 缺失且无法反问；工具不可达；用户要求本 skill 直接执行资源变更（超出"只读分析"边界）。
打包：已排除（无）、剩余假设（monthly_cost/utilization 缺失时 ROI 为估算值非真实数据）、
建议先看 estimated_savings 的计算依据是否基于真实用量。
