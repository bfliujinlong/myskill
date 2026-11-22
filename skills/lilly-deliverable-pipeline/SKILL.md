---
name: lilly-deliverable-pipeline
display_name: Lilly 交付物与 HLD/LLD 流水线
description: "Lilly AIOps/AliSCP 项目交付物生产流水线：把圆桌共识（R1–Rn 红线）与仿真/设计过程增量并入 HLD/LLD，生成黑灰禁蓝的 docx/pptx，并把设计流程沉淀为可复用资产。当用户处理 Lilly 项目的 HLD/LLD、圆桌增订并入、SOW/报价/docx 生成、交付物版本谱系或设计过程归档时激活。"
icon: "📐"
trigger: Lilly HLD LLD 圆桌增订 交付物 docx 报价 SOW 设计过程
patterns:
  - pattern: "(?i)Lilly.*(HLD|LLD|AIOps|AliSCP)"
    confidence: 0.9
  - pattern: "(圆桌|增订|R[1-9]).*(HLD|LLD|并入|红线)"
    confidence: 0.85
  - pattern: "(PM04|PM05|D0[1-9]|D1[0-8]).*(docx|pptx|交付)"
    confidence: 0.8
inputs:
  - name: input_sources
    description: "输入源：基线文档版本表 + 圆桌纪要/增订稿路径 + 仿真结论"
    type: path
    required: true
  - name: target_doc
    description: "目标交付物：HLD(Codex md) 或 LLD(Codex md) 或 SOW/报价"
    type: string
    required: true
  - name: output_dir
    description: "交付物落盘目录"
    type: path
    default: "客户项目/Lilly_AIOps/02_项目方案/codex/Lilly_AIOps_实现包_2026-11-14/deliverables"
depends-on: [cloud-migration-pm]
scripts: [gen_lld_v11.py, _style.py]
---

# Lilly 交付物与 HLD/LLD 流水线

## Overview
把 Lilly 项目的设计过程固化为可重复执行的流水线。核心原则来自 `cloud-migration-pm` 的「HLD 先行 → 评审通过 → LLD 细化」，并叠加本项目特有的**圆桌红线增量并入**机制：新共识不重写全文，而是先列 R1–Rn 冲突清单，再精确改文 + 新增章节，保持版本谱系可追溯。

配色遵循投标规范：**黑/灰/安畅红 C00000，禁蓝**；docx 标题用 Word 内置标题样式（可出导航窗格/目录），中文绑定 `w:eastAsia` 微软雅黑。

## Workflow

### Step 1: 输入源与基线确认
- **Mode**: `agentic`
- **Input**: SOW / 圆桌纪要 / 增订稿 / 仿真结论 / 品牌模板
- **Output**: 输入源版本表（来源、用途、状态：已并入/参考/待并入）
- **关键**: 先确认基线版本与权威源，避免基于过期 V1.0 改文档。参考 `references/版本谱系.md`。
- **Validate**: 每个输入源都能定位到文件与日期。
- **On failure**: 缺权威源则停在「待确认」，不猜测。

### Step 2: 冲突清单显式化（R1–Rn）
- **Mode**: `agentic`
- **Input**: 圆桌共识/红线 + 基线文档现有表述
- **Output**: 冲突表（# / 现有表述 / 红线共识 / 修订动作 / 落点）
- **关键**: 先列全冲突再改文档；每条红线必须对应一个落点章节。
- **Validate**: 红线数量与落点数量一一对应。

### Step 3: HLD 先行，评审通过才出 LLD
- **Mode**: `agentic`
- **Input**: 五层架构 / 四场景 / 红线对照 / 集成点
- **Output**: HLD Codex 合并稿（md）
- **关键**: HLD 只做概要层（本期/路线图分界、角色权限、治理、审计），细节留给 LLD。
- **Validate**: HLD 含红线对照表且一票否决项均为「未触发」。

