User communicates in Chinese, prefers free models, runs on GCP free tier VM. Concerned about credit card charges.

---

User runs an OPC at an MSP: end-to-end cloud-migration for clients (Ali/Huawei/OCI) — pre-sales/商务 to delivery(迁移/LZ/运维). Self-identifies as Forward Deployed Engineer (FDE). Deploys Hermes as the productivity engine; wants to maximize OCI Always-Free for AI + solo efficiency. Frame all help toward this end-to-end OPC+FDE operating model.

---

Azure OpenAI: 资源liujl-9958-resource, 端点https://liujl-9958-resource.openai.azure.com/, 区域westus3, 部署gpt-5-mini. 由Azure Sponsorships $5000额度支撑; ⚠️耗尽后自动转PAYG按量扣绑定信用卡(不自动停), 用户极度担心超额. 硬规则: 我只用ReadOnly SP监控+超阈值强告警, 绝不自动停资源/绝不给全量AK; 用户在Azure门户自设Budget+ActionGroup+runbook硬停. 用途: [难]任务delegate gpt-5-mini; 不进自动路由链(显式说才用).

---

②传"reasoning_effort":"low"仍无效——本部署(gpt-5-mini @ liujl-9958)无论直连(api-version=2025-04-01-preview)还是经cc2azure代理, 均把全部max_completion_tokens烧进reasoning(reasoning_tokens=1400/3000实测), content恒为空(2026-08-24三次直连+一次代理全空). 结论: 该部署特性, 不可靠产出正文; 难任务delegate若要可见输出须换思路(放宽max_completion_tokens到极大或改他模型), 勿依赖它返正文.

---

用户硬性要求: 陈述技术事实(尤其OCI免费额度/计费规则/服务上限等)必须先查官方文档核实, 不可凭记忆乱说. 实例: 我曾称'1个Always Free实例'被纠正, 官方写'two compute instances'+Ampere A1共4 OCPU/24GB. 此原则适用于一切技术参数断言.

---

用户想要类似豆包的语音对话, 已落地Telegram通道(ffmpeg+voice.auto_tts:true, nous托管TTS/STT零额外key). 微信无原生语音, 语音交互一律走Telegram.

---

模型路由(2026-08-24扩展固化进SOUL.md): 主tencent/hy3:free(Nous), fallback 15个= nous池5(hy3主+solar-pro4+poolside-laguna-s+stepfun-flash+meituan-longcat) + OpenRouter池10(nemotron-3-nano-30b-a3b/nemotron-3.5-lightning/nemotron-nano-12b-vl/nemotron-nano-9b/north-mini-code/laguna-xs-2.1/dots-3-note/lfm-2.5/omni-30b-reasoning/inkling). 看门狗free_model_watchdog.sh每5分双端点探测(2026-08-24用户要求停, 脚本仍在); daily_free_model_research.sh每日外网调研新免费模型(cron de34307286a0). 已剔除: glm-5.2(404/OR限流), gemma-4×2(429), inkling-small(403), content-safety(非对话). voice.auto_tts=false. 难任务delegate azure gpt-5-mini.

---

简历当前定稿(2026-08-24):中英文版在 ~/personal/resume/,AI 部分用 Azure OpenAI (GPT-5) 基调(非 Hermes/OCI),黑灰配色无蓝去AI感,3页完整。docx 中文微软雅黑/英文Arial(用户本地所见);PDF 用 Noto CJK+DejaVu 等价替身(本机无版权字体)。源=历史docx(Jinlong Liu Resume 2026.docx / 刘金龙简历 2026 更新版.docx)。

---

cron job 模型独立于全局router: Hermes的cron任务各自在~/.hermes/cron/jobs.json写死model/provider字段, 不继承config.yaml全局model. 旧job全写z-ai/glm-5.2:free@openrouter(已废弃限流), 致Feishu Status Check连败17次. 修复:`cronjob update`不接受model参数(报No updates), 须直接改jobs.json的model/provider/base_url并加fallback_providers, 改完即生效无需重启. 2026-08-24已批量把9个agent型job改hy3@nous+4 fallback.

---

note.txt在/home/note.txt: 含Azure OpenAI端点(liujl-9958-resource.openai.azure.com) + 两把84字符key(AZ1给cc2azure代理 / AZ2给Cursor直连). Claude Code配置~/.claude/settings.json(ANTHROPIC_BASE_URL=:4000走cc2azure)、Cursor配置~/.cursor/settings.json(free_poll轮询nous 5模型 + openai_fallback直连Azure gpt-5-mini). 两工具默认免费轮询、自选OpenAI兜底. cc已装/usr/bin/claude v2.1.238.

---

新skill free-model-guard(~/skills/free-model-guard): 抗限流免费router+看门狗+难任务delegate完整方案, 含scripts/free_model_watchdog.sh(双端点探测重排)、daily_free_model_research.sh(每日外网调研)、azure_spend_guard.sh(Azure本地账本告警, 阈值$50 Telegram告警). 换机器一键复现见SKILL.md.

---

OpenRouter免费模型实测(2026-08-24): 可用=nemotron-3-nano-30b-a3b(AA Intel14.5强推)、nemotron-3.5-lightning(1M)、nemotron-nano-12b-vl(多模态)、nemotron-nano-9b、north-mini-code、laguna-xs-2.1、dots-3-note(512K)、lfm-2.5、omni-30b-reasoning、inkling; 不可用=glm-5.2(404/Decart池)、gemma-4×2(429)、inkling-small(403)、content-safety(非对话). 注意OR免费层偶发整层限流(当日15个全429/404), 故轮询主用nous池.

---

切换 Hermes 默认模型时必须同步所有 cron job：cron job 各自在 ~/.hermes/cron/jobs.json 写死 model/provider，不继承 config.yaml 全局默认；且 `hermes cron update <id> --model X` 静默不改 model 字段(实测)。正确做法=python 直接改 jobs.json 里每个 job 的 model/provider/base_url 并加 fallback_providers，否则老 job 继续撞废弃模型连败(曾 Feishu Status Check 连败17次)。另：改 config 后需本机 systemctl --user restart hermes-gateway.service 让新进程生效(terminal在gateway树内不能自重启被护栏拦)。

---

OpenRouter 免费层可整体宕机：实测某时刻 15 个 OR 免费模型全部 429/404，nous 池 5 个仍全活。免费模型轮询配置应以 nous 池为主、OR 池为辅，不要反过来。OCI 费用核查用 /home/ubuntu/oci-monitor/venv/bin/oci (不在默认PATH,需source venv + export OCI_CONFIG_DIR=/home/ubuntu/.oci)，已写进 ~/.bashrc 新 shell 可直接用。

---

Azure gpt-5-mini 花费告警用本地账本方案：FOUNDRY key 是资源级，读不到订阅级 consumption API(401)。脚本 ~/.hermes/scripts/azure_spend_guard.sh 用本地 JSON 账本自记每次 gpt-5-mini 估算 cost，超阈值($50)发 Telegram。delegate 后需手动 `azure_spend_guard.sh record <reasoning_tokens>` 记账(或固化进 model-router 流程自动记)。

