---
name: free-public-endpoint
description: "获取免费公网域名并打通 cloudflared 隧道路由。触发：免费域名 / DuckDNS KO / dsh公网。"
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [免费域名, cloudflared, 隧道, DuckDNS, FreeDNS, 公网暴露, OCI, dsh, 零费用]
    related_skills: [oci-free-tier, dsh-nous-deploy, ai-cloud-hub]
---

# 免费公网端点（Free Public Endpoint）

## When to Use
- 用户要给自托管服务(OCI 免费机上的 dsh/nginx、本地 lab、树莓派等)一个**免费公网域名**
- 现有 cloudflared 隧道在跑但"0 路由 / 无公网 URL"(OCI AI Hub 控制台没加路由的死结)
- 用户想注册免费域名但**绝不绑信用卡**、不想折腾手机 SMS
- DuckDNS 返回 KO、不知道为什么

## 核心结论（2026-08 实测）
1. **最省事通路 = FreeDNS (afraid.org) 子域 + CNAME 指向 cloudflared 隧道**
   - 免费、邮件验证、**无需手机、无需 reCAPTCHA**
   - 可在它的 DNS 面板建 **CNAME** 记录 → 直接指向 `<TUNNEL_ID>.cfargotunnel.com`
   - 不要求把域名 NS 转到 Cloudflare，跨服务商可用
2. **DuckDNS + Cloudflare 命名隧道 = 结构性走不通（2026-08-29 OpenAI 委托诊断, 证据确凿, 已结案）**
   - 实测：`dig vkim.duckdns.org` → `162.159.137.85`（CF anycast IP，DNS 解析正确）；CF Hostname Routes 加 `vkim.duckdns.org → http://localhost:3080` 成功（绿条"Successfully created route"）
   - **但 `curl -k https://vkim.duckdns.org` 仍 HTTP 000**（边缘直接断，连 cloudflared 都收不到请求）；命名隧道日志里 `vkim.duckdns` 出现 **0 次**
   - **根因（架构性）**：Cloudflare Tunnel 的 Public Hostname 要求该域名 **zone 必须加入你的 CF 账号**（Full 接入改 NS，或 Partial 接入加 TXT 校验）。DuckDNS 只让你改 `*.duckdns.org` 子域的 **A 记录**，**无法把 `duckdns.org` 的 NS delegation 给 Cloudflare，也无法在 DuckDNS 加 CF 要求的 TXT/CNAME 验证** → CF 边缘对这个 Host 没有证书、没有路由 → TLS 握手返回 `unrecognized_name` (alert 624) 断开 → curl 报 000
   - **Cloudflare 官方 FAQ 确认**：隧道公共主机名需 zone 在 CF，Partial 接入值须为 `*.cdn.cloudflare.net`（DuckDNS 不支持）
   - **结论：DuckDNS 方案必须放弃**。填 `162.159.137.85` 对错已无意义（整个"duckdns 指向 CF"思路结构性不通）。别再在 duckdns 上花时间
   - **域名拼写坑（独立）**：CF Hostname Routes 加域名易多打字母（如 `vkim.ducksdns.org` 多 s），DuckDNS 无此拼写 → 路由配错。加完用 `dig +short <你填的域名>` 核对是否在 DuckDNS 正确子域上
4. **pp.ua / nic.ua 免费但需乌克兰本地税号（РНОКПП）** → 海外用户无法注册，排除
4. **GoDaddy 等付费注册商禁止**（绑卡自动续费，触碰零费用红线）

