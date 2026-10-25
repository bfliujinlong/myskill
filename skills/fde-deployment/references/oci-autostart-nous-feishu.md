# OCI 免费机 自动起停 + Nous Token 恢复（实战记录）

本文件固化 2026-08-22 跑通的真实路径，供 fde-deployment 及 OPC 运维复用。

## 1. OCI 自动起停（Resource Scheduler，机器关机也生效）
- oci-cli 3.90.3 **没有** `oci scheduler` 子命令（PyPI 最新就是它，不是镜像锁的）。但 SDK `oci.resource_scheduler` 可用。
- 用 SDK 建 Schedule（不要指望 CLI）：
```python
import oci
from oci.resource_scheduler.models import CreateScheduleDetails, Resource
cfg = oci.config.from_file("~/.oci/config", "DEFAULT")
client = oci.resource_scheduler.ScheduleClient(cfg)
TEN = cfg["tenancy"]; IID = "<实例ocid>"
# 开机: 北京09:00
client.create_schedule(create_schedule_details=CreateScheduleDetails(
    compartment_id=TEN, display_name="free-ubuntu-vm-daily-start",
    description="每天北京09:00自动开机", action="START_RESOURCE",
    recurrence_type="CRON", recurrence_details="0 9 * * *",
    local_time_zone="Asia/Shanghai", resources=[Resource(id=IID)]))
# 关机: 北京24:00
client.create_schedule(create_schedule_details=CreateScheduleDetails(
    compartment_id=TEN, display_name="free-ubuntu-vm-daily-stop",
    description="每天北京24:00自动关机", action="STOP_RESOURCE",
    recurrence_type="CRON", recurrence_details="0 16 * * *",
    local_time_zone="Asia/Shanghai", resources=[Resource(id=IID)]))
```
- action 枚举：`START_RESOURCE` / `STOP_RESOURCE` / `BACKUP_RESOURCE`（不是 START/STOP）。
- 查询：`client.list_schedules(compartment_id=TEN)` → `items`（注意不是 `.data` 直接列表，是 `.data.items`）。
- 块存储查询用 `oci bv volume get` / `oci bv boot-volume get`（不是 `compute boot-volume`，旧 CLI 无此子命令）；需 `--availability-domain` 拿 attachment 的 volume-id。

## 2. Nous Token 失效 → 静态 API Key 恢复
- Hermes 的 Nous 走 **OAuth device_code**（auth.json），会过期且 refresh 可能失败 → 日志 `401 Your API key is invalid`。
- 恢复：把用户给的**静态 key** `sk-nous-...` 写入 `.env` 的 `NOUS_API_KEY=`（受保护文件，用 python 读改写，不能用 patch）。
- 验证：`hermes chat -q "回复OK"` 返回 OK 且无 401；或 curl `https://inference-api.nousresearch.com/v1/models -H "Authorization: Bearer $KEY"` 返回模型列表（404 模型名是正常，401 才是 key 错）。
- 静态 key 不过期，比 OAuth 稳；`hermes status` 仍显示旧 OAuth "logged in" 是显示滞后，实际调用走 `.env` key。
- 免费模型名例：`upstage/solar-pro4:free`（config.yaml 默认）。

## 3. 记忆上限是 config.yaml 嵌套段
- `memory_char_limit` 是 `config.yaml` 里 `memory:` 段下的键，不是顶层键。
- `hermes config set memory_char_limit 8000` 会误写成顶层、运行时不读（回落 2200）。
- 正确：`hermes config set memory '{...}' --force` 写整段，或手写 `memory:` 段嵌套。
- 当前已设 8000 / user_char_limit 5000。

## 4. 日报脚本 PATH 坑
- systemd/cron 环境 PATH 不含 hermes；脚本里用裸 `hermes` 会 command not found（日志假"sent"）。
- 改绝对路径：`/home/ubuntu/.hermes/hermes-install/venv/bin/hermes send -t telegram:5701842056 "..."`。
- 推送不依赖 gateway 进程，机器重启后也能发。

## 5. 飞书后台授权（用户操作，我替不了）
- "Can't message this bot yet" = 后台未发布。步骤：开机器人能力 → 权限管理开 `im:message`/`im:message:send_as_bot`/`im:resource` → 事件订阅 `im.message.receive_v1` → 版本管理与发布。
- 权限搜索框只在当前 tab 内搜；`im:resource` 等不在"用户身份权限"tab，要切"应用身份/机器人身份"tab 才看得到。每加权限都要重新发版。
- Hermes 端连通用 `hermes status` 看 Feishu ✓ configured；Token 有效性用 `open.feishu.cn/health` 200 + `im/v1/messages` 返回 400(非401) 验证。
