---
name: spreadsheet-delivery
description: "生成 Excel/表格类交付物（报价单、工作量预估、Landing Zone 清单等），严格克隆用户提供的 xlsx 模板——字体/颜色/合并单元格/列宽/公式 100% 继承。触发词：报价单、xlsx、按模板、生成表格、工作量预估、人天拆解、客户模板。"
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [excel, xlsx, 报价单, 模板克隆, 交付物, 人天, 售前]
    related_skills: [solution-delivery, presales-architect, roles-finance]
---

# 表格交付物工程师（Spreadsheet Delivery）

把"出报价单 / 工作量预估 / 资源清单"标准化产出 **.xlsx 文件**，且**严格克隆用户模板格式**。

## When to Use
- 用户发来一个 xlsx 模板说"按这个格式出一份报价单/清单"
- 用户要求"按我的模板""格式一致""字体颜色要对"
- 售前报价（LZ / Migration / Ops / 客户定制模板）、工作量人天拆解（WBS）
- **中东（迪拜）客户报价 / 人天评估**：说"出中东报价""按 Fintech 模板出中东报价（中英文）""出中东人天评估报告（A/B/C 三档）"即触发 —— 见 `references/me-quotation-workflow.md`（已固化模板路径、三档人天、OA WBS 结构、Scope 数据源、发件 chat，直接照做无需重探）

## 核心铁律（用户多次纠正后总结，务必遵守）

### 0. 输出风格：不要 AI 感、不要废话（用户反复强调）
- 用户原话：「说了几次了 不要ai感太强」「不要废话，我要解决我的问题」。
- 交付物（xlsx/docx）**内容要专业、克制**，不写"您好！已为您生成..."之类客套；文件本身说清即可。
- 聊天回复：**极简、直接给结果/文件路径**，不铺陈解释、不分点自嗨、不"✅已完成"式汇报。任务做完发交付物即止。
- 报错/卡点才多说；顺利时一句话带过。

### 1. 复制模板文件，只改单元格值 —— 绝不新建 workbook 自配样式
```python
import shutil, openpyxl
shutil.copyfile(USER_TEMPLATE, OUT)          # 先复制，保留所有格式
wb = openpyxl.load_workbook(OUT)
ws = wb["Sheet名"]
ws["D5"] = "新客户名"                         # 只改值
ws["G16"] = 8000                             # 只改值
wb.save(OUT)
```
新建 `Workbook()` + 自己设 `PatternFill`/`Font(Calibri)` 会被用户打回——模板是 Arial Unicode MS 22号标题、合并单元格、红色批注字，这些**只有复制文件才能继承**。

### 2. 不要插入/删除行改结构
默认只覆盖现有数据行的值（保留原行样式/合并/公式）。**只有用户明确说"拆人天/加一行"时才插行**，插行用 `copy_row_style()` 复制相邻行样式：
```python
import copy
def copy_row_style(src_ws, sr, dst_ws, dr):
    for c in range(1, dst_ws.max_column+1):
        s = src_ws.cell(sr,c)
        if s.has_style: dst_ws.cell(dr,c)._style = copy.copy(s._style)
ws.insert_rows(18)
copy_row_style(ws, 17, ws, 18)
```
⚠️ **MergedCell 写值报错（本会话反复踩坑）**：模板常有合并单元格（如 `B14:B15`、`B16` 属于合并区）。直接 `ws["B16"]="x"` 会抛 `AttributeError: 'MergedCell' object attribute 'value' is read-only`。
**修复**：写值前先批量取消相关行合并（用 `merged_cells.ranges` 遍历，不要用 `coord in ws.merged_cells` 判断，它对合并区不生效）：
```python
for mr in list(ws.merged_cells.ranges):
    if mr.min_row >= 14 and mr.max_row <= 30:   # 只动数据区
        ws.unmerge_cells(str(mr))
# 之后再 ws.cell(r,c).value = ... 写值
```
新增 Sheet 用 `wb.copy_worksheet(src)` 则无此问题（整表复制已含合并）。
新增 Sheet 用 `wb.copy_worksheet(src_ws)`（继承源表全部样式），再清值重写。

### 3. 公式必须算总价（关键坑）
openpyxl 只写公式**字符串**，不计算结果。手机/部分查看器打开公式单元格显示**空白**，用户会以为"没算总价"。
**修复**：用 LibreOffice 无头模式重算并写回缓存值（公式 + 缓存值双留）：
```bash
soffice --headless --calc --convert-to xlsx --outdir /tmp/recalc out.xlsx
cp /tmp/recalc/out.xlsx out.xlsx
```
（LibreOffice 没装：`sudo apt-get install -y --no-install-recommends libreoffice-calc`）
验证缓存值：`openpyxl.load_workbook(f, data_only=True)` 读 Total 单元格应得数字而非 None。

