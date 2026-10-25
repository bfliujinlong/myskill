#!/usr/bin/env python3
"""
model-discovery-discover.py — Discover and update free LLM API platform catalog.

Sources (in priority order):
  1. mnfst/awesome-free-llm-apis data.json (primary curated list)
  2. OpenRouter free models blog/ranking (supplemental)
  3. Retained user-added entries from ~/.hermes/model-discovery/config.yaml

Outputs:
  ~/.hermes/model-discovery/catalog.json  — merged, de-duplicated platform list
  ~/.hermes/model-discovery/last_update.log — run timestamp + source notes
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

HERMES_DIR = Path.home() / ".hermes"
DISCOVERY_DIR = HERMES_DIR / "model-discovery"
CONFIG_FILE = DISCOVERY_DIR / "config.yaml"
CATALOG_FILE = DISCOVERY_DIR / "catalog.json"
LOG_FILE = DISCOVERY_DIR / "last_update.log"

PRIMARY_SOURCE_URL = "https://raw.githubusercontent.com/mnfst/awesome-free-llm-apis/main/data.json"
PRIMARY_SOURCE_FALLBACK = "https://raw.githubusercontent.com/mnfst/awesome-free-llm-apis/main/README.md"

REQUEST_TIMEOUT = 20  # seconds


def http_get(url: str, timeout: int = REQUEST_TIMEOUT) -> str | None:
    """Fetch URL content with timeout. Returns None on failure."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Hermes-ModelDiscovery/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status != 200:
                return None
            return resp.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError):
        return None


def load_user_config() -> dict:
    """Load user config.yaml if present. Returns dict with optional 'custom_platforms' key."""
    if not CONFIG_FILE.exists():
        return {}
    try:
        import yaml
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data if isinstance(data, dict) else {}
    except ImportError:
        # PyYAML not available — skip user additions in discovery
        print("WARNING: PyYAML not installed; skipping user config merge", file=sys.stderr)
        return {}
    except Exception as e:
        print(f"WARNING: Failed to read config.yaml: {e}", file=sys.stderr)
        return {}


def fetch_primary_catalog() -> dict | None:
    """Fetch mnfst/awesome-free-llm-apis data.json."""
    text = http_get(PRIMARY_SOURCE_URL)
    if text is None:
        print(f"WARNING: Failed to fetch {PRIMARY_SOURCE_URL}", file=sys.stderr)
        return None
    try:
        data = json.loads(text)
        if not isinstance(data, dict) or "providers" not in data:
            print("WARNING: data.json has unexpected structure", file=sys.stderr)
            return None
        return data
    except json.JSONDecodeError as e:
        print(f"WARNING: data.json parse error: {e}", file=sys.stderr)
        return None


def normalize_provider(p: dict) -> dict:
    """Normalize a provider record from data.json into our catalog schema."""
    country = p.get("country", "UNKNOWN")
    base_url = p.get("baseUrl", "")
    models = p.get("models", [])
    model_names = [m.get("id", "") for m in models if m.get("id")]
    description = p.get("description", "")
    url = p.get("url", "")

    return {
        "name": p.get("name", ""),
        "country": country,
        "flag": p.get("flag", ""),
        "url": url,
        "base_url": base_url,
        "api_type": p.get("category", "unknown"),  # "provider_api" or "inference_provider"
        "description": description,
        "models": model_names,
        "needs_api_key": _infer_key_requirement(base_url, description),
        "rate_limit_note": _extract_rate_note(description),
        "eu_accessible": _eu_accessible_flag(country, base_url),
        "last_seen": datetime.now(timezone.utc).isoformat(),
    }


def _infer_key_requirement(base_url: str, description: str) -> bool:
    """Guess whether a platform needs an API key from its metadata.

    When in doubt, returns True (safer — user must confirm).
    """
    if not base_url:
        return True
    # Known keyless endpoints (from the curated list)
    keyless_hints = [
        "ovhcloud.com",  # OVH anonymous tier
    ]
    desc_lower = (description or "").lower()
    if "no api key" in desc_lower or "anonymous" in desc_lower:
        return False
    if "no credit card" in desc_lower and "signup" in desc_lower:
        return False
    for hint in keyless_hints:
        if hint in base_url:
            return False
    return True


