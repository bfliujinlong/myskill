#!/usr/bin/env python3
"""把报价单 Markdown 表格转成 xlsx 交付件。

用法:
    python3 xlsx_from_md.py 报价_CN.md -o 报价_CN.xlsx
    python3 xlsx_from_md.py 报价_CN.md --brand alibaba -o 报价_阿里.xlsx
    python3 xlsx_from_md.py 报价_CN.md            # 默认同目录同名 .xlsx

规则:
    - 解析 md 中的表格（| 分隔），每个表格写成一个 sheet
    - 首个表格作为主表（sheet 名 主表），其余按出现次序命名 表2/表3...
    - 表格外的段落按标题层级写入"说明" sheet
    - --brand 指定厂家色系：表头底/表头字色/正文字色取自 brand-doc-kit 的
      brand_profiles（色值单一事实源，禁止此处硬编码）
      省略 --brand 时为中性灰表头（正式投标场景，禁蓝）

退出码: 0 = 成功；2 = 输入不可用
"""
import argparse
import json
import re
import sys
from pathlib import Path

try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill
    from openpyxl.utils import get_column_letter
except ImportError:
    print("缺少 openpyxl，请先 pip install openpyxl", file=sys.stderr)
    sys.exit(2)

# 中性（正式投标/无厂家归属）：深灰表头，禁蓝
NEUTRAL = {
    "primary": "333333",
    "text": "333333",
    "table_shade": "D9D9D9",
    "table_shade_text": "000000",
    "label": "黑灰",
}

# kit 的 brand_profiles 是色值单一事实源；此处只读，不复制色值
PROFILE_DIR = (Path(__file__).resolve().parent.parent.parent
               / "brand-doc-kit" / "brand_profiles")
VALID_BRANDS = ("alibaba", "tencent", "anchnet", "aws", "azure")


def load_brand(name: str):
    """读取厂家色系；返回 dict。未指定厂家时返回中性灰。"""
    if name in (None, "", "blackgray", "default", "neutral"):
        return dict(NEUTRAL)
    if name not in VALID_BRANDS:
        raise SystemExit(
            f"未知 brand: {name}（可选：{'/'.join(VALID_BRANDS)} 或省略走中性灰）")
    p = PROFILE_DIR / f"{name}.json"
    if not p.exists():
        raise SystemExit(f"缺少色系文件: {p}（kit 品牌色单一事实源缺失）")
    d = json.loads(p.read_text(encoding="utf-8"))
    return {
        "primary": d.get("primary", NEUTRAL["primary"]),
        "text": d.get("text", NEUTRAL["text"]),
        "table_shade": d.get("table_shade", d.get("primary")),
        "table_shade_text": d.get("table_shade_text", "FFFFFF"),
        "label": d.get("label", name),
    }


def parse_md(path: Path):
    """返回 (tables, notes)：tables 为二维列表，notes 为 (标题, 正文) 列表。"""
    lines = path.read_text(encoding="utf-8").splitlines()
    tables = []
    notes = []
    cur = []
    buf = []
    for ln in lines:
        if ln.lstrip().startswith("|") and ln.rstrip().endswith("|"):
            if buf:
                notes.append("\n".join(buf).strip())
                buf = []
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
                continue  # 分隔行
            cur.append(cells)
        else:
            if cur:
                tables.append(cur)
                cur = []
            if ln.strip():
                buf.append(ln.strip())
    if cur:
        tables.append(cur)
    if buf:
        notes.append("\n".join(buf).strip())
    return tables, notes


def write_sheet(ws, rows, brand=None):
    for r in rows:
        ws.append(r)
    if not rows:
        return
    b = brand or dict(NEUTRAL)
    head_fill = PatternFill("solid", fgColor=b["table_shade"])
    head_font = Font(bold=True, color=b["table_shade_text"])
    body_font = Font(color=b["text"])
    for c in range(1, len(rows[0]) + 1):
        ws.cell(row=1, column=c).font = head_font
        ws.cell(row=1, column=c).fill = head_fill
    for ri in range(2, len(rows) + 1):
        for ci in range(1, len(rows[ri - 1]) + 1):
            ws.cell(row=ri, column=ci).font = body_font
    for ci in range(1, len(rows[0]) + 1):
        width = max((len(str(r[ci - 1])) for r in rows if len(r) > ci - 1),
                    default=8)
        ws.column_dimensions[get_column_letter(ci)].width = min(width * 1.6 + 2, 40)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("md")
    ap.add_argument("-o", "--out", default=None)
    ap.add_argument("--brand", default="blackgray",
                    help="厂家色系：alibaba/tencent/anchnet/aws/azure；省略=中性灰（正式投标）")
    args = ap.parse_args()

    src = Path(args.md)
    if not src.exists():
        print(f"文件不存在: {src}", file=sys.stderr)
        return 2
    out = Path(args.out) if args.out else src.with_suffix(".xlsx")

    tables, notes = parse_md(src)
    if not tables:
        print(f"未在 {src} 中找到任何 Markdown 表格", file=sys.stderr)
        return 2

    brand = load_brand(args.brand)
    wb = Workbook()
    ws = wb.active
    ws.title = "主表"
    write_sheet(ws, tables[0], brand)
    for i, t in enumerate(tables[1:], start=2):
        write_sheet(wb.create_sheet(f"表{i}"), t, brand)
    if notes:
        ns = wb.create_sheet("说明")
        for n in notes:
            ns.append([n])

    out.parent.mkdir(parents=True, exist_ok=True)
    wb.save(out)
    print(f"已生成 {out}（{len(tables)} 个表，色系 {brand['label']}，"
          f"表头 {brand['table_shade']}）", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
