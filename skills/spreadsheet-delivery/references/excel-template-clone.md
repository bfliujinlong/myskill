# Excel 模板克隆 — 可运行脚本模板与常见结构速查

## 完整脚本骨架（严格克隆 + 公式缓存）

```python
import openpyxl, shutil, copy, sys

SRC = "/path/to/USER_TEMPLATE.xlsx"          # 用户模板
OUT = "/path/to/OUTPUT.xlsx"
shutil.copyfile(SRC, OUT)
wb = openpyxl.load_workbook(OUT)

def fill_info(ws):
    # 只改客户信息区的值, 不动样式
    ws["D5"] = "客户名"; ws["L5"] = "2026-08-21"
    ws["D8"] = "客户经理"; ws["G8"] = "电话"
    ws["D10"] = "架构师"; ws["G10"] = "电话"; ws["G11"] = "邮箱"

def copy_row_style(src_ws, sr, dst_ws, dr):
    for c in range(1, dst_ws.max_column+1):
        s = src_ws.cell(sr,c)
        if s.has_style: dst_ws.cell(dr,c)._style = copy.copy(s._style)

# 改数据行(只改值, 公式字符串保留)
ws = wb["Migration"]; fill_info(ws)
ws["C16"] = "新服务名"; ws["D16"] = "详情..."; ws["E16"] = 40; ws["G16"] = 235
# H16 原公式 =E16*G16 保留, 不用写死
ws.save(OUT)

# 算缓存值(关键): LibreOffice 无头重算
# bash: soffice --headless --calc --convert-to xlsx --outdir /tmp/rc OUT.xlsx && cp /tmp/rc/OUT.xlsx OUT.xlsx
```

## Fintech 报价单模板结构速查（真实项目验证）

文件：`Fintech Quotation_LZ&Migration_EN_V1.1*.xlsx`
- **字体**：标题/正文 `Arial Unicode MS`（非 Calibri）；数量列 `Microsoft YaHei UI`/`微软雅黑`；批注 M 列 `Calibri` 10号 + **红色 `FFFF0000` 18号**
- **标题**：B2，22号 bold，居中
- **客户信息区**（B5 起，两列布局）：Customer Name(D5) / Contact(E5) / Quote Date(L5) / Quote Validity(L7) / Account Manager(D8) / Solution Architect(D10) / Monetary Unit(L11)
- **表头行 14-15**（合并）：B14:B15 序号合并；G14 跨 One-time Charges，G15=Unit Price(USD)，H15=Subtotal(USD)；I14 跨 Recurring(Monthly)，I15=Unit Price(USD/monthly)；K14 跨 Yearly
- **数据行**：Landing Zone 2行(16-17) Total 18；Migration 5行(16-20) Total 21；Scope 是 A 列纯文本框
- **公式**：`H=r=E*r*G*r`、`J=r=E*r*I*r`、`K=r=I*r*12`、`L=r=E*r*K*r`、`G{Total}=SUM(H16:H17)` 等
- **数字格式**：`\$#,##0.00`；VAT 列 `0%`（显示 `/` 实际 0%）
- **列宽**：B12/C22/D64/E10/G33/M43
- **Note 行**：B20(或下移) 通用说明，字体 Calibri 10

## 常见坑
1. `ws.cell(r,c).font = other.font` → `TypeError: unhashable type 'StyleProxy'`（openpyxl 坑）。改值别碰 font 对象，`copy_worksheet` 已继承。
2. 文件名含全角逗号 `，` → Python 嵌套 f-string 引号乱。用 `sys.argv` 传路径或写独立 .py 文件读。
3. `openpyxl` 读模板公式得到字符串；验证总价必须 `data_only=True` 且文件经 LibreOffice 重算过。
4. `wb.get_sheet_by_name()` 已废弃 → 用 `wb["Sheet名"]`。
5. 插入行后 Total 行公式范围要手动更新（如 H16:H17 → H16:H18）。
