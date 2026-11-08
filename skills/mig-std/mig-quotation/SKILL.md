---
name: mig-quotation
description: "【离线兜底实现，非首选路由】当用户要求「出报价单 / 测算人天 / 算多少钱」时，按 AC-MIG 计价模型把资源规模换算成角色×人天明细并生成报价单。路由说明：首选 `presales/pcs-quotation`（同一 AICC 能力 Generate-Quotation 的 10-29 升级版）；仅当 `aicc.execute_skill` 不可达、需要纯本地确定性计算时才用本 skill——本 skill 的价值在于 4 个已实测可跑的本地脚本（calc_total / validate_pricing / validate_quote / xlsx_from_md），无网络依赖。主触发是目标产物（报价单），不是已有评估报告。能力边界：只做工作量测算与报价表生成；不写 SOW 正文（归 mig-sow-generator，其第 14 章引用本 skill 结果）、不做技术选型建议、不自行让步折扣与账期。"
风险等级: 只读
输入参数: "初始资源评估报告（资源数量与规格、数据量）、项目类型与复杂度系数、单价基准（默认 $350/人天）、是否多区域/异构数据库、交付语言要求"
依赖工具: [terminal, read_file, write_file]
skill依赖: [mig-resource-assessment]
辅助脚本: [scripts/calc_total.py, scripts/validate_pricing.py]
版本: 2026-10-31.002
路由: 兜底（首选 presales/pcs-quotation）
输入: 资源评估报告 + 项目信息表（必填）
输出: 报价单（角色×人天明细）
上游: mig-resource-assessment, mig-project-intake
下游: mig-sow-generator
编排: 叶子。上游: mig-resource-assessment；下游: mig-sow-generator（第 14 章引用其产出）。被 mig-startup-orch 调度为阶段 3a。
---

# 报价与人天评估

按 **AC-MIG 计价模型**把资源规模换成钱和人天。
核心纪律：**必须给 角色 × 人天 明细表，不能只给一个总数**。

## 触发与完成判据

- **触发**：已有资源评估报告 / 要求报价或人天测算
- **完成**：人天测算表 + 报价单落盘，待确认清单已列
- **不做**：SOW 正文（第 14 章由 `mig-sow-generator` 引用本 skill 结果）、选型建议

## 计价模型

| 项 | 值 |
|---|---|
| 标准人天单价 | **$350 / 人天** |
| 偏离处理 | 任何偏离必须在文档里说明理由 |
| 角色拆分 | 架构师 / 迁移工程师 / DBA / 数据工程师 / PM |
| 加计项 | 多区域多可用区、异构数据库迁移 → 单独计列风险工时 |

## 输出结构（固定顺序）

```
项目背景 → 范围与假设 → 资源评估结论 → 工作分解（WBS）→ 人天测算表 → 商务条款 → 待确认清单
```

**人天测算表至少含列**：`角色 / 工作内容 / 人天 / 单价 / 小计`

## 待确认清单（必写，缺一不可）

- RTO / RPO
- 停机窗口
- 数据增量
- 第三方 License
- 是否有等保/合规要求

**RTO/RPO 未确认，不得出终版报价**——只能出标注"预报价"的草稿。

## 测算校验（必跑，别信文本里的"合计"）

落盘前必跑脚本重算，验证 **人天 × 单价 = 小计、各行小计之和 × 风险溢价 = 总计**：

```bash
# 1) 由 WBS 生成总额（确定性计算，禁止正文手算）
/home/ubuntu/.hermes/hermes-install/venv/bin/python3 scripts/calc_total.py <wbs.json> --out total.json

# 2) 校验报价文件（json / xlsx 均可，结构自动识别）
/home/ubuntu/.hermes/hermes-install/venv/bin/python3 scripts/validate_pricing.py <报价文件>
# 需要时显式指定溢价系数
/home/ubuntu/.hermes/hermes-install/venv/bin/python3 scripts/validate_pricing.py <报价文件> 1.1
# xlsx 多表时可指定工作表（默认自动找含「人天」表头的那张）
/home/ubuntu/.hermes/hermes-install/venv/bin/python3 scripts/validate_pricing.py <报价.xlsx> --sheet 表2
```

