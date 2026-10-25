#!/usr/bin/env python3
"""
model-discovery-probe.py — Probe discovered platforms for real accessibility
from the CURRENT host (France / Paris OCI / aarch64).

For each platform in the catalog, this script attempts a synthetic minimal call
to determine:

  - network reachability (DNS + TCP connect + TLS handshake succeed?)
  - whether the endpoint returns a valid OpenAI-compatible response (or equivalent)
  - approximate latency (time to first token / total)
  - whether authentication is required / whether the key works

Results are written to:
  ~/.hermes/model-discovery/probes.json  (0600)
  appended to ~/.hermes/model-discovery/last_update.log

IMPORTANT LIMITATIONS:
  - This script does NOT register accounts or obtain API keys.
  - Platforms that require an API key will be probed WITHOUT a key first to
    detect the auth-error signature; if the user has stored a key in config.yaml,
    that key is used for a second authenticated probe.
  - Some platforms (especially China-hosted) may be unreachable from Paris.
    The script records this as "unreachable" rather than guessing.
  - Rate limits apply: the script throttles itself to avoid exhausting free quotas.
"""

import json
import os
import stat
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HERMES_DIR = Path.home() / ".hermes"
DISCOVERY_DIR = HERMES_DIR / "model-discovery"
CATALOG_FILE = DISCOVERY_DIR / "catalog.json"
PROBES_FILE = DISCOVERY_DIR / "probes.json"
LOG_FILE = DISCOVERY_DIR / "last_update.log"

# Minimal prompt used for all probes (short, cheap, deterministic)
PROBE_PROMPT = "Say exactly: hello"
PROBE_MAX_TOKENS = 16
REQUEST_TIMEOUT = 25  # seconds per probe
MIN_DELAY_BETWEEN_PROBES = 3.0  # seconds, to avoid hammering free tiers

# Endpoints that are known to be OpenAI-compatible
OPENAI_COMPATIBLE_MODELS = {
    "https://api.openai.com/v1",
    "https://api.mistral.ai/v1",
    "https://api.groq.com/openai/v1",
    "https://api.cerebras.ai/v1",
    "https://api.cohere.com/v2",
    "https://openrouter.ai/api/v1",
    "https://api.aionlabs.ai/v1",
    "https://api.z.ai/api/paas/v4",
    "https://open.bigmodel.cn/api/paas/v4",
    "https://integrate.api.nvidia.com/v1",
}


def http_post(url: str, payload: dict, api_key: str | None = None, timeout: int = REQUEST_TIMEOUT) -> dict:
    """Make a POST request. Returns {"success": bool, "error": str, "latency_s": float, "status_code": int}."""
    start = time.time()
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={
        "Content-Type": "application/json",
        "Accept": "application/json",
    })
    if api_key:
        req.add_header("Authorization", f"Bearer {api_key}")

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            latency = time.time() - start
            body = resp.read().decode("utf-8", errors="replace")
            return {
                "success": True,
                "status_code": resp.status,
                "latency_s": round(latency, 3),
                "body_preview": body[:300],
            }
    except urllib.error.HTTPError as e:
        latency = time.time() - start
        body = e.read().decode("utf-8", errors="replace")[:300]
        return {
            "success": False,
            "status_code": e.code,
            "latency_s": round(latency, 3),
            "error": f"HTTP {e.code}: {body}",
        }
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        latency = time.time() - start
        return {
            "success": False,
            "status_code": 0,
            "latency_s": round(latency, 3),
            "error": f"Network: {e!r}",
        }


def is_openai_compatible(base_url: str) -> bool:
    """Heuristic: does the base_url look OpenAI-compatible?"""
    for known in OPENAI_COMPATIBLE_MODELS:
        if base_url.startswith(known):
            return True
    # Generic heuristic: ends with /v1 or /v1/
    return base_url.rstrip("/").endswith("/v1")


def build_probe_payload(base_url: str, model: str | None = None) -> dict:
    """Build the JSON body for a minimal chat completion request."""
    model_id = model or "unknown"
    if is_openai_compatible(base_url):
        return {
            "model": model_id,
            "messages": [{"role": "user", "content": PROBE_PROMPT}],
            "max_tokens": PROBE_MAX_TOKENS,
            "temperature": 0.0,
        }
    else:
        # Generic fallback — may not work for non-OpenAI endpoints
        return {
            "prompt": PROBE_PROMPT,
            "max_tokens": PROBE_MAX_TOKENS,
        }


def build_probe_url(base_url: str, model: str) -> str:
    """Build the full POST URL for a probe.

    OpenAI-compatible endpoints expect POST /chat/completions.
    Non-compatible endpoints: probe at base_url directly (best-effort).
    """
    if is_openai_compatible(base_url):
        return f"{base_url.rstrip('/')}/chat/completions"
    return base_url


