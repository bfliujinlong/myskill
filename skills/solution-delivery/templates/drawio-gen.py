#!/usr/bin/env python3
"""drawio-gen.py - 生成标准 draw.io (.drawio) 架构图文件。

用法:
  python3 drawio-gen.py OUTPUT.drawio --title "系统架构" \
    --nodes "用户层:web:客户/渠道" "接入层:lb:SLB" "应用层:app:微服务" "数据层:db:MySQL" \
    --edges "用户层->接入层" "接入层->应用层" "应用层->数据层"

节点格式: 名称:形状:说明
  形状: web | lb | app | db | cloud | storage | queue | fw | default
边格式:   源名称->目标名称  (源/目标须是已定义的节点名)
"""
import argparse
import html
import xml.sax.saxutils as su

SHAPES = {
    "web":     ("rounded=1;whiteSpace=wrap=0;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;", 160, 60),
    "lb":      ("rounded=1;whiteSpace=wrap=0;html=1;fillColor=#d5e8d4;strokeColor=#82b366;", 160, 60),
    "app":     ("rounded=1;whiteSpace=wrap=0;html=1;fillColor=#ffe6cc;strokeColor=#d79b00;", 160, 60),
    "db":      ("shape=cylinder3;whiteSpace=wrap=0;html=1;fillColor=#f8cecc;strokeColor=#b85450;size=10;", 120, 80),
    "cloud":   ("shape=cloud;whiteSpace=wrap=0;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;", 160, 100),
    "storage": ("shape=cylinder3;whiteSpace=wrap=0;html=1;fillColor=#fff2cc;strokeColor=#d6b656;size=8;", 120, 80),
    "queue":   ("shape=mxgraph.flowchart.delay;whiteSpace=wrap=0;html=1;fillColor=#fff2cc;strokeColor=#d6b656;", 140, 60),
    "fw":      ("rounded=0;whiteSpace=wrap=0;html=1;fillColor=#f5f5f5;strokeColor=#666666;dashed=1;", 160, 60),
    "default": ("rounded=1;whiteSpace=wrap=0;html=1;fillColor=#ffffff;strokeColor=#333333;", 160, 60),
}


def esc(s: str) -> str:
    return su.escape(s)


def parse_node(s: str):
    parts = s.split(":", 2)
    name = parts[0].strip()
    shape = parts[1].strip() if len(parts) > 1 else "default"
    desc = parts[2].strip() if len(parts) > 2 else ""
    return name, shape, desc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("output")
    ap.add_argument("--title", default="系统架构")
    ap.add_argument("--nodes", nargs="*", default=[])
    ap.add_argument("--edges", nargs="*", default=[])
    ap.add_argument("--cols", type=int, default=4, help="每行节点数(自动分层布局)")
    args = ap.parse_args()

    nodes = [parse_node(n) for n in args.nodes]
    # 自动分层：按出现顺序从左到右，每 cols 个换行
    layout = {}
    x0, y0, gx, gy = 40, 120, 220, 180
    for i, (name, shape, desc) in enumerate(nodes):
        col = i % args.cols
        row = i // args.cols
        layout[name] = (x0 + col * gx, y0 + row * gy)

    cells = []
    # 标题
    cells.append(
        f'<mxCell id="title" value="{esc(args.title)}" style="text;html=1;fontSize=18;fontStyle=1;align=center;" vertex="1" parent="1">'
        f'<mxGeometry x="40" y="40" width="600" height="40" as="geometry"/></mxCell>'
    )
    # 节点
    for name, shape, desc in nodes:
        style, w, h = SHAPES.get(shape, SHAPES["default"])
        x, y = layout[name]
        label = name + (f"\\n({desc})" if desc else "")
        cells.append(
            f'<mxCell id="n_{esc(name)}" value="{esc(label)}" style="{style}" vertex="1" parent="1">'
            f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>'
        )
    # 边
    for ei, e in enumerate(args.edges):
        if "->" not in e:
            continue
        src, dst = e.split("->", 1)
        src, dst = src.strip(), dst.strip()
        if src in layout and dst in layout:
            cells.append(
                f'<mxCell id="e{ei}" value="" style="endArrow=classic;html=1;" edge="1" parent="1" '
                f'source="n_{esc(src)}" target="n_{esc(dst)}">'
                f'<mxGeometry relative="1" as="geometry"/></mxCell>'
            )

    mxgraph = (
        '<mxGraphModel dx="800" dy="600" grid="1" gridSize="10" guides="1" tooltips="1" '
        'connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="850" pageHeight="1100" '
        'math="0" shadow="0">'
        '<root>'
        '<mxCell id="0"/>'
        '<mxCell id="1" parent="0"/>'
        + "".join(cells) +
        '</root></mxGraphModel>'
    )
    drawio = (
        '<!DOCTYPE html>\n<mxGraphModel'
        ' xmlns="http://www.jgraph.com/mxgraph"'
        ' xmlns:mx="http://www.jgraph.com/mxgraph" as="model">'
        + mxgraph + '</mxGraphModel>\n'
    )
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(drawio)
    print(f"[ok] 已生成 draw.io 文件: {args.output}  (节点 {len(nodes)} 个, 边 {len(args.edges)} 条)")


if __name__ == "__main__":
    main()
