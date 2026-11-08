#!/usr/bin/env python3
"""把 SOW Markdown 转成 docx 交付件。

用法:
    python3 build_docx.py SOW_CN.md -o SOW_CN.docx                 # 默认黑灰（投标口径）
    python3 build_docx.py SOW_CN.md --brand alibaba -o SOW_阿里.docx
    python3 build_docx.py SOW_CN.md --brand tencent -o SOW_腾讯.docx

--brand 取值:
    blackgray（默认，投标/技术标黑灰口径）
    alibaba 阿里橙 / anchnet 安畅红 / tencent 腾讯蓝 / aws AWS黑 / azure Azure浅蓝

版式约定:
    - 正文中文宋体 / 英文 Calibri，标题黑体加粗
    - 默认配色仅黑灰（#000000 / #333333 / #D9D9D9），不出现蓝色
    - 指定 brand 时按 brand_profiles/<brand>.json 取厂家品牌色（色值均来自真实厂家文档提取）
    - H1 = 章标题（14pt），H2 = 二级标题（12pt），正文 10.5pt
    - md 表格转成 docx 表格，表头底色 + 加粗

退出码: 0 = 成功；2 = 输入不可用或缺少依赖
"""
import argparse
import json
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
SHADE_TEXT = RGBColor(0x00, 0x00, 0x00)   # 表头文字色
FONT_CN, FONT_HEAD_CN, FONT_EN = "宋体", "黑体", "Calibri"

PROFILE_DIR = Path(__file__).resolve().parent.parent / "brand_profiles"


def load_brand(name: str):
    """按厂家名加载品牌色系 profile，返回解析后的配色字典。"""
    pf = PROFILE_DIR / f"{name}.json"
    if not pf.exists():
        raise SystemExit(f"未找到品牌 profile: {pf}（可用: "
                         + ", ".join(x.stem for x in sorted(PROFILE_DIR.glob('*.json'))) + "）")
    d = json.loads(pf.read_text(encoding="utf-8"))
    return {
        "ink": RGBColor.from_string(d.get("text", "333333")),
        "head": RGBColor.from_string(d.get("heading", "000000")),
        "shade": d.get("table_shade", "D9D9D9"),
        "shade_text": RGBColor.from_string(d.get("table_shade_text", "000000")),
        "font_cn": d.get("font_cn", "宋体"),
        "font_head_cn": d.get("font_head_cn", "黑体"),
        "font_en": d.get("font_en", "Calibri"),
        "label": d.get("label", name),
    }


def apply_brand(brand: str):
    """把品牌 profile 套用到模块级配色常量；blackgray 保持默认黑灰。"""
    global INK, HEAD, SHADE, SHADE_TEXT, FONT_CN, FONT_HEAD_CN, FONT_EN
    if brand in (None, "", "blackgray", "default"):
        return "黑灰（投标口径）"
    b = load_brand(brand)
    INK, HEAD = b["ink"], b["head"]
    SHADE, SHADE_TEXT = b["shade"], b["shade_text"]
    FONT_CN, FONT_HEAD_CN, FONT_EN = b["font_cn"], b["font_head_cn"], b["font_en"]
    return b["label"]


def set_font(run, name_cn=None, name_en=None, size=10.5,
             bold=False, color=None):
    name_cn = name_cn or FONT_CN
    name_en = name_en or FONT_EN
    color = color or INK
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


def head_shade(cell):
    """表头单元格：底色 SHADE + 文字色 SHADE_TEXT（深色底用白字）。"""
    shade(cell)
    for p in cell.paragraphs:
        for r in p.runs:
            r.font.color.rgb = SHADE_TEXT
            r.font.bold = True


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
                            head_shade(cell)
            continue
        # 标题
        m = re.match(r"^(#{1,4})\s+(.*)$", ln)
        if m:
            lvl, text = len(m.group(1)), m.group(2).strip()
            size = {1: 14, 2: 12, 3: 11, 4: 10.5}[lvl]
            p = doc.add_heading(level=min(lvl, 4))
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            run = p.add_run(text)
            set_font(run, name_cn=FONT_HEAD_CN, size=size, bold=True, color=HEAD)
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
    ap.add_argument("--brand", default="blackgray",
                    help="alibaba/anchnet/tencent/aws/azure/blackgray(默认)")
    args = ap.parse_args()

    label = apply_brand(args.brand)
    print(f"色系: {label}", file=sys.stderr)

    src = Path(args.md)
    if not src.exists():
        print(f"文件不存在: {src}", file=sys.stderr)
        return 2
    out = Path(args.out) if args.out else src.with_suffix(".docx")

    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(10.5)
    style.element.rPr.rFonts.set(qn("w:eastAsia"), FONT_CN)

    parse_and_build(src, doc)
    out.parent.mkdir(parents=True, exist_ok=True)
    doc.save(out)
    print(f"已生成 {out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