### 4. "按模板" = 字体/颜色/合并格/公式全对齐
用户说"按我的模板"指的是**视觉与结构一致**，不是"内容相似"。检查清单：
- 标题字体/字号（常见 Arial Unicode MS 22 bold）
- 表头合并单元格（如 B14:B15 序号合并、G14 跨 One-time）
- 数字格式（`\$#,##0.00`、`0%` VAT 列）
- 批注列特殊色（如红色 `FFFF0000` 18号）
- 公式引用（`=E16*G16`、`=SUM(H16:H17)` 保留）

### 5. 中英文两份
- 用英文版：沿用模板字体（Arial Unicode MS），不要换 Calibri
- 中文版：可用微软雅黑（中文更工整），但结构/列宽/合并必须同模板
- 用 `hermes send -t telegram:5701842056 "说明 MEDIA:/绝对路径/文件.xlsx"` 直接发用户

### 6. 中文化时清掉模板自带的英文残留（本会话踩两次）
复制模板后，模板**自带**的英文标签/批注不会自动变中文。务必全文扫一遍英文串并翻译，否则用户会说"note 还是英文"：
- 客户信息区标签：如 `B5: "Customer Name:"` → 改 `"客户名称："`
- 模板底部 note：`B20: "Note: 1. For the purpose..."` 及汇率说明 → 整段翻译
- Scope / 批注列：若模板留了占位英文（如 "Information not available"），按用户给的真实内容（如 html 资源清单）替换，不要留占位
**扫描方法**：`openpyxl` 载入后遍历所有 sheet 单元格，正则 `[A-Za-z]{4,}` 命中且含 `Note/Note:/Customer/Spec/Remote/Optional/Billing` 等关键词的，逐条翻译或替换。

### 7. 小体量客户用"三档报价"策略
用户是小体量（个位数 VM）客户时，不要给单一大包人天（如 75 人天会被打回"太多"）。
**做法**：按同一 WBS 结构出 A/B/C 三档，让客户/内部选档：
- A 轻量（极小，纯迁移无 POC）：~30 人天
- B 轻量（小，含轻量 POC）：~40 人天
- C 轻量（中小，含设计+POC+割接）：~50 人天
人天单价按 $235/人天；阶段比例参考奥芯明 OA 的 WBS（调研/设计/POC/实施/割接/验收）。
中英文各一份独立文件，文件名带 `_A/_B/_C_CN/EN` 后缀。

### 9. 严格克隆 = 连"留空分组"结构也要对齐（奥芯明 OA 模板教训）
用户给的模板常有**非直觉结构**，复制文件后必须保留，不能"自动化摊平"：
- **两行表头**：`E1:H1` 合并写"职位-工作量"，第二行 `E2:H2` 才是 4 个角色子表头。不要改成单行。
- **分组首行写值、同组其余行留空**：如 B 列项目名只在 `B3` 写、C 列阶段只在每组首行写（`C3="调研"`、`C4:C5` 空），并用 `merge_cells` 把同组单元格合并（`C3:C5` 等）。遍历任务时**只在每组首行填阶段名+人天，后续任务行只填 D 列任务文本**。
- **底部 G 列标记**：`G26="远程"`、`G27="现场20%"`、`G28="现场50%"`，H 列用 `=H26*1.2 / *1.5` 算上浮。E24:H24 是 `=SUM(E3:E22)` 合计。这些公式复制模板时已自带，清数据区时**别清掉底部公式行**（只清 B3:H23 数据区）。
- **列宽/字体**：OA 模板是 Calibri 10 号（不是 Arial），C=19、D=34。以 `inspect` 脚本实际读出为准，不要假设。

### 10. 发用户前必须 LibreOffice 重算（否则白做）
凡写了公式（`=E16*G16`、`=SUM(...)`）的 xlsx，**发送前必跑**：
```bash
cp out.xlsx /tmp/r.xlsx && soffice --headless --calc --convert-to xlsx --outdir /tmp/rc /tmp/r.xlsx >/dev/null 2>&1 && cp /tmp/rc/r.xlsx out.xlsx
```
openpyxl 写的公式在手机/Excel 打开若不重算会显空白，用户会判"没算总价"。重算后用 `load_workbook(f, data_only=True)` 验证 Total 单元格为数字再发。
⚠️ **覆盖写回会被沙箱/审批拦截**——若 `hermes send` 前这一步被拦，先告知用户"等待确认重算覆盖"，不要假装已发。

## 参考
- `references/excel-template-clone.md` — 完整可运行脚本模板 + Fintech/OA 模板结构速查 + 常见坑
- `references/oci-scheduled-shutdown.md` — OCI Always Free 实例定时关机(cron UTC16:00=北京24:00)+ 开机 systemd 播报 的可复用脚本

## 注意
- xlsx 用 `openpyxl`；docx 用 `python-docx`；两者 PEP668 环境需 `pip3 install --quiet openpyxl python-docx`（venv 或 uv）
- 读 xlsx 时 `data_only=True` 才能拿到公式缓存值；不传则拿到公式字符串
- 文件名含中文/全角逗号时，用变量传参别硬编码进 shell 引号串，避免 SyntaxError
