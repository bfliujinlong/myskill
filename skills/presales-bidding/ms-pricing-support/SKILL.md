---
name: ms-pricing-support
description: >
  基于显式报价参数生成确定性报价测算表，所有数字必须来自输入参数，不推断价格。
  使用当用户说"报价测算"、"报价支持"、"价格测算"、"pricing"、"报价表"时激活。
version: 0.1.0-rc.8
status: in-development
allowed-tools: Read, Write, Bash
---

# PCS Pricing Support — 报价测算支持

唯一目标：把**显式报价参数**（数量、单价、周期、折扣）通过确定性脚本计算为报价测算表。

> 所有价格数字必须来自用户显式提供的输入参数。本 Skill 不推断单价、不套用默认价目、不引入模型估算数字。

---

## 支持范围

**支持：**
- 读取显式报价参数 JSON（一次性项、周期项、周期月数、折扣率）；
- 运行 `scripts/compute_pricing.py` 得到确定性合计；
- 按 `references/output-template.md` 生成报价测算表。

**暂不支持（v0.1 边界）：**
- 推断或补全任何缺失的单价/数量；
- 套用行业默认价、成本模型或模型估算；
- 批准价格或对外发送报价。

---

## 执行步骤

### 步骤 0 — 前置检查（强制）

Read `project.yaml`：存在→继续；否则 `BLOCKED: 当前目录不是已初始化的 PCS Project，未找到 project.yaml`。

### 步骤 1 — 收集显式报价参数

要求用户提供或确认报价参数 JSON，字段见 `examples/pricing-input.json`。每个 `quantity` 与 `unit_price` 必须是显式数字。

**禁止**：不替用户补任何价格数字；若缺数字，如实告知缺失项，不猜测。

### 步骤 2 — 确定性计算（强制用脚本）

```bash
python3 "$PLUGIN_ROOT/skills/ms-pricing-support/scripts/compute_pricing.py" --config /path/to/pricing-input.json
```

- 退出码 0：得到确定性合计（一次性合计、月度合计、周期总额、折扣、总计）；
- 退出码非 0：存在缺失或非数值数字，脚本拒绝产出。此时输出 `BLOCKED: 报价参数不完整，缺失显式数字，无法测算`，不得手工凑数。

**纪律**：报价表中的每个数字都必须来自脚本输出（即来自显式输入），不得在文档中手写未经脚本计算的价格。

### 步骤 3 — 生成报价测算表（PREVIEW 模式）

按 `references/output-template.md` 填入脚本输出。默认 PREVIEW。

**报价计量基线完整声明（强制，RC3-P2-012）：**
必须区分三类数量并在报价表中统一输出：

1. **客户/RFP 数量 Baseline**（来自 RFP/客户沟通原文）：
   - 云主机：约 200 台
   - 中间件：约 30 套
   - K8s 集群：数量待确认
2. **报价测算数量**（本次报价计算基准）：
   - 云主机：200 台
   - 中间件：30 套
   - K8s 集群：17 套
3. **客户最终确认数量**：待确认
4. **结算调整机制**：待商务及客户确认

报价表必须输出统一声明：
> 本次报价测算基于 200 台云主机、30 套中间件和 17 套 K8s 集群；客户最终纳管数量及结算调整机制待确认。

**规则：**
- 200、30、17 都是报价测算基准，不得升级为客户最终确认数量；
- 报价表中使用精确数量计算时，必须标记 `pricing_basis`；
- 数量差异不得由 SOW 静默修正；
- 正式结算机制没有输入时，只能写"待商务及客户确认"；
- 不修改现有确定性 Pricing 算法和折扣规则。

### 步骤 4 — 保存（仅用户明确要求时）

须同时满足，缺一即 `BLOCKED` 不写入：

| 条件 | 失败输出 |
|---|---|
| 客户名称已明确 | `BLOCKED: 客户名称待确认，无法生成文件名` |
| 脚本已成功计算（退出码 0） | `BLOCKED: 报价参数不完整，无法测算` |
| 目标目录 `04_商务与合同/01_报价与测算/` 已存在 | `BLOCKED: 目标目录不存在，请先运行 ms-project-init` |
| 目标文件不存在 | `BLOCKED: 文件已存在，路径 <路径>，不覆盖` |

目标文件名：`YYYY-MM-DD-客户名称-报价测算.md`

**写入边界**：只在既有标准目录创建缺失目标文件；Agent 不批准价格；不写入 Company KB；不对外发送。

---

## 输出状态声明

每次执行必须声明：`PREVIEW` / `CREATED: <路径>` / `BLOCKED: <原因>` 之一。

---

## 参考文件

- `scripts/compute_pricing.py` — 确定性报价计算器
- `examples/pricing-input.json` — 无敏感参数示例
- `references/output-template.md` — 报价测算表模板
- `references/contract.json` — 输入输出契约
