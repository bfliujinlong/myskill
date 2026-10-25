Feishu: Hermes接cli_aa093013dc38dcbb(凭证~/.feishu/credentials.json); 另cli_aaeb0ff8aa381cb3是anchnet旧应用勿用. 该app后台需发布才能发消息(步骤见计划§Phase0).

---

_sys: memory_char_limit 已扩至8000/user_char_limit 5000(2026-08-21, config.yaml memory段嵌套). 维护原则: 记忆只放跨会话稳定事实, 临时状态与易变细节(飞书发布步骤/隧道重建命令/卡单审批/部署状态)移入~/.hermes/plans/或skills, 不占记忆额度. 每周审查删过期/重复条目.

---

用户硬约束: 零费用绝不花信用卡一分钱(已建双护栏). 飞书app cli_aa093013dc38dcbb需被拉进目标会话才能发消息(报错230002). 已设FEISHU_HOME_CHANNEL=oc_986f621882053506879238b4ab5a81cf但bot未进群, 飞书告警暂未通. ⚠️实测API级根因(2026-08-31探针): 应用凭证有效(tenant token 正常获取, 机器人"kim的助手"activate_status=2), 但缺'应用身份权限' im:chat:readonly(im:chat/im:chat:read 任一)→查询群聊/确认在群内全返回 99991672 Access denied; 该 scope 缺失掩盖了 230002 bot未进群. 修复=飞书后台给 cli_aa093013dc38dcbb 勾 im:chat:readonly 应用身份权限+创建版本发布+把bot拉进群 oc_986f621882053506879238b4ab5a81cf.

---

飞书多维表格(bitable)自动化卡点: anchnet应用 cli_aaeb0ff8aa381cb3 与主应用 cli_aa093013dc38dcbb 均无 bitable:app/bitable:app:readonly 权限; lark_oapi 读写 anchnet.feishu.cn 的 wiki 表(含 ?sheet= 多维表格)返回 99991672 Access denied. 用户在 anchnet 租户做周维度 OKR/任务跟踪(对比'上周表 vs 本周表'、补 G列交付结论+右侧加英文列). 未开权限前, 飞书表格类任务只能让用户导出CSV离线处理, 或先去飞书后台给应用开 bitable 权限才能自动读写.

---

dsh 隧道=OCI AI Hub 托管(oci-ai-hub, ID 255a72ac-a360-4834-93d7-9eeead262373, 法兰克福边缘, 副本ID 159a7eec-f4c3-46b8-aeff-a33ad3849ef7=本机cloudflared)。本地链路全通: dsh:3081 ← nginx:3080(systemd active) ← cloudflared.service active. ⚠️致命死结: OCI AI Hub 控制台显示该隧道**路由数=0**, 即未配任何公网入口, 故无外网URL. 已验证多路走不通: ①命名隧道默认子域<id>.cfargotunnel.com返回000; ②trycloudflare临时隧道被CF限流429(账户级, 持续数小时, 重试加重); ③本机无cert.pem, cloudflared CLI无法list/add路由; ④`oci ai`是Language Service非隧道, CLI无AI Hub隧道命令. **唯一开公网的办法=用户登OCI控制台 oci-ai-hub隧道页点'+添加路由'选Public Hostname类型→生成cfargotunnel.com子域**. 这不是我能用CLI/终端解决的, 必须用户UI操作. dsh 公网打通前, >20MB大文件走飞书通道(已验证V19 45.8MB成功).

---

Telegram bot 收文件单条上限20MB, 超了直接拦截不落盘(报'Maximum: 20 MB')。大文件改走飞书/钉钉/微信通道发(飞书单文件100MB、钉钉1GB)。实测: 泉峰技术标框架_20260825_v19.docx(45.8MB)经飞书发成功落到 ~/.hermes/cache/documents/doc_b5bc41ffd482_泉峰技术标框架_20260825_v19.docx。本地拆卷(split -b 15m)也行。

---

