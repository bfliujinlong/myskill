---
name: mig-sow-generator
description: "【离线兜底实现，非首选路由】当用户要求「生成 SOW / 工作说明书 / 出 SOW 文档」时，基于项目信息表与资源评估报告生成 SOW。两套模板按交付模式二选一：**服务包模式**（`templates/SOW模板_服务包模式.md`，9 章 + 4 附录，含 RACI 责任矩阵 / SLA 四级 / PCR 变更流程 / 乙方排除项 / 分模块独立验收，事实源 `references/real_sow_yuanjing.md`）与**技术方案模式**（`templates/SOW模板.md`，标准 14 章）。判定：客户要求是「服务包/按系统数验收/不按人天结算」或涉及 RACI、SLA、PCR、排除项 → 服务包模式（默认）；客户要求偏架构设计与技术深度 → 技术方案模式。路由说明：首选 `presales/pcs-sow`；仅当 `aicc.execute_skill` 不可达时才用本 skill，复用 `scripts/build_docx.py`（`--brand` 套厂家色系，默认黑灰）。能力边界：只写 SOW 正文与交付物清单；不做报价测算（归 mig-quotation，商务章只引用其结果）、不做 HLD/LLD 方案设计。"
风险等级: 只读
输入参数: "项目信息表（mig-project-intake 产出）、初始资源评估报告（mig-resource-assessment 产出）、交付语言要求（中文/英文/双语）、客户名是否匿名"
依赖工具: [read_file, write_file, execute_code]
skill依赖: [mig-project-intake, mig-resource-assessment]
辅助脚本: [scripts/build_docx.py]
版本: 2026-10-31.003
路由: 兜底（首选 presales/pcs-sow）
输入: 项目信息表 + 资源评估报告（必填）
输出: SOW 文档（服务包模式 9 章 + 4 附录 / 技术方案模式 14 章）
上游: mig-project-intake, mig-resource-assessment
下游: 无（启动阶段终点）
编排: 叶子。上游: mig-project-intake, mig-resource-assessment, mig-quotation；下游: 无（启动阶段终点）。被 mig-startup-orch 调度为阶段 3b。
---

# SOW 生成

先**选模板**，再按该模板骨架写。章节顺序固定，不改结构、不并章。

## 触发与完成判据

- **触发**：已有项目信息 + 评估结果 / 客户明确要求 SOW
- **完成**：模板内各章齐全、待确认清单已列、docx 落盘
- **不做**：报价测算（`mig-quotation`，商务章只引用其结果不自行计算）、HLD/LLD 设计

## 第〇步：选厂家色系（按项目厂家定模板与皮肤）

| 项目厂家 | 模板文件 | `--brand` | 主色 |
|---|---|---|---|
| 阿里云 | `templates/SOW模板_阿里橙.md` | `alibaba` | `FF6A00` 阿里橙 |
| 腾讯云 | `templates/SOW模板_腾讯蓝.md` | `tencent` | `3370FF` 腾讯蓝 |
| AWS | `templates/SOW模板_AWS黑.md` | `aws` | `16191F` AWS 黑 |
| Azure | `templates/SOW模板_Azure浅蓝.md` | `azure` | `00477F` 深蓝 + `9CB9D8` 浅蓝表头 |
| 厂家中立 / 无厂家 / 多云 | `templates/SOW模板_安畅红.md` | `anchnet` | `C00000` 安畅红 |
| 正式投标技术标 | 任意 | 省略（默认 `blackgray`） | `333333`/`000000`/`D9D9D9`，禁蓝 |

**口径**：需要厂家风格就用厂家的，没有就体现安畅的。色值取自真实厂家文档提取（`brand_profiles/*.json` 内 `evidence` 字段），**不臆造**。

**区分品牌色与项目色**：客户项目自带色（如拳头游戏 `FF0000`、MCD `C00000`）是**项目/客户色**，不得当厂家品牌色用。

渲染命令：
```bash
PY=/home/ubuntu/.hermes/hermes-install/venv/bin/python3
$PY scripts/build_docx.py templates/SOW模板_阿里橙.md --brand alibaba -o SOW_CN.docx
```

