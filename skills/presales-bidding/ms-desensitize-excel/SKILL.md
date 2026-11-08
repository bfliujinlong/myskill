---
name: ms-desensitize-excel
description: 对 Excel (.xlsx) 文件执行脱敏处理。使用 openpyxl 读取和修改工作簿，将真实客户标识替换为代号或 [REDACTED]，保留 SLA 数值、计价公式、RACI 矩阵等业务数据。处理所有 Sheet、单元格、图表标题、批注。
---

# Excel 脱敏 Skill

## 概述

对 Excel (.xlsx) 文件执行脱敏处理，将 L2 原始材料转化为 L1 可自动加载的脱敏版本。

**核心原则**：脱敏标识符，保留信息。Excel 中的数值、公式、百分比必须完整保留。

## 前置检查

1. 确认源文件位于 L2 区
2. 确认目标目录为 L1 区
3. 读取源目录和目标目录的 `.kb-policy.yaml`
4. 确认已安装 `openpyxl`：`pip install openpyxl`

## 执行步骤

### 步骤 1：读取 Excel 工作簿

```python
from openpyxl import load_workbook
wb = load_workbook("input.xlsx")
```

### 步骤 2：逐 Sheet 脱敏

对工作簿中的所有 Sheet 执行脱敏：

| 区域 | 说明 |
|------|------|
| Sheet 名称 | 检查是否含客户名 |
| 单元格文本 | 逐单元格替换 |
| 图表标题 | 检查 chart.title |
| 批注 | 检查 cell.comment |
| 页眉页脚 | 检查 sheet.oddHeader/oddFooter |
| 数据验证 | 检查 validation 公式 |
| 条件格式 | 通常不含标识符，但需检查 |

### 步骤 3：Excel 特有处理

| 元素 | 处理方式 |
|------|---------|
| Sheet 名称 | 含客户名 → 替换为代号 |
| 单元格文本 | 字符串类型 → 脱敏替换 |
| 单元格数值 | **保留不动**（SLA 数值、金额、百分比） |
| 单元格公式 | 检查公式中是否含标识符 |
| 图表 | 标题、轴标签、数据系列名称 |
| 批注 | 逐批注替换 |
| 合并单元格 | 处理合并区域的文本 |
| 隐藏 Sheet | 同样需要处理 |

### 步骤 4：区分文本和数值

```python
for row in sheet.iter_rows():
    for cell in row:
        if isinstance(cell.value, str):
            # 文本 → 脱敏
            result = engine.process_text(cell.value)
            cell.value = result.text
        elif isinstance(cell.value, (int, float)):
            # 数值 → 保留
            pass
        # 公式 → 检查但不修改公式结构
```

### 步骤 5：处理 Sheet 名称

```python
for sheet_name in wb.sheetnames:
    result = engine.process_text(sheet_name)
    if result.replacements:
        wb[sheet_name].title = result.text
```

### 步骤 6：保存脱敏工作簿

```python
wb.save("output-脱敏.xlsx")
```

### 步骤 7：验证

- 重新打开工作簿，搜索真实客户名/IP
- 确认数值列未被修改
- 确认公式仍可正常计算
- 确认图表引用未断裂

### 步骤 8：重命名输出文件

按命名规范：`主题-客户代号-脱敏.xlsx`

## Excel 特有注意事项

1. **数值保护**：Excel 中的数值（SLA 百分比、金额、工单量）是核心业务数据，**绝对不可修改**
2. **公式保护**：公式中的单元格引用不可修改，只替换公式中的字符串常量
3. **Sheet 名称**：Sheet 名称有 31 字符限制，替换后需检查长度
4. **图表引用**：修改 Sheet 名称后，图表引用可能断裂，需验证
5. **数据透视表**：透视表的源数据范围引用需注意
6. **隐藏行列**：隐藏的行列也需要脱敏

## 金标准参考

`02-Offering素材/02-SLA与服务治理/SLA-SLO矩阵-MFG-A-脱敏.md`
