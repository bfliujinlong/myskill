STOP EMAIL SEND — 用户明确指令 (2026-09-08)

用户要求："请不要邮件发了 停止这个功能"

执行：
- 停止自动发邮件 (cron / herme cron / 任何自动发送)
- 已发邮件不撤回（已发送到 liujl@anchnet.com + liujinlong@outlook.com）
- 未来需要邮件时：先确认用户明确授权
- 当前邮件功能状态：已禁用，需手动启用

受影响的脚本:
- /tmp/send_email.py (已有，更改收件/附件后执行过)
- /home/ubuntu/.hermes/scripts/oci-cost-daily.sh (不发邮件，只本地播报)
- 其他任何包含 sendmail/smtp 自动触发的脚本

用户偏好：TG 主通道 + 本地文件为主，邮件仅在用户明确说"发邮件"时才发。
