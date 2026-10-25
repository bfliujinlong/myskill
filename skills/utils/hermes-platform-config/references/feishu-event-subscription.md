# Feishu Event Subscription Setup

Guide for setting up event subscription in the 飞书开发者控制台 to enable Hermes to receive messages.

## Required Events

For Hermes to receive and respond to messages, subscribe to:

### 1. `im.message.receive_v1` (Required)

This event fires when the bot receives a message in a chat it's in.

**Setup steps:**

1. Open [飞书开发者控制台](https://open.feishu.cn/)
2. Select your application
3. Navigate to **事件订阅** (Event Subscription)
4. Add event: `im.message.receive_v1`
5. Save and deploy

### 2. `card.action.trigger` (Optional)

Fires when a user interacts with a card (button click, form submission, etc.). Only needed if you use card UI elements.

**Setup steps:**

1. In **事件订阅**, add event: `card.action.trigger`
2. Configure the card actions you want to handle

## Verification

After configuring events:

1. In the developer console, use the **测试事件** (Test Event) feature to simulate events
2. Check that Hermes gateway logs show incoming events after restart
3. Send a real message to the bot in Feishu and verify it's received

## Common Issues

| Problem | Cause | Fix |
|---------|-------|-----|
| Bot doesn't receive messages | Event not subscribed | Add `im.message.receive_v1` in event subscription |
| Event not triggering | App not deployed | Save and deploy the event subscription config |
| Webhook mode not receiving | Public URL not accessible | Ensure webhook URL is publicly reachable, or switch to WebSocket mode |
| Message goes to other bot | `FEISHU_ALLOW_BOTS` misconfigured | Set to `none` (default) unless you need to handle other bots |

## WebSocket vs Webhook Mode

- **WebSocket** (`connection_mode: websocket`): No public IP needed. Hermes connects outbound to Feishu. Simpler setup.
- **Webhook** (`connection_mode: webhook`): Requires a publicly reachable URL. Feishu sends events to your URL. Use only if WebSocket is unavailable.
