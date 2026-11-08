#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""开箱验证：把厂家变体 md 渲染成 docx，核验色值 / 附录 E / 服务名串用 / 差异度。

用法:
    python3 verify_brand_variants.py                 # 验证 brand-doc-kit/templates 下全部变体
    python3 verify_brand_variants.py --dir /tmp/x    # 指定变体目录

校验项（任一 FAIL 即退出码 1）:
    1. docx 主色 / 表头底色与 brand_profiles/<brand>.json 一致
    2. 附录 E（厂家专有口径，E.1-E.5）存在
    3. 无跨厂家服务名串用（DMS / Organizations 等真同名词要求带厂家前缀消歧）
    4. 同类型 5 个厂家 md 互不相同（差异度 5/5）
"""
import argparse, re, subprocess, sys, zipfile, hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
KIT = HERE.parent
sys.path.insert(0, str(HERE))
import vendor_kb as kb  # noqa: E402

PY = sys.executable
EXPECT = {"alibaba": ("FF6A00", "FF6A00"), "tencent": ("3370FF", "3370FF"),
          "anchnet": ("C00000", "C00000"), "aws": ("232F3E", "232F3E"),
          "azure": ("00477F", "9CB9D8")}
# 各厂家专属服务名标记（手工 curated，只应出现在自家文档）
MARKER = {
    "alibaba": ["ECS", "OSS", "CEN", "RAM", "SLS", "SMC", "PolarDB", "DataWorks",
                "MaxCompute", "ROS", "VSwitch"],
    "tencent": ["CVM", "COS", "CCN", "CAM", "CLB", "TKE", "CLS", "TencentDB",
                "TDSQL", "CBS", "CFS", "CWP"],
    "aws": ["EC2", "EKS", "CloudWatch", "CloudTrail", "Transit Gateway", "MGN",
            "CloudFormation"],
    "azure": ["Entra ID", "ExpressRoute", "Log Analytics", "Azure SQL", "vWAN",
              "Bicep", "Sentinel", "Defender for Cloud"],
    "anchnet": [],
}
# 跨厂家真同名词（官方同拼写），文中必须带厂家 / 全名前缀消歧
COLLISION = {"DMS": ["Database Migration Service", "数据传输服务", "DTS"],
             "Organizations": ["组织 Organizations", "AWS Organizations"]}


def check_one(md: Path, brand: str, docx: Path) -> tuple:
    """渲染单个变体并核验，返回 (是否通过, 明细字符串)。"""
    r = subprocess.run([PY, str(KIT / "scripts" / "build_docx.py"), str(md),
                        "--brand", brand, "-o", str(docx)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return False, f"渲染失败: {r.stderr[:200]}"
    xml = zipfile.ZipFile(docx).read("word/document.xml").decode("utf-8")
    colors = re.findall(r'w:color w:val="([0-9A-Fa-f]{6})"', xml)
    fills = re.findall(r'w:shd[^/]*w:fill="([0-9A-Fa-f]{6})"', xml)
    ep, es = EXPECT[brand]
    okc = ep in colors or ep in fills
    oks = es in fills or es in colors
    txt = md.read_text(encoding="utf-8")
    leak = []
    for other, ms in MARKER.items():
        if other == brand:
            continue
        for m in ms:
            if re.search(r'(?<![A-Za-z])' + re.escape(m) + r'(?![A-Za-z0-9])', txt):
                leak.append(m)
    for tok, disamb in COLLISION.items():
        if re.search(r'(?<![A-Za-z])' + re.escape(tok) + r'(?![A-Za-z0-9])', txt):
            if not any(d in txt for d in disamb):
                leak.append(f"{tok}(未消歧)")
    own = sum(1 for m in MARKER[brand] if m in txt) if MARKER[brand] else None
    has_e = "附录 E" in txt and "E.5" in txt
    return (okc and oks and not leak and has_e), \
        f"主色{'✓' if okc else '✗'} 表头{'✓' if oks else '✗'} " \
        f"附录E{'✓' if has_e else '✗'} 标记{own if own is not None else 'n/a'} 串用{leak or '无'}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=str(KIT / "templates"))
    ap.add_argument("--workdir", default="/tmp/brand_verify_docx")
    args = ap.parse_args()
    root = Path(args.dir)
    out = Path(args.workdir); out.mkdir(parents=True, exist_ok=True)
    fail = 0
    for dtype in ("quotation", "hld", "lld", "bid"):
        suf = kb.DOC_TYPES[dtype]["suffix"]
        seen = {}
        for b in kb.BRAND_ORDER:
            md = root / f"{suf}_{kb.get_vendor(b)['label']}.md"
            if not md.exists():
                print(f"FAIL {dtype:9s} {b:8s} 缺文件 {md.name}")
                fail += 1
                continue
            ok, detail = check_one(md, b, out / f"{dtype}_{b}.docx")
            seen[b] = hashlib.md5(md.read_bytes()).hexdigest()
            print(f"{'OK  ' if ok else 'FAIL'} {dtype:9s} {b:8s} {detail}")
            fail += 0 if ok else 1
        uniq = len(set(seen.values()))
        print(f"差异度 {dtype}: {uniq}/{len(kb.BRAND_ORDER)}")
        fail += 0 if uniq == len(seen) else 1
    print(f"\n总失败: {fail}")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
