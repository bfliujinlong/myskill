#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 阶段 02 调研表 driver：按目标云 profile 生成双语调研表（xlsx + md + json）
# 依赖：openpyxl（缺失时降级为只出 md/json，并在输出中显式说明，不静默）
# 红线：不写价格/单价/人天；不虚构资源数据；未核实项写「待确认」
"""mig-survey-table driver.

输入 JSON：
{
  "project": "客户-云迁移项目",
  "source_cloud": "aws",
  "target_cloud": "alicloud",
  "lang": "bilingual",              # zh / en / bilingual
  "client": {"客户名称": "...", "项目名称": "..."},
  "resources": [{"类型": "计算(ECS)", "云厂商": "AWS", "数量": 2}],
  "systems":  [{"系统名": "OA系统", "模块": "用户认证"}],
  "databases":[{"实例名": "oa-mysql-prod", "引擎": "MySQL"}],
  "nfr":      [{"类别": "RTO", "指标": "恢复时间目标", "要求值": "<=4h"}],
  "out_dir": "./out"
}
输出：调研表_{lang}.xlsx / 调研表.md / survey_table.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date

DOMAIN_ORDER = ["网络", "安全", "IAM", "计算", "存储", "数据库", "大数据", "监控运维"]
PROFILE_DEFAULT = os.path.expanduser("~/.hermes/skills/learning/_shared/cloud_profiles")
CLOUD_LABEL = {"alicloud": "阿里云", "aws": "AWS", "azure": "Azure",
               "huawei": "华为云", "oci": "OCI", "gcp": "GCP", "multi": "多云中立"}
TBD = "待确认"

# ---------------------------------------------------------------- 表结构定义
# 表单式 sheet：(key, 中文标题, 英文标题, [(字段中文, 字段英文, 示例/说明中文, 示例/说明英文), ...])
FORM_SHEETS = [
    ("customer", "客户基本信息", "Client Basic Information", [
        ("客户名称 *", "Client Name *", "填写客户公司全称", "Full legal company name"),
        ("项目名称 *", "Project Name *", "项目内部代号/名称", "Internal project code/name"),
        ("联系人姓名", "Contact Person", "项目负责人", "Project owner/lead"),
        ("联系电话", "Phone", "", ""),
        ("电子邮箱", "Email", "", ""),
        ("源云平台 *", "Source Cloud Platform *", "AWS / Azure / 阿里云 / 华为云 / 其他",
         "AWS / Azure / Alibaba Cloud / Huawei Cloud / Other"),
        ("目标云平台 *", "Target Cloud Platform *", "阿里云 / OCI / 其他",
         "Alibaba Cloud / OCI / Other"),
        ("源环境位置", "Source Environment Location", "当前 IT 基础设施所处位置",
         "Current IT infrastructure location"),
        ("迁移类型 *", "Migration Type *", "资源平移 / 容器化改造 / 混合架构",
         "Lift & Shift / Containerization / Hybrid"),
        ("停机窗口 *", "Downtime Window *", "<=48h", "Acceptable downtime"),
        ("业务系统架构图", "Business System Architecture Diagram", "如有请粘贴或另附文件",
         "Paste or attach separately if available"),
        ("目标地域是否已确认 *", "Target region confirmed *", "如 cn-shanghai；未定填「待确认」",
         "e.g. cn-shanghai; write 待确认 if undecided"),
        ("客户是否已有目标云账号", "Client has active target-cloud account", "是 / 否", "Yes / No"),
        ("是否已有目标云服务在使用中", "Existing target-cloud services in use", "列出已有服务（如有）",
         "List existing services if any"),
        ("是否需要多可用区或多地域部署", "Multi-AZ or multi-region deployment required",
         "Multi-AZ / Multi-Region / Both", "Multi-AZ / Multi-Region / Both"),
    ]),
    ("compliance", "合规与安全", "Compliance & Security", [
        ("G1 需要的边界安全防护", "G1 Perimeter security required",
         "WAF / Anti-DDoS / 云防火墙 / 全部", "WAF / Anti-DDoS / Cloud Firewall / All"),
        ("G2 需要的身份和访问管理", "G2 Identity and access management needed",
         "RAM / 堡垒机 / MFA / SSO", "RAM / Bastion / MFA / SSO"),
        ("G3 数据加密标准要求", "G3 Data encryption standards required",
         "AES-256 / 国密 SM4 / TLS 1.3", "AES-256 / SM4 / TLS 1.3"),
        ("G4 合规认证要求", "G4 Compliance certifications needed",
         "ISO27001 / SOC2 / PCI-DSS / 等保三级 / 其他", "ISO27001 / SOC2 / PCI-DSS / Other"),
        ("数据驻留要求", "Data residency requirements", "数据必须驻留的国家/地区",
         "Country/region where data must reside"),
        ("行业监管要求", "Industry regulatory requirements",
         "如 PIPL(中国) / GDPR(欧盟) / PDPL(沙特)", "e.g. PIPL (CN) / GDPR (EU) / PDPL (SA)"),
        ("安全审计频率", "Security audit frequency", "月度 / 季度 / 年度",
         "Monthly / Quarterly / Annual"),
        ("渗透测试要求", "Penetration testing requirements", "年度渗透测试 / 无",
         "Annual pentest / None"),
    ]),
    ("network", "网络与跨云连接", "Network & Cross-Cloud", [
        ("跨云带宽需求", "Cross-cloud bandwidth", "100 Mbps / 1 Gbps",
         "Source-to-target bandwidth"),
        ("专线需求", "Dedicated line requirement", "是 / 否", "Yes / No"),
        ("VPN 需求", "VPN requirement", "是 / 否", "Yes / No"),
        ("可接受网络延迟", "Acceptable network latency", "<=100ms",
         "Source-to-target latency requirement"),
        ("VPC 数量需求", "VPC count required", "需要创建的 VPC 数量", "Number of VPCs to create"),
        ("子网规划", "Subnet planning", "是 / 否", "Yes / No"),
        ("NAT 网关需求", "NAT gateway requirement", "是 / 否", "Yes / No"),
        ("负载均衡需求", "Load balancer requirement", "如 ALB / NLB / 两者都需要",
         "e.g. ALB / NLB / Both"),
        ("CDN 需求", "CDN requirement", "是 / 否", "Yes / No"),
        ("DNS 服务需求", "DNS service requirement", "是 / 否", "Yes / No"),
    ]),
]

# 表格式 sheet：(key, 中文标题, 英文标题, 中文列, 英文列, 输入键, 预置行(中文,英文))
NFR_PRESET = [
    ("RTO", "RTO", "恢复时间目标", "Recovery Time Objective", ""),
    ("RPO", "RPO", "恢复点目标", "Recovery Point Objective", ""),
    ("可用性分档", "Availability", "To Business", "To Business", "面向内部业务系统"),
    ("可用性分档", "Availability", "To Customer", "To Customer", "面向外部客户系统"),
    ("可用性分档", "Availability", "IoT", "IoT", "物联网设备链路"),
    ("可用性分档", "Availability", "基础架构", "Infrastructure", "底层基础架构"),
    ("灾备等级", "DR Tier", "灾备等级", "DR Tier", "Hot / Warm / Cold"),
    ("停机窗口", "Downtime", "可接受停机窗口", "Acceptable Downtime Window", "单次最长停机时间"),
    ("备份策略", "Backup", "备份策略", "Backup Strategy", "全量/增量/差异频率"),
]

TAB_SHEETS = [
    ("resources", "资源清单", "Resource Inventory",
     ["序号", "类型", "云厂商", "区域", "实例规格", "数量", "CPU", "内存(GB)", "存储(GB)",
      "存储类型", "公网带宽(Mbps)", "用途", "标签", "采集时间"],
     ["No.", "Type", "Cloud Provider", "Region", "Instance Type", "Qty", "vCPU", "Memory (GB)",
      "Storage (GB)", "Storage Type", "Public Bandwidth (Mbps)", "Purpose", "Tags", "Collected At"],
     "resources"),
    ("systems", "应用拓扑", "Application Topology",
     ["序号", "系统名", "模块", "依赖上游", "依赖下游", "端口", "协议", "是否核心(P0/P1/P2)",
      "迁移优先级", "备注"],
     ["No.", "System", "Module", "Upstream Dependency", "Downstream Dependency", "Port",
      "Protocol", "Criticality (P0/P1/P2)", "Migration Priority", "Notes"],
     "systems"),
    ("databases", "数据库详情", "Database Details",
     ["序号", "实例名", "引擎", "版本", "规格", "存储(GB)", "全量数据量(GB)", "增量日均(GB)",
      "字符集", "高可用模式", "备份策略", "兼容性风险", "采集时间"],
     ["No.", "Instance", "Engine", "Version", "Spec", "Storage (GB)", "Full Data Size (GB)",
      "Daily Increment (GB)", "Charset", "HA Mode", "Backup Policy", "Compatibility Risk",
      "Collected At"],
     "databases"),
    ("nfr", "非功能需求", "Service Level Requirements",
     ["序号", "类别", "指标", "要求值", "说明"],
     ["No.", "Category", "Metric", "Required Value", "Notes"],
     "nfr"),
]

REQUIRED_CLIENT_FIELDS = ["客户名称 *", "项目名称 *", "源云平台 *", "目标云平台 *",
                          "迁移类型 *", "停机窗口 *", "目标地域是否已确认 *"]


def load_input(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    for key in ("project", "target_cloud"):
        if not data.get(key):
            raise ValueError("输入缺少必填字段 %s，无法确定调研口径，终止" % key)
    return data


def load_profile(cloud: str, prof_dir: str):
    """解析 cloud_profiles/{cloud}.md 的 8 域锚点表；文件缺失返回 ({}, 缺失原因)。"""
    path = os.path.join(prof_dir, "%s.md" % cloud)
    if not os.path.exists(path):
        return {}, "profile 文件不存在：%s" % path
    table = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) < 2 or cells[0] not in DOMAIN_ORDER:
                continue
            if set(cells[0]) <= set("-: "):
                continue
            table.setdefault(cells[0], cells[1])
    return table, ""


def bilingual(lang: str, zh: str, en: str) -> str:
    if lang == "zh":
        return zh
    if lang == "en":
        return en
    return "%s / %s" % (zh, en)


def build_rows(data: dict, lang: str) -> tuple:
    """返回 (sheets, coverage)。sheets: [{title, header, rows}]"""
    src = data.get("source_cloud", "")
    tgt = data.get("target_cloud", "")
    src_label = CLOUD_LABEL.get(src, src or TBD)
    tgt_label = CLOUD_LABEL.get(tgt, tgt or TBD)
    client = data.get("client", {}) or {}
    sheets = []

    # 1) 客户基本信息 / 合规 / 网络（表单式）
    for key, tz, te, fields in FORM_SHEETS:
        header = [bilingual(lang, "字段", "Field"),
                  bilingual(lang, "填写内容", "Your Answer"),
                  bilingual(lang, "示例/说明", "Example/Description"),
                  bilingual(lang, "备注", "Notes")]
        rows = []
        for fz, fe, hz, he in fields:
            answer = ""
            if key == "customer":
                answer = client.get(fz, "")
                if not answer and fz == "源云平台 *":
                    answer = src_label
                if not answer and fz == "目标云平台 *":
                    answer = tgt_label
            rows.append([bilingual(lang, fz, fe), answer, bilingual(lang, hz, he), ""])
        sheets.append({"key": key, "title": bilingual(lang, tz, te), "header": header, "rows": rows})

    # 2) 表格式 sheet（预填调用方给的数据；没给就只出表头，不编造示例数据）
    for key, tz, te, cz, ce, input_key in TAB_SHEETS:
        header = cz if lang == "zh" else (ce if lang == "en" else
                                          ["%s / %s" % (a, b) for a, b in zip(cz, ce)])
        rows = []
        if key == "nfr":
            for i, (_cz, _ce, mz, me, note) in enumerate(NFR_PRESET, 1):
                rows.append([i, bilingual(lang, _cz, _ce), bilingual(lang, mz, me), "",
                             bilingual(lang, note, "") if note else ""])
            for item in data.get("nfr", []) or []:
                rows.append([len(rows) + 1, item.get("类别", ""), item.get("指标", ""),
                             item.get("要求值", ""), item.get("说明", "")])
        else:
            for i, item in enumerate(data.get(input_key, []) or [], 1):
                rows.append([i] + [item.get(col, "") for col in cz[1:]])
        sheets.append({"key": key, "title": bilingual(lang, tz, te), "header": header, "rows": rows})

    # 3) 目标云差异 sheet（X 轴适配层）
    src_prof, src_miss = load_profile(src, PROFILE_DEFAULT) if src else ({}, "未声明 source_cloud")
    tgt_prof, tgt_miss = load_profile(tgt, PROFILE_DEFAULT)
    header = [bilingual(lang, "域", "Domain"),
              bilingual(lang, "源端产品锚点", "Source Products"),
              bilingual(lang, "目标产品锚点", "Target Products"),
              bilingual(lang, "调研落点", "Survey Focus"),
              bilingual(lang, "备注", "Notes")]
    rows = []
    for d in DOMAIN_ORDER:
        s = src_prof.get(d, "")
        t = tgt_prof.get(d, "")
        note = ""
        if not t:
            t = TBD
            note = bilingual(lang, "目标云 profile 未取到该域锚点", "anchor missing in target profile")
        rows.append([bilingual(lang, d, d), s or TBD, t, "", note])
    sheets.append({"key": "profile", "title": bilingual(lang, "目标云差异", "Cloud Delta"),
                   "header": header, "rows": rows})

    # 4) 覆盖率：必填项填充统计
    filled = sum(1 for r in sheets[0]["rows"] if str(r[1]).strip())
    coverage = {"required_total": len(REQUIRED_CLIENT_FIELDS),
                "required_filled": sum(1 for r in sheets[0]["rows"]
                                       if r[0].split(" /")[0] in REQUIRED_CLIENT_FIELDS
                                       and str(r[1]).strip()),
                "customer_rows_filled": filled}
    meta = {"src_profile_missing": src_miss, "tgt_profile_missing": tgt_miss,
            "src_label": src_label, "tgt_label": tgt_label}
    return sheets, coverage, meta


def render_md(data: dict, sheets: list, coverage: dict, meta: dict) -> str:
    today = date.today().isoformat()
    lines = ["# %s" % bilingual(data.get("lang", "bilingual"), "云迁移调研表",
                                "Cloud Migration Survey"),
             "",
             "| 字段 | 值 |", "|---|---|",
             "| 项目 | %s |" % data.get("project", ""),
             "| 源云 | %s |" % meta["src_label"],
             "| 目标云 | %s |" % meta["tgt_label"],
             "| 生成日期 | %s |" % today,
             "| 必填项填充 | %d/%d |" % (coverage["required_filled"], coverage["required_total"]),
             ""]
    if meta["src_profile_missing"]:
        lines.append("> 源云 profile：%s" % meta["src_profile_missing"])
    if meta["tgt_profile_missing"]:
        lines.append("> 目标云 profile：%s" % meta["tgt_profile_missing"])
    lines.append("")
    for sh in sheets:
        lines += ["## %s" % sh["title"], "",
                  "| " + " | ".join(sh["header"]) + " |",
                  "|" + "|".join(["---"] * len(sh["header"])) + "|"]
        if sh["rows"]:
            for r in sh["rows"]:
                lines.append("| " + " | ".join("" if v is None else str(v) for v in r) + " |")
        else:
            lines.append("| " + " | ".join(["（待填写）"] + [""] * (len(sh["header"]) - 1)) + " |")
        lines.append("")
    lines += ["> 本表不含价格、单价、人天与月费信息（与报价物理隔离）。",
              "> 未核实项一律标注「待确认」，不得虚构资源、人员与案例。"]
    return "\n".join(lines) + "\n"


def write_xlsx(path: str, data: dict, sheets: list) -> str:
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        from openpyxl.utils import get_column_letter
    except ImportError as exc:  # 明确说明降级原因，不静默
        return "xlsx 未生成：缺少 openpyxl（%s）。已输出 md/json，可 pip 安装后重跑。" % exc

    DARK = "404040"
    GRAY = "D9D9D9"
    LIGHT = "F2F2F2"
    hf = PatternFill("solid", start_color=DARK, end_color=DARK)
    hfont = Font(bold=True, color="FFFFFF", size=11)
    tfont = Font(bold=True, size=12, color=DARK)
    border = Border(*[Side(style="thin", color=GRAY)] * 4)
    align = Alignment(vertical="center", wrap_text=True)

    wb = Workbook()
    ws = wb.active
    ws.title = "填写说明" if data.get("lang", "bilingual") != "en" else "Instructions"
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=4)
    c = ws.cell(row=1, column=1, value=bilingual(data.get("lang", "bilingual"),
                                                 "云迁移调研表 — 填写说明",
                                                 "Cloud Migration Survey — Instructions"))
    c.font = tfont
    notes = [
        bilingual(data.get("lang", "bilingual"), "1. 带 * 号为必填项；不适用请填 N/A",
                  "1. Fields marked * are required; enter N/A if not applicable"),
        bilingual(data.get("lang", "bilingual"), "2. 请先填「客户基本信息」，再按表顺序填写",
                  "2. Fill in Client Basic Information first, then follow sheet order"),
        bilingual(data.get("lang", "bilingual"), "3. 未核实的内容请填「待确认」，不要留空猜测",
                  "3. Write 待确认 for unverified items; never guess"),
        bilingual(data.get("lang", "bilingual"), "4. 本表不含价格、单价、人天与月费信息",
                  "4. This sheet contains no pricing, unit price, man-day or monthly fee"),
        bilingual(data.get("lang", "bilingual"), "5. 完成后返回项目经理，团队将在 3 个工作日内反馈",
                  "5. Return to the PM; feedback within 3 business days"),
    ]
    for i, n in enumerate(notes, 3):
        ws.cell(row=i, column=1, value=n).alignment = align
    ws.column_dimensions["A"].width = 60

    for sh in sheets:
        s = wb.create_sheet(sh["title"][:31])
        for i, h in enumerate(sh["header"], 1):
            cell = s.cell(row=1, column=i, value=h)
            cell.font = hfont
            cell.fill = hf
            cell.alignment = align
            cell.border = border
        for ri, row in enumerate(sh["rows"], 2):
            for ci, v in enumerate(row, 1):
                cell = s.cell(row=ri, column=ci, value=v)
                cell.border = border
                cell.alignment = align
                if ri % 2 == 0:
                    cell.fill = PatternFill("solid", start_color=LIGHT, end_color=LIGHT)
        for ci in range(1, len(sh["header"]) + 1):
            s.column_dimensions[get_column_letter(ci)].width = 22 if ci > 1 else 26
        s.freeze_panes = "A2"
    wb.save(path)
    return ""


def self_test() -> int:
    sample = {
        "project": "自检项目", "source_cloud": "aws", "target_cloud": "alicloud",
        "lang": "bilingual",
        "client": {"客户名称 *": "自检客户", "项目名称 *": "自检项目"},
        "resources": [{"类型": "计算(ECS)", "云厂商": "AWS", "区域": "ap-southeast-1",
                       "实例规格": "t3.large", "数量": 2}],
        "systems": [{"系统名": "OA系统", "模块": "用户认证", "依赖上游": "LDAP"}],
        "databases": [{"实例名": "oa-mysql-prod", "引擎": "MySQL", "版本": "5.7"}],
        "nfr": [{"类别": "RTO", "指标": "恢复时间目标", "要求值": "<=4h"}],
    }
    sheets, coverage, meta = build_rows(sample, "bilingual")
    md = render_md(sample, sheets, coverage, meta)
    assert len(sheets) == 8, "sheet 数应为 3 表单 + 4 表格 + 1 profile，实际 %d" % len(sheets)
    assert not meta["tgt_profile_missing"], "alicloud profile 应存在，不应缺失"
    prof_sheet = [s for s in sheets if s["key"] == "profile"][0]
    assert all(r[2] != TBD for r in prof_sheet["rows"]), "alicloud 8 域锚点应全部取到"
    assert coverage["required_filled"] >= 4, "目标云/源云/客户名/项目名应计入已填，实际 %d" % coverage["required_filled"]
    assert "不含价格" in md, "红线声明必须出现在 md 中"
    # 未声明 source_cloud 时不得编造源端锚点
    s2, _, m2 = build_rows({"project": "x", "target_cloud": "oci", "lang": "zh"}, "zh")
    assert m2["src_profile_missing"], "未声明 source_cloud 时必须记录缺失原因"
    print("[self-test] sheets=%d 必填=%d/%d MD=%dB" % (
        len(sheets), coverage["required_filled"], coverage["required_total"], len(md.encode())))
    print("[self-test] PASS")
    return 0


def main() -> int:
    global PROFILE_DEFAULT
    ap = argparse.ArgumentParser(description="mig-survey-table driver（阶段 02 调研表）")
    ap.add_argument("--input", help="输入 JSON 路径")
    ap.add_argument("--out-dir", default=".", help="输出目录")
    ap.add_argument("--profile-dir", default=PROFILE_DEFAULT, help="cloud_profiles 目录")
    ap.add_argument("--self-test", action="store_true", help="内置自检")
    args = ap.parse_args()
    if args.profile_dir:
        PROFILE_DEFAULT = args.profile_dir

    if args.self_test:
        return self_test()
    if not args.input:
        print("ERROR: 需指定 --input 或 --self-test", file=sys.stderr)
        return 2

    try:
        data = load_input(args.input)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print("ERROR: 读取输入失败：%s" % exc, file=sys.stderr)
        return 2

    lang = data.get("lang", "bilingual")
    if lang not in ("zh", "en", "bilingual"):
        print("ERROR: lang 仅支持 zh / en / bilingual，实际 %s" % lang, file=sys.stderr)
        return 2

    sheets, coverage, meta = build_rows(data, lang)
    md = render_md(data, sheets, coverage, meta)
    os.makedirs(args.out_dir, exist_ok=True)

    paths = {}
    mdp = os.path.join(args.out_dir, "调研表.md")
    with open(mdp, "w", encoding="utf-8") as fh:
        fh.write(md)
    paths["调研表.md"] = mdp

    xnote = ""
    if data.get("xlsx", True):
        xp = os.path.join(args.out_dir, "调研表_%s.xlsx" % lang)
        xnote = write_xlsx(xp, data, sheets)
        if not xnote:
            paths["xlsx"] = xp

    missing_required = [r[0].split(" /")[0] for r in sheets[0]["rows"]
                        if r[0].split(" /")[0] in REQUIRED_CLIENT_FIELDS and not str(r[1]).strip()]
    payload = {
        "conclusion": "可发出" if not missing_required else "待补充必填项后发出",
        "confidence": "高" if (not missing_required and not meta["tgt_profile_missing"]) else "低",
        "suggested_action": "补齐必填项后发客户填写" if missing_required else
                            "发给客户填写，回收后走 mig-resource-assessment / alibabacloud-migration-survey",
        "escalation_reason": ("目标云 profile 缺失：%s" % meta["tgt_profile_missing"])
                             if meta["tgt_profile_missing"] else "",
        "sheets": [{"key": s["key"], "title": s["title"], "rows": len(s["rows"])} for s in sheets],
        "coverage": coverage,
        "missing_required": missing_required,
        "profile": {"source": meta["src_label"], "target": meta["tgt_label"],
                    "source_missing": meta["src_profile_missing"],
                    "target_missing": meta["tgt_profile_missing"]},
        "artifacts": paths,
        "notes": xnote,
    }
    jp = os.path.join(args.out_dir, "survey_table.json")
    with open(jp, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    print("OK sheets=%d 必填=%d/%d 结论=%s -> %s%s" % (
        len(sheets), coverage["required_filled"], coverage["required_total"],
        payload["conclusion"], jp, (" | " + xnote) if xnote else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
