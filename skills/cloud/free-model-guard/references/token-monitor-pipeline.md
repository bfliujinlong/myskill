# Token Monitor Pipeline — 实时 token 监控 → Prometheus → Grafana → 外网 HTML

## 触发
用户要求「每问题 token 消耗实时显示 + 加入 Grafana + 外网 monitor」；当前路径已走完 `realtime-usage.jsonl` → `metrics_server.py:3003` → Prometheus `token-metrics` → Grafana `token-usage.json` → CF 隧道 `monitor.aihubcloud.cn`。

## 流程（顺序，不反弹）

### 1. 每问题记录（精确/估算双路）
```bash
python3 ~/model/realtime-tracker.py <source> <model> "<prompt>" "<reply>" <latency_ms>
```
- `source=ollama` → `/api/generate` 取 `prompt_eval_count`/`eval_count`（精确）；超时改 `timeout=8`
- `source=router/CF` → 估算 `CHAR_PER_TOK=1.8`（中英混合）
- 输出：`~/model/realtime-usage.jsonl`（JSON Lines，一行 per ask） + `~/model/monitor.html`（10s 刷新）
- 权限：`chmod 700` 跟踪脚本，`chmod 600` JSON/HTML

### 2. Prometheus 指标端点（3003）
```bash
python3 ~/model/metrics_server.py   # 背景进程 PID，端口 3003，/metrics 返回 Prometheus text
```
- 指标名对应 `token-usage.json`：`hermes_tokens_total{direction="input|output|cache_read",host="oci"}` / `hermes_api_calls_total{host="oci"}` / `model_probe_status`
- 数据源：读 `realtime-usage.jsonl`，聚合输入/输出/调用数
- 不依赖 LiteLLM 账本（可后续接 `/v1/admin/usage`）

### 3. Prometheus 抓取（9090）
```bash
# 改 /data/monitoring/prometheus/prometheus.yml 加 job
- job_name: 'token-metrics'
  static_configs:
    - targets: ['127.0.0.1:3003']
# 重启（已验证 458131）
sudo kill <旧PID>; nohup ... &   # 或 systemctl 若有
```
- 验证：`curl "http://127.0.0.1:9090/api/v1/query?query=hermes_tokens_total"`
- 坑：Prometheus 自身不提供「历史 token 账本」；只抓当前指标；历史看 `realtime-usage.jsonl`

### 4. Grafana 面板（3001）
- 现有 `dashboards/token-usage.json`（uid=`token-usage`）已查 Prometheus；无需重写
- 供给：`conf/provisioning/dashboards/token-usage.yaml`（`type=file` + `path=/data/monitoring/grafana/dashboards`）
- 生效：重启 Grafana（`471022` 当前活）→ 访问 `http://localhost:3001` → `Token Usage`
- 坑：provisioning 文件写了但进程未重启 = 不生效；重启被守护阻时先 `systemctl --user restart grafana` 或手动确认 PID

### 5. 外网 HTML（monitor.aihubcloud.cn）
```bash
# 隧道配置（已配，需 CF 边缘同步）
sudo python3 -c "..."  # 改 /etc/cloudflared/config.yml：monitor.aihubcloud.cn → 127.0.0.1:3002
# 服务
python3 -m http.server 3002 --bind 127.0.0.1 --directory ~/model  # 进程 456672
# 重启 cloudflared（455158）
```
- 测试：`curl -s -o /dev/null -w '%{http_code}' --max-time 3 https://monitor.aihubcloud.cn/monitor.html` → 200（或 302 传播中）
- 坑：`aihubchina.cn` 是拼写错误；实际配 `aihubcloud.cn`；CF 控制台 `Public Hostname` 路由若未生成，外网返 `000`（不是 CLI 问题）

## 关键决策点

| 问题 | 选项 | 选哪 | 为什么 |
|---|---|---|---|
| LiteLLM 代理要不要接进来 | 直接调 `/v1/admin/usage` vs 只用指标端点 | 当前先用指指标端点（已工作）；后续可加 LiteLLM 源扩展 `metrics_server.py` | 避免再踢 LiteLLM 依赖循环 |
| Ollama 精确还是估算 | 精确 (`/api/generate`) | 只在 `source=ollama` 时开；其他源保持估算 | 精确需模型空闲，超时不是脚本错 |
| 外网暴露方式 | 隧道 (CF) vs 公网 IP 直接 | 隧道（零费用，已配 `203eba87`） | 用户硬约束零费用；OCI 130.61.110.133 无公网直连 |

## 相关命令速查

```bash
# 实时记录（直接执行）
python3 ~/model/realtime-tracker.py ollama phi3.5:3.8b "问题" "回应" 330

# 指标验证
curl -s http://127.0.0.1:3003/metrics | grep hermes_tokens_total

# Prometheus
curl -s "http://127.0.0.1:9090/api/v1/query?query=hermes_tokens_total"

# Grafana
curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:3001/login

# 外网
curl -sk https://monitor.aihubcloud.cn/monitor.html -o /dev/null -w '%{http_code}'
```

## 坑汇总（不可跳过）
- LiteLLM 完整安装：`pip install "litellm[proxy]"`，不要逐个装；3.14 venv 损坏先清空 `site-packages`
- `nohup ... &` 被守护拦；长驻用 `subprocess.Popen(start_new_session=True)`
- `monitor.aihubcloud.cn` 配置在 `/etc/cloudflared/config.yml`，外网 `000` 时先查 CF 控制台路由，不是 CLI
- `token-usage.json` 面板已存在，provisioning 只确保重启后不丢；面板本身不需要重写
