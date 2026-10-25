# Feishu/Lark Environment Variables

Complete list of environment variables for the Hermes Feishu/Lark platform adapter.

## Required

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `FEISHU_APP_ID` | ✅ | — | Feishu/Lark App ID (format: `cli_xxx`) |
| `FEISHU_APP_SECRET` | ✅ | — | Feishu/Lark App Secret |

## Connection

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `FEISHU_DOMAIN` | — | `feishu` | `feishu` (China) or `lark` (international) |
| `FEISHU_CONNECTION_MODE` | — | `websocket` | `websocket` or `webhook` |

## Access Control

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `FEISHU_ALLOWED_USERS` | — | (empty) | Comma-separated open_id whitelist |
| `FEISHU_ALLOW_BOTS` | — | `none` | Accept other bot messages: `none`, `mentions`, `all` |
| `FEISHU_REQUIRE_MENTION` | — | `true` | Group messages must @bot |
| `FEISHU_GROUP_POLICY` | — | `allowlist` | Group policy: `open`, `allowlist`, `disabled` |
| `FEISHU_BOT_OPEN_ID` | — | (empty) | Bot's open_id (for @mention detection) |
| `FEISHU_BOT_USER_ID` | — | (empty) | Bot's user_id (for @mention detection) |
| `FEISHU_BOT_NAME` | — | (empty) | Bot's display name (for @mention detection) |

## Webhook Mode (optional)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `FEISHU_WEBHOOK_HOST` | — | `127.0.0.1` | Webhook server bind address |
| `FEISHU_ENCRYPT_KEY` | — | (empty) | Webhook signature verification encrypt key |
| `FEISHU_VERIFICATION_TOKEN` | — | (empty) | Webhook payload auth verification token |

## Batch Processing

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `HERMES_FEISHU_TEXT_BATCH_DELAY_SECONDS` | — | `0.6` | Silent period before batching text messages |
| `HERMES_FEISHU_TEXT_BATCH_MAX_MESSAGES` | — | `8` | Max messages per text batch |
| `HERMES_FEISHU_TEXT_BATCH_MAX_CHARS` | — | `4000` | Max chars per text batch |
| `HERMES_FEISHU_MEDIA_BATCH_DELAY_SECONDS` | — | `0.8` | Silent period before batching media |

## WebSocket Tuning

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `HERMES_FEISHU_WS_RECONNECT_INTERVAL` | — | `120` | Reconnect attempt interval (seconds) |
| `HERMES_FEISHU_WS_PING_INTERVAL` | — | (SDK default) | WebSocket ping interval (seconds) |

## Deduplication

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `HERMES_FEISHU_DEDUP_CACHE_SIZE` | — | `2048` | Seen message ID cache size |

## Reactions

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `FEISHU_REACTIONS` | — | `true` | Show Typing/CrossMark reactions during processing |

## Delivery

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `FEISHU_HOME_CHANNEL` | — | — | Chat ID for cron/notification output |
