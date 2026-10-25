# 输出模板：PPT 数据刷新

`<>` 为占位符，产出时替换。脚本用法见 `scripts/refresh_pptx.py`，示例见 `examples/`。

## 模板 1：data.json（token 模式）

```json
{
  "tokens": {
    "KPI_ARR": "<1,284 万>",
    "USERS_Q3": "<18,902>",
    "GROWTH_QOQ": "<23.4%>"
  },
  "charts": {
    "slide<N>/<ChartName>": {
      "categories": ["<Q1>", "<Q2>", "<Q3>"],
      "series": { "<营收>": [<980>, <1102>, <1284>] }
    }
  }
}
```
单位写进值里（"1,284 万" 而不是 "1284"）。图表键格式 `slide{页码}/{形状名}`，用 `--scan` 获取。

## 模板 2：mapping.json（位置模式，无 token 的历史 deck）

```json
{
  "text": [
    {
      "slide": <4>,
      "shape": "<TextBox 12>",
      "paragraph": 0,
      "old_hint": "<12,345>",
      "new": "<18,902>"
    }
  ]
}
```
`old_hint` 防错位：位置对不上就报错，不静默改错。

## 模板 3：change-report.md（脚本产出）

```markdown
# PPT 数据刷新变更报告

## 已替换（<N> 处）
| 页码 | 位置 | 旧值 | 新值 |
| --- | --- | --- | --- |

## ⚠️ 未匹配的图表键（<N> 个）
## 未匹配的占位符 / 未被使用的数据键
## 待人工确认的疑似数据点
## 后续人工校验清单（六步校验的勾选框）
```

## 模板 4：data-inventory.json（扫描产出）

```json
{
  "tokens": [{ "token": "<NAME>", "first_seen": "slide<N>/<shape>" }],
  "charts": [{ "id": "slide<N>/<name>", "series": ["<名>"] }],
  "dataish": [{ "slide": <N>, "shape": "<名>", "value": "<12,345>" }]
}
```
