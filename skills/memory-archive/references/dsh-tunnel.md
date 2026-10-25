用户不想用 scp/CLI 传文件(嫌麻烦), 倾向网页上传: dsh 对话框附件 或 我搭 filebrowser 拖拽到 ~/cloud-docs/。大文件走聊天机器人慢。dsh 'API key is invalid' 根因=token过期(同步cron关了); 已建静默同步 cron dsh-token-sync-silent(job 5ed16e725c96, 每30分).

---

售前一条龙: 架构图(solution-delivery)→方案(presales-architect)→PPT(powerpoint)→发Telegram. 注: solution-delivery & spreadsheet-delivery 是用户自有skill, 改前需 `hermes curator adopt <名>`.

---

中文PDF生成坑(2026-08-24验证): libreoffice无头损坏; reportlab拒CFF/PostScript CJK字体. 唯一可用=glyf轮廓TTF(/tmp/nssc.ttf=NotoSansSC-VF.ttf)+reportlab registerFont(TTFont). 简历docx用python-docx(微软雅黑). 视觉偏好: 朴素商务风, 黑/深灰, 禁蓝色等'AI感'配色.

---

现状(2026-08-29最新实测更新): 隧道已恢复——/etc/cloudflared/token 是**有效新 token**(184字符JSON: a=6413823f...(CF账号)/t=203eba87-df2c-4fb6-8ca4-8698f0e3deeb(TUNNEL_ID)/s=secret), systemd cloudflared.service 用 --token-file 该 token 启动且 active; 家目录 config.yml 的  才是失效旧 token(别再用). 隧道活着但 ingress 无 hostname 规则=仍'0路由'死结(外部访问不通). 加 Public Hostname 路由最稳=CF网页控制台隧道页点'添加路由'(不需cert); 本机无 cert.pem 故 cloudflared tunnel list/route dns 不可用(报错No cert正常). CNAME 目标恒为 <TUNNEL_ID>.cfargotunnel.com = 203eba87-df2c-4fb6-8ca4-8698f0e3deeb.cfargotunnel.com. quick tunnel 已弃用(曾因RestartSec=5被CF限流429/1015).

---

dsh 插件(知乎'必装10个')可用性(2026-08-29探测): 多数第三方仓库已404——omdsh-dev的agent-teams/plan-execute/context-doctor/reverse-skill/ModLens 全404, deepseek-ai的dsh-tui/desktop 也404. 尚存: dsh-better-sidebar(github omdsh-dev/DSH-better-sidebar, 200), dsh-web-ui(zhu1090093659/dsh-web-ui, 301), dsh-at-file(omdsh-dev/dsh-at-file, 301). 安装用 `dsh plugin --profile web add <repo>` (需在本机dsh profile目录跑). 用户要求全装但先搞定外部访问再装.

---

dsh 真实项目根=/home/ubuntu/hermes/deploy/dsh-src (注意: 不是 /home/ubuntu/.hermes/deploy/dsh-src, 多一个点会导致 systemd CHDIR 失败). 启动用 `node --import tsx/esm apps/cli/src/bin.ts --profile web` (cd 到该目录), 因为 pnpm bin 代理在 systemd bash -lc 下找不到 dsh 命令. dsh.service 当前 ExecStart 已改为此绝对路径调法.

---

dsh Web UI 外部访问硬坑: `--trusted-host` 不接受通配符 `*.trycloudflare.com` (api-request-trust.ts 要求规范 host[:port] 权威, 通配会被拒/不生效). 必须写精确域名(如 healing-organic-retro-metres.trycloudflare.com 或 vkim.duckdns.org). 外部 Host 不在白名单→HTTP 403. quick tunnel 重启换URL故不能靠通配, 必须固定域名+精确trusted-host.

---

用户域名资产: 已注册免费 DuckDNS 域名 vkim.duckdns.org (动态DNS, 仅支持填IP不支持CNAME). 接Cloudflare命名隧道(dshnew, tunnel ID 203eba87-df2c-4fb6-8ca4-8698f0e3deeb)方案: DuckDNS IPv4填CF anycast IP 162.159.137.85 + CF控制台 Zero Trust→Tunnels→dshnew→Hostname Routes 加 vkim.duckdns.org→http://localhost:3080. 目的: 替代不稳定的 quick tunnel 临时URL(healing-organic-retro-metres.trycloudflare.com)作 dsh 固定公网入口.

