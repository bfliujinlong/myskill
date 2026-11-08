#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 项目复盘（阶段 06）driver：经验教训 -> 复盘报告 + 知识库回写清单
# stdlib only；只产出文档与回写建议，不自动改任何文件
"""mig-retro driver.

输入 JSON：
{
  "project": "客户名-项目名",
  "phase": "全周期",
  "acceptance_signed": true,
  "metrics": {"计划工期(天)": 90, "实际工期(天)": 102},
  "lessons": [{"category": "做得差", "what": "...", "root_cause": "...", "owner": "...", "due_date": "..."}]
}
输出：项目复盘报告.md / 知识库回写清单.md / retro.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date

CATEGORIES = ["做得好", "做得差", "改进项"]

# 各分类的知识库回写动作模板（建议目标路径，需人工确认）
KB_ACTION = {
    "做得好": {"action": "沉淀为可复用资产", "target": "01服务流程/（模板 / checklist）"},
    "做得差": {"action": "补红线或前置检查项", "target": "相关 skill 的「红线」/「常见陷阱」章节"},
    "改进项": {"action": "纳入改进待办并跟踪", "target": "项目改进 backlog（按季度回顾）"},
}


def load_input(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    for key in ("project", "phase"):
        if key not in data:
            raise ValueError("输入缺少必填字段 %s，无法定位复盘范围，终止" % key)
    return data


def normalize(data: dict) -> tuple:
    """按 category 归类并做完整性检查；缺失项标「待确认」并收集升级原因。"""
    grouped = {c: [] for c in CATEGORIES}
    unknown = []
    gaps = {"missing_root_cause": [], "missing_owner": [], "missing_due_date": []}
    for i, item in enumerate(data.get("lessons", []) or [], start=1):
        cat = str(item.get("category", "")).strip()
        if cat not in CATEGORIES:
            unknown.append({"index": i, "category": cat or "空"})
            continue
        entry = {
            "no": i,
            "what": str(item.get("what", "")).strip() or "待确认",
            "root_cause": str(item.get("root_cause", "")).strip(),
            "owner": str(item.get("owner", "")).strip(),
            "due_date": str(item.get("due_date", "")).strip(),
        }
        if cat == "做得差" and not entry["root_cause"]:
            entry["root_cause"] = "根因待分析"
            gaps["missing_root_cause"].append(i)
        if cat == "改进项":
            if not entry["owner"]:
                entry["owner"] = "待确认"
                gaps["missing_owner"].append(i)
            if not entry["due_date"]:
                entry["due_date"] = "待确认"
                gaps["missing_due_date"].append(i)
        grouped[cat].append(entry)
    return grouped, unknown, gaps


def build_writebacks(grouped: dict) -> list:
    """推导知识库回写建议；只给建议路径，明确不自动写入。"""
    out = []
    for cat in CATEGORIES:
        meta = KB_ACTION[cat]
        for e in grouped[cat]:
            out.append({
                "no": e["no"],
                "category": cat,
                "item": e["what"],
                "action": meta["action"],
                "suggested_target": meta["target"],
                "confirm_required": True,
                "note": "需人工确认目标文件后再写入，本 skill 不自动改文件",
            })
    return out


def render(grouped: dict, data: dict, gaps: dict, unknown: list) -> tuple:
    today = str(data.get("retro_date") or date.today().isoformat())
    total = sum(len(v) for v in grouped.values())
    signed = bool(data.get("acceptance_signed"))

    rl = ["# 项目复盘报告", "",
          "| 字段 | 值 |", "|---|---|",
          "| 项目 | %s |" % data["project"],
          "| 复盘范围 | %s |" % data["phase"],
          "| 复盘日期 | %s |" % today,
          "| 条目总数 | %d |" % total,
          "| 验收签字状态 | %s |" % ("已签字" if signed else "**未确认（复盘应在验收签字后进行）**"), ""]

    metrics = data.get("metrics") or {}
    if metrics:
        rl += ["## 0. 项目指标（实测）", "", "| 指标 | 值 |", "|---|---|"]
        for k, v in metrics.items():
            rl.append("| %s | %s |" % (k, v))
        rl.append("")

    headers = {
        "做得好": "## 1. 做得好（保持与推广）",
        "做得差": "## 2. 做得差（含根因）",
        "改进项": "## 3. 改进项（行动计划）",
    }
    for cat in CATEGORIES:
        rl += [headers[cat], ""]
        items = grouped[cat]
        if not items:
            rl += ["（无条目）", ""]
            continue
        if cat == "做得差":
            rl += ["| 序号 | 问题描述 | 根因分析 |", "|---|---|---|"]
            for e in items:
                rl.append("| %d | %s | %s |" % (e["no"], e["what"], e["root_cause"]))
        elif cat == "改进项":
            rl += ["| 序号 | 改进项 | 责任人 | 计划完成日期 |", "|---|---|---|---|"]
            for e in items:
                rl.append("| %d | %s | %s | %s |" % (e["no"], e["what"], e["owner"], e["due_date"]))
        else:
            rl += ["| 序号 | 做法 | 沉淀建议 |", "|---|---|---|"]
            for e in items:
                rl.append("| %d | %s | 沉淀为模板 / checklist |" % (e["no"], e["what"]))
        rl.append("")

    rl += ["## 4. 复盘检查清单回执", "",
           "- [ ] 复盘会已召开",
           "- [ ] 经验教训已记录（做得好 / 做得差 / 改进项）",
           "- [ ] 可复用资产已归档到 `01服务流程/`",
           "- [ ] 项目文档已完整归档", ""]
    if unknown:
        rl += ["> 警告：%d 条条目 category 不在 {做得好/做得差/改进项} 中，已跳过：%s" % (
            len(unknown), "、".join(str(u["index"]) for u in unknown)), ""]
    rl += ["> 本报告不含价格、单价、人天与月费信息；未核实项标「待确认」，不虚构人员与案例。", ""]
    report_md = "\n".join(rl) + "\n"

    wl = ["# 知识库回写清单（需人工确认后执行）", "",
          "| 序号 | 分类 | 条目 | 回写动作 | 建议目标 | 是否已确认 |",
          "|---|---|---|---|---|---|"]
    for w in build_writebacks(grouped):
        wl.append("| %d | %s | %s | %s | %s | 否 |" % (
            w["no"], w["category"], w["item"], w["action"], w["suggested_target"]))
    wl += ["", "> 本清单仅为建议；**写入动作需人工确认**，本 skill 不自动修改任何 skill 或知识库文件。", ""]
    return report_md, "\n".join(wl) + "\n"


def self_test() -> int:
    sample = {
        "project": "自检项目",
        "phase": "全周期",
        "acceptance_signed": True,
        "metrics": {"计划工期(天)": 90, "实际工期(天)": 102},
        "lessons": [
            {"category": "做得好", "what": "调研阶段用只读采集脚本，零生产影响"},
            {"category": "做得差", "what": "割接当晚回滚演练不足", "root_cause": "未做回滚演练"},
            {"category": "做得差", "what": "数据库版本兼容漏测"},
            {"category": "改进项", "what": "割接前强制回滚演练", "owner": "PM", "due_date": "2026-12-31"},
            {"category": "改进项", "what": "版本兼容性前置检查"},
        ],
    }
    grouped, unknown, gaps = normalize(sample)
    report, wb = render(grouped, sample, gaps, unknown)
    assert len(grouped["做得好"]) == 1 and len(grouped["做得差"]) == 2 and len(grouped["改进项"]) == 2
    assert gaps["missing_root_cause"] == [3], "缺根因的条目应被捕获，实际 %s" % gaps["missing_root_cause"]
    assert gaps["missing_owner"] == [5] and gaps["missing_due_date"] == [5]
    assert "根因待分析" in report and "待确认" in report
    print("[self-test] 条目=%d 缺根因=%s 缺owner=%s 报告=%dB 回写清单=%dB" % (
        5, gaps["missing_root_cause"], gaps["missing_owner"],
        len(report.encode()), len(wb.encode())))
    print("[self-test] PASS")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="mig-retro driver（阶段 06 复盘）")
    ap.add_argument("--input", help="输入 JSON 路径")
    ap.add_argument("--out-dir", default=".", help="输出目录")
    ap.add_argument("--self-test", action="store_true", help="内置自检")
    args = ap.parse_args()

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

    grouped, unknown, gaps = normalize(data)
    report_md, wb_md = render(grouped, data, gaps, unknown)

    os.makedirs(args.out_dir, exist_ok=True)
    paths = {}
    for name, content in (("项目复盘报告.md", report_md), ("知识库回写清单.md", wb_md)):
        p = os.path.join(args.out_dir, name)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(content)
        paths[name] = p

    escalation = []
    if gaps["missing_root_cause"]:
        escalation.append("做得差条目 %s 缺根因分析" % gaps["missing_root_cause"])
    if gaps["missing_owner"] or gaps["missing_due_date"]:
        escalation.append("改进项 %s 缺责任人/完成日期" % sorted(
            set(gaps["missing_owner"]) | set(gaps["missing_due_date"])))
    if not data.get("acceptance_signed"):
        escalation.append("验收签字状态未确认（复盘应在验收后进行）")
    if unknown:
        escalation.append("条目 %s 的 category 非法已跳过" % [u["index"] for u in unknown])

    payload = {
        "conclusion": "复盘报告已生成" + ("（含 %d 项升级信息）" % len(escalation) if escalation else ""),
        "confidence": "高" if not escalation else "低",
        "suggested_action": "补齐根因/责任人后进复盘会" if escalation else "召开复盘会并执行归档",
        "escalation_reason": "；".join(escalation),
        "sections": grouped,
        "metrics": data.get("metrics") or {},
        "kb_writebacks": build_writebacks(grouped),
        "checklist": ["复盘会已召开", "经验教训已记录", "可复用资产已归档", "项目文档已归档"],
        "unknown_category_items": unknown,
        "artifacts": paths,
    }
    jp = os.path.join(args.out_dir, "retro.json")
    with open(jp, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    print("OK 条目=%d 升级=%d -> %s" % (
        sum(len(v) for v in grouped.values()), len(escalation), jp))
    return 0


if __name__ == "__main__":
    sys.exit(main())
