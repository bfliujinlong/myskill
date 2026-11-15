#!/bin/bash
# oci-grab-telegram-report.sh - 每2小时播报 OCI 抢注进展到 Telegram
LOG="/home/bfyalong/.hermes/overseas-deploy/oci-grabber/oci-grab.log"
TARGET="telegram:5701842056"

if [ ! -f "$LOG" ]; then
  hermes send -t "$TARGET" "OCI抢注播报: 日志文件还不存在，抢注可能还未启动。"
  exit 0
fi

# 统计（匹配 v5 实际日志格式：EU-FRANKFURT-1-AD-1/2/3）
total=$(grep -c "Cycle #" "$LOG" 2>/dev/null || echo 0)

ad1_ok=$(grep -c "EU-FRANKFURT-1-AD-1.*success\|EU-FRANKFURT-1-AD-1.*launched\|EU-FRANKFURT-1-AD-1.*running" "$LOG" 2>/dev/null || echo 0)
ad2_ok=$(grep -c "EU-FRANKFURT-1-AD-2.*success\|EU-FRANKFURT-1-AD-2.*launched\|EU-FRANKFURT-1-AD-2.*running" "$LOG" 2>/dev/null || echo 0)
ad3_ok=$(grep -c "EU-FRANKFURT-1-AD-3.*success\|EU-FRANKFURT-1-AD-3.*launched\|EU-FRANKFURT-1-AD-3.*running" "$LOG" 2>/dev/null || echo 0)

ad1_cap=$(grep -c "EU-FRANKFURT-1-AD-1.*out of host capacity" "$LOG" 2>/dev/null || echo 0)
ad2_cap=$(grep -c "EU-FRANKFURT-1-AD-2.*out of host capacity" "$LOG" 2>/dev/null || echo 0)
ad3_cap=$(grep -c "EU-FRANKFURT-1-AD-3.*out of host capacity" "$LOG" 2>/dev/null || echo 0)

ad1_limit=$(grep -c "EU-FRANKFURT-1-AD-1.*FATAL\|EU-FRANKFURT-1-AD-1.*limit" "$LOG" 2>/dev/null || echo 0)
ad2_limit=$(grep -c "EU-FRANKFURT-1-AD-2.*FATAL\|EU-FRANKFURT-1-AD-2.*limit" "$LOG" 2>/dev/null || echo 0)
ad3_limit=$(grep -c "EU-FRANKFURT-1-AD-3.*FATAL\|EU-FRANKFURT-1-AD-3.*limit" "$LOG" 2>/dev/null || echo 0)

last_success=$(grep -i "success\|launched\|running" "$LOG" 2>/dev/null | tail -1 || echo "暂无成功")
last_time=$(grep -oP '\[\K[^\]]+' "$LOG" 2>/dev/null | tail -1 || echo "N/A")
is_running=$(pgrep -f "oci_grab_instance.py" >/dev/null 2>&1 && echo "运行中" || echo "已停止")

cat << EOF > /tmp/oci-report.txt
📊 OCI 抢注播报 (每2小时)
⏰ 时间: $last_time
🔄 状态: $is_running
📈 总轮询: ${total} 次
🏆 成功: AD-1 ${ad1_ok}, AD-2 ${ad2_ok}, AD-3 ${ad3_ok}
❌ 容量满: AD-1 ${ad1_cap}, AD-2 ${ad2_cap}, AD-3 ${ad3_cap}
🚫 额度/错误: AD-1 ${ad1_limit}, AD-2 ${ad2_limit}, AD-3 ${ad3_limit}
📝 最近成功: ${last_success}
EOF

hermes send -t "$TARGET" -f /tmp/oci-report.txt
rm -f /tmp/oci-report.txt
