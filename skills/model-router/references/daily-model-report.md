---
name: daily-model-report
description: 每日模型用量报告（Prometheus 真实计数 → Telegram）+ LiteLLM 依赖矩阵 + 免费额度口径
version: "1.0.0"
---

# 每日模型用量报告 + 监控栈（2026-10-17 实测固化）

## 监控栈全景（谁喂谁）

```
hermes 真实用量 exporter(:9199, hermes_tokens_total/hermes_api_calls_total, 带 model 标签)
token 实时 tracker(~/model/metrics_server.py :3003, 从 realtime-usage.jsonl 聚合)
        ↓ scrape
Prometheus(:9090, job token-metrics → 127.0.0.1:3003)
        ↓ datasource
Grafana(:3001, dashboard uid=token-usage, provisioning: /data/monitoring/grafana/conf/provisioning/dashboards/token-usage.yaml)
        ↓
monitor.html(:3002 http.server ~/model/) ← CF 隧道 monitor.aihubcloud.cn
每日报告 cron 6586b6eabafe (0 1 * * * UTC = 上海 9:00, no_agent, script=~/.hermes/scripts/model-daily-report.sh → telegram:5701842056)
```

- Grafana/Prometheus 本体在 `/data/monitoring/`（grafana bin+conf+dashboards，prometheus yml+data）；两者都以 ubuntu 用户跑，改 config 不需 sudo，重启 `kill <pid>` + 原命令行拉起即可。
- `/etc/cloudflared/config.yml` 受保护需 sudo 改；改完 `sudo systemctl restart cloudflared`。
- **LiteLLM 无 admin 账本**：本部署 `/v1/admin/usage`、`/v1/admin/spend/logs` 全 404（admin 未开）。要 LiteLLM 侧精确 per-request 账本需改 config 开 `admin=true` + DB；未开前 token 精确口径用 :9199 exporter（gateway 逐次真实计数）或 `~/.hermes/state.db` 的 `session_model_usage` 表。
- **依赖矩阵（决定 LiteLLM 能不能杀）**：Claude Code（settings.json `ANTHROPIC_BASE_URL=http://localhost:4000`）和 Codex（config.toml `model_provider="litellm"`）**依赖** LiteLLM :4000；bailian `bl` CLI（直连 token-plan/ws 端点）和 CodeBuddy bridge（直连 copilot.tencent.com）**不依赖**。杀 451847 前先确认当天不用 cc/codex。
- Claude Code 经 LiteLLM 调非 Anthropic 模型报 `unrecognized_model` = 链路通、只缺 model 映射（settings.json `modelOverrides` / modelPicker `behavesAs`），不是断连。Codex 报 `stdin is not a terminal` = 需 tty 交互，不是断连。

## 每日报告脚本要点（model-daily-report.sh）

1. 数据源一律走 Prometheus HTTP API（`sum by (model) (increase(hermes_tokens_total{direction="input"}[24h]))`），不重算、不估算——:9199 是 gateway 逐次调用真实计数。
2. `increase(...[24h])` 的返回行是 `metric_dict value` 形式，用 `line.rsplit(' ',1)` 拆再 `ast.literal_eval` 解析标签，取 top-N 按消耗排序。
3. 服务健康段逐个 curl（9090/9199/3003/4000/11434 + 百炼探活 `max_tokens:1`），报 HTTP 码；token-metrics(:3003) 根路径 404 属正常（只有 /metrics 路由）。
4. no_agent cron：stdout 原样投递 Telegram，空 stdout 不发。脚本必须 `set -o pipefail` 但查询失败要打 `QUERY_ERR` 行而不是崩掉（否则整报发不出）。
5. 报告尾部固定说明额度口径：OpenRouter 免费层无余额 API（429=当日限流次日重置）；百炼 token-plan 剩余额度只能控制台订阅页看（或 `bl usage token-plan`，需 console 登录）。

## 用户口径

- 用户问「目前模型什么/还有多少用量」：先答会话注入元数据的实际模型，再答 config.yaml default（两者可能不同=fallback 触发或刚切），最后给 24h 消耗表。免费池「剩余额度」大多无 API 可查，直接说明重置机制，不编数字。
- 日报建好后告知 cron job id + 触发时间（上海 9:00），不要每次手动跑。
