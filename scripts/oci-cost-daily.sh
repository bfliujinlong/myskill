#!/bin/bash
# oci-cost-daily.sh - 生成当日OCI费用播报文本(供cron调用)
# 输出纯文本到 stdout, 由 hermes cron 投递到全渠道
set -o pipefail

VENV="/home/ubuntu/oci-monitor/venv"
OCI="$VENV/bin/oci"
export OCI_CONFIG_DIR=/home/ubuntu/.oci
# 用 venv 的 python 跑 oci + 解析, 完全避开 shell 变量/pipefail 坑
START=$(TZ=UTC date -d "$(TZ=UTC date +%Y-%m-01)" +%Y-%m-%d)
END=$(TZ=UTC date -d "tomorrow" +%Y-%m-%d)

"$VENV/bin/python3" - "$OCI" "$START" "$END" << 'PYEOF'
import sys, subprocess, json, os
from collections import defaultdict
oci, start, end = sys.argv[1], sys.argv[2], sys.argv[3]
tenant = "ocid1.tenancy.oc1..aaaaaaaax6j4qdqjvsmgkouo3xvzuvvg7w4wgca33q5y2sap5773n6mdgdgq"
region = "eu-frankfurt-1"
raw = subprocess.run(
    [oci, "usage-api", "usage-summary", "request-summarized-usages",
     "--region", region, "--tenant-id", tenant,
     "--time-usage-started", start, "--time-usage-ended", end,
     "--granularity", "DAILY"],
    capture_output=True, text=True
)
if raw.returncode != 0:
    print("OCI CLI 调用失败:", raw.stderr[:300])
    sys.exit(0)
try:
    d = json.loads(raw.stdout)
except Exception as e:
    print("JSON解析失败:", e)
    sys.exit(0)
items = d.get("data", {}).get("items", [])
total = 0.0
days = set()
svc = defaultdict(float)
for it in items:
    amt = float(it.get("computed-amount") or 0)
    total += amt
    days.add(it.get("time-usage-started", "")[:10])
cur = items[0].get("currency", "SGD") if items else "SGD"
now = os.popen('TZ=Asia/Shanghai date +%Y-%m-%d\\ %H:%M').read().strip()
print(f"【OCI 每日费用播报】 {now} CST")
print("=" * 38)
print(f"本月区间: {start} ~ {end}")
print(f"估算总花费: ${total:.4f} {cur}  (约 ¥{total*5.3:.2f})")
print(f"活跃计费日: {len(days)} 天")
if total <= 0.05:
    print("状态: 恒定遗账(非新增), 免费额度内, 次月账期归零")
else:
    print("状态: ⚠️ 有新增消费, 请核查")
print("=" * 38)
print("机器: OCI 法兰克福免费机 | 目标: 零费用")
PYEOF
