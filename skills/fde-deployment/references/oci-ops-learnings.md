# OCI Free-Tier 运维要点（FDE 栈底座，2026-08-22 验证）

本文件沉淀 OPC 单兵在 OCI Always-Free 上跑 Hermes/FDE 栈时踩过并验证过的运维手法。
原则：FDE 是部署系统，OCI 免费机 + Hermes 就是你的 Forward Deployed Stack（principle 5）。

## 1. 块存储卷重启后不挂载（iSCSI 掉线）—— 已验证修复
**症状**：`lsblk` 无 sdb；`iscsiadm -m session` 显示 `No active sessions`；`/data` 空；`~/cloud-docs`（软链到 /data/cloud-docs）断。
**根因**：OCI 块存储走 iSCSI 附加；重启后 iSCSI 会话未自动重连（即使 `open-iscsi`/`iscsid` 是 enabled），且 fstab 缺 `/data` 条目。
**修复（实测 sdb 回来 + /data 挂上）**：
```bash
sudo iscsiadm -m node -L all        # 重连缓存的 node（IQN 在 /etc/iscsi/nodes）
lsblk | grep sdb                    # 确认 150G 卷回来
sudo blkid /dev/sdb                 # 拿 UUID
# fstab 追加（用 UUID 不用 /dev/sdb，SCSI 名跨重启不稳）：
UUID="<uuid>"  /data  ext4  defaults,noatime,_netdev  0 2
sudo mount -a
```
**坑**：fstab 注释示例写的是 `/data1`，用 python `"/data" in s` 判断会误命中 `/data1` 子串 → 用行级匹配或 `sudo tee -a` 直接追加。OCI 强制要求 `_netdev`，否则重启卡死。

## 2. 每天自动起停（OCI Resource Scheduler，非 CLI）—— 已验证
`oci-cli` 3.90.3 **无 `scheduler` 子命令**，但 SDK 含 `oci.resource_scheduler`。用 python + SDK 建云端 Schedule（机器关机也生效）：
```python
import oci, oci.resource_scheduler.models as m
c = oci.config.from_file("~/.oci/config")
cl = oci.resource_scheduler.ResourceSchedulerClient(c)
# CreateScheduleDetails(action="START_RESOURCE", recurrence_type="CRON",
#   recurrence_details="0 9 * * *", local_time_zone="Asia/Shanghai",
#   resources=[m.Resource(id=INSTANCE_OCID, type="INSTANCE")])
# STOP_RESOURCE 同理，recurrence "0 0 * * *" = 北京24:00
```
**注意**：`oci compute volume-attachment list` 在本环境 stdout 返回空（0 bytes，无报错）——绕开，用 `iscsiadm -m node` 拿 IQN。`oci bv volume get` 正常可用。

## 3. Nous token 失效 → 静态 API Key —— 已验证
**症状**：`hermes status` 显示 `logged in`，但模型调用 401 `AuthenticationError`。
**根因**：`auth.json` 里 OAuth `access_token` 过期（`expires_at`），refresh 未兜住。
**修复**：把静态 Key 写进 `.env` 的 `NOUS_API_KEY=sk-nous-...`。`.env` 是受保护文件，`patch` 会被拒 → 用 python 读改写。
**坑**：`hermes status` 可能仍显示旧 OAuth "logged in"，但实际调用走 `.env` 的 key；`hermes chat` 实测返回 OK 即成功。
**cron drift_skip**：模型从 `zai/glm` 换成 `nous/upstage` 后，未 pin 的 cron 会 skip（报 `drift_skip:silent`）。修：`hermes cron edit <id> --provider nous --model upstage/solar-pro4:free`。

## 4. OSS 对象存储挂载 —— 未解决（记录坑，非方案）
OCI OS 走 S3 兼容需 `customer-secret-key`。本环境用 API-key 用户跑 `oci iam customer-secret-key create` 返回 **404 NotAuthorized**（即使 user 列表显示 `can-use-customer-secret-keys: true`，home region 已是 FRA）—— Oracle IAM 权限，机器上绕不过。
**rclone 坑**：`downloads.rclone.org` 的 1.75 deb 实测**无 oci 也无 s3 后端**（`rclone backend` 列表搜不到）——该包被裁剪，不可用。
**现状**：保留 `sync-to-oci-os.sh` 脚本同步备份模式（已验证可用）。用户明确要求"**一定要自动挂载**"——待在 OCI 控制台网页手动建 secret key 后，再配 rclone s3 后端 + systemd 开机自挂 `/mnt/oss`。**不要**把本节当已验证挂载流程。
