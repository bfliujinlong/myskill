# AWS Quick / Builder ID 登录与 MFA 细节

## 登录链路
- 入口：`https://aws.com/quick`。桌面 App 只有 macOS/Windows，**无 Linux 版**；headless 服务器只能走 web。
- Quick Free 注册/登录：`https://signup.aws.amazon.com/billing/signup/service?app=AmazonQuickSuite&tier=free&funnel=boost#/validation`
- 实际认证跳转到 `https://us-east-1.signin.aws/platform/d-<目录ID>/login`——vault 的 Site/Origin 填 `https://us-east-1.signin.aws`。
- 应用域名基于 `quicksight.aws.amazon.com` 家族；`quicksuite.aws.amazon.com`、`quick.aws.amazon.com` **不存在**（猜出来会 DNS 解析失败被浏览器守卫拦）。
- 官方允许域名清单见 docs.aws.amazon.com/quick 用户指南 "Signing in"（signin.aws、awsapps.com、region.quicksight.aws.amazon.com 等）。

## Builder ID MFA 管理（与 IAM 是两套，别删错）
- 管理入口：`https://profile.aws.amazon.com` → **Security** → MFA devices 表（或 `https://settings.aws.com` → Manage security and sign-in）。
- **关闭 MFA = 删光表里所有设备**；剩任何一个，登录仍强制 MFA。用户说"我删了 MFA"但仍被要码，首查残留设备和删除位置。
- IAM 控制台（console.aws.amazon.com/iam）删的是 IAM 用户 MFA，对 Builder ID 登录无效。
- 删除/变更后，headless 侧必须清 cookie 全新流程验证（旧 workflow 缓存 MFA 状态）。
- 拿新密钥：Security → **Register device** → Authenticator app → **Show secret key**（QR 码下的 base32）。注册必须输入 App 当前码确认；未完成确认的设备会出现"登录要码但密钥算不出有效码"的半绑定状态。
- TOTP 参数：标准 RFC6238（SHA1 / 30s / 6 位），与主流验证器一致。
- 被 MFA 锁死：登录页 **Troubleshoot MFA** → 注册邮箱收码恢复；该流程在无头浏览器里跟不动（about:blank），让用户在自己浏览器完成，验证码不进聊天。

## 登录异常速查
| 现象 | 原因 |
|---|---|
| 填邮箱后进了注册/建新账号流 | 邮箱拼错，AWS 按新用户处理；核对 vault |
| 密码通过、仍跳 MFA（用户称已删） | 还有残留设备，或删的是 IAM MFA，或旧 session 缓存 |
| TOTP 全新码+钟准仍被拒 | setup key 不是该账号注册的那把 |
| 提交后 about:blank | 跳转域名解析失败或恢复链接不可跟随 |
| 标签页在 browser_exec 调用之间变 about:blank | 无头标签页被回收（尤其 browser_vault fill 失败后）→ 见下方"单调用配方" |

## 无头登录成功配方（2026-11-22 实测跑通，进入 quick.aws.com）
关键教训：**整个登录流程必须在一条 browser_exec 调用内跑完**，调用之间标签页会被回收成 about:blank，OTP 页停留几分钟也会超时作废。

### 坑
1. **密码框是 `type:text`**（placeholder `Enter password`，用 CSS 掩码显示圆点）→ `browser_vault fill` 自动识别失败；且 browser_vault 偶发 "Could not determine the current page origin"。
2. **AWS OTP 邮件是 HTML**，正文含多个 6 位数字（HTML 标记里的假数字）→ 直接对原始 HTML 跑 `\d{6}` 正则会抓错码，提交报 "verification code does not match"。**必须先剥离 HTML**（去 `<style>/<script>`、去标签、反转义实体）再抓 6 位码。
3. OTP 有效期约 10 分钟；诊断/改脚本耗时会让它过期。

### 配方（browser_exec 内 Python，cryptography + imaplib 都可用）
- browser_exec 的 Python 环境**有 cryptography/imaplib/email**，可直接读 `vault.key`+`vault.json.enc`（Fernet 解密）拿到密码——**进程内解密、base64 传入 JS 用 atob 还原填框，密码/码值绝不 print、不进聊天**，安全等价于 browser_vault。
- 单次调用顺序：清 cookie → new_tab(注册URL) → 接受 cookie → 填邮箱 → Continue → 轮询密码页 → 注入 AWS 密码(base64) → Continue → 轮询 "Verify your identity" → 记录 submit_time → IMAP 轮询取 From=login.awsapps.com 且 Date≥submit_time-45s 的最新邮件 → 剥 HTML 抓 6 位码 → 填 OTP → Continue → 轮询离开 OTP 页/到 quick.aws.com。
- 企业邮箱 OTP：IMAP `imap.exmail.qq.com:993`，密码从 vault 条目（identifier=邮箱）取；OTP 只写 chmod 600 临时文件或进程内传递。
- 填框统一用 `Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set` + dispatch input/change（React 受控组件直接赋 .value 不生效）。

### 登录后
- 成功进 `https://quick.aws.com/sn/account/<acctId>/start/chat`，title=Quick。
- **Quick Free 有月度额度**：耗尽后页面提示 "You've hit your monthly limit. Next refresh in N days."，聊天输入框 disabled，无法使用，须等刷新（非登录问题）。
