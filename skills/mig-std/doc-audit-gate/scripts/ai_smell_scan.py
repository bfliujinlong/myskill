#!/usr/bin/env python3
"""AI 味 / 红线机器可检扫描器（doc-audit-gate 审计一 + 部分审计二）。

用法:
    python3 ai_smell_scan.py <doc.md|doc.docx> [--brand alibaba] [--json]

检出类别与扣分见 SKILL.md 审计一表；红线（占位符残留 / 虚构人员 / 金额臆造）
命中即 verdict=BLOCK。

退出码: 0 = PASS/PASS_NOTE；1 = REWORK/BLOCK；2 = 输入不可用
"""
import argparse
import json
import re
import sys
import zipfile
from pathlib import Path

# ---- 词表（命中即扣分） ----
JARGON = ["赋能", "抓手", "闭环", "打法", "对齐颗粒度", "一站式", "全方位",
          "深度融合", "生态化反", "组合拳", "顶层设计", "落地闭环", "链路打通",
          "护城河", "底层逻辑", "心智", "赛道", "新基建赋能"]
EMPTY_OPEN = [r"在当今[^。]{0,20}(?:浪潮|时代|背景下)", r"随着[^。]{0,30}(?:飞速发展|不断发展|日益)",
              r"众所周知", r"随着云计算[^。]{0,20}发展", r"在.{0,10}数字化转型的浪潮中"]
MECH_CONNECT = [r"^首先", r"^其次", r"^再次", r"^最后", r"^需要注意的是", r"^值得注意的是",
                r"^综上所述", r"^总而言之", r"^总的来看"]
FILLER = [r"以专业(?:的)?态度", r"严谨(?:的)?(?:方法|态度|作风)", r"奠定(?:了)?坚实(?:的)?基础",
          r"具有(?:重要|深远)(?:的)?意义", r"保驾护航", r"再创辉煌", r"共同努力下",
          r"确保万无一失", r"全力以赴", r"圆满完成"]
PLACEHOLDER = [r"\{\{[^}]*\}\}", r"\bTODO\b", r"待补充", r"\bXXX\b", r"\bN/A\b", r"待填"]
EMOJI = re.compile("[\U0001F300-\U0001FAFF\u2600-\u27BF]")
COMMIT = ["确保万无一失", "全力以赴", "零风险", "绝对可靠", "万无一失"]

# 虚构人员/案例线索（人工复核，脚本只提示）
PERSON_HINT = re.compile(r"(项目经理|工程师|架构师)[：: ]?[王李张刘陈杨黄赵吴周徐孙马朱胡郭何高林罗郑梁谢宋唐许韩冯邓曹彭曾肖田董袁潘蒋蔡余杜叶程苏魏吕丁任沈姚卢姜崔钟谭陆汪范金石廖贾夏韦付方白邹孟熊秦邱江尹薛闫段雷侯龙史陶黎贺顾毛郝龚邵万钱严覃武戴莫孔向汤)]")
CERT_HINT = re.compile(r"\b(PMP|CCIE|CISSP|VCP|RHCE|ACE|ACP)\s*#?\d*|\b(PMP|CCIE|CISSP)\s*证书编号")
CASE_HINT = re.compile(r"曾(服务|交付|完成)(过)?\s*[^，。]{2,20}(客户|项目|集团|银行|药业|能源)")


def read_text(path: Path) -> str:
    """读 md 或 docx 的纯文本；docx 走 zipfile 直读，不依赖 python-docx。"""
    if path.suffix.lower() == ".docx":
        with zipfile.ZipFile(path) as z:
            xml = z.read("word/document.xml").decode("utf8", "ignore")
        xml = re.sub(r"</w:p>", "\n", xml)
        return re.sub(r"<[^>]+>", "", xml)
    return path.read_text(encoding="utf-8")


