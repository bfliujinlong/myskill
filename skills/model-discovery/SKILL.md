---
name: model-discovery
description: "Find free LLM APIs and probe reachability from this host."
version: 0.1.0
author: Jinlong Liu (jinlongliu), Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [llm, free-models, api, discovery, probe, devops]
    related_skills: [free-model-guard, model-router]
---

# Model Discovery Skill

Maintains a live catalogue of free / permanent-free LLM API platforms and checks which ones are actually reachable from this host (France / Paris OCI, aarch64).

**What it does:**
- Fetches the curated free-LLM-API list from `mnfst/awesome-free-llm-apis` (data.json) on every discovery run.
- Merges in your hand-added custom platforms and API keys from `~/.hermes/model-discovery/config.yaml`.
- Writes a machine-readable `catalog.json` of all known platforms (permission 0600).
- Probes each platform for real reachability + latency from the current host, with and without an API key.
- Writes `probes.json` (permission 0600) with per-platform test results.
- Prints a human-readable Markdown report sorted with EU-accessible / reachable platforms first.

**What it does NOT do:**
- Register accounts or create API keys for you.
- Pay for or waive real-name-verification requirements.
- Guarantee that a platform listed as "free" still gives free access — policies change; the probe is the source of truth.

---

## When to Use

- You want an up-to-date list of free LLM APIs you can call from Paris.
- You are comparing providers and want real latency numbers from your actual server.
- A platform you used yesterday quit working and you want to know which alternatives are live.
- You are setting up a new free endpoint and want to confirm it reaches the server before wiring it into your router.

**Don't use for:**
- Paying-for-promotion or commercial procurement decisions without verifying terms of service.
- Testing platforms that explicitly forbid automated probing in their ToS (the skill is gentle — minimal prompt, throttled — but the platform owner may still object).

---

## Prerequisites

- **Python 3.11+** with stdlib only for `discover.py`.
- **PyYAML** (`pip install pyyaml`) only if you want to maintain `config.yaml` with user keys / custom platforms. Without it, discovery still works (primary source only) and probes run unauthenticated.
- **Network egress** from this host to the platforms being probed (no VPN/proxy required unless the platform is geo-blocked — China-hosted ones are likely blocked from DE).
- **None** for read-only report generation once `catalog.json` and `probes.json` exist.

---

## How to Run

All paths are resolved relative to `~/.hermes/model-discovery/`.

### 1. Initialise the config and credential directory

```bash
# First time only — copy the template into place
cp ~/.hermes/skills/model-discovery/templates/config.yaml ~/.hermes/model-discovery/config.yaml
chmod 600 ~/.hermes/model-discovery/config.yaml

cp ~/.hermes/skills/model-discovery/templates/api_keys.yaml ~/.hermes/model-discovery/api_keys.yaml
chmod 600 ~/.hermes/model-discovery/api_keys.yaml
```

### 2. Discover the current platform list

```bash
python3 ~/.hermes/skills/model-discovery/scripts/discover.py
```

This writes:

- `~/.hermes/model-discovery/catalog.json` — merged platform list
- `~/.hermes/model-discovery/last_update.log` — run history

No API keys are needed for discovery.

### 3. Probe platforms from this host

```bash
python3 ~/.hermes/skills/model-discovery/scripts/probe.py
```

This writes:

- `~/.hermes/model-discovery/probes.json` — per-platform reachability + latency

If you have added API keys to `config.yaml` under `api_keys:`, probe.py will attempt authenticated probes for those platforms as well.

> **Probe policy:** minimal prompt (`"Say exactly: hello"`, 16 tokens), 3-second gap between probes, 25-second timeout. This is designed to be cheap and polite to free tiers.

### 4. Generate the report

```bash
python3 ~/.hermes/skills/model-discovery/scripts/report.py
# or save to a file:
python3 ~/.hermes/skills/model-discovery/scripts/report.py --output ~/free-llm-report.md
```

The report is sorted with reachable + EU-accessible platforms first.

### 5. Quick-test a single new endpoint manually

When you find a platform not yet in the catalogue and want a fast yes/no before adding it:

```bash
python3 ~/.hermes/skills/model-discovery/scripts/quicktest.py <base_url> [api_key] [model_name]
```

