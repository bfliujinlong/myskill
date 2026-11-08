#!/usr/bin/env python3
"""merge_chapters.py — 整合分段章节为对外技术方案书，跑四维自检 + 交叉引用检查。

用法:
  python3 merge_chapters.py --dir 技术方案/[项目]/ \
      --output 对外技术方案书-[项目]-v1.0.md \
      [--sla-count 45] [--catalog-count 131] [--role-count 16]

四维自检（coverage_gate）:
  1. 映射覆盖: 章节 02 项级映射表 In-Scope 项 有目录映射 x/N
  2. 佐证覆盖: y/N
  3. RFP 追溯: 附录A 追溯行数 z/R
  4. 叙事完整度: 每章有 How 流程（流程/步骤/触发 关键字）
交叉引用: SLA 条目数 / 目录条目数 / 角色数 与上游一致（可选 --sla-count 等）
"""
import argparse
import os
import re
import sys

ORDER = [
    ("01", "公司介绍与项目理解"),
    ("02", "服务范围与责任边界"),
    ("03", "服务水平与运营保障"),
    ("04", "运营组织与服务协同"),
    ("05", "Mobilization与服务接管"),
    ("06", "工具平台与技术方案"),
    ("07", "持续改进与安全合规"),
    ("08", "治理体系与报告"),
    ("09", "云厂商合作与持续演进"),
    ("附录A", "RFP追溯矩阵"),
    ("附录B", "覆盖率自检"),
]

def find_chapter(dirpath, prefix):
    for fn in sorted(os.listdir(dirpath)):
        if fn.startswith(prefix) and fn.endswith(".md"):
            return os.path.join(dirpath, fn)
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--sla-count", type=int, default=None)
    ap.add_argument("--catalog-count", type=int, default=None)
    ap.add_argument("--role-count", type=int, default=None)
    ap.add_argument("--rfp-count", type=int, default=None,
                    help="RFP 要求总数 R；给定后校验附录A追溯率 z/R，缺项在 --strict 下 BLOCK")
    ap.add_argument("--strict", action="store_true",
                    help="L3 门禁：任一维度不达标 exit 2（BLOCK），不静默通过")
    args = ap.parse_args()

    chapters = []
    for prefix, title in ORDER:
        p = find_chapter(args.dir, prefix)
        if p is None:
            print(f"[WARN] 缺少章节: {prefix} {title}")
            continue
        chapters.append((title, p))

    if len(chapters) < 9:
        print("[FAIL] 章节不完整，中止整合")
        sys.exit(1)

    merged = ["# 对外技术方案书\n"]
    toc = ["## 目录\n"]
    body_chapters = []  # (prefix, title, body) 仅正文 01-09，供逐章叙事检查
    for i, (title, p) in enumerate(chapters, 1):
        with open(p, encoding="utf-8") as f:
            body = f.read()
        merged.append(f"\n<!-- 章节 {i}: {title} -->\n")
        merged.append(body)
        toc.append(f"{i}. {title}")
        pref = os.path.basename(p)[:2]
        if pref.isdigit():
            body_chapters.append((pref, title, body))
    merged.insert(1, "\n".join(toc) + "\n\n---\n")

    out = "\n".join(merged)
    # 四维自检（L3 门禁：可 BLOCK）
    text = out
    NARR = r"流程|步骤|触发|生命周期|矩阵|闭环|How|责任人|机制|时序"
    n_mapping = len(re.findall(r"目录条目|目录映射|条目（|条目 \|", text))
    n_evidence = len(re.findall(r"同行业|同类案例|佐证|实证|历史交付参考", text))
    n_trace = len(re.findall(r"^\| R\d+ \|", text, re.M))
    n_narrative = len(re.findall(NARR, text))
    n_diagram = len(re.findall(r"┌|→|```mermaid", text))

    # 门禁维度收集
    gate_fail = []  # (维度, 事实, 期望)
    # 维度1 逐章叙事完整度：01-09 每章至少 1 处 How/流程叙述
    thin_chapters = [f"{pref} {title}" for pref, title, body in body_chapters
                     if not re.search(NARR, body)]
    if thin_chapters:
        gate_fail.append(("叙事完整度", f"缺 How 叙述章节: {'; '.join(thin_chapters)}", "01-09 每章≥1处"))
    # 维度2 RFP 追溯率 z/R（给定 --rfp-count 时）
    if args.rfp_count:
        if n_trace < args.rfp_count:
            gate_fail.append(("RFP追溯率", f"附录A 追溯行 {n_trace}", f"应={args.rfp_count}（R1-Rn全量）"))
    # 维度3 佐证覆盖：至少 1 处两段式案例佐证
    if n_evidence == 0:
        gate_fail.append(("案例佐证", "0 处佐证", "≥1 处（两段式）"))
    # 维度4 映射覆盖：至少 1 处项级目录映射
    if n_mapping == 0:
        gate_fail.append(("目录映射", "0 处映射", "≥1 处项级映射"))

    # 交叉引用（若给阈值）
    checks = []
    if args.sla_count:
        sla_hits = len(re.findall(r"\b(?:SLA|SLO)\b", text))
        checks.append(("SLA/SLO 提及", sla_hits, f"预期表 {args.sla_count} 项"))
    if args.catalog_count:
        cat_hits = len(re.findall(r"条\b|条目", text))
        checks.append(("目录条目提及", cat_hits, f"预期 {args.catalog_count} 条"))
    if args.role_count:
        role_hits = len(re.findall(r"角色|SDM|TAM|L1|L2|L3", text))
        checks.append(("团队角色提及", role_hits, f"预期 {args.role_count} 角色"))

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(out)

    print("=== 整合完成 ===")
    print(f"章节数: {len(chapters)}")
    print(f"映射提及: {n_mapping} | 佐证提及: {n_evidence} | 追溯行: {n_trace}")
    print(f"叙事关键词: {n_narrative} | 图示符号: {n_diagram}")
    for name, got, exp in checks:
        print(f"交叉引用 {name}: {got} ({exp})")

    print("=== 四维门禁 ===")
    if not gate_fail:
        print("[PASS] 四维自检通过（映射/佐证/追溯/叙事完整度）")
    else:
        for dim, got, exp in gate_fail:
            print(f"[GATE-FAIL] {dim}: {got}（期望 {exp}）")
        if args.strict:
            print("BLOCKED: 四维自检未通过，回补对应章节后重跑；不静默通过。")
            sys.exit(2)
        else:
            print("[WARN] 未开 --strict，门禁仅提示不阻断；对外交付前应 --strict 重跑。")

    print(f"输出: {args.output}")

if __name__ == "__main__":
    main()
