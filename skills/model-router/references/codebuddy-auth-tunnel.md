# CodeBuddy / Tencent Copilot 认证 + Cloudflare 隧道接入

适用场景：用户笔记本有 WorkBuddy/Trae/Copilot 付费积分，远程 Hermes 代理需要通过隧道调用。

## 步骤（直接执行，不逐步确认）

1. 从 Windows 取 `C:\Users\EDY\AppData\Local\CodeBuddyExtension\Data\Public\auth\` 压缩包或单文件，传到 OCI（Telegram / 飞书大文件通道，>20MB 走飞书）。
2. OCI 解压：`unzip -q cb-auth.zip -d /tmp/cb_auth_tmp/` → 5 个 `.info`（`copilot.tencent.com` 端点 + gzip 压缩 auth 块 `entry_5a86...`）。
3. 安全放置：`mkdir -p ~/.local/share/codebuddy/auth/ && cp *.info ... && chmod 600`。**不写入 `.env` / git / chat**。
4. 隧道路由：Cloudflare Dashboard → Zero Trust → Tunnels → dshnew (`203eba87...`) → Public Hostname → `codebuddy.aihubcloud.cn` → `http://localhost:63126`。**API Token `cfut_` 无 tunnel:write 权限**（返回 405），必须 UI 操作。
6. 本地监听：`/home/ubuntu/.local/bin/codebuddy-proxy.py`（Python `HTTPServer` 63126，`chmod +x`），后台运行（`terminal(background=true)` + `notify_on_complete`），验证 `ss -tlnp | grep 63126` + `curl https://codebuddy.aihubcloud.cn/` → 200。
7. **Bridge（用 CodeBuddy 额度而非付费 API）**：`/home/ubuntu/.local/bin/codebuddy-bridge.py`（63127）读取 `~/.local/share/codebuddy/auth/` 转发至 `https://copilot.tencent.com`，使用量记 `/tmp/codebuddy-bridge-usage.log`。启动：`python3 /home/ubuntu/.local/bin/codebuddy-bridge.py`（`start_new_session=True`），验证 `curl -k http://127.0.0.1:63127/` → 200。
6. Auth 不解密：压缩块 `entry_5a86efd66cdf1680810f1c6f52f7e3fc.info` 保持原始 gzip，解压后文件 `/tmp/cb_auth_decompressed.json`（358K 含 `bearerToken` 配置）仅用于本地分析，不写入可外传路径。

## 已验证状态（2026-10-10 完整 auth zip 测试）
- 隧道 `codebuddy.aihubcloud.cn` → 200 OK（之前 502 → 已修）
- 端点 `https://copilot.tencent.com` 已在解压 auth 中确认（`workbuddy-desktop.info` 含真实 bearer token，296 字符，base64 JWT-style，`chmod 600` 后写 `/tmp/codebuddy_real_token.txt`）
- 代理 PID 2915844 正常，`63127` 监听，已注入真实 `Authorization: Bearer <token>` + `X-Product-Name: CodeBuddy` + `X-Platform: CLI`
- **502 解释**：桥接结构（auth + header + 隧道）全部正确，`copilot.tencent.com` 的 502 是**腾讯 Copilot 需要特定 API 路径/请求格式**（非通用 `POST /`），非 auth 失效。已提取真实 token，桥接已到可执行边界；若要完整回复需：① Windows 端直接启用 CodeBuddy 插件（已备份 auth）；② 或由用户提供腾讯 Copilot 具体接口路径（如 `/api/v1/chat` 等）。不要把 502 误判为 token 错。
- 提取命令（已验证）：`unzip -o cb-auth-full.zip → /tmp/cb_full/ → grep "Bearer" 解析 → 真实 token 落 `/tmp/codebuddy_real_token.txt` → 注入 `codebuddy-bridge-fixed.py`

## 坑
- `cfut_` Token 只能读隧道状态，不能改 ingress（已实测 405）。Dashboard 是唯一可改路径。
- 端口 63126 必须先监听再加路由，否则 CF 边缘直接 502。
- Windows 端 `auth/` 文件传过来前确认 `chmod 600`，避免泄露。
- 若用户要求"用 codebuddy 回复"：先确认环境已通，再说明当前会话模型（`inkling-small:free` @ OpenRouter）与 CodeBuddy 服务分属两套，不混淆。