Example:

```bash
python3 ~/.hermes/skills/model-discovery/scripts/quicktest.py \
  https://api.groq.com/openai/v1 \
  "$GROQ_API_KEY" \
  llama-3.3-70b-versatile
```

Exit code 0 = reachable; 1 = unreachable.

---

## Quick Reference

| Step | Command | Needs keys? | Writes |
|---|---|---|---|
| Discover | `python3 .../discover.py` | No | `catalog.json` |
| Probe all | `python3 .../probe.py` | Optional | `probes.json` |
| Report | `python3 .../report.py` | No (reads catalog+probes) | stdout or file |
| Quick-test one | `python3 .../quicktest.py <url> [key] [model]` | Optional | stdout |
| Init config | `cp .../templates/config.yaml ~/.hermes/model-discovery/` | No | `config.yaml` |

---

## Procedure

### A. Daily automated refresh (cron)

1. Install PyYAML once if you use `config.yaml`:

   ```bash
   pip install pyyaml --quiet
   ```

2. Verify the scripts once manually:

   ```bash
   python3 ~/.hermes/skills/model-discovery/scripts/discover.py && \
   python3 ~/.hermes/skills/model-discovery/scripts/probe.py && \
   python3 ~/.hermes/skills/model-discovery/scripts/report.py -o ~/free-llm-report-$(date +%F).md
   ```

3. Install the cron job (runs daily at 06:00 UTC):

   ```bash
   cat <<'CRON' | crontab -
   # Her Mes model-discovery daily refresh
   0 6 * * * /home/ubuntu/.hermes/hermes-install/venv/bin/python3 \
     /home/ubuntu/.hermes/skills/model-discovery/scripts/discover.py \
     >> /home/ubuntu/.hermes/model-discovery/last_update.log 2>&1

   5 6 * * * /home/ubuntu/.hermes/hermes-install/venv/bin/python3 \
     /home/ubuntu/.hermes/skills/model-discovery/scripts/probe.py \
     >> /home/ubuntu/.hermes/model-discovery/last_update.log 2>&1
   CRON
   ```

   Adjust the timing so `probe.py` runs 5 minutes after `discover.py` finishes — probe needs the fresh catalog.

4. Ensure `HERMES_HOME` or the hardcoded path `~/.hermes` is correct; the scripts already use `Path.home() / ".hermes"` so no env var is required.

### B. Adding a platform manually (when discovery misses it)

1. Edit `~/.hermes/model-discovery/config.yaml`:

   ```yaml
   custom_platforms:
     - name: "MyNewProvider"
       country: "DE"          # ISO 3166-1 alpha-2 (optional)
       flag: "🇩🇪"            # emoji flag (optional)
       url: "https://myprovider.example.com/api-keys"
       base_url: "https://api.myprovider.example.com/v1"
       api_type: "provider_api"   # or "inference_provider" or "custom"
       description: "Pay-per-use, but a free trial of 1M tokens/month."
       models:
         - "my-provider/llama-3.3-70b"
         - "my-provider/qwen-2.5-72b"
       needs_api_key: true
       rate_limit_note: "10 RPM free tier"
       eu_accessible: true
   ```

   At minimum: `name` and `base_url`. Everything else helps the report and probe choose a model and decide whether to try unauthenticated first.

2. Add the API key if you have one:

   ```yaml
   api_keys:
     MyNewProvider: "sk-xxxxxxxxxxxxxxxxxxxxx"
   ```

3. Re-run discovery (which now merges your custom entry) and probe:

   ```bash
   python3 ~/.hermes/skills/model-discovery/scripts/discover.py
   python3 ~/.hermes/skills/model-discovery/scripts/probe.py
   python3 ~/.hermes/skills/model-discovery/scripts/report.py
   ```

### C. Rotating or revoking an API key

