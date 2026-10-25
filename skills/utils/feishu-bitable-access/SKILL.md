---
name: feishu-bitable-access
description: "读写飞书 wiki 多维表格与对比。触发: 对比飞书上周本周表 / 补G列 / 飞书表读写."
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [飞书, feishu, 多维表格, bitable, wiki, OKR, 对比]
    related_skills: [fde-client-discovery-questions, productivity/tender-docx-assembly]
---

# 飞书 Wiki 多维表格 读写

## When to Use
- 用户发来 `anchnet.feishu.cn/wiki/<token>?sheet=...` 或类似飞书多维表格链接,要求读/对比/写
- 任务如:对比上周与本周 OKR 表、补 G 列交付结论、右侧加英文列、复制创建副本并更新
- 任何需要把飞书表数据拉到本地处理再写回的场景

## 关键事实(本用户环境)
- 表格在 **anchnet 租户**,用 `~/.feishu/anchnet_credentials.json`(app_id=`cli_aaeb0ff8aa381cb3`)
- 主应用 `~/.feishu/credentials.json`(cli_aa093013dc38dcbb)通常无权读 anchnet 空间表 → 用 anchnet creds
- wiki token 在 URL `/wiki/<TOKEN>` 之后(`?sheet=` 前那段)

## 可靠做法:用 raw OpenAPI,别用 lark_oapi 的 wiki node API
`lark_oapi` SDK 的 `client.wiki.v2.space_node` 没有 `.get()` 方法(Space Node resource 只有 list/create/copy/move),且 `GetNodeSpaceRequest` 无法经 resource 调用。直接用 `requests` + `tenant_access_token` 最稳:

```python
import json, requests
c = json.load(open('/home/ubuntu/.feishu/anchnet_credentials.json'))
tk = requests.post("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
                   json={"app_id": c['app_id'], "app_secret": c['app_secret']}, timeout=15).json()['tenant_access_token']
h = {"Authorization": f"Bearer {tk}", "Content-Type": "application/json"}

# 1) wiki token -> 真实 bitable app_token
wiki_tok = "F3Y6w2PGOiyc1MkMpDlcBcnQnrh"   # 从 URL 提取
node = requests.get(f"https://open.feishu.cn/open-apis/wiki/v2/spaces/get_node?token={wiki_tok}&obj_type=bitable", headers=h, timeout=15).json()['data']['node']
app_token = node['obj_token']

# 2) 列 tables
tbls = requests.get(f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables", headers=h).json()
# tbls['data']['items'] -> [{name, table_id}]

# 3) 读记录(view/sheet 由 table_id 决定; URL 的 ?sheet= 对应某个 table_id)
tid = "<table_id>"
recs = requests.get(f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{tid}/records?page_size=100", headers=h).json()

# 4) 写回(补 G 列 / 加英文列)
#    更新单元格:
requests.put(f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{tid}/records/{record_id}",
             headers=h, json={"fields": {"G列字段名": "最终交付结论..."}})
#    新增一列(英文):
requests.post(f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{tid}/fields",
              headers=h, json={"field_name": "专业英文", "type": 1})  # type=1 文本
```

## 电子表格(Spreadsheet)读写

飞书表格分两种:**多维表格**(bitable,URL 含 `/wiki/`+`?sheet=`)和**电子表格**(spreadsheet,URL 含 `/sheets/`或标题含"OKR""工时"等)。两者 API 完全不同。

### ⚠️ 判断方法
- URL 含 `/sheets/` → 电子表格(spreadsheet)
- URL 含 `/wiki/`+`?sheet=` → 多维表格(bitable)
- wiki node 返回 `obj_type: "sheet"` → 电子表格;`obj_type: "bitable"` → 多维表格
- 标题含"OKR""工时""报价"等 → 通常是电子表格

### 电子表格 API 路径
```python
# 查询 sheet 信息(获取 sheet_id)
GET /sheets/v3/spreadsheets/{sheet_token}/sheets/query
# 返回: items[].sheet_id (注意是 sheet_id,不是 sheetId)

# 读单元格值
GET /sheets/v3/spreadsheets/{sheet_token}/values/{sheet_id}!A1:T122
# 注意: 用 sheet_id,不是 sheet name; 返回 404 通常是缺 sheets:spreadsheet 权限
```

