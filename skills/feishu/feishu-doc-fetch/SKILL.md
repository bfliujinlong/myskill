---
name: feishu-doc-fetch
description: "读飞书 wiki / docx / sheets / slides 链接并整理内容. Use when 用户发飞书文档/wiki/表格/幻灯片链接要读内容或梳理纪要."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [feishu, wiki, docx, fetch]
    related_skills: [feishu-bitable-access]
---

# 飞书文档读取（wiki / docx / sheets / slides 链接）

## When to Use

用户发飞书链接（wiki 或 docx）要读内容、梳理纪要、提取信息时按此流程，不要先问权限。

## 读取流程

1. **docx 链接**（`/docx/<doc_token>`）：直接 `mcp__feishu_mcp__fetch_doc` 传完整 URL 即可，一步到位。
2. **wiki 链接**（`/wiki/<wiki_token>`）：wiki token ≠ 文档 token，需两步：
   - 先 `fetch_doc` 传 wiki URL 或裸 token → 返回里含节点解析出的真实 `obj_token`/`doc_id`；
   - 再 `fetch_doc` 传该 obj_token 读正文。
3. **节点类型判别**：解析结果 `obj_type` 为 `box`/`Unknown` 或非 docx 类型时，MCP 代理读不了（wiki 节点可能是表格/画板/文件容器，不是文档），不是权限问题，换参重试无意义。

## 降级路径（用户规则：读不了就装对应 CLI，不要报死）

MCP 读不了的节点类型，按序试：
1. 告知用户节点类型不可读，问它实际是什么（文档/表格/思维笔记）；
2. 若是多维表格 → 走 feishu-bitable-access 技能；
3. 用户确认需要时安装对应飞书 CLI 再取——用户明确说过"如果不能读 安装对应飞书 cli"，直接动手装而不是回复做不到。

## 坑
- `web_extract` 抓飞书 wiki/docx 只会拿登录页，别浪费一轮。
- wiki 解析返回的 obj_token 可能本身也是另一个 wiki 层级，需再解析一层。

## 文件型节点（obj_type=file）—— 走 drive download，别再用 blocks

`/wiki/<token>` 或 `/file/<token>` 解析出 `obj_type=file` 时，它是上传的二进制（docx/xlsx/pdf），不是在线文档：`blocks` 类接口必返 404，重试和换参无意义。走下载接口：

```python
# 1) 拿 wiki 节点真实 token（只有 /wiki/ 链接才需要这一步）
#    GET /open-apis/wiki/v2/spaces/get_node?token=<wiki_token>
#    → data.node.obj_token 才是文件 token，data.node.obj_type 判别类型
# 2) 下载（鉴权头 Authorization: Bearer <tenant_access_token>）
#    GET /open-apis/drive/v1/files/{file_token}/download
#    → 直接是文件字节流，resp.read() 落盘成 .docx/.xlsx
```

落盘后 unzip 解包本地解析，不用装 docx/openpyxl 之外的依赖：
- docx 正文：`word/document.xml`，正则去标签（`</w:p>`→换行、`</w:tc>`→` | `）+ `html.unescape`，够读全文本
- xlsx 结构：`xl/workbook.xml` 取 sheet 名 → `xl/_rels/workbook.xml.rels` 映射 sheet xml → 逐单元格 `r/v/f/t`（`f` 是公式、`t="s"` 指向 `xl/sharedStrings.xml`）

**凭据**：`~/.hermes/.env` 的 `FEISHU_APP_ID` / `FEISHU_APP_SECRET` 换 `tenant_access_token`；值只在本机脚本内使用，绝不写进产出文件、日志或回复。

**发回给用户**：`POST /open-apis/im/v1/files`（multipart，`file_type` 用 `xls`/`docx`）拿 `file_key`，再 `POST /open-apis/im/v1/messages?receive_id_type=chat_id` 发 `msg_type=file`。≤20MB 走飞书直发，大于则改其他通道。

**坑**：
- 终端 heredoc（`cat > x.py <<'EOF'` / `python3 - <<'PY'`）写长脚本会被网关守卫拦或解析失败（实测 exit 2 且无 traceback）。用 write_file 落脚本再 `python3 脚本.py`。
- 脚本里 `src = open('/dev/stdin').read()` 这类占位写法不会报错也不干活，回显 ok 不等于生成了文件——落盘后必须 `ls -la` 验文件存在。

## Sheets（/sheets/ 链接）—— MCP 不支持，走 OpenAPI 直读 ✅

