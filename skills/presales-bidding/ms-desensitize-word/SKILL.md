---
name: ms-desensitize-word
description: 对 Word (.docx) 文件执行脱敏处理。使用 python-docx 读取和修改文档内容，将真实客户标识替换为代号或 [REDACTED]，保留 SLA 数值、指标结构、表格数据等业务信息。处理正文、表格、页眉页脚、批注。
---

# Word 脱敏 Skill

## 概述

对 Word (.docx) 文件执行脱敏处理，将 L2 原始材料转化为 L1 可自动加载的脱敏版本。

**核心原则**：脱敏标识符，保留信息。

## 前置检查

1. 确认源文件位于 L2 区
2. 确认目标目录为 L1 区
3. 读取源目录和目标目录的 `.kb-policy.yaml`
4. 确认已安装 `python-docx`：`pip install python-docx`

## 执行步骤

### 步骤 1：读取 Word 文档

```python
from docx import Document
doc = Document("input.docx")
```

### 步骤 2：逐段脱敏

对以下所有文本区域执行脱敏：

| 区域 | 说明 |
|------|------|
| 正文段落 | `doc.paragraphs` |
| 表格单元格 | `doc.tables → rows → cells → paragraphs` |
| 页眉 | `doc.sections[i].header.paragraphs` |
| 页脚 | `doc.sections[i].footer.paragraphs` |
| 批注 | `doc.comments`（如存在） |

对每个文本区域，使用共享脱敏引擎处理：

```python
from desensitize_engine import DesensitizeEngine
engine = DesensitizeEngine()
result = engine.process_text(paragraph.text)
paragraph.text = result.text
```

### 步骤 3：Word 特有处理

| 元素 | 处理方式 |
|------|---------|
| 正文段落 | 逐段替换 |
| 表格 | 逐单元格替换，保留数值列 |
| 页眉/页脚 | 检查公司名、项目名 |
| 批注/修订 | 检查批注内容 |
| 嵌入图片 | 检查图片文件名和 alt 文本 |
| 超链接 | 检查 URL 中的域名 |
| 文档属性 | 清除 author、company、last_modified_by |
| 文本框/形状 | 遍历所有 shape 中的文本 |

### 步骤 4：清除文档元数据

```python
# 清除文档属性中的敏感信息
core_props = doc.core_properties
core_props.author = ""
core_props.company = ""
core_props.last_modified_by = ""
core_props.title = "脱敏文档标题"
```

### 步骤 5：保存脱敏文档

```python
doc.save("output-脱敏.docx")
```

### 步骤 6：验证

- 重新打开文档，搜索真实客户名/IP/域名
- 确认表格中的 SLA 数值完整
- 确认文档格式未被破坏

### 步骤 7：重命名输出文件

按命名规范：`主题-客户代号-脱敏.docx`

## Word 特有注意事项

1. **格式保留**：python-docx 替换文本时会保留原有格式（字体、颜色、大小），但需验证
2. **表格嵌套**：注意表格中可能嵌套表格
3. **文本框**：文档中的文本框（TextBox）需要单独遍历
4. **修订记录**：如果文档开启了修订模式，需要先接受所有修订再脱敏
5. **嵌入对象**：Excel 嵌入对象中的数据也需要脱敏

## 金标准参考

`02-Offering素材/02-SLA与服务治理/SLA-SLO矩阵-MFG-A-脱敏.md`