---

Hermes推GitHub备份坑: .hermes/.gitignore已排除.env但【漏了.env.aliyun】(含阿里云AK), push前必须补一行.env.aliyun进.gitignore。本机无gh CLI/无SSH key/无git credential helper, push只能走HTTPS+PAT(必须classic PAT ghp_ 而非fine-grained)。仓库bfliujinlong/hermes-backup。推送范围: skills/, memories/(MEMORY.md/USER.md), config.yaml, cron/jobs.json; 排除hermes-install/(1.6G)/deploy/dsh-src/(1.5G)/cache/logs/*.db/.env/.env.aliyun。

---

DuckDNS+Cloudflare隧道死路(2026-08-29实测验证): DuckDNS只支持改子域A记录IP, 不支持CNAME/改NS, 因此无法把域名zone加入Cloudflare。CF命名隧道Public Hostname要求域名zone在CF(Full改NS或Partial加TXT校验), 否则边缘TLS返回unrecognized_name(alert 624)直接断, curl报HTTP 000, 请求从未到本机。证据: curl -k vkim.duckdns.org→000, 而*.trycloudflare.com→200, 隧道日志vkim出现0次。结论: DuckDNS域名走不通CF隧道, 必须eu.org(能改NS)或付费域名接CF。用户曾创建vkim.duckdns.org并填162.159.137.85(anycast IP)仍失败。

---

Cloudflare 隧道配置: tunnel 203eba87-df2c-4fb6-8ca4-8698f0e3deeb, hostname dsh.203eba87-df2c-4fb6-8ca4-8698f0e3deeb.cfargotunnel.com -> http://127.0.0.1:3080, token 位于 /etc/cloudflared/token

---

【Cloudflare隧道现状】tunnel 203eba87-df2c-4fb6-8ca4-8698f0e3deeb，hostname dsh.203eba87-df2c-4fb6-8ca4-8698f0e3deeb.cfargotunnel.com → http://127.0.0.1:3080，token位于/etc/cloudflared/token。隧道本身active，但访问失败因dsh端口未监听（已修复）。

---

Cloudflare Workers AI 已验证可用：Account ID=6413823f...，API Token=[CF_TOKEN_REDACTED]（存储在 ~/.hermes/skills/cloudflare/cf.env，chmod 600）。注意 Global Key（cfk_ 开头）不能用于 Workers AI，必须用 API Token。可用模型 9 个（Llama 3.1/3.3/4, Mistral, DeepSeek, GPT-OSS, Gemma, GLM）。

---

dsh 公网访问修复（2026-09-07）：quick tunnel URL 从 journalctl 提取；nginx 必须 `proxy_set_header Origin ""` 否则 API 返回 403；`--trusted-host` 只接受 `host[:port]` 格式；cron job dsh-token-sync-silent (5ed16e725c96) 已禁用（会污染 credentials.yaml）。

---

DSH nginx 安全加固已配置：限流 10r/s 每 IP、并发连接限制 10、安全响应头、访问日志 /var/log/nginx/dsh-access.log。nginx 监听 3082 反向代理到 dsh 127.0.0.1:3081。

---

浏览器 JS crypto.randomUUID() 仅在安全上下文（HTTPS 或 localhost）可用。DSH 前端使用 crypto.randomUUID()，通过 HTTP（如 http://IP:port）访问会报 'uuid is not a function'。解决方案：HTTPS（Cloudflare Full strict）或 SSH 端口转发到 localhost。

---

【PPT 制作经验】AWS 案例 PPT 用 pptxgenjs 生成，配色 Midnight Executive (NAVY=1E2761, ICE_BLUE=CADCFC, ACCENT=0D9488)，8 页标准结构：Title→Background→Solution→Capabilities→Technical→Results→Takeaways→Thank You。生成命令：cd ~ && npm init -y && npm install pptxgenjs && node create_ppt.js

---

用户购买域名 aihubcloud.cn（新网注册），但新网不支持改 NS 记录，Cloudflare 隧道自定义域名无法配置。只能继续用 trycloudflare.com 隧道域名。

---

域名 aihubcloud.cn（新网注册），NS 已改到 Cloudflare（anna/jaime.ns.cloudflare.com）。需在 CF 控制台配 tunnel hostname routes → aihubcloud.cn→:3000, dsh.aihubcloud.cn→:3081。Token 之前给过但本会话丢失，需用户重发。

---

域名 aihubcloud.cn 已托管 Cloudflare。配置：openmaic.aihubcloud.cn → :3000 (OpenMAIC)，dsh.aihubcloud.cn → :3081 (DSH)，aihubcloud.cn → 301 → openmaic。SSL Full + Always HTTPS + Security Medium。CF 隧道 203eba87 跑着。

---

Cloudflare 配置关键参数(2026-09): CF账号=<EMAIL>, Zone ID=100380e22b85e5f8e66730342913976d, Tunnel ID=203eba87-df2c-4fb6-8ca4-8698f0e3deeb, 域名=aihubcloud.cn。ingress通过API管理(--token模式)，非本地config.yml。

---

Cloudflare + Next.js 不兼容坑(2026-09实测): ①CF的Rocket Loader/Auto Minify/Mirage/Polish/Brotli必须全部关；②CF会缓存HTML(s-maxage=31536000)导致chunk引用过期→空白页；③Next.js dev模式的HMR WebSocket被CF阻断→必须用`next build`+`next start`生产模式。

---

CF隧道token管理(2026-09): 用户给过cfut_前缀的tunnel token(184字符JWT)和cfk_前缀的Global API Key。token在本会话中多次丢失(会话压缩)，每次都要用户重发。CF API调用用X-Auth-Key(Global Key)比Bearer <REDACTED>更稳(401少)。

---

Cloudflare 账号邮箱=<EMAIL>（Global Key 认证用）。新阿里云 VM=8.133.232.216（用户要求 aicc.aihubcloud.cn 解析到此 IP）。

---

AICCP 项目新动态：用户在阿里云 ECS 8.133.232.216（Ubuntu 24.04 aarch64）上部署了 AICC 前端/后端/PG/Redis/MinIO（Docker），域名 aihubcloud.cn 托管在 Cloudflare（NS: anna/jaime.ns.cloudflare.com），当前在配 nginx 反向代理 + Cloudflare DNS 指向该 ECS。

---

User has registered a Twilio number (+1 202 816 6399) and is exploring ways to integrate its SMS reception into Telegram and Cloudflare workflows. They want messages from this number automatically forwarded and handled via these systems.

---

Twilio SMS转发项目(2026-09-20): 用户注册了Twilio(AC08d469...)，买了美国号+1 202 816 6399(DC华盛顿区号，旧号231 758 5738已释放)。Webhook指向sms.aihubcloud.cn→本机9999端口→转发到Telegram。目的：收海外服务验证码。注意：Palantir AIP屏蔽VoIP号(Twilio/Google Voice全废)，需实体SIM号(TextVerified或eSIM)。Photon sidecar(端口8789)已修改新增/history API但SDK本身不支持历史消息查询。

---

Cloudflare API Token(cfut_前缀, 非Global Key): [CF_TOKEN_REDACTED]. 账号ID=6413823f243b9dc615778a19021db968, Zone ID=100380e22b85e5f8e66730342913976d. Global Key(cfk_前缀)邮箱不匹配, 勿再用于API调用. API Token权限有限(不能改tunnel配置). 隧道Public Hostname必须从CF控制台UI加.

---

Twilio 账号(2026-09-20): Account SID=[REDACTED_TWILIO_SID], 号码=+1 202 816 6399(DC华盛顿区号,旧号231 758 5738已释放), 余额$10.67。Webhook指向sms.aihubcloud.cn→本机9999→转发到Telegram。目的: 收海外服务验证码。注意: Palantir AIP屏蔽VoIP号(Twilio/Google Voice全废), 需实体SIM号(TextVerified或eSIM)。

---

用户设备与环境(2026-09-20): 主力笔记本=Windows(D:\Work\, 用户EDY, 有cloudflared可跑quick tunnel)。Trae本地端口=50010(不是5001, netstat实测), WorkBuddy有API key(ck_前缀,永久有效, 但API端点地址未确认)。偏好:直接动手执行, 反复确认会烦; cloudflared quick tunnel URL会变(重启即换)不需记。