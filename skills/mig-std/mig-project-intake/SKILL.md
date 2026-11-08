---
name: mig-project-intake
description: "项目启动阶段，当用户要求「创建/填写项目信息表、整理立项信息、把客户背景材料结构化」时，收集客户背景、迁移目标与约束条件并产出项目信息表。主触发是目标产物（项目信息表），不是已有材料。能力边界：只做材料内部的信息抽取、一致性检查与结构化落盘；不做云上资源采集与核验（归 mig-resource-assessment）、不做规模评估、不测算人天、不生成 SOW。"
风险等级: 只读
输入参数: "客户背景材料（文档/表单/对话记录）、源云与目标云、迁移范围（系统清单）、时间与合规约束、干系人与联系方式"
依赖工具: [mcp__feishu_mcp__fetch_doc, mcp__feishu_mcp__fetch_file, read_file, web_extract, write_file]
skill依赖: []
版本: 2026-10-27.001
输入: 客户背景材料（会议纪要/邮件/招标文件/系统清单）
输出: 项目信息表 project-info.md
上游: 无（流水线起点）
下游: mig-resource-assessment, mig-quotation, mig-sow-generator
编排: 叶子。上游: 无（链路起点）；下游: mig-resource-assessment。被 mig-startup-orch 调度为阶段 1。
---

# 项目信息收集

把一个迁移项目从"客户口头说的"变成"字段齐全、可流转的结构化信息表"。
这是整条流水线的**入口**，后面所有 skill 都吃它的产出。

## 触发与完成判据

- **触发**：新迁移项目立项 / 客户提供背景材料 / 明确要求填项目信息表
- **完成**：项目信息表落盘，且必填字段齐备或已进"待确认清单"
- **不做**：资源评估（`mig-resource-assessment`）、报价（`mig-quotation`）、SOW（`mig-sow-generator`）

## 执行流程

1. **收素材**：本地文件走 `read_file`；飞书文档走 `mcp__feishu_mcp__fetch_doc` / `mcp__feishu_mcp__fetch_file` 拉成本地 md 再读，不要直接 `web_extract`（只拿登录页）。
2. **抽取字段**：按下表逐项填，能推断的标注推断依据，不能推断的留空进待确认清单。
3. **一致性校验**：只查**材料内部**矛盾（清单内部重复/命名冲突、目标区域与合规要求冲突、时间约束自相矛盾）。**不查云上实际**——清单与云上是否对得上是 `mig-resource-assessment` 的事，本 skill 不采集任何云资源。
4. **落盘**：同时输出 JSON（管线消费）和 Markdown（人读）。

## 字段表（项目信息表）

| 分组 | 字段 | 必填 | 说明 |
|---|---|---|---|
| 项目 | 项目名 / 客户名 / 编号 | ✅ | 客户名对外匿名时用 `xx customer` |
| 项目 | 项目类型 | ✅ | 迁移 / 容灾 / 上云 / 改造 |
| 源端 | 源云平台 + 区域 | ✅ | 如 AWS me-central-1 |
| 源端 | 账号数量 / 是否多账号 | ⬜ | 影响 Landing Zone 设计 |
| 源端 | 系统清单 | ✅ | 系统名 / 用途 / 是否生产 / 技术栈 |
| 目标 | 目标云平台 + 区域 | ✅ | 如 阿里云 me-east-1 |
| 目标 | 网络互联方式 | ⬜ | 专线 / VPN / 公网 |
| 规模 | 实例数量与规格 | ⬜ | 交给 `mig-resource-assessment` 补 |
| 规模 | 数据量（全量 / 增量） | ⬜ | 单位明确 TB/GB |
| 约束 | RTO / RPO | ⬜ | 未确认不得出终版报价 |
| 约束 | 停机窗口 | ⬜ | 可用时长 + 允许时段 |
| 约束 | 合规要求 | ⬜ | 等保 / 数据驻留 / 行业监管 |
| 约束 | 交付截止日 | ⬜ | |
| 干系人 | 客户对接人 / 我方负责人 | ✅ | |

## 输入缺失行为

### 交互模式

按必填清单逐项向工程师提问补齐，一次问清，不挤牙膏。

### 无头模式（不得反问，逐输入预定义）

按 `输入参数` 逐项一行，**没有缺失分支的输入 = 未定义行为，禁止执行**。

