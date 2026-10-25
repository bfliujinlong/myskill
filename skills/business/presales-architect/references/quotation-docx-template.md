# 报价单 .docx 生成 — 可复用片段（python-docx）

售前报价单常需按固定模板出中英文两份。以下是从本会话 AXM 报价单实测提炼的可复用骨架。

## 依赖
```bash
pip install python-docx openpyxl   # openpyxl 用于读既有 xlsx 模板
```

## 1. 先提取既有模板结构（不要手抄）
```python
import openpyxl
wb = openpyxl.load_workbook("客户模板.xlsx", data_only=True)
for ws in wb.worksheets:
    for r in range(1, min(ws.max_row,40)+1):
        row=[f"[{openpyxl.utils.get_column_letter(c)}{r}]{ws.cell(r,c).value}"
             for c in range(1, min(ws.max_column,14)+1) if ws.cell(r,c).value]
        if row: print(" | ".join(row))
```
→ 拿到表头列名/字段顺序后，照抄进生成脚本。

## 2. 生成双语文档骨架
```python
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

def set_cell_bg(cell, color="4472C4"):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd'); shd.set(qn('w:val'),'clear')
    shd.set(qn('w:color'),'auto'); shd.set(qn('w:fill'), color)
    tcPr.append(shd)

def fill(cell, text, bold=False, size=9, align=None):
    cell.text=""; p=cell.paragraphs[0]
    if align: p.alignment=align
    r=p.add_run(str(text)); r.font.size=Pt(size); r.font.bold=bold
    r.font.name='Calibri'; r._element.rPr.rFonts.set(qn('w:eastAsia'),'微软雅黑')

# 表头行：蓝底白字
def style_header(row):
    for c in row.cells:
        set_cell_bg(c,"4472C4")
        for p in c.paragraphs:
            for r in p.runs:
                r.font.bold=True; r.font.color.rgb=RGBColor(0xFF,0xFF,0xFF); r.font.size=Pt(9)
```
- 中文版标题用微软雅黑/宋体；英文版直接用 Calibri
- 表格用 `doc.add_table(rows=1, cols=N); doc.style='Table Grid'`
- 费用合计行用 `fill(cell, "费用合计（含税）：", bold=True)` + 数字

## 3. SmartCare 计费项标准价（安畅，2026 V2.7）
| 计费项 | 月单价(¥) | 年单价(¥) |
|---|---|---|
| VM（实例数） | 240 | 2880 |
| PaaS 服务（实例） | 200 | 2400 |
| 数据库管理（实例） | 240 | 2880 |
| 容器管理 Worker节点 | 120 / 150 | 1440 / 1800 |
| DevOps 非微服务 Pipeline | 240 | 2880 |
| 安全管理（专业，标准×0.3） | N/A | N/A |
| 服务级别系数 | 金1.2 / 银1.0 / 铜0.8 | 同左 |

## 4. 英文术语速查（对齐 Dubai Fintech 范本）
- 云迁移与运维服务报价单 → Cloud Migration & SmartCare Operations Service Quotation
- 云迁移工程师 → Cloud Migration Engineer
- 数据库迁移工程师 → Database Migration Engineer
- 云交付架构师 → Cloud Delivery Architect
- 项目经理 → Project Manager
- 运维/托管 → Operations / Managed Service / SmartCare
- 订阅制（月/年）→ Subscription-based (monthly/yearly)
- 不含项 → Exclusions: cloud resource fees, third-party software licenses, application code development
- 报价有效期 → Quote validity: 30 days from quote date
- 远程上浮 → Onsite delivery incurs +20% on person-day rate

## 5. 输出与校验
生成后务必回读校验（避免格式错/数字错）：
```python
import docx
d=docx.Document("out.docx")
for tb in d.tables:
    for row in tb.rows[:4]:
        print(" | ".join(c.text[:15].replace("\n","/") for c in row.cells))
```
