---
name: ppt-data-refresh
description: "刷新 PowerPoint（.pptx）pitch deck、汇报材料中的业务数据：扫描数据点、按映射回写数字/表格/图表数据、保留原样式，输出变更清单与差异报告。当用户需要更新 deck 中的 KPI、财务数据、用户数、季度数据，或要求『刷新 PPT 数据』『更新 pitch deck』时使用。"
description_zh: "刷新 PowerPoint pitch deck 中的数据"
description_en: "Refresh data points inside a PowerPoint pitch deck while preserving formatting"
version: 1.0.1
agent_created: true
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - AskUserQuestion
trigger: ["刷新PPT", "PPT数据", "pitch deck", "更新deck", "deck数据刷新", "更新PPT数字", "refresh deck"]
---

# PPT 数据刷新

季度更新 deck 时，最花时间的不是改数，而是**找全**该改的数、以及改完不破坏版式。这个 skill 把过程固定成六步，并附一个可执行脚本。

## 核心原则

1. **不在原文件上直接改。** 先复制一份，产出新文件，原文件保留。
2. **不手改数字。** 所有新值来自结构化数据源（Excel / CSV / JSON），可追溯。
3. **保留样式。** 只替换文本内容，不动字体、字号、颜色、位置、单位。
4. **先预演再落盘。** 默认 `--dry-run`，人工确认 diff 后再写。

## 六步流程

### 第 1 步 体检：生成数据点清单

```bash
python scripts/refresh_pptx.py --deck Q3_deck.pptx --scan --out data-inventory.json
```

脚本扫描全部幻灯片（含表格、图表、备注页），输出：

- **已命名的占位符** `{{TOKEN}}`：可自动替换，最可靠
- **表格单元格中的占位符**：同上
- **疑似数据点**：匹配 `12,345` / `45.6%` / `¥1.2M` 等形态的纯文本数字，需人工确认是否纳入
- **图表**：图表名、series 名称、当前取值

### 第 2 步 建映射

推荐做法：在 deck 模板里把数字写成 `{{KPI_ARR}}`、`{{USERS_Q3}}` 这样的 token，一次改造，长期受益。

对无法改模板的历史 deck，用 `mapping.json` 指定位置：

```json
{
  "text": [
    {
      "slide": 4,
      "shape": "TextBox 12",
      "paragraph": 0,
      "old_hint": "12,345",
      "new": "18,902"
    }
  ]
}
```

`old_hint` 用于防止错位——位置对不上就报错，不静默改错。

### 第 3 步 取数

从唯一数据源导出 `data.json`：

```json
{
  "tokens": {
    "KPI_ARR": "1,284 万",
    "USERS_Q3": "18,902",
    "GROWTH_QOQ": "23.4%"
  },
  "charts": {
    "slide6/Chart 3": {
      "categories": ["Q1", "Q2", "Q3"],
      "series": { "营收": [980, 1102, 1284] }
    }
  }
}
```

**单位写进值里**（"1,284 万" 而不是 "1284"），避免单位被漏改。

### 第 4 步 预演

```bash
python scripts/refresh_pptx.py --deck Q3_deck.pptx --data data.json --dry-run --report change-report.md
```

输出变更清单：`页码 / 位置 / 旧值 / 新值 / 变化率`。逐条核对，重点看变化率异常的（比如 >100% 或方向相反）。

### 第 5 步 回写

```bash
python scripts/refresh_pptx.py --deck Q3_deck.pptx --data data.json --out Q4_deck.pptx --report change-report.md
```

图表使用 `replace_data` 更新 series，不重建图表对象，样式与坐标轴设置保持不变。

### 第 6 步 校验（人工，不可省）

- [ ] 单位与口径未变（同比还是环比？含税还是不含税？）
- [ ] 期间标注同步更新（标题、副标题、页脚、图表 X 轴）
- [ ] 同比 / 环比自洽：总数与分项之和一致，占比合计 100%
- [ ] 全文搜索旧值，确认没有残留（尤其是备注页和隐藏页）
- [ ] 页脚日期、版本号已更新
- [ ] 与数据源再抽样比对 3 处

## 脚本用法

```
python scripts/refresh_pptx.py --deck FILE [--data JSON] [--out FILE] [--dry-run]
                               [--scan] [--report MD] [--map JSON]
```

| 参数 | 说明 |
| --- | --- |
| `--deck` | 输入 .pptx（必填） |
| `--scan` | 只体检，输出数据点清单 |
| `--data` | 新数据 JSON（tokens / charts） |
| `--map` | 位置映射 JSON，用于无 token 的历史 deck |
| `--out` | 输出文件；省略则自动命名 `<原名>_refreshed.pptx` |
| `--dry-run` | 预演，不写文件 |
| `--report` | 输出变更报告 Markdown |

依赖：`pip install python-pptx`。

### 快速上手（用自带样例验证环境）

```bash
python scripts/refresh_pptx.py --deck examples/Q3_deck_template.pptx --scan
python scripts/refresh_pptx.py --deck examples/Q3_deck_template.pptx \
       --data examples/data.example.json --dry-run --report /tmp/diff.md
```

`examples/` 内有模板 deck、示例 data.json 与实测产出的变更报告，可用来确认脚本可用后再处理真实 deck。

## 已知限制

| 限制 | 说明 | 规避 |
| --- | --- | --- |
| SmartArt | python-pptx 不支持直接改写 | 在 PowerPoint 中拆成普通形状后再跑脚本 |
| 链接图表（Excel 联动） | 底层数据在外部工作簿 | 在 Excel 侧更新后右键"刷新数据" |
| 图片中的数字 | 位图无法文本替换 | 重新出图后替换 |
| 主题字体继承 | 跨 run 的 token 会归拢到首个 run | 保持 token 在同一 run 内完整书写 |
| 数字格式 | 千分位与小数位不自动处理 | 格式化后写入 data.json |

## 输出交付物

- 刷新后的 `.pptx`
- `change-report.md`：变更清单（含未匹配 token、未被使用的数据键、需人工确认的疑似数据点）
- `data-inventory.json`：deck 数据点基线，下次刷新可复用

## 边界

- **不做**：改动版式与视觉设计、重写文案、自动判断业务口径。
- **不确定时**：单位、口径、期间无法从 deck 与数据源判断，用 AskUserQuestion 确认，不猜。


---

## 输出模板

所有交付物模板见 `references/templates.md`。产出文档时按模板填充，不自创结构；模板未覆盖的字段按项目实际补充并在交付物中注明。
