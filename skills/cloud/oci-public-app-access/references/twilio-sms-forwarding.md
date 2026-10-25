# Twilio SMS → Telegram Forwarder via Cloudflare Tunnel

## Use case
Forward SMS received by a Twilio US number to a Telegram chat, so the user can receive verification codes on their domestic phone.

## Architecture

```
Twilio US number → Cloudflare Tunnel (sms.domain.com) → Local Python HTTP server → Telegram Bot API
```

## Setup steps

### 1. Create the forwarder script

```python
# /home/ubuntu/twilio-forward/sms_forwarder.py
import os, json, logging, http.server, urllib.request, urllib.parse, ssl

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
LISTEN_PORT = int(os.getenv('TWILIO_LISTEN_PORT', '9999'))

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = json.dumps({"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read()).get("ok", False)

class TwilioHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode('utf-8')
        params = urllib.parse.parse_qs(body)
        from_num = params.get('From', [''])[0]
        to_num = params.get('To', [''])[0]
        msg = params.get('Body', [''])[0]
        send_telegram(f"📨 <b>新短信 ({to_num})</b>\n来自: {from_num}\n内容: <code>{msg}</code>")
        self.send_response(200)
        self.send_header('Content-Type', 'application/xml')
        self.end_headers()
        self.wfile.write(b'<?xml version="1.0"?><Response></Response>')

http.server.HTTPServer(('0.0.0.0', LISTEN_PORT), TwilioHandler).serve_forever()
```

### 2. Add Cloudflare tunnel route

```yaml
# /home/ubuntu/.cloudflared/config.yml
ingress:
  - hostname: sms.aihubcloud.cn
    service: http://127.0.0.1:9999
  - service: http_status:404
```

Restart: `sudo systemctl restart cloudflared.service`

### 3. Configure Twilio webhook

```bash
curl -s -X POST "https://api.twilio.com/2010-04-01/Accounts/<SID>/IncomingPhoneNumbers/<PN_SID>.json" \
  -u "<SID>:<AUTH_TOKEN>" \
  -d "SmsUrl=https%3A%2F%2Fsms.aihubcloud.cn%2F"
```

### 4. Run the forwarder

```bash
cd /home/ubuntu/twilio-forward
TELEGRAM_BOT_TOKEN=*** TELEGRAM_CHAT_ID=*** TWILIO_LISTEN_PORT=9999 \
  /data/hermes-install/venv/bin/python3 sms_forwarder.py &
```

## Pitfall: nohup kills background processes

`nohup python3 script.py &` may get killed when the parent shell exits. Use systemd or `setsid` for long-running services.

## Pitfall: Twilio numbers are VoIP

Twilio numbers are marked as `voip` in carrier databases. High-security platforms (Palantir, NVIDIA, etc.) reject VoIP numbers for verification. Use TextVerified (non-VoIP) or a real US SIM for those services.

## Pitfall: cloudflared config.yml editing

After editing `/home/ubuntu/.cloudflared/config.yml`, must restart: `sudo systemctl restart cloudflared.service`. The running cloudflared process does not auto-reload config.