def _extract_rate_note(description: str) -> str:
    """Pull the rate-limit sentence from a provider description."""
    s = (description or "")
    # Take first sentence-ish
    for sep in [". ", ".\n", "\n"]:
        if sep in s:
            return s.split(sep)[0].strip()
    return s.strip()


def _eu_accessible_flag(country: str, base_url: str) -> bool | None:
    """Return True if EU-hosted or known accessible from EU.

    Returns None when uncertain (user should test).
    """
    eu_countries = {"FR", "DE", "NL", "BE", "IE", "SE", "FI", "DK", "AT", "IT", "ES", "PT", "PL", "CZ", "EE", "LT", "LV"}
    if country in eu_countries:
        return True
    # US-hosted but widely accessible
    if country == "US":
        return True  # most US providers reachable from DE; test confirms
    if country == "CN":
        return False  # China-hosted likely blocked from DE without proxy
    return None  # unknown — needs probe


def merge_catalog(primary: dict | None, user_config: dict) -> list[dict]:
    """Merge primary source + user custom entries into one list."""
    platforms: dict[str, dict] = {}

    # Primary source first
    if primary:
        for p in primary.get("providers", []):
            norm = normalize_provider(p)
            if norm["name"]:
                platforms[norm["name"].lower()] = norm

    # User custom entries (override / supplement)
    custom = user_config.get("custom_platforms", [])
    if isinstance(custom, list):
        for p in custom:
            if not isinstance(p, dict) or not p.get("name"):
                continue
            name = p["name"]
            entry: dict = {
                "name": name,
                "country": p.get("country", "CUSTOM"),
                "flag": p.get("flag", ""),
                "url": p.get("url", ""),
                "base_url": p.get("base_url", ""),
                "api_type": p.get("api_type", "custom"),
                "description": p.get("description", ""),
                "models": p.get("models", []),
                "needs_api_key": p.get("needs_api_key", True),
                "rate_limit_note": p.get("rate_limit_note", ""),
                "eu_accessible": p.get("eu_accessible", None),
                "custom": True,
                "last_seen": datetime.now(timezone.utc).isoformat(),
            }
            platforms[name.lower()] = entry

    return list(platforms.values())


def write_catalog(platforms: list[dict]) -> None:
    """Write catalog.json with restricted permissions (owner read/write only)."""
    DISCOVERY_DIR.mkdir(parents=True, exist_ok=True)
    tmp = CATALOG_FILE.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({"last_updated": datetime.now(timezone.utc).isoformat(), "platforms": platforms}, f, indent=2, ensure_ascii=False)
    os.replace(tmp, CATALOG_FILE)
    os.chmod(CATALOG_FILE, stat.S_IRUSR | stat.S_IWUSR)  # 0o600


def write_log(primary_ok: bool, platform_count: int, note: str = "") -> None:
    """Append a run summary line to last_update.log."""
    DISCOVERY_DIR.mkdir(parents=True, exist_ok=True)
    line = (
        f"[{datetime.now(timezone.utc).isoformat()}] "
        f"primary_source={'OK' if primary_ok else 'FAIL'} "
        f"platforms={platform_count} "
        f"{note}\n"
    )
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line)


def main() -> int:
    print("=== Model Discovery — fetching primary source ===")
    start = time.time()
    primary = fetch_primary_catalog()
    elapsed = time.time() - start
    primary_ok = primary is not None
    print(f"Primary source: {'OK' if primary_ok else 'FAIL'} ({elapsed:.1f}s)")

    user_config = load_user_config()
    custom_count = len(user_config.get("custom_platforms", []))
    print(f"User custom entries: {custom_count}")

    platforms = merge_catalog(primary, user_config)
    print(f"Merged catalog: {len(platforms)} platforms")

    write_catalog(platforms)

    note = ""
    if custom_count:
        note += f" custom={custom_count}"
    if elapsed > 10:
        note += f" slow_fetch={elapsed:.1f}s"
    write_log(primary_ok, len(platforms), note)

    print(f"Catalog written to {CATALOG_FILE}")
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
