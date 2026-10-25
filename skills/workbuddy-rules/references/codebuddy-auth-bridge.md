---
description: CodeBuddy (Tencent Copilot) 认证提取 + 本地代理桥接 + 隧道路由验证。用于将 Windows CodeBuddy auth 迁移到 OCI 隧道，并通过真实 token 调用 Tencent Copilot 而非付费 API。
---

# 触发
- 用户要求「使用 codebuddy / 切 codebuddy / 用腾讯 Copilot」
- 需要从 Windows `CodeBuddyExtension/Data/Public/auth/` 提取真实 bearer token
- 需在 OCI ARM64 上做本地代理（localhost:63127/63128）并通过 CF Tunnel 暴露

# 步骤（顺序，不跳）
1. **收文件**：用户从 Windows 传 `cb-auth-full.zip`（或 `.info` 集合）。大文件走 Telegram/飞书（>20MB 走飞书），小文件直接 DM。
2. **解压 + 查找真实 token**：
   - `unzip -o cb-auth-full.zip -d /tmp/cb_full/`
   - 最完整的 auth 通常在 `workbuddy-desktop.info` / `workbuddy-desktop.*.info`（非早期 `entry_5a8...` 压缩件）
   - 提取：搜索 `"tokenType":"Bearer"` 上下文，取前面的长 base64 值（通常 ~300 字符，含 `==` 结尾）；保存 `/tmp/codebuddy_real_token.txt`，`chmod 600`
3. **批确认内容**：
   - 端点 = `copilot.tencent.com`（来自 `auth.endpoint` 或 `internalDomain`）
   - 需要的头 = `Authorization: Bearer <token>` + `X-Product-Name: CodeBuddy` + `X-Platform: CLI`
   - **不要假设路径**：先 `curl -I` 测 `/chat`（值 200 HTML）、`/`（404 JSON）、`/v1/chat`（404）确认唯一可用路径；腾讯 Copilot 真实 API 路径未公开，桥接常只到登录页，直接回复需用 Windows 插件
4. **写桥接**：`/home/ubuntu/.local/bin/codebuddy-bridge-fixed.py`（或 `-proxy.py`），读 token+端点，监听 `127.0.0.1:63127`（或 `63128` 对应 CodeBuddy UI 端口）
5. **隧道更新**：CF Zero Trust → Tunnels → dshnew → `codebuddy.aihubcloud.cn` → URL 改 `http://localhost:63128`（或 `63127` 对应桥接）→ Save
6. **验证**：`curl -k https://codebuddy.aihubcloud.cn/` → 200（HTML）；`/chat` → 403 `Missing required header: x-codebuddy-request`（说明端点正确，缺腾讯专有头，预期行为）
7. **记录用量**：桥接写入 `/tmp/codebuddy-bridge-usage.log`；token 不写入 `.env`/chat

# 坑 / 规则
- **不要把完整 token 写进聊天回复**：只给路径 `/tmp/codebuddy_real_token.txt` + `chmod 600`
- **不要凭记忆说 Tencent Copilot API 路径**：公共路径均 404，真实回复路径在 CodeBuddy 客户端内部，由插件封装；桥接的价值是「通隧道 + 备 token」，完整对话回复建议直接在 Windows 端用 CodeBuddy 插件
- ** tunnel 更新必须 CF Dashboard UI**（API Token `cfut_` 无修改权限，之前 405 已验证）
- **CodeBuddy UI 端口**：本地 `63128`（node，Hy4 preview），桥接 `63127`（proxy）；不要混淆
- 若用户只想「试回复」而非完整 Copilot 接入：直接切 `hermes config` 到 `CF Workers AI` (`llama-3.1-8b`) 或本地 `ollama qwen3:4b`，这才是可验证的回复路径
