---
name: mig-resource-assessment
description: "项目启动阶段，当用户要求「核验资源规模、采集源端真实资源、出具资源评估报告」时，基于系统清单做初始资源评估并输出评估报告。主触发是目标产物（评估报告），不是已有清单。能力边界：只做只读资源采集与规模评估；不做系统级深度调研（mig-system-survey）、不测算报价与不写 SOW。"
风险等级: 只读
输入参数: "系统清单（来自 mig-project-intake）、源云账号凭据或只读授权、目标云平台、采集时间窗口"
依赖工具: [mcp__alicloud, mcp__aws, mcp__azure, mcp__hwecs, mcp__hwrds, mcp__hwevs, mcp__hwvpc, mcp__hwobs, read_file, write_file, execute_code]
skill依赖: [mig-cloud-adapter]
辅助脚本: [scripts/aggregate.py]（软链至 `mig-cloud-adapter` 同名脚本，避免同源重复）

**跨 skill 能力契约**：本 skill 依赖 `mig-cloud-adapter` 的采集能力，不复制其脚本，只通过软链复用，并在能力声明中标注归属。若 `mig-cloud-adapter` 变更 `aggregate.py` 的输入 schema 或退出码含义，须同步验证本 skill 的调用方式仍然成立。
输入: 系统清单 + 云账号凭据（必填）
输出: 评估报告 + inventory.json
上游: mig-project-intake
下游: mig-quotation, mig-sow-generator
版本: 2026-10-27.001
编排: 叶子。上游: mig-project-intake；下游: mig-quotation, mig-sow-generator。被 mig-startup-orch 调度为阶段 2。依赖 mig-cloud-adapter 提供采集能力。
---

# 初始资源评估

把"客户说自己有 76 台机器"变成"采集时间 X、实际 Y 台、规格分布 Z"的可信数字。
**只用只读接口**，不碰任何变更类 API。

## 触发与完成判据

- **触发**：已有系统清单 / 拿到源云只读授权 / 要求评估资源规模
- **完成**：评估报告落盘，含资源明细表 + 规模结论 + 采集覆盖率
- **不做**：系统级深度调研（`mig-system-survey`）、报价（`mig-quotation`）、方案设计类

## 执行流程

**分工**：批量查询与聚合计算一律走 `scripts/aggregate.py`，正文只做流程决策与判定，不手写采集循环和汇总算术。

**能力契约（脚本实际能力边界）**：`scripts/aggregate.py` 只输出四件事——`coverage`（覆盖率）、`missing_ids`（缺失 ID）、`gaps`（缺口清单）、`by_domain`（分域 expected/collected 计数）。它**不做**规格映射、不出容量合计（vCPU/内存/存储）、不识别引擎版本。第 4、5 步的规格映射与容量汇总由本 skill 正文基于 `collected` 明细自行完成，不得声称由脚本产出。若后续脚本扩展了能力，须同步更新本段声明。

1. **拿凭据**：源云只读凭据，走环境变量/凭据文件注入，不在 SKILL 与配置里硬编码。按源云选 MCP：阿里云 `mcp__alicloud`、AWS `mcp__aws`、Azure `mcp__azure`、华为云 `mcp__hwecs`/`mcp__hwrds`/`mcp__hwevs`/`mcp__hwvpc`/`mcp__hwobs`。
2. **分域采集**：计算 / 存储 / 数据库 / 中间件 / 网络五域并行只读拉取，结果写入 `inventory.json`（`{"expected": [...], "collected": [...], "unmatched": [...]}`）。
3. **对齐系统清单**：云上实际资源与清单比对 → `scripts/aggregate.py <inventory.json>`，输出**覆盖率**与**差异项**。
4. **规格映射**：源端规格 → 目标云等价规格，查 `references/云规格映射表.md`。规格无映射的单独列出，标"待人工选型"。
5. **规模结论**：由本 skill 基于 `collected` 明细自行汇总——实例总数、vCPU/内存合计、存储总量、数据库实例数与引擎版本；分域 expected/collected 计数可对照 `scripts/aggregate.py` 输出的 `by_domain`。
6. **风险初判**：按 `references/风险清单.md` 逐项比对（异构数据库、跨地域带宽、Serverless 依赖、快照增量规模）。

## 采集覆盖判据

| 覆盖率 | 处置 |
|---|---|
| ≥ 95% | 可出评估报告，正常流转 |
| 80–95% | 出报告，差异项列入待确认清单 |
| < 80% | **升级**：凭据权限不足或清单严重失真，先补授权再评估 |

## 输入缺失行为

### 交互模式

向工程师要凭据或确认区域；规格无映射时请工程师指定目标规格。

### 无头模式（不得反问，逐输入预定义）

