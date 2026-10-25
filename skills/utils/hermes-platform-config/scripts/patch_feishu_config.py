#!/usr/bin/env python3
"""
Patch Hermes config.yaml and channel_directory.json to add a Feishu platform.

Usage:
    python patch_feishu_config.py [--app-id CLI_APP_ID] [--app-secret APP_SECRET]
                                 [--domain feishu|lark] [--mode websocket|webhook]

Defaults read from environment variables FEISHU_APP_ID and FEISHU_APP_SECRET if not provided.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone

import yaml


HERMES_HOME = os.path.expanduser("~/.hermes")
CONFIG_PATH = os.path.join(HERMES_HOME, "config.yaml")
CHANNEL_DIR_PATH = os.path.join(HERMES_HOME, "channel_directory.json")


def load_yaml(path: str) -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f) or {}


def save_yaml(path: str, data: dict) -> None:
    with open(path, "w") as f:
        yaml.dump(
            data,
            f,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
        )


def load_json(path: str) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def save_json(path: str, data: dict) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def patch_config(app_id: str, app_secret: str, domain: str, mode: str) -> dict:
    config = load_yaml(CONFIG_PATH)
    config.setdefault("platforms", {})

    config["platforms"]["feishu"] = {
        "app_id": app_id,
        "app_secret": app_secret,
        "domain": domain,
        "connection_mode": mode,
        "text_batch_delay_seconds": 0.6,
        "text_batch_max_messages": 8,
        "text_batch_max_chars": 4000,
        "media_batch_delay_seconds": 0.8,
        "require_mention": True,
        "group_policy": "allowlist",
        "allowed_users": [],
        "ws_reconnect_interval": 120,
    }

    save_yaml(CONFIG_PATH, config)
    print(f"✓ config.yaml updated — Feishu platform added (domain={domain}, mode={mode})")
    return config


def patch_channel_dir() -> dict:
    channel_dir = load_json(CHANNEL_DIR_PATH)
    channel_dir.setdefault("platforms", {})

    if "feishu" not in channel_dir["platforms"]:
        channel_dir["platforms"]["feishu"] = [
            {
                "id": "default",
                "name": "Feishu Home",
                "type": "dm",
                "thread_id": None,
            }
        ]
        print("✓ channel_directory.json updated — Feishu platform registered")
    else:
        print("ℹ channel_directory.json already has a Feishu entry — skipping")

    channel_dir["updated_at"] = datetime.now(timezone.utc).isoformat()
    save_json(CHANNEL_DIR_PATH, channel_dir)
    return channel_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Patch Hermes Feishu platform config")
    parser.add_argument("--app-id", default=os.environ.get("FEISHU_APP_ID"), help="Feishu App ID")
    parser.add_argument("--app-secret", default=os.environ.get("FEISHU_APP_SECRET"), help="Feishu App Secret")
    parser.add_argument("--domain", default="feishu", choices=["feishu", "lark"], help="Domain (default: feishu)")
    parser.add_argument("--mode", default="websocket", choices=["websocket", "webhook"], help="Connection mode (default: websocket)")
    args = parser.parse_args()

    if not args.app_id or not args.app_secret:
        print("ERROR: --app-id and --app-secret are required (or set FEISHU_APP_ID / FEISHU_APP_SECRET env vars)", file=sys.stderr)
        sys.exit(1)

    patch_config(args.app_id, args.app_secret, args.domain, args.mode)
    patch_channel_dir()
    print("\nDone. Restart the gateway from an external shell: sudo systemctl restart hermes-gateway")


if __name__ == "__main__":
    main()
