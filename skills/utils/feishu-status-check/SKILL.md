---
name: feishu-status-check
category: utils
description: Check Feishu workspace status
dependency: Feishu App ID
dependency: Feishu App Secret
usage: Use as a cron job
---
# Feishu Status Check / Doc Reader

## Description

用 Feishu 自建应用的 App ID + App Secret 检查 Feishu 工作区状态，或**读取飞书文档/表格内容**（用于售前报价、迁移需求表等场景）。

## Usage

可作为 cron job，也可按需手动调用来拉取飞书文档。

## Dependencies

- Feishu App ID（形如 `cli_xxxx`）
- Feishu App Secret
- （读取文档时）应用需开通对应 scope 并**重新发布版本**

## 凭证存放（安全）

存到 `~/.feishu/credentials.json`（600 权限），**绝不进聊天明文**：
```json
{ "app_id": "cli_xxxx", "app_secret": "xxxxxxxx" }
```

## 换 tenant_access_token（已验证可用）

```bash
APPID=$(python3 -c "import json;print(json.load(open('/home/ubuntu/.feishu/credentials.json'))['app_id'])")
APPSEC=$(python3 -c "import json;print(json.load(open('/home/ubuntu/.feishu/credentials.json'))['app_secret'])")
TOK=$(curl -s -X POST https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal \
  -H "Content-Type: application/json" \
  -d "{\"app_id\":\"$APPID\",\"app_secret\":\"$APPSEC\"}" \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['tenant_access_token'])")
```
- 法兰克福 OCI 机器连 `open.feishu.cn` 正常（~2s），网络不是问题。
- token 42 位，有效期约 2 小时，按需现换。

## 读取文档/表格需要的 scope（开通后必须「版本管理与发布」→ 重新发布才生效）

| 文档类型 | 需要的 scope |
|---|---|
| Wiki 文档 | `wiki:wiki:readonly` + `wiki:node:read` |
| 新版文档(docx) | `docx:document:readonly` |
| 在线表格/电子表格 | `sheets:spreadsheet:readonly` |
| 多维表格 | `bitable:readonly` |
| 云文档文件 | `drive:drive:readonly` |

读取示例：
```bash
curl -s "https://open.feishu.cn/open-apis/wiki/v2/spaces/get_node?token=<wiki_token>" \
  -H "Authorization: Bearer $TOK"
```

## ⚠️ 关键坑：跨企业读不了

飞书文档分**企业空间**。如果文档在 `anchnet.feishu.cn`（安畅企业），而自建应用是**个人飞书或其他企业**建的 → 调 API 返回 `Access denied / 需 xxx scope`（即使 scope 开了也读不了），因为**跨企业隔离**。

→ 应用必须建在**文档所属企业**下（用该企业账号登录 open.feishu.cn 建应用），且文档授权给该应用。

**实战结论**：想读安畅企业文档，最稳的还是让用户在飞书里**导出文件**（Word/Excel/PDF）再用上传页拖过来，绕开跨企业权限问题。本机上传页：`https://<cloudflared域名>/upload.html`（见 dsh 隧道）。

## 推送通道（本机已验证）

飞书渠道 webhook 需公网入口 + Encrypt Key/Verification Token；但若只是**从 Hermes 发消息给用户**，用：
```
hermes send -t telegram:5701842056 "消息内容"
```
复用 Hermes 已配 Telegram 凭证，无需自建 bot token。格式是 `platform:chatid`（不是裸 chatid）。

## Notes

- 应用创建：open.feishu.cn → 开发者后台 → 创建企业自建应用。
- 权限开通后**必须重新发布版本**，否则 scope 不生效。
- 开发态只能开发者自己测，发布后才能正常收消息/被授权。