---
name: memory-token-saver
description: Use when 要省 token：记忆写本地文件而非每轮注入、精简 MEMORY.md、按需检索归档。触发词：省token / token 优化 / 记忆写本地 / context 太占。
---

# Memory Token Saver

目标：把每轮系统提示里强制注入的记忆体积压到最小，明细全部落本地，按需读。

## 每轮强制注入的成本（固定支出）

| 项 | 位置 | 注入方式 |
|---|---|---|
| MEMORY.md | `~/.hermes/memories/MEMORY.md` | **每轮全量注入** |
| USER.md | `~/.hermes/memories/USER.md` | **每轮全量注入** |
| 技能列表（96 个） | `~/.hermes/skills/` | 每轮注入名称+描述 |
| memory-archive/references/ | 已有存档 | **不注入**（按需读）✅ |
| ENV-REGISTRY.md | 67KB | **不注入** ✅ |
| memories/local/ | 本地明细 | **不注入** ✅ |

结论：**只有 MEMORY.md 和 USER.md 是每轮真金白银的开销**。其余都在本地，读到才花钱。

## 写入决策树（记住这个）

```
新信息 → 是否每轮都需要？
  ├─ 是（身份/硬约束/交付通道/当前冲刺）→ MEMORY.md，但必须极简
  └─ 否 → 本地文件，按需读
       ├─ 环境/IP/路径/cron    → memories/ENV-REGISTRY.md
       ├─ 历史明细（11 主题）  → skills/memory-archive/references/*.md
       └─ 其他项目/一次性细节  → memories/local/<topic>.md
```

## MEMORY.md 硬规则

- 字符上限 **2200**（不是默认的 6000）。超限 = 每轮白烧 token。
- 只写「每轮都用得上」的：身份、硬约束、交付通道、当前冲刺。
- **禁止**写入：已完成事项日志、具体排障过程、数字台账、一次性结论。
- 一条记忆一句话，不用列表套列表。

## 精简手法

1. 把「环境台账」类整段挪走 → `ENV-REGISTRY.md`，MEMORY.md 只留一行指针
2. 排障过程 → `memory-archive/references/` 对应主题文件
3. 保留的条目去修饰词，只留动词+宾语+条件

## 验证是否生效

```bash
wc -c ~/.hermes/memories/MEMORY.md ~/.hermes/memories/USER.md
```
目标：两者合计 **< 3000 字符**。

## 相关

- `memory-archive` 技能：11 个主题的历史明细，按需读
- `memories/ENV-REGISTRY.md`：环境台账总表