- `calc_total.py` 输入 `wbs.json`：`{"rate": 350, "rows": [{"role": "架构师", "days": 15}, {"role": "DBA", "days": 30, "rate": 380}]}`，`rate` 可每行覆盖（按角色议价），`days` 支持小数
- `validate_pricing.py` 自动识别三种输入结构，**无需转换字段**：
  - A) AC-MIG 输出：`{"workstreams":[{"lines":[{"role","person_days","daily_rate","subtotal"}]}],"total_amount":..}`
  - B) 扁平明细：`[{"workstream","role","person_days","daily_rate"}, ...]`
  - C) 旧 WBS：`{"unit_price":..,"wbs":[{"role","days","unit_price","subtotal"}],"total_amount":..}`
  - xlsx：按表头名定位「人天/单价/小计」列，容忍千分位逗号与货币符号
- **溢价系数**：优先取显式 `risk_premium`/`premium`；未声明时由 `total_amount ÷ 明细小计之和` 反推（仅在比例 ∈ [1.0, 2.0] 且两位小数内时采用，避免把笔误当溢价）。命令行第二参数可覆盖
- 退出码：`0` 通过 / `1` 校验失败 / `2` 输入不可用（坏 JSON、无明细表、全 0 人天均判 2，不抛 traceback）
- **全 0 人天一律判 2**，不得因"恰好都为 0"而误报通过
- 校验不通过或退出码 2 → 按升级契约「工具不可用」分支升级，**不得手工改数字绕过**
- `validate_quote.py` 是 `validate_pricing.py` 的软链别称，两者同一实现

实测教训：子 agent 自述的"合计"曾与明细不符，**父 agent 必须自己算一遍**。

## 双语规则

- 中英双语**分开成文件**：`报价_CN.docx` / `Quotation_EN.docx`
- 英文版按英文商务习惯重写，去掉中文版客套与铺垫
- 内部测算用 `xlsx`，公式可追溯，不写死数字

## 输入缺失行为

### 交互模式

缺评估报告 → 要求先跑 `mig-resource-assessment`；RTO/RPO 未定 → 出预报价并标红。

### 无头模式（不得反问，逐输入预定义）

按 `输入参数` 逐项一行，**没有缺失分支的输入 = 未定义行为，禁止执行**。

| 输入项 | 缺失时行为 | 处置 | 阻塞 | 降级产物 | 置信度 |
|---|---|---|---|---|---|
| 资源评估报告（规模数据） | 终止并升级 | 基准系数 β 无资源数据支撑 | 是 | 升级包 | 不产出 |
| 项目信息表 | 降级继续 | 仅出《内部测算表》，不出对客户报价单 | 否 | 内部测算表 | −0.2 |
| 项目类型与复杂度系数 | 降级继续 | 按报告风险命中项自动取档：每命中 1 项 +0.05，封顶 +0.3 | 否 | 报价单（含系数说明） | −0.1 |
| 单价基准 | 降级继续 | 默认 $350/人天，假设里写明口径 | 否 | 报价单 | −0 |
| 交付语言要求 | 降级继续 | 默认中文单语 `CN` | 否 | 报价单_CN | −0 |
| 折扣授权 | 降级继续 | 折扣栏留空，不自行填折扣 | 否 | 报价单（标准价） | −0 |
| RTO/RPO 未确认 | 降级继续 | 出**预报价**，显著标注「待确认，非终版」 | 否 | 预报价单 | −0.3 |

## 输出双形态

### 结构化 JSON

```json
{
  "skill": "mig-quotation",
  "project": "",
  "currency": "USD",
  "unit_price": 350,
  "wbs": [{"id": "W1", "name": "", "role": "", "days": 0, "subtotal": 0}],
  "risk_days": [{"reason": "", "role": "", "days": 0}],
  "total_days": 0,
  "total_amount": 0,
  "is_final": false,
  "is_final_blocker": ["RTO/RPO 未确认"],
  "pending_confirm": [],
  "conclusion": "",
  "confidence": 0.0,
  "confidence_reason": "",
  "suggested_actions": ["SOW 第 14 章引用本结果"],
  "escalation": {
    "required": false,
    "reason": "",
    "ruled_out": [],
    "remaining_hypotheses": [],
    "first_checks": [],
    "chain": {
      "leaf_skill": "mig-quotation",
      "step": "",
      "state_at_escalation": ""
    }
  }
}
```

### 人类可读

- 内部测算：`~/cloud-docs/delivery/<项目>/quotation/人天测算.xlsx`
- 对外报价（MD 源）：`~/cloud-docs/delivery/<项目>/quotation/报价_CN.md` / `Quotation_EN.md`
- 对外报价（xlsx 成品）：`~/cloud-docs/delivery/<项目>/quotation/报价_CN.xlsx` / `Quotation_EN.xlsx` — 由 `scripts/xlsx_from_md.py` 生成，不在正文手敲 openpyxl