## 第一步：选模板（二选一，不混用）

| 判定信号 | 选 | 骨架 |
|---|---|---|
| 服务包/按系统数验收/不按人天结算；涉及 RACI、SLA 等级、PCR 变更流程、乙方排除项、大模块独立验收 | **服务包模式**（默认） | 9 章 + 附录 A–D：`templates/SOW模板_服务包模式.md` |
| 客户要架构设计与技术深度（计算/存储/DB/中间件/网络/HA/可观测分模块详设） | 技术方案模式 | 标准 14 章：`templates/SOW模板.md` |

**默认服务包模式**（真实项目绝大多数按此签）。客户未明示时按服务包模式起稿，并在正文首段写明计价模式。

## 骨架（唯一出处）

**章节结构取自所选模板文件，正文不复制**。生成前先读该文件取章节与要点；模板缺失属断链，按下方输入缺失行为处理。

**服务包模式事实源**：`references/real_sow_yuanjing.md`（真实 SOW，AWS→腾讯云，V1.0 评审稿）——提供 7 阶段工作规划、RACI 责任矩阵（5 组 40+ 活动）、乙方排除项、验收标准 5 条、SLA 四级、大数据/SAP/LZ 专项、阶段交付物表、PCR 流程。**复用结构与条款口径，不得复制客户名/编号/人天数字/第三方厂商名**。

生成顺序：先给每章写二级标题 + 3–5 个要点，确认后再展开正文。**不要一上来就写满全文**。

## 写作口径

| 项 | 要求 |
|---|---|
| 数字 | 全部来自评估报告，标注采集时间；未核实的写"待确认"，不估 |
| 人员 | **绝不虚构人名、角色、证书、案例**（废标风险） |
| 风险章 | 诚实写明"这个量级下常见问题是 X，应对是 Y"，不粉饰 |
| 待确认清单 | 必写：RTO/RPO、停机窗口、数据增量、第三方 License、等保/合规要求 |
| 术语 | Landing Zone、Availability Zone、SOW、Migration Wave、PCR 不翻译 |
| 计价模式 | 服务包模式默认：**人天/人月仅作能力与工作量评估依据，不作为结算、签到、出勤验收依据** |
| 范围基线 | 以《迁移系统范围清单（调研确认版）》为唯一基线；**同文档内多章节数字必须一致，冲突时写"待确认"并现场核实，不得臆造** |
| 验收 | 核心四条不可省：不以人天为依据 / 以清单+交付物+迁移完成系统数为依据 / 每套系统须验证+完整性+功能+确认割接 / 各模块分别验收互不依赖 |
| 排除项 | 必写，且明确"清单外与范围外须走附录 A PCR 增补" |

## 去 AI 味（硬性）

禁止：赋能、抓手、闭环、一站式、全方位、深度融合；"在当今数字化转型的浪潮中"类空洞开场；每段都以"首先/其次/最后"或"需要注意的是"收尾。

应该：直接给结论和数字；用客户自己的系统名、真实资源量说话。

## 双语规则

- 对外文档**中英双语，分成两个文件**：`SOW_CN.docx` / `SOW_EN.docx`
- 英文版不是逐句直译，按英文商务习惯重写，去掉中文版客套与铺垫

## 输入缺失行为

### 交互模式

缺项目信息或评估报告 → 要求先跑 `mig-project-intake` / `mig-resource-assessment`；语言要求未定 → 默认中文。

### 无头模式（不得反问，逐输入预定义）

按 `输入参数` 逐项一行，**没有缺失分支的输入 = 未定义行为，禁止执行**。