`mcp__feishu_mcp__fetch_doc` 对 sheet 同样报 `Unsupported document type`。**但 OpenAPI 能读，这是可靠路径**，三步：

```python
# 1) tenant_access_token：POST /open-apis/auth/v3/tenant_access_token/internal
#    凭据读 ~/.hermes/.env 的 FEISHU_APP_ID / FEISHU_APP_SECRET
# 2) 列子表：GET /sheets/v3/spreadsheets/{token}/sheets/query
#    → data.sheets[] 含 sheet_id / title / grid_properties.row_count / column_count
# 3) 取值：GET /sheets/v2/spreadsheets/{token}/values/{sheet_id}!A1:{末列}{末行}
#    ?valueRenderOption=ToString&dateTimeRenderOption=FormattedString
#    → data.valueRange.values 是二维数组
```

先跑 `sheets/query` 拿每个子表的行列数再拼 range——**别猜 A1:Z1000**，猜大了返回空、猜小了截断。

脚本已存 `/home/ubuntu/.hermes/cache/scratch/sheet_all.py`，改 `SHT = '<token>'` 可复用（打印全部子表、去空行、存 `sheet_all.json`）。

**坑**：
- 路径必须带 `/open-apis` 前缀，否则返回 200 的官网 HTML，看着像成功实则噪音。
- 空单元格返回 `None`，渲染前过滤 `None` 和空串，否则打印一大片 `None`。
- 多子表要逐个 sheet_id 取，没有一次拿全表的接口。
- URL 尾部 `?sheet=xxx` 只指定默认打开的子表，内容解析仍要读全部子表——用户关心的往往在别的 tab。

## Slides（/slides/ 链接）读取的坑 2026-10-27 实测

**现状：应用未开通 slides 元素级读权限，只能拿元数据，拿不到正文。** 已实测全部路径：

| 路径 | 结果 |
|---|---|
| `mcp__feishu_mcp__fetch_doc` | ❌ `[VALIDATION:1005] Unsupported document type: Unknown`，productID=sld |
| `mcp__feishu_mcp__fetch_file` | ❌ 404 |
| `docsync.py`（只支持 docx/wiki） | ❌ 不适用 |
| `GET /slides/v1/presentations/{token}` | ✅ 200，但**只有结构 ID**：slides/layouts/masters 全是字符串 ID，正文 0 字符 |
| `GET .../presentations/{token}/slides` 及逐页 elements | ❌ 404 |
| `POST /drive/v1/export_tasks`（pptx/pdf） | ✅ 返回 ticket |
| `GET /drive/v1/export_tasks/{ticket}` | ❌ 400 `token is required`，补 `?token=` 后仍 404 |
| `POST /drive/v1/metas/batch_query` | ✅ 标题/密级/创建&修改时间/owner |
| 网页抓取 / 浏览器 | ❌ 跳登录页（cloud browser 还返回 no CDP endpoint） |

**要通**：给飞书应用加 `slides:slides` 或 `slides:slides:readonly` 权限，或在飞书里手动导出 PPTX 丢本地路径再读。

**踩坑**：
- 飞书 OpenAPI 必须带 `/open-apis` 前缀，否则返回 200 的官网 HTML，看着像成功实则噪音。
- 终端 heredoc（`cat > x.py <<'EOF'`）会被网关守卫误判为重启命令拦下，改用 write_file。
- 写脚本别漏 `import os`（`Path.expanduser` 依赖它）。
- 纪要整理类任务：读全正文后按"基本信息/核心问题按人归类/分工/决策/待办按归属"结构输出，待办要标到具体人。

## 权限类读失败（401 / 402 / 403）—— 不是参数错，是没权限，别换参重试

| 对象 | 接口 | 结果 | 处置 |
|---|---|---|---|
| `file/<token>` 上传文件链接 | `mcp__feishu_mcp__fetch_file` | ❌ 403（无下载权限） | 让用户本地下载后发本地路径或贴内容；换 token / 换参重试无意义 |
| 智能纪要（minutes）链接 | `feishu_doc_read` / `fetch_doc` | ❌ 401 / 402 | 同上，只能用户本地取 |
| `/docx/<token>` 在线文档 | `fetch_doc` 传完整 URL | ✅ 通常可用 | 优先路径 |

**判定原则**：403/401/402 是鉴权/权限层拒绝，不是节点类型或参数错误——反复换 token、换接口、重排参数都拿不到，直接转人工（用户本地下载）。只有 `404` 才可能是节点类型不对（见上文件型/slides 段），需先判别 obj_type。
