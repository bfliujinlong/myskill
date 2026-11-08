# 云迁移项目报价单

> 人类可读渲染模板。渲染时用 `aicc.execute_skill` 返回的 `outputs`（或本地降级时
> `scripts/ac_mig_pricing.py` 的输出）填充 `{{ }}` 占位符。真实 DOCX 由 AICC 后端
> `document_generator.py` 另行生成，本模板用于 Markdown/聊天场景的即时渲染。

**项目**: {{ project_name }}
**生成时间**: {{ generated_at }}
**数据来源**: {{ "真实 AI 生成" if llm_used else "本地方法论降级（mock/未配置 LLM）" }}
**置信度**: {{ confidence }}

## 报价明细（按 Workstream）

| Workstream | 角色 | 人天 | 日单价 | 小计 |
|---|---|---|---|---|
{{#each workstreams}}{{#each lines}}| {{../name}} | {{role}} | {{person_days}} | ¥{{daily_rate}} | ¥{{subtotal}} |
{{/each}}{{/each}}

## 汇总

- 总人天: **{{ total_person_days }}**
- 原始小计（未计风险溢价）: ¥{{ raw_subtotal }}
- 风险溢价系数: {{ risk_premium }}
- **总金额: ¥{{ total_amount }} {{ currency }}**

## 备注

{{#each notes}}- {{this}}
{{/each}}

## 结论（结构化 JSON 对照）

- conclusion: {{ conclusion }}
- confidence: {{ confidence }}
- suggested_action: {{ suggested_action }}
- escalation_reason: {{ escalation_reason or "无，正常产出" }}