## 免费域名方案对比表
| 方案 | 推荐度 | 需手机 | reCAPTCHA | 可做 CNAME→隧道 | 备注 |
|---|---|---|---|---|---|
| FreeDNS (afraid.org) | 5/5 | 否 | 否 | ✅ | 最适配 cloudflared，CF 自动签发证书 |
| **is-a.bot** (GitHub PR) | 4/5 | 否 | 否 | ✅ CNAME | 免费子域名，需 GitHub 账号 + PR 审核（几小时-几天）；域名格式 `xxx.is-a.bot` |
| **DuckDNS** | **0/5 死路** | 否 | 可能 | ❌ 只能 A 记录 | **结构性走不通**：CF 命名隧道要求域名 zone 在 CF，DuckDNS 无法配合 → 非托管域名 TLS 000。已结案，放弃 |
| **pp.ua / nic.ua** | **0/5** | ❌ 需乌克兰税号 | - | ✅ | 仅限乌克兰公民/个体企业家，海外用户无法注册 |
| Freenom (.tk/.ml) | 3/5 | 否 | 可能 | ⚠️ 需 NS 转 Cloudflare | 可靠性时好时坏 |

## 执行步骤（FreeDNS 路线，最少真人动作）
1. 用户去 https://freedns.afraid.org/ 注册（邮件验证）
2. Subdomains → Add → 选一个共享域 → 建子域（如 `dsh-你的名.magicdns.org`）
3. 编辑该记录：类型 **CNAME**，值填 `<TUNNEL_ID>.cfargotunnel.com`（TUNNEL_ID 从 `cloudflared tunnel list` 或 token 解码得到；托管隧道 token 形如 `cfut_...`，本地 `cloudflared tunnel create` 会返回 UUID）
4. 本机改隧道 config（路径 `~/.cloudflared/config.yml` 或 `/etc/cloudflared/config.yml`）：
   ```
   tunnel: <TUNNEL_ID>
   ingress:
     - hostname: dsh-你的名.magicdns.org
       service: http://127.0.0.1:3080
     - service: http_status:404
   ```
5. 重启 cloudflared：`sudo systemctl restart cloudflared`（systemd）或 `cloudflared tunnel run <name>`（临时）
6. 验证：`dig +short dsh-你的名.magicdns.org CNAME` 应指向 `<TUNNEL_ID>.cfargotunnel.com`；`curl -v https://子域` 应落到 127.0.0.1:3080

## Cloudflare 隧道多实例冲突（高频坑）
- **症状**：cloudflared 隧道注册了但连不上，或 URL 530/502；`cloudflared tunnel list` 报错缺 cert.pem
- **根因**：残留旧 cloudflared 进程占用 tunnel，新进程抢不到连接
- **修复**：`pkill -9 -f cloudflared` 杀掉所有残留 → 等 3 秒 → 重新启动单个实例
- **验证**：`ps aux | grep cloudflared | grep -v grep | wc -l` 应为 1；`grep "Registered tunnel" <logfile>` 确认新连接注册成功

## Cloudflare Tunnel Token 长度陷阱（2026-09 新增）
- **症状**：`cloudflared tunnel run --token cfut_...` 报 "Provided Tunnel token is not valid"
- **根因**：用户给的 token 只有 ~53 字符（`cfut_` 前缀 + 短串），但 cloudflared 要求 184+ 字符的完整 JWT
- **区分**：
  - **Tunnel Token**（隧道运行时用）：184+ 字符 JWT，形如 `cfut_eyJhIjoi...很长...`
  - **API Token**（API 调用鉴权）：可能较短，或 `cfk_` 开头（Global Key）
- **修复**：去 CF 控制台 **Zero Trust → Tunnels → 你的隧道 → Copy token**（完整复制，不要截断），确认长度 >100 字符
- **token 存放**：直接传给 `--token` 参数，或写入 `/etc/cloudflared/token`（JSON 格式含 AccountTag/TunnelID/TunnelSecret）

## systemd-resolved DNS 传播坑（OCI 环境，2026-09 新增）
- **症状**：域名 NS 已改到 Cloudflare，`dig @1.1.1.1` 解析正确，但 `dig @localhost` 返回 NXDOMAIN
- **根因**：OCI 机器 systemd-resolved 上游只有 `169.254.169.254`（VCN DNS），VCN DNS 缓存旧 NS 记录不更新；resolved 没有 fallback 到其他 DNS
- **修复**：创建 `/etc/systemd/resolved.conf.d/99-fix-dns.conf`：
  ```
  [Resolve]
  DNS=1.1.1.1 1.0.0.1
  FallbackDNS=169.254.169.254
  DNSSEC=no
  DNSOverTLS=no
  ```
  然后 `sudo systemctl restart systemd-resolved`