| 输入项 | 缺失时行为 | 处置 | 阻塞 | 降级产物 | 置信度 |
|---|---|---|---|---|---|
| 资源评估报告 | 终止并升级 | 第 2/5/6 章无数据支撑 | 是 | 升级包 | 不产出 |
| 项目信息表 | 终止并升级 | 第 1/11 章无依据 | 是 | 升级包 | 不产出 |
| 交付语言要求 | 降级继续 | 默认中文单语 `CN` | 否 | SOW_CN | −0 |
| 客户匿名要求 | 降级继续 | 默认匿名 `xx customer` | 否 | SOW（匿名） | −0 |
| 所选模板文件缺失（服务包模式或技术方案模式） | 终止并升级 | 章节结构无唯一出处，构成断链 | 是 | 升级包 | 不产出 |
| `references/real_sow_yuanjing.md` 缺失（仅服务包模式） | 降级继续 | 条款口径无事实源，按模板自带要点写 | 否 | SOW（服务包） | −0.1 |
| 报价（商务章） | 降级继续 | 写「报价另附 / 金额留白」，不自行计算 | 否 | SOW（商务章待补） | −0.1 |
| 交付模式未明示（服务包 / 技术方案） | 降级继续 | 默认服务包模式，首段写明计价口径 | 否 | SOW（服务包） | −0 |

## 输出双形态

### 结构化 JSON

```json
{
  "skill": "mig-sow-generator",
  "project": "",
  "language": "CN | EN | BOTH",
  "chapters": [{"no": 1, "title": "", "status": "outline | full", "word_count": 0}],
  "anonymized": true,
  "pending_confirm": [],
  "conclusion": "",
  "confidence": 0.0,
  "confidence_reason": "",
  "suggested_actions": [],
  "escalation": {
    "required": false,
    "reason": "",
    "ruled_out": [],
    "remaining_hypotheses": [],
    "first_checks": [],
    "chain": {
      "leaf_skill": "mig-sow-generator",
      "step": "",
      "state_at_escalation": ""
    }
  }
}
```

### 人类可读

- **交付前必过闸门**：`doc-audit-gate`（去 AI 味 + 事实红线 + 色系合规），PASS 才允许发客户
- Markdown 版：`~/cloud-docs/delivery/<项目>/sow/SOW_CN.md`
- docx 版：`~/cloud-docs/delivery/<项目>/sow/SOW_CN.docx` — 由 `scripts/build_docx.py` 生成，不在正文手敲 python-docx

## 升级契约

**触发**：
- **置信度 < 0.6**（任意降级累计扣分后）→ 升级，不交付产物
- **风险等级与授权不匹配**：本次任务要求调用任何 create/update/delete 类云 API，超出本 skill `风险等级`（只读）与租户授权范围 → 立即终止并升级
- **工具不可用**：所选模板文件缺失（构成断链）或 `scripts/build_docx.py` 执行失败 → 升级
- 无头模式缺评估报告或项目信息
- 客户范围存在根本分歧（迁什么系统没谈拢）
- 涉及需法务/商务确认的条款（违约金、SLA 承诺等级）

**升级包三要素**（缺一不可，同时进 JSON 的 `escalation` 对象）：

- `ruled_out` — 已排除了什么：如已确认非模板问题、已排除客户范围分歧（客户已书面确认迁移边界）
- `remaining_hypotheses` — 剩余哪些假设：如剩余假设为停机窗口 4 小时、数据日增 2%
- `first_checks` — 建议人先看哪里（最多三条）：① 确认评估报告是否已落盘；② 确认第 14 章报价是否已由 `mig-quotation` 产出；③ 确认客户名是否可公开

**升级前必做**：14 章中已写实的章号列出，依赖未确认输入的章号列出，逐条写进升级包。

## 红线

- 不编造人员、证书、案例、客户名（匿名用 `xx customer`）
- 不自行计算报价；商务章只引用 `mig-quotation` 的产出
- 事实源 `references/real_sow_yuanjing.md` 只复用结构与条款口径；**客户名、文档编号、人天数字、第三方厂商名不得带入任何新客户文档**
- 交付物落 `~/cloud-docs/delivery/<项目>/sow/`

## 引用（不复制）

- 14 章骨架与商务口径 → `workbuddy-rules` / `references/selling.md`
- 迁移方法论 → `workbuddy-rules` / `references/cloud-msp.md`
- 模板 → `templates/SOW模板_服务包模式.md`（默认） / `templates/SOW模板.md`（技术方案）
- 服务包模式事实源 → `references/real_sow_yuanjing.md`
