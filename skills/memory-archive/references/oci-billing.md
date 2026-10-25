Cloudflare: acct=6413823f243b9dc615778a19021db968(控制台登录邮箱Bfyalong@gmail...). 硬约束: 用户本地无法直连OCI公网130.61.110.133, 一切外网访问走命名隧道中转.

---

OCI 免费机 (VM.Standard.A1.Flex 2 OCPU/12GB, ARM aarch64). 公网130.61.110.133(法国巴黎出口，非德国). 系统盘45G+数据盘150G=197G/200G. 已装tf1.12.2/claude-code/node22. 目标0费用. dsh.service running (node tsx, port 3081). cloudflared active (quick tunnel + AI Hub tunnel). nginx proxy 3080→3081.

---

_sys FDE 作战原则(摘自两篇行业文《面了100个FDE》《FDE之后AI人才需求的分水岭》): 1)什么值得做>快速做; 2)先进现场跟着干一遍才懂业务; 3)把客户模糊想法变真问题; 4)AI进组织后人与系统重分工; 5)端到端负责≠端到端自己干完(用Hermes+OCI当系统而非手); 6)Result Owner不是接口人; 7)同问题下次最好别再需FDE(把一次性活变可复用系统); 8)FDE真正价值=把不确定翻译成可交付; 9)分化大于扩招(中间'只会调prompt的人'将失竞争力); 10)技术深耕是护城河(FDE须有真实工程能力如OCI写迁移脚本/roles-*技能). 用户是单兵OPC+FDE, 这些原则指导所有售前/交付自动化.

---

_sys FDE 官方定义(2026-08-22, Palantir官方文档): FDE角色由Palantir于2005年为卖Gotham发明. 现产品化'AI FDE'=交互式agent通过对话操作Foundry(Ontology=业务语义层=FDE核心交付物, Apollo=部署系统). FDE=客户现场写生产代码+拥有'数据→决策'闭环; SA/SE=演示后交专业服务. 用户单兵OPC+FDE即微型Palantir部署(OCI免费机当Foundry/Apollo, Hermes当AI FDE).

---

TG代理需求(2026-08-23): 用户在中国大陆, 手机TG需代理. 方案①每天自动转发youxiubot发的tg://proxy节点到微信+iMessage(脚本~/oci-monitor/youxiu_proxy_forward.py已写, 卡在需用户给TG API_ID/API_HASH); ②长远OCI Frankfurt自建常驻MTProto代理(等Cloudflare隧道建好才连得上).

---

OCI CLI 路径: /home/ubuntu/.hermes/hermes-install/venv/bin/oci (唯一可用). 原 oci-monitor→/data 软链已断(/data空). 账单查法: oci usage-api usage-summary request-summarized-usages --tenant-id <ocid> --granularity DAILY --time-usage-started/end. 9月1-3日费用=$0.00, 上月$0.0344遗账已归零.

---

OCI日报(~/oci-monitor/oci-daily-report.sh): 全费用维度+风险优先排序+块存储>95%🔴/>85%🟡; 上海9:00发Telegram+iMessage. 账单=SGD. 本月真实$0.0344 SGD全为Object Storage请求费, 删桶后9月归零.

---

OCI CLI不在系统PATH, 在/home/ubuntu/oci-monitor/venv/bin/oci. 调用前须: source /home/ubuntu/oci-monitor/venv/bin/activate + export OCI_CONFIG_DIR=/home/ubuntu/.oci. 账单查询: oci usage-api usage-summary request-summarized-usages --tenant-id <tenancy ocid> --granularity MONTHLY. OCI账期=自然月, 账单次月第2天起生成后结算(先用量后出账, 非每日扣).

---

OCI费用核查补遗：oci usage-api usage-summary request-summarized-usages 参数名是 --time-usage-started / --time-usage-ended（非 --from-time/--to-time；--granularity MONTHLY 会报 InvalidParameter）。延迟结算数据（如 $0.0344 遗账）需把 END 设为 UTC 明天才能纳入当月统计（今天UTC未到时该item的 time-usage-ended=明天）。脚本勿用 `set -u` 或 `|| RAW='{}'` 短链（会吞掉 oci 错误致 RAW 空、total 恒为0）。

---

用户要求'彻底修复'类任务时期望我自主解决, 不要再把控制台点击步骤反弹回给他. 但dsh公网访问是硬墙(必须OCI控制台UI加路由), 卡住时要明确说明'这是账户UI操作我替不了'而非反复让他查. 用户倾向我直接动手+交付结果, 而非列步骤让他执行.

---

