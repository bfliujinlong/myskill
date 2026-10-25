# Azure OpenAI via Hermes `azure-foundry` — verified recipe

Verified 2026-08-24 on Hermes v0.20.4. Endpoint used:
`https://liujl-9958-resource.openai.azure.com/openai/v1` (westus3, deployment `gpt-5-mini`).

## 1. Probe the endpoint (raw SDK, confirms key + URL are valid)
Read the key from the user's secret store into an env var — never inline it.
```python
import os
from openai import OpenAI
key = os.environ["AZURE_KEY"]                       # length 84 in this case
base = "https://<resource>.openai.azure.com/openai/v1"
c = OpenAI(api_key=key, base_url=base)
models = [m.id for m in c.models.list().data]
print("gpt-5-mini in list:", "gpt-5-mini" in models)
```

## 2. Real chat completion (catches the reasoning-token pitfall)
```python
r = c.chat.completions.create(
    model="gpt-5-mini",
    messages=[{"role": "user", "content": "用一句话介绍你自己。"}],
    max_completion_tokens=2000,        # MUST be large — gpt-5-mini is a reasoning model
    temperature=1,
)
print(r.choices[0].message.content)
```
- `max_completion_tokens=50` → `content: ""`, `finish_reason: length`,
  `reasoning_tokens: 50` (budget fully consumed by reasoning). Empty output.
- `max_completion_tokens=2000` → normal Chinese reply. Verified working.

## 3. Write Hermes config (config.yaml is write-protected — use the CLI)
```bash
hermes config set model.provider azure-foundry
hermes config set model.default gpt-5-mini
hermes config set model.base_url "https://<resource>.openai.azure.com/openai/v1"
hermes config set model.api_mode chat_completions
# key lives in ~/.hermes/.env as AZURE_FOUNDRY_API_KEY
```

## 4. End-to-end verification through Hermes itself
```bash
hermes -z "用六个字以内回答：今天天气如何？"   # new session → uses Azure gpt-5-mini
```
Confirmed output: `多云偏热` (real gpt-5-mini reply).

## Behavior Hermes handles automatically (do NOT reimplement)
- Detects `openai.azure.com` → forces `api_mode: chat_completions` (gpt-5/x on
  Azure 404 on `/responses`).
- Sends `max_completion_tokens` for gpt-4o / o-series / gpt-5.x.
- Forwards `api-version` via `default_query` (extracted from legacy base URLs).
- Treats `default` as the deployment name.

## Scope note
The app used here (`cli_aaeb0ff8aa381cb3`, anchnet) had NO `bitable:app` scope,
so Feishu bitable read/write was blocked. That is unrelated to this recipe and
out of scope.
