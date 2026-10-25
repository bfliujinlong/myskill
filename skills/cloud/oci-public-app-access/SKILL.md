---
name: oci-public-app-access
description: "Expose a local web app on OCI Always Free VM to the internet"
version: "1.0"
author: hermes-agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [oci, networking, security-list, iptables, public-access]
    related_skills: [oci-always-free-ops, dsh-deploy]
---

# Public App Access on OCI Always Free VM

## When to use
- Deploy a web app (OpenMAIC, dsh, Node/Python service) on OCI Always Free VM
- App runs on localhost but `curl http://<public-ip>:<port>` times out or returns 000

## The three layers that must ALL pass

```
Browser → OCI Security List → Host iptables → App listen address
```

## Step 1: Find the security list

```bash
INSTANCE_OCID=<instance_ocid>
VNIC_OCID=$(oci compute vnic-attachment list --compartment-id <tid> --instance-id $INSTANCE_OCID --query 'data[0]."vnic-id"' --raw-output)
SUBNET_OCID=$(oci network vnic get --vnic-id $VNIC_OCID --query 'data."subnet-id"' --raw-output)
SL_OCID=$(oci network subnet get --subnet-id $SUBNET_OCID --query 'data."security-list-ids"[0]' --raw-output)
```

## Step 2: Check for NSG vs Security List

```bash
oci network subnet get --subnet-id $SUBNET_OCID | python3 -c "import sys,json;d=json.load(sys.stdin)['data'];print('NSGs:',d.get('nsg-ids',[]));print('SLs:',d.get('security-list-ids',[]))"
```
- If NSG: `oci network nsg rules add` (additive, safe)
- If Security List: `oci network security-list update --force` (replaces ALL rules)

## Step 3: Add the port

**Security List** (⚠️ include SSH 22 or you get locked out):
```bash
oci network security-list update \
  --security-list-id $SL_OCID \
  --ingress-security-rules '[{"protocol":6,"source":"0.0.0.0/0","tcp-options":{"destination-port-range":{"max":3000,"min":3000}}},{"protocol":6,"source":"0.0.0.0/0","tcp-options":{"destination-port-range":{"max":22,"min":22}}}]' \
  --force
```

**NSG** (additive):
```bash
oci network nsg rules add --nsg-id <nsg> --direction=INGRESS --protocol=6 --source=0.0.0.0/0 --destination-port-range=3000-3000
```

## Step 4: Open host iptables

```bash
sudo iptables -L INPUT -n --line-numbers
# Find the REJECT rule, insert BEFORE it
sudo iptables -I INPUT 4 -p tcp --dport 3000 -j ACCEPT
```

**Persist**: `sudo apt install iptables-persistent && sudo netfilter-persistent save`

## Step 5: Configure app listen address

| Scenario | Config |
|---|---|
| Direct access | `--host 0.0.0.0` |
| nginx proxy | App on `127.0.0.1:<port>`, nginx on `:80` |
| Cloudflare tunnel | No port opening, use tunnel URL |

**dsh specific**: change `--host 127.0.0.1` to `--host 0.0.0.0` + add `--trusted-host <public-ip>` in `/etc/systemd/system/dsh.service`

## Step 6: Verify

```bash
curl -s -o /dev/null -w "%{http_code}" http://<public-ip>:<port>/
# 200 = success; 000 = still blocked
```

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Works locally, times out outside | iptables | Add rule before REJECT |
| HTTP 403 | Trust fence | Add IP to app's trusted-host |
| Connection refused | App not listening | Check `ss -tlnp` |

## Cloudflare named tunnel: expose any local HTTP service (webhooks, APIs, SMS forwarders)

Named tunnels can expose **any** local HTTP service — not just web apps. Used in this session to expose a Twilio SMS webhook forwarder:

```yaml
# /home/ubuntu/.cloudflared/config.yml
ingress:
  - hostname: sms.aihubcloud.cn
    service: http://127.0.0.1:9999
  - service: http_status:404
```

After editing, restart: `sudo systemctl restart cloudflared.service`

Then external services (Twilio, Stripe, etc.) can send webhooks to `https://sms.aihubcloud.cn/` and the tunnel routes them to your local service.

**Requirements:**
- Domain must be on Cloudflare (aihubcloud.cn is)
- Tunnel must be running (`systemctl status cloudflared`)
- Local service must listen on the specified port

## Cloudflare quick tunnel (UNRELIABLE)

`cloudflared tunnel --url` often fails with ingress hostname conflict. Prefer:
1. Direct port access (this skill)
2. Named tunnel (`cloudflared run --token` + console config)
3. Quick tunnel after `rm -rf /etc/cloudflared /home/ubuntu/.cloudflared`

### Pitfall: quick tunnel DNS can go NXDOMAIN

After `cloudflared tunnel --url` registers a tunnel, `dig <url>` may still return NXDOMAIN for minutes, or indefinitely if Cloudflare rate-limited the account. Before troubleshooting the app, verify: `dig @1.1.1.1 <url> +short` — if empty, the tunnel URL itself is dead, not the app.

