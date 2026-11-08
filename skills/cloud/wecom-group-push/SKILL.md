---
name: wecom-group-push
description: Use when 把告警/通知推到企业微信群. 群机器人Webhook选型/@人身份陷阱/频率限制/纯标准库中继脚本.
---

# 企业微信群消息推送

## 何时用
- 用户要把监控告警（P0/P1…）、值班通知、自动化结果推到企业微信群。
- 用户发来企业微信开发者文档链接：`doc_id=21661`（智能机器人长连接）、`document/path/91770`（消息推送/群机器人）。
- 关键词：企业微信、企微群、群机器人、webhook、告警推群。

## 两条技术路线（先选型再动手）

| 路线 | 官方文档 | 适用 | 网络 | 凭证 | 推荐 |
|---|---|---|---|---|---|
| A. 群机器人 Webhook（现名"消息推送"） | developer.work.weixin.qq.com/document/path/91770 | 单向推消息到群 | 全出站 HTTPS，无需公网 IP | 1 个 webhook key | ⭐ 默认首选 |
| B. 智能机器人（长连接） | open.work.weixin.qq.com/help2/pc/cat?doc_id=21661 | 双向（收群消息+交互应答） | 长连接出站，无需公网 IP | Bot ID + Secret | 仅二期需要交互时 |

**判定规则**：只要目标是"把 X 推到群"，一律走 A。B 的收消息/长连接能力对单向推送是过剩的，接入更重（需在管理后台建智能机器人 + 配长连接/API 模式）。

## 实施步骤（路线 A）

1. **取 webhook key**：企业微信客户端 → 目标群 → 添加群机器人 → 消息推送 → 复制 Webhook 地址，取 `?key=` 后面那段。
   - 安全：key 等同发消息权限，一律 [REDACTED]，不进聊天/不进 git/不写死代码。
2. **跑中继脚本**：纯 Python 标准库（见 `scripts/wecom_webhook_relay.py`），只出站访问 `qyapi.weixin.qq.com`，不监听公网端口 → 不需要公网 IP、不需要安全组开入站。
3. **接监控源**：Alertmanager `webhook_configs` 指向中继；或阿里云监控/CloudWatch 转发；或 cron 健康检查直接调 `send_*()`。
4. **验真**：脚本自带 `--test` 发一条示例卡片到群，确认 @人 生效。
5. **固化**：中继做成 systemd / K8s Deployment + 存活探针。

## 消息类型与字段（官方已核对）

- `msgtype` 支持：text / markdown / markdown_v2 / image / news / file / template_card 等共 8 种。
- **@人**：markdown 用 `<@userid>`；text 用 `mentioned_list: ["userid"]` 或 `mentioned_mobile_list: ["138xxxx"]`。
- markdown 颜色：`<font color="info">`(绿) / `comment`(灰) / `warning`(橙红)。P0 用 `warning`。
- template_card 文本通知型：`card_type: "text_notice"`，字段 `source / main_title / emphasis_content / sub_title_text / horizontal_content_list / card_action`。

## ⚠️ 关键陷阱：@人身份体系不互通

- **企业微信 userid ≠ 飞书 open_id**。用户常从飞书 @人 把 open_id（形如 `ou_xxx`）直接拿来填企微 `@` —— 无效，消息不会艾特到人。
- 企微 @人 必须填**企业微信的 userid**（或手机号）。实施前必须向用户索取目标成员的企微 userid / 手机号，并在方案里显式标注此缺口。
- 不要假设飞书 open_id 可跨平台使用；两套体系完全独立。

## 频率限制

- 群机器人：约 **20 条/分钟**。P0 量级内无需限流，但中继应做按指纹去重（建议 10 分钟 TTL）防告警风暴刷屏。

## 安全红线

- webhook key 属凭证，[REDACTED]，存运维保密库；脚本只读环境变量 `WECOM_WEBHOOK_KEY`。
- 中继不出公网、不暴露端口；仅 `qyapi.weixin.qq.com` 出站白名单。
