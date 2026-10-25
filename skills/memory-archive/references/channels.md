微信通道: Hermes支持Weixin个人号走iLink bot(o9cq80-...@im.wechat), DM可用且能收语音文件, 群聊不通. 用户选'微信文字+长回复自动附语音'(weixin-voice)而非切Telegram. 微信收不到语音输入, 双向语音须走Telegram. 用户微信实测发过医院CTA报告(双肺栓塞, 产后高危), medical-advisor用.

---

邮件通知默认收件人固定为 liujinlong@outlook.com（发件人走 vliujinlong@qq.com 代发，因个人版outlook基础认证被禁）。用户指令："以后说发邮件给我都是发到liujinlong@outlook.com"。EMAIL_HOME_ADDRESS 已设此值。

---

Hermes email adapter 已配但网关未重启加载: .env 写了EMAIL_ADDRESS=vliujinlong@qq.com(QQ代发, 因个人版outlook基础认证被微软禁用连不上), EMAIL_SMTP/IMAP=qq.com:587/993, EMAIL_HOME_ADDRESS=liujinlong@outlook.com, EMAIL_ALLOWED_USERS=两个邮箱. SMTP外发已实测通(发往outlook成功). 但IMAP收信轮询(adapter)需重启网关才加载——重启须在本机独立SSH终端跑 systemctl --user restart hermes-gateway.service(当前gateway会话内不能自重启, 被护栏拦).

---

用户新确认的偏好：给客户/合作方发问时，要整理成单封邮件模板让_users直接复制粘贴，不要散碎问题。币种默认USD。

---

Telegram发文件正确方式: 从.env加载TELEGRAM_BOT_TOKEN(不是上下文里的token, 两者后缀不同), 用sendDocument端点. 直接curl用上下文token会401.