### Pitfall: stale cloudflared processes from prior sessions

Old quick tunnels (e.g. `--url http://127.0.0.1:3080`) started days ago can hold the tunnel DNS alive while a new one for a different port registers. Kill all cloudflared processes before starting a new one: `kill $(pgrep -f cloudflared) 2>/dev/null; sleep 2; cloudflared tunnel --url http://127.0.0.1:<port>`

### Pitfall: Next.js dev server HMR breaks over public IP

Next.js `next dev` relies on a WebSocket HMR connection (`/_next/webpack-hmr`). Over a public IP this WebSocket often stalls, leaving the page with `opacity:0` on all elements — HTML renders but UI stays blank. **Fix: build and run production mode:**
```bash
kill $(pgrep -f "next dev\|next-server\|pnpm dev") 2>/dev/null
pnpm build && PORT=3000 HOST=0.0.0.0 pnpm start
```
Production mode renders full HTML without WebSocket dependency.

## Pitfall: Cloudflare tunnel token 不完整导致认证失败

从 CF 控制台复制的 token 可能被截断（显示为 `cfut_ZSxy...`）。完整 token 应 184+ 字符（JWT 格式）。短 token 会导致 `Provided Tunnel token is not valid` 错误。

**验证**：`echo $TOKEN | wc -c` — 若 < 100，token 不完整，需重新从 CF 控制台 Copy token。

## Pitfall: systemd-resolved 不传播 Cloudflare NS

OCI VCN DNS (`169.254.169.254`) 可能未同步新域名的 NS 记录，导致本机 `dig example.com` 返回 NXDOMAIN，但外部 `dig @1.1.1.1 example.com` 正常。

**症状**：浏览器通过 CF 隧道访问正常，但本机服务间调用失败；`curl -sk https://domain` 返回 000。

**修复**：让 systemd-resolved 走 Cloudflare DNS 作为 fallback：
```bash
sudo mkdir -p /etc/systemd/resolved.conf.d
sudo tee /etc/systemd/resolved.conf.d/cf.conf << EOF
[Resolve]
DNS=1.1.1.1 1.0.0.1
FallbackDNS=169.254.169.254
DNSSEC=no
EOF
sudo systemctl restart systemd-resolved
```

## Pitfall: 双 cloudflared 冲突导致流量黑洞

旧 quick tunnel (`cloudflared tunnel --url`) 和新的 named tunnel (`cloudflared run --token`) 同时运行时，CF 边缘可能把流量路由到旧隧道（指向已失效的本地端口），导致域名返回 000。

**规则**：启动新隧道前，必须杀掉所有旧进程：
```bash
pkill -9 -f cloudflared 2>/dev/null; sleep 2
sudo systemctl disable cloudflared-dsh.service 2>/dev/null
sudo systemctl stop cloudflared-dsh.service 2>/dev/null
```

## Pitfall: Next.js dev 模式不适用于公共服务

`next dev` 依赖 WebSocket HMR，在公网 IP 或隧道后常导致页面 `opacity:0` 空白。

**规则**：公共服务必须用 production 模式：
```bash
# 构建
cd /app && npx next build
# 启动（systemd 管理）
ExecStart=/usr/bin/node /app/node_modules/next/dist/bin/next start -p 3000
```

## Pitfall: OpenMAIC TTS 配置需完整的环境变量

OpenMAIC 的 TTS 能力 (`/api/health` 中 `tts: true`) 需要以下环境变量全部设置：
```
TTS_OPENAI_API_KEY=<key>
TTS_OPENAI_BASE_URL=https://openrouter.ai/api/v1
TTS_OPENAI_MODELS=fish-audio/s2.1-pro-free:free
TTS_BROWSER_NATIVE_ENABLED=true
ASR_BROWSER_NATIVE_ENABLED=true
```

缺少任一变量会导致 `tts: false` 或喇叭灰色。

## Pitfall: Fish Audio TTS 需 response_format: 'mp3'

OpenMAIC 的 tts-providers.ts 中 OpenAI TTS 请求必须包含 `response_format: 'mp3'`，否则 fish-audio 返回原始 PCM 而非 MP3。

**修复位置**：`/data/OpenMAIC/lib/audio/tts-providers.ts` line 316

## Pitfall: OpenMAIC 进程无人看管导致频繁断线

直接 `nohup npx next start &` 启动后，进程崩溃不会自动重启；旧进程残留端口导致新进程 `EADDRINUSE`。

**规则**：必须用 systemd 服务管理：
```bash
sudo tee /etc/systemd/system/openmaic.service << 'EOF'
[Unit]
Description=OpenMAIC Web App
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/data/OpenMAIC
Environment=NODE_ENV=production
Environment=PORT=3000
Environment=HOST=127.0.0.1
Environment=OPENAI_API_KEY=<key>
Environment=OPENAI_BASE_URL=https://api.mistral.ai/v1
Environment=OPENAI_MODELS=ministral-8b-2512
ExecStart=/usr/bin/node /data/OpenMAIC/node_modules/next/dist/bin/next start -p 3000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload && sudo systemctl enable --now openmaic
```
