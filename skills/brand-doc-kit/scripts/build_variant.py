#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""按厂家色系 + 厂家专有口径，生成报价单 / HLD / LLD / 投标技术标 的变体 Markdown。

设计意图：写骨架一次，5 个厂家各自一份变体文档，避免人工复制粘贴时漏改服务名。
骨架与厂家事实分离——骨架在 build_skeleton() 里，厂家事实全在 vendor_kb.VENDOR_KB。

用法:
    python3 build_variant.py --type quotation --brand alibaba -o /tmp/q_阿里橙.md
    python3 build_variant.py --type hld --all -o /tmp/hld/     # 一次出 5 个厂家
    python3 build_variant.py --type lld --brand aws --no-appendix

退出码: 0 = 成功；2 = 参数/输出不可用
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vendor_kb as kb  # noqa: E402

PROFILE_DIR = Path(__file__).resolve().parent.parent / "brand_profiles"


# ---------------------------------------------------------------- 骨架：报价单
def skel_quotation(v, brand):
    return f"""# {{{{客户名}}}} {{{{项目名}}}} {kb.DOC_TYPES['quotation']['title']}（{v['label']}）

> 色系皮肤：`--brand {brand}`（渲染时由 `scripts/build_docx.py` 套用 {v['vendor']} 品牌色）

> 版本：v{{{{N}}}} ｜ 日期：{{{{date}}}} ｜ 币种：{{{{CNY|USD}}}}
> 单价基准：$350/人天（AC-MIG）｜ 有效期：{{{{30}}}} 天
> 目标云：**{v['vendor']}**
> 状态：{{{{draft|final}}}}

---

## 一、计价假设

| 项 | 取值 | 来源 |
|---|---|---|
| 单价（人天） | $350 | AC-MIG 基准 |
| 目标云 | {v['vendor']} | 项目信息表 |
| 项目类型 | {{{{新建/迁移/改造}}}} | 项目信息表 |
| 复杂度系数 | {{{{1.0 / 1.2 / 1.5}}}} | 评估报告 |
| 多区域标志 | {{{{是/否}}}} | 项目信息表 |
| 异构数据库标志 | {{{{是/否}}}} | 评估报告 |
| 交付语言 | {{{{中/英/双语}}}} | 项目信息表 |

> 未确认项一律不臆造，列入「五、待确认清单」。

## 二、角色 × 人天明细

| # | 角色 | 工作内容 | 人天 | 单价 | 小计 |
|---|---|---|---|---|---|
| 1 | {{{{角色}}}} | {{{{内容}}}} | {{{{n}}}} | 350 | {{{{n×350}}}} |
| … | | | | | |
| | **合计** | | **{{{{总人天}}}}** | | **{{{{总金额}}}}** |

> 角色池：PM · 云架构师 · 云工程师（计算及存储）· 迁移工程师（中间件）· 数据库工程师 · 大数据工程师 · 安全架构师 · {{{{专项实施方}}}}团队

## 三、加计项

| 项 | 触发条件 | 加计比例 | 金额 |
|---|---|---|---|
| 多区域 | 跨 ≥2 地域 | {{{{}}}} | |
| 异构数据库 | 跨引擎迁移 | {{{{}}}} | |
| 风险储备 | 复杂度 ≥1.2 | {{{{}}}} | |

## 四、总计

| 项 | 金额 |
|---|---|
| 人天小计 | {{{{}}}} |
| 加计合计 | {{{{}}}} |
| **合同金额** | **{{{{}}}}** |

> 校验：人天 × 单价 = 小计，各行小计之和 = 总计。
> 执行 `scripts/validate_quote.py` 自动校验，失败不得出稿。

## 五、待确认清单

- [ ] RTO / RPO
- [ ] 停机窗口
- [ ] 数据增量
- [ ] 第三方 License
- [ ] 等保 / 合规要求
- [ ] 目标地域与可用区清单

## 六、不含项

- 云资源费用（由甲方与{v['vendor']}侧直接结算）
- 第三方软件 License
- 甲方人员配合成本
- 超出约定轮次的方案返工
"""


