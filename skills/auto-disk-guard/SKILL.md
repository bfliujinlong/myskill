---
name: auto-disk-guard
description: "系统盘空间守护：自动巡检+清理，阈值可配，安全红线保护业务目录。当系统盘使用率超过阈值时自动清理可安全删除的缓存/日志/临时文件。"
triggers:
  - disk full
  - cleanup disk
  - disk guard
  - 磁盘清理
  - 系统盘满
  - auto cleanup
---

# auto-disk-guard — 系统盘空间守护

## 用途
当系统盘（/）使用率超过阈值时，自动安全清理缓存、日志、临时文件，确保业务服务不中断。

## 安全红线（绝对不删）
- `/data/hermes-install` — Hermes 安装目录
- `/data/sysmove` — 从系统盘迁移过来的大目录（npm-global/codex/litellm-venv/hermes-tools/hermes-installs/hermes-git/ollama-lib/google-cloud-sdk/az），全是系统目录的软链目标，删了服务直接挂
- `/data/ollama-models` — Ollama 模型库（由 ollama.service drop-in 的 OLLAMA_MODELS 指向）
- `/data/OpenMAIC` — OpenMAIC 项目
- `/data/cloud-docs` / `/data/cloud-docs-local` — 云文档
- `/data/hermes-deploy` — Hermes 部署目录
- `/data/pcs-presales-ps` — PCS 交付体系
- `/data/tenders` — 投标文件
- `/data/crowdsec` / `/data/unified-monitoring-agent` — 监控安全
- `/data/cache` — 业务缓存
- `/data/hermes-lsp` — Hermes LSP

## 迁移大目录到 /data（删不够时的第二步，2026-10-08 验证）

当清理缓存后系统盘仍紧张，把大目录整体迁到 /data 并软链回原位（服务无感知）：

```bash
migrate() {
  local SRC="$1" DST="$2" SUDO="$3"
  [ -L "$SRC" ] && return 0        # 已是软链跳过
  $SUDO rsync -a "$SRC/" "$DST/"   # 先复制（勿用 mv，跨盘 mv 慢且中断不可恢复）
  $SUDO mv "$SRC" "${SRC}.old-mig"
  $SUDO ln -s "$DST" "$SRC"
  $SUDO rm -rf "${SRC}.old-mig"
}
```

**规则与坑**：
- 迁移运行中服务的目录前，能停先停（如 ollama：`systemctl stop` → 迁 → `start`）；不能停的（如 ~/.hermes/tools，gateway 进程持有旧 inode）软链后新进程走 /data，旧进程到下次重启才完全切换，不影响当前运行。
- Ollama 模型库迁移额外需 systemd drop-in：`/etc/systemd/system/ollama.service.d/*.conf` 写 `Environment="OLLAMA_MODELS=/data/ollama-models"` + daemon-reload，否则重启后 ollama 又往系统盘 ~/.ollama 写。
- 大目录 rsync 耗时长（10G 级要几分钟），terminal 用 timeout≥600 或后台跑，勿中途重复执行。
- **迁完必须逐个验证服务**：跑一遍相关 CLI（`claude --version`/`bl`/`gcloud`/`az`/`hermes --version`/`ollama list`）+ 探端口 + `systemctl is-active`，全部真实输出后才报成功。
- 顺手清 journal（`journalctl --vacuum-size=100M`）+ `apt-get clean`。
- 记录迁移前哪些服务本来就是 DOWN 的（避免把存量故障误报成本次迁移造成）。

**已迁移清单（软链已建，重复迁移前先 `ls -la` 检查是否已是软链）**：`~/.npm-global`、`~/.codex`、`~/.litellm-venv`、`~/.hermes/cache/uv`、`~/.hermes/tools`、`~/.hermes/installs`、`~/.hermes/.git` → `/data/sysmove/*`；`/usr/local/lib/ollama`、`/usr/lib/google-cloud-sdk`、`/opt/az` → `/data/sysmove/*`。效果：系统盘 52%→30%（释放 10G）。

## 可清理目标