---

本机资源画像(2026-08-25实测): 架构aarch64(ARM), 2核CPU, 无GPU, 内存11G(可用9.8G), 无ollama(本就未装也未用). 当前Hermes模型=tencent/hy3:free via nous云端API; Azure gpt-5-mini也走云端API; cc/codex走本地litellm网关(:4100免费轮询). 结论: 本地ARM小机不适合跑模型权重(纯CPU推理慢且抢资源), 正确架构=云端免费API(nous/hy3, OpenRouter免费层, Azure Sponsorships gpt-5-mini)做推理, 本地只做路由/编排/中转. 用户曾误以为本机用Ollama——实际从未使用.

---

投标/技术标文档生产工作流(用户反复用): 1)收招标文件+公司SOW+客户托管SOW; 2)出审查报告(售前顾问视角,按P0占位符/重复/P1演示价值/P2差异化分级); 3)按P0→P1→P2改或重建; 4)matplotlib画黑灰图(拓扑/流程/门控/甘特/决策树,无蓝无网格线)内嵌; 5)python-docx组装(宋体/微软雅黑,Table Grid); 6)发Telegram。Azure gpt-5-mini delegate写长文常挂起(第4章曾252s无响应),主模型hy3直接写更稳。

---

用户正积极制作泉峰集团 AWS→阿里云迁移技术投标文件（投标方=阿里云MSP安畅网络科技），技术标8项结构（封面+附件1-8）。审查/撰写投标章节时用 Azure gpt-5-mini（openai）委托做技术审查；产出要求无AI感（黑灰/无蓝/无'AI'字眼/自然实务文风，且用户明确'格式不要AI感觉那么强'）。

---

已按用户要求将 Hermes 技能软链同步到 Claude Code（~/.claude/skills）与 Codex（~/.codex/skills），单一真源 ~/.hermes/skills，Hermes 改 skill 自动同步（2026-08-27 完成，79个分类skill+顶层自有skill如 fde-deployment/free-model-guard/solution-delivery/spreadsheet-delivery）。

---

全通道限流根因已修：原全局 model.default = nvidia/nemotron-3-super-120b-a12b:free (OpenRouter免费层) 不稳，导致飞书/钉钉/微信/cron全撞 HTTP 429 free-models-per-day。已用 `hermes config set model.default tencent/hy3:free` + `model.provider nous` 改为 hy3@nous（保留原15个fallback池），改后需 systemctl --user restart hermes-gateway.service 生效。结论：nemotron-3-super-120b-a12b:free 不宜作默认，hy3@nous最稳。改config必须用 hermes config set（直接patch yaml被护栏拒）。

---

OCI 全局每日播报已建成: 脚本 ~/oci-monitor/daily_global_report.sh (复制至 ~/.hermes/scripts/), cron任务 905b3955de1a 每天9:00 deliver=all no_agent=true 跑此脚本。播报5维度: 费用明细(按计费日)+昨日资源运行+在跑服务+模型运行+Azure OpenAI用量。同时修复了每小时$0.0344刷屏告警(oci-billing-check.sh加≤$0.05遗账白名单)。飞书/微信投递常失败(230002/iLink限流), Telegram/钉钉/短信/邮件能到。

---

用户要求硬技术/架构/基础设施排障用 OpenAI(gpt-5-mini via Azure) 出权威方案: 本轮 dsh 外部访问卡死, 用户明确'请使用 openai 给我权威的解决方案', 我 delegate gpt-5-mini 实测环境给方案. 与既有'难任务delegate gpt-5-mini'规则一致, 但用户强调'权威解决方案'场景(网络/隧道/CF/基础设施)主动用 OpenAI 而非只靠免费模型盲试.

---

用户需要域名但要求'免费'且零费用红线禁止绑信用卡自动扣费。GoDaddy 无免费域名(最便宜$0.99首年且强制绑卡续费),已告知用户改走真正免绑卡免费域名:.pp.ua / .us.kg / is-a.dev / eu.org(审核) / DuckDNS / Cloudflare子域。最实用:注册免费域名→托管Cloudflare→给cloudflared隧道加Public Hostname路由打通dsh公网(解决dsh隧道路由数=0无公网URL死结)。Freenom已关停勿用。

---

dsh外部访问死局(2026-08-29实测, OpenAI gpt-5-mini诊断确认): DuckDNS/任何'只给A记录'的免费DNS【不能】走Cloudflare命名隧道。CF隧道Public Hostname要求域名zone加入CF账号(Full改NS/Partial加TXT-CNAME校验), DuckDNS只允许改子域A记录→无法校验→CF边缘无证书无路由→TLS unrecognized_name(alert 624)断开→外网HTTP 000。铁证: curl -k https://vkim.duckdns.org→000, 而*.trycloudflare.com→200, 命名隧道日志duckdns出现0次。填CF anycast IP(162.159.137.85)也无效。正确路径: 注册能改NS到CF的域名(eu.org免费/<$10普通域名)→CF Add Site→改NS→Zero Trust→Tunnels→dshnew(203eba87)→Add Public Hostname: dsh.域名.com→http://localhost:3080。quick tunnel临时URL(trycloudflare.com)能通但重启变URL。dsh.service的--trusted-host必须写精确域名、不接受*.通配, 否则/api报403。

---

iOS 语音助理方案(已部署 2026-08-30): iPhone 16(iOS18)喊Siri→快捷指令听写→打OCI中继 /relay/ask?q= →朗读回复。中继=/home/ubuntu/oci-monitor/tg_relay.py(fastapi:8099, systemd tg-relay.service)+nginx 3080加/relay location+CF quick tunnel healing-organic-retro-metres.trycloudflare.com暴露。模型用OpenRouter免费 nvidia/nemotron-3.5-lightning:free(因Nous免费API裸调报missing tags, OR免费层无此限)。Telegram直连方案废弃(国内api.telegram.org被墙+快捷指令不走代理)。iOS18无'添加到Siri'入口, 靠'在搜索中显示'+喊指令名或主屏图标触发。

---

WorkBuddy/百炼标书决策(2026-08-30): 不装WorkBuddy(闭源商业+需百炼智能付费API+违反零费用+数据出境风险)。标书四步能力(招标解读→目录生成→内容生成→合规审查)用Hermes现有skill(tender-docx-assembly/presales-architect/solution-delivery)+本地免费模型复刻, 素材在~/cloud-docs不外传。

---

钉钉/全通道限流根因(2026-08-31修复): 原全局 model.default = nvidia/nemotron-3-super-120b-a12b:free (OpenRouter免费层) 不稳导致飞书/钉钉/微信/cron全撞HTTP 429。已用 hermes config set model.default tencent/hy3:free + model.provider nous 改为 hy3@nous 根治。改后需 systemctl --user restart hermes-gateway.service 生效。结论:nemotron-3-super-120b-a12b:free 不宜作默认,hy3@nous最稳。改config必须用 hermes config set(直接patch yaml被护栏拒)。

---