### ⚠️ 电子表格权限要求
- 读:`sheets:spreadsheet`(电子表格只读)
- 写:`sheets:spreadsheet`(电子表格读写)
- 多维表格权限(`bitable:app`)对电子表格**无效**——这是两个独立的权限体系
- 应用还需被加为表格协作者,否则报 `1310213 No view permission`
- 开通链接: `https://open.feishu.cn/app/cli_aaeb0ff8aa381cb3/auth?q=sheets:spreadsheet`

### ⚠️ 已知 OKR 表格(电子表格类型)
- 上周: wiki=`F3Y6w2PGOiyc1MkMpDlcBcnQnrh`, obj_token=`Vj3QshA9KhGYe8to7mjchXFUn7D`, sheet_id=`D7dkp8`(最终版-Walter Input-20260629)
- 本周: wiki=`Ns9Lwo66CibxAVkapJicybf4nOf`, obj_token=`Hdb0sNajyhTIWEte4sFcZmt4nEd`, sheet_id=`D7dkp8`(最终版-Walter Input-20260629)
- 两者都是电子表格(spreadsheet),不是多维表格。读写必须走 `/sheets/v3/` API + `sheets:spreadsheet` 权限。

### ⚠️ 其他内部系统(腾讯会议/AICC/明道)
- **腾讯会议录制**(`meeting.tencent.com/crm/...`):需扫码登录,headless 浏览器无法自动登录。降级:用户下载 MP4 发给 agent,或口述要点
- **AICC 平台**(`8.153.148.69`):需账号密码,无 API。只能浏览器登录后操作
- **明道**(`mingdao.anchnet.com`):支持飞书登录/手机号+密码。headless 脚本 cookie 不持久,每次回到登录页。降级:导出 Excel
- **通用原则**:内部系统无 API + 需登录 → 别反复试密码/扫码,直接让用户导出数据或口述关键信息

## ⚠️ 硬前置:应用权限(不开通=Access denied 99991672)
必须在飞书开发者后台给 `cli_aaeb0ff8aa381cb3` 开通**应用身份权限**并**发布版本**:
- 读:`wiki:wiki:readonly`(或 `wiki:wiki`)、`wiki:node:read`、`bitable:app:readonly`
- 写(补列/加列):`bitable:app`
- 直达开通链接(报错里会给):
  `https://open.feishu.cn/app/cli_aaeb0ff8aa381cb3/auth?q=wiki:wiki,wiki:wiki:readonly,wiki:node:read`
  `https://open.feishu.cn/app/cli_aaeb0ff8aa381cb3/auth?q=bitable:app,bitable:app:readonly`

## 飞书 MCP 文档与表格的权限验证与操作

飞书官方提供远程 MCP 服务 `https://mcp.feishu.cn/mcp`(TAT 鉴权),但 Hermes 原生 MCP client 只支持 stdio 和 HTTP transport,没有"远程 MCP 代理"模式。最稳方案:**本地跑一个 stdio 脚本,脚本内部把 JSON-RPC 调用转发到远程 MCP**。

```python
# scripts/feishu_mcp_server.py
import json, time, httpx
MCP_URL = "https://mcp.feishu.cn/mcp"

def get_tat():
    creds = json.loads(Path('/home/ubuntu/.feishu/credentials.json').read_text())
    r = httpx.post('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
        json={'app_id': creds['app_id'], 'app_secret': creds['app_secret']})
    return r.json()['tenant_access_token']

def remote_call(method, params=None):
    tat = get_tat()
    payload = {'jsonrpc':'2.0','id':int(time.time()*1000)%1000000,'method':method}
    if params: payload['params'] = params
    r = httpx.post(MCP_URL, headers={
        'X-Lark-MCP-TAT': tat,
        'X-Lark-MCP-Allowed-Tools': 'search-doc,fetch-doc,create-doc,update-doc,list-docs,get-comments,add-comments,search-user,get-user,fetch-file',
        'Content-Type':'application/json',
        'Accept':'application/json, text/event-stream',
    }, json=payload, timeout=120)
    text = r.text.strip()
    if text.startswith('data:'):
        for line in text.split('\n'):
            if line.strip().startswith('data:'):
                text = line.strip()[5:].strip()
                break
    return json.loads(text).get('result',{})
```

