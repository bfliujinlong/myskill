User jinlongliu (OPC+FDE, cloud migration/MSP, Shanghai UTC+8, zero-cost hard constraint). Confirmed preference after long session (2026-09-28 to session reset): (1) Direct execution preferred over step lists / clarification loops — say "直接修" and do it, don't ask; (2) When saying "使用 openai / 难任务", delegate to Azure gpt-4o (provider=azure-foundry, endpoint liujl-9958-resource, api-version=2025-04-01-preview, key AZURE_FOUNDRY_API_KEY, temperature=1, max_completion_tokens) — NEVER expose key in replies; (3) Free-model-first routing: main=OpenRouter nemotron-3.5-lightning/CF Workers AI/Mistral 8b, local Ollama qwen3:4b+phi3.5 on ARM OCI; (4) Current gateway config broken: default=aliyun/qwen-max (OpenRouter 429/401), NOT Azure; user has restarted gateway 10x without fixing config — must use `hermes config set` + independent SSH restart; (5) Feishu fix is UI-only (cli_aa093013dc38dcbb: apply identity permissions + publish version + pull bot into oc_<REDACTED:MISTRAL_KEY>) — I cannot replace; (6) API keys must never appear in chat; if exposed (e.g., sk-sp-H... DashScope, sk-or-... OR keys), immediately chmod 600 + tell user to rotate; (7) Response style: concise Chinese, no "已完成" loops, no AI-feel bullet stacks; save to /tmp/ or /home/ubuntu/ directly; deliver via Telegram 5701842056 + email liujinlong@outlook.com; (8) Vision analyze fails due to OR 429 — diagnose from file paths/context; (9) Child Liu Yifan (born 2014-06-30), family info in ~/personal/; (10) All technical assertions must be verified against docs/real tool output first — no memory-guessing.
§
User confirmed 2026-09-29 session preferences (already covered by existing memory): direct execution preferred (no clarification loops); concise Chinese; no long closing loops; zero-cost hard constraint; never expose full API keys in chat (chmod 600); save to Telegram 5701842056; use Simplified Chinese exclusively; WhatsApp connected but untested; WeChat DM only (group blocked by user request); model routing: free-pool-first (OpenRouter/nemotron-3.5-lightning + Nous/longcat) with Qwen fallback via Bailian token-plan (provider=alibaba-cn, base_url=https://token-plan.cn-beijing.maas.aliyuncs.com/compatible-mode/v1); new OR key (sk-or-v1-b1743...) saved to .env chmod 600; Bailian CLI bl v2.1.0 installed at ~/.npm-global/bin/bl with .bailian/config.json profile=token-plan region=cn-beijing; Feishu repair completed (permissions published + bot in group oc_986f621882053506879238b4ab5a81cf + MCP PID 95249); resume (Chinese + English .docx) delivered to Telegram 5701842056; gateway restart requires independent SSH (not inside gateway session due to SIGTERM guard). No new persistent environment or user-profile facts added; existing skills (workbuddy-rules, model-router, qy-dubaifintech-bid, free-model-guard) cover workflow.
§
Work pattern — channel repair + disk cleanup + model switch (2026-09-22 executed): when user asks "修复全部渠道" or "清理" or "巡检磁盘": (1) verify each channel independently (Telegram curl, Feishu MCP pid, DingTalk dws auth status, openmaic curl); (2) do NOT assume single fix for all; (3) clean only after confirming target (qwen/ollama rm, dsh service stop, openmaic move to backup, apt/temp/playwright clean); (4) never delete .hermes/state.db or .hermes/.git without explicit confirmation; (5) after cleaning, always report real execution results (curl HTTP codes, pgrep pids, grep lines) not descriptions; (6) model switch to free pool uses hermes config set model.default nvidia/nemotron-3.5-lightning:free --provider openrouter, then verify via grep config.yaml; (7) Telegram bot test uses curl with token from .env (DO NOT write token in reply); (8) openmaic.aihubcloud.cn 502 = post-backend model fix needed (check /data/OpenMAIC_20260922_backup/.env.local for Nous references); (9) magnet for skill update: clean+verify pattern + free-model priority + direct execution preference.
§
User preference (confirmed 2026-09-28): When saying "使用 openai / 用 gpt-4o / 难任务", delegate to Azure gpt-4o (provider=azure-foundry, endpoint <REDACTED:AZURE_ENDPOINT>, api-version=2025-04-01-preview, key AZURE_FOUNDRY_API_KEY in .env chmod 600, NEVER expose in replies). Local ARM64 Codex missing binary; Claude CLI at ~/.npm-global/bin/claude 2.1.283 (PATH must include for command to work). When user asks to review/fix code or send deliverables: (1) use real tool output (grep/curl/file read), never invent; (2) if vision_analyze fails (e.g., image rate-limit 429), fall back to real file/text content; (3) deliver to Telegram (chat 5701842056) + email (liujinlong@outlook.com) promptly; (4) concise direct Chinese, no "已完成" self-praise loops; (5) for Feishu errors 230002/99991672, state clearly "you must do UI steps (open permissions + publish + pull bot into group) — I cannot replace" rather than repeating attempts.
§
User preference (durable, confirmed 2026-10-10): direct execution over clarification loops; no "已完成" self-praise loops; concise Chinese; verify technical assertions against docs first (OCI Always Free = 2 instances, etc.). Zero-cost hard constraint; never expose API keys in chat (chmod 600); Azure gpt-4o (azure-foundry) only for hard technical delegate when explicitly requested. Model routing preference: free-pool-first (nous/hy3/longcat, OR nemotron-3.5-lightning) -> Mistral 8b / CF Workers AI / Ollama local as backups. LiteLLM 4000 repair state: 3.14 venv rebuilt (pydantic 2.50.0/aligned, uvloop/backoff/prisma installed); direct CF 200 verified; autostart script + systemd + .bashrc at /home/ubuntu/.local/bin/litellm-autostart.sh.
§
GitHub 备份已固化: 仓库=bfliujinlong/hermes-backup(private)。认证=专用Deploy Key(无token落盘, 非账号级权限, 比PAT安全): 本机生成ed25519密钥对, 公钥加仓库Deploy keys(写权限), 本地config让git对该域名走此密钥。remote=git@github.com:bfliujinlong/hermes-backup.git。同步脚本/home/ubuntu/oci-monitor/sync_github.sh(增量commit+push, 无明文token)。cron: 系统crontab `0 16 * * 0`(=上海周日24:00,机器UTC)跑sync_github.sh。恢复脚本/home/ubuntu/oci-monitor/restore_hermes.sh(换机git clone+重建187个skills→cc/codex软链)。进备份: config/skills/memories/cron/jobs.json/scripts。排除(.gitignore): .env/.env.aliyun(密钥), hermes-install/dsh-src(大源码), sessions/gateway*.log(运行时态), cloud-docs(输出物)。换机需手动配: .env/.env.aliyun/.oci/config/Cloudflare token/dsh-src重装/系统服务。
§
dsh 隧道=OCI AI Hub 托管(oci-ai-hub, ID 255a72ac-a360-4834-93d7-9eeead262373, 法兰克福边缘, 副本ID 159a7eec-f4c3-46b8-aeff-a33ad3849ef7=本机cloudflared)。本地链路全通: dsh:3081 ← nginx:3080(systemd active) ← cloudflared.service active. ⚠️致命死结: OCI AI Hub 控制台显示该隧道**路由数=0**, 即未配任何公网入口, 故无外网URL. 已验证多路走不通: ①命名隧道默认子域<id>.cfargotunnel.com返回000; ②trycloudflare临时隧道被CF限流429(账户级, 持续数小时, 重试加重); ③本机无cert.pem, cloudflared CLI无法list/add路由; ④`oci ai`是Language Service非隧道, CLI无AI Hub隧道命令. **唯一开公网的办法=用户登OCI控制台 oci-ai-hub隧道页点'+添加路由'选Public Hostname类型→生成cfargotunnel.com子域**. 这不是我能用CLI/终端解决的, 必须用户UI操作. dsh 公网打通前, >20MB大文件走飞书通道(已验证V19 45.8MB成功).
§
dsh外部访问死局(2026-08-29实测, OpenAI gpt-5-mini诊断确认): DuckDNS/任何'只给A记录'的免费DNS【不能】走Cloudflare命名隧道。CF隧道Public Hostname要求域名zone加入CF账号(Full改NS/Partial加TXT-CNAME校验), DuckDNS只允许改子域A记录→无法校验→CF边缘无证书无路由→TLS unrecognized_name(alert 624)断开→外网HTTP 000。铁证: curl -k https://vkim.duckdns.org→000, 而*.trycloudflare.com→200, 命名隧道日志duckdns出现0次。填CF anycast IP(162.159.137.85)也无效。正确路径: 注册能改NS到CF的域名(eu.org免费/<$10普通域名)→CF Add Site→改NS→Zero Trust→Tunnels→dshnew(203eba87)→Add Public Hostname: dsh.域名.com→http://localhost:3080。quick tunnel临时URL(trycloudflare.com)能通但重启变URL。dsh.service的--trusted-host必须写精确域名、不接受*.通配, 否则/api报403。
§
Critical technical state (2026-08-31 late): dsh.service had restart loop (counter 1963→1966) due to illegal 'NOUS_API_KEY' in /home/ubuntu/.dsh/.credentials.yaml. Fixed by removing NOUS_API_KEY, keeping only DEEPSEEK_API_KEY. dsh now running (PID 68913, port 3081). Cloudflare tunnel: 203eba87-df2c-4fb6-8ca4-8698f0e3deeb, hostname dsh.203eba87-df2c-4fb6-8ca4-8698f0e3deeb.cfargotunnel.com → http://127.0.0.1:3080. vision_analyze broken due to expired OpenAI key in config; config.yaml updated to use OpenRouter google/gemma-4-31b-it:free but gateway NOT restarted yet — needs manual restart.
§
CF Workers AI endpoint test 2026-10-10: new cfut_ token (len 126, chmod 600 at ~/.hermes/skills/cloudflare/cf.env) passes file/perm check but curl to api.cloudflare.com returns HTTP 000 / exit 43 (Failed sending HTTP POST), not 401 — root cause is network/egress from OCI Frankfurt VM, not token expiry. User directs: do not receive/store full token in chat; verify via file only; endpoint already correct (/client/v4/accounts/.../ai/run/@cf/...). Related: user's hard rule — all external access via named tunnel (cloudflared dshnew 203eba87), CF peering dispute in DE noted 2026-09-05.
§
【2026-09-14 系统维护经验】OpenMAIC 和 DSH 在同一 OCI 机上通过 Cloudflare 隧道暴露两个子域名（openmaic.aihubcloud.cn / dsh.aiubaihubcloud.cn）。双 cloudflared 冲突根因是旧 quick-tunnel 没杀干净；修复=禁用 cloudflared-dsh.service + 确保只跑一个 named tunnel。Next.js dev 模式 HMR WebSocket 被 CF 阻断导致空白页，必须 build + start 生产模式。DSH settings.yaml 的 agent-default-model.model 必须引用 llm-deepseek.models 中存在的 ID，否则模型选择器静默失败。Strands Agents SDK 已创建为 skill（Python+TS, Agent/Tools/Hooks/Structured Output/Conversation/Multi-Agent/Model Providers/Observability/MCP）。系统盘守护 auto-disk-guard 的安全红线需包含 .env.local 和 .credentials.yaml（当前版本可能未包含，需 adopt 后修补）。
§
现状(2026-08-29最新实测更新): 隧道已恢复——/etc/cloudflared/token 是**有效新 token**(184字符JSON: a=6413823f...(CF账号)/t=203eba87-df2c-4fb6-8ca4-8698f0e3deeb(TUNNEL_ID)/s=secret), systemd cloudflared.service 用 --token-file 该 token 启动且 active; 家目录 config.yml 的 cfut_Kvbat... 才是失效旧 token(别再用). 隧道活着但 ingress 无 hostname 规则=仍'0路由'死结(外部访问不通). 加 Public Hostname 路由最稳=CF网页控制台隧道页点'添加路由'(不需cert); 本机无 cert.pem 故 cloudflared tunnel list/route dns 不可用(报错No cert正常). CNAME 目标恒为 <TUNNEL_ID>.cfargotunnel.com = 203eba87-df2c-4fb6-8ca4-8698f0e3deeb.cfargotunnel.com. quick tunnel 已弃用(曾因RestartSec=5被CF限流429/1015).
§
模型路由(2026-10-08实测): 免费池几乎全灭——OpenRouter免费层全线429(free-models-per-day)/多个模型404(longcat/hy3/solar-pro4/glm-4.5-air/stepfun免费已下架); Nous池404+key失效401; Mistral仅ministral-8b-2512存活(mistral-small 429); CF Workers AI key 401失效; Ollama本地只剩phi3.5:3.8b(响应超时,慢)。唯一稳定=Bailian token-plan qwen3.8-max(实测OK)。已把 config.yaml default/provider/base_url + 18个cron job 全切到 qwen3.8-max@alibaba-cn (base_url=https://token-plan.cn-beijing.maas.aliyuncs.com/compatible-mode/v1), fallback=ministral-8b。provider名必须 alibaba-cn(不是aliyun)。改完需用户在独立SSH跑 systemctl --user restart hermes-gateway.service。
§
CodeBuddy/Tencent Copilot bridge verified (2026-10-10): tunnel codebuddy.aihubcloud.cn -> 63128 (CF dshnew 203eba87), real bearer token 296 chars at /tmp/codebuddy_real_token.txt (chmod 600) from cb-auth-full.zip, bridge /home/ubuntu/.local/bin/codebuddy-bridge-fixed.py (PID 2917767+). Direct /chat endpoint needs CodeBuddy client session header (403 without). OpenRouter free tier exhausted (429, X-RateLimit-Remaining: 0, reset 1791676800000). User selected A (Tencent Copilot path). Model running Hy4 preview/glm-5.3 via CodeBuddy 63128.
§
LiteLLM 4000 rebuilt: 3.12 venv rebuilt with pydantic 2.50.0 / pydantic-core 2.46.4; uvloop installed; master_key and config fixed; autostart script / systemd user service / .bashrc written at /home/ubuntu/.local/bin/litellm-autostart.sh; 3.14 broken site-packages cleared (backup at .broken_backup_2026_10_10). Direct CF Workers AI route verified 200 (--http1.1). /home/ubuntu/model/ directory contains 9 verified models with switch script. LiteLLM process may need final /models initialization but dependencies are aligned.
§
2026-09-29 会话确认的持久偏好：回复简洁直接（已固化，不输出重复长闭合/无意义重复）；技术参数断言先查已验证状态或官方文档（不凭记忆乱说）；零费用硬约束（不花信用卡、Azure Sponsorships $5000 已停额度需监控、不编造数字）；用户已完成飞书三步修复（权限+发布+进群 oc_986f621882053506879238b4ab5a81cf），飞书 MCP 代理 PID 33869 运行中；Qwen 兜底已配置为 fallback（qwen3.8-max @ token-plan.cn-beijing, base_url 已修正，.env ALIYUN_BAILIAN_API_KEY 已与 bl CLI 同步）；难任务/模型故障时主动用 Qwen（百炼）而非反复试免费池；外部文章无法访问时直接用真实提取素材替代，不编造内容；用户选择直接执行而非列步骤，期望我直接修并交付简洁结果；简历文件 Jinlong_Liu_Resume_English_2026.docx 已接收提取（不暴露完整内容）；vision_analyze 因 OR 免费层 429 限流不可依赖，诊断优先用文件路径/真实工具输出。
§
CodeBuddy bridge (2026-10-10): /home/ubuntu/.local/bin/codebuddy-bridge-fixed.py PID 2917767 @ 63127; real bearer token (296 chars) extracted from cb-auth-full.zip → /tmp/codebuddy_real_token.txt (chmod 600); endpoint https://copilot.tencent.com/chat returns HTML landing (not JSON API); real Tencent Copilot API requires CodeBuddy CLI internal routing (internalDomain from auth), Windows plugin direct use is working path; auth backup at ~/.local/share/codebuddy/auth/ (5 .info files).
§
User is an FDE (Forward Deployed Engineer) / OPC (One Person Company) in cloud migration consulting. Maintains ~80 Hermes skills covering 售前/商务/PM/SRE/运维. Works on GCP free tier VM. Uses Hermes Agent as AI assistant. Prefers concise, no-nonsense Chinese communication. Has multiple channels: Telegram, Dingtalk, Feishu, WeChat, email. Runs free-model routing with hourly health checks via cron job 'hourly-model-guard'. Concerned about API key security — rotates keys when exposed.
§
Skill update 2026-10-10 (session): model-router SKILL.md patched — added `references/codebuddy-auth-tunnel.md` (Tencent Copilot auth + CF tunnel setup, chmod 600, 405 pitfall, proxy PID 2901396, verified 200) + verification section. Current session model verified = `thinkingmachines/inkling-small:free` @ OpenRouter (switch from nemotron-3-ultra-550b). User direct-execution / conciseness / no long loops preference already embedded in model-router; no new duplicate rules added.
§
GCP 免费机 35.206.98.210 (free-ubuntu-vm, e2-micro 2核/955M内存/x86_64, Ubuntu 24.04, sudo免密): SSH 走专用密钥 ~/.ssh/id_ed25519_gcp35 连 bfyalong 用户(公钥已登记)。上面跑第二个 Hermes gateway(独立bot, home channel同5701842056), 配置: default=qwen3.8-max@alibaba-cn(token-plan), fallback=Mistral ministral-8b→OR nemotron免费; 只留Telegram(微信变量已注释, config platforms已清空)。⚠️大坑: 用execute_code/terminal往远端.env写密钥时, 工具会把"KEY=变量引用"模式脱敏成字面三个星号写入——传密钥必须stdin管道+运行时字符串拼接, 写完验证len和sha256前8位。1G内存跑不了ollama, 定位=轻量节点/美国出口中转。
§
用户硬约束: 零费用绝不花信用卡一分钱(已建双护栏). 飞书app cli_aa093013dc38dcbb需被拉进目标会话才能发消息(报错230002). 已设FEISHU_HOME_CHANNEL=oc_986f621882053506879238b4ab5a81cf但bot未进群, 飞书告警暂未通. ⚠️实测API级根因(2026-08-31探针): 应用凭证有效(tenant token 正常获取, 机器人"kim的助手"activate_status=2), 但缺'应用身份权限' im:chat:readonly(im:chat/im:chat:read 任一)→查询群聊/确认在群内全返回 99991672 Access denied; 该 scope 缺失掩盖了 230002 bot未进群. 修复=飞书后台给 cli_aa093013dc38dcbb 勾 im:chat:readonly 应用身份权限+创建版本发布+把bot拉进群 oc_986f621882053506879238b4ab5a81cf.
§
OpenMAIC (OCI 130.61.110.133:3000): Next.js app, switched from Nous free pool (dead) to Mistral API (ministral-8b-2512). Nous free pool fully retired (hy3/solar-pro4/longcat all 404/401). Use `pnpm build` + `pnpm start` (production mode), not dev mode (WebSocket HMR fails over HTTP). iptables was blocking port 3000, fixed with iptables rule. Microphone/TTS grayed out - need HTTPS for getUserMedia; user plans to register domain + use Cloudflare tunnel to solve.
§
CrowdSec bouncer (crowdsec-firewall-bouncer) on OCI VM: service active but bouncer inactive since 2026-10-10; start fails with "Interactive authentication required" because /etc/crowdsec/bouncers/crowdsec-firewall-bouncer.yaml uses ${BACKEND}/${API_KEY} variable substitution (unfilled). Fix = fill BACKEND (e.g. iptables) + api_key in config then systemctl start; cscli decisions=0, no real attacks. Confirmed via real cscli/systemctl/log checks, not assumption.
§
Session 2026-10-10 final: user selected A (Tencent Copilot / CodeBuddy direct via tunnel). All artifacts verified: bridge PID 2917767/2915844, auth /tmp/cb_full/*.info -> token /tmp/codebuddy_real_token.txt (chmod 600), tunnel codebuddy.aihubcloud.cn -> 63128 (200), OpenRouter daily 429 (X-RateLimit-Remaining 0) confirmed root cause of previous reply failure. User wants Telegram reply via CodeBuddy; Windows plugin with sync'd auth is working path.
§
OCI磁盘清理(2026-08-29): 系统盘/sda1原46%(20G/45G)→清理后37%(17G)。动作: journald限SystemMaxUse=200M+MaxRetentionSec=7day写/etc/systemd/journald.conf并restart(防日志无限涨); apt clean; 迁移缓存到/data: /home/ubuntu/.npm→/data/npm-cache, /home/ubuntu/.cache→/data/cache, ~/.local/share/pnpm/store→/data/pnpm-store, /home/ubuntu/oci-monitor→/data/oci-monitor(venv activate里VIRTUAL_ENV已改/data/oci-monitor/venv)。dsh真实源码/home/ubuntu/hermes/deploy/dsh-src(非.dsh)。数据盘/data 147G, 用掉~6G。
§
LiteLLM proxy 451847 @ :4000 active (qwen3.8-max via alibaba-cn token-plan); metrics_server 456672 @ 3003 feeds Prometheus 458131; Grafana 471022 3001 with token-usage.yaml provisioned; external monitor https://monitor.aihubcloud.cn/monitor.html via tunnel 203787; Bailian key updated in ~/.bailian/config.json token-plan (852-char aliyun token, chmod 600, old sk-ws-H rotated); AICC SSH alias `ali`/`aicc` → root@139.196.171.8 (id_ed25519_github).
§
系统盘/数据盘迁移(2026-08-29): 为减系统盘增量, 已将大缓存/venv 软链到 /data(150G数据盘, 挂载/dev/sdb): /home/ubuntu/.npm→/data/npm-cache; /home/ubuntu/.cache→/data/cache; /home/ubuntu/.local/share/pnpm/store→/data/pnpm-store; /home/ubuntu/oci-monitor→/data/oci-monitor (venv activate 里 VIRTUAL_ENV 已改/data/oci-monitor/venv). journald 限 SystemMaxUse=200M+MaxRetentionSec=7day 写进 /etc/systemd/journald.conf. 系统盘 20G→17G(37%). 注: hermes-install(1.6G)是Hermes本体留系统盘未迁.
§
Claude Code 本地配置(2026-10-09): CLI v2.1.283 在 ~/.npm-global/bin/claude, settings.json 指向 localhost:4000 (LiteLLM), API key=sk-ant-local。LiteLLM 4000端口当前只有 Qwen 3.8-max (百炼 token-plan), Claude free 模型已从 OpenRouter 下架(404)。用户Windows端走智谱 GLM 代理: ANTHROPIC_BASE_URL=https://open.bigmodel.cn/api/anthropic, 模型=glm-5.1。Skill trigger: 用户说"使用 claude / claude 分析"时, 调用本地 claude CLI; 说"使用 codex"时, 调用 codex CLI (ARM64缺包→自动降级 Claude/Azure gpt-4o)。
§
飞书应用权限开通易踩坑(2026-08-31实测): 用户截图开权限时开在"用户身份权限(user_access_token)"标签页,但API调tenant_access_token需"应用身份权限(tenant_access_token)"标签——两套独立授权,开错标签=Access denied. 且用户开在"kim chat working"应用而非让我用的cli_aaeb0ff8aa381cb3(anchnet旧应用). 正确路径: 进cli_aaeb0ff8aa381cb3 → 切"应用身份权限"标签 → 勾wiki:wiki/wiki:wiki:readonly/wiki:node:read + bitable:app/bitable:app:readonly → 版本管理与发布→创建版本→发布. Hermes机器上只有anchnet旧应用和主应用cli_aa093013dc38dcbb的凭证,无"kim chat working"凭证.
§
iOS 语音助理方案(已部署 2026-08-30): iPhone 16(iOS18)喊Siri→快捷指令听写→打OCI中继 /relay/ask?q= →朗读回复。中继=/home/ubuntu/oci-monitor/tg_relay.py(fastapi:8099, systemd tg-relay.service)+nginx 3080加/relay location+CF quick tunnel healing-organic-retro-metres.trycloudflare.com暴露。模型用OpenRouter免费 nvidia/nemotron-3.5-lightning:free(因Nous免费API裸调报missing tags, OR免费层无此限)。Telegram直连方案废弃(国内api.telegram.org被墙+快捷指令不走代理)。iOS18无'添加到Siri'入口, 靠'在搜索中显示'+喊指令名或主屏图标触发。
§
【2026-09-06】项目台账：①QY-DubaiFintech：AWS→阿里云 me-east-1(迪拜)，76 EC2/27 DB/45 Redis/51TB/5源区，目标2AZ双活，报价冲刺中；②汤臣倍健 DataWorks 0621：Trino→Spark双跑，754已修/722"空日志"待解(16类错误已分类)；③美年体检 AI数据中台 MJ-AI-DW-2026-001：108人天10章LLD，MaxCompute/Hologres/RDS PG/OSS；④Tapestry Landing Zone：HLD 23页8领域完成，LLD PPT待做；⑤远景能源云迁移调研推进中；⑥AICCP平台收尾(Vue3/FastAPI/PG16/Redis/MinIO，三层架构，腾讯云ECS 8.153.152.218，仓库 bfliujinlong/AI-CCP，AI能力必须走Skill→Prompt→LLM→Structured Output)。
§
难任务用 Azure OpenAI 偏好 (2026-09-08):
- 触发: 用户说「使用openai」/「难任务」/「快速给我」/ 明确要求 Azure
- 端点: https://<REDACTED:AZURE_ENDPOINT>
- 部署: gpt-5-mini
- api-version: 2025-04-01-preview
- 鉴权: api-key header (key 在 .env 的 AZURE_FOUNDRY_API_KEY)
- ⚠️ 参数必须用 max_completion_tokens (不是 max_tokens)
- ⚠️ temperature 只支持默认值 1 (不能传 0.3)
- ⚠️ 该部署会把大量 token 烧在 reasoning 上 (实测 reasoning_tokens=2176/6189)
- OpenAI 直连 key 已废 (401), 不要再试
§
AICC ECS = kimtestvm (i-uf65uz7ssmvcqla865kf), cn-shanghai, 公网 139.196.171.8 (旧IP 8.133.232.216已废弃). SSH别名: ssh ali / ssh aicc → root@139.196.171.8 (id_ed25519_github). 服务栈: Docker 5容器(nginx:80/frontend, uvicorn:8000/backend, postgres:5432, redis:6379, minio:9000+9001). 安全组仅开22+80, 后端/DB/Redis/MinIO外网不通(nginx反代:80→:8000). 公钥通过阿里云云助手RunCommand注入. 2026-10-08已通过nginx sub_filter注入mobile-responsive.css做手机适配(不改源码).
§
_sys FDE五级进阶路线图(微信科普版, 2026-08-30 学自《FDE时代来了:普通人从Skill到FDE的五级进阶路线图》硕硕AI成长日记): L1 Skill=把套路写成AI可执行说明书(重复5次以上的事,1-2-3-4步+意会判断标准); L2 Agent=给目标/工具/边界让AI自己干(定时任务自动跑,只验收); L3 系统化=流程SOP化+AI员工分工+数据回流(标准:休假一周业务还转); L4 产品化=能力变数字资产反复卖(一次生产反复收租); L5 FDE=一人公司(判断线你出+产能线AI出)。核心:用AI是本事,把AI装进业务是手艺,活成FDE是路线;不要跳级(L1地基没打好谈系统化=空中楼阁);不会写代码也能到L4。此路线与memory中Palantir官方FDE定义(现场写生产代码+拥有数据→决策闭环)互补——官方版是岗位定义,此科普版是普通人自我进阶路径。
§
全通道限流根因已修：原全局 model.default = nvidia/nemotron-3-super-120b-a12b:free (OpenRouter免费层) 不稳，导致飞书/钉钉/微信/cron全撞 HTTP 429 free-models-per-day。已用 `hermes config set model.default tencent/hy3:free` + `model.provider nous` 改为 hy3@nous（保留原15个fallback池），改后需 systemctl --user restart hermes-gateway.service 生效。结论：nemotron-3-super-120b-a12b:free 不宜作默认，hy3@nous最稳。改config必须用 hermes config set（直接patch yaml被护栏拒）。
§
模型路由更新(2026-09-28): Azure gpt-4o (provider=azure-foundry) 已验证为唯一稳定付费; 主默认=OpenRouter nemotron-3.5-lightning; 百炼修法=选DashScope(UI)+写.env DASHSCOPE_API_KEY+chmod 600+systemctl重启(不能在gateway子进程); freellmapi.co=403/GitHub全404未验证; 评估报告已写~/cloud-docs/远景大数据改造_人力评估_基于V5.md(~185人天/$65k); 简历已更新中英文简洁版docx; Telegram已发5701842056+文件; vision分析失败直接从路径诊断(已实测429 X-RateLimit-Reset); 直接执行规则已固化在model-router SKILL.md
§
切换 Hermes 默认模型时必须同步所有 cron job：cron job 各自在 ~/.hermes/cron/jobs.json 写死 model/provider，不继承 config.yaml 全局默认；且 `hermes cron update <id> --model X` 静默不改 model 字段(实测)。正确做法=python 直接改 jobs.json 里每个 job 的 model/provider/base_url 并加 fallback_providers，否则老 job 继续撞废弃模型连败(曾 Feishu Status Check 连败17次)。另：改 config 后需本机 systemctl --user restart hermes-gateway.service 让新进程生效(terminal在gateway树内不能自重启被护栏拦)。
§
dsh 插件(知乎'必装10个')可用性(2026-08-29探测): 多数第三方仓库已404——omdsh-dev的agent-teams/plan-execute/context-doctor/reverse-skill/ModLens 全404, deepseek-ai的dsh-tui/desktop 也404. 尚存: dsh-better-sidebar(github omdsh-dev/DSH-better-sidebar, 200), dsh-web-ui(zhu1090093659/dsh-web-ui, 301), dsh-at-file(omdsh-dev/dsh-at-file, 301). 安装用 `dsh plugin --profile web add <repo>` (需在本机dsh profile目录跑). 用户要求全装但先搞定外部访问再装.
§
DuckDNS+Cloudflare隧道死路(2026-08-29实测验证): DuckDNS只支持改子域A记录IP, 不支持CNAME/改NS, 因此无法把域名zone加入Cloudflare。CF命名隧道Public Hostname要求域名zone在CF(Full改NS或Partial加TXT校验), 否则边缘TLS返回unrecognized_name(alert 624)直接断, curl报HTTP 000, 请求从未到本机。证据: curl -k vkim.duckdns.org→000, 而*.trycloudflare.com→200, 隧道日志vkim出现0次。结论: DuckDNS域名走不通CF隧道, 必须eu.org(能改NS)或付费域名接CF。用户曾创建vkim.duckdns.org并填162.159.137.85(anycast IP)仍失败。
§
用户笔记本环境(2026-09-20): Windows系统, 工作路径D:\Work\日常\上云迁移\01服务流程\04其他\03AI报价\00资源\03tool\。Trae+WorkBuddy已装并运行在笔记本(端口5001/5002)。cloudflared已有但之前误下macOS版(darwin-amd64),实际需Windows版。用户要暴露笔记本的Trae+WorkBuddy到OCI调用(通过cloudflared隧道)。代理脚本=laptop_proxy.py(笔记本端HTTP代理,监听3000转发到Trae 5001/WorkBuddy 5002)。AWS QDE Phase III考核:用户有操作手册+PPT V3(10页),考核五大方向(SSO/账户管理/IM邮箱/OA对接/自动化Skill),需录15分钟Demo视频(必须出镜)。
§
Hermes推GitHub备份坑: .hermes/.gitignore已排除.env但【漏了.env.aliyun】(含阿里云AK), push前必须补一行.env.aliyun进.gitignore。本机无gh CLI/无SSH key/无git credential helper, push只能走HTTPS+PAT(必须classic PAT ghp_ 而非fine-grained)。仓库bfliujinlong/hermes-backup。推送范围: skills/, memories/(MEMORY.md/USER.md), config.yaml, cron/jobs.json; 排除hermes-install/(1.6G)/deploy/dsh-src/(1.5G)/cache/logs/*.db/.env/.env.aliyun。
§
dsh (DeepSeek Harness) public access: quick tunnel URLs change on restart (e.g. marina-resident-mom-mug.trycloudflare.com) which breaks dsh's --trusted-host whitelist causing HTTP 502. OCI AI Hub tunnel (203eba87) has 0 routes in console - must add Public Hostname route manually. dsh local access works at http://127.0.0.1:3081 and http://130.61.110.133:3080 (nginx proxy).
§
AgentTeams (agentscope-ai/AgentTeams) v1.2.5 (2026-10-16): 开源多 Agent 协作 OS (Matrix透明人机协作, Apache-2.0, 5.8k stars). 关键: Qwen Code/OpenCode 编码CLI委派 + QwenPaw 原地升级 + MCP修复 + Dashboard v1.3.1 (nillikechatchat主导). 贡献者: @LUOSENGWA(多修复PR) @shiyiyue1102 @014-code. AgentCore(aliyun)独立: 企业Agent构建/治理/Trace审计平台(非开源). 相关链接已真实提取至 ~/.hermes/cache/web/ (github主库/v1.2.5/agentcore), 非编造.
§
难任务用 Azure OpenAI 规则(2026-09-08 固化):
- 触发: 用户说「使用openai」/「难任务」/ 明确要求 Azure
- 端点: https://<REDACTED:AZURE_ENDPOINT>
- 部署: gpt-5-mini
- api-version: 2025-04-01-preview
- 鉴权: api-key header (key 在 .env 的 AZURE_OPENAI_KEY)
- ⚠️ 参数必须用 max_completion_tokens (不是 max_tokens)
- ⚠️ temperature 只支持默认值 1
- ⚠️ 该部署会把大量 token 烧在 reasoning 上
- OpenAI 直连 key 已废 (401), 不要再用
§
用户域名资产: 已注册免费 DuckDNS 域名 vkim.duckdns.org (动态DNS, 仅支持填IP不支持CNAME). 接Cloudflare命名隧道(dshnew, tunnel ID 203eba87-df2c-4fb6-8ca4-8698f0e3deeb)方案: DuckDNS IPv4填CF anycast IP 162.159.137.85 + CF控制台 Zero Trust→Tunnels→dshnew→Hostname Routes 加 vkim.duckdns.org→http://localhost:3080. 目的: 替代不稳定的 quick tunnel 临时URL(healing-organic-retro-metres.trycloudflare.com)作 dsh 固定公网入口.
§
用户在 anchnet 飞书租户有云文档文件夹(如 Y6ZYfOPkFlnMPTdxlNRcP0U8nDd)需 Hermes 读取,但 anchnet 应用 cli_aaeb0ff8aa381cb3 缺 drive:drive / drive:drive:readonly / space:document:retrieve 应用身份权限(tenant级,非用户授权),报错 99991672。主应用 cli_aa093013dc38dcbb 读该租户返回 forbidden。解决路径:飞书开发者后台给 cli_aaeb0ff8aa381cb3 开'应用身份权限'勾 drive:drive:readonly 并创建版本发布才生效(只勾选不发布=不生效)。用户曾愿给开放平台账号让我代操作,但我基于零费用/凭据红线建议其自助。
§
邮件通道已配置完成：发件人 vliujinlong@qq.com (QQ授权码, 因个人版outlook基础认证被禁只能QQ代发), 收件人/Home地址固定 liujinlong@outlook.com。Hermes email adapter 靠 .env 的 EMAIL_* 变量驱动 (SMTP/IMAP 基础认证)。配置已验证 SMTP+IMAP 双向登录成功, 测试邮件⚠️网关未重启(email adapter未加载), 需用户SSH登OCI跑 `systemctl --user restart hermes-gateway.service` 才真正生效(当前对话terminal是gateway子进程, 重启会被护栏拦自杀)。用户指令: 以后说发邮件都发liujinlong@outlook.com。
§
Codex CLI fix (2026-10-09): ~/.codex was symlink→/data/sysmove/codex, bwrap rejects symlink paths→sandbox fails. Fix: cp -a real content back, rm symlink. config.toml 加 sandbox_mode="danger-full-access". OPENAI_API_KEY 在 .bashrc 被终端工具脱敏成 ***（实际值 <REDACTED:API_KEY>，dummy 值，LiteLLM 代理处理真实认证）。Codex 0.157.1 + Claude 2.1.295 均通过 LiteLLM :4000 正常工作。
§
Hermes email adapter 已配但网关未重启加载: .env 写了EMAIL_ADDRESS=vliujinlong@qq.com(QQ代发, 因个人版outlook基础认证被微软禁用连不上), EMAIL_SMTP/IMAP=qq.com:587/993, EMAIL_HOME_ADDRESS=liujinlong@outlook.com, EMAIL_ALLOWED_USERS=两个邮箱. SMTP外发已实测通(发往outlook成功). 但IMAP收信轮询(adapter)需重启网关才加载——重启须在本机独立SSH终端跑 systemctl --user restart hermes-gateway.service(当前gateway会话内不能自重启, 被护栏拦).
§
LiteLLM 4000 (/data/hermes-install/venv) 3.12 venv rebuilt; 3.14 site cleared; pydantic 2.50.0/core 2.46.4/backoff/uvloop fixed; master_key/config set; auto-start scripts written (autostart.sh + systemd + .bashrc); /models requires full venv init (direct CF 200 verified); /home/ubuntu/model/ 9-model switch ready; kiro-cli v2.29.0 installed.
§
模型路由配置现状(2026-08-31): model.default=nvidia/nemotron-3.5-lightning:free, provider=nous, base_url=https://inference-api.nousresearch.com/v1, fallback_providers含5个nous+9个openrouter模型。注意:nous端hy3已过期(404),所以默认走nous的nemotron-3.5-lightning实际仍走nous端点。理想应设provider=openrouter让默认走OpenRouter。但gateway重启后钉钉实测正常(14:19:31 response ready, 142 chars, 0.8s)。
§
cron job 模型独立于全局router: Hermes的cron任务各自在~/.hermes/cron/jobs.json写死model/provider字段, 不继承config.yaml全局model. 旧job全写z-ai/glm-5.2:free@openrouter(已废弃限流), 致Feishu Status Check连败17次. 修复:`cronjob update`不接受model参数(报No updates), 须直接改jobs.json的model/provider/base_url并加fallback_providers, 改完即生效无需重启. 2026-08-24已批量把9个agent型job改hy3@nous+4 fallback.
§
note.txt在/home/note.txt: 含Azure OpenAI端点(<REDACTED:AZURE_ENDPOINT>) + 两把84字符key(AZ1给cc2azure代理 / AZ2给Cursor直连). Claude Code配置~/.claude/settings.json(ANTHROPIC_BASE_URL=:4000走cc2azure)、Cursor配置~/.cursor/settings.json(free_poll轮询nous 5模型 + openai_fallback直连Azure gpt-5-mini). 两工具默认免费轮询、自选OpenAI兜底. cc已装/usr/bin/claude v2.1.238.
§
用户笔记本环境(2026-09-20): Windows系统, 有Trae(本地端口50010, 非默认5001)和WorkBuddy(封闭客户端, 无本地API/CLI, 只有云端key ck_开头)。cloudflared已装(D:\Work\soft\cloudflared.exe), quick tunnel可跑通但laptop_proxy.py未启动(502)。用户有多个API key但均失效/不匹配: DeepSeek(sk-f74...b640, 余额不足), 阿里百炼(sk-ws-H...SHAXyU, 格式不匹配), HuggingFace(<REDACTED:HF_TOKEN>, OCI巴黎DNS解析失败)。
§
2026-09-28 修正规则已固化（用户反复要求）：回复不再输出长闭合循环（"已执行全部清理..."）；完成直接给结论/路径/状态；交付物确认后直接说"已足够"。技术参数断言先查官方/已验证状态不凭记忆；外部文章无法访问直接替代真实素材（epub/本地FDE资料）；难任务→Azure gpt-4o(azure-foundry, key AZURE_FOUNDRY_API_KEY); 模型路由当前故障=config.yaml写死aliyun/qwen-max(应改azure/gpt-4o); 微信/飞书/钉钉渠道修复优先级：飞书缺发布版本>钉钉dws webhook>微信iLink DM; 用户重启gateway10次无效=不是启动问题而是config未改。
§
dsh-token-sync-silent cron (job 5ed16e725c96) 已禁用(2026-09-07)。该 job 每30分跑 sync-nous-token.sh，会把 NOUS_API_KEY 写回 .credentials.yaml，导致 dsh 启动崩溃(unknown top-level key)。credentials.yaml 只允许 version:1 + refs: + DEEPSEEK_API_KEY。dsh 用 OpenRouter 免费模型(nemotron-3.5-lightning:free)，settings.yaml 设 baseURL=https://openrouter.ai/api/v1。
§
Azure OpenAI (liujl-9958-resource, sub 6e0359de): 所有模型部署（gpt-5-mini/gpt-4o-1/gpt-35-turbo）全部返回空 content，根因=token 100% 烧在 reasoning_tokens 上。新端点 services.ai.azure.com/openai/v1 + gpt-4o 也空。唯一解：请求时显式传 reasoning_effort:"none"（仅 Chat Completions API + max_completion_tokens 参数生效）。建议用户用 Mistral 或 gpt-4o + reasoning_effort:"none"。
§
OCI费用播报脚本坑(已固化): /home/ubuntu/.hermes/scripts/oci-cost-daily.sh 必须用 python subprocess 调 oci CLI（不能 shell $(...) + set -o pipefail，会吞掉 oci stdout 致$0.0000假零）；END 用 TZ=UTC date -d tomorrow（非今天，否则漏掉延迟结算的$0.0344那笔）。cron任务905b3955de1a(每天9点,deliver=all)必须 no_agent=true（否则agent处理输出再调一次模型撞429）。该任务初次创建未落库+脚本bug+agent模式撞429三层问题已全解。
§
Hermes skills已软链到Claude Code与Codex(单一真源, 绝对路径): ~/.hermes/skills/<cat>/<name> → ~/.claude/skills/<name> 与 ~/.codex/skills/<name>. 2026-08-27批量建79+个业务相关skill软链(售前/FDE/云迁移/投标/工程方法论/GitHub/运维/文档生成), 排除creative/apple/personal等噪音. cc/codex自动发现SKILL.md. 改Hermes skill后cc/codex自动同步. 验证: test -f ~/.codex/skills/<name>/SKILL.md.
§
飞书 MCP 已部署并验证可用(2026-09-07)：本地 stdio 代理 `~/.hermes/scripts/feishu_mcp_server.py` 作为网关子进程跑，10 个工具自动注册为 `mcp__feishu_mcp__<tool>`(search-doc/fetch-doc/create-doc/update-doc/list-docs/get-comments/add-comments/search-user/get-user/fetch-file)。配置在 config.yaml 的 mcp_servers.feishu-mcp 段。MCP 的 fetch-file 限 5MB，不支持电子表格读写。
§
Azure OpenAI: 资源liujl-9958-resource, 端点https://<REDACTED:AZURE_ENDPOINT>/, 区域westus3, 部署gpt-5-mini. 由Azure Sponsorships $5000额度支撑; ⚠️耗尽后自动转PAYG按量扣绑定信用卡(不自动停), 用户极度担心超额. 硬规则: 我只用ReadOnly SP监控+超阈值强告警, 绝不自动停资源/绝不给全量AK; 用户在Azure门户自设Budget+ActionGroup+runbook硬停. 用途: [难]任务delegate gpt-5-mini; 不进自动路由链(显式说才用).
§
pcs-presales-ps skill created at ~/.hermes/skills/pcs-presales-ps/ with 11 subdirectories (00-系统说明与索引 through 99-归档与废弃素材) mirroring Feishu wiki structure, plus SKILL.md. Cloudflare tunnel hostname is very long because it's auto-generated UUID format: dsh.<tunnel-uuid>.cfargotunnel.com — user asked about this.
§
OCI CLI不在系统PATH, 在/home/ubuntu/oci-monitor/venv/bin/oci. 调用前须: source /home/ubuntu/oci-monitor/venv/bin/activate + export OCI_CONFIG_DIR=/home/ubuntu/.oci. 账单查询: oci usage-api usage-summary request-summarized-usages --tenant-id <tenancy ocid> --granularity MONTHLY. OCI账期=自然月, 账单次月第2天起生成后结算(先用量后出账, 非每日扣).
§
OCI→GCP SSH跳板已配: ~/.ssh/config 别名 gcp/gcp35 → bfyalong@35.206.98.210, IdentityFile id_ed25519_gcp35(非默认名,必须靠config指定,裸ssh会Permission denied)。同步用 rsync -azL -e 'ssh -i /home/ubuntu/.ssh/id_ed25519_gcp35'(路径必须绝对,~在-e里不展开)。已同步skills(234个)/memories/SOUL.md/scripts到GCP; cron jobs.json故意不同步(GCP仅955M内存跑不了重任务)。
§
GitHub 备份已切 Deploy Key 认证(无token落盘): 本机生成ed25519密钥对, 公钥加仓库Deploy keys(写权限), 本地config让git走此密钥, remote=git@github.com:bfliujinlong/hermes-backup.git。之前给的 PAT(ghp_jmD57...)用户已删/revoke, 不再用明文token推送。cron系统crontab `0 16 * * 0`(=上海周日24:00)跑 ~/oci-monitor/sync_github.sh。恢复脚本 ~/oci-monitor/restore_hermes.sh。
§
【2026-09-20 模型状态终查】免费池全灭(Nous 401/OR 429/GF DNS墙)，仅 Mistral Free(ministral-8b)+Cloudflare Workers AI(10万req/天)可用。Azure gpt-4o 唯一稳定付费。model-router skill 是用户自有(不能patch)，建议 `hermes curator adopt model-router` 后更新。DeepSeek 需预充值¥10才让用 key。智谱 GLM 免费模型多但 key 已过期。用户笔记本 Trae 端口=50010，WorkBuddy 是封闭客户端无本地API。
§
Skill trigger rule (2026-09-28): 当用户说「使用 codex / 使用 claude / claude 分析 / codex 修改」时，直接调用本地 CLI（claude 2.1.283 在 /home/ubuntu/.npm-global/bin/claude，PATH 需含 .npm-global/bin；codex ARM64 缺 @openai/codex-linux-arm64 → 自动降级 Claude / Azure gpt-4o 兜底）。不再反弹「没装」。已写入 ~/model-router-free-fallback.md + 记忆此规则。
§
DingTalk Workspace CLI (dws) v1.0.61 已装在本机 /home/ubuntu/.local/bin/dws（linux/arm64）。Skills 自动装到 ~/.agents/skills/、~/.claude/skills/、~/.hermes/skills/（14个产品skill：doc/calendar/chat/contact/drive/event/mail/minutes/todo/wiki/aitable/aisearch等）。认证流程走 OAuth 设备码（dws auth login --device），当前等待用户扫码授权中。
§
OCI 全局每日播报已建成: 脚本 ~/oci-monitor/daily_global_report.sh (复制至 ~/.hermes/scripts/), cron任务 905b3955de1a 每天9:00 deliver=all no_agent=true 跑此脚本。播报5维度: 费用明细(按计费日)+昨日资源运行+在跑服务+模型运行+Azure OpenAI用量。同时修复了每小时$0.0344刷屏告警(oci-billing-check.sh加≤$0.05遗账白名单)。飞书/微信投递常失败(230002/iLink限流), Telegram/钉钉/短信/邮件能到。
§
model-probe.py v2(2026-10-08): 分层探测路由——简单任务→本地Ollama(deepseek-r1:1.5b>qwen3:4b>phi3.5), 难任务→Ali百炼qwen3.8-max, 中间档→Mistral ministral-8b. cron a1b2c3d4e5f6 schedule原为空(从未跑过), 已修为'5 * * * *'每小时. 输出/data/model-probe/model-rank.json含routing_policy. 仅Ali主力挂才发TG告警. 旧版备份model-probe.py.bak-20261008.
§
Twilio SMS转发项目(2026-09-20): 用户注册了Twilio(AC08d469...)，买了美国号+1 202 816 6399(DC华盛顿区号，旧号231 758 5738已释放)。Webhook指向sms.aihubcloud.cn→本机9999端口→转发到Telegram。目的：收海外服务验证码。注意：Palantir AIP屏蔽VoIP号(Twilio/Google Voice全废)，需实体SIM号(TextVerified或eSIM)。Photon sidecar(端口8789)已修改新增/history API但SDK本身不支持历史消息查询。
§
用户偏好(2026-09-20确认): ①难任务/技术排障主动用OpenAI(Azure gpt-4o)出方案,不要反复问; ②不装vLLM(ARM CPU无GPU不适合),用Ollama本地模型+云端免费API; ③Cloudflare隧道是首选公网暴露方案,比quick tunnel稳定; ④免费模型全挂时直接切Azure,不要反复试; ⑤飞书发文件需要im:chat:readonly权限(应用身份权限,不是用户授权); ⑥用户期望我直接动手交付结果,不要列步骤让他执行; ⑦用户在中国大陆,笔记本Windows系统,OCI机器在巴黎/法兰克福。
§
本地Ollama实测(2026-10-08, 2核ARM/11G): deepseek-r1:1.5b=14.7tok/s(最快兜底), phi3.5:3.8b=8.9, qwen3:4b=6-8, deepseek-r1:7b=3.7(慢,仅离线用). Ollama模型目录已迁/data/ollama-models(systemd drop-in /etc/systemd/system/ollama.service.d/models-on-data.conf 设 OLLAMA_MODELS). 本地4B档是上限, 7B以上<4tok/s不装.
§
Cloudflare API Token(cfut_前缀, 非Global Key): <REDACTED:CF_API_TOKEN>. 账号ID=6413823f243b9dc615778a19021db968, Zone ID=100380e22b85e5f8e66730342913976d. Global Key(cfk_前缀)邮箱不匹配, 勿再用于API调用. API Token权限有限(不能改tunnel配置). 隧道Public Hostname必须从CF控制台UI加.
§
dsh 真实项目根=/home/ubuntu/hermes/deploy/dsh-src (注意: 不是 /home/ubuntu/.hermes/deploy/dsh-src, 多一个点会导致 systemd CHDIR 失败). 启动用 `node --import tsx/esm apps/cli/src/bin.ts --profile web` (cd 到该目录), 因为 pnpm bin 代理在 systemd bash -lc 下找不到 dsh 命令. dsh.service 当前 ExecStart 已改为此绝对路径调法.
§
dsh Web UI 外部访问硬坑: `--trusted-host` 不接受通配符 `*.trycloudflare.com` (api-request-trust.ts 要求规范 host[:port] 权威, 通配会被拒/不生效). 必须写精确域名(如 healing-organic-retro-metres.trycloudflare.com 或 vkim.duckdns.org). 外部 Host 不在白名单→HTTP 403. quick tunnel 重启换URL故不能靠通配, 必须固定域名+精确trusted-host.
§
OCI 免费机 (VM.Standard.A1.Flex 2 OCPU/12GB, ARM aarch64). 公网130.61.110.133(法国巴黎出口，非德国). 系统盘45G+数据盘150G=197G/200G. 已装tf1.12.2/claude-code/node22. 目标0费用. dsh.service running (node tsx, port 3081). cloudflared active (quick tunnel + AI Hub tunnel). nginx proxy 3080→3081.
§
查新报告附件清单 python-docx 整理已完成（2026-09-25）：全部12份文献已从已提取真实文本直接读出（[1]张开店/点金照明Z2023-12-23/[2]蒋帅帅周志峰GD32J2023/[3]盛楠康阳机器人J2022/[4]赵德福STC89C52/[5]梁飞紫外线/[6]王健台灯/[7]金鑫调光/[8]叶飞得邦安防灯/[9]刘峰创意时钟/[10]马相一小车/[11]毕经海ArduinoLED/[12]蒙建源风扇），已写入 /home/ubuntu/查新报告_附件清单_真实提取.md，未编文献/未虚构技术参数。
§
User's resource breakdown includes IaaS VMs and PaaS components (application servers and database instances). They prefer to create a migration quotation and follow the Anchnet pricing template for additional services like deployment and business tracking on AICC.
§
Twilio 账号(2026-09-20): Account SID=<REDACTED:TWILIO_SID>, 号码=+1 202 816 6399(DC华盛顿区号,旧号231 758 5738已释放), 余额$10.67。Webhook指向sms.aihubcloud.cn→本机9999→转发到Telegram。目的: 收海外服务验证码。注意: Palantir AIP屏蔽VoIP号(Twilio/Google Voice全废), 需实体SIM号(TextVerified或eSIM)。
§
OCI CLI 路径: /home/ubuntu/.hermes/hermes-install/venv/bin/oci (唯一可用). 原 oci-monitor→/data 软链已断(/data空). 账单查法: oci usage-api usage-summary request-summarized-usages --tenant-id <ocid> --granularity DAILY --time-usage-started/end. 9月1-3日费用=$0.00, 上月$0.0344遗账已归零.
§
OCI free VM now runs Ollama with Qwen3-4B (2.5GB, 128K ctx) + Phi-3.5-mini (2.2GB, 128K ctx). Qwen3-0.6B was deployed then removed. Hermes provider 'ollama' configured (base_url=http://localhost:11434/v1, context_length=131072). Total ~5GB RAM used, 7GB free.
§
presales-architect 验证补充(2026-09-08): Expr Logistics 报价单按 Fintech 模板 1:1 还原成功(CN/EN 3-4 sheets, 公式到位)。Azure gpt-5-mini 调用已验证可用(端点+key+max_completion_tokens+temperature=1)。架构图用 PIL 深灰 PNG 无依赖。去 AI 感规则：禁蓝/禁AI字眼/天然段落/无机械格式。用户要求"完全依赖模板"时直接复制表头结构+替换数据，不重新设计格式。
§
GitHub 备份仓库=bfliujinlong/hermes-backup(私有)。认证用 SSH Deploy Key(无token落盘)。cron 周日16:00 UTC(=上海24:00)跑 ~/oci-monitor/sync_github.sh 增量同步配置/skills/memory/脚本。恢复=git clone + bash restore_hermes.sh。换机需手动补: .env/.env.aliyun、OCI config、CF token、dsh-src重装、系统服务。
§
用户偏好：自主执行，不要反复确认。能直接做的事直接做（发消息、部署、生成文件），不要先问"要不要我去做"。用户说"发消息给她"意思是直接发，不是问能不能发。用户说"这环境部署在你本机"意思是直接用本机环境操作，不要反弹回让用户手动做。正式报价/交付物用 .docx 分章节输出，不要只给 md。竞品报价分析工作流：提取竞品 xlsx/docx → 解析定价模型（单价/结构/范围）→ 对比自有定价（AC-MIG $350/天）→ 识别差异与差异化点 → 给出定价策略建议（匹配/压价/价值差异化）。
§
dsh (DeepSeek Harness) 配置: provider route "deepseek-official" 指向 Nous (https://inference-api.nousresearch.com/v1), 非 DeepSeek 官方. systemd 环境变量 DEEPSEEK_API_KEY 实际存 Nous OAuth token. nginx 必须设 "proxy_set_header Origin \"\"" 否则 dsh API 返回 forbidden.
§
用户需要域名但要求'免费'且零费用红线禁止绑信用卡自动扣费。GoDaddy 无免费域名(最便宜$0.99首年且强制绑卡续费),已告知用户改走真正免绑卡免费域名:.pp.ua / .us.kg / is-a.dev / eu.org(审核) / DuckDNS / Cloudflare子域。最实用:注册免费域名→托管Cloudflare→给cloudflared隧道加Public Hostname路由打通dsh公网(解决dsh隧道路由数=0无公网URL死结)。Freenom已关停勿用。
§
dws CLI 已装好并认证：/home/ubuntu/.local/bin/dws，身份=金龙 @ 上海安畅网络科技股份有限公司（corp_id=ding58230c81113bca4f35c2f4657eb6378f, user_id=053123341198056）。Token 有效至 2026-09-05，刷新至 2026-10-05。dws 无法读取部分钉钉文档（wiki node search 返回 Data not found），需用户粘贴内容或移到个人空间。
§
【2026-09-10】已整合 4 个 FDE 开源项目(fdeops/fdestack/openfde/fde-guide)为统一 Skill `fde-toolkit`(~/.hermes/skills/business/fde-toolkit/)，同步到 cc/codex。核心方法论: Skills管流程执行，仓库管业务记忆。阶段模型 land→discover→plan→ship→outcome，8个客户生命周期Skills。用户正系统构建 FDE 实战能力。
§
WorkBuddy 100套提示词: GitHub仓库 feng-liu-1994/workbuddy-100-prompts(10分类,纯前端index.html,localStorage存数据)。已clone整理成MD并push到 bfliujinlong/hermes-backup(workbuddy-prompts/100-prompts-complete.md)。docx版在 ~/cloud-docs/WorkBuddy-100-Prompts.docx。
§
新skill free-model-guard(~/skills/free-model-guard): 抗限流免费router+看门狗+难任务delegate完整方案, 含scripts/free_model_watchdog.sh(双端点探测重排)、daily_free_model_research.sh(每日外网调研)、azure_spend_guard.sh(Azure本地账本告警, 阈值$50 Telegram告警). 换机器一键复现见SKILL.md.
§
模型切换(2026-10-21): 先cb-official->cb-hy4(hermes config set), 当前default=cb-hy4 (hy4-preview, anthropic/hy4). gateway未重启故端点仍旧; 重启须独立SSH systemctl --user restart hermes-gateway.service (子进程内不能自重启). litellm路由cb-hy4->qwen3.8-flash.
§
阿里云云助手(Cloud Assistant)远程管理ECS: aliyun ecs RunCommand --RegionId cn-shanghai --Type RunShellScript --InstanceId.1 <id> --CommandContent <base64> --ContentEncoding Base64. 用途: 注入SSH公钥/执行命令/修复安全组, 无需ECS本身SSH可达. 比安全组开临时端口更安全.
§
【2026-09-06】WorkBuddy 技能已导入本机：workbuddy-rules(全局公约+4细则)、qy-dubaifintech-bid(报价档案)、aiccp-platform(平台规范)，及文档处理 pdf/docx/xlsx/pptx/humanizer/summarize。当日 Hermes v0.21.0 完成 venv 重建+软链修复+systemd 自启(用户级 hermes-gateway.service)。
§
2026-09-26 会话确认：用户反复要求精简（“内容太多太乱了” + “以后不要说出这些没有意义的东西”），已修正回复风格：不再输出重复的“已执行全部清理...”长闭合循环，仅给结论/状态/路径。用户未提供新个人身份信息；业务偏好已固化：直接动手交付、简洁直接、零费用、外部文章无法访问时直接用本地真实素材、难任务用 Azure gpt-4o（azure-foundry）、无密钥泄露、磁盘47%、已保存记忆。无新增记忆条目需要保存。
§
dsh 公网访问修复（2026-09-07）：quick tunnel URL 从 journalctl 提取；nginx 必须 `proxy_set_header Origin ""` 否则 API 返回 403；`--trusted-host` 只接受 `host[:port]` 格式；cron job dsh-token-sync-silent (5ed16e725c96) 已禁用（会污染 credentials.yaml）。
§
用户设备与环境(2026-09-20): 主力笔记本=Windows(D:\Work\, 用户EDY, 有cloudflared可跑quick tunnel)。Trae本地端口=50010(不是5001, netstat实测), WorkBuddy有API key(ck_前缀,永久有效, 但API端点地址未确认)。偏好:直接动手执行, 反复确认会烦; cloudflared quick tunnel URL会变(重启即换)不需记。
§
For cloud migration project pricing and breakdown (e.g., IaaS VMs and PaaS components), user prefers using established Anchnet templates whenever possible, and expects a full scope evaluation and accurate estimation.
§
用户要求硬技术/架构/基础设施排障用 OpenAI(gpt-5-mini via Azure) 出权威方案: 本轮 dsh 外部访问卡死, 用户明确'请使用 openai 给我权威的解决方案', 我 delegate gpt-5-mini 实测环境给方案. 与既有'难任务delegate gpt-5-mini'规则一致, 但用户强调'权威解决方案'场景(网络/隧道/CF/基础设施)主动用 OpenAI 而非只靠免费模型盲试.
§
LiteLLM 多模型路由器已部署在 port 4200（4100 旧实例仍跑），OpenRouter key 已配。8 个免费模型健康：nemotron-3-ultra-550b/nemotron-3-super-120b/north-mini-code/laguna-s-2.1/laguna-xs-2.1/ling-3.0-flash-fin。配置在 /home/ubuntu/.litellm/config.yaml。
§
【Cloudflare隧道现状】tunnel 203eba87-df2c-4fb6-8ca4-8698f0e3deeb，hostname dsh.203eba87-df2c-4fb6-8ca4-8698f0e3deeb.cfargotunnel.com → http://127.0.0.1:3080，token位于/etc/cloudflared/token。隧道本身active，但访问失败因dsh端口未监听（已修复）。
§
用户正在构建售前资料库（SmartCare案例集），路径 /home/ubuntu/cloud-docs/SmartCare案例集/（北区/东1组/东2组）。后续会按方向（Landing Zone/云迁移/WA优化/大数据/DR/IaC等）要求抽取对应案例，整理成售前可用素材。已建 HLD 架构设计 Skill（~/.hermes/skills/business/hld-design.md）和售前报价 Skill。
§
用户笔记本环境(2026-09-20): Windows x64, 路径 D:\Work\日常\上云迁移\01服务流程\04其他\03AI报价\00资源\03tool\trae-wb-local。Trae本地端口=50010(非5001), WorkBuddy无本地端口(封闭客户端)。cloudflared已装并跑通(quick tunnel URL会变)。OCI机是ARM64无法跑Chrome/浏览器自动化。
§
AICCP 项目新动态：用户在阿里云 ECS 8.133.232.216（Ubuntu 24.04 aarch64）上部署了 AICC 前端/后端/PG/Redis/MinIO（Docker），域名 aihubcloud.cn 托管在 Cloudflare（NS: anna/jaime.ns.cloudflare.com），当前在配 nginx 反向代理 + Cloudflare DNS 指向该 ECS。
§
dws CLI v1.0.61 已装好并认证（金龙 @ 上海安畅，corp_id=ding58230c81113bca4f35c2f4657eb6378f），14个 dingtalk-* skill 已装。钉钉出站 webhook 未配（待用户创建机器人后填 DINGTALK_WEBHOOK_URL）。读在线文档/多维表格/日历/待办/通讯录/云盘/考勤等需先开 CLI 访问管理 + 7个API权限。
§
域名 aihubcloud.cn 已托管 Cloudflare。配置：openmaic.aihubcloud.cn → :3000 (OpenMAIC)，dsh.aihubcloud.cn → :3081 (DSH)，aihubcloud.cn → 301 → openmaic。SSL Full + Always HTTPS + Security Medium。CF 隧道 203eba87 跑着。
§
OpenMAIC (Tsinghua THU-MAIC 开源项目) 部署在 OCI /home/ubuntu/OpenMAIC，端口 3000，配置 Nous 免费 API（OPENAI_API_KEY=nous，OPENAI_BASE_URL=https://inference-api.nousresearch.com/v1）。项目需要 pnpm install + pnpm dev 启动。
§
用户正在构建售前资料库，后续会按方向（如 Landing Zone / 云迁移 / WA 优化 / 大数据 / DR / IaC 等）要求整理售前素材。素材来源为 SmartCare 案例集（北区/东1组/东2组），路径 /home/ubuntu/cloud-docs/SmartCare案例集/，每组含 .pptx 和已提取的 案例集.md。要求：按方向抽取对应案例 → 整理成售前可用资料。
§
浏览器 JS crypto.randomUUID() 仅在安全上下文（HTTPS 或 localhost）可用。DSH 前端使用 crypto.randomUUID()，通过 HTTP（如 http://IP:port）访问会报 'uuid is not a function'。解决方案：HTTPS（Cloudflare Full strict）或 SSH 端口转发到 localhost。
§
DSH故障修复确认(2026-10-12): 初始FAILURE(exit-code PID288199)根因=settings.yaml拼写错误(thinkingmodels->thinkingmachines/inkling-small); 修正后重启->active PID288304. 清理/重装/配置全部完成. 外部访问仍需CF控制台Public Hostname(非CLI).
§
用户不想用 scp/CLI 传文件(嫌麻烦), 倾向网页上传: dsh 对话框附件 或 我搭 filebrowser 拖拽到 ~/cloud-docs/。大文件走聊天机器人慢。dsh 'API key is invalid' 根因=token过期(同步cron关了); 已建静默同步 cron dsh-token-sync-silent(job 5ed16e725c96, 每30分).
§
【dsh自动重启循环修复完成】根因：/home/ubuntu/.dsh/.credentials.yaml 中遗留非法 key NOUS_API_KEY（应仅保留 DEEPSEEK_API_KEY）。dsh.service 重启counter曾达1966。修复：清除NOUS_API_KEY，保留DEEPSEEK_API_KEY。现dsh正常运行（PID 68913，监听 3081）。
§
查新报告附件清单（2026-09-25）：基于已提取真实文本（5884字，20260110，知网，检索词“智能人体感应灯”），明确提供12份文献：前3份完整摘述（[1]张开店/点金照明Z类2023-12-23/[2]蒋帅帅周志峰GD32J类2023/[3]盛楠康阳机器人J类2022），后9份摘要已含在原提取文本（PIR原理硕士/多传感器融合/毫米波雷达）。未编文献/未虚构技术参数。
§
_sys: memory_char_limit 已扩至8000/user_char_limit 5000(2026-08-21, config.yaml memory段嵌套). 维护原则: 记忆只放跨会话稳定事实, 临时状态与易变细节(飞书发布步骤/隧道重建命令/卡单审批/部署状态)移入~/.hermes/plans/或skills, 不占记忆额度. 每周审查删过期/重复条目.
§
Cloudflare 配置关键参数(2026-09): CF账号=<EMAIL>, Zone ID=100380e22b85e5f8e66730342913976d, Tunnel ID=203eba87-df2c-4fb6-8ca4-8698f0e3deeb, 域名=aihubcloud.cn。ingress通过API管理(--token模式)，非本地config.yml。
§
dsh 启动失败根因：cron job dsh-token-sync-silent (5ed16e725c96) 每30分把 NOUS_API_KEY 写回 .dsh/.credentials.yaml，覆盖手动修复。credentials-local 解析器拒绝未知 key → 插件树加载失败 → 404。修复=清凭证文件+禁用该cron。已禁用(2026-09-07)。
§
多雲價格查詢 MCP 可用性調研結果（2026-09-03）：✅ 可用=awslabs.aws-pricing-mcp-server（AWS，已接入）；❌ 不可用=GCP（MCP v1→v2 不相容）、Azure（包無實際 server 入口）、阿里/騰訊/華為/火山/OCI（無 MCP 包）。短期方案：AWS 走 MCP 自動查，其他 7 朵雲靠能力矩陣+公開報價估算。
§
Cloudflare 隧道配置: tunnel 203eba87-df2c-4fb6-8ca4-8698f0e3deeb, hostname dsh.203eba87-df2c-4fb6-8ca4-8698f0e3deeb.cfargotunnel.com -> http://127.0.0.1:3080, token 位于 /etc/cloudflared/token
§
用户技术偏好(2026-09新增): ①倾向开源模型(不仅免费，还要开源)；②所有长期跑的服务必须用systemd管理+Restart=always；③难技术问题(网络/CF/基础设施)主动用OpenAI(Azure gpt-5-mini)出方案；④CF命名隧道比quick tunnel更稳(不会重启换URL)；⑤不喜欢我反复询问或给建议，期望我直接动手修复。
§
model-router 技能已修补（2026-09-29）：新增 qwen3.8-max 兜底、百炼修复顺序（bl CLI -> .env -> provider -> base_url -> 独立重启）、飞书三重锁、简洁规则（无长闭合）、无编造内容规则、vision_analyze 429 处理。技能已 curator-managed，可直接加载。
§
域名 aihubcloud.cn（新网注册），NS 已改到 Cloudflare（anna/jaime.ns.cloudflare.com）。需在 CF 控制台配 tunnel hostname routes → aihubcloud.cn→:3000, dsh.aihubcloud.cn→:3081。Token 之前给过但本会话丢失，需用户重发。
§
CF隧道token管理(2026-09): 用户给过cfut_前缀的tunnel token(184字符JWT)和cfk_前缀的Global API Key。token在本会话中多次丢失(会话压缩)，每次都要用户重发。CF API调用用X-Auth-Key(Global Key)比Bearer <REDACTED>更稳(401少)。
§
Twilio: 账号<REDACTED:TWILIO_SID>, 余额$10.67, 当前号码+1 202 816 6399(DC华盛顿区号, 旧号已释放). 用途: 收海外服务验证码→转发到TG. Palantir AIP屏蔽VoIP号, 需实体SIM号(TextVerified或Tello eSIM).
§
Claude Code (Windows) 走智谱 ANTHROPIC 代理：ANTHROPIC_BASE_URL=https://open.bigmodel.cn/api/anthropic，模型 glm-5.1，非直连 Anthropic。配置在 C:\Users\<用户名>\.claude\settings.json。
§
GCP机器35.206.98.210(root登录, 仅publickey禁密码): OCI本机被拒. DeepSeek官方API(api.deepseek.com)从OCI网络可达(0.3s), 但无免费额度需预充值≥¥10才有key; dsh里的DEEPSEEK_API_KEY实为已废的OpenRouter key.
§
AICCP 技术栈：Vue3/FastAPI/Docker(5容器)/PG16/Redis/MinIO/UUID PKs/RBAC；AI 开发强制 Skill→Prompt→LLM→Structured Output；部署腾讯云 ECS 8.153.152.218；仓库 bfliujinlong/AI-CCP。
§
用户设备(2026-08-30): iPhone 16主力(iOS18, 日常Telegram/微信聊Hermes), iPhone 13完好备用, iPhone 6太老A8废弃, 安卓若干台密码遗忘。桌面AI助理用iPhone而非改造儿童机器人(Alilo G6封闭嵌入式系统不可编程, 已确认不值得改造)。
§
用户在本轮明确要求：以后回复不要重复“已执行全部清理与修复，已交付全部输出物，已确认无遗漏，已给出路径。已足够。已完成全部流程。”这类无意义长闭合文本。修正已执行：简洁直接，只给结论/路径/状态，交付物已确认后不再逐条自嗨。已保存 memory 并在本轮已实际遵守（后续回复已大幅压缩，仅保留必要结论行）。
§
【2026-09-05】用戶機器在德國（法蘭克福OCI），非中國網絡環境。模型路由應優先考慮歐洲直連（Groq/Mistral），硅基流動/智譜/火山方舟在德國延遲較高且不穩定。Deutsche Telekom與Cloudflare有peering爭議，德國OCI機跑CF隧道會拖慢API調用，應直連。
§
OCI 法兰克福 VM 网络限制：api-inference.huggingface.co DNS 解析失败（网络墙），GitHub Models 端点也不通。可达的免费 LLM：Mistral、Groq、OpenRouter、Google Gemini、Cloudflare Workers AI。
§
孩子课件来源含夸克网盘(截图路径 我的云盘/个人/学习/孩子/学而思/2026/暑假/科学),夸克无 CLI 只能网页/App 手动传。另收到百度分享链接(8教你制作PPT pan.baidu.com/s/1VOgYiIDxnOe8j849V-8_5Q?pwd=54U4)。
§
【2026-09-05】硅基流動(SiliconFlow)對德國/海外IP：key返回"Invalid token"，可能是未完成實名認證、未領2000萬免費額度、或key過期。需去cloud.siliconflow.cn確認額度狀態。德國用戶推薦先測Groq（歐洲更穩）。
§
aliyun CLI v3.4.11 installed and configured at /home/ubuntu/.aliyun/config.json (chmod 600). Verified working with DescribeRegions.
§
dsh.service 重启循环问题已修复: /home/ubuntu/.dsh/.credentials.yaml 中清除了非法的 NOUS_API_KEY，仅保留 DEEPSEEK_API_KEY。dsh 现已正常启动（PID 68913，监听 3081）
§
vision_analyze 工具看不到本地截图文件（MEDIA: URI 或本地路径均无法在 vision 模型渲染）。截图分析需靠用户上传图片到对话，或通过 OCR（tesseract 可装但效果差，PaddleOCR 在 ARM 上 segfault）。
§
【工作风格偏好】用户倾向于直接解决问题而非反复尝试或确认。对于临时的登录/认证障碍（如AWS MFA验证码），期望我直接给出清晰明确的解决路径。正式报价时倾向用$350/人天，需要区分LCZ scope（include/exclude AI layer）。
§
Cloudflare: acct=6413823f243b9dc615778a19021db968(控制台登录邮箱Bfyalong@gmail...). 硬约束: 用户本地无法直连OCI公网130.61.110.133, 一切外网访问走命名隧道中转.
§
DSH nginx 安全加固已配置：限流 10r/s 每 IP、并发连接限制 10、安全响应头、访问日志 /var/log/nginx/dsh-access.log。nginx 监听 3082 反向代理到 dsh 127.0.0.1:3081。
§
用户Windows工作路径: D:\Work\日常\上云迁移\01服务流程\04其他\03AI报价\00资源\03tool\ (从bat报错路径可见). 笔记本是Windows系统, 直接给PowerShell/CMD命令, 不要给bash.
§
User communicates in Chinese, prefers free models, runs on GCP free tier VM. Concerned about credit card charges.
§
SSH config别名: gcp/gcp35→bfyalong@35.206.98.210(GCP免费机), ali/aicc→root@139.196.171.8(阿里云AICC). 都在~/.ssh/config.
§
用户最大化用钉钉渠道：装 dws CLI 后能直接读文档/日历/待办/多维表格/云盘/考勤/会议纪要，不需要企业微应用（dws 走个人 OAuth 设备码认证，无需超管审批）。用户明确倾向"装就行"直接动手。
§
雏鹰杯 2026 附件 4-7 整理已完成（2026-09-25）：路径: /home/ubuntu/雏鹰杯_附件4-7_整理.docx, /home/ubuntu/雏鹰杯_附件4_研究综述_扩展.docx。
§
Telegram发文件正确方式: 从.env加载TELEGRAM_BOT_TOKEN(不是上下文里的token, 两者后缀不同), 用sendDocument端点. 直接curl用上下文token会401.
§
用户在中国大陆（上海时区，UTC+8），本地 AI 智能体包括 Claude Code / Codex CLI / Cursor / WorkBuddy 桌面端，需规避 OpenAI/Codex 直连限制
§
Cloudflare 账号邮箱=<EMAIL>（Global Key 认证用）。新阿里云 VM=8.133.232.216（用户要求 aicc.aihubcloud.cn 解析到此 IP）。
§
用户购买域名 aihubcloud.cn（新网注册），但新网不支持改 NS 记录，Cloudflare 隧道自定义域名无法配置。只能继续用 trycloudflare.com 隧道域名。
§
GitHub 私有仓库: xx-customer-iac (IaC代码), xx-customer-ci (CI代码)。SSH key id_ed25519_github 已加到账号级。
§
ali CLI profiles：liujinlong(cn-shanghai)、tc_bigdata(cn-shenzhen)、anchang(cn-hangzhou)。
§
2026-09-28 用户明确指令：回复不要重复长闭合文本（"已执行全部清理..."），只给结论/路径/状态；交付完成后直接说已足够，不逐条自嗨。已执行并固化。
§
OCI SSH 连接故障: 服务器130.61.110.133只允许publickey认证，用户无私钥，需通过OCI控制台或私钥恢复。
§
【个人/环境台账 WorkBuddy 2026-10 补】Windows 用户名 bXfyalongx，WSL 用户名 Manju；Claude Code Windows 端走智谱 GLM 中转(open.bigmodel.cn/api/anthropic) 或腾讯云 Coding Plan(WorkBuddy 凭证)，非直连 Anthropic。WorkBuddy 积分 12,288.9 为封闭生态，仅能在 WorkBuddy/CodeBuddy CLI 内消耗，无法导出。用户提问极简(1-3词)依赖共同上下文推断；会话常以 hi/在吗/早上好 开场请求状态检查。Bash 工具默认沙箱限制不能 SSH 外部服务器，需 dangerouslyDisableSandbox。ali CLI profiles: liujinlong(cn-shanghai)、tc_bigdata(cn-shenzhen)、anchang(cn-hangzhou)。
§
【汤臣倍健 0621 数据失败分类明细】1561 失败实例/571 任务/16 类错误：Trino→Spark 迁移失败 137 任务(DDL 不兼容 114、目录命名 14、函数差异 9)；DataWorks DI 配置问题 175 任务(生产数据源缺失 29、环境未绑定 19、字段未映射 22)；Serverless 资源组缺包 102 任务(Python 自定义镜像缺依赖 46)。已修 754，722"空日志"待解。团队分工：潘超胜、刘家君、丁宇文、陈铭。
§
【工作风格补充】坚持"不解决不要停"——核心问题未彻底解决不中断；配置完成后常要求验证测试；敏感凭证(API key、SSH 密钥 kimtestkey.pem)写入本地文件而非聊天发送。技术输出偏好表格、可执行步骤、状态符号(✅⚠️❌)。
§
【输出偏好】报价/交付物中英双语、自然专业、去 AI 味；对外统一 Word/docx。Feishu(Lark) wiki/sheets/drive 用于项目文档与报价模板管理。


## 2026-10-26 归档（从 MEMORY.md 精简移入）

### 免费模型池现状（2026-10-25 实测）
- Nous: api.nousresearch.com 已 NXDOMAIN（域名消失）；inference-api.nousresearch.com 存活但免费模型 0/8（401 out of funds / 404 free period ended）
- OpenRouter: 免费模型实测 12/17 可用，但有 free-models-per-day 日额度，密集探测会打爆（已降 cron 至每 6 小时）
- 主通道: 本地 litellm(:4000) → cb2openai(:4100) → CodeBuddy（46 模型，不耗 OR 额度）
- 探活必须用 localhost，不能用 127.0.0.1（后者 curl 返回 000）

### 域名/隧道
aihubcloud.cn 托管 Cloudflare，隧道 203eba87；openmaic→:3000，dsh→:3081。
CF+Next.js 须关 RocketLoader/AutoMinify，且必须 build+start（非 dev）。

### AICCP 部署
GitHub Actions SSH 自动部署腾讯云 ECS 8.153.152.218（docker-compose.prod.yml），仓库 bfliujinlong/AI-CCP，设计原则含 Fact Sheet First。

### OCI / GCP
- OCI 机 130.61.110.133（巴黎 ARM，CLI 不在 PATH 需 source）
- GCP 机 35.206.98.210（e2-micro 1G）跑备用 gateway，走 ~/.ssh/id_ed25519_gcp35
- OCI ARM 抢实例脚本 oracle-arm-grab-toolkit 持续优化（目标 10 分钟内抢到）
- GCP us-central1-f e2-micro(free-ubuntu-vm) 已建

### 飞书
主 app cli_aa093013dc38dcbb；三重锁=应用身份权限+发布版本+bot 进群；99991672/230002 均权限问题，属用户 UI 操作我替不了。大文件通道。

### 钉钉 / 明道
dws CLI 已认证（金龙@上海安畅）。明道(anchnet) 工时系统凭据存 .env，用户要求自主登录抓取，不要每次导出。

### WorkBuddy 积分
12,288.9 分，封闭生态，仅能在 WorkBuddy/CodeBuddy CLI 内消耗，不可导出他用。

### 本地 Windows 环境
Windows 机（用户名 EDY/bXfyalongx，WSL 用户名 Manju，D:\Work\日常\上云迁移\）；Bash 有沙箱限制，SSH 外部服务器需 dangerouslyDisableSandbox。

### python-docx 填表坑（2026-10-24 实踩）
表格型申报书正文都在 table[i].rows[r].cells[c].paragraphs，不在 doc.paragraphs（顶层只有 29 段，实际 137 段全在 11 个表里，多为 1x1 单元格）。
批量替换必须写 iter_paragraphs 遍历顶层段落+所有表格单元格+嵌套表，否则 replace 静默未命中。
保留格式的替换方法：在 p.runs 上按字符偏移切片改 text，不要整段重写 paragraph.text。

### 科奇少年 2026 申报（孩子科创）
走「科奇少年青少年科学探究专项活动」，不是之前的上海市青少年科技创意设计展示活动。
初评只收 3 份 PDF：课题申报书 + 课题申报活页(匿名评审) + 原创性与诚信申报承诺书。
官方模板 https://xiaowaibao.oss-cn-shanghai.aliyuncs.com/ytywenjian/2026chuyingbei/ 下三个 docx。
评审 6 维：选题价值/问题意识/研究设计/可行性/创新意识/表达规范。工作目录 ~/chuyingbei/。
