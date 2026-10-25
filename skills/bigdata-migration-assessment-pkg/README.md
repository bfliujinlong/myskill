# 大数据迁移评估 Skill（我方口径三层模型）

> 版本 1.0.0 ｜ 安畅网络 · 售前解决方案中心
> 适用：AWS / 阿里云 / 自建 Hadoop → 腾讯云 / 阿里云 的数据湖、数仓、ETL、调度、实时链路迁移改造的**人力工作量评估**

---

## 它解决什么问题

售前接到大数据迁移项目时，最常见的三种翻车：

| 翻车方式 | 后果 |
|---|---|
| 拿客户/友商给的人月数乘个系数就报 | 用的是对方的逻辑，差异根因说不清，谈判没有底牌 |
| 按"同构集群搬迁"估异构托管服务改造 | 量级性低估。真实案例中低估了 **6.9 倍** |
| PB 级数据按 `量 ÷ 产能` 线性外推 | 算出 9429 人天这种荒谬数字；且完全没看到工期风险 |

本 Skill 把评估过程固化成**确定性脚本 + 可追溯参数表**，让同一份输入永远算出同一个结果，且每个数字都能回溯到"哪条事实触发的"。

---

## 三层模型

```
大数据总人力 = 模型1（复杂度分级）+ 模型2（标准服务目录）+ 模型3（超服务目录项）
```

| 层 | 覆盖 | 算法 |
|---|---|---|
| **模型1** | 平台 / 模块级改造 | D1架构 / D2数据 / D3耦合 / D4改造深度 各 1–5 分 → 平均分落 L1–L5 等级 → 基准人天区间 × 修正系数（连乘） |
| **模型2** | 有标准计费项的资源搬迁 | 资源量 ÷ 标准产能。**超计费上限的量不做线性外推**，改走"工具部署人天 + 传输期值守人天"替代算法，并出带宽场景表 |
| **模型3** | 目录里查不到计费项的工作 | 按产能定律逐项定价，全部标注"需单独商务谈判" |

判重规则：模型1 按模块整体计价的应用，其内部作业不再进入模型3；模型3 只收未被模型1 覆盖的作业/对象级工作。

---

## 六条硬纪律（P0）

1. **独立重算** — 客户/友商的人月数只能进"差异对比"栏，禁止当基数缩放
2. **三层不重复计** — 判重规则写死在 SKILL.md
3. **超目录必须显式标红** — 脚本自动做计费上限校验，超限即告警并拒绝线性外推
4. **系数连乘且来源可追溯** — 每个修正系数必须写明触发依据
5. **给区间不给点值** — 输出低/中/高三值，中值 = (低+高)/2
6. **不猜单价** — 必须用户显式给或从基准参数表取，且声明成本价 / 刊例价

---

## 安装

### 方式一：作为 Plugin 安装（推荐，可进 Skill Center）

整个 `bigdata-migration-assessment-pkg/` 目录就是一个标准 Claude Code Plugin：

```
bigdata-migration-assessment-pkg/
├── .claude-plugin/plugin.json
└── skills/bigdata-migration-assessment/
```

放入 Skill Center / Plugin 市场目录即可被发现。

### 方式二：单 Skill 直接安装

把 `skills/bigdata-migration-assessment/` 整个目录拷到：

- 个人级：`~/.claude/skills/bigdata-migration-assessment/`
- 项目级：`<项目>/.claude/skills/bigdata-migration-assessment/`

重启会话后可通过 `/bigdata-migration-assessment` 或自然语言触发。

**依赖**：`python3` + `openpyxl`（`pip install openpyxl`）。无其他依赖，不联网。

---

## 目录结构

```
skills/bigdata-migration-assessment/
├── SKILL.md                              三层模型 + 6 条 P0 纪律 + 执行步骤（步骤 0 强制输入校验）
├── references/
│   ├── baseline-params.md                等级表 / 修正系数 / 3 套阶段权重 / 岗位比例 / 单价
│   │                                     / 标准服务目录产能与计费上限 / 超上限替代算法 / 口径陷阱表
│   ├── scoring-rubric.md                 D1–D4 打分标尺 + 常见误判 + 异构迁移路径对照表
│   │                                     （AWS→腾讯云 19 条 + 阿里云/自建 8 条）
│   └── customer-info-checklist.md        待客户确认清单模板 P0/P1/P2（25 项）+ 降本杠杆量化写法
├── scripts/
│   ├── bd_assess.py                      确定性三层模型计算器 → 6 页 xlsx
│   └── inject_v7.py                      回写《应用复杂度评估 V7》体系工作簿
└── examples/
    └── envision-input.json               真实案例输入（AWS→腾讯云，20PB 数据湖），可直接当模板改
```

