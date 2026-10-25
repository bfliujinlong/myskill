---
name: oci-free-tier
description: "OCI Always Free ARM 实例抢夺与法兰克福区域抢注策略。"
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [OCI, Oracle Cloud, Always Free, ARM, 抢实例, eu-frankfurt-1, 免费云]
    related_skills: [overseas-model-hub, cloud-migration, multi-cloud]
---

# OCI Always Free ARM 实例抢夺（oci-free-tier）

## When to Use（何时使用）

- 用户想白嫖 Oracle Cloud 的 Always Free ARM 实例（VM.Standard.A1.Flex，最多 4 OCPU / 24GB）
- 免费额度常被抢光，需要**持续自动重试**直到创建成功
- 目标区域常为 eu-frankfurt-1（法兰克福，免费额度紧张）
- 抢到后要在实例上部署服务（如 Hermes 网关），且用户偏好**原生部署不用容器**

## 核心原理

OCI 免费 ARM 容量随时释放、随时被抢。抢注脚本的工作模式：
- 遍历该区域的多个 **Availability Domain（AD）**，并发或轮询发起 `launch_instance`
- 捕获 `HTTP 500 / OutOfHostCapacity`（容量不足）→ 重试
- 捕获 `HTTP 429`（限流）→ 指数退避 + 抖动
- 捕获 `401/403`（认证错）→ 致命，停
- 成功后立即停，取公网 IP

## 已验证可用的脚本

本会话落盘的脚本在 `~/.hermes/overseas-deploy/`：

| 文件 | 作用 |
|------|------|
| `oci-grabber/oci_grab_instance.py` | **v4 抢注脚本**，配置硬编码（user/tenancy OCID、fingerprint、subnet/image OCID、法兰克福 3 个 AD 全写在 CONFIG 里），需同目录 `private_key.pem` + `ssh-key-2026-08-14.pub` |
| `oci-claim.py` | 我写的聚焦法兰克福单区域版，读 `~/.oci/config`，成功后调 `notify.sh` |
| `notify.sh` | 占位通知（写日志+打印，预留 Telegram 片段） |
| `setup-native.sh` | **原生部署 Hermes 网关（不用 Docker）**，Python venv + systemd + Nginx Basic Auth |
| `setup.sh` | Docker 版部署（重机器备用） |

> 脚本完整清单、运行命令、网关安全底线见 **`references/deploy-scripts.md`**。

## 运行 v4 抢注脚本

```bash
cd ~/.hermes/overseas-deploy/oci-grabber
# 必须放好这两个文件：
#   private_key.pem        <- 你的 OCI API 私钥（本地放，勿传聊天）
#   ssh-key-2026-08-14.pub <- 脚本自动读取（已生成）
nohup python3 oci_grab_instance.py > grab.log 2>&1 &
# 菜单选 2 开始抢；Ctrl+C 停
```

## ⚠️ 凭证安全（重要）

1. **OCI API 私钥 `private_key.pem` 绝不要通过聊天/压缩包传来**。本地 `scp` 或粘贴到文件，权限 600。
2. **如果曾经把含私钥的包发出去过**，立刻去 OCI Console 撤销该 API Key 并重建（v5 README 已明确警告）。
3. 推荐改用 **v5 风格**：配置从 `~/.oci/config` 或 `OCI_*` 环境变量读取，脚本内不硬编码任何私钥/OCID。
4. `.gitignore` 必须排除 `private_key.pem`、`~/.oci/config`、SSH 私钥。

## v4 vs v5 差异（用户踩过的版本）

| 项 | v4 | v5 |
|----|----|----|
| 配置 | 硬编码在脚本 | 环境变量 / `~/.oci/config` |
| AD 策略 | 顺序轮询 3 个 AD | **真正多 AD 并发**（ThreadPool，≤3 worker） |
| 429 处理 | 固定睡 120s | 指数退避 + jitter，上限 300s |
| 已有 A1 检查 | 无 | 有，防止重复创建 |
| 黄金时间假设 | 有（02-06/10-14 UTC 更激进） | 取消，不再假定释放规律 |
| 规格 fallback | 手动切换 config | 40 周期后自动 1c6g→2c12g |
| 私钥 | 随包（已弃用） | **不含任何私钥** |

> 结论：v5 更安全更稳，但 v4 的硬编码 OCID 对用户已填好的法兰克福环境能直接跑。二选一，推荐 v5 模式。

## 法兰克福（eu-frankfurt-1）要点

- AD 名称形如 `jBix:EU-FRANKFURT-1-AD-1/2/3`（从 OCI Console 复制，**不要抄网上的**）
- 免费 ARM 在该区域极紧张，重试可能持续数小时甚至数天
- 推荐起手规格 **1 OCPU / 6GB**（成功率最高），有余量再建第二个

## 用户偏好（本会话确认）

- **不要容器**：部署 Hermes 网关用原生 Python venv + systemd（`setup-native.sh`），不强制 Docker
- **直接执行**：用户说"你执行优化即可"——优化类任务直接动手改脚本、做语法检查，不必反复确认
- 抢到后通知：用户要求 Telegram 通知（频道 5701842056），`notify.sh` 已留接入片段待填 bot token

## 常见陷阱

- 只放 `private_key.pem` 却忘放 `ssh-key-*.pub` → 脚本读公钥报错
- 私钥权限太开放（644）→ OCI SDK 拒绝加载
- 用网上抄的 AD 名称 → 与你自己租户不符，创建失败
- 429 时疯狂循环 → 只会增加限流，必须退避
- 抢到后不立刻保存公网 IP / 不写 SSH 私钥 → 登不进去
