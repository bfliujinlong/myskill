#!/usr/bin/env python3
"""明道云工时确认单核查脚本"""

import json
import sys
import os
from datetime import datetime, timedelta
from collections import defaultdict

def load_pages(files):
    all_rows = []
    for f in files:
        if not os.path.exists(f):
            print(f"[WARN] {f} not found, skip")
            continue
        with open(f, 'r', encoding='utf-8') as fh:
            data = json.loads(fh.read())
            if isinstance(data, str):
                data = json.loads(data)
            for row_id, cells in data.items():
                row = {}
                for col_id, val in cells.items():
                    row[int(col_id)] = val
                all_rows.append(row)
    return all_rows

def audit(rows, title=""):
    if not rows:
        return "没有数据"

    num_cols = max(max(r.keys()) for r in rows) if rows else 0

    col_map = {}
    for i in range(1, num_cols + 1):
        vals = [r.get(i, '') for r in rows[:5] if r.get(i, '')]
        col_map[i] = ','.join(vals[:3])

    issues = []
    summary = defaultdict(float)
    people = defaultdict(float)
    projects = defaultdict(float)

    for idx, r in enumerate(rows):
        vals = [r.get(i, '') for i in range(num_cols + 1)]

        def has_val(*indices):
            for i in indices:
                if i < len(vals) and vals[i].strip():
                    return True
            return False

        def get_val(*indices):
            for i in indices:
                if i < len(vals) and vals[i].strip():
                    return vals[i].strip()
            return ''

        name = get_val(1, 2)
        date = get_val(2, 3)
        status = get_val(0, 1, 4)
        project = get_val(4, 5, 6)
        work_hours = get_val(5, 6, 7)

        try:
            hours = float(work_hours) if work_hours else 0
        except:
            hours = 0

        if name and hours > 0:
            people[name] += hours
            summary['total'] += hours
            if project:
                projects[f"{name}_{project}"] += hours

        if '确认中' in status and hours == 0:
            issues.append(('R3', f"行{idx+1}: {name} 工时=0 但状态=确认中"))

        if hours > 0 and '周末' in status:
            d = None
            try:
                d = datetime.strptime(date, '%Y-%m-%d')
            except:
                pass
            if d and d.weekday() >= 5:
                issues.append(('R1', f"行{idx+1}: {name} 周末({date})报{hours}h"))

    md = []
    md.append(f"# 工时确认单核查报告")
    if title:
        md.append(f"**单据**: {title}")
    md.append("")
    md.append(f"**总工时**: {summary['total']:.1f}h = {summary['total']/8:.1f}人日")
    md.append("")

    md.append("## 按人汇总")
    md.append("| 人员 | 工时(h) | 人日 |")
    md.append("|------|---------|------|")
    for name, h in sorted(people.items(), key=lambda x: -x[1]):
        md.append(f"| {name} | {h:.1f} | {h/8:.1f} |")
    md.append("")

    if issues:
        md.append("## 风险点")
        md.append("| 规则 | 问题 |")
        md.append("|------|------|")
        for rule, desc in issues:
            md.append(f"| {rule} | {desc} |")
        md.append("")

    md.append("## 说明")
    md.append("- R1=周末工时, R3=0小时确认中")
    md.append("- 如需R2(调休)判定，请参考 references/holiday_2026.md")

    return '\n'.join(md)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('files', nargs='+', help='page JSON files')
    parser.add_argument('-o', '--output', default='report.md')
    parser.add_argument('--title', default='')
    args = parser.parse_args()

    rows = load_pages(args.files)
    report = audit(rows, args.title)

    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(report)

    print(report)
    print(f"\n✅ 报告已保存: {args.output}")
