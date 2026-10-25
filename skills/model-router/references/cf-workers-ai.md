# Cloudflare Workers AI 验证与修复（class-level 参考）

适用：Hermes 通过 CF Workers AI 作为兜底/主模型时的验证、故障定位、调用格式。

## 规则（无需回顾本次会话即可执行）

- Token 类型：`cfut_` 前缀的 **API Token**（不是 `cfk_` Global Key）。存 `~/.hermes/skills/cloudflare/cf.env`，chmod 600。**永不写入聊天/脚本/commit**。
- 端点：`POST https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/@cf/{model}`。错误端点 `/ai/models` 返回 404，不要用。
- `curl` 默认 HTTP/2 → CF 边缘 `Failed sending HTTP POST request (43)`（TLS 1.3 握手成功，POST 发不出）。修法：加 `--http1.1`。已验证 200 模型：`@cf/mistralai/mistral-small-3.1-24b-instruct`、`@cf/meta/llama-3.1-8b-instruct`、`@cf/meta/llama-3.3-70b-instruct-fp8-fast`。
- Token 验证：`GET /user/tokens/verify` 只检查 token 是否 active，**不检查 Workers AI 权限 scope**。若推理 `/ai/run` 401，去 CF Dashboard → Profile → API Tokens → Edit → 加 `Workers AI` / `Edit` 权限（或新建选 "Workers AI" 模板）。
- Hermes 侧配置：CF 非内置 provider，`hermes model` 不列出。需手动配 `config.yaml`：`providers:` 段加 `cloudflare-workers-ai`（含 `api_key`、`base_url` 含 `account_id`、`context_length`）；`model:` 段设 `default: '@cf/...'` + `provider: cloudflare` + `base_url`。改后只能由独立 SSH 终端 `systemctl --user restart hermes-gateway.service` 生效（gateway 子进程内重启被 SIGTERM 护栏拦）。
- 验证脚本（不含 token，运行时读文件）：`~/.hermes/scripts/cf_wai_check.sh`（已建，chmod 700）。直接执行：`bash ~/.hermes/scripts/cf_wai_check.sh`，输出 HTTP 码 + 是否有内容。

## 诊断顺序（不重复试，直接定位）

1. `cat ~/.hermes/skills/cloudflare/cf.env | head -c 4` 确认前缀 `CF_` 且长度 >60；`ls -l` 确认 600。
2. `curl --http1.1 -w '%{http_code}' -o /dev/null ... /ai/run/@cf/meta/llama-3.1-8b-instruct` → 看 HTTP 码（预期 200）。若 401 → 权限缺；若 000/43 → 加 `--http1.1`；若 404 → 端点错。
3. 若 200 但内容空 → 不是 CF 问题，检查 `hermes gateway` 日志看是否走错 provider 或 fallback 触发。

## 典型错误与修法（单条规则，不重复）

- `curl` 无 `--http1.1`：43 / 000。修：加参数。
- `/ai/models` 404：端点错。修：换 `/ai/run/@cf/...`。
- 401/403：token 有效但无 Workers AI 权限。修：CF Dashboard 改 token 权限（非重试同一 curl）。
- `hermes config set model.default ...` 后未重启 / 重启无效：检查 `config.yaml` 是否被子进程旧值覆盖；重启必须在 gateway 外的独立 SSH 终端。

## 已验证模型对比（直接推理 POST，`--http1.1`，token 从 `cf.env` 读，不含 token 值）

| 模型端点 | HTTP | 耗时 | 结果说明 |
|---|---|---|---|
| `@cf/meta/llama-3.1-8b-instruct` | **200** | ~0.55s | ✅ 有真实内容（非空 response） |
| `@cf/mistralai/mistral-7b-instruct` | **400** | ~0.42s | ❌ 端点/模型名可能不匹配（非 401/404，非服务端故障） |
| `@cf/openai/gpt-4o-mini` | **400** | ~0.15s | ❌ 同上 |

结论：只有 `llama-3.1-8b` 当前端点 100% 可用；其他模型需先确认官方正确 `@cf/` 路径（CF 无 UI 下拉，模型名在路径中，错则 400）。直接路由优先，不依赖 LiteLLM 代理（LiteLLM 4000 独立，可能因 `pydantic_core` 环境损坏而宕，非 CF 故障）。

## 模型切换机制（不依赖 LiteLLM）

- 目录：`/home/ubuntu/model/`（`cf_models.json` + `models.txt` + `current_model.txt` + `switch_cf_model.sh`）。
- 切换命令：`bash ~/model/switch_cf_model.sh <模型名>`（如 `mistral-7b`、`gpt-4o-mini`、默认 `llama-3.1-8b`）。脚本更新 `~/model/current_model.txt` 并尝借 `sed` 改 `cf_wai_check.sh` 中的端点路径。
- 直接验证：`bash ~/.hermes/scripts/cf_wai_check.sh`（或 `~/scripts/cf_wai_check.sh`）。输出 HTTP 码；200 + 非空内容 = 可用。