# ------------------------------------------------------------------- 骨架：HLD
def skel_hld(v, brand):
    dom_rows = "\n".join(
        f"| {i} | {cn} | 见 {{{{第{i}章}}}} | {{{{设计要点}}}} |"
        for i, (cn, _k) in enumerate(kb.DOMAIN_ORDER, 1)
    )
    dom_chapters = "\n\n".join(
        f"## {i}. {cn}\n\n"
        f"**{i}.1 设计要点**：{v['domains'][key]}\n\n"
        f"**{i}.2 关键组件**：{{{{按 {v['vendor']} 官方服务名填写}}}}\n\n"
        f"**{i}.3 选型理由**：{{{{一句话：为什么是这个，而不是另一个}}}}\n\n"
        f"**{i}.4 待确认**：{{{{依赖甲方提供的信息，没有就写「无」}}}}"
        for i, (cn, key) in enumerate(kb.DOMAIN_ORDER, 1)
    )
    return f"""# {{{{客户名}}}} {{{{项目名}}}} {kb.DOC_TYPES['hld']['title']}（{v['label']}）

> 色系皮肤：`--brand {brand}`（渲染时由 `scripts/build_docx.py` 套用 {v['vendor']} 品牌色）

> 版本：v{{{{N}}}} ｜ 日期：{{{{date}}}} ｜ 密级：L2-内部级
> 目标云：**{v['vendor']}** ｜ 状态：{{{{draft|final}}}}
> 输入事实源：`pcs-factsheet` 结构化 facts（目标云未定时先走 `pcs-arch-selection`）

---

## 0. 设计原则与总体架构

**0.1 设计原则**：{{{{≤6 条，每条一句话，禁止排比堆砌}}}}
**0.2 总体架构**：{{{{一段话叙述：源端 → 目标端的分区与关键路径}}}}
**0.3 领域覆盖一览**

| # | 领域 | 章节 | 设计结论（一句话） |
|---|---|---|---|
{dom_rows}

> 8 大领域一一对应 `pcs-hld` 判据；任一领域留空即为未完成。

{dom_chapters}

## 9. 高可用与容灾

**9.1 可用性目标**：{{{{SLA / RTO / RPO，未确认写「待确认」}}}}
**9.2 容灾策略**：{{{{同城多 AZ / 异地灾备，按 {v['vendor']} 服务实现}}}}

## 10. 成本与优化

**10.1 资源清单与费用估算**：{{{{引用 mig-sizeng-advice / pcs-lz-estimate 输出}}}}
**10.2 优化建议**：{{{{预留实例 / 存储分层 / 闲置回收}}}}

## 11. 待确认清单

- [ ] 目标地域与可用区
- [ ] 合规框架（等保 / ISO27001 / SOC2 等）
- [ ] 网络互联方式与带宽
- [ ] 数据与驻留要求
"""


# ------------------------------------------------------------------- 骨架：LLD
def skel_lld(v, brand):
    return f"""# {{{{客户名}}}} {{{{项目名}}}} {kb.DOC_TYPES['lld']['title']}（{v['label']}）

> 色系皮肤：`--brand {brand}`（渲染时由 `scripts/build_docx.py` 套用 {v['vendor']} 品牌色）

> 版本：v{{{{N}}}} ｜ 日期：{{{{date}}}} ｜ 密级：L2-内部级
> 目标云：**{v['vendor']}** ｜ 目标地域：{{{{region}}}}
> 前置：本文件的输入是 HLD（未产出 HLD 时不得启动，参数无法落地）
> 参考域名基线：{v['vendor']}｜账号：{v['domains']['account'][:40]}…｜网络：{v['domains']['network'][:40]}…

---

## 1. 网络拓扑与地址规划

**1.1 地址规划表**

| VPC / VNet | 网段 CIDR | 用途 | 子网 CIDR | 可用区 | 说明 |
|---|---|---|---|---|---|
| {{{{名称}}}} | {{{{10.x.0.0/16}}}} | {{{{生产/测试/共享}}}} | {{{{10.x.1.0/24}}}} | {{{{az-a}}}} | |

**1.2 路由表**：{{{{每条写：目标网段 → 下一跳 → 说明}}}}
**1.3 互联**：{{{{专线 / VPN / 云联网，按 {v['vendor']} 服务实现}}}}
**1.4 安全组 / 防火墙规则矩阵**

| 源 | 目的 | 端口 | 协议 | 动作 | 依据 |
|---|---|---|---|---|---|

> 规则必须有依据列；写「全通 / 0.0.0.0/0 全放」须注明甲方书面确认。

## 2. 计算实例规格表

| 主机名 | 用途 | 实例规格 | vCPU | 内存 | 系统盘 | 数据盘 | 数量 |
|---|---|---|---|---|---|---|---|
| {{{{}}}} | | {{{{按目标地域实际可购买清单}}}} | | | | | |

> **规格真实性红线**：{v['spec_hint']}

## 3. 数据库规格表

| 实例名 | 引擎与版本 | 规格 | 存储 | 高可用 | 备份策略 | 备注 |
|---|---|---|---|---|---|---|

## 4. 存储设计

| 存储类型 | 容量 | 访问模式 | 生命周期 | 加密 |
|---|---|---|---|---|

> 参考基线（{v['vendor']}）：{v['domains']['storage']}

## 5. 安全与合规清单

| # | 检查项 | 基线要求 | 当前状态 | 责任人 |
|---|---|---|---|---|

> 参考基线（{v['vendor']}）：{v['domains']['security']}
> 身份与访问：{v['domains']['iam']}

## 6. 监控与告警配置

| 监控对象 | 指标 / 日志源 | 阈值 | 告警级别 | 通知方式 |
|---|---|---|---|---|

> 参考基线（{v['vendor']}）：{v['domains']['monitor']}

## 7. 部署步骤（IaC）

- 编排工具：**{v['iac']}**
- 目录结构：{{{{modules / environments / variables}}}}
- 执行顺序：{{{{网络 → 安全 → 计算 → 数据 → 监控}}}}
- 回滚方式：{{{{按栈销毁 / 版本回退}}}}

> 部署步骤里的资源规格必须人工核对是否真实存在（模板值与 Mock 值常见）。

## 8. 待确认清单

- [ ] 网段与甲方现网是否冲突
- [ ] 实例规格在目标地域的可购买性
- [ ] 数据库版本兼容性
- [ ] 安全规则例外项
"""


