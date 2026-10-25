---
name: azure-model-integration
description: Connect cc/dsh/Hermes to Azure-hosted Claude or GPT.
---

# Azure-hosted model integration

## When to use
- User says "用 Azure 的 Claude / GPT", "接 Azure OpenAI", "cc 用 Azure 模型", "我建了 Azure 资源".
- User wants to spend Azure Sponsorships credits ($5000) on model inference, NOT personal OpenAI/Anthropic bills.
- User was banned from Anthropic personal account (hard constraint: prefer Azure-hosted Claude over console.anthropic.com).

## Two destinations, two protocols
| Azure resource | Protocol | What it hosts |
|---|---|---|
| **Azure OpenAI** (`*.openai.azure.com`) | OpenAI-compatible | GPT family (gpt-5, gpt-5-mini, gpt-4o, …) |
| **Azure AI Foundry** (`*.services.ai.azure.com/anthropic`) | Anthropic-compatible | Claude family (claude-sonnet-4, claude-opus-4, …) |

Key insight: **Claude Code (cc) speaks the Anthropic protocol.** So:
- Foundry **Claude** → cc can use it DIRECTLY (same protocol). ✅
- Azure OpenAI **GPT** → cc CANNOT use it directly (protocol mismatch) → needs a translation proxy. ⚠️

## Path A — Foundry Claude (cleanest, no proxy)
Deploy Claude in ai.azure.com (Model Catalog → Claude → Serverless). Then:
- Python SDK: `from anthropic import AnthropicFoundry` (NOT plain `Anthropic`), `base_url="https://<res>.services.ai.azure.com/anthropic"`, auth via key or Entra ID.
- **cc direct**: set env `ANTHROPIC_REVERSE_PROXY=https://<res>.services.ai.azure.com/anthropic/` + `ANTHROPIC_API_KEY=<Foundry key>` + `ANTHROPIC_MODELS=claude-sonnet-4,claude-opus-4`, then run `claude`. No proxy process needed.
- Gotcha: `base_url` MUST end in `/anthropic`. Model field = your **deployment name**, not the public model name. 404 ⇒ wrong URL or deployment name.

## Path B — Azure OpenAI GPT into cc (translation proxy)
litellm's bundled proxy was broken in this environment (`ModuleNotFoundError: proxy_server`). Do NOT rely on it. Use the minimal FastAPI proxy in `scripts/cc2azure.py` instead — it translates Anthropic `/v1/messages` → Azure `chat/completions`. Verified working for direct API calls (curl returns correct Claude-style Message JSON).

Run it (key is read at request time from a server-side file, never hardcoded):
```
cd <skill dir>/scripts && python3 -m uvicorn cc2azure:app --host 0.0.0.0 --port 4000
```
Then point cc at it:
```
export ANTHROPIC_BASE_URL=http://localhost:4000
export ANTHROPIC_API_KEY=anything
# or persist in ~/.claude/settings.json: {"env":{"ANTHROPIC_BASE_URL":"http://localhost:4000","ANTHROPIC_API_KEY":"proxy"}}
```
**Known gap (honest):** the proxy was curl-verified but cc itself failed with "body is JSON but not a Message" because cc sends **streaming** requests and expects SSE `data:` frames + full Message fields (`usage`, etc.). Before declaring cc working, add SSE streaming support to the proxy (return `data: {json}\n\n` chunks, end with `data: [DONE]`) or force cc non-streaming. This is the one remaining step — do not assume cc works until you see a real cc response.

