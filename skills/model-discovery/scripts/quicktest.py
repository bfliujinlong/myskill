#!/usr/bin/env python3
"""
model-discovery-quicktest.py — Lightweight single-endpoint probe for quick
manual verification when adding a new platform.

Usage:
  python model-discovery-quicktest.py <base_url> [api_key] [model_name]
  python model-discovery-quicktest.py --help

Exit code:
  0 — reachable (got a successful response)
  1 — unreachable or error
  2 — usage error
"""

import sys
import time
import json
import urllib.request
import urllib.error
from typing import Optional


PROBE_PROMPT = "Say exactly: hello"
PROBE_MAX_TOKENS = 16
REQUEST_TIMEOUT = 20


def is_openai_compatible(base_url: str) -> bool:
    known_prefixes = [
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
    ]
    for known in known_prefixes:
        if base_url.startswith(known):
            return True
    return base_url.rstrip("/").endswith("/v1")


def probe(base_url: str, api_key: Optional[str], model: str) -> dict:
    data: dict
    if is_openai_compatible(base_url):
        data = {
            "model": model,
            "messages": [{"role": "user", "content": PROBE_PROMPT}],
            "max_tokens": PROBE_MAX_TOKENS,
            "temperature": 0.0,
        }
    else:
        data = {
            "prompt": PROBE_PROMPT,
            "max_tokens": PROBE_MAX_TOKENS,
        }

    payload = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(base_url, data=payload, headers={
        "Content-Type": "application/json",
        "Accept": "application/json",
    })
    if api_key:
        req.add_header("Authorization", f"Bearer {api_key}")

    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
            latency = round((time.time() - start) * 1000)
            body = resp.read().decode("utf-8", errors="replace")
            return {
                "success": True,
                "status_code": resp.status,
                "latency_ms": latency,
                "body_preview": body[:400],
            }
    except urllib.error.HTTPError as e:
        latency = round((time.time() - start) * 1000)
        body = e.read().decode("utf-8", errors="replace")[:300]
        return {
            "success": False,
            "status_code": e.code,
            "latency_ms": latency,
            "error": f"HTTP {e.code}: {body}",
        }
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        latency = round((time.time() - start) * 1000)
        return {
            "success": False,
            "status_code": 0,
            "latency_ms": latency,
            "error": f"Network: {e!r}",
        }


def main() -> int:
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print("Usage: python model-discovery-quicktest.py <base_url> [api_key] [model_name]")
        print("  base_url   — API endpoint base URL (e.g. https://api.groq.com/openai/v1)")
        print("  api_key    — (optional) Bearer token")
        print("  model_name — (optional) model id; defaults to 'unknown'")
        return 2

    base_url = sys.argv[1].rstrip("/")
    api_key = sys.argv[2] if len(sys.argv) > 2 else None
    model = sys.argv[3] if len(sys.argv) > 3 else "unknown"

    print(f"Probing {base_url} ...")
    if api_key:
        print("Using API key: YES (value hidden)")
    else:
        print("Using API key: NO")

    result = probe(base_url, api_key, model)

    if result["success"]:
        print(f"✅ REACHABLE | HTTP {result['status_code']} | {result['latency_ms']}ms")
        print(f"Response preview: {result['body_preview'][:200]}")
        return 0
    else:
        print(f"❌ UNREACHABLE | {result['error']}")
        if result.get("status_code"):
            print(f"   HTTP status: {result['status_code']}")
        print(f"   Latency: {result['latency_ms']}ms")
        return 1


if __name__ == "__main__":
    sys.exit(main())
