---
name: agent-doc-access
description: >-
  给子 agent/架构师接飞书钉钉文档：docsync 一条命令把云文档拉成本地 md 再读文件。
---

# 子 agent 文档接入（飞书 / 钉钉）

## 为什么这么做

子 agent 的工具箱**不包含钉钉 MCP**，飞书 MCP 也不保证每个子 agent 都能拿到
（实测：子 agent 只有 `feishu_doc_read` / `feishu_drive_*`，`dingtalk-*` 一个都没有）。

但子 agent **一定有 terminal**，而 `dws` CLI 在 terminal 里可直接调用。
所以正确做法不是"给权限"，而是**把文档拉成本地文件，让 agent 读文件**——这条路 100% 通。

## docsync 用法

脚本：`/home/ubuntu/.hermes/scripts/docsync.py`
解释器：`/home/ubuntu/.hermes/hermes-install/venv/bin/python3`（脚本只用标准库，系统 python3 也行）

```bash
PY=/home/ubuntu/.hermes/hermes-install/venv/bin/python3

# 飞书 docx（URL 或裸 token 都行）
$PY /home/ubuntu/.hermes/scripts/docsync.py feishu "https://anchnet.feishu.cn/docx/ZyJfduBNqop8LCx71ZYcgPw8n3g"

# 飞书 wiki（自动解析 obj_token，两步合一）
$PY /home/ubuntu/.hermes/scripts/docsync.py feishu "https://anchnet.feishu.cn/wiki/V4hSwWkUFiyzeek7hDjcTDbznnc"

# 钉钉（--node 传 id 或完整 URL）
$PY /home/ubuntu/.hermes/scripts/docsync.py dingtalk "N7dx2rn0JbgqEwqPtb3pdZDN8MGjLRb3"

# 列目录
$PY /home/ubuntu/.hermes/scripts/docsync.py list feishu

# 指定输出
$PY /home/ubuntu/.hermes/scripts/docsync.py feishu <url> -o /tmp/sow.md
```

输出默认落 `~/cloud-docs/_inbox/<platform>-<id>.md`，打印路径和字符数。

## 给子 agent 的 prompt 模板

派活时把这段塞进 context：

> 你要读的文档已由父 agent 抓取到本地，直接用 read_file 读：
> - `~/cloud-docs/_inbox/feishu-GVvDdE0mfoZ6t8x5cY0cNhghnbd.md`（MSP_Migration_SOW_CN_V1.0）
> - `~/cloud-docs/_inbox/dingtalk-N7dx2rn0JbgqEwqPtb3pdZDN8MGjLRb3.md`（欧姆龙 KO 会纪要）
>
> 需要新文档时自己跑：
> `/home/ubuntu/.hermes/hermes-install/venv/bin/python3 /home/ubuntu/.hermes/scripts/docsync.py feishu <url>`
> 钉钉同理把 `feishu` 换 `dingtalk`。不要指望 MCP 工具，你没有。

## 平台能力现状（2026-10-26 实测）

| 通道 | 子 agent 直接可用 | 走 docsync | 备注 |
|---|---|---|---|
| 飞书 | 部分（feishu_doc_read 能拿到） | ✅ | 父会话有 10 个 MCP 工具；凭据走 `~/.hermes/.env` 的 FEISHU_APP_ID/SECRET |
| 钉钉 | ❌ 无 MCP | ✅ | 走 `dws` CLI，已认证（金龙@上海安畅） |
| 企业微信 | ❌ | ❌ | **从未接入**：插件目录存在但 `platforms.wecom` 配置为空，需 corp_id/agent_id/secret，用户后台操作 |
| 微信 | ❌ | ❌ | iLink bot，仅个人 DM，不进群 |

## 飞书电子表格（sheets）读取

`docsync.py` 不覆盖电子表格。用 `lark-cli`（在 `/home/ubuntu/.npm-global/bin`，需 export PATH）：

```bash
export PATH=$PATH:/home/ubuntu/.npm-global/bin
TOK=<spreadsheet_token>            # URL /sheets/ 后第一段
lark-cli sheets +csv-get --spreadsheet-token "$TOK" --sheet-id <sheet_id> --range "A1:U80" > /tmp/<sheet_id>.json 2>&1
```

