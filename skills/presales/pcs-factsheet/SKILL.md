---
name: pcs-factsheet
---

# 项目 Fact Sheet 生成（pcs-factsheet）

| 字段 | 值 |
|---|---|
| **description** | 项目 Fact Sheet 生成 - 触发条件：项目刚启动，已拿到客户背景/目标/约束或初步系统清单，需要把这些信息结构化为标准 Fact Sheet（基础设施/安全合规/架构/团队估算/建议）时触发；完成判据：产出含 `summary`/`infrastructure`/`security_compliance`/`architecture`/`team_estimate`/`recommendations` 六段的结构化 Fact Sheet。不负责报价（`pcs-quotation`）、不负责 SOW 章节撰写（`pcs-sow`）——Fact Sheet 是这两者的共同输入。 |
| **风险等级** | 只读（纯信息结构化，不触达任何客户系统，不写任何外部状态） |
| **输入参数** | 必填：`project_type`（项目类型）/`current_cloud`（当前云或 IDC）/`target_cloud`（目标云）；选填：`vm_count`/`database_count`/`region_count`/`account_count`/`vpc_count`/`security_level`/`storage_tb`/`app_count`/`k8s_cluster_count`/`budget_range`/`timeline_months` |
| **依赖工具** | aicc.execute_skill |
| **版本** | 2026-10-29.001 |

对应 AICC 后端内置能力 `Generate-FactSheet`。
对应「云迁移Agent构建计划与排期-V1.xlsx」Skill 清单中的两项（本 skill 合并覆盖两者的输入输出边界）：

- **项目信息收集**（输入=客户背景/目标/约束，输出=项目信息表，模板=项目信息模板）→ 对应本 skill 的输入侧（`project_type`/`current_cloud`/`target_cloud` 等基础信息）；
- **初始资源评估**（输入=系统清单，绑定工具=云资源适配，输出=初始资源评估报告，模板=评估模板）→ 对应本 skill 的输出侧（`infrastructure`/`architecture`/`team_estimate`）。

AICC 当前 22 个内置能力里没有独立的"资源适配/盘点"工具，`vm_count`/`database_count` 等量化字段
依赖用户或 `云资源适配`（支撑层能力，不在本次 axon-skills 范围内）提供；本 skill 不做实时资源盘点。

## 触发条件 / 完成判据

- 触发：项目启动阶段，已获得客户基础信息（哪怕只有 `project_type`/`current_cloud`/`target_cloud` 三项）。
- 完成：六段结构化 Fact Sheet 全部产出，且 `team_estimate` 与量化字段（vm_count 等）的缺失情况有明确说明。

## 判断逻辑（正文）

1. **输入完整性检查**：三个必填字段（`project_type`/`current_cloud`/`target_cloud`）是否齐全。
   - 交互模式：缺失时直接向用户提问（可参考项目信息模板里的标准问法：项目类型/现状云/目标云/行业/合规要求）。
   - 无头模式：不得假设可反问——
     a) 三项全缺：**终止并升级**，无法产出有意义的 Fact Sheet；
     b) 仅缺可选量化字段（vm_count 等）：**降级继续**，调用时该字段传 `null`，在输出 `recommendations`
        里注明"需补充 XX 以提升估算精度"。
2. **调用依赖工具**：`aicc.execute_skill("Generate-FactSheet", {<上述字段>})`。
3. **降级判定**：`llm_used=false` 时，`summary`/`recommendations` 等文本字段为 mock 占位，
   `confidence` 记为低，`suggested_action` 建议"人工按实际客户访谈信息改写 summary/recommendations，
   量化字段（infrastructure 里的数字）若来自用户输入可直接采信"。
4. **输出渲染**：无专属模板（`templates/`），直接用 AICC 后端生成的 DOCX；Markdown 渲染可直接把
   六段按标题罗列输出。

## 输出双形态

**结构化 JSON**（标准包络 + 原始 `output_schema`）：

```json
{
  "conclusion": "Fact Sheet 已生成，关键缺口: ...",
  "confidence": "高 | 低",
  "suggested_action": "可直接用于报价/SOW生成 | 需先补齐量化字段再用于报价",
  "escalation_reason": null,
  "summary": "...",
  "infrastructure": {},
  "security_compliance": ,
  "architecture": {},
  "team_estimate": {},
  "recommendations": []
}
```

**人类可读**：AICC 后端自动生成的 DOCX（`document.download_url`）。

## 升级契约

- **触发条件**：`project_type`/`current_cloud`/`target_cloud` 三项必填信息缺失且无头模式不可反问；
  或 `aicc.execute_skill` 工具不可达。
- **升级打包**：
  - 已排除：是否已尝试从上游对话/表单里提取过这三项（避免重复问客户）；
  - 剩余假设：哪些量化字段完全没有值、Fact Sheet 的哪些段落因此只能是占位文本；
  - 建议先看哪里：直接让人工工程师补齐三项必填信息后重跑。
- **组合语义**：被 `pcs-presales-orch` 调用时是整个售前流程的第一个叶子节点，若在此处升级，
  编排层应直接终止后续分支（报价/SOW/WBS 都依赖本 skill 的输出），不应继续往下走。