- **运行时热修**（立即生效，不重启）：`resolvectl dns enp0s6 1.1.1.1 1.0.0.1` + `resolvectl domain enp0s6 '~oraclevcn.com' '~oraclecloud.com'`
- **验证**：`dig +short 域名 @localhost` 应返回 CF IP（如 172.67.x / 104.21.x）

## nginx 与 cloudflared 冲突（高频坑，2026-09 新增）
- **症状**：隧道通了但域名显示错误服务，或无法创建文件夹/API 报错（实际流量被 nginx 劫持到别的服务）
- **根因**：旧 nginx 占用 :3080 并 proxy_pass 到 :3081（DSH），而 cloudflared 默认把第一个 ingress 指向 :3080 → 所有域名都落到 DSH
- **发现**：`ss -tlnp | grep :3080` 看 :3080 是谁在听；`cat /etc/nginx/sites-enabled/*` 看 proxy_pass 目标
- **修复**：`sudo pkill -9 nginx` 或 `sudo systemctl stop nginx` → 确认 cloudflared 直接指向正确端口（:3000 OpenMAIC / :3081 DSH）
- **原则**：cloudflared 隧道和 nginx 反向代理二选一，不要同时占同一端口
- `curl "https://www.duckdns.org/update?domains=名&token=TOKEN&ip="` 返回 `KO` = 失败
- 根因：① 域名没注册成功（GitHub 登录后没点 add domain）；② 名字被占用；③ token 复制带空格/换行
- 验证：`dig +short 名.duckdns.org` 若返回 `34.83.254.21`（DuckDNS 占位 IP）= 域名不存在
- 解法：换唯一名（如 `liujinlongdsh`）重测；确认控制台 domains 列表里有该名；token 用页面顶部那串总 token

## 跨服务商结论（重要）
- cloudflared 要么由 Cloudflare DNS 自动建 CNAME（域在你的 CF 账号内），要么你在 DNS 提供商处手动建 CNAME → `<TUNNEL_ID>.cfargotunnel.com`
- **DuckDNS 子域通常不能建这种 CNAME** → 不能直接当隧道 hostname
- FreeDNS / 任何允许自定义 CNAME 的 DNS 均可，无需转 NS 到 Cloudflare

## 本机现状参考（用户环境，2026-09）
- OCI 免费 ARM 机，公网 IP 130.61.110.133，域名 `aihubcloud.cn` 已托管 Cloudflare
- cloudflared 2026.9.1，隧道 `203eba87-df2c-4fb6-8ca4-8698f0e3deeb`，systemd `cloudflared.service` 运行
- 命名隧道 + CF API 管理路由（非本地 config.yml ingress）
- 服务: `openmaic.aihubcloud.cn` → :3000, `dsh.aihubcloud.cn` → :3081

## 系统盘空间治理（2026-09 新增，OCI Always Free）
- **原则**：系统盘 45G 控制在 35% 上下，超了再清理；数据盘 147G 作缓存/备份/大文件仓库
- **守护脚本**：`~/.hermes/scripts/auto-disk-guard.sh`，cron 每天 UTC 16:00（上海 24:00）巡检
- **阈值触发**：`THRESHOLD=35`（系统盘使用率 >35% 才清理）
- **安全红线**：绝不删 hermes-install / OpenMAIC / cloud-docs / hermes-deploy 等 11 个业务目录
- **清理目标**：/tmp(>3天) / uv-cache / pip-cache / npm-cache / journal / apt / snap / 旧备份
- **单例锁**：`/tmp/auto-disk-guard.lock` 防并发
- **日志**：`~/.hermes/logs/auto-disk-guard.log`
- **验证清理后服务**：OpenMAIC :3000 / DSH :3081 / litellm :4200 必须仍在线

## 用户硬约束
- 零费用、绝不绑信用卡；不推荐任何付费注册商（GoDaddy 等）
- 真人动作（OAuth 登录、收邮件/手机码）用户自己做，我做完后续配置