# ---------------------------------------------------------------- 骨架：技术标
def skel_bid(v, brand):
    return f"""# {{{{客户名}}}} {{{{项目名}}}} {kb.DOC_TYPES['bid']['title']}（{v['label']}）

> 色系皮肤：`--brand {brand}`
> **默认口径**：正式投标以黑灰（`--brand blackgray`，禁蓝）为准；本变体仅在甲方明确指定
> {v['vendor']} 生态 / 或招标文件要求体现厂家风格时使用。

> 版本：v{{{{N}}}} ｜ 日期：{{{{date}}}} ｜ 密级：L2-内部级
> 数字只从「客户直源 / 待商务确认」取，标源；禁止无源数字与虚构案例。

---

## 01 公司介绍与项目理解

- 1.1 公司核心资质（来源 `company_intro`，资质表 + 说明，**不得虚构证书编号**）
- 1.2 项目背景与痛点理解（客户资产规模 + 强制要求）
- 1.3 方案总体架构（组件 × RFP 对位表 + 关键口径；目标云：**{v['vendor']}**）

## 02 服务范围与责任边界

- 2.1 服务范围（项级目录映射表：服务域 × 条目数 × 角色 × 案例佐证）
- 2.2 Service Catalog 结构（四档 + 条目数）
- 2.3 Run / Build / OOS 分类处理流程
- 2.4 RACI 责任矩阵（拆甲方侧角色）
- 2.5 服务边界管理（排除项 + 范围变化走 PCR）

## 03 服务水平与运营保障

- 3.1 事件分级定义（P1-P4）
- 3.2 SLA / SLO 承诺（分项 + 定性 + 关键指标节选）
- 3.3 War Room 应急响应（启动条件 / 角色 / 执行流程）
- 3.4 事件管理（全生命周期 + 技术 / 管理升级矩阵）
- 3.5 问题管理（RCA 五步 + 三层根因 + 时限）
- 3.6 变更管理（分类 + 流程 + 度量）
- 3.7 监控与告警（工具 + 介入链路）
- 3.8 备份与 DR（DR-SLA 分级）

## 04 运营组织与服务协同

- 4.1 服务组织架构
- 4.2 团队配置（角色画像表）
- 4.3 升级路径（技术 / 管理双轨）
- 4.4 服务能力持续性（备份 / 知识 / 复盘）

## 05 Mobilization 与服务接管

- 5.1 双轨并行交接（Infra + Security）
- 5.2 里程碑（M0-M5）
- 5.3 验收门禁
- 5.4 交接时间轴
- 5.5 交接事项清单
- 5.6 Transition 风险管理

## 06 工具平台与技术方案（{v['vendor']} 专有基线）

- 6.1 工具清单（全量复用表）
- 6.2 ITSM 集成
- 6.3 告警介入链路
- 6.4 FinOps
- 6.5 AI 赋能
- 6.6 **目标云技术基线**：{v['domains']['compute'][:50]}…；IaC 工具：**{v['iac']}**

## 07 持续改进、安全与合规

- 7.1 CSI 闭环与案例（脱敏两段式，不构成本项目承诺）
- 7.2 安全合规运营（{v['domains']['security'][:40]}…）

## 08 治理体系与报告

- 8.1 治理会议矩阵
- 8.2 报告体系

## 09 云厂商合作与持续演进

- 9.1 云厂商合作（与目标云：{v['vendor']}）
- 9.2 Landing Zone 与持续演进

## 附录 A：RFP 要求全量追溯矩阵

| 编号 | RFP 要求（摘要） | 方案章节 | 关键交付物 |
|---|---|---|---|

## 附录 B：覆盖率自检（四维）

```
In-Scope 项数 / 目录映射 / 案例佐证 / RFP 追溯率 / 叙事完整度 / 图示
```

---

## 硬约束速查

1. 数字只从「客户直源 / 待商务确认」取，标源；
2. 丰满 = 已确证事实的展开度，不引入无源数字；
3. 案例两段式；图只画已锚定条目；
4. 内部痕迹不外泄；不虚构人员 / 证书 / 案例（废标风险）。

> 门禁：对外交付前跑 `merge_chapters.py --strict [--rfp-count R]`，四维全 PASS 才可出稿；
> 再过 `doc-audit-gate`（去 AI 味 + 事实红线 + 版式色系）。
"""