泉峰AWS→阿里云迁移投标项目: 投标方=上海安畅网络科技(阿里云MSP), 招标方=泉峰集团。技术标8项结构(封面+附件1-8): 人员团队/类似业绩(迁移+运维各≥3个2025-01-01后案例)/技术响应(S-01~S-04)/实施方案(G0-G7里程碑)/专业服务/增值服务/偏离表/声明及文件。源框架文件=泉峰技术标框架_20260825_v19.docx(45.8MB, 飞书收)。客户托管SOW硬约束: 15项MSP/25类云产品×4区域(华东1杭州+华东2上海+华北2北京+华南1深圳)/故障P1 15分P2 30分P3 2hP4 1工作日/SLA To Business≥99.9% To Customer IoT≥99.95% 基础架构≥99.5%/4小时协调阿里云原厂。招标不接受负偏离。

---

大文件（>20MB）经 Feishu 通道可正常收发——本会话 V19 框架（45.8MB）经 Feishu 成功收到，Telegram 被20MB限制拦截。Feishu 是大文件可靠通道（飞书单文件100MB）。

---

用户在 anchnet 飞书租户有云文档文件夹(如 Y6ZYfOPkFlnMPTdxlNRcP0U8nDd)需 Hermes 读取,但 anchnet 应用 cli_aaeb0ff8aa381cb3 缺 drive:drive / drive:drive:readonly / space:document:retrieve 应用身份权限(tenant级,非用户授权),报错 99991672。主应用 cli_aa093013dc38dcbb 读该租户返回 forbidden。解决路径:飞书开发者后台给 cli_aaeb0ff8aa381cb3 开'应用身份权限'勾 drive:drive:readonly 并创建版本发布才生效(只勾选不发布=不生效)。用户曾愿给开放平台账号让我代操作,但我基于零费用/凭据红线建议其自助。

---

飞书应用权限开通易踩坑:在飞书开发者后台开了权限必须'创建版本+发布'才真正对 tenant 生效;只勾选不发布会持续报 Access denied。区分'应用身份权限'(tenant)与'用户授权/OAuth'两层——读云文档/多维表格要的是应用身份权限。此经验适用于所有 anchnet 飞书素材自动化读取。

---

飞书 anchnet 应用 cli_aaeb0ff8aa381cb3 读 wiki 多维表格还需 wiki:wiki:readonly(或 wiki:wiki)+wiki:node:read 权限,叠加之前的 bitable:app/bitable:app:readonly。缺任一组即 99991672 Access denied。lark_oapi 的 wiki.v2.space_node 无 .get() 方法, 改用 requests 直调 OpenAPI(tenant_access_token + /wiki/v2/spaces/get_node?token=&obj_type=bitable 拿 obj_token) 最稳。开权限后须发布版本才生效。

---

飞书应用权限开通易踩坑(2026-08-31实测): 用户截图开权限时开在"用户身份权限(user_access_token)"标签页,但API调tenant_access_token需"应用身份权限(tenant_access_token)"标签——两套独立授权,开错标签=Access denied. 且用户开在"kim chat working"应用而非让我用的cli_aaeb0ff8aa381cb3(anchnet旧应用). 正确路径: 进cli_aaeb0ff8aa381cb3 → 切"应用身份权限"标签 → 勾wiki:wiki/wiki:wiki:readonly/wiki:node:read + bitable:app/bitable:app:readonly → 版本管理与发布→创建版本→发布. Hermes机器上只有anchnet旧应用和主应用cli_aa093013dc38dcbb的凭证,无"kim chat working"凭证.

---

用户反复发同一条飞书表格对比指令(4次)但权限未开,体现其倾向"发指令期望我自动搞定"而非先确认前置依赖。遇到权限/外部阻塞时不要反复空跑,应明确给"开权限A / 导出数据B"二选一,等用户真做完再动。飞书wiki表读取用requests直调OpenAPI(tenant_access_token)最稳,lark_oapi SDK的space_node resource缺get方法需绕开。

---

飞书备用 app 凭证(2026-08-31 用户提供, 作备用不启用): 已追加到 .env 的备用段(不覆盖现有主app cli_aa093013dc38dcbb)。启用需覆盖主 app 的 id/secret 两行并重启 gateway service; 前置坑=bot须进会话+发布版本(防230002)+anchnet租户读文档需开wiki/bitable权限发布(防99991672)。Hermes adapter 仅单 app 实例, 不支持双开。

