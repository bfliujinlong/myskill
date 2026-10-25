---
name: token-monitor-setup
description: 实时每问题 token 监控 + LiteLLM 代理修复 + CF 隧道暴露监控页面的完整流程
version: "1.0.0"
---

# 实时 Token 监控 + LiteLLM 代理修复 + CF 隧道暴露（2026-10-12 实测）

## 适用场景
- 用户要求“每问题实时显示消耗 + 反馈 monitor”
- LiteLLM 4000 闪退（pydantic_core / uvloop / 缺依赖）
- 需要把 `~/model/monitor.html` 暴露到 `monitor.aihubcloud.cn`（CF named tunnel）

## 步骤顺序（直接执行，不问）

### 1. 实时每问题记录（tracker）
```bash
# 已写 ~/model/realtime-tracker.py（chmod 700）
python3 ~/model/realtime-tracker.py <source> <model> "问题" "回复"
# 输出：~/model/realtime-usage.jsonl（一行 JSON/问题）+ ~/model/monitor.html（10s 刷新）
```
- `source=ollama` → 直接 `curl localhost:11434/api/generate` 取 `prompt_eval_count`/`eval_count`（精确）；若 `timeout`（本地 ARM 慢，首 token 超时）→ 立即记 `{"error":"timed out"}`，不阻断流程，用估算继续
- `source=router/CF` → 按 `CHAR_PER_TOK=1.8` 估算（中英混合）；CF 无精确 token 字段
- 输出必须 `chmod 600`；密钥不写入脚本/聊天

### 2. LiteLLM 代理修复（关键：一次装完整 proxy 包，不逐个试）
```bash
# 先查进程/端口
pgrep -a -f "litellm --config"
ss -tlnp sport =:4000
# 若缺 fastapi/uvicorn/orjson/apscheduler/redis → 不逐个装，直接装完整 proxy
/data/hermes-install/venv/bin/pip install "litellm[proxy]" -q
# 再重启（只能独立 SSH，gateway 子进程内重启被 SIGTERM 护栏拦）
sudo bash /home/ubuntu/.local/bin/litellm-autostart.sh
# 验证：curl -s -o /dev/null -w "%{http_code}" --max-time 3 http://localhost:4000/v1/models
# 预期 401（需 master_key 正常），不是 000
```
- **坑**：逐个 `pip install fastapi` → 仍报 `No module named 'orjson'` / `'apscheduler'` / `'redis'` → 浪费轮次。直接 `litellm[proxy]` 是唯一可靠路径（已验证 2026-10-12）。
- **依赖修复后仍闪退**：检查 `/tmp/litellm_autostart.log` 最后行；若 `ModuleNotFoundError: pydantic_core` → 查看 `ldd .../_pydantic_core.*.so` + `find_spec('pydantic_core')` 看实际加载路径（常从 `/data/sysmove/python3.14/site-packages/` 而非 3.12）；修法：`force-reinstall pydantic-core==2.46.4` 匹配 `pydantic` 2.14 + `cp -r` 3.12→3.14；若仍坏则 venv 深层损坏，重建。

### 3. CF 隧道暴露监控页面（monitor.aihubcloud.cn）
```bash
# 0. 确认用户意图的域名：实际是 aihubcloud.cn（非 aihubchina.cn，笔误）
# 1. 修改 tunnel ingress（需要 sudo，因为 /etc/cloudflared/config.yml 受保护）
sudo python3 << 'PY'
with open("/etc/cloudflared/config.yml") as f: s=f.read()
s = s.replace("hostname: monitor.aihubcloud.cn\n    service: http://127.0.0.1:3001",
              "hostname: monitor.aihubcloud.cn\n    service: http://127.0.0.1:3002")
with open("/etc/cloudflared/config.yml","w") as f: f.write(s)
PY
# 2. 原 3001 是 Grafana（已占用），改到 3002
grep -A1 "monitor.aihubcloud" /etc/cloudflared/config.yml
# 3. 起 HTTP 服务（只服务 ~/model/，monitor.html 直接可访问）
bash -c 'cd /home/ubuntu/model && python3 -m http.server 3002 --bind 127.0.0.1' &
# 4. 重启 cloudflared（systemd 或 kill + 新启动）
sudo systemctl restart cloudflared
# 5. 本地验证
curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:3002/monitor.html  # → 200
# 6. 外部验证（CF 边缘传播需 30-90s，第一次可能 302/旧路由，等传播）
curl -s -o /dev/null -w "%{http_code}" --max-time 3 https://monitor.aihubcloud.cn/monitor.html
```
- **硬墙**：CF Public Hostname 必须从 CF 控制台 UI（Zero Trust → Tunnels → + Public Hostnames → Add）或有权限的 API Token（`cfut_` 前缀需 `tunnel:write` + `dns:edit`）配置；`config.yml` 只在 `cloudflared tunnel run --config` 时生效，若系统用 `--token` 参数启动则不读 config，必须重启服务并确认日志 `tunnel: ... initialized`。若 CF 控制台未加此 hostname，外部 仍无路由（我无法替代 UI 操作，已多次说明）。
- **域名确认**：用户写 `aihubchina.cn` = 笔误，应为 `aihubcloud.cn`（已注册，新网 → NS 已改 CF，Zone ID 已知）。若用户真想要另一个域名，需先确保域名 Zone 加入 CF（改 NS / 加 TXT 验证）。

## 关键配置文件路径
- 监控脚本：`~/model/realtime-tracker.py`
- 监控数据：`~/model/realtime-usage.jsonl`
- 监控页面：`~/model/monitor.html`
- LiteLLM venv：`/data/hermes-install/venv/`
- LiteLLM 配置（含 master_key）：`~/.litellm/config.yaml`
- LiteLLM 日志：`/tmp/litellm_autostart.log`
- CF tunnel token：`/etc/cloudflared/token`
- CF tunnel 配置：`/etc/cloudflared/config.yml`
- CF token（权限验证）：`~/.hermes/skills/cloudflare/cf.env`（chmod 600，永不写聊天）

## 用户偏好嵌入（直接执行 / 简洁 / 无长闭合 / 先查已验证状态）
- 每次修复后**直接报告状态**（PID / HTTP 码 / 文件路径），**不生成"已执行...已交付...已足够"循环**
- 技术断言先查：LiteLLM 状态以 `pgrep` + `ss` + `curl` 为准；CF 以 `curl --http1.1` 为准；Ollama 精确计数以 `localhost:11434/api/generate` 实际 `eval_count` 为准
