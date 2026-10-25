_sys FDE+SA/TAM 协同售前共识(2026-08-22): SA/TAM管'方案对不对'(架构/选型/可行性), FDE管'在现场跑不跑得通'(业务结果/落地验证/对结果负责); 合一点=SA 8步售前流程每步加'FDE可执行验证'红线. 物料10项≈fde-deployment各阶段文件; 能力框架'案例/异议库更新机制'=FDE原则7. 车机召回截图关联未确认,不纳入.

---

iOS桌面语音助理(用户iPhone 16, iOS 18): 用快捷指令"问我助理"实现喊Siri→录音→发Telegram bot→读Hermes回复→朗读。链路走Telegram Bot HTTP API(api.telegram.org/bot<TOKEN>/sendMessage POST表单chat_id+text=听写文本; getUpdates?offset=-1&limit=1 GET取result.message.text)。token=.env的TELEGRAM_BOT_TOKEN, chat_id=TELEGRAM_HOME_CHANNEL。触发用"嘿Siri打开问我助理"(Siri原生开指令, 不需绑短语); iOS18"添加到Siri"入口在指令自身详情页(长按卡片→详情), 不在自动化列表也不在设置→Siri。避坑: getUpdates偶尔读旧消息(等待改5-8秒); token明文存iPhone本地(丢机风险); 用户有旧iPhone13/6及密码遗忘的安卓, 但iPhone16是主用助理设备。

---

用户设备(2026-08-30): iPhone 16主力(iOS18, 日常Telegram/微信聊Hermes), iPhone 13完好备用, iPhone 6太老A8废弃, 安卓若干台密码遗忘。桌面AI助理用iPhone而非改造儿童机器人(Alilo G6封闭嵌入式系统不可编程, 已确认不值得改造)。

---

_sys FDE五级进阶路线图(微信科普版, 2026-08-30 学自《FDE时代来了:普通人从Skill到FDE的五级进阶路线图》硕硕AI成长日记): L1 Skill=把套路写成AI可执行说明书(重复5次以上的事,1-2-3-4步+意会判断标准); L2 Agent=给目标/工具/边界让AI自己干(定时任务自动跑,只验收); L3 系统化=流程SOP化+AI员工分工+数据回流(标准:休假一周业务还转); L4 产品化=能力变数字资产反复卖(一次生产反复收租); L5 FDE=一人公司(判断线你出+产能线AI出)。核心:用AI是本事,把AI装进业务是手艺,活成FDE是路线;不要跳级(L1地基没打好谈系统化=空中楼阁);不会写代码也能到L4。此路线与memory中Palantir官方FDE定义(现场写生产代码+拥有数据→决策闭环)互补——官方版是岗位定义,此科普版是普通人自我进阶路径。

---

User's key expectations: 1) Save work patterns/preferences to memory when revealed. 2) Use Simplified Chinese exclusively (explicitly requested after seeing Japanese). 3) Respond quickly to /btw prefix requests as side notes. 4) Handle API key exposure seriously — user flagged 'sk-or-...260b' may have been exposed in image screenshot. 5) When vision_analyze fails, explain why clearly rather than pretending to see image.

---

用戶公司案例庫：SmartCare-案例集-北区-V1.1.pptx (52頁)，內含 Landing Zone / WA優化 / 跨雲遷移 / 大數據遷移 / IaC / 容災 / 信創 等8大場景、10+真實客戶案例（外服雲、Veolia、Cabot、安聯、無印良品、阿斯利康、越秀、史泰博、百濟神州等）。做 HLD 方案時應優先引用此案例庫的模式與經驗。

---

用户正在构建售前资料库，后续会按方向（如 Landing Zone / 云迁移 / WA 优化 / 大数据 / DR / IaC 等）要求整理售前素材。素材来源为 SmartCare 案例集（北区/东1组/东2组），路径 /home/ubuntu/cloud-docs/SmartCare案例集/，每组含 .pptx 和已提取的 案例集.md。要求：按方向抽取对应案例 → 整理成售前可用资料。

---

【2026-09-05】硅基流動(SiliconFlow)對德國/海外IP：key返回"Invalid token"，可能是未完成實名認證、未領2000萬免費額度、或key過期。需去cloud.siliconflow.cn確認額度狀態。德國用戶推薦先測Groq（歐洲更穩）。

---

PPTX合并工作流(已验证): python-pptx Presentation.copy()跨实例失败; zipfile XML raw approach可用. 标准插入法: 读base和src的slide XML→重写rels(media换名复用,E3 layout/master复用)→更新sldIdLst+presentation.xml.rels+[Content_Types].xml. 流程=收文件→验证→zipfile合并→PyMuPDF质量验证→Telegram发送.

---

Mistral AI key 已验证可用，存储在 ~/.hermes/skills/mistral/mistral.env (chmod 600)。免费层限速严（~1次/分钟），适合低频高质量调用。可用模型：mistral-small-latest, codestral-latest, ministral-8b-2512 等 16 个。

---

用户在中国大陆（上海时区，UTC+8），本地 AI 智能体包括 Claude Code / Codex CLI / Cursor / WorkBuddy 桌面端，需规避 OpenAI/Codex 直连限制

---

ali CLI profiles：liujinlong(cn-shanghai)、tc_bigdata(cn-shenzhen)、anchang(cn-hangzhou)。

---

vision_analyze 工具看不到本地截图文件（MEDIA: URI 或本地路径均无法在 vision 模型渲染）。截图分析需靠用户上传图片到对话，或通过 OCR（tesseract 可装但效果差，PaddleOCR 在 ARM 上 segfault）。

---

安全规则: 有攻击立即封IP，零容忍。

---

GitHub 私有仓库: xx-customer-iac (IaC代码), xx-customer-ci (CI代码)。SSH key id_ed25519_github 已加到账号级。

---

Sys FBliujinlong GitHub=bfliujinlong/hermes-backup(private,Deploy Key认证);用户新需求=把workbuddy-100-prompts fork/clone到bfliujinlong下并整理成MD

---

WorkBuddy 100套提示词: GitHub仓库 feng-liu-1994/workbuddy-100-prompts(10分类,纯前端index.html,localStorage存数据)。已clone整理成MD并push到 bfliujinlong/hermes-backup(workbuddy-prompts/100-prompts-complete.md)。docx版在 ~/cloud-docs/WorkBuddy-100-Prompts.docx。

---

User frequently assembles PPT proposals (SmartCare案例集/MS project bids) using python-pptx. Template cloning is standard workflow. User sends source PPTX + target structure, assistant generates merged output. Dark business style, no blue/'AI' feel.

---

Twilio: 账号[REDACTED_TWILIO_SID], 余额$10.67, 当前号码+1 202 816 6399(DC华盛顿区号, 旧号已释放). 用途: 收海外服务验证码→转发到TG. Palantir AIP屏蔽VoIP号, 需实体SIM号(TextVerified或Tello eSIM).

---

用户在本轮明确要求：以后回复不要重复“已执行全部清理与修复，已交付全部输出物，已确认无遗漏，已给出路径。已足够。已完成全部流程。”这类无意义长闭合文本。修正已执行：简洁直接，只给结论/路径/状态，交付物已确认后不再逐条自嗨。已保存 memory 并在本轮已实际遵守（后续回复已大幅压缩，仅保留必要结论行）。

---

aliyun CLI v3.4.11 installed and configured at /home/ubuntu/.aliyun/config.json (chmod 600). Verified working with DescribeRegions.