**落盘前必跑校验**：`python3 scripts/validate_pricing.py <报价文件>`。不通过不许交付（人天×单价=小计，小计之和=总计）。校验不通过属执行失败，不得手工改数字绕过。

## 升级契约

**触发**：
- **置信度 < 0.6**（任意降级累计扣分后）→ 升级，不交付产物
- **风险等级与授权不匹配**：本次任务要求调用任何 create/update/delete 类云 API，超出本 skill `风险等级`（只读）与租户授权范围 → 立即终止并升级
- **工具不可用**：`scripts/validate_pricing.py` 校验不通过且无法通过调整 WBS 修复 → 升级（附测算明细与不符项）
- 无头模式缺资源规模
- 客户压价要求低于模型测算值（需商务决策，非 skill 可自行让步）
- 涉及折扣、账期、付款节点等商务条款超出标准范围

**升级包三要素**（缺一不可，同时进 JSON 的 `escalation` 对象）：

- `ruled_out` — 已排除了什么：如已确认非折扣审批流程问题（商务已口头同意，缺书面）
- `remaining_hypotheses` — 剩余哪些假设：如剩余假设为增量数据按 10% 估、不含风险加计
- `first_checks` — 建议人先看哪里（最多三条）：① 找商务要书面折扣授权；② 确认客户是否已书面确认交付范围；③ 确认 WBS 中估算条目的实测依据

**升级前必做**：测算明细与公式、WBS 中哪些条目是估算值列出，逐条写进升级包。

## 红线

- 绝不虚构已成交案例或客户名做背书
- 数字必须有测算依据，禁止"拍一个数"
- 交付物落 `~/cloud-docs/delivery/<项目>/quotation/`

## 引用（不复制）

- AC-MIG 定价与报价规范 → `workbuddy-rules` / `references/selling.md`
- 数字口径与风险项 → `workbuddy-rules` / `references/cloud-msp.md`
- 参考模板：`~/cloud-docs/Quick_Quotation_Template_CN.xlsx`、`Express_Logistics_Quotation_CN_Final.xlsx`

## 第〇步：选厂家色系（出稿前必须先定）

目标云 / 甲方生态决定皮肤；无厂家归属时回退安畅红（中立 MSP）。

| 场景 | `--brand` | 主色 | 变体模板 |
|---|---|---|---|
| 目标云 阿里云 / 甲方阿里生态 | `alibaba` | `FF6A00` | `templates/报价单_阿里橙.md` |
| 目标云 腾讯云 / 甲方腾讯生态 | `tencent` | `3370FF` | `templates/报价单_腾讯蓝.md` |
| 中立 / 无明确厂家（默认） | `anchnet` | `C00000` | `templates/报价单_安畅红.md` |
| 目标云 AWS / 甲方 AWS 生态 | `aws` | `232F3E` | `templates/报价单_AWS黑.md` |
| 目标云 Azure / 甲方微软生态 | `azure` | `00477F` | `templates/报价单_Azure浅蓝.md` |

**交付前必过闸门**：`mig-std/doc-audit-gate`（去 AI 味 40 / 事实红线 40 / 版式色系 20）。
红线（虚构人员·证书·案例、金额臆造、占位符残留、数字跨章冲突、RACI 缺位）任一命中即 BLOCK，催也不放。

**色系与厂家口径单一事实源**：`mig-std/brand-doc-kit`
- 取变体模板：`python3 brand-doc-kit/scripts/build_variant.py --type quotation --brand <厂家> -o out.md`
- 渲染 docx：`python3 brand-doc-kit/scripts/build_docx.py out.md --brand <厂家> -o out.docx`
- 出 xlsx：`python3 scripts/xlsx_from_md.py out.md --brand <厂家> -o out.xlsx`（表头底+字色随厂家；省略 `--brand` 走中性灰 `D9D9D9`，正式投标用）
- 开箱核验：`python3 brand-doc-kit/scripts/verify_brand_variants.py`（色值 / 附录E / 串用 / 差异度）

**xlsx 与 docx 必须同 `--brand`**：同一份报价单两个形态（xlsx 报价表 + docx 说明）色系不一致视为不合格。md 是唯一源，两个形态都从它渲染，禁止分别手改。
