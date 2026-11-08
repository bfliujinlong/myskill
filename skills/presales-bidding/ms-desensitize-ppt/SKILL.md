---
name: ms-desensitize-ppt
description: 对 PowerPoint (.pptx) 文件执行脱敏处理。使用 python-pptx 读取和修改演示文稿，将真实客户标识替换为代号或 [REDACTED]，保留 SLA 数据、架构描述、案例数据等业务信息。处理所有幻灯片、文本框、表格、备注。
---

# PPT 脱敏 Skill

## 概述

对 PowerPoint (.pptx) 文件执行脱敏处理，将 L2 原始材料转化为 L1 可自动加载的脱敏版本。

**核心原则**：脱敏标识符，保留信息。PPT 中的案例数据、SLA 数值、架构描述必须完整保留。

## 前置检查

1. 确认源文件位于 L2 区
2. 确认目标目录为 L1 区
3. 读取源目录和目标目录的 `.kb-policy.yaml`
4. 确认已安装 `python-pptx`：`pip install python-pptx`

## 执行步骤

### 步骤 1：读取 PPT 演示文稿

```python
from pptx import Presentation
prs = Presentation("input.pptx")
```

### 步骤 2：逐幻灯片脱敏

对所有幻灯片中的文本区域执行脱敏：

| 区域 | 说明 |
|------|------|
| 标题文本框 | slide.shapes.title |
| 内容文本框 | slide.shapes → text_frame |
| 表格 | slide.shapes → table |
| 备注页 | slide.notes_slide.notes_text_frame |
| 图片 alt 文本 | shape.alternative_text |
| 超链接 | run.hyperlink.address |
| 母版/版式 | slide_master / slide_layouts |

### 步骤 3：PPT 特有处理

| 元素 | 处理方式 |
|------|---------|
| 文本框 | 逐段落逐 run 替换 |
| 表格 | 逐单元格替换 |
| 图表 | 标题、数据标签、系列名称 |
| SmartArt | 遍历所有节点文本 |
| 备注页 | 演讲者备注中的标识符 |
| 母版 | 公司 logo 旁的文本 |
| 嵌入对象 | Excel/Word 嵌入对象 |
| 视频/音频 | 文件名和描述文本 |

### 步骤 4：处理母版和版式

```python
# 母版中的文本（如公司名、页脚）
for master in prs.slide_masters:
    for shape in master.shapes:
        if shape.has_text_frame:
            for para in shape.text_frame.paragraphs:
                result = engine.process_text(para.text)
                # 替换文本
```

### 步骤 5：保存脱敏演示文稿

```python
prs.save("output-脱敏.pptx")
```

### 步骤 6：验证

- 重新打开演示文稿，逐页检查
- 确认排版未被破坏
- 确认图表数据完整

### 步骤 7：重命名输出文件

按命名规范：`主题-客户代号-脱敏.pptx`

## PPT 特有注意事项

1. **排版保护**：PPT 的排版对演示效果至关重要，替换文本时保持 run 级别的格式
2. **SmartArt**：SmartArt 图形中的文本需要通过 XML 遍历
3. **嵌入 Excel**：PPT 中嵌入的 Excel 图表数据也需要脱敏
4. **备注页**：演讲者备注经常包含客户内部信息，必须检查
5. **母版页脚**：母版中的公司名、日期、页码需要检查
6. **动画文本**：动画效果中的文本与普通文本相同处理

## 金标准参考

`02-Offering素材/02-SLA与服务治理/SLA-SLO矩阵-MFG-A-脱敏.md`