### Step 4: LLD 增量合并
- **Mode**: `agentic`
- **Input**: HLD + LLD V1.0 基线 + 冲突清单
- **Output**: LLD Codex 合并稿（md），含精确改文段 + 新增章节全文
- **关键**: 「精确改文」写清原文→改后文；新增章节带接口契约与代码证据，不虚构接口。
- **Validate**: 每条 R 都有落点；准确率 SLA 措辞标注「内部验收口径，非对外 SLA」。

### Step 5: Markdown → docx 生成
- **Mode**: `script`
- **Input**: Codex 合并稿 + `_style.py`
- **Output**: 黑灰禁蓝 docx，内置标题样式
- **关键**: 复用 `_style.py`（new_doc/set_doc_fonts/cover/para/bullet/add_table）；⚠️ `_style.BASE` 指向已过时的旧目录，**新脚本必须显式指定输出路径**（见 `scripts/gen_lld_v11.py`）。图片缺失降级为占位说明，不阻断生成。
- **Validate**: 用 python-docx 读回——标题样式为 `Heading N`、关键章节齐全、蓝色 run = 0。

### Step 6: 报价 CN/EN 同步（如涉及）
- **Mode**: `script`
- **Input**: WBS 人天 + 费率口径
- **Output**: 中英双语报价单分文件
- **关键**: WBS 是报价硬前提；单一数据源（`aia_quote_model.json`），脚本重算校验；双费率禁混（AC-MIG `$350/人天` vs AIA ¥费率二选一）。⚠️ 已知坑：历史 `aia_quote_model.json` 与文档金额曾不一致，复用前必校验。

### Step 7: 红线闸门自检
- **Mode**: `agentic`
- **Input**: 生成的交付物
- **Output**: 一票否决项逐条结论
- **关键**: 禁删 / 不自动改生产 / 双人四眼 / RWD SELECT-only / HITL / 不虚构人员案例 / 零费用。任一触发即驳回。
- **Validate**: 对照 `references/红线清单.md` 逐条 Pass。

### Step 8: 编号落盘 + 记忆回写
- **Mode**: `agentic`
- **Input**: 交付物 + 设计决策
- **Output**: 按 D01–D18 / PM01–PM10 编号落盘；高频事实写 memory
- **关键**: 记忆只写「决策/约束/路径/口径」，禁写「已生成/已交付」日志。详见 `references/记忆回写规范.md`。

## Output
- HLD/LLD Codex 合并稿（md，可追溯设计过程）
- 黑灰禁蓝 docx/pptx（内置标题样式、导航窗格/自动目录可用）
- 版本谱系表 + 红线自检结论

## Lessons Learned

### Do
- 先列 R1–Rn 冲突清单再改文档，保持增量可追溯。
- HLD 评审通过再出 LLD；接口参数取自仿真/handbook 真实契约。
- docx 用内置 Heading 样式 + `w:eastAsia`，禁用手动加粗大字号。
- 复用共享样式层 `_style.py`，一交付物一生成脚本，输出到 deliverables。

### Don't
- 不直接改 V1.0 全文而不留冲突清单（丢失设计过程）。
- 不用 `_style.BASE`（过时路径），必须显式指定 OUT。
- 不把「准确率≥80%」「RTO/RPO 具体值」写成对外 SLA 承诺。
- 不把生产自处置重启/规格变更写成「本期自动执行」。
- 不虚构人员/案例/指标；不写「已交付 XX」类记忆日志。

### Common Failures
- `_style.py` 的 BASE 指向 `客户项目/Lilly_AIOps/AgentCore_Scenario_Design`（不存在）→ 生成失败或写入错目录。
- `aia_quote_model.json` 与文档金额不一致（127000 vs 127050）→ 复用前必校验单一数据源。
- 圆桌增订稿长期停在「待并入」→ HLD/LLD 与共识脱节（本 skill 就是为此而建）。

### When to Ask
- 首次告警场景 SOP（R-003）、AAD 最终组名、审计保留期、准确率阈值——这些必须客户确认，标注「待确认」不自行给定。