### 系统盘（/）
| 路径 | 典型大小 | 清理条件 |
|------|----------|----------|
| /tmp/* (>3天) | 200M+ | mtime > 3 |
| ~/.cache/uv/* | 100M | 安全删除 |
| ~/.local/share/uv/ | 100M | 安全删除 |
| ~/.cache/pip/ | 50M+ | pip cache purge |
| ~/.cache/pnpm/, ~/.cache/npm/ | 10M+ | 安全删除 |
| /var/log/journal/ | 50M+ | vacuum 7d/50M |
| /var/log/*.gz, *.old | 10M+ | mtime > 7 |
| /var/cache/apt/archives/ | 24K | apt autoclean |

### 数据盘（/data，仅清理操作日志）
| 路径 | 典型大小 | 清理条件 |
|------|----------|----------|
| /data/log/*.gz, *.1-.7 | 70M+ | mtime > 3 |
| /data/log/btmp.* | 6M+ | mtime > 7 |
| /data/backups/skills_*.tar.gz (>7天) | 89M/个 | 保留最近7天 |
| /home/ubuntu/.hermes/cron/output/ | 2M+ | mtime > 2 |
| /home/ubuntu/.hermes/cron/*.lock | 小 | mtime > 1 |

## 服务影响防护（端口快照审计）
用户硬约束：「保证不允许影响服务」。磁盘清理**绝不停服务、不 kill、不 restart**——脚本通篇无此类操作。在此之上加一道可验证的护栏：
- **清理前后拍关键业务端口快照**（litellm :4000、tg-relay :8099、dsh :3080/:3081、openmaic :3000、codebuddy 隧道 :63126-63128 等），清理后比对。
- **任何业务端口消失 → 写日志 + 发 Telegram 告警，绝不自动重启掩盖问题**，留待人工核查。
- 用 `EXIT trap` 覆盖所有退出路径（含低于阈值免清理分支），保证每次运行都审计。
- 端口探测用 `/usr/bin/ss -tlnp | grep ":<port> "`，不要依赖进程名（同机多实例会误判）。

## Cron 配置（实际生效）
```cron
# 每日 16:00 UTC = 北京时间 00:00，系统盘清理
0 16 * * * /home/ubuntu/.hermes/scripts/auto-disk-guard.sh >> /home/ubuntu/.hermes/logs/auto-disk-guard-cron.log 2>&1
```
> 阈值默认 35%，低于阈值只跑端口审计不清理。日志在 `~/.hermes/logs/auto-disk-guard.log`（脚本内）与 `~/.hermes/logs/auto-disk-guard-cron.log`（cron 输出）。

## 核心脚本
`/home/ubuntu/.hermes/scripts/auto-disk-guard.sh`

### 特性
- 阈值触发（默认35%），低于阈值不执行
- 安全红线检查：所有删除操作前校验路径是否在保护列表
- 单例锁防止并发
- 详细日志输出到 `/home/ubuntu/.hermes/logs/auto-disk-guard.log`
- 返回码：0=正常/已清理至阈值下，1=清理后仍超阈值

## Cron 配置
```cron
# 每日 03:30 执行磁盘守护（备份完成后）
30 3 * * * /home/ubuntu/.hermes/scripts/auto-disk-guard.sh >> /data/log/auto-disk-guard-cron.log 2>&1
```

## 手动执行
```bash
# 直接运行
/home/ubuntu/.hermes/scripts/auto-disk-guard.sh

# 查看日志
tail -20 /data/log/auto-disk-guard.log

# 模拟执行（仅查看使用率，不清理）
df -h / | awk 'NR==2 {print "Usage:", $5}'
```

## 阈值调整
编辑脚本中的 `THRESHOLD` 变量（默认35）。建议范围：30-40。

## 故障排查
- 如果清理后仍超阈值：检查是否有新的大文件或目录
  ```bash
  du -sh /* 2>/dev/null | sort -rh | head -10
  du -sh /home/ubuntu/* 2>/dev/null | sort -rh | head -10
  ```
- 如果脚本报错：检查日志 `/data/log/auto-disk-guard.log`