1. Edit `~/.hermes/model-discovery/config.yaml` and replace the value under `api_keys:`.
2. If the key is compromised, also revoke it on the provider side.
3. Re-run `probe.py` to confirm the new key works.
4. The old key is overwritten in-place — no separate deletion step. Ensure `config.yaml` itself is not in git history (it should be excluded by the skill's advice and your `.gitignore`).

---

## Probing Logic

- **Unauthenticated probe first.** Every platform is probed without a key. This tells us whether the endpoint is reachable at all AND whether it requires a key (401/403 vs network error vs success).
- **Authenticated probe second, only if:**
  - a key is available in `config.yaml`, AND
  - the unauthenticated probe failed with a 401/403 (suggesting auth is the only barrier), OR
  - the unauthenticated probe succeeded (to verify the key also works).
- **Model selection:** uses the first listed model from the catalog, or `"unknown"` if none is listed. `quicktest.py` lets you override the model on the command line.
- **Endpoint type detection:** OpenAI-compatible endpoints (`/v1` style) send a `chat.completions` style body. Non-compatible endpoints send a generic `prompt`-style body — these usually fail, which is informative.

---

## Pitfalls

- **"Reachable" ≠ "truly free".** A probe can succeed even if the free tier has expired or the provider silently switched to pay-only. Always read the provider's current pricing page; the catalog metadata is a snapshot.
- **China-hosted platforms (CN flag).** These are very likely blocked from Paris without a proxy. The skill marks them `eu_accessible: false` based on country; the probe will confirm. Direct connection will probably time out.
- **Google Gemini free tier:** the catalog notes say prompts may be used for training outside EU/UK/EEA. For a German host, verify current Google's geo-policy before sending sensitive data.
- **Mistral free mode:** free-mode input/output may be used for training unless you opt out. The catalog metadata mentions this.
- **Probe throttling:** the 3-second gap between probes is a floor, not a ceiling. If you have many platforms, a full probe cycle can take ~2 minutes. Do not reduce the delay below 1 second without understanding each provider's free-tier rate limit.
- **PyYAML missing:** if `pyyaml` is not installed, `discover.py` and `probe.py` will skip loading `config.yaml` user entries and keys. They still work (primary source + unauthenticated probes only). Install `pyyaml` to enable the full workflow.
- **Keys in `config.yaml`** are stored as plaintext YAML unless you encrypt the file externally with `age`/`gpg`. The skill recommends 0600 permissions and git exclusion, but does not enforce encryption automatically.
- **Cron environment:** cron runs with a minimal PATH. The cron examples above use the absolute path to the Hermes venv python (`/home/ubuntu/.hermes/hermes-install/venv/bin/python3`). If your Hermes install moves, update the cron line.

---

## Verification

After a full cycle, confirm:

1. `catalog.json` exists and contains at least the platforms from the primary source.
2. `probes.json` exists and contains one result per platform in `catalog.json`.
3. The report (`report.py` stdout or `--output` file) lists platforms with reachable indicators.
4. At least one EU-hosted platform (e.g. Mistral / OVHcloud / OVH) shows as reachable if your host has unfettered internet.
5. Custom entries appear in the report with the "User-added custom entry" marker.

To run a self-check non-interactively:

```bash
python3 ~/.hermes/skills/model-discovery/scripts/discover.py && \
python3 ~/.hermes/skills/model-discovery/scripts/probe.py && \
python3 ~/.hermes/skills/model-discovery/scripts/report.py | head -30
```

Expected: a Markdown report with a "Summary" section and at least one "### 🇫🇷 Mistral AI" or similar entry near the top if reachable.

---

## Security Notes

- **API key storage:** keys live in `~/.hermes/model-discovery/config.yaml` or `api_keys.yaml`, permission 0600. These files are NOT committed anywhere by the skill. You are responsible for excluding them from any dotfiles/git repo.
- **Never paste keys into chat.** When asking Hermes for help with a platform, describe the problem without including the key. The skill's scripts read keys only from the config files on disk.
- **Stronger protection:** encrypt the config file with age or gpg, and extend the scripts (or wrap them) to decrypt on the fly. The skill's current scripts do not do this automatically — that is a future enhancement you can contribute.
- **Probe privacy:** the probe prompt is hard-coded as `"Say exactly: hello"` — no user data ever enters a probe. Do not modify `probe.py` to send real prompts without understanding the privacy policy of each provider.
- **Logs:** `last_update.log` contains only timing + platform counts; no keys or request bodies.