按 `输入参数` 逐项一行，**没有缺失分支的输入 = 未定义行为，禁止执行**。

| 输入项 | 缺失时行为 | 处置 | 阻塞 | 降级产物 | 置信度 |
|---|---|---|---|---|---|
| 系统清单 | 降级继续 | 以云上采集结果为唯一口径，标注「无清单可比对」，覆盖率记为不适用 | 否 | 报告（缺差异项） | −0.2 |
| 源云只读凭据 | 终止并升级 | — | 是 | 升级包 | 不产出 |
| 目标云平台 | 终止并升级 | 无目标规格映射基准，规模结论无法成立 | 是 | 升级包 | 不产出 |
| 采集时间窗口 | 降级继续 | 取当前时间为采集时间并在报告中标注 | 否 | 报告（采集时间=执行时刻） | −0.05 |
| 规格映射缺失（单条） | 降级继续 | 该条标 `待人工选型`，不计入映射完成率分子 | 否 | 报告（含待选型清单） | −0.05/条 |
| 单域采集失败（如网络域） | 降级继续 | 该域标「未采集」，其余域继续 | 否 | 报告（该域缺失） | −0.1/域 |

## 输出双形态

### 结构化 JSON

```json
{
  "skill": "mig-resource-assessment",
  "collected_at": "2026-10-27T10:00:00+08:00",
  "source": {"cloud": "", "region": "", "account_count": 0},
  "resources": {
    "compute": {"count": 0, "vcpu_total": 0, "mem_gb_total": 0, "by_spec": {}},
    "storage": {"total_tb": 0, "by_type": {}},
    "database": {"count": 0, "engines": {}},
    "middleware": {"count": 0, "types": {}},
    "network": {"vpc_count": 0, "eip_count": 0, "bandwidth_mbps": 0}
  },
  "coverage": 0.0,
  "diff_vs_checklist": [],
  "mapping_unresolved": [],
  "conclusion": "",
  "confidence": 0.0,
  "confidence_reason": "",
  "suggested_actions": ["下一步调用 mig-quotation"],
  "escalation": {
    "required": false,
    "reason": "",
    "ruled_out": [],
    "remaining_hypotheses": [],
    "first_checks": [],
    "chain": {
      "leaf_skill": "mig-resource-assessment",
      "step": "",
      "state_at_escalation": ""
    }
  }
}
```

### 人类可读

套 `templates/assessment-report.md`，落 `~/cloud-docs/delivery/<项目>/assessment/初始资源评估报告.md`。

## 数字口径（硬性）

- 资源数量：区分**规格**与**数量**，必须标注源端采集时间
- 数据量：区分**全量快照**与**增量**，单位 TB/GB 明确
- 停机窗口 RTO/RPO：未确认不得出终版报价（本 skill 若拿到就记，拿不到就标待确认）
- 所有未确认项进"待确认清单"单列一节

## 升级契约

**触发**：
- **置信度 < 0.6**（任意降级累计扣分后）→ 升级，不交付产物
- **风险等级与授权不匹配**：本次任务要求调用任何 create/update/delete 类云 API，超出本 skill `风险等级`（只读）与租户授权范围 → 立即终止并升级
- 无有效只读凭据（无头模式）
- **工具不可用**：`mig-cloud-adapter` 不可用导致零资源成功、或 `scripts/aggregate.py` 缺失/执行失败 → 升级，不静默降级为纯清单估算
- 覆盖率 < 80%
- 发现清单之外的生产级资源（说明客户漏报，需人确认范围）

**升级包三要素**（缺一不可，同时进 JSON 的 `escalation` 对象）：

- `ruled_out` — 已排除了什么：如已确认非权限问题（换账号重试仍 403）、已排除清单口径过时
- `remaining_hypotheses` — 剩余哪些假设：如剩余 12 台可能在未授权的第二个账号下
- `first_checks` — 建议人先看哪里（最多三条）：① 查 IAM 只读策略是否覆盖全部 region；② 确认是否有第二个订阅/账号；③ 确认清单是否为最新版本

**升级前必做**：已尝试的采集方式、失败码、已排除的原因，逐条写进升级包。

## 红线

- **只读**：禁止调用任何 create/update/delete 类 API
- 零费用：采集 API 调用注意免费额度，大数据量清单分页拉取
- 不编造资源数字；采不到就写"未采集"

## 引用（不复制）

- 云 CLI 适配 → `mig-cloud-adapter`（贾泽鹏）
- 规格映射表 → `references/云规格映射表.md`（本 skill 内）
- 常见风险清单 → `references/风险清单.md`（本 skill 内）；数字口径 → `workbuddy-rules` / `references/cloud-msp.md`
