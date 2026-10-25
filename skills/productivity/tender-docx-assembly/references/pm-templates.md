# PM Templates (Project Management Templates)

> 适用场景：投标/交付时需要配套的项目管理模板（Project Charter、RACI、风险登记册、甘特图、状态报告等）
> 来源：2026-09-08 替代 Template22 付费版（$99.99）

## 快速创建

```python
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from docx.shared import Pt, Inches, Cm, RGBColor

# 颜色定义（黑灰商务风，无蓝色）
C = {'dg': '333333', 'mg': '555555', 'lg': '888888', 'bh': '444444', 'bs': '666666', 'ba': 'EAEAEA', 'ac': 'D4AF37'}
```

## 15 个模板清单

| 序号 | 模板 | 核心列/结构 |
|------|------|-------------|
| 1 | Project Charter | 项目信息、背景、范围、里程碑、干系人、审批 |
| 2 | RACI Matrix | 任务 × 角色矩阵，R/A/C/I 分配 |
| 3 | Risk Register | 风险ID、描述、类别、可能性、影响、等级、应对策略 |
| 4 | Gantt Chart | 任务、负责人、起止日期、工期、完成%、周维度进度条 |
| 5 | Status Report | 进展、下周计划、风险问题 |
| 6 | Issue Tracker | 问题ID、标题、优先级、类型、状态 |
| 7 | Budget Tracker | 类别、预算、实际、剩余、使用率（含SUM公式） |
| 8 | Resource Plan | 角色、人员、投入比例、工时、成本 |
| 9 | Action Plan | 行动项、负责人、优先级、状态、完成% |
| 10 | Change Log | 变更ID、内容、申请人、审批人、影响 |
| 11 | WBS | WBS编码、工作包、工期 |
| 12 | Kanban Board | 待办/进行中/待验证/已完成 四列 |
| 13 | Cost Benefit | 成本项、收益项、ROI公式 |
| 14 | Stakeholder | 干系人、影响力、态度、沟通策略 |
| 15 | Dashboard | KPI卡片 + 里程碑进度 |

## openpyxl 关键坑

### Alignment 参数验证
```python
# ❌ 错误：horizontal='top' 会 ValueError
Alignment(horizontal='top', vertical='left')  # 报错！

# ✅ 正确：horizontal 和 vertical 取值范围不同
Alignment(horizontal='left', vertical='top')  # horizontal: left/center/right/general/fill/distributed/justify/centerContinuous
                                            # vertical: top/center/bottom/justify/distributed
```

### Cell Shading（单元格背景色）
```python
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

# ❌ 错误：qn('w:shd') 返回字符串，无 .set() 方法
shd = qn('w:shd')  # AttributeError: 'str' object has no attribute 'set'

# ✅ 正确：用 OxmlElement 创建元素
shd = OxmlElement('w:shd')
shd.set(qn('w:fill'), 'E0E0E0')
shd.set(qn('w:val'), 'clear')
cell._tc.get_or_add_tcPr().append(shd)
```

### 表格插入到指定段落后
```python
# ❌ 错误：Paragraph 无 _tbl 属性
target_para._tbl.addnext(table._tbl)  # AttributeError

# ✅ 正确：用 _element
target_para._element.addnext(table._tbl)
```

### 合并单元格顺序
```python
# ❌ 错误：先 merge 再赋值 → MergedCell 只读
ws.merge_cells('A1:B1')
ws['A1'].value = 'x'  # AttributeError: 'MergedCell' object attribute 'value' is read-only

# ✅ 正确：先赋值左上角，再 merge
ws['A1'].value = 'x'
ws.merge_cells('A1:B1')
```

## 中文字体设置

```python
from matplotlib.font_manager import FontProperties

# 使用 Noto Sans CJK（本机已装）
font_prop = FontProperties(fname='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
font_prop_bold = FontProperties(fname='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc')

# 全局设置
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['Noto Sans CJK SC', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
```

## Logo 设计（页眉用）

```python
from matplotlib.patches import FancyBboxPatch

# AC 字母设计 + 安畅网络/SmartCare 品牌
fig, ax = plt.subplots(figsize=(4, 0.9))
box = FancyBboxPatch((0.1, 0.15), 0.55, 0.55, boxstyle="round,pad=0.05",
                     facecolor='#333333', edgecolor='#555555', linewidth=1.5)
ax.add_patch(box)
ax.text(0.375, 0.425, 'A C', ha='center', va='center', fontsize=16,
        fontweight='bold', color='#FFFFFF', fontproperties=font_prop_bold)
ax.text(0.85, 0.55, '安畅网络', fontproperties=font_prop_bold, fontsize=16, color='#333333')
ax.text(2.75, 0.55, 'SmartCare', fontproperties=font_prop_bold, fontsize=12, color='#D4AF37')
```