---

飞书 app 现状: 主=cli_aa093013dc38dcbb(跑着, 但230002 bot未进会话致飞书投递常失败); 备用=anchnet旧应用 cli_aaeb0ff8aa381cb3(仅存.env备用段未启用)。两者皆受飞书两坑约束: 应用身份权限须发布版本才生效 + bot须进会话。

---

飞书 anchnet 周报 wiki（U8sEw05S6iO9fwk48r6cCm91n4c=上周 / F3Y6w2PGOiyc1MkMpDlcBcnQnrh=本周，?sheet=D7dkp8）是**电子表格(spreadsheet, obj_type=sheet)**非多维表格：wiki/v2/spaces/get_node 拿 obj_token 当 app_token，再用 sheets/v2/spreadsheets/{token}/values/{sheetId}!A1:Z400 读写(读 valueRenderOption=ToString)。列: A Objective/B SEQ(OKR ID)/C KeyResult/D ExpectedOutcome/E TASK/F 优先级/G 最终交付结论/H 英文版/I 交付物link...。写单元格需 sheets:spreadsheet 读写权限；主应用 cli_aa093013dc38dcbb 仅开 bitable:app(多维表格只读)→对电子表格 PUT 返回 403 91403 Forbidden。要写必须后台开 sheets:spreadsheet 并发布版本。注意 SEQ 有 '06Kx'(数字0)写法非'OK'。

---

pcs-presales-ps skill created at ~/.hermes/skills/pcs-presales-ps/ with 11 subdirectories (00-系统说明与索引 through 99-归档与废弃素材) mirroring Feishu wiki structure, plus SKILL.md. Cloudflare tunnel hostname is very long because it's auto-generated UUID format: dsh.<tunnel-uuid>.cfargotunnel.com — user asked about this.

---

DingTalk Workspace CLI (dws) v1.0.61 已装在本机 /home/ubuntu/.local/bin/dws（linux/arm64）。Skills 自动装到 ~/.agents/skills/、~/.claude/skills/、~/.hermes/skills/（14个产品skill：doc/calendar/chat/contact/drive/event/mail/minutes/todo/wiki/aitable/aisearch等）。认证流程走 OAuth 设备码（dws auth login --device），当前等待用户扫码授权中。

---

用户最大化用钉钉渠道：装 dws CLI 后能直接读文档/日历/待办/多维表格/云盘/考勤/会议纪要，不需要企业微应用（dws 走个人 OAuth 设备码认证，无需超管审批）。用户明确倾向"装就行"直接动手。

---

已落地：本地 stdio MCP 代理脚本 scripts/feishu_mcp_server.py（仅 httpx 依赖），转发 Hermes 工具调用到飞书远程 MCP（mcp.feishu.cn），自动管理 TAT 刷新。config.yaml 已加 feishu-mcp server 段，网关重启后生效。命名规则 mcp__feishu_mcp__<tool>（server名 feishu-mcp → feishu_mcp）。

---

【2026-09-06】商务基准：定价模型 AC-MIG，标准 $350/人天；SOW 标准 14 章；报价迭代=基线版→参考模板对齐→中英双版分文件；对外交付 Word/docx，讲解 PPT，内部测算 Excel；文档协作 Feishu wiki/sheets/drive。

---

dws CLI 已装好并认证：/home/ubuntu/.local/bin/dws，身份=金龙 @ 上海安畅网络科技股份有限公司（corp_id=ding58230c81113bca4f35c2f4657eb6378f, user_id=053123341198056）。Token 有效至 2026-09-05，刷新至 2026-10-05。dws 无法读取部分钉钉文档（wiki node search 返回 Data not found），需用户粘贴内容或移到个人空间。

---

飞书 MCP 通过 stdio 代理接入 Hermes：本地跑 /home/ubuntu/.hermes/scripts/feishu_mcp_server.py（内部转发到 https://mcp.feishu.cn/mcp + TAT 鉴权），config.yaml 加 mcp_servers.feishu-mcp 段。可用工具：search-doc/fetch-doc/create-doc/update-doc/list-docs/get-comments/add-comments/search-user/get-user/fetch-file。不支持电子表格读写。