SKELS = {
    "quotation": skel_quotation,
    "hld": skel_hld,
    "lld": skel_lld,
    "bid": skel_bid,
}


def appendix_e(v, brand):
    """生成「附录 E 厂家专有口径」，四类事实全部来自 vendor_kb。"""
    tools = "\n".join(f"- {t}" for t in v["migration_tools"])
    acc = "\n".join(f"- {t}" for t in v["acceptance"])
    biz = "\n".join(f"- {t}" for t in v["commercial"])
    prof = json.loads((PROFILE_DIR / f"{brand}.json").read_text(encoding="utf-8"))
    return f"""
---

## 附录 E {v['vendor']}专有口径

**E.1 目标端平台基线**（专有服务名按官方写法，不臆造 / 不翻译）

| 领域 | {v['vendor']} 基线 |
|---|---|
""" + "\n".join(
        f"| {cn} | {v['domains'][key]} |" for cn, key in kb.DOMAIN_ORDER
    ) + f"""

**E.2 迁移工具与方式**
{tools}
- IaC / 编排：{v['iac']}

**E.3 验收口径**
{acc}

**E.4 商务口径**
{biz}

**E.5 色系与证据**
- `--brand {brand}` → 主色 `{prof.get('primary')}`，表头底 `{prof.get('table_shade')}`，正文 `{prof.get('text')}`
- 色值来源：{prof.get('evidence', '—')}
"""


def build(doc_type: str, brand: str, with_appendix: bool = True) -> str:
    v = kb.get_vendor(brand)
    body = SKELS[doc_type](v, brand)
    if with_appendix:
        body += appendix_e(v, brand)
    return body


def main() -> int:
    ap = argparse.ArgumentParser(description="生成厂家色系文档变体 md")
    ap.add_argument("--type", required=True, choices=sorted(SKELS),
                    help="文档类型：quotation/hld/lld/bid")
    ap.add_argument("--brand", choices=kb.BRAND_ORDER, help="厂家 key")
    ap.add_argument("--all", action="store_true", help="一次生成 5 个厂家")
    ap.add_argument("--no-appendix", action="store_true", help="不附厂家专有口径附录")
    ap.add_argument("-o", "--out", required=True, help="输出文件或目录")
    args = ap.parse_args()

    if not args.all and not args.brand:
        ap.error("需要 --brand 或 --all")

    brands = kb.BRAND_ORDER if args.all else [args.brand]
    out = Path(args.out)
    if args.all:
        out.mkdir(parents=True, exist_ok=True)
    elif out.parent != Path(""):
        out.parent.mkdir(parents=True, exist_ok=True)

    for b in brands:
        content = build(args.type, b, not args.no_appendix)
        if args.all:
            fp = out / f"{kb.DOC_TYPES[args.type]['suffix']}_{kb.get_vendor(b)['label']}.md"
        else:
            fp = out
        fp.write_text(content, encoding="utf-8")
        print(f"已生成 {fp}（{len(content)} 字符）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