**加到 config.yaml**:
```yaml
mcp_servers:
  feishu-mcp:
    command: /home/ubuntu/.hermes/hermes-install/venv/bin/python3
    args: [/home/ubuntu/.hermes/scripts/feishu_mcp_server.py]
    timeout: 120
    connect_timeout: 60
```

**可用工具(重启网关后自动注册)**: `search-doc`, `fetch-doc`, `create-doc`, `update-doc`, `list-docs`, `get-comments`, `add-comments`, `search-user`, `get-user`, `fetch-file`。

## ⚠️ 限制：MCP 的 fetch-file 限 5MB；不支持电子表格(spreadsheet)读写(只能读 doc/docx/wiki)。
8. **飞书 MCP 已部署并验证可用(2026-09-07)**：网关加载后 `feishu-mcp` 子进程(PID 视启动而定)作为 stdio 代理跑在网关树下,10 个工具自动注册为 `mcp__feishu_mcp__<tool>`: `search-doc`/`fetch-doc`/`create-doc`/`update-doc`/`list-docs`/`get-comments`/`add-comments`/`search-user`/`get-user`/`fetch-file`。MCP 进程会在网关启动时拉起,随网关重启而重建。
9. **明道(Mingdao)走飞书扫码登录**：明道支持"飞书登录"按钮→跳转 `accounts.feishu.cn`→用户扫 QR→回明道。但 headless 脚本每次开新浏览器会丢 cookie,**扫一次下次脚本又回到登录页**。解法:① 用 `browser_exec` 浏览器工具在同一会话内保持登录态,扫一次后立刻在同一 `session` 内跳转读数据;② 或让用户导出 Excel。
10. **vision_analyze 在免费模型(longcat/hy3)下无法看到截图**:截了图发给 vision 会回"I don't see any image attached"。降级:Tesseract OCR(验证码效果差)、PaddleOCR(ARM 上 segfault)。**唯一可靠方式=人眼读码**——用户看一眼比任何 OCR 都快。
1. **只勾选权限不发布=不生效**。开通后必须:开发者后台 → 该应用 → 版本管理与发布 → 创建版本 → 发布。否则 API 仍返回 `99991672 Access denied`。
2. **权限类型错**:报错要的是"应用身份权限(tenant)",不是用户授权/OAuth。在"权限管理→应用身份权限"里勾。
3. **开错应用**:表格在 anchnet 租户,必须用 `cli_aaeb0ff8aa381cb3` 的凭证与权限,主应用 `cli_aa093013dc38dcbb` 会 `forbidden`。
4. **字段名要用中文真名**(如"最终交付结论"),不是列字母 G。先读一条记录看 `fields` 的 key。
5. **电子表格≠多维表格**:URL 含 `/sheets/` 的是电子表格(spreadsheet),含 `/wiki/`+`?sheet=` 的是多维表格(bitable)。电子表格读写需 `sheets:spreadsheet` 权限,多维表格需 `bitable:app`。两者 API 路径完全不同。
6. **应用未加协作者=400 No view permission**:即使应用有权限,表格本身也必须把应用加为协作者(表格→分享→添加应用)。两个应用在各自的租户都无协作者身份时,读电子表格会返回 `{"code":1310213,"msg":"No view permission"}`。降级方案:用户导出 CSV/Excel 发我处理。
7. **飞书 MCP 不支持电子表格**:飞书官方 MCP 只支持文档/知识库操作(`search-doc`/`fetch-doc`等),不支持电子表格(spreadsheet)读写。电子表格数据仍需走 raw OpenAPI + 应用权限。

## 降级路径:用户导出

当应用权限不通(99991672)或表格未加应用协作者(1310213)时,别反复重试。让用户:
1. **飞书表格**:右上角 → 导出 → Excel/CSV
2. **明道/内部系统**:菜单 → 导出 Excel/CSV

收文件后用 Python 本地分析(对比/补列/英文化),交付成品让用户手动粘回。空转 API 比让用户点几下慢得多。

**例外**:图片验证码。浏览器能到登录页但 CAPTCHA 拦住时,Tesseract/PaddleOCR 通常读不出(PaddleOCR 在 ARM 上会 segfault)。别循环 OCR,直接让用户读一下验证码发过来(比导出还快)。

## 验证步骤(动手前必做)
先跑上面的"列 tables"片段,若返回 `code=0` 且有 items → 权限已通,直接干;若 `99991672` → 停,让用户去后台开权限并发布,别空转。
