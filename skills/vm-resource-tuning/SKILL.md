---
name: vm-resource-tuning
description: "巡检小内存 VM 资源并调优 swap/磁盘。触发：巡检、swap 优化、内存不足。"
triggers:
  - 巡检
  - swap 优化
  - 内存不足
  - 机器卡
  - resource check
---

# vm-resource-tuning — 小内存 VM 资源巡检与调优

## When to Use
用户说“巡检”“资源情况”“机器卡”“内存不足”“swap 优化”，或需要诊断/调优小内存云 VM（GCP e2-micro 这类 1-2G 免费层，跑 Hermes gateway + cron + LSP 已经很挤）的内存/CPU/swap/磁盘压力时。

## 巡检流程（一条命令拿全）

```bash
uptime; free -h; swapon --show; df -h /; \
ps aux --sort=-%mem | head -8; vmstat 1 3
```

判读要点：
- `vmstat` 的 **si/so 持续非零 + wa% 高** = 内存颠簸（thrashing），load 高多半是换页造成的，不是 CPU 忙——别误判为 CPU 问题。
- `free` 看 **available** 列，不看 free 列。
- 内存大户排序处理：Hermes 机器上典型是 gateway(~290M)、pyright-langserver LSP(~210M)、cron scheduler(~85M)。**第一刀永远是关 pyright LSP**（省 ~210M），但先问用户是否近期做 Python 开发。
- 任何编译类任务（node build 等）不要在 1G VM 上跑，必 OOM；转到大内存机器。

## Swap/内存调优（已验证，持久化）

```bash
# 1. swappiness 降为 10：优先用物理内存，减少磁盘换页
sudo tee /etc/sysctl.d/99-swap-tuning.conf > /dev/null << 'EOF'
vm.swappiness=10
vm.vfs_cache_pressure=50
EOF
sudo sysctl --system

# 2. 启用 zswap（换出页先在内存压缩 ~3:1，小内存 VM 提速最明显）
echo zstd | sudo tee /sys/module/zswap/parameters/compressor
echo 1   | sudo tee /sys/module/zswap/parameters/enabled
# 持久化
echo "options zswap enabled=1 compressor=zstd max_pool_percent=25" | \
  sudo tee /etc/modprobe.d/zswap.conf > /dev/null
```

**坑**：
- GCP 内核（*-gcp）**没有 zram 模块**（modprobe zram 报 not found），不要在 zram 上浪费时间，直接用 zswap，效果类似。
- 调完看 `free -h`：换出的页会随压力下降自动回收，swap 占用下降即生效；zswap 当前存量看 `/sys/kernel/debug/zswap/stored_pages`（需 root）。

## 磁盘清理（配合 auto-disk-guard skill）

GCP 免费层磁盘 30G 封顶（所有 VM 共享额度，超出按量计费：Standard ~$0.04/GB/月）不可免费扩，清理优先级（实测一轮 ~1.4G）：
1. `sudo journalctl --vacuum-size=100M`（journald 常年 500M+）
2. **snap 旧 revision**：`snap list --all | awk '/disabled/{print $1,$3}'` 找出后逐个 `sudo snap remove <name> --revision=<rev>`，每个旧版本 50-350M，只删 disabled 的，活跃版本（如 google-cloud-cli）不删
3. `sudo apt clean && sudo apt autoremove -y`
4. `~/.hermes/cache/uv`（可达 380M，删除后 uv 下次自建）
5. `~/.cache/pip`、`~/.npm/_cacache`
6. **已停用服务的源码/安装包**：`~/.hermes/deploy/dsh-src`（1.5G，dsh 停用后可全删）、`~/.hermes/lark-cli.tar.gz`（14M 安装残留）

## 大目录排查

```bash
# 逐层排查，不要一次 du 整个 .hermes
sudo du -sh /var/log /snap /tmp ~/.hermes 2>/dev/null | sort -rh
du -sh ~/.hermes/* 2>/dev/null | sort -rh | head -12
```

**坑**：`du -sh ~/.hermes` 在 swap 颠簸的慢盘上可超 60s 超时——拆成 `du -sh ~/.hermes/*` 逐子目录查，或用 `--max-depth=1` 限定深度，不要对整个用户目录树跑全量 `du`。

## 通道精简（GCP 副机定位）

GCP 免费机作为轻量中转/备用节点，只保留 Telegram 通道。飞书/微信/钉钉的 platforms 配置和 .env 变量应清空，避免与 OCI 主机的多通道冲突。具体做法：
- `config.yaml` 的 `platforms:` 设为 `{}`
- `.env` 只留 `TELEGRAM_*` 变量，删除 FEISHU/WECHAT/DINGTALK/EMAIL 等
- 飞书状态检查类 cron 用 `hermes cron pause <id>` 暂停（不删，方便以后恢复）
- 已停用的 dsh 服务连源码一起删（`systemctl --user stop/disable` + `rm -rf ~/.hermes/deploy/dsh-src ~/.dsh`），省 1.5G+；dsh 只在 OCI 主机保留
- `hermes cron delete <id>` 删掉不再需要的 cron（如 OCI 抢注播报）

## 每日磁盘清理 cron

创建 `~/.hermes/scripts/disk-cleanup.sh`（journald→100M、apt clean、npm/pip 缓存、Hermes 缓存>7天、/tmp>7天、snap 旧版本、docker prune），用 `hermes cron create --name "每日磁盘清理" --deliver "telegram:5701842056" --no-agent --script "disk-cleanup.sh" "0 14 * * *"` 注册（0 14 UTC = 上海 22:00）。脚本输出直接送达 Telegram。

## 模型选择（百炼 Token Plan）

百炼 Token Plan 按 Credits 统一计量，不同模型兑换率不同。按量计费价格对比（中国区，元/百万 tokens）：
- qwen3.8-max：输入 12 / 输出 36 / 缓存 1.5
- glm-5.2：输入 8 / 输出 28 / 缓存 2.1

GLM-5.2 比 qwen3.8-max 便宜约 30%，同等对话消耗 Credits 更少。用户已选 glm-5.2 作为默认。

切换默认模型用 `hermes config set model.default glm-5.2`，provider 保持 `alibaba-cn`。

**坑**：config.yaml 的 default 可能被某些进程/gateway重启覆盖回旧值（如 qwen3.8-max）。每次重启 gateway 前先 `grep default: ~/.hermes/config.yaml` 确认值正确，被改则重新 `hermes config set` 再重启。

## 用户偏好
- 巡检结果用表格呈现（项目/状态/评价），结论先行，建议按收益排序。
- 破坏性操作（关 LSP、删缓存）先报告方案并征得同意再执行；纯安全清理（journal vacuum、apt clean、旧 snap revision）可直接做。
- 巡检命令要快——用户会中途打断长时间运行的 `du`，拆成小命令分批跑，不要一条大命令等 60s+。
- 用户说"停止"或"抢注"时立即停手当前巡检，不要继续跑后台命令。
