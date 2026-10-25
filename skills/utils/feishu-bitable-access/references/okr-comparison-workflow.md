# OKR 对比与补列工作流

## 场景
用户要对比两周飞书 OKR 表（电子表格类型），找出本周新增完成的 OKR ID（B列），填写 G 列（最终交付结论），并在右侧加 H 列（专业英文翻译）。

## 前置条件
- 应用 `cli_aaeb0ff8aa381cb3` 已开通 `sheets:spreadsheet` 权限并发布
- 应用已被加为两个表格的协作者
- 用 anchnet 凭证（`~/.feishu/anchnet_credentials.json`）

## 工作流

### Step 1: 读两张表
```python
import json, requests
c = json.load(open('/home/ubuntu/.feishu/anchnet_credentials.json'))
tk = requests.post('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
                   json={'app_id': c['app_id'], 'app_secret': c['app_secret']}, timeout=15).json()['tenant_access_token']
h = {'Authorization': f'Bearer {tk}', 'Content-Type': 'application/json'}

# 上周
lw = requests.get('https://open.feishu.cn/open-apis/sheets/v3/spreadsheets/Vj3QshA9KhGYe8to7mjchXFUn7D/values/D7dkp8!A1:H122',
                  headers=h, params={'valueRenderOption': 'ToString'}).json()
# 本周
tw = requests.get('https://open.feishu.cn/open-apis/sheets/v3/spreadsheets/Hdb0sNajyhTIWEte4sFcZmt4nEd/values/D7dkp8!A1:H122',
                  headers=h, params={'valueRenderOption': 'ToString'}).json()
```

### Step 2: 对比找新增完成
- 解析 B 列（OKR ID）和 F 列（状态/完成标志）
- 找出本周状态变为"完成"但上周不是"完成"的行
- 提取这些行的 OKR ID

### Step 3: 生成 G 列内容
对每个新增完成的 OKR:
- 根据 C 列（Key Result）和 D 列（Expected Outcome）生成"最终交付结论"
- 格式:"完成了[KR]，交付了[具体成果]，解决了[问题]"

### Step 4: 生成 H 列（专业英文）
- 把 G 列中文翻译成专业英文
- 用词参考:Delivered/Implemented/Achieved/Resolved

### Step 5: 写回飞书
```python
# 补 G 列
requests.put(f'https://open.feishu.cn/open-apis/sheets/v3/spreadsheets/{sheet_token}/values/{sheet_id}!G{row}:G{row}',
             headers=h, json={'values': [[g_col_content]]})

# 加 H 列(先新增列)
requests.post(f'https://open.feishu.cn/open-apis/sheets/v3/spreadsheets/{sheet_token}/columns',
              headers=h, json={'title': '专业英文'})
```

## 已知表结构(BOSE FY27 OKR)
- A: Objective
- B: SEQ(OKR ID)
- C: Key Result
- D: Expected Outcome
- E: TASK
- F: 状态/完成标志
- G: 最终交付结论(待填)
- H: 专业英文(待加)

## 降级方案
如果权限不通(99991672)或未加协作者(1310213):
1. 让用户导出两份 Excel
2. 本地 Python 对比分析
3. 生成填写内容让用户粘回
