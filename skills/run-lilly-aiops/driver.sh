#!/usr/bin/env bash
# run-lilly-aiops driver: 重跑礼来 AIOps 交付物流水线，并对产物做体检。
# fail-fast：任一步失败即非零退出。
set -euo pipefail

UNIT="/home/ubuntu"
cd "$UNIT"

echo "[1/3] 生成 RWD Insights Agent deck ..."
node scripts/create_lilly_ppt.js

echo "[2/3] 体检 deck ..."
python3 - <<'PY'
import zipfile, re, collections, sys
p = "/home/ubuntu/Lilly_RWD_Insights_Agent_AWS.pptx"
z = zipfile.ZipFile(p)
slides = [n for n in z.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n)]
c = collections.Counter()
for n in z.namelist():
    if n.endswith(".xml"):
        c.update(re.findall(r'srgbClr val="([0-9A-Fa-f]{6})"', z.read(n).decode("utf-8", "ignore")))
print(f"  slides={len(slides)}  size={len(open(p,'rb').read())}B")
print(f"  top colors={c.most_common(6)}")
print(f"  alibaba-orange FF6A00 count={c.get('FF6A00', 0)}")
# 页数不符说明脚本被改动，直接失败，避免产出残缺 deck
if len(slides) != 8:
    sys.exit(f"  FAIL: expected 8 slides, got {len(slides)}")
if not c:
    sys.exit("  FAIL: no colors parsed, deck is likely empty")
PY

echo "[3/3] 复制报价单模板 ..."
python3 -c "import shutil; shutil.copyfile('/data/cloud-docs/客户报价单/中东迪拜客户_云迁移与运维报价单_中文版.xlsx','/home/ubuntu/AIOps智能运维服务报价单_中文版_V2.xlsx')"
ls -la /home/ubuntu/AIOps智能运维服务报价单_中文版_V2.xlsx

echo "OK: run-lilly-aiops completed"
