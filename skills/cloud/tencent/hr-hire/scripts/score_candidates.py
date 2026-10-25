#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
score_candidates.py — 按统一口径给多份简历打分并排序，输出评分卡 Markdown。

用法:
    python score_candidates.py candidates.json > scorecard.md
    python score_candidates.py candidates.json --out scorecard.md

输入 JSON 结构:
{
  "position": "高级数据开发工程师（P6）",
  "rubric": [
    {"name": "硬性门槛", "weight": 30, "gate": true},
    {"name": "经验匹配", "weight": 25},
    {"name": "技能深度", "weight": 20},
    {"name": "项目复杂度", "weight": 15},
    {"name": "稳定性",   "weight": 10}
  ],
  "candidates": [
    {
      "name": "候选人 A",
      "source": "内推",
      "gate_pass": true,
      "gate_note": "",
      "scores": [
        {"name": "硬性门槛", "score": 30, "evidence": "本科（计算机）；6 年经验"},
        {"name": "经验匹配", "score": 18, "evidence": "2 个跨云迁移项目，TB 级"},
        {"name": "技能深度", "score": 15, "evidence": "精通 Spark/Trino/Hive"},
        {"name": "项目复杂度", "score": 10, "evidence": "负责实施，未任方案负责人"},
        {"name": "稳定性", "score": 5, "evidence": "近 5 年 3 段，1 段不足 8 个月"}
      ],
      "concerns": ["2024-03 至 2024-10 空档期原因", "期望薪资高于带宽上限"]
    }
  ]
}

规则:
    - gate 维度不达标（gate_pass=false）时不计总分，单独列出
    - 每个维度没有 evidence 时告警，提示补证据
    - 权重合计不为 100 时自动归一化
"""

import argparse
import json
import sys
from pathlib import Path


def render(doc):
    rubric = doc["rubric"]
    weights = {d["name"]: d.get("weight", 0) for d in rubric}
    total_weight = sum(weights.values()) or 100
    gate_names = [d["name"] for d in rubric if d.get("gate")]

    passed, gated = [], []
    for cand in doc["candidates"]:
        scores = {s["name"]: s for s in cand.get("scores", [])}
        raw = sum(s.get("score", 0) for s in scores.values())
        final = round(raw / total_weight * 100, 1)
        row = {"cand": cand, "raw": raw, "final": final, "scores": scores}
        (gated if (gate_names and cand.get("gate_pass") is False) else passed).append(row)

    passed.sort(key=lambda r: r["final"], reverse=True)

    lines = []
    lines.append("# 候选人评分卡")
    lines.append("")
    lines.append("**岗位**：%s" % doc.get("position", "未填写"))
    lines.append("")
    lines.append("**评分维度**：" + "、".join(
        "%s（%s%%, %s）" % (d["name"], d.get("weight", 0), "一票否决" if d.get("gate") else "评分")
        for d in rubric))
    lines.append("")

    lines.append("## 一、排序总表")
    lines.append("")
    lines.append("| 排名 | 候选人 | 来源 | 匹配分 | 建议 | 关键短板 |")
    lines.append("| --- | --- | --- | --- | --- | --- |")
    for i, row in enumerate(passed, start=1):
        cand = row["cand"]
        suggestion = ("进入面试" if row["final"] >= 75
                      else "进入初筛电话" if row["final"] >= 60
                      else "备选" if row["final"] >= 45
                      else "不通过")
        weak = min(cand.get("scores", []), key=lambda s: s.get("score", 0)) if cand.get("scores") else None
        weak_txt = "%s %s/%s" % (weak["name"], weak.get("score", 0), weights.get(weak["name"], "-")) if weak else "-"
        lines.append("| %d | %s | %s | %.1f | %s | %s |" % (
            i, cand.get("name", "-"), cand.get("source", "-"), row["final"], suggestion, weak_txt))
    lines.append("")

    if gated:
        lines.append("## 二、不满足硬性门槛（不计总分）")
        lines.append("")
        for row in gated:
            cand = row["cand"]
            lines.append("- **%s**（%s）：%s" % (
                cand.get("name", "-"), cand.get("source", "-"),
                cand.get("gate_note") or "未说明"))
        lines.append("")

    lines.append("## 三、逐人明细")
    lines.append("")
    for row in passed + gated:
        cand = row["cand"]
        lines.append("### %s  %s" % (cand.get("name", "-"), cand.get("source", "")))
        lines.append("")
        lines.append("**匹配分：%.1f / 100**" % row["final"])
        lines.append("")
        lines.append("| 维度 | 权重 | 得分 | 证据 |")
        lines.append("| --- | --- | --- | --- |")
        for d in rubric:
            s = row["scores"].get(d["name"])
            if not s:
                lines.append("| %s | %s | 缺失 | ⚠️ 未评分 |" % (d["name"], d.get("weight", 0)))
                continue
            ev = s.get("evidence") or "⚠️ 无证据"
            lines.append("| %s | %s | %s | %s |" % (
                d["name"], d.get("weight", 0), s.get("score", 0),
                str(ev).replace("|", "\\|")))
        lines.append("")
        concerns = cand.get("concerns") or []
        if concerns:
            lines.append("**存疑点（面试需核实）**")
            lines.append("")
            for j, c in enumerate(concerns, start=1):
                lines.append("%d. %s" % (j, c))
            lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("> 合规提示：评分仅基于与岗位相关的任职条件与可验证证据。")
    lines.append("> 不得记录或评价性别、年龄、婚育、户籍、民族、宗教、外貌等无关信息。")
    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="候选人统一口径评分")
    parser.add_argument("input", help="输入 JSON 文件")
    parser.add_argument("--out", help="输出 Markdown 文件；省略则打印到标准输出")
    args = parser.parse_args()

    path = Path(args.input)
    if not path.exists():
        print(json.dumps({"ok": False, "error": "文件不存在: %s" % path}, ensure_ascii=False))
        sys.exit(1)

    doc = json.loads(path.read_text(encoding="utf-8"))
    if not doc.get("candidates"):
        print(json.dumps({"ok": False, "error": "candidates 为空"}, ensure_ascii=False))
        sys.exit(1)

    text = render(doc)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print("已输出: %s" % args.out)
    else:
        sys.stdout.reconfigure(encoding="utf-8")
        print(text)


if __name__ == "__main__":
    main()
