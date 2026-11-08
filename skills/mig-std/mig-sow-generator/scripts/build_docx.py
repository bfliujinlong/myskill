#!/usr/bin/env python3
"""把 SOW Markdown 转成 docx 交付件（黑灰版式，禁蓝）。

用法:
    python3 build_docx.py SOW_CN.md -o SOW_CN.docx

版式约定（投标/技术标口径）:
    - 正文中文宋体 / 英文 Calibri，标题黑体加粗
    - 配色仅黑灰（#000000 / #333333 / #595959 / #D9D9D9），不出现蓝色
    - H1 = 章标题（14pt），H2 = 二级标题（12pt），正文 10.5pt
    - md 表格转成 docx 表格，表头灰底加粗

退出码: 0 = 成功；2 = 输入不可用或缺少依赖
"""
import argparse
import re
import sys
from pathlib import Path

try:
    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml.ns import qn
    from docx.shared import Pt, RGBColor
except ImportError:
    print("缺少 python-docx，请先 pip install python-docx", file=sys.stderr)
    sys.exit(2)

INK = RGBColor(0x33, 0x33, 0x33)      # 正文深灰
HEAD = RGBColor(0x00, 0x00, 0x00)     # 标题纯黑
SHADE = "D9D9D9"                      # 表头灰底


def set_font(run, name_cn="宋体", name_en="Calibri", size=10.5,
             bold=False, color=INK):
    run.font.name = name_en
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run._element.rPr.rFonts.set(qn("w:eastAsia"), name_cn)


def shade(cell):
    from docx.oxml import OxmlElement
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), SHADE)
    tcPr.append(shd)


def parse_and_build(md_path: Path, doc: Document):
    lines = md_path.read_text(encoding="utf-8").splitlines()
    i = 0
    while i < len(lines):
        ln = lines[i].rstrip()
        # 表格块
        if ln.lstrip().startswith("|"):
            block = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
                    block.append(cells)
                i += 1
            if block:
                t = doc.add_table(rows=len(block), cols=len(block[0]))
                t.style = "Table Grid"
                for r, row in enumerate(block):
                    for c in range(min(len(row), len(block[0]))):
                        cell = t.cell(r, c)
                        cell.text = ""
                        p = cell.paragraphs[0]
                        run = p.add_run(row[c])
                        set_font(run, size=9.5, bold=(r == 0))
                        if r == 0:
                            shade(cell)
            continue
        # 标题
        m = re.match(r"^(#{1,4})\s+(.*)$", ln)
        if m:
            lvl, text = len(m.group(1)), m.group(2).strip()
            size = {1: 14, 2: 12, 3: 11, 4: 10.5}[lvl]
            p = doc.add_heading(level=min(lvl, 4))
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            run = p.add_run(text)
            set_font(run, name_cn="黑体", size=size, bold=True, color=HEAD)
            i += 1
            continue
        # 列表 / 正文
        if ln.strip():
            m2 = re.match(r"^(\s*)[-*]\s+(.*)$", ln)
            text = m2.group(2) if m2 else ln.strip()
            p = doc.add_paragraph(style="List Bullet" if m2 else None)
            run = p.add_run(text)
            set_font(run, size=10.5)
        i += 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("md")
    ap.add_argument("-o", "--out", default=None)
    args = ap.parse_args()

    src = Path(args.md)
    if not src.exists():
        print(f"文件不存在: {src}", file=sys.stderr)
        return 2
    out = Path(args.out) if args.out else src.with_suffix(".docx")

    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(10.5)
    style.element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")

    parse_and_build(src, doc)
    out.parent.mkdir(parents=True, exist_ok=True)
    doc.save(out)
    print(f"已生成 {out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