## gpt-5 family API quirks (verified)
- Use **`max_completion_tokens`**, NOT `max_tokens` (latter → 400 "Unsupported parameter").
- **No `temperature` param** — gpt-5 only accepts the default (1). Sending `temperature:0.7` → 400 "Unsupported value".
- **CRITICAL — `reasoning_effort` controls content vs reasoning split**: gpt-5-mini (2025-08-07) is a reasoning model that defaults to consuming 100% of `max_completion_tokens` into `reasoning_tokens`, leaving `content` empty. Fix: always pass `"reasoning_effort":"none"` (or `"minimal"`) to get normal content responses. Verified: with `reasoning_effort:none`, `reasoning_tokens=0` and content returns normally.
- Deployment check: `GET https://<res>.openai.azure.com/openai/deployments?api-version=2024-06-01` with header `api-key`. **404 means no model deployed yet** (resource exists but you must Deploy in Studio first). 405 models listed under `/openai/models` does NOT mean deployed.
- Chat call: `POST /openai/deployments/<deployName>/chat/completions?api-version=2024-06-01`.

## Two Azure OpenAI endpoints (important distinction)
| Endpoint | URL pattern | Notes |
|----------|-------------|-------|
| **Classic OpenAI** | `https://<res>.openai.azure.com/openai/deployments/<name>/chat/completions` | Old format, api-version required, some models return empty |
| **New AI Services (OpenAI-compatible)** | `https://<res>.services.ai.azure.com/openai/v1` | ✅ Working for OpenAI-compatible clients (OpenMAIC, litellm). Field is `model` (deployment name), NOT in path. Verified 2026-09. |
| **New AI Services (direct)** | `https://<res>.services.ai.azure.com/v1/chat/completions` | Alternative path, may return 404 for some configurations |

**Pitfall**: The `/openai/v1` path prefix is REQUIRED for OpenAI-compatible APIs on the new AI Services endpoint. Using just `/v1` returns `404 Resource not found`.

## Azure CLI deployment management (verified commands)
- List deployments: `az cognitiveservices deployment list --resource-group <rg> --account-name <name>` (note: misspelling causes "not recognized" — use full form, not short aliases)
- Create deployment: `az rest --uri '<mgmt-url>/deployments/<name>?api-version=2024-06-01-preview' -m PUT -b '{"sku":{"name":"GlobalStandard","capacity":50},"properties":{"model":{"format":"OpenAI","name":"gpt-4o","version":"2024-11-20"}}'`
- **Wait for propagation**: a `Succeeded` ARM state does NOT mean the API endpoint is ready. Propagation can take minutes to hours. If `DeploymentNotFound`, wait and retry.
- Get subscription resource list: `az resource list --subscription <sub-id> --output table` — reveals all resources across RGs.

## Azure Sponsorship billing limitation
- The `Microsoft.Consumption` API (usageDetails, balancesummary) returns 400/404 for Web Direct offer subscriptions. You CANNOT programmatically query spend.
- Alternatives: Azure Portal → Cost Management + Billing, or manual estimation (calls × model price).
- Spend is typically very low for testing (e.g., ~$0.10 for 50 gpt-5-mini calls).

## Non-reasoning model preference for production
- For content-generation tasks where reasoning isn't needed, prefer `gpt-4o` or `gpt-4o-mini` over gpt-5-mini to avoid the reasoning_effort complexity.
- If stuck with gpt-5-mini, ALWAYS pass `reasoning_effort:"none"` or you will get silent empty responses.

## Security (user is sensitive about key exposure)
- User stores keys in a server file (e.g. `/home/note.txt`) and may ask "我可以关了不" (can I rotate/disable it). **Recommend rotating the key in Azure after any share/read**, then re-inject.
- Prefer **Entra ID keyless auth** (`azure-identity` DefaultAzureCredential + `https://ai.azure.com/.default`) for production to avoid keys on disk.
- Never hardcode keys in scripts/configs world-readable. Read from a file at runtime (as `scripts/cc2azure.py` does).

## Wiring other tools
- **dsh** (OpenAI-compatible, already on this box): point its OpenAI base_url at `https://<res>.openai.azure.com/openai/v1/` + key. No proxy needed (native OpenAI protocol).
- **Hermes**: add an `azure-openai` provider in `~/.hermes/config.yaml` (endpoint + key + deployment name). Consult `model-router` skill for routing.
- **汤臣倍健 / client projects**: code-gen stays in the Azure enterprise tenant (compliant), but never paste real customer table schemas/PII into any endpoint — use desensitized samples.
