---
name: litellm-gateway-guard
description: Use when model guard 报路由全 dead 或排查本机 LiteLLM :4000。
---

# LiteLLM 网关巡检排障（本机 :4000）

## 架构依赖图

```
Hermes(default=cb-official, base_url=http://127.0.0.1:4000/v1)
  └─ litellm-proxy.service  (:4000, /home/ubuntu/.litellm/config.yaml)
       ├─ cb-official ─→ openai/glm-5.3   @ 百炼 DASHSCOPE_CN_BASE_URL
       ├─ cb-hy4      ─→ anthropic/hy4-preview @ copilot.tencent.com (CODEBUDDY_API_KEY)
       ├─ cb-* 其余    ─→ http://127.0.0.1:4100/v1  ← cb2openai.service
       ├─ qwen3.8-flash / deepseek-v4.1-flash / glm-5.3 ─→ 百炼（同上 base）
       ├─ mistral-mini ─→ api.mistral.ai
       ├─ cf-qwen      ─→ Cloudflare Workers AI
       └─ ollama-local ─→ 127.0.0.1:11434 (qwen3:4b)
```

**cb-cli / cb-glm53 / cb-glm52 / cb-ds41f / cb-kimi27 等所有 cb-* 全部依赖 cb2openai(:4100)。**

## 坑 1：cb2openai 静默死亡 → cb-* 全 dead

症状：cb-* 全部 `litellm.InternalServerError: Connection error`，
`ss -ltnp | grep 4100` 无输出（服务 `inactive (dead)` 而非 failed，systemd 不自动拉）。

修复：`systemctl --user start cb2openai.service`，`curl -s http://127.0.0.1:4100/v1/models` 验证。

预防：hourly_model_guard.sh 开头已加前置自检，4100 不通就自动 start 后轮询等就绪。

**坑 1b（2026-10-25 实踩）：固定 `sleep 8` 不够 → 后续路由全误判 dead。**
实测某轮 start 后 8s 时 4100 仍未 ready，脚本照常往下跑，
结果除 cb-official 外 10 条路由 9~13ms 全部 dead；手 curl 却全 200。
改法：start 后 **轮询**（3s 一次、最多 15 次 = 45s）再进入探测循环，别用固定 sleep。
同理 litellm :4000 自身也要先探 `/health/liveliness`，不通则 restart 并轮询等待。

## 坑 2：max_tokens:8 把思考型模型探成 dead

hy4-preview（腾讯 CodeBuddy anthropic 端点）先输出 reasoning，
`max_tokens:8/64` 时返回 `content: null, stop_reason: max_tokens`。
若只看响应里有没有 `"content"` 字样会误判（错误 JSON 里也有 content 关键词）。

正确做法：
1. 探活 `max_tokens` 至少 **300**（hy4 实测 110 output tokens 才吐正文）。
2. 判活用 python 解析 JSON：`choices[0].message.content` 非空才算 OK；
   content 空则退回 `reasoning_content`；两者都空 = DEAD。**不要 grep `"content"`。**

## 坑 8：单次探测即判 dead 会误报

判活只看一次请求，上游刚拉起/限流抖动时会把活路由打成 dead（2026-10-25 实踩）。
guard 脚本已改为：首探 dead → `sleep 5` 复探一次，仍空才判 dead，
并在 detail 里标 `retried-ok` 表示复探通过（方便区分真抖动与真故障）。

## 坑 3：ollama-local 冷启动 25s+ 超时

qwen3:4b 冷加载 25–52s，`--max-time 25` 必然超时判 dead。探活统一 `--max-time 60`。

## 坑 4：百炼 Token Plan 免费额度耗尽

`Free quota exhausted. To continue accessing the model on a paid basis...`
影响 `glm-5.3` / `qwen3.8-flash` / `deepseek-v4.1-flash` / `cb-official` 直连路径。

cb-official 有 fallback 到 cb-hy4，所以实测会返回 `model: hy4-preview` ——
**看到返回 hy4 说明它走腾讯额度、是活的，不要当 dead。**

零费用硬约束：绝不充值、不关 "use free tier only"。

## 坑 5：fallback 全失败时，报错是骗人的

litellm 上报的是**原始**模型的错误（如百炼 Free quota exhausted），
不是最后那个 fallback 的错误。症状：主路由看着 dead，单独 curl 它的 fallback 却是通的。

排查必须逐个 curl fallback 成员，不要只看顶层 error message。

## 坑 6：cb-hy4 小 max_tokens 返回空 → 打断 fallback

hy4-preview 在 client 传 `max_tokens` < 300（如 50）时把预算烧在 thinking 上，
content 为空，litellm 抛 `APIConnectionError: 'NoneType' object is not iterable`。
这不是网络错，是空响应。

对策：fallback 链不能只有一环，写
`cb-official: [cb-hy4, cb-cli, cf-qwen, ollama-local]` 多级。
（坑 2 说的探活 max_tokens≥300 依然成立：探测用小值会误杀 hy4。）

## 坑 7：model_group_alias 不继承目标组的 fallback

litellm 按请求时的**原始 model 名**查 fallback 表。给 alias `opus: cb-official`
配 `fallbacks: - opus: [...]` 不生效，别名永远不 fallback（连续 dead）。

正确做法：把别名**提升为真实 model_name 条目**（复制目标组的 litellm_params），
并从 `model_group_alias` 里删掉同名键 —— 同名同时出现在 model_list 和 alias 会让 fallback 失效。

验证脚本（改完必跑）：

```bash
/data/hermes-install/venv/bin/python -c "
import yaml
d=yaml.safe_load(open('/home/ubuntu/.litellm/config.yaml'))
names=[m['model_name'] for m in d['model_list']]
print('dup:',[n for n in set(names) if names.count(n)>1])
print('alias冲突:',sorted(set(d['router_settings']['model_group_alias']) & set(names)))
"
```

## 巡检速查

```bash
bash /home/ubuntu/.hermes/scripts/hourly_model_guard.sh
cat /data/model-probe/hourly-guard-rank.json
systemctl --user is-active litellm-proxy cb2openai
ss -ltnp | grep -E '4000|4100|11434'
```

改 `/home/ubuntu/.litellm/keys.env` 或 litellm config 后必须 `systemctl --user restart litellm-proxy`
（gateway 子进程内不能自重启，需独立 SSH）。

## 现状基线（2026-10-23 09:27 UTC，修复后 18/18 全通）

| 路由 | 状态 | 延迟 |
|---|---|---|
| cb-official（→cb-cli fallback） | ok | ~6s |
| cb-hy4（→cb-cli fallback） | ok | ~3.5s |
| cb-cli / cb-glm53 / cb-glm52 / cb-ds41f / cb-kimi27 | ok | 7–9s |
| qwen3.8-flash / glm-5.3 / deepseek-v4.1-flash | ok（走 fallback） | 百炼耗尽 |
| opus / sonnet / haiku / default / claude-* | ok（走 fallback） | — |
| mistral-mini | ok | ~1.2s |
| cf-qwen | ok | ~0.3s（最快） |
| ollama-local | ok（慢） | ~50s |

百炼三条上游仍未恢复（Token Plan 额度未重置），全靠 fallback 顶着。
每日 UTC 00:00 左右看额度是否回滚；若恢复，把 model_list 里
opus/sonnet/haiku 等别名条目的 model 改回 `openai/qwen3.8-flash` 即可。