返回 JSON，正文在 `d["data"]["annotated_csv"]`，每行形如 `[row=N] 单元格,单元格,...`——按 `'] '` 切一次取后半段即为正文。

```bash
python3 -c "
import json
d=json.load(open('/tmp/<sheet_id>.json'))
for line in d['data']['annotated_csv'].split('\n'):
    if '] ' not in line: continue
    body=line.split('] ',1)[1]
    if body.strip(', '): print(line.split(']')[0]+']', body[:300])
" > /tmp/<sheet_id>.txt 2>&1
```

然后 `read_file /tmp/<sheet_id>.txt`。

- 一个 spreadsheet 有多个子表，`sheet_id` 是 URL `#` 后那段；逐个 `+csv-get` 落不同文件。
- `+sheet-list` 不可靠（常返回空），**不要依赖它枚举子表**，用 URL 里的 sheet_id。
- 单元格含逗号会被引号包裹，直接按 `,` split 会切错；要分列就用 csv 模块，否则只取前几列。
- 表格分享密码属凭证，一律 [REDACTED]，不进 skill/记忆/交付文档。

## 飞书云盘文件（`/file/`）下载

`docsync.py` 与 `sheets +csv-get` 都**不覆盖 `/file/` 云盘文件**（docx/wiki/sheets 之外的裸文件，如 xlsx、pdf）。
对 `https://anchnet.feishu.cn/file/<token>` 跑 `docsync` 会失败——别浪费时间重试，直接走 `lark-cli drive +download`：

```bash
export PATH=$PATH:/home/ubuntu/.npm-global/bin
TOK=<file_token>            # URL /file/ 后第一段
lark-cli drive +inspect --url "https://anchnet.feishu.cn/file/$TOK"   # 可选：确认文件信息
lark-cli drive +download --file-token "$TOK" --output "/home/ubuntu/<name>.xlsx" --overwrite
```

下载后 xlsx 用 `openpyxl`：`wb=openpyxl.load_workbook(path, data_only=True)`，`wb.sheetnames` 看子表。
非空单元格多时先整表导出到 `/home/ubuntu/_<name>_dump.txt` 再 `read_file`，别靠 stdout。
需比对两列时把差异也单独落盘（如 `_diff.txt`）再读。

- URL 形式判路由：`/docx/`→docsync、`/wiki/`→docsync、`/sheets/`→`sheets +csv-get`、`/file/`→`drive +download`。

## 踩过的坑

- 钉钉 `dws doc list` 已废弃 → 用 `dws drive list --workspace <id>` 或 `dws wiki node list`。
- `dws doc read` 必须带 `--node`，裸 id 会被拒（`flag --node is required`）。
- dws 返回 JSON，正文在 **`markdown` 字段**，`content` 常为空——只取 content 会得到空文件。
- 飞书 wiki token ≠ docx token，必须先用 `/wiki/v2/spaces/get_node` 换 `obj_token`。
- 文件名别塞整个 URL（含 `//` 会被当路径），只取 id 或 md5 前 8 位。
- 飞书 `/docx/v1/documents/{id}/blocks` 默认 page_size 500，超长文档要翻页——当前未实现翻页，长文档会截断。
- **terminal 的 stdout 会被吞**：命令后接 `| head` 或让 python 直接打印，高频只回 `exit 0` + 1 行。一律**先落盘再 `read_file`**，不要用 stdout 判断成败。
- **落盘成功 ≠ 拿到了内容**：`ls -la` 看到文件不等于里面有数据，必须 `read_file` 解析出正文后再下结论。禁止基于不可见输出断言「读成功了 / 清单已确认」——实际可能一行都没输出。
- **长分析跨上下文压缩时，中间结论必须写入具名磁盘文件再 `read_file` 回读**：`execute_code` 的输出正文和对话上下文会在压缩后丢失（只剩「1 lines output」），只有磁盘文件能续做。每完成一步就把结构化结果 append 到固定文件，别指望工具输出留在上下文里。

## 权限边界

飞书报错 `99991672` / `230002` 是**应用身份权限+发布版本+bot 进群**三重锁，
属用户 UI 操作，agent 替不了。文档抓不到时先确认 bot 是否在文档所在群/知识库。
