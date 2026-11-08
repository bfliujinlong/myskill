---
name: pcs-quotation
---

# 云迁移报价生成（pcs-quotation）

| 字段 | 值 |
|---|---|
| **description** | 云迁移报价生成 - 触发条件：已有 Fact Sheet（见 `pcs-factsheet` 输出）且需要按角色/人天/金额出一份正式报价单时触发；完成判据：产出按 6 个 Workstream 拆分、含风险溢价的报价单（结构化 JSON + DOCX）。不负责 Fact Sheet 本身的采集/生成（那是 `pcs-factsheet` 的边界），不负责 SOW 章节撰写（那是 `pcs-sow`）。 |
| **风险等级** | 低风险写（只生成文档/落库一条执行历史，不改任何客户侧系统状态） |
| **输入参数** | `facts`（Fact Sheet 结构化对象，必填，来自 `pcs-factsheet` 的输出或用户直接提供）；`risk_premium`（风险溢价系数，选填，默认 1.1） |
| **依赖工具** | aicc.execute_skill |
| **版本** | 2026-10-29.001 |

对应 AICC 后端内置能力 `Generate-Quotation`（`backend/app/ai/skills/builtin.py`）。
对应「云迁移Agent构建计划与排期-V1.xlsx」Skill 清单中的 **报价与人天评估**（项目启动阶段，刘金龙负责，输入=资源规模，输出=报价单+人天，模板=计价模型）。

## 触发条件 / 完成判据

- 触发：用户已提供或已产出 Fact Sheet，且明确要求"报价/算人天/出报价单"。
- 完成：返回按 Landing Zone / 迁移设计 / 数据迁移 / 应用迁移 / 切割切换 / 运维交接 六个
  Workstream 拆分的人天与金额汇总，且每个 Workstream 即使是 0 人天也要在 `notes` 里说明。

## 判断逻辑（正文）

1. **输入完整性检查**：`facts` 是否存在且至少含 `project_type`/`current_cloud`/`target_cloud`。
   - 交互模式：缺失时直接向用户追问缺的字段。
   - 无头模式：不得假设可反问，按以下分支之一处理——
     a) 若上游刚执行过 `pcs-factsheet` 并有输出，直接取其 `outputs` 作为 `facts`（调工具取数）；
     b) 若 `facts` 部分字段缺失但不影响报价粒度（如 `budget_range` 缺失），用 `null` 占位继续，在输出的
        `notes`/`剩余假设` 里记录（降级继续）；
     c) 若连 `project_type`/`target_cloud` 都没有，无法估算，**终止并升级**（见下方升级契约）。
2. **调用依赖工具**：`aicc.execute_skill("Generate-Quotation", {"facts": facts, "risk_premium": risk_premium or 1.1})`。
3. **降级判定**：检查返回的 `llm_used`。
   - `true`：按正常结果处理，`confidence` = 高。
   - `false`（mock）：**不可直接交付**，改走本地确定性计算 `scripts/ac_mig_pricing.py`
     （需要先把 `facts` 里的资源规模按 `references/ac-mig-pricing.md` 的方法论人工/规则转成
     `workstream/role/person_days/daily_rate` 明细行，再传入脚本），`confidence` = 低。
   - `aicc.execute_skill` **不可达**（本机默认状态：127.0.0.1:8000 / 8.153.148.69 均不通）：
     直接走本地确定性链路，不等待、不重试：
     1. 按 `references/ac-mig-pricing.md` 把 `facts` 转成 `role/person_days/daily_rate` 明细行；
     2. `~/.hermes/skills/mig-std/mig-quotation/scripts/calc_total.py <wbs.json>` 算人天与总额；
     3. `validate_pricing.py <quote.json>` 校验「人天×单价=小计，小计之和×风险溢价=总计」
        （json / xlsx 均可，三种 JSON 结构自动识别；第二参数可显式传溢价系数，
        xlsx 用 `--sheet <表名>` 指定工作表，默认自动找含「人天」表头的那张）；
        退出码 2 = 输入不可用（坏 JSON / 无明细表 / 全 0 人天），不抛 traceback；
     4. `xlsx_from_md.py <quote.md> -o <out.xlsx>` 出 Excel 报价单（安畅模板口径）；
     5. `confidence` = 低，`suggested_action` 写明「本地确定性计算，未经 AICC 大模型渲染，需人工复核后交付」。
     风险溢价仍按 6 个 Workstream 小计汇总后统一乘一次（默认 1.1），不得逐行乘。
   - `aicc.execute_skill` **不可达**（本机默认状态：127.0.0.1:8000 / 8.153.148.69 均不通）：
     直接走本地确定性链路，不等待、不重试：
     1. 按 `references/ac-mig-pricing.md` 把 `facts` 转成 `role/person_days/daily_rate` 明细行；
     2. `~/.hermes/skills/mig-std/mig-quotation/scripts/calc_total.py <wbs.json>` 算人天与总额；
     3. `validate_pricing.py <quote.json>` 校验「人天×单价=小计，小计之和=总计」；
     4. `xlsx_from_md.py <quote.md> -o <out.xlsx>` 出 Excel 报价单（安畅模板口径）；
     5. `confidence` = 低，`suggested_action` 写明「本地确定性计算，未经 AICC 大模型渲染，需人工复核后交付」。
     风险溢价仍按 6 个 Workstream 小计汇总后统一乘一次（默认 1.1），不得逐行乘。
4. **定价方法论**：完整规则见 `references/ac-mig-pricing.md`（不复制到此处，只链接）。核心点：
   六个 Workstream 固定拆分、风险溢价在全部小计汇总后统一乘一次（默认 1.1）。
5. **输出渲染**：用 `templates/quotation-report.md` 产出人类可读版本；结构化 JSON 见下。

## 输出双形态

**结构化 JSON**（在 `Generate-Quotation` 原始 `output_schema` 之上包一层标准包络）：

```json
{
  "conclusion": "报价已生成，总金额 ¥{total_amount}，共 {total_person_days} 人天",
  "confidence": "高 | 低",
  "suggested_action": "交付给客户 | 人工复核金额异常的 Workstream 行后再交付",
  "escalation_reason": null,
  "workstreams": [...],
  "total_person_days": 0,
  "total_amount": 0,
  "currency": "CNY",
  "notes": []
}
```

**人类可读**：AICC 后端自动生成的 DOCX（`document.download_url`）+ `templates/quotation-report.md`
的 Markdown 渲染（聊天场景即时展示用）。

## 升级契约

- **触发条件**：
  - `aicc.execute_skill` 工具不可达（后端连接失败）且本地降级计算因 `facts` 关键字段缺失也算不出；
  - `llm_used=false` 且降级计算后仍有 Workstream 金额为 0 但该 Workstream 其实应有工作量（如有数据库却"数据迁移"为 0）；
  - `facts` 中 `project_type`/`target_cloud` 缺失，无头模式下不可反问。
- **升级打包**（交给人工时至少包含）：
  - 已排除：是否已尝试过真实 LLM 调用（`llm_used` 的值）、是否已跑过本地确定性计算；
  - 剩余假设：哪些字段是靠默认值/空值补的（如 `budget_range`/`timeline_months` 缺失时的处理）；
  - 建议先看哪里：`workstreams` 里 `subtotal` 为 0 但同类项目通常不为 0 的行。
- **组合语义**：若本 skill 被 `pcs-presales-orch` 调用，升级结果向上传递时必须附带"在报价这一步升级，
  当前 `facts` 状态摘要"，供编排层决定是否有其他叶子 skill 可以先补全缺失信息再回来重试。
