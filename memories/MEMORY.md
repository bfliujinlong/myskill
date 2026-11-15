用户 jinlongliu，中文沟通，上海 UTC+8。安畅 OPC+FDE（云迁移/MSP 售前+交付），用 Hermes 当生产力引擎。当前冲刺：QY-DubaiFintech 报价。

硬约束：零费用绝不花信用卡；密钥 chmod 600、不进聊天/不进 git；技术参数先查官方文档或实测再断言，不凭记忆；绝不编造人员/证书/案例（投标造假=废标）。

交付：文件发 Telegram 5701842056；"发邮件"默认 liujinlong@outlook.com；>20MB 走飞书。

风格：直接动手交付结果，不列步骤不反复确认；回复简洁中文，禁"✅已完成"式自嗨与长闭合；禁 AI 味词（赋能/抓手/闭环/一站式）；反 AI 感配色禁蓝；技术表达用表格+可执行步骤+状态符号。

售前/投标：安畅 AC-MIG $350/人天，SOW 14 章；报价迭代=基线版→对齐模板→中英双版分文件；客户名用"xx customer"匿名。

模型路由：主通道本地 litellm(:4000)→cb2openai(:4100)→CodeBuddy。Nous 免费模型全灭，OpenRouter 有日额度需节流。明细见 skill model-router。

记忆明细存档（按需读，不占每轮注入）：
- 环境台账/机器IP/路径/cron/域名 → memories/ENV-REGISTRY.md
- 历史明细 11 主题（飞书/OCI账单/dsh隧道/投标模板/项目/模型路由史等）→ skills/memory-archive/references/
- 本项目一次性细节 → memories/local/
§
本机GCP(free-ubuntu-vm, 公网35.206.98.210, 仅22端口对外)环境坑: 系统/usr/bin/python3 无PIL, 后台任务用它渲染必 ModuleNotFoundError; 须用Hermes会话python(PIL 13.0.0), 长渲染改前台分批否则被回收。codex-cli 0.166.0 已装 ~/.local/bin/codex, 空载RSS仅24.7MB(官方"4GB"是全场景值非启动门槛, 本机955MiB可跑小任务)。
§
本机静态服务坑(2026-11-02 复盘, 详见 memories/local/retro_2026-11-02_http-server-chinese-path.md): 本机IP=10.0.0.42, 8899 是 python http.server(cwd=/home/ubuntu, pid随起)。客户项目产物在 `/home/ubuntu/客户项目/泉峰/泉峰_新费率_输出/`。⚠️ 中文URL**绝不可手写百分号编码**(曾把"费"拼成"利"误判404); 一律用 `python3 -c "from urllib.parse import quote; print(quote(p,safe='/'))"` 生成。飞书 file/ 链接 fetch_file 返403, 分钟纪要 read/fetch 返401/402, 此类只能让用户本地发文件。
§
### 用户偏好与工作风格
- **直接动手交付**：
  - 用户偏好直接执行任务，不需要多次确认或解释步骤，而是直接交付结果。

- **技术表达风格**：
  - 用户偏好使用表格、可执行步骤和状态符号（✅⚠️❌）来表达技术信息，避免 AI 味的表述。

- **安全与合规**：
  - 用户强调零费用、不使用信用卡，并且严格保护密钥和敏感信息，确保不在聊天中泄露任何密码或凭证。

- **文档处理**：
  - 用户要求自行提取文档内容，不要求用户粘贴内容，确保文档内容的完整性和准确性。

- **模型与工具使用**：
  - 用户使用 Hermes 作为生产力引擎，并依赖多种技能（如 `axon-skills` 和 `run-skill-generator`）来完成任务。

- **交付方式**：
  - 用户偏好通过 Telegram 和邮件（liujinlong@outlook.com）接收大文件，超过20MB的文件通过飞书发送。

- **技术参数验证**：
  - 用户要求技术参数和配置信息先查官方文档或实测，不凭记忆断言。

- **模型路由与配置**：
  - 用户要求确保模型路由正确，支持多种模型，并验证 `/model` 端点显示正确的模型列表。
§
安畅交付模板库(已入库 workbuddy-rules/references): SOW 通用脱敏母版=sow-template-anchnet.md(14章+附录E MSP口径+红线); 填充实例=Lilly_SOW_V1.1_安畅模板.md; 生成脚本=~/build_sow_anchnet.py(安畅红C00000/黑灰禁蓝)、~/build_sow_anchnet_official.py(官方7段); 报价单版式对齐 IAC_Quotation_*.md + ~/build_aia_quotation.py(背景→范围假设→资源评估→WBS→人天表→商务→待确认, $350/人天, 中英分文件).