| 输入项 | 缺失时行为 | 处置 | 阻塞 | 降级产物 | 置信度 |
|---|---|---|---|---|---|
| 客户背景材料 | 终止并升级 | — | 是 | 升级包 | 不产出 |
| 源云 + 区域 | 终止并升级 | — | 是 | 升级包 | 不产出 |
| 目标云 + 区域 | 终止并升级 | — | 是 | 升级包 | 不产出 |
| 迁移范围（系统清单） | 终止并升级 | — | 是 | 升级包 | 不产出 |
| 干系人与联系方式 | 降级继续 | 留空进待确认清单 | 否 | 信息表（干系人待确认） | −0.1 |
| 时间与合规约束 | 降级继续 | 留空进待确认清单，标注影响 RTO/RPO 与停机窗口 | 否 | 信息表（约束待确认） | −0.1 |
| 项目类型 | 降级继续 | 标 `推断`（据材料判定 迁移/容灾/上云/改造） | 否 | 信息表（类型推断） | −0.1 |

- 能从素材推断 → 填值并标 `推断`，同时写推断依据
- 非阻塞项缺失 → 留空进待确认清单，降级继续，按上表扣置信度
- 任一阻塞项缺失 → **终止并升级**，不产出信息表

## 输出双形态

### 结构化 JSON（schema 固定）

```json
{
  "skill": "mig-project-intake",
  "project": {"name": "", "customer": "", "type": ""},
  "source": {"cloud": "", "region": "", "account_count": 0},
  "target": {"cloud": "", "region": "", "interconnect": ""},
  "systems": [{"name": "", "purpose": "", "production": true, "stack": ""}],
  "constraints": {"rto": "", "rpo": "", "downtime_window": "", "compliance": []},
  "conclusion": "complete | partial",
  "confidence": 0.0,
  "confidence_reason": "",
  "missing_fields": [],
  "suggested_actions": ["下一步调用 mig-resource-assessment"],
  "escalation": {
    "required": false,
    "reason": "",
    "ruled_out": [],
    "remaining_hypotheses": [],
    "first_checks": [],
    "chain": {
      "leaf_skill": "mig-project-intake",
      "step": "",
      "state_at_escalation": ""
    }
  }
}
```

### 人类可读

套 `templates/project-info.md` 渲染成 Markdown，落 `~/cloud-docs/delivery/<项目>/intake/项目信息表.md`。

## 升级契约

**触发**：
- **置信度 < 0.6**（任意降级累计扣分后）→ 升级，不交付产物
- **风险等级与授权不匹配**：本次任务要求调用任何 create/update/delete 类云 API，超出本 skill `风险等级`（只读）与租户授权范围 → 立即终止并升级
- **工具不可用**：飞书文档 `fetch_doc` 返回登录页/403，且无本地材料可用 → 升级（注明已尝试的取数方式与失败码）
- 阻塞项（背景材料/源云/目标云/系统清单）在无头模式下缺失
- 素材内部自相矛盾且无法判定
- 客户明确表示"不确定迁什么"

**升级包三要素**（缺一不可，同时进 JSON 的 `escalation` 对象）：

```json
{
  "ruled_out": ["已排除的假设，如：非跨境迁移（材料已明确同区域）"],
  "remaining_hypotheses": ["剩余假设，如：清单 76 台均为生产实例"],
  "first_checks": ["建议人先看哪，最多三条按优先级：①… ②… ③…"]
}
```

- `ruled_out` — 已排除了什么（哪些假设已被材料证伪或确认不适用）
- `remaining_hypotheses` — 剩余哪些假设（未验证、影响后续结论的判断）
- `first_checks` — 建议人先看哪里（最多三条，按优先级排序）

## 输出双形态落盘约定

- 交付物根目录：`~/cloud-docs/delivery/<项目>/`
- 本 skill 产出：`intake/项目信息表.md` + `intake/project-info.json`

## 红线

- 不编造客户信息、人员、案例；未核实写"未核实"
- 客户名对外匿名时用 `xx customer`
- 不在此阶段给任何金额或人天数字

## 引用（不复制）

- 定价与商务口径 → `workbuddy-rules` / `references/selling.md`
- 迁移方法论 → `workbuddy-rules` / `references/cloud-msp.md`
