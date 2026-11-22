---
name: browser-vault-login
version: 1.0.0
author: jinlongliu
license: MIT
description: Use when 无头浏览器登录第三方站点/控制台(含MFA). 凭证走vault, TOTP排查.
metadata:
  hermes:
    tags: [browser, vault, login, mfa, totp, aws]
    related_skills: [hermes-agent, web/blocked-page-recovery]
---

# 无头浏览器 + Vault 登录第三方站点

## When to Use
- 用户要在 headless 服务器（OCI/GCP 等无 GUI）上登录第三方站点/云控制台（AWS Quick、各类 web 应用）。
- 登录被 MFA/TOTP 卡住，或用户问“能不能把密码/验证码/MFA 发你”。
- 需要用 `browser_vault` 安全注入凭证完成表单登录。

适用：headless 服务器（OCI/GCP 等无 GUI）上登录 AWS 等控制台。组件：`browser_exec`（无头浏览器）+ `browser_vault`（凭证注入）+ `hermes vault` CLI（入库）。

## 常驻红线
- 密码、TOTP setup key、API key **一律不进聊天正文、不复述**；入库只能由用户在机器上跑 `hermes vault add --kind login` 完成——Telegram 等无头会话弹不出 browser_vault 的加密输入框，别尝试。
- 唯一例外：**30 秒一次性 TOTP 码**在用户明确要求时可展示用于诊断比对（见下），且一次给 prev/current/next 三窗口。
- vault handle、邮箱等标识符不算秘密，可出现在聊天。
- 用户在聊天里贴了密钥时：提醒已暴露、不复述、建议事后重置，流程照走。

## 标准登录流程
1. **入库**（用户在机器上）：`hermes vault add --kind login`。Site/Origin 填**重定向后真正的登录域**（如 `https://us-east-1.signin.aws`），不是入口营销页域名；站点有 MFA 必须同时填 Authenticator key（base32 setup key 或 `otpauth://` URI），否则 `enter_code` 无码可生成。
2. `browser_exec` 打开登录入口 → 接受 cookie 横幅 → 填邮箱等标识符 → Continue。
3. `tool_call browser_vault action=list` 拿 handle → `action=fill` 注入密码（值不经模型）。
4. `browser_exec` 提交 → 轮询跳转。遇 MFA 页 → `action=enter_code`（自动生成并填 TOTP）→ 立即提交。
5. **验证登录态**：直接导航目标应用域名看页面内容，别只看提交响应；跳转丢失/域名不存在时先 `getent hosts` 确认真实域名。

## MFA/TOTP 被拒排查（按序，别跳步）
1. **时钟**：`date -u` 对比目标站响应 `Date:` 头（`curl -sI`）。TOTP ±30s 即失效；NTP 同步下两边应一致。
2. **码新鲜度**：跨工具调用有秒级延迟，改为**同一 browser_exec 进程内**用 stdlib（hmac/hashlib/struct，RFC6238 SHA1/30s/6位）生成→填入→提交，见 `scripts/totp.py` 的算法。
3. 钟准 + 新鲜码仍被拒 → **结论是密钥错，不是时序**。诊断：应用户要求给出 prev/current/next 三窗口码（覆盖约 90 秒，容忍手机钟差），让用户比对验证器 App 当前显示——三者之一匹配=密钥对（查账号侧，如绑了别的设备）；全不匹配=用户拿错了 key。
4. 修复只有两条路：用户在站点 profile 页 **Register device → Show secret key** 拿新 setup key 重入 vault；或**删光全部 MFA 设备**后重试。手机验证器（Google/Microsoft Authenticator）不显示原始密钥，丢了只能重绑。

## 状态变更必须全新会话
- 用户在自己设备改了密码/MFA 后重试登录，先 `cdp('Network.clearBrowserCookies')` 再重走**全流程**——旧会话缓存了「密码已验证、下一步 MFA」的 workflow 状态，直接导航会跳回 MFA 页，误判修改未生效。
- 登录流程走向异常（被当成新用户/进了注册流）→ 先核对 vault 里标识符拼写，邮箱拼错一个字母站点就按新账号处理。

## 浏览器守卫与恢复链接
- 导航到 **DNS 解析不了的域名**会被守卫当内网地址拦截；猜子域名前先 `getent hosts` / `curl -sI` 验证。
- 部分登录恢复链接（如 AWS "Troubleshoot MFA"）在无头浏览器里跳 about:blank 跟不动；恢复流程让用户在自己浏览器完成，邮箱验证码不进聊天。

## references/
- `references/aws-builder-id.md` — AWS Quick / Builder ID 登录链路与 MFA 管理细节（与 IAM MFA 的区别、彻底关闭条件）。
- `scripts/totp.py` — 标准库 TOTP 三窗口生成器（诊断比对用，密钥走环境变量）。