OCI费用播报脚本坑(已固化): /home/ubuntu/.hermes/scripts/oci-cost-daily.sh 必须用 python subprocess 调 oci CLI（不能 shell $(...) + set -o pipefail，会吞掉 oci stdout 致$0.0000假零）；END 用 TZ=UTC date -d tomorrow（非今天，否则漏掉延迟结算的$0.0344那笔）。cron任务905b3955de1a(每天9点,deliver=all)必须 no_agent=true（否则agent处理输出再调一次模型撞429）。该任务初次创建未落库+脚本bug+agent模式撞429三层问题已全解。

---

邮件通道已配置完成：发件人 vliujinlong@qq.com (QQ授权码, 因个人版outlook基础认证被禁只能QQ代发), 收件人/Home地址固定 liujinlong@outlook.com。Hermes email adapter 靠 .env 的 EMAIL_* 变量驱动 (SMTP/IMAP 基础认证)。配置已验证 SMTP+IMAP 双向登录成功, 测试邮件已发outlook通。⚠️网关未重启(email adapter未加载), 需用户SSH登OCI跑 `systemctl --user restart hermes-gateway.service` 才真正生效(当前对话terminal是gateway子进程, 重启会被护栏拦自杀)。用户指令: 以后说发邮件都发liujinlong@outlook.com。

---

OCI每小时$0.0344告警已修: oci-billing-check.sh 加遗账白名单 KNOWN_LEFTOVER=0.05, 低于此判定'免费额度内'不告警. 实测输出'✅ 账单正常'. 该遗账9月账期归零, 不再每小时刷屏.

---

系统盘/数据盘迁移(2026-08-29): 为减系统盘增量, 已将大缓存/venv 软链到 /data(150G数据盘, 挂载/dev/sdb): /home/ubuntu/.npm→/data/npm-cache; /home/ubuntu/.cache→/data/cache; /home/ubuntu/.local/share/pnpm/store→/data/pnpm-store; /home/ubuntu/oci-monitor→/data/oci-monitor (venv activate 里 VIRTUAL_ENV 已改/data/oci-monitor/venv). journald 限 SystemMaxUse=200M+MaxRetentionSec=7day 写进 /etc/systemd/journald.conf. 系统盘 20G→17G(37%). 注: hermes-install(1.6G)是Hermes本体留系统盘未迁.

---

GitHub 备份仓库=bfliujinlong/hermes-backup(私有)。认证用 SSH Deploy Key(无token落盘)。cron 周日16:00 UTC(=上海24:00)跑 ~/oci-monitor/sync_github.sh 增量同步配置/skills/memory/脚本。恢复=git clone + bash restore_hermes.sh。换机需手动补: .env/.env.aliyun、OCI config、CF token、dsh-src重装、系统服务。

---

OCI磁盘清理(2026-08-29): 系统盘/sda1原46%(20G/45G)→清理后37%(17G)。动作: journald限SystemMaxUse=200M+MaxRetentionSec=7day写/etc/systemd/journald.conf并restart(防日志无限涨); apt clean; 迁移缓存到/data: /home/ubuntu/.npm→/data/npm-cache, /home/ubuntu/.cache→/data/cache, ~/.local/share/pnpm/store→/data/pnpm-store, /home/ubuntu/oci-monitor→/data/oci-monitor(venv activate里VIRTUAL_ENV已改/data/oci-monitor/venv)。dsh真实源码/home/ubuntu/hermes/deploy/dsh-src(非.dsh)。数据盘/data 147G, 用掉~6G。

---

GitHub 备份已固化: 仓库=bfliujinlong/hermes-backup(private)。认证=专用Deploy Key(无token落盘, 非账号级权限, 比PAT安全): 本机生成ed25519密钥对, 公钥加仓库Deploy keys(写权限), 本地config让git对该域名走此密钥。remote=git@github.com:bfliujinlong/hermes-backup.git。同步脚本/home/ubuntu/oci-monitor/sync_github.sh(增量commit+push, 无明文token)。cron: 系统crontab `0 16 * * 0`(=上海周日24:00,机器UTC)跑sync_github.sh。恢复脚本/home/ubuntu/oci-monitor/restore_hermes.sh(换机git clone+重建187个skills→cc/codex软链)。进备份: config/skills/memories/cron/jobs.json/scripts。排除(.gitignore): .env/.env.aliyun(密钥), hermes-install/dsh-src(大源码), sessions/gateway*.log(运行时态), cloud-docs(输出物)。换机需手动配: .env/.env.aliyun/.oci/config/Cloudflare token/dsh-src重装/系统服务。

---

GitHub 备份已切 Deploy Key 认证(无token落盘): 本机生成ed25519密钥对, 公钥加仓库Deploy keys(写权限), 本地config让git走此密钥, remote=git@github.com:bfliujinlong/hermes-backup.git。之前给的 PAT([GH_PAT_REDACTED])用户已删/revoke, 不再用明文token推送。cron系统crontab `0 16 * * 0`(=上海周日24:00)跑 ~/oci-monitor/sync_github.sh。恢复脚本 ~/oci-monitor/restore_hermes.sh。