钉钉机器人('小钉 kim') 2026-08-31 14:13报错'⚠️ The model provider failed after retries'——根因: 当前model.default=tencent/hy3:free经Nous调用,但Nou端hy3免费期已结束(返回404 'This model's free period has ended')。修复: hermes config set model.default nvidia/nemotron-3.5-lightning:free(OpenRouter免费层),重启网关。网关重启后自动拉起(进程2193585),钉钉重连成功。记忆更新: 全局默认模型已切到OpenRouter免费层(nemotron-3.5-lightning:free),hy3@nous(旧值)已弃用。

---

钉钉/全通道限流根因(2026-08-31): 原全局 model.default = nvidia/nemotron-3-super-120b-a12b:free (OpenRouter免费层) 不稳，导致飞书/钉钉/微信/cron全撞HTTP 429。修复: hermes config set model.default nvidia/nemotron-3.5-lightning:free + model.provider nous 改为 OpenRouter免费层。改后需 systemctl --user restart hermes-gateway.service 生效。结论: nemotron-3-super-120b-a12b:free 不宜作默认，改config必须用 hermes config set(直接patch yaml被护栏拒)。

---

钉钉机器人报错(2026-08-31): 小钉 kim 报'⚠️ The model provider failed after retries'——根因是 model.default=tencent/hy3:free 经 Nous 调用，但 Nous 端 hy3 免费期已结束（返回404 'This model's free period has ended'）。修复: hermes config set model.default nvidia/nemotron-3.5-lightning:free（OpenRouter免费层），重启网关后钉钉重连成功。当前全局默认模型已切到 OpenRouter 免费层。

---

模型路由配置现状(2026-08-31): model.default=nvidia/nemotron-3.5-lightning:free, provider=nous, base_url=https://inference-api.nousresearch.com/v1, fallback_providers含5个nous+9个openrouter模型。注意:nous端hy3已过期(404),所以默认走nous的nemotron-3.5-lightning实际仍走nous端点。理想应设provider=openrouter让默认走OpenRouter。但gateway重启后钉钉实测正常(14:19:31 response ready, 142 chars, 0.8s)。

---

dsh.service 重启循环问题已修复: /home/ubuntu/.dsh/.credentials.yaml 中清除了非法的 NOUS_API_KEY，仅保留 DEEPSEEK_API_KEY。dsh 现已正常启动（PID 68913，监听 3081）

---

User is an FDE (Forward Deployed Engineer) / OPC (One Person Company) in cloud migration consulting. Maintains ~80 Hermes skills covering 售前/商务/PM/SRE/运维. Works on GCP free tier VM. Uses Hermes Agent as AI assistant. Prefers concise, no-nonsense Chinese communication. Has multiple channels: Telegram, Dingtalk, Feishu, WeChat, email. Runs free-model routing with hourly health checks via cron job 'hourly-model-guard'. Concerned about API key security — rotates keys when exposed.

---

Critical technical state (2026-08-31 late): dsh.service had restart loop (counter 1963→1966) due to illegal 'NOUS_API_KEY' in /home/ubuntu/.dsh/.credentials.yaml. Fixed by removing NOUS_API_KEY, keeping only DEEPSEEK_API_KEY. dsh now running (PID 68913, port 3081). Cloudflare tunnel: 203eba87-df2c-4fb6-8ca4-8698f0e3deeb, hostname dsh.203eba87-df2c-4fb6-8ca4-8698f0e3deeb.cfargotunnel.com → http://127.0.0.1:3080. vision_analyze broken due to expired OpenAI key in config; config.yaml updated to use OpenRouter google/gemma-4-31b-it:free but gateway NOT restarted yet — needs manual restart.

---

【dsh自动重启循环修复完成】根因：/home/ubuntu/.dsh/.credentials.yaml 中遗留非法 key NOUS_API_KEY（应仅保留 DEEPSEEK_API_KEY）。dsh.service 重启counter曾达1966。修复：清除NOUS_API_KEY，保留DEEPSEEK_API_KEY。现dsh正常运行（PID 68913，监听 3081）。

---

多雲價格查詢 MCP 可用性調研結果（2026-09-03）：✅ 可用=awslabs.aws-pricing-mcp-server（AWS，已接入）；❌ 不可用=GCP（MCP v1→v2 不相容）、Azure（包無實際 server 入口）、阿里/騰訊/華為/火山/OCI（無 MCP 包）。短期方案：AWS 走 MCP 自動查，其他 7 朵雲靠能力矩陣+公開報價估算。

---

Nous 免费池状态(2026-09-05实测): hy3:free=404(免费期结束) / longcat-2.0:free=✅存活(当前主模型). 全局默认=model.default=meituan/longcat-2.0:free, provider=nous, base_url=https://inference-api.nousresearch.com/v1. 注:Nous免费层裸REST调chat/completions报missing tags,须走litellm网关或Hermes OAuth.

---

【2026-09-04故障记录+修复】三渠道(微信/飞书/钉钉)同时报错 "rate-limiting" + "failed after retries"。根因链: ①config 写死已剔除模型 z-ai/glm-5.2:free + OR minimax 全下架 → 429/404; ②改 hy3@nous 后 Nous 免费池全面退场 → 404。最终改 default=meituan/longcat-2.0:free (Nous) + 3个OR 兜底才稳住。教训: Nous 免费池不可靠，longcat 是目前唯一确认活的 Nous 免费模型。

---

教训: 被问"你是什么模型/版本"时, 不要凭记忆猜(我曾错答 solar-pro4 / hy3), 应先看会话顶部注入的 "Model: / Provider: " 元数据再回答。当前真实模型=meituan/longcat-2.0:free via nous。

---

【2026-09-05 紧急】config.yaml 会莫名被还原：本次会话中两次出现 default 从 longcat 变回 hy3:free 的情况，原因未查明（可能是 gateway 重启时某进程覆写、或 hermes config set 在 gateway 进程内被拦截后回滚）。修法：每次重启网关前必须 grep 确认 config.yaml 的 model.default 是 meituan/longcat-2.0:free，若非则立即 hermes config set 再重启。

---

【2026-09-05 备份系统审计结果】①sync-memory-github.sh / sync-skills-github.sh 最近成功是8月30，9月3日未跑或失败，本地有65个文件未推送。②restore-hermes.sh 路径假设错误（指向 ~/.hermes/deploy/ 但那是 dsh-src 源码，不是配置备份），clone 后 config.yaml 仍是8月30旧版。③cron jobs.json 里9个任务仍有7个写死 hy3:free@nous（已失效），重开机会继续撞 404。需修：jobs.json 批量改 longcat + 恢复脚本重写 + 手动推一次 GitHub。

---

【2026-09-04:model-router技能需adopt后修补】当前 model-router SKILL.md 写死 `tencent/hy3:free` 为主模型，但 Nous 免费池全面退场后它已 404。需要 `hermes curator adopt model-router` 后把主模型改为 `meituan/longcat-2.0:free`，并加 pitfall：「config.yaml 被还原为旧值会导致渠道全面报 rate-limiting，每次重启渠道报错先 grep config.yaml 确认 default，再看 gateway 日志实际在用什么模型」。

---

模型路由(2026-09-05): 全局默认=meituan/longcat-2.0:free@nous. Nous免费池仅longcat存活(hy3/solar-pro4/laguna-s-2.1/stepfun-3.7-flash均404). 用户要求"切hy3"会失败,需告知已死.

---

【2026-09-05】用戶機器在德國（法蘭克福OCI），非中國網絡環境。模型路由應優先考慮歐洲直連（Groq/Mistral），硅基流動/智譜/火山方舟在德國延遲較高且不穩定。Deutsche Telekom與Cloudflare有peering爭議，德國OCI機跑CF隧道會拖慢API調用，應直連。

---

【2026-09-05 実測】Nous 免費池完全退場：tencent/hy3:free / upstage/solar-pro4:free / poolside/laguna-s-2.1:free / stepfun/step-3.7-flash:free 全部返回 404 "free period has ended"。僅 meituan/longcat-2.0:free 仍存活（本機當前正在使用）。MobaXterm 成功連入 OCI 機器（130.61.110.133，上次登錄 2026-09-05 06:10 UTC）後可用 SSH 查詢 OCI 帳單/資源。後續模型層宕機復現風險高，需確保 config.yaml 中 default + 所有 cron job 均指向已確認存活模型，並建議增加健康檢查以免某天未手動改就再次全通道宕機。

---

Cloudflare Workers AI verified working (Account ID: 6413823f243b9dc615778a19021db968, 9 models incl @cf/meta/llama-3.1-8b-instruct, @cf/mistralai/mistral-small-3.1-24b-instruct). Mistral AI verified working (key VfOSv...WRyiE, 16 models incl ministral-8b-2512, codestral-latest). Multi-model Cloudflare Worker proxy deployed at https://bfyalong.bfyalong.workers.dev routing /workers-ai/*, /mistral/*, /openrouter/*, /dsh/*.

---

User has verified API keys: Cloudflare Workers AI (Account 6413823f243b9dc615778a19021db968, token [CF_TOKEN_REDACTED]...), Mistral AI ([MISTRAL_KEY_REDACTED]), Anthropic Claude (sk-ant-api03-6Wo...), Azure OpenAI (liujl-9958-resource, keys [AZURE_KEY1_REDACTED] and [AZURE_KEY2_REDACTED]). Also has Cloudflare Global Key [CF_GLOBAL_KEY_REDACTED] (useless for Workers AI/Tunnels).

---

dsh-token-sync-silent cron (job 5ed16e725c96) 已禁用(2026-09-07)。该 job 每30分跑 sync-nous-token.sh，会把 NOUS_API_KEY 写回 .credentials.yaml，导致 dsh 启动崩溃(unknown top-level key)。credentials.yaml 只允许 version:1 + refs: + DEEPSEEK_API_KEY。dsh 用 OpenRouter 免费模型(nemotron-3.5-lightning:free)，settings.yaml 设 baseURL=https://openrouter.ai/api/v1。

---

dsh 启动失败根因：cron job dsh-token-sync-silent (5ed16e725c96) 每30分把 NOUS_API_KEY 写回 .dsh/.credentials.yaml，覆盖手动修复。credentials-local 解析器拒绝未知 key → 插件树加载失败 → 404。修复=清凭证文件+禁用该cron。已禁用(2026-09-07)。

---

Nous 免费池仅 2 个模型可用: meituan/longcat-2.0:free (128K) / poolside/laguna-xs-2.1:free (32K). 其他 5 个 (dots-studio/nemotron-*/liquid/cohere) 在 Nous 端返回 404. 之前这些模型走 OpenRouter, 但 key (sk-or-...) 已过期(401).

---

dsh (DeepSeek Harness) 配置: provider route "deepseek-official" 指向 Nous (https://inference-api.nousresearch.com/v1), 非 DeepSeek 官方. systemd 环境变量 DEEPSEEK_API_KEY 实际存 Nous OAuth token. nginx 必须设 "proxy_set_header Origin \"\"" 否则 dsh API 返回 forbidden.

---

dsh (DeepSeek Harness) 配置前必须实测 Nous 免费模型可用性。Nous 已下架所有之前可用的免费模型(dots-studio/nemotron-3.5/nemotron-nano-9b/nemotron-nano-12b-vl/liquid/lfm-2.5/cohere-north-mini 全 404)。目前仅 meituan/longcat-2.0:free 和 poolside/laguna-xs-2.1:free 确认存活。Azure OpenAI gpt-5-mini 不兼容 dsh(要求 max_completion_tokens 参数和 api-key header，dsh deepseek adapter 不支持)。

---

难任务用 Azure OpenAI 规则(2026-09-08 固化):
- 触发: 用户说「使用openai」/「难任务」/ 明确要求 Azure
- 端点: https://liujl-9958-resource.openai.azure.com
- 部署: gpt-5-mini
- api-version: 2025-04-01-preview
- 鉴权: api-key header (key 在 .env 的 AZURE_OPENAI_KEY)
- ⚠️ 参数必须用 max_completion_tokens (不是 max_tokens)
- ⚠️ temperature 只支持默认值 1
- ⚠️ 该部署会把大量 token 烧在 reasoning 上
- OpenAI 直连 key 已废 (401), 不要再用

---

Azure OpenAI 调用规范 (2026-09-08 实测):
- key 变量名是 AZURE_FOUNDRY_API_KEY (不是 AZURE_OPENAI_KEY)
- 参数必须用 max_completion_tokens (max_tokens 报 400)
- temperature 只支持默认值 1 (传 0.3 报 429)
- api-version=2025-04-01-preview
- OpenAI 直连 key 已废 (401), 不要再试

---

Azure OpenAI 关键坑 (2026-09-08):
- .env 中变量名是 AZURE_FOUNDRY_API_KEY (不是 AZURE_OPENAI_KEY)
- 参数必须用 max_completion_tokens (max_tokens 报 400)
- temperature 只能默认 1 (传其他值报 429)
- OpenAI 直连 key 已废 (401)

---

难任务用 Azure OpenAI 偏好 (2026-09-08):
- 触发: 用户说「使用openai」/「难任务」/「快速给我」/ 明确要求 Azure
- 端点: https://liujl-9958-resource.openai.azure.com
- 部署: gpt-5-mini
- api-version: 2025-04-01-preview
- 鉴权: api-key header (key 在 .env 的 AZURE_FOUNDRY_API_KEY)
- ⚠️ 参数必须用 max_completion_tokens (不是 max_tokens)
- ⚠️ temperature 只支持默认值 1 (不能传 0.3)
- ⚠️ 该部署会把大量 token 烧在 reasoning 上 (实测 reasoning_tokens=2176/6189)
- OpenAI 直连 key 已废 (401), 不要再试

---

presales-architect 验证补充(2026-09-08): Expr Logistics 报价单按 Fintech 模板 1:1 还原成功(CN/EN 3-4 sheets, 公式到位)。Azure gpt-5-mini 调用已验证可用(端点+key+max_completion_tokens+temperature=1)。架构图用 PIL 深灰 PNG 无依赖。去 AI 感规则：禁蓝/禁AI字眼/天然段落/无机械格式。用户要求"完全依赖模板"时直接复制表头结构+替换数据，不重新设计格式。

---

OpenMAIC (Tsinghua THU-MAIC 开源项目) 部署在 OCI /home/ubuntu/OpenMAIC，端口 3000，配置 Nous 免费 API（OPENAI_API_KEY=nous，OPENAI_BASE_URL=https://inference-api.nousresearch.com/v1）。项目需要 pnpm install + pnpm dev 启动。

---

OpenMAIC (OCI 130.61.110.133:3000): Next.js app, switched from Nous free pool (dead) to Mistral API (ministral-8b-2512). Nous free pool fully retired (hy3/solar-pro4/longcat all 404/401). Use `pnpm build` + `pnpm start` (production mode), not dev mode (WebSocket HMR fails over HTTP). iptables was blocking port 3000, fixed with iptables rule. Microphone/TTS grayed out - need HTTPS for getUserMedia; user plans to register domain + use Cloudflare tunnel to solve.

---

【2026-09-12 会话摘要】用户正在准备 Amazon FDE 角色，系统学习 AWS Agentic AI 体系和生命科学行业方案。本日工作：

1. 导入 4 个 FDE GitHub 项目（fdeops/fdestack/openfde/fde-guide）→ 创建统一 skill fde-toolkit
2. 整理 AWS 零信任/SASE 开源项目全景 → cloud-docs
3. 整理 AWS Life Sciences 临床 trials 案例集（6家药企）→ cloud-docs
4. 创建 AWS Agentic AI FDE 速查手册 → cloud-docs
5. 创建 Amazon FDE 课程体系脑图 → cloud-docs
6. 制作 Lilly RWD Insights Agent PPT（8页，137KB）→ /home/ubuntu/Lilly_RWD_Insights_Agent_AWS.pptx

技术环境发现：
- Azure OpenAI (liujl-9958-resource) 所有模型返回空 content（100% token 烧 reasoning，该订阅共性问题）
- Nous Free Pool 完全退出（hy3:free 404）
- Hugging Face API 在 OCI 法兰克福不可达
- Mistral API 是目前唯一可用免费后端（ministral-8b-2512）

待办：
- 用户需注册域名 → Cloudflare 隧道 → OpenMAIC HTTPS 公网访问
- 用户需拿 Groq API key（被墙，需 VPN）
- 用户需创建 Azure gpt-4o-mini 部署（当前只有 gpt-5-mini/4o-1/35-turbo，全返回空）

---

Azure OpenAI (liujl-9958-resource, sub 6e0359de): 所有模型部署（gpt-5-mini/gpt-4o-1/gpt-35-turbo）全部返回空 content，根因=token 100% 烧在 reasoning_tokens 上。新端点 services.ai.azure.com/openai/v1 + gpt-4o 也空。唯一解：请求时显式传 reasoning_effort:"none"（仅 Chat Completions API + max_completion_tokens 参数生效）。建议用户用 Mistral 或 gpt-4o + reasoning_effort:"none"。

---

OCI 法兰克福 VM 网络限制：api-inference.huggingface.co DNS 解析失败（网络墙），GitHub Models 端点也不通。可达的免费 LLM：Mistral、Groq、OpenRouter、Google Gemini、Cloudflare Workers AI。

---

Azure OpenAI liujl-9958-resource (westus3): gpt-5-mini/gpt-4o-1/gpt-35-turbo 全返回空 content（reasoning 烧满 token），不可用于对话。仅 text-embedding-3-large 正常。勿再试。

---

LiteLLM 多模型路由器已部署在 port 4200（4100 旧实例仍跑），OpenRouter key 已配。8 个免费模型健康：nemotron-3-ultra-550b/nemotron-3-super-120b/north-mini-code/laguna-s-2.1/laguna-xs-2.1/ling-3.0-flash-fin。配置在 /home/ubuntu/.litellm/config.yaml。

---

Nous 免费池永久退场（7月12日起 TCP dead），OpenRouter 免费池是当前主力免费来源，但模型列表每周变化需定期扫描。

---

用户技术偏好(2026-09新增): ①倾向开源模型(不仅免费，还要开源)；②所有长期跑的服务必须用systemd管理+Restart=always；③难技术问题(网络/CF/基础设施)主动用OpenAI(Azure gpt-5-mini)出方案；④CF命名隧道比quick tunnel更稳(不会重启换URL)；⑤不喜欢我反复询问或给建议，期望我直接动手修复。

---

OpenMAIC TTS/语音修复(2026-09): 服务端用Fish Audio via OpenRouter(fish-audio/s2.1-pro-free:free)，需在tts-providers.ts请求体加response_format:'mp3'；浏览器端用Web Speech API(TTS_BROWSER_NATIVE_ENABLED=true/ASR_BROWSER_NATIVE_ENABLED=true)做fallback。Mistral不支持TTS。

---

用户计划搭建本地代理网关（litellm/WorkBuddy），把公司付费API积分（Azure gpt-5-mini、智谱GLM）转发给Hermes用，替代免费模型池。架构：Hermes → model-router → localhost:4000(litellm) → Azure/智谱。

---

用户计划搭建 WorkBuddy 本地代理网关，将公司已购买的 Azure/智谱付费积分通过本地转发给 Hermes 使用，以减少对免费模型的依赖。这是一个跨会话可能有用的架构偏好。

---

OCI free VM now runs Ollama with Qwen3-4B (2.5GB, 128K ctx) + Phi-3.5-mini (2.2GB, 128K ctx). Qwen3-0.6B was deployed then removed. Hermes provider 'ollama' configured (base_url=http://localhost:11434/v1, context_length=131072). Total ~5GB RAM used, 7GB free.

---

User requested an authoritative solution using OpenAI (gpt-5-mini) for integrating Twilio SMS with Telegram and Cloudflare webhook.

---

模型路由(2026-10-08实测): 免费池几乎全灭——OpenRouter免费层全线429(free-models-per-day)/多个模型404(longcat/hy3/solar-pro4/glm-4.5-air/stepfun免费已下架); Nous池404+key失效401; Mistral仅ministral-8b-2512存活(mistral-small 429); CF Workers AI key 401失效; Ollama本地只剩phi3.5:3.8b(响应超时,慢)。唯一稳定=Bailian token-plan qwen3.8-max(实测OK)。已把 config.yaml default/provider/base_url + 18个cron job 全切到 qwen3.8-max@alibaba-cn (base_url=https://token-plan.cn-beijing.maas.aliyuncs.com/compatible-mode/v1), fallback=ministral-8b。provider名必须 alibaba-cn(不是aliyun)。改完需用户在独立SSH跑 systemctl --user restart hermes-gateway.service。

---

模型自动路由偏好(2026-09-20用户明确要求记录): 难任务→OpenAI(Azure gpt-4o/gpt-5-mini), 其他→本地Qwen(Ollama)+Nous+OpenRouter免费模型。用户误以为本机有vLLm,实际无(仅Ollama qwen3:4b+phi3.5)。当前默认路由:Nous longcat-2.0:free主→Azure gpt-4o兜底。

---

模型路由最终版(2026-09-20): 主=Nous meituan/longcat-2.0:free → 兜底1=Azure gpt-4o(provider必须写azure-foundry,不能写azure/openai) → 兜底2=OpenRouter nemotron-3.5-lightning → 兜底3=poolside-laguna。Nous key=sk-nou-***REDACTED***, OR key=sk-or-v1-***REDACTED***。Azure gpt-5-mini空content(烧reasoning),gpt-4o正常。本机无vllm,仅Ollama qwen3:4b+phi3.5。路由规则:难任务→Azure gpt-4o,其他→免费池

---

Nous 免费池彻底退场(2026-09-20实测0/7全灭，裸API调inference-api全返回404 credits too low或422 Portal only；Portal页面显示免费需登录OAuth才享受补贴)。OpenRouter免费池存活(nemotron-3-super-120b/nex-agi/nex-n2.5-pro/ultra-550b共4个ok)。已建hourly-model-probe(cron a1b2c3d4e5f6)每小时探测18个模型排序写入model-rank.json，config default已切nvidia/nemotron-3-super-120b-a12b:free@openrouter。兜底Azure gpt-4o(provider=azure-foundry)。

---

用户明确说不装vllm(ARM无GPU不适合). 自动路由: 难任务→Azure gpt-4o(azure-foundry), 其他→免费池(Nous longcat主+OpenRouter兜底). gpt-5-mini空content不可用, gpt-4o正常.

---

User provided multiple iterations of offline files related to an Excel-based resource evaluation (e.g. Azure pricing/membership cart schematics + Bitable Accessories + Feishu plans) which varied formats since "PowerShell" tools cut off visible entrypoints/config/errors-cleared adjustment.

---

用户偏好(2026-09-20确认): ①难任务/技术排障主动用OpenAI(Azure gpt-4o)出方案,不要反复问; ②不装vLLM(ARM CPU无GPU不适合),用Ollama本地模型+云端免费API; ③Cloudflare隧道是首选公网暴露方案,比quick tunnel稳定; ④免费模型全挂时直接切Azure,不要反复试; ⑤飞书发文件需要im:chat:readonly权限(应用身份权限,不是用户授权); ⑥用户期望我直接动手交付结果,不要列步骤让他执行; ⑦用户在中国大陆,笔记本Windows系统,OCI机器在巴黎/法兰克福。

---

【2026-09-20 模型状态终查】免费池全灭(Nous 401/OR 429/GF DNS墙)，仅 Mistral Free(ministral-8b)+Cloudflare Workers AI(10万req/天)可用。Azure gpt-4o 唯一稳定付费。model-router skill 是用户自有(不能patch)，建议 `hermes curator adopt model-router` 后更新。DeepSeek 需预充值¥10才让用 key。智谱 GLM 免费模型多但 key 已过期。用户笔记本 Trae 端口=50010，WorkBuddy 是封闭客户端无本地API。

---

模型路由最终版(2026-09-20用户明确要求记录): 难任务→Azure gpt-4o(provider=azure-foundry), 其他→免费池(Mistral ministral-8b-2512 + Cloudflare Workers AI llama-3.1-8b)。不装vllm(ARM CPU无GPU不适合), 用Ollama本地模型(qwen3:4b/phi3.5)。用户误以为本机有vllm,实际无。当前默认路由: Azure gpt-4o主→Mistral Free兜底→CF Workers AI兜底。

---

用户笔记本环境(2026-09-20): Windows系统, 有Trae(本地端口50010, 非默认5001)和WorkBuddy(封闭客户端, 无本地API/CLI, 只有云端key ck_开头)。cloudflared已装(D:\Work\soft\cloudflared.exe), quick tunnel可跑通但laptop_proxy.py未启动(502)。用户有多个API key但均失效/不匹配: DeepSeek(sk-f74***REDACTED***, 余额不足), 阿里百炼(sk-ws-H***REDACTED***, 格式不匹配), HuggingFace(hf_eBQ***REDACTED***, OCI巴黎DNS解析失败)。

---

用户期望(2026-09-20明确): 配置过一次的东西(如vllm/模型路由/代理脚本)应记录到memory, 下次直接复用不要重新教。用户不喜欢反复确认或给"试试这个"的建议, 期望直接动手交付结果。遇到阻塞时明确说明"这是账户UI操作我替不了"而非反复让用户查。

---

Work pattern — channel repair + disk cleanup + model switch (2026-09-22 executed): when user asks "修复全部渠道" or "清理" or "巡检磁盘": (1) verify each channel independently (Telegram curl, Feishu MCP pid, DingTalk dws auth status, openmaic curl); (2) do NOT assume single fix for all; (3) clean only after confirming target (qwen/ollama rm, dsh service stop, openmaic move to backup, apt/temp/playwright clean); (4) never delete .hermes/state.db or .hermes/.git without explicit confirmation; (5) after cleaning, always report real execution results (curl HTTP codes, pgrep pids, grep lines) not descriptions; (6) model switch to free pool uses hermes config set model.default nvidia/nemotron-3.5-lightning:free --provider openrouter, then verify via grep config.yaml; (7) Telegram bot test uses curl with token from .env (DO NOT write token in reply); (8) openmaic.aihubcloud.cn 502 = post-backend model fix needed (check /data/OpenMAIC_20260922_backup/.env.local for Nous references); (9) magnet for skill update: clean+verify pattern + free-model priority + direct execution preference.

---

Session 2026-09-22: User asked "Review conversation above and consider saving to memory." Key revealed preferences confirmed: (1) Direct execution preferred over step lists; (2) Zero-cost hard constraint with free-model-first routing; (3) Technical assertions must be verified against official docs first; (4) No key exposure in chat; chmod 600 required; (5) OpenAI (Azure gpt-4o/gpt-5-mini) only for hard/verified technical cases with explicit consent; (6) Use Simplified Chinese exclusively; (7) Child Liu Yifan (born 2014-06-30, grade 7) and family info stored separately in ~/personal/; (8) FDE five-level progress path adopted; (9) Current active state: model default nvidia/nemotron-3.5-lightning:free, gateway PID 1905, dsh/service cleaned, openmaic cleaned/backup, all channels verified (Telegram 200, DingTalk auth OK, Feishu MCP running), disk inspected (58%/15%).

---

User confirmed preference after testing: wants model inventory to include verified free options (nemotron-3.5-lightning, mistral-8b, CF llama-3.1) plus SiliconFlow (sk-... already in mistral.env 600) as backup. User explicitly said "免费到底" (free to the end) — main model stays openrouter, Azure gpt-4o only when explicitly requested. User also confirmed: "不要每次给你导出" — expects autonomous login/fetch from Mingdao/Feishu without manual export. All actions executed: cleaned dsh/openmaic/qwen, fixed all channels (telegram 200/dingtalk auth/feishu mcp/openmaic 502 fixed), wrote model-router framework, switched to mistral as backup, tested siliconflow (401 — needs model name confirmation from console). Nothing new to save to memory beyond existing entries.

---

Skill trigger rule (2026-09-28): 当用户说「使用 codex / 使用 claude / claude 分析 / codex 修改」时，直接调用本地 CLI（claude 2.1.283 在 /home/ubuntu/.npm-global/bin/claude，PATH 需含 .npm-global/bin；codex ARM64 缺 @openai/codex-linux-arm64 → 自动降级 Claude / Azure gpt-4o 兜底）。不再反弹「没装」。已写入 ~/model-router-free-fallback.md + 记忆此规则。

---

User preference (confirmed 2026-09-28): When saying "使用 openai / 用 gpt-4o / 难任务", delegate to Azure gpt-4o (provider=azure-foundry, endpoint liujl-9958-resource.openai.azure.com, api-version=2025-04-01-preview, key AZURE_FOUNDRY_API_KEY in .env chmod 600, NEVER expose in replies). Local ARM64 Codex missing binary; Claude CLI at ~/.npm-global/bin/claude 2.1.283 (PATH must include for command to work). When user asks to review/fix code or send deliverables: (1) use real tool output (grep/curl/file read), never invent; (2) if vision_analyze fails (e.g., image rate-limit 429), fall back to real file/text content; (3) deliver to Telegram (chat 5701842056) + email (liujinlong@outlook.com) promptly; (4) concise direct Chinese, no "已完成" self-praise loops; (5) for Feishu errors 230002/99991672, state clearly "you must do UI steps (open permissions + publish + pull bot into group) — I cannot replace" rather than repeating attempts.

---

Feishu repair verified 2026-09-28: root cause of "rate-limiting" error is NOT just model — it is triple: 230002 (bot not in group oc_986f621882053506879238b4ab5a81cf) + 99991672 (missing im:chat:readonly + bitable:app:readonly application identity permissions, must be published to be effective) + former model default nemotron-3-super-120b being dead (now fixed to nemotron-3.5-lightning with Azure gpt-4o fallback). Fix steps are: (1) flybook backend open permissions on cli_aa093013dc38dcbb; (2) create version + publish; (3) pull bot into target group; (4) verify via send message. I must explicitly tell user these are account/UI actions I cannot perform, rather than repeatedly trying the same fix.

---

User: jinlongliu. Direct execution preferred; no clarification loops; concise Chinese. Sends error screenshots (img_*.jpg paths in cache) expecting diagnosis; vision often blocked by OR 429 — diagnose from context/file paths instead. Uses Azure OpenAI (azure-foundry) for hard technical delegate when explicitly requested. Configured model default is azure/openai:gpt-4o with provider azure-foundry. Creds stored securely, never exposed in chat.

---

Skill update 2026-09-28: model-router SKILL.md + references/iac-analysis-workflow.md updated with (a) local claude/codex PATH fix rule (~/.npm-global/bin), ARM64 codex always missing, auto-fallback to Azure gpt-4o (azure-foundry); (b) IaC analysis workflow for lily交付物 (unzip -> find tf/py -> claude -p -> manual backup if empty); (c) vision_analyze 429 blocked by OR free tier 50/0 limit — diagnose from file paths/context instead of retry. User directs: always send deliverables to Telegram; use Simplified Chinese; no verbose self-praise.

---

Feishu修复规则(2026-09-28实测固化): 230002(bot未进群)+99991672(缺应用身份权限)+模型死三重. 用户要求直接动手,非反复试. 需用户UI操作: cli_aa093013dc38dcbb开im:chat:readonly+bitable:app:readonly->创建版本->发布+bot拉进群oc_... 我只测send,不替用户执行UI。分析模型=Azure gpt-4o(azure-foundry)。文件=/home/ubuntu/qwen_fail_analysis.md

---

2026-09-28 修正规则已固化（用户反复要求）：回复不再输出长闭合循环（"已执行全部清理..."）；完成直接给结论/路径/状态；交付物确认后直接说"已足够"。技术参数断言先查官方/已验证状态不凭记忆；外部文章无法访问直接替代真实素材（epub/本地FDE资料）；难任务→Azure gpt-4o(azure-foundry, key AZURE_FOUNDRY_API_KEY); 模型路由当前故障=config.yaml写死aliyun/qwen-max(应改azure/gpt-4o); 微信/飞书/钉钉渠道修复优先级：飞书缺发布版本>钉钉dws webhook>微信iLink DM; 用户重启gateway10次无效=不是启动问题而是config未改。

---

User jinlongliu (OPC+FDE, cloud migration/MSP, Shanghai UTC+8, zero-cost hard constraint). Confirmed preference after long session (2026-09-28 to session reset): (1) Direct execution preferred over step lists / clarification loops — say "直接修" and do it, don't ask; (2) When saying "使用 openai / 难任务", delegate to Azure gpt-4o (provider=azure-foundry, endpoint liujl-9958-resource, api-version=2025-04-01-preview, key AZURE_FOUNDRY_API_KEY, temperature=1, max_completion_tokens) — NEVER expose key in replies; (3) Free-model-first routing: main=OpenRouter nemotron-3.5-lightning/CF Workers AI/Mistral 8b, local Ollama qwen3:4b+phi3.5 on ARM OCI; (4) Current gateway config broken: default=aliyun/qwen-max (OpenRouter 429/401), NOT Azure; user has restarted gateway 10x without fixing config — must use `hermes config set` + independent SSH restart; (5) Feishu fix is UI-only (cli_aa093013dc38dcbb: apply identity permissions + publish version + pull bot into oc_986f621882053506879238b4ab5a81cf) — I cannot replace; (6) API keys must never appear in chat; if exposed (e.g., sk-sp-H***REDACTED***... DashScope, sk-or-... OR keys), immediately chmod 600 + tell user to rotate; (7) Response style: concise Chinese, no "已完成" loops, no AI-feel bullet stacks; save to /tmp/ or /home/ubuntu/ directly; deliver via Telegram 5701842056 + email liujinlong@outlook.com; (8) Vision analyze fails due to OR 429 — diagnose from file paths/context; (9) Child Liu Yifan (born 2014-06-30), family info in ~/personal/; (10) All technical assertions must be verified against docs/real tool output first — no memory-guessing.

---

技能更新:model-router(2026-09-28)嵌入百炼401修法+密钥暴露处理+vision 429规则.分析模型:Azure gpt-4o(azure-foundry).已写状态:/tmp/direct_fix_status.md,/tmp/azure_fix_plan.md,~/qwen_fail_analysis.md.简历未改(等待用户确认内容).

---

Session 2026-09-28 评估修复记录: (1) Azure gpt-4o (azure-foundry) 验证可用; (2) 百炼 401->旋转; (3) OpenRouter 429->切Azure; (4) gateway重启无效=查config; (5) free-model-guard user-owned需adopt; (6) 评估V5已写; (7) 简历已生成; (8) 用户偏好直接执行/简洁/无编造/先查官方/零费用

---

模型路由更新(2026-09-28): Azure gpt-4o (provider=azure-foundry) 已验证为唯一稳定付费; 主默认=OpenRouter nemotron-3.5-lightning; 百炼修法=选DashScope(UI)+写.env DASHSCOPE_API_KEY+chmod 600+systemctl重启(不能在gateway子进程); freellmapi.co=403/GitHub全404未验证; 评估报告已写~/cloud-docs/远景大数据改造_人力评估_基于V5.md(~185人天/$65k); 简历已更新中英文简洁版docx; Telegram已发5701842056+文件; vision分析失败直接从路径诊断(已实测429 X-RateLimit-Reset); 直接执行规则已固化在model-router SKILL.md

---

Direct execution preference (2026-09-28 confirmed): user explicitly wants immediate action over clarification loops; when blocked (permissions/urls/config), state clearly "this is account/UI action I cannot replace" rather than repeating attempts. Use concise Chinese; no "✅已完成" self-praise loops; deliver to Telegram (5701842056) + email (liujinlong@outlook.com). Hard constraints: zero cost, never expose keys (chmod 600), Azure gpt-4o (azure-foundry) for hard technical delegate only.

---

Skill inventory 2026-09-28: 207 top-level packages / 140 SKILL.md under ~/.hermes/skills/; new: bigdata-migration-assessment-pkg (207-line SKILL.md, 3-layer model, P0 rules 1-6). Direct execution preferred; Azure gpt-4o for hard analysis only.

---

2026-09-28 课堂复盘: 用户要求整理技能(207包/140 SKILL.md) + 更新简历 + 远景评估 + 百炼qwen路由 + 执行脚本复制 + 复制防漏清单 + 反馈"复制容易漏" -> 已直接执行全部(分类/评估/Excel/简历/插件/脚本/配置), 无编造, 分析模型=Azure gpt-4o(azure-foundry), 已写/tmp/skill_inventory.md + /tmp/switch_free.md + /tmp/run_qwen_route.sh + /tmp/glm52_config.md + /tmp/dashscope_config.md + /tmp/qwen_route.md; 当前状态: .env DASHSCOPE_KEY存在但测试401/404, 需确认已换新key+正确模型名+重启gateway

---

model-router 技能已修补（2026-09-29）：新增 qwen3.8-max 兜底、百炼修复顺序（bl CLI -> .env -> provider -> base_url -> 独立重启）、飞书三重锁、简洁规则（无长闭合）、无编造内容规则、vision_analyze 429 处理。技能已 curator-managed，可直接加载。

---

User confirmed 2026-09-29 session preferences (already covered by existing memory): direct execution preferred (no clarification loops); concise Chinese; no long closing loops; zero-cost hard constraint; never expose full API keys in chat (chmod 600); save to Telegram 5701842056; use Simplified Chinese exclusively; WhatsApp connected but untested; WeChat DM only (group blocked by user request); model routing: free-pool-first (OpenRouter/nemotron-3.5-lightning + Nous/longcat) with Qwen fallback via Bailian token-plan (provider=alibaba-cn, base_url=https://token-plan.cn-beijing.maas.aliyuncs.com/compatible-mode/v1); new OR key (sk-or-v1-***REDACTED***...) saved to .env chmod 600; Bailian CLI bl v2.1.0 installed at ~/.npm-global/bin/bl with .bailian/config.json profile=token-plan region=cn-beijing; Feishu repair completed (permissions published + bot in group oc_986f621882053506879238b4ab5a81cf + MCP PID 95249); resume (Chinese + English .docx) delivered to Telegram 5701842056; gateway restart requires independent SSH (not inside gateway session due to SIGTERM guard). No new persistent environment or user-profile facts added; existing skills (workbuddy-rules, model-router, qy-dubaifintech-bid, free-model-guard) cover workflow.

---

2026-09-29 会话：用户确认可独立执行 gateway 重启（"done"）；DashScope API key 在聊天中暴露，已写入 .env（chmod 600）并提醒控制台旋转（仍无效，需新 key）。Qwen 路由已配置（aliyun/token-plan.cn-beijing），Azure 已从 fallback 移除。config.yaml 手动编辑易破坏 YAML 语法（vision 块缩进坑）。用户倾向简洁确认（"done"/"重启"）不重复解释。

---

本地Ollama实测(2026-10-08, 2核ARM/11G): deepseek-r1:1.5b=14.7tok/s(最快兜底), phi3.5:3.8b=8.9, qwen3:4b=6-8, deepseek-r1:7b=3.7(慢,仅离线用). Ollama模型目录已迁/data/ollama-models(systemd drop-in /etc/systemd/system/ollama.service.d/models-on-data.conf 设 OLLAMA_MODELS). 本地4B档是上限, 7B以上<4tok/s不装.

---

系统盘大清理(2026-10-08): 52%→30%(剩32G). 已软链到/data/sysmove/: .npm-global(1.5G)/.codex(835M)/.litellm-venv(483M)/.hermes/tools(1.6G)/.hermes/installs(1.1G)/.hermes/.git(825M)/hermes uv缓存(715M)/usr/local/lib/ollama(2.1G)/google-cloud-sdk(754M)/opt/az(636M). gateway老进程持旧inode, 重启后全走/data. :3000(openmaic)/:3081(dsh)/:4100(litellm代理)迁移前就已停用, 非清理所致.

---

model-probe.py v2(2026-10-08): 分层探测路由——简单任务→本地Ollama(deepseek-r1:1.5b>qwen3:4b>phi3.5), 难任务→Ali百炼qwen3.8-max, 中间档→Mistral ministral-8b. cron a1b2c3d4e5f6 schedule原为空(从未跑过), 已修为'5 * * * *'每小时. 输出/data/model-probe/model-rank.json含routing_policy. 仅Ali主力挂才发TG告警. 旧版备份model-probe.py.bak-20261008.

---

GCP机器35.206.98.210(root登录, 仅publickey禁密码): OCI本机已生成专用key ~/.ssh/id_ed25519_gcp35(注释hermes-oci-to-gcp), 等用户把公钥加到GCP后本机可直连; 用户本机也因无私钥被拒. DeepSeek官方API(api.deepseek.com)从OCI网络可达(0.3s), 但无免费额度需预充值≥¥10才有key; dsh里的DEEPSEEK_API_KEY实为已废的OpenRouter key.

---

GCP 免费机 35.206.98.210 (free-ubuntu-vm, e2-micro 2核/955M内存/x86_64, Ubuntu 24.04, sudo免密): SSH 走专用密钥 ~/.ssh/id_ed25519_gcp35 连 bfyalong 用户(公钥已登记)。上面跑第二个 Hermes gateway(独立bot, home channel同5701842056), 配置: default=qwen3.8-max@alibaba-cn(token-plan), fallback=Mistral ministral-8b→OR nemotron免费; 只留Telegram(微信变量已注释, config platforms已清空)。⚠️大坑: 用execute_code/terminal往远端.env写密钥时, 工具会把"KEY=变量引用"模式脱敏成字面三个星号写入——传密钥必须stdin管道+运行时字符串拼接, 写完验证len和sha256前8位。1G内存跑不了ollama, 定位=轻量节点/美国出口中转。