---

飞书 MCP 已部署并验证可用(2026-09-07)：本地 stdio 代理 `~/.hermes/scripts/feishu_mcp_server.py` 作为网关子进程跑，10 个工具自动注册为 `mcp__feishu_mcp__<tool>`(search-doc/fetch-doc/create-doc/update-doc/list-docs/get-comments/add-comments/search-user/get-user/fetch-file)。配置在 config.yaml 的 mcp_servers.feishu-mcp 段。MCP 的 fetch-file 限 5MB，不支持电子表格读写。

---

飞书 MCP 已部署为本地 stdio 代理（/home/ubuntu/.hermes/scripts/feishu_mcp_server.py），注册在 config.yaml mcp_servers.feishu-mcp 下，TAT 鉴权走主应用 cli_aa093013dc38dcbb，转发到 https://mcp.feishu.cn/mcp。可用工具：search-doc/fetch-doc/create-doc/update-doc/list-docs/get-comments/add-comments/search-user/get-user/fetch-file。网关子进程 PID 158703 运行中。

---

明道(anchnet)登录凭据(用户明确要求记住,避免每次导出): 用户名 15102159929, 密码 G00didea!。登录障碍=图片验证码(OCR无法识别,tesseract乱码,PaddleOCR在ARM crash,vision模型读不了截图)。解法:①飞书扫码登录(飞书OAuth中转) ②用户截图发我。明道URL: https://mingdao.anchnet.com/app/d880d8b0-1aa8-44d6-b5c6-f724a9d26c12/workflowdetail/record/6a9e0cbd131b7ae3469c8d72/6a9e0cc3131b7ae3469c8e89

---

明道登录完整流程(已验证): 打开 https://accounts.feishu.cn/accounts/page/login?app_id=12&no_trap=1&redirect_uri=... → 飞书扫码登录(非账号密码) → 跳转回明道 → 访问记录页。关键: headless 浏览器需通过 playwright + JS 操作(input setter dispatchEvent)。每次脚本开新 context 会丢失 session,需重新扫码。明道登录页URL: https://mingdao.anchnet.com/network?ReturnUrl=... 飞书扫码中转后 session 建立。

---

用户硬偏好:「不要每次给你导出」——明道等内部系统数据,用户期望我自主登录抓取,而非反复让用户手动导出。遇到登录障碍(OCR/验证码)应多换思路(飞书OAuth中转/保持会话等待扫码),不要反弹回用户。

---

明道(anchnet)系统：用户公司项目管理系统，用于工时记录、项目管理、招聘。登录需飞书扫码（图片验证码，有效期30-60秒，headless浏览器无法自动完成）。登录凭据：用户名15102159929，密码G00didea!。读取明道数据需用户自行截图或导出Excel发我分析。

---

dws CLI v1.0.61 已装好并认证（金龙 @ 上海安畅，corp_id=ding58230c81113bca4f35c2f4657eb6378f），14个 dingtalk-* skill 已装。钉钉出站 webhook 未配（待用户创建机器人后填 DINGTALK_WEBHOOK_URL）。读在线文档/多维表格/日历/待办/通讯录/云盘/考勤等需先开 CLI 访问管理 + 7个API权限。

---

Feishu MCP (feishu-mcp) confirmed working for reading wiki sheets (spreadsheets). Token auto-refresh via feishu_mcp_server.py proxy. Need to use browser automation (Playwright) for LuckySheet data extraction since MCP only supports docx not spreadsheets.

---

User's current active projects: 1) Hisense-Bosch AC MSP proposal (IoT 7x24 ops, done), 2) Express Logistics LZ+Migration quotation ($359,550, done), 3) 百威 project AI engineer recruitment (resume screening, K8s hard requirement), 4) Feishu OKR weekly comparison (blocked on login), 5) Mingdao工时 analysis (blocked on wrong password).

---

User sent multiple offline documents and directly requested to upload, analyze, and integrate content into Feishu tables — emphasizes task completion over clarifications or delays. User expects IaaS and PaaS breakdowns to be incorporated into project deliverables.