---

_sys 用户FDE进阶定位+L4补齐(2026-08-30): 用户已是L5一人公司形态(判断线=选型/方案/商务取舍,产能线=Hermes+OCI免费机当AI员工团队). L4产品化补齐方向(基于真实资产,不虚构客户案例): ①AIOps智能运维标准服务包(已有中英文报价单¥504k/年+技术方案+架构图,抽客户专属变通用SKU,最成熟MVP); ②云迁移技术标书代写服务包(泉峰AWS→阿里云标书V19框架参数化复用,铁律:人员/案例真实不编); ③FDE/AI落地实战培训课(给传统MSP/集成商,基于FDE作战原则10条+Palantir官方定义); ④OCI免费机+FDE一人公司方法论(给想零成本跑AI的小团队). 渠道:微信DM/Telegram/知识星球/闲鱼(不进群、不代投、数据不出境、零费用). 定价:B端按项目/年服,C端小课299-999/模板99-499.

---

【jinlongliu FDE能力画像（来自存档笔记自评）】具备：软件工程师(生产级编码)+客户发现(售前云迁移)/部署运营(OCI+Hermes+dsh/Cloudflare全套)+现场安全意识。短板：L5 eval数据集/回归框架、L6可观测(OTel trace埋点)、L7治理(身份/权限/审计文档化)。OPC卖交付(云迁移+AIOps)，用验收24项第11/23项防scope creep。

---

用户偏好：回复简洁直接，不要"✅已完成"式自嗨；技术参数（尤其OCI/云费用）先查官方文档核实再输出；零费用硬约束（不花信用卡）；工作节奏快（白天不休息，UTC+8）；多渠道（Telegram为主）；倾向我直接动手交付结果而非列步骤。

---

OCI SSH 连接故障: 服务器130.61.110.133只允许publickey认证，用户无私钥，需通过OCI控制台或私钥恢复。

---

OCI CLI 路径: /home/ubuntu/.hermes/hermes-install/venv/bin/oci (不在默认PATH,需 source /home/ubuntu/.bashrc 或全路径调用). /home/ubuntu/oci-monitor→/data/oci-monitor 软链已断(/data空),不可用.

---

dsh (DeepSeek Harness) public access: quick tunnel URLs change on restart (e.g. marina-resident-mom-mug.trycloudflare.com) which breaks dsh's --trusted-host whitelist causing HTTP 502. OCI AI Hub tunnel (203eba87) has 0 routes in console - must add Public Hostname route manually. dsh local access works at http://127.0.0.1:3081 and http://130.61.110.133:3080 (nginx proxy).

---

【2026-09-14 系统维护经验】OpenMAIC 和 DSH 在同一 OCI 机上通过 Cloudflare 隧道暴露两个子域名（openmaic.aihubcloud.cn / dsh.aiubaihubcloud.cn）。双 cloudflared 冲突根因是旧 quick-tunnel 没杀干净；修复=禁用 cloudflared-dsh.service + 确保只跑一个 named tunnel。Next.js dev 模式 HMR WebSocket 被 CF 阻断导致空白页，必须 build + start 生产模式。DSH settings.yaml 的 agent-default-model.model 必须引用 llm-deepseek.models 中存在的 ID，否则模型选择器静默失败。Strands Agents SDK 已创建为 skill（Python+TS, Agent/Tools/Hooks/Structured Output/Conversation/Multi-Agent/Model Providers/Observability/MCP）。系统盘守护 auto-disk-guard 的安全红线需包含 .env.local 和 .credentials.yaml（当前版本可能未包含，需 adopt 后修补）。

---

用户笔记本环境(2026-09-20): Windows系统, 工作路径D:\Work\日常\上云迁移\01服务流程\04其他\03AI报价\00资源\03tool\。Trae+WorkBuddy已装并运行在笔记本(端口5001/5002)。cloudflared已有但之前误下macOS版(darwin-amd64),实际需Windows版。用户要暴露笔记本的Trae+WorkBuddy到OCI调用(通过cloudflared隧道)。代理脚本=laptop_proxy.py(笔记本端HTTP代理,监听3000转发到Trae 5001/WorkBuddy 5002)。AWS QDE Phase III考核:用户有操作手册+PPT V3(10页),考核五大方向(SSO/账户管理/IM邮箱/OA对接/自动化Skill),需录15分钟Demo视频(必须出镜)。

---

用户笔记本环境(2026-09-20): Windows x64, 路径 D:\Work\日常\上云迁移\01服务流程\04其他\03AI报价\00资源\03tool\trae-wb-local。Trae本地端口=50010(非5001), WorkBuddy无本地端口(封闭客户端)。cloudflared已装并跑通(quick tunnel URL会变)。OCI机是ARM64无法跑Chrome/浏览器自动化。