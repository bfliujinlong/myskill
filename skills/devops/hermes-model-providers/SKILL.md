---
name: hermes-model-providers
description: Switch Hermes model; config.yaml is write-protected.
version: 1
author: hermes-agent
license: mit
metadata:
  hermes:
    tags: [hermes, model-config, azure-openai, azure-foundry, llm-providers]
    related_skills: [overseas-model-hub, model-router, ai-cloud-hub]
---

# Hermes Model Providers

## When to Use
- User asks to change the Hermes default model or provider (Azure OpenAI,
  OpenAI-compatible `base_url`, Nous, OpenRouter, etc.).
- A `patch`/`write_file` on `~/.hermes/config.yaml` is refused with
  "Refusing to write to Hermes config file" — use `hermes config set` instead.
- Wiring a paid/enterprise model (e.g. Azure `gpt-5-mini`) as Hermes' backend.


Use when the user wants Hermes to talk to a model backend other than the bundled
free defaults — Azure OpenAI (azure-foundry), a custom OpenAI-compatible
`base_url`, or simply to change the default model. ALSO use when a `patch` or
`write_file` on `~/.hermes/config.yaml` is refused ("Refusing to write to Hermes
config file").

## Key constraint: config.yaml is WRITE-PROTECTED
Hermes refuses direct edits to `~/.hermes/config.yaml` — both the `patch` tool
and `write_file` bounce with "Refusing to write to Hermes config file: ...
Agent cannot modify security-sensitive configuration." **Always edit model
config via the CLI:**
```
hermes config set model.provider azure-foundry
hermes config set model.default gpt-5-mini
hermes config set model.base_url "https://<res>.openai.azure.com/openai/v1"
hermes config set model.api_mode chat_completions
hermes config get model.default
```
Nested/list values (e.g. `model.fallback_providers`) can't be set in one
`config set` call. Leave them as-is, or hand-edit offline only with the user's
explicit go-ahead (state the protection first).

## Azure OpenAI via the native `azure-foundry` provider (verified end-to-end)
Hermes has FIRST-CLASS support for Azure OpenAI / Microsoft Foundry — do NOT
build a proxy for the OpenAI-shaped route unless you specifically need the
Anthropic Messages surface (e.g. for Claude Code). Recipe:
```
model:
  provider: azure-foundry
  base_url: https://<resource>.openai.azure.com/openai/v1
  api_mode: chat_completions
  default: gpt-5-mini            # the DEPLOYMENT name, not the family
  fallback_providers:            # keep free models as a zero-cost guardrail
    - provider: nous
      model: tencent/hy3:free
    - provider: openrouter
      model: z-ai/glm-5.2:free
```
- API key goes in `~/.hermes/.env` as `AZURE_FOUNDRY_API_KEY=<key>` (env var
  name confirmed by `hermes_cli/auth.py` ProviderConfig; `AZURE_FOUNDRY_BASE_URL`
  is the fallback for the URL).
- Hermes AUTO-HANDLES the Azure gotchas: it detects `openai.azure.com` and forces
  `chat_completions` (gpt-5 on Azure 404s on `/responses`), it sends
  `max_completion_tokens` for gpt-4o/5.x, and forwards `api-version` via
  `default_query`. No custom proxy needed for the OpenAI-shaped route.
- `default` MUST be the deployment name exactly as in the Azure portal
  (e.g. `gpt-5-mini`, not `gpt-5`). Versioned aliases also work
  (`gpt-5-mini-2025-08-07`).
- See `references/azure-foundry-recipe.md` for the full probe + verification
  script used to validate this.

## Verify before declaring success
1. Probe with the raw SDK (confirms key + URL + lists deployments):
   `OpenAI(api_key=KEY, base_url=URL).models.list()` → returns models.
2. Real chat completion through Hermes: `hermes -z "用一句话介绍你自己"`
   should return model text. This also proves the new default is live for
   NEW sessions (see pitfall below).

## Pitfalls
- **Config change does NOT affect the already-running session.** A session
  started before the edit still runs the old model. Only NEW sessions (new
  `hermes chat`, a fresh `hermes -z`, or a new gateway turn after
  `systemctl --user restart hermes-gateway.service`) pick up the new default.
  Always verify with a fresh invocation and tell the user the current session
  is unaffected.
- **gpt-5-mini is a REASONING model.** With the raw Azure SDK, a small
  `max_completion_tokens` (e.g. 50) lets `reasoning_tokens` eat the whole budget
  and `content` comes back EMPTY (`finish_reason: length`). Verified: budget 50
  → empty; budget 2000 → normal Chinese output. Hermes sizes this from context
  automatically, but when scripting raw SDK calls, give a large budget.
- **Never touch the user's Azure budget.** Configuring the model is fine; never
  auto-stop resources or rotate/grant full AK. The user owns Budget/ActionGroup
  in the Azure portal. Keep Azure as an explicit, opt-in model — it is NOT in
  the automatic free fallback chain unless the user asks.
- **Don't paste secrets into scripts or logs.** Read the key from the user's
  secret store (e.g. a local secure file) into an env var; print only length.

## Out of scope / not covered here
- CC→Azure proxy (`cc2azure.py`) for Claude Code — that is a separate,
  user-specific setup (Anthropic→Azure translation). This skill is about Hermes'
  own model config only.
- Feishu/Lark bitable read-write — requires the app to hold `bitable:app`
  scope; the relevant anchnet app lacked it this session, so no validated
  write recipe exists yet.
