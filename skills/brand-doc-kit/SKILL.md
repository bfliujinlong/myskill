---
name: brand-doc-kit
description: >
  厂家色系文档工具包：为报价单 / HLD / LLD / 投标技术标 生成「厂家品牌色 + 厂家专有服务名口径」的变体文档并渲染 docx。
  使用当用户说"按厂家出模板""阿里橙/腾讯蓝/AWS黑/Azure浅蓝文档""厂家风格方案""给客户出报价单/HLD/LLD/技术标"时激活。
  色值与服务名的单一事实源；不做内容编写（内容归各上游 skill）。
version: 2026-10-31.001
status: active
allowed-tools: Read, Write, Bash
---

# 厂家色系文档工具包（brand-doc-kit）

**定位**：只管「皮肤 + 厂家专有口径」，不管内容。内容由 `mig-quotation` / `pcs-hld` / `mig-lld` /
`ms-technical-proposal` 产出，本 kit 负责套厂家色系、补厂家服务名基线、渲染 docx、开箱核验。

## 为什么存在

同一份 HLD 给阿里云客户和给 AWS 客户，不能只是换配色——服务名、迁移工具、验收口径、IaC 工具全都不同。
把「骨架」和「厂家事实」分离，写一次骨架出 5 份变体，避免人工复制粘贴时漏改服务名（串用会直接被脚本拦下）。

## 色系表（事实源，色值取自真实厂家文档提取，非臆造）

| 厂家 | `--brand` | 主色 | 表头底 | 正文 | 证据 |
|---|---|---|---|---|---|
| 阿里云 | `alibaba` | `FF6A00` | `FF6A00`+白字 | `222222` | AIOPS_报价单_阿里橙.docx ×6 |
| 腾讯云 | `tencent` | `3370FF` | `3370FF`+白字 | `222222` | 腾讯云迁移题库.docx ×3 |
| 安畅（中立/默认） | `anchnet` | `C00000` | `C00000`+白字 | `222222` | AIOPS_报价单_安畅红.docx ×6 |
| AWS | `aws` | `232F3E` | `232F3E`+白字 | `333333` | 官方 Navy（用户拍板） |
| Azure | `azure` | `00477F` | `9CB9D8`浅蓝+黑字 | `222222` | Cabot_China_Azure_HLD.docx ×30/×9 |
| 正式投标技术标 / 无厂家 | 省略（默认 blackgray） | `333333`/`000000` | `D9D9D9` | `333333` | AGENTS.md：投标禁蓝 |

**选型口径**：有厂家归属就用厂家色；中立 / 无明确厂家回退**安畅红**；正式投标技术标默认黑灰禁蓝
（仅当甲方明确指定厂家生态时才用厂家变体）。

**排除项（项目色 ≠ 品牌色）**：拳头游戏 `FF0000`/`181818`（Riot 项目色）；MCD AWS LZ `C00000`（项目色）；
AWS 三个 pptx 扫 theme+slideMaster+slide 均无品牌色（`475569`/`1E293B` 是中性灰）。

## 用法（三步）

```bash
SK=~/.hermes/skills; KIT=$SK/mig-std/brand-doc-kit; PY=/home/ubuntu/.hermes/hermes-install/venv/bin/python3

# 1 取变体模板骨架（4 类 × 5 厂家 = 20 份，已预生成在 templates/）
$PY $KIT/scripts/build_variant.py --type hld --brand aws -o /tmp/HLD_AWS.md
$PY $KIT/scripts/build_variant.py --type quotation --all -o /tmp/q/   # 一次出 5 个厂家

# 2 填内容后渲染 docx
$PY $KIT/scripts/build_docx.py /tmp/HLD_AWS.md --brand aws -o /tmp/HLD_AWS.docx

# 3 开箱核验（色值 / 附录E / 服务名串用 / 差异度）
$PY $KIT/scripts/verify_brand_variants.py
```

`--type` 取值：`quotation`（报价单）/ `hld` / `lld` / `bid`（投标技术标）。

## 服务交付阶段对位（RFP → 报价 → 合同 → 方案 → 实施 → 运维）

| 阶段 | 文档类型 | `--type` | 上游 skill |
|---|---|---|---|
| 调研 / 报价 | 报价单 | `quotation` | `mig-quotation` / `pcs-quotation` |
| 方案 | HLD | `hld` | `pcs-hld` |
| 方案落地 | LLD | `lld` | `mig-lld` |
| 投标 / 合同 | 投标技术标 | `bid` | `ms-technical-proposal` |
| 合同范围 | SOW | （已有 5 套） | `mig-sow-generator` |

## 目录结构

```
brand_profiles/          # 5 份色系 profile（色值 + 证据，单一事实源）
scripts/
  build_docx.py          # md → docx，--brand 套色（SOW 通过软链接复用本文件）
  build_variant.py       # 生成厂家变体 md（骨架 + 附录 E）
  vendor_kb.py           # 厂家专有基线：8 大域 × 5 厂家 + 工具/验收/商务/IaC
  verify_brand_variants.py  # 开箱核验：色值/附录E/串用/差异度
templates/               # 20 份预生成变体（4 类 × 5 厂家）
```

## 维护纪律

- **色值**只改 `brand_profiles/*.json`，且必须写 `evidence`（来源文件 + 命中次数）；禁止在别处硬编码色值。
- **服务名**只改 `scripts/vendor_kb.py`，按厂家官方写法，不臆造不翻译（ECS / OSS / CEN / RAM 保持原文）。
- 新增厂家：加 profile + 加 `vendor_kb` 条目（8 域必填齐）→ 跑 `build_variant.py --all` → 跑 `verify_brand_variants.py`。
- `DMS` / `Organizations` 是跨厂家真同名词，文中必须带厂家或全名前缀消歧，否则核验判串用。

## 闸门

所有变体出稿前必过 `mig-std/doc-audit-gate`：
去 AI 味 40 / 事实红线 40 / 版式色系 20；≥90 PASS，红线（虚构人员·证书·案例、金额臆造、
占位符残留、数字跨章冲突、RACI 缺位）任一命中即 **BLOCK**，催也不放。
模板骨架用 `--template` 豁免占位符（当前 20 份 92–96 分全 PASS）。
