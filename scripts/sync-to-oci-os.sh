#!/bin/bash
# 增量备份 Hermes 资产到 OCI Object Storage 免费桶(10GB)
# 桶: hermes-backup / namespace: frstrtmjwyeq / region: eu-frankfurt-1
set -e
OCI=/home/ubuntu/oci-monitor/venv/bin/oci
NS="frstrtmjwyeq"
BUCKET="hermes-backup"
REGION="eu-frankfurt-1"
TS=$(date +%Y%m%d)
LOG=/data/backups/oci-os.log
mkdir -p /data/backups

echo "[$(date -u +%FT%TZ)] 开始同步到 OCI OS" >> "$LOG"

# 1. cloud-docs 整体上传(增量, 用 --no-overwrite 省流量; 但为简单用 put 覆盖)
echo "  上传 cloud-docs ..." >> "$LOG"
$OCI os object bulk-upload --namespace $NS --bucket-name $BUCKET --src-dir ~/cloud-docs --region $REGION 2>&1 | tail -1 >> "$LOG"

# 2. skills + memory 打每日快照上传
SNAP="/tmp/hermes-skills-mem-$TS.tar.gz"
tar czf "$SNAP" -C ~ .hermes/skills .hermes/memory 2>/dev/null
$OCI os object put --namespace $NS --bucket-name $BUCKET --name "snapshots/hermes-skills-mem-$TS.tar.gz" --file "$SNAP" --region $REGION 2>&1 | tail -1 >> "$LOG"
rm -f "$SNAP"

# 3. 保留最新7天快照(删旧的)
$OCI os object list --namespace $NS --bucket-name $BUCKET --prefix snapshots/ --region $REGION --all 2>/dev/null | python3 -c "
import sys,json,subprocess
d=json.load(sys.stdin)
objs=sorted([o['name'] for o in d.get('data',[]) if o['name'].endswith('.tar.gz')])
old=objs[:-7]
for o in old:
    subprocess.run(['$OCI','os','object','delete','--namespace','$NS','--bucket-name','$BUCKET','--name',o,'--region','$REGION','--force'],capture_output=True)
print(f'  快照保留最新7个, 删{len(old)}旧')
" 2>&1 >> "$LOG"

echo "[$(date -u +%FT%TZ)] 同步完成" >> "$LOG"
