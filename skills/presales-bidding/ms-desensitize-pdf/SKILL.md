---
name: ms-desensitize-pdf
description: 对 PDF (.pdf) 文件执行脱敏处理。使用 pdfplumber/PyPDF2 提取文本，脱敏后重新生成 PDF。对于扫描版 PDF，先 OCR 提取文本再脱敏。保留 SLA 数值、表格数据、图表内容。
---

# PDF 脱敏 Skill

## 概述

对 PDF (.pdf) 文件执行脱敏处理，将 L2 原始材料转化为 L1 可自动加载的脱敏版本。

**核心原则**：脱敏标识符，保留信息。PDF 中的 SLA 数据、表格、图表说明必须完整保留。

**特殊挑战**：PDF 是版式固定格式，直接修改文本会破坏排版。本 Skill 采用「提取 → 脱敏 → 重新生成」的策略。

## 前置检查

1. 确认源文件位于 L2 区
2. 确认目标目录为 L1 区
3. 读取源目录和目标目录的 `.kb-policy.yaml`
4. 确认已安装依赖：`pip install pdfplumber PyPDF2 reportlab`
5. 判断 PDF 类型：文本版（可直接提取）vs 扫描版（需 OCR）

## 执行步骤

### 步骤 1：判断 PDF 类型

```python
import pdfplumber
with pdfplumber.open("input.pdf") as pdf:
    text = pdf.pages[0].extract_text()
    if text and len(text.strip()) > 50:
        # 文本版 PDF
        pdf_type = "text"
    else:
        # 扫描版 PDF，需要 OCR
        pdf_type = "scanned"
```

### 步骤 2A：文本版 PDF 脱敏

```python
import pdfplumber
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# 提取所有文本
all_text = []
with pdfplumber.open("input.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        if text:
            all_text.append(text)

# 脱敏
engine = DesensitizeEngine()
desensitized_pages = []
for page_text in all_text:
    result = engine.process_text(page_text)
    desensitized_pages.append(result.text)

# 重新生成 PDF（简化版，保留文本结构）
doc = SimpleDocTemplate("output.pdf", pagesize=A4)
styles = getSampleStyleSheet()
story = []
for page_text in desensitized_pages:
    for line in page_text.split("\n"):
        if line.strip():
            story.append(Paragraph(line, styles['Normal']))
        else:
            story.append(Spacer(1, 12))
doc.build(story)
```

### 步骤 2B：扫描版 PDF 脱敏（OCR）

```python
import pytesseract
from pdf2image import convert_from_path

# PDF → 图片 → OCR → 脱敏 → 重新生成
images = convert_from_path("input.pdf")
desensitized_texts = []
for img in images:
    text = pytesseract.image_to_string(img, lang='chi_sim+eng')
    result = engine.process_text(text)
    desensitized_texts.append(result.text)

# 重新生成 PDF（使用 reportlab 或 XeLaTeX）
```

### 步骤 3：PDF 特有处理

| 元素 | 处理方式 |
|------|---------|
| 正文文本 | 提取后脱敏 |
| 表格 | 提取表格数据，脱敏文本列，保留数值列 |
| 图片/图表 | 无法直接脱敏图片内容，在报告中标注 |
| 水印 | 检查水印文本是否含客户标识 |
| 页眉页脚 | 提取后脱敏 |
| 元数据 | 清除 author、title、subject |
| 书签/目录 | 检查书签文本 |
| 注释/批注 | 提取后脱敏 |

### 步骤 4：清除 PDF 元数据

```python
from PyPDF2 import PdfReader, PdfWriter
reader = PdfReader("input.pdf")
writer = PdfWriter()
writer.append(reader)
writer.add_metadata({
    "/Author": "",
    "/Title": "脱敏文档",
    "/Subject": "",
    "/Creator": "",
})
with open("output.pdf", "wb") as f:
    writer.write(f)
```

### 步骤 5：验证

- 重新提取文本，搜索真实客户名/IP
- 确认表格数据完整
- 确认页数一致

### 步骤 6：重命名输出文件

按命名规范：`主题-客户代号-脱敏.pdf`

## PDF 特有注意事项

1. **排版损失**：重新生成的 PDF 排版可能与原版不同，这是已知限制
2. **图片内容**：PDF 中的图片（截图、架构图）无法直接脱敏，需要人工审核
3. **扫描版 OCR**：OCR 准确率不是 100%，脱敏后需要人工校验
4. **表格结构**：复杂表格（合并单元格、嵌套表格）提取后可能丢失结构
5. **加密 PDF**：需要先解密再处理
6. **建议**：对于重要 PDF，建议先转为 Word 脱敏后再转回 PDF

## 金标准参考

`02-Offering素材/02-SLA与服务治理/SLA-SLO矩阵-MFG-A-脱敏.md`