def scan(text: str, brand: str = "none", allow_placeholder: bool = False):
    """扫描文本，返回 (deductions, redlines, score, verdict)。"""
    lines = [l.strip() for l in text.splitlines()]
    deductions = []
    redlines = []

    def hit(name, pts, matches, note=""):
        if matches:
            deductions.append({"category": name, "detail": f"{len(matches)} 处: "
                              + ", ".join(list(dict.fromkeys(matches))[:5]),
                              "points": pts})
            return pts
        return 0

    def find_all(pats, src=None):
        """返回整段匹配文本（非捕获组），避免只拿到正则碎片。"""
        out = []
        src = src if src is not None else text
        for p in pats:
            for m in re.finditer(p, src, flags=re.M):
                s0 = m.group(0).strip()
                if s0:
                    out.append(s0[:24])
        return out

    d = 0
    d += hit("咨询黑话", 2 * len(find_all(JARGON)) or 0, find_all(JARGON)) if find_all(JARGON) else 0
    d += hit("空洞开场", 5, find_all(EMPTY_OPEN))
    mc = find_all(MECH_CONNECT)
    if mc:
        d += hit("机械连接", len(mc) + (5 if len(mc) > 3 else 0), mc)
    d += hit("无信息量铺陈", 3, find_all(FILLER))
    ph = find_all(PLACEHOLDER)
    if ph:
        if allow_placeholder:
            deductions.append({"category": "占位符（模板模式豁免）",
                               "detail": f"{len(ph)} 处，视为模板骨架，非缺陷", "points": 0})
        else:
            redlines.append({"redline": "占位符残留", "detail": ", ".join(list(dict.fromkeys(ph))[:5])})

    em = EMOJI.findall(text)
    if em:
        d += hit("emoji 装饰", len(em), list(dict.fromkeys(em))[:5])

    cm = find_all(COMMIT)
    if cm:
        d += hit("过度承诺", 3, cm)
        redlines.append({"redline": "过度承诺（法务风险）", "detail": ", ".join(cm[:3])})

    # 排比堆砌：连续 >=3 行同构（以相同词开头或以「XX化/型/级」结尾）
    seq, prev = 0, None
    for raw in lines:
        l = re.sub(r"^\s*(?:>[\s-]*|[-*+]\s+|\|)", "", raw).strip()
        if not l:
            continue
        key = l[:2]
        seq = seq + 1 if key == prev else 1
        prev = key
        if seq == 3:
            d += 4
            deductions.append({"category": "排比堆砌", "detail": f"连续同构起始「{key}」", "points": 4})
            break

    # 空话标题：标题后 3 行内无数字、无表格
    for i, l in enumerate(lines):
        if re.match(r"^#{1,4}\s*(概述|背景|总结|结语|前言)\s*$", l):
            body = "\n".join(lines[i + 1:i + 6])
            if not re.search(r"\d", body) and "|" not in body:
                d += 3
                deductions.append({"category": "空话标题", "detail": l, "points": 3})

    # 数字一致性：跨章抓取「系统/台/套/人天」前的整数，冲突提示
    nums = re.findall(r"(?:约|共|总计)?\s*(\d{2,4})\s*(?:台|套|个系统|个应用|人天)", text)
    freq = {}
    for n in nums:
        freq[n] = freq.get(n, 0) + 1
    if len(freq) > 1:
        top = max(freq.values())
        others = [k for k, v in freq.items() if v == 1 and int(k) != int(max(freq, key=freq.get))]
        if others and top >= 2:
            redlines.append({"redline": "数字可能不一致（须现场核实，不得自选）",
                             "detail": f"出现多个体量数字: {sorted(freq, key=freq.get, reverse=True)[:5]}"})

    # 虚构线索（只提示，交人工判读）
    for nm, pat in (("疑似虚构人员", PERSON_HINT), ("疑似虚构证书", CERT_HINT), ("疑似虚构案例", CASE_HINT)):
        m = pat.findall(text)
        if m:
            redlines.append({"redline": f"{nm}（人工复核）",
                             "detail": ", ".join([x if isinstance(x, str) else x[0] for x in m[:3]])})

    score = max(0, 100 - d)
    if redlines:
        verdict = "BLOCK"
    elif score >= 90:
        verdict = "PASS"
    elif score >= 80:
        verdict = "PASS_NOTE"
    elif score >= 60:
        verdict = "REWORK"
    else:
        verdict = "BLOCK"
    return deductions, redlines, score, verdict


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("doc")
    ap.add_argument("--brand", default="none")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--template", action="store_true",
                    help="模板模式：占位符不算红线（模板本身即占位符骨架）")
    args = ap.parse_args()

    src = Path(args.doc)
    if not src.exists():
        print(f"文件不存在: {src}", file=sys.stderr)
        return 2

    text = read_text(src)
    ded, red, score, verdict = scan(text, args.brand, args.template)

    if args.json:
        print(json.dumps({"skill": "doc-audit-gate", "doc": str(src), "brand": args.brand,
                          "score": score, "verdict": verdict,
                          "deductions": ded, "redlines_hit": red,
                          "blocking": verdict == "BLOCK"},
                         ensure_ascii=False, indent=2))
    else:
        print(f"文档: {src}")
        print(f"字数: {len(text)} ｜ 色系声明: {args.brand}")
        print(f"总分: {score}/100 ｜ 结论: {verdict}")
        if ded:
            print("\n扣分明细:")
            for x in ded:
                print(f"  -{x['points']:>3}  {x['category']}: {x['detail']}")
        if red:
            print("\n红线命中（BLOCK）:")
            for x in red:
                print(f"  [!] {x['redline']}: {x['detail']}")
        if not ded and not red:
            print("\n机器可检项无命中；仍需人工判读：结论先行/数字密度/句长错落/重复内容。")
    return 0 if verdict in ("PASS", "PASS_NOTE") else 1


if __name__ == "__main__":
    sys.exit(main())
