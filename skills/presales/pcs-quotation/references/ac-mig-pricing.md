# AC-MIG 定价方法论

> 迁移自 `/workspace/.claude/skills/aicc-quotation/SKILL.md` 第 24-37 行，`SKILL.md` 正文只链接本文件，不复制内容（遵循 spec 的"事实知识归 references"规则）。

## Workstream 拆分

按以下 6 个 Workstream 拆分报价，缺一不可（即使某个 Workstream 人天为 0 也要列出并注明原因）：

1. Landing Zone
2. 迁移设计
3. 数据迁移
4. 应用迁移
5. 切割切换
6. 运维交接

## 每个 Workstream 内部结构

每个 Workstream 下按角色列出：

| 字段 | 说明 |
|---|---|
| role | 角色（如 云架构师/迁移工程师/DBA/项目经理） |
| person_days | 该角色投入人天 |
| daily_rate | 日单价（¥） |
| subtotal | `person_days × daily_rate`，未乘风险溢价前的小计 |

## 风险溢价

- 系数默认 **1.1**，可按项目复杂度/客户议价空间调整（范围建议 1.0–1.3）。
- 应用方式：`total_amount = Σ(subtotal) × risk_premium`，溢价是在全部 Workstream 汇总之后统一乘，不是逐条乘。

## 报价表建议落地格式

CSV 风格一行一条：

```
workstream,role,person_days,daily_rate,subtotal
Landing Zone,云架构师,5,3500,17500
数据迁移,DBA,8,3000,24000
...
```

## 口径参考（本地降级模式/无 LLM 时人工核对用）

- `/workspace/pcs-presales`（报价刊例）
- `00项目/01-AICC/04AICloudConsultingPlatform/02产品SOW/安畅标准SOW/00定价与服务目录`

## 置信度判定（供 SKILL.md 正文的升级契约引用）

- `llm_used=true` 且 facts 字段完整 → 置信度「高」
- `llm_used=false`（mock 降级）或 facts 关键字段缺失靠默认值补齐 → 置信度「低」，`suggested_action` 必须包含"人工复核金额异常的 Workstream 行"