def probe_platform(platform: dict, api_key: str | None) -> dict:
    """Probe a single platform. Returns a results dict."""
    name = platform.get("name", "unknown")
    base_url = platform.get("base_url", "")
    models = platform.get("models", [])

    # Try the first listed model, or fall back to a plausible default
    model = models[0] if models else "unknown"

    result: dict[str, Any] = {
        "platform": name,
        "base_url": base_url,
        "model_probed": model,
        "api_key_used": bool(api_key),
        "probes": [],
    }

    if not base_url:
        result["probes"].append({"attempt": "no_base_url", "success": False, "error": "no base_url configured"})
        return result

    # Build the URL and OpenAI-compatible payload
    url = build_probe_url(base_url, model)
    payload = build_probe_payload(base_url)
    if is_openai_compatible(base_url):
        payload["model"] = model

    # Attempt 1: unauthenticated (to detect auth requirement)
    r1 = http_post(url, payload, api_key=None)
    result["probes"].append({"attempt": "unauth", **r1})

    # Attempt 2: authenticated if a key is available AND unauth didn't already succeed
    if api_key and (not r1["success"] or r1.get("status_code") in (401, 403)):
        r2 = http_post(url, payload, api_key=api_key)
        result["probes"].append({"attempt": "auth", **r2})

    # Summary
    successes = [p for p in result["probes"] if p.get("success")]
    if successes:
        best = min(successes, key=lambda p: p.get("latency_s", 999))
        result["reachable"] = True
        result["auth_required"] = not any(p.get("attempt") == "unauth" and p.get("success") for p in result["probes"])
        result["latency_ms"] = round(best.get("latency_s", 0) * 1000)
        result["status_code"] = best.get("status_code")
    else:
        result["reachable"] = False
        result["auth_required"] = None  # unknown
        result["latency_ms"] = None
        result["status_code"] = None

    return result


def load_catalog() -> list[dict]:
    if not CATALOG_FILE.exists():
        print(f"ERROR: catalog not found at {CATALOG_FILE}", file=sys.stderr)
        print("Run discover.py first.", file=sys.stderr)
        sys.exit(1)
    with open(CATALOG_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("platforms", [])


def load_user_keys() -> dict[str, str]:
    """Load API keys from config.yaml under 'api_keys' mapping (name -> key)."""
    CONFIG_FILE = DISCOVERY_DIR / "config.yaml"
    if not CONFIG_FILE.exists():
        return {}
    try:
        import yaml
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            keys = data.get("api_keys", {})
            # Only return keys that are non-empty strings
            return {k: v for k, v in keys.items() if isinstance(v, str) and v.strip()}
    except ImportError:
        print("WARNING: PyYAML not installed; cannot load user API keys", file=sys.stderr)
        return {}
    except Exception as e:
        print(f"WARNING: Failed to read API keys: {e}", file=sys.stderr)
        return {}


def write_probes(results: list[dict]) -> None:
    DISCOVERY_DIR.mkdir(parents=True, exist_ok=True)
    tmp = PROBES_FILE.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({
            "probed_at": datetime.now(timezone.utc).isoformat(),
            "results": results,
        }, f, indent=2, ensure_ascii=False)
    os.replace(tmp, PROBES_FILE)
    os.chmod(PROBES_FILE, stat.S_IRUSR | stat.S_IWUSR)


def write_log_note(note: str) -> None:
    DISCOVERY_DIR.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now(timezone.utc).isoformat()}] probe: {note}\n")


def main() -> int:
    print("=== Model Discovery — probing platforms from current host ===")
    platforms = load_catalog()
    print(f"Loaded {len(platforms)} platforms from catalog")

    keys = load_user_keys()
    if keys:
        print(f"Loaded {len(keys)} user API keys (names only, values hidden)")
    else:
        print("No user API keys loaded — will probe unauthenticated only")

    results = []
    for i, p in enumerate(platforms):
        name = p.get("name", "?")
        eu_flag = p.get("eu_accessible")
        eu_str = {True: "EU", False: "non-EU", None: "?"}.get(eu_flag, "?")
        print(f"\n[{i+1}/{len(platforms)}] {name} ({eu_str}) — {p.get('base_url', 'no URL')}")

        key = keys.get(name) or keys.get(name.lower())
        result = probe_platform(p, api_key=key)
        results.append(result)

        s = "REACHABLE" if result["reachable"] else "UNREACHABLE"
        auth = result.get("auth_required")
        auth_str = {True: "auth-required", False: "no-auth", None: "unknown"}.get(auth, "?")
        lat = result.get("latency_ms")
        lat_str = f"{lat}ms" if lat else "n/a"
        print(f"  -> {s} | auth: {auth_str} | latency: {lat_str}")

        if i < len(platforms) - 1:
            time.sleep(MIN_DELAY_BETWEEN_PROBES)

    write_probes(results)

    reachable = sum(1 for r in results if r["reachable"])
    log_note = f"probed={len(platforms)} reachable={reachable} keys_used={len([r for r in results if r.get('api_key_used')])}"
    write_log_note(log_note)

    print(f"\n=== Summary: {reachable}/{len(platforms)} reachable ===")
    print(f"Results written to {PROBES_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