---

## 快速上手

### 1. 复制样例输入改数

```bash
cp skills/bigdata-migration-assessment/examples/envision-input.json ./my-project.json
```

输入契约主要字段：

| 字段 | 说明 |
|---|---|
| `coefficients` | `automation` / `doc` / `bandwidth` / `compliance` / `other`，取值依据见 baseline-params.md |
| `model1_units[]` | `{group, name, d1..d4, note}`，note 必须写打分依据 |
| `model2_resources[]` | `{item, qty, unit}`，item 命中标准目录则自动取产能；不在目录则报错提示移到 model3 |
| `model2_alternatives[]` | 超上限项的替代算法人天，必须给 `basis` |
| `bandwidth_scenarios[]` | 带宽场景，用于出日历工期表 |
| `model3_items[]` | `{category, item, qty, rate}` 或直接给 `man_days` |
| `comparisons[]` | 差异对比口径 + 根因 |
| `levers[]` | 降本杠杆 |
| `open_items[]` | 待客户确认清单 |

### 2. 跑计算

```bash
# 先只看数字
python3 skills/bigdata-migration-assessment/scripts/bd_assess.py \
  --config my-project.json --print-only

# 出工作簿
python3 skills/bigdata-migration-assessment/scripts/bd_assess.py \
  --config my-project.json --out 客户名-大数据人力评估.xlsx
```

输出固定 6 页：`01-评估模型说明` / `02-模型1·复杂度分级` / `03-模型2·标准服务目录` / `04-模型3·超服务目录项` / `05-汇总·阶段·岗位·成本` / `06-待客户确认清单`。

### 3.（可选）回写既有评估表

若项目已在用《应用复杂度评估 V7》体系的工作簿：

```bash
python3 skills/bigdata-migration-assessment/scripts/inject_v7.py \
  --workbook "应用复杂度评估 V7.xlsx" \
  --config my-project.json \
  --out "应用复杂度评估 V7-含大数据评估.xlsx" \
  --team "团队4-大数据"
```

脚本只填 A–G、M–Q、AC、AD 列，**不动原表任何公式**，等级/人天/阶段拆分由原生公式链自行计算；并追加一页 `大数据评估说明`。

> openpyxl 不计算公式，用 Excel / WPS 打开一次即可触发重算。

---

## 失败即拒绝（脚本行为）

脚本遵守"缺输入就 BLOCKED，绝不猜数"：

| 场景 | 行为 |
|---|---|
| 模型1 单元缺 D 分 | `BLOCKED: 模型1 单元缺字段 d3: {...}`，退出码 2 |
| D 分不在 1–5 | `BLOCKED`，退出码 2 |
| 目录外工作项塞进 `model2_resources` | `BLOCKED: ... 不在标准服务目录，且未显式给 rate。若确属目录外工作，请移到 model3_items` |
| 模型3 条目既无 `rate` 又无 `man_days` | `BLOCKED`，退出码 2 |
| 三层输入全空 | `BLOCKED: 三层输入全空，无可测算内容` |
| 资源量超计费上限 | 不阻断，但打印 `!! 超计费上限: xxx 超 184.2×，线性外推 9429.40 人天不成立`，并在工作簿中标红单列 |

---

## 实测基准（回归用例）

样例输入 `examples/envision-input.json`（AWS→腾讯云，18858.8 TB 对象存储 + 9800 表元数据 + 4065 条 Spark ETL）：

```
模型1  低 538.50  中 703.50  高 868.50
模型2  目录内 159.37 ×1.2 = 191.24  + 替代 26.05 = 217.29
  !! 超计费上限: 对象存储(按量) 超 184.2×，线性外推 9429.40 人天不成立
  !! 超计费上限: 存储迁移(非对象) 超 3.1×，线性外推 316.60 人天不成立
模型3  453.34 （29 项，全部需单独商务谈判）
合计   低 1209.13  中 1374.13  高 1539.13 人天 = 62.46 人月
成本价 ¥3,433,980   刊例价 ¥4,442,831
```

**改动 `references/baseline-params.md` 后请用本用例回归**，数字对不上说明基准参数被动过——那等于改了报价口径，需商务同意。

---

## 版本与维护

| 版本 | 变更 |
|---|---|
| 1.0.0 | 首版。三层模型、两个脚本、三份参考、一个真实案例样例 |

**维护约定**：
- `references/baseline-params.md` 是报价口径的唯一真相源，改它等于改口径
- 新增异构迁移路径（如新云厂商对端）请补进 `references/scoring-rubric.md` 的对照表
- 新增标准计费项请同时改 `baseline-params.md` 表格与 `scripts/bd_assess.py` 的 `CATALOG` 常量，两处必须一致
