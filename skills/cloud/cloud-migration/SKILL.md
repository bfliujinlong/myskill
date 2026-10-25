---
name: cloud-migration
description: "云迁移：评估、6R策略、迁移计划、割接与回滚、成本与风险管控。"
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [云迁移, 上云, 搬迁, 割接, 6R, migration]
    related_skills: [project-manager, presales-architect, multi-cloud]
---

# 云迁移（Cloud Migration）

## When to Use（何时使用）

- 客户要从 IDC/友商云迁移到目标云（如阿里云/华为云/AWS/GCP）
- 需要做迁移评估、制定 6R 策略、排迁移计划
- 涉及割接窗口、回滚预案、数据一致性校验
- 迁移后成本对比、优化建议

## 标准工作流

### 1. 现状盘点（发现）
- 资源清单：计算/存储/网络/数据库/中间件/依赖的第三方服务
- 耦合关系：调用链、数据流向、强依赖
- 量级：数据量、QPS、峰值、合规要求（等保/数据出境）
- 工具：各云都提供迁移中心/ATF（应用迁移服务）

### 2. 6R 策略定级
| 策略 | 含义 | 适用 |
|------|------|------|
| Rehost 重新托管 | 直接搬（lift-shift） | 紧急上云、标准化应用 |
| Replatform 平台重构 | 小改适配托管服务 | 想减负运维 |
| Refactor 重构 | 云原生改造 | 长期成本/弹性诉求 |
| Repurchase 替换 | 换 SaaS | 非核心系统 |
| Retain 保留 | 暂不移 | 合规/依赖未清 |
| Retire 退役 | 下线 | 僵尸系统 |

### 3. 迁移计划模板
- 分批：先非核心→核心；先只读→读写
- 每批：评估→改造→演练→割接→观察
- 割接窗口：选低峰，明确起止、负责人、通讯群
- 回滚：数据快照/镜像前置，5 分钟内可回退

### 4. 割接检查清单
- [ ] 全量+增量数据同步完成，差异<阈值
- [ ] 一致性校验脚本通过
- [ ] DNS/网关切换预案就绪
- [ ] 旧环境保留可回滚（不立即销毁）
- [ ] 监控告警覆盖新环境
- [ ] 业务方验收口径一致

### 5. 成本对比
迁移前后 TCO：一次性（迁移人天）+ 月度（资源+流量+运维）对比，量化上云收益。

## 6. 数据一致性双跑验证评审（交付物审查，高频）

迁移双跑/灰度期，客户或团队会产出"双跑验证计划与数据测试报告"类 xlsx（分层：ODS/DW/DM/SR/Hive核心/分区/推送任务/不可双跑等）。**这类表本质是结果登记的 tracker，常常名实不符、开口项未闭环**——作为 FDE 要把它审成可交付物。审查步骤：

1. **全覆盖**：用 openpyxl 逐 sheet 读，对每个状态列（名称可能为 验证状态/状态/结论/是否一致/割接上线状态/对象级校验状态/复核）做 `collections.Counter` 分布统计。一眼看出通过/未通过/无需割接占比。
2. **开口项（open items）闭环检查**：筛出「责任人 且 是否已修复 同时为空」的行——尤其当 失败字段数 高或 最低/平均一致率<90% 时，这是真风险。底稿里常占绝大多数（实测某 208 行 sheet 有 193 行开口、93 行低一致率且无人认领）。
3. **总览 vs 明细 叙事缺口**：总览判"通过"但明细有"不通过/不通过(复核:不用处理)"——要在报告正文用一句话统一解释为什么明细不通过仍算总体通过。
4. **白名单审计**：不一致行若全非白名单（既没加白也没填原因/修复），属未决，必须单列。
5. **真开口风险上提**：不可双跑/推送任务里 任务未通过 / 未上线（库表名变化等）节点，别被"已上线"多数淹没，单独拎出跟踪清单。
6. **格式健康度**：日期格式（20260807 / 2026-08-07 / 2026.08.04 混用）、状态词十余种、表尾 `None` 占位列——统一后才能交客户。

**升级成交付物三件事**（可让 Hermes 自动做）：① 补"报告正文"三页（范围/方法论/总体结论与遗留风险）；② 从 xlsx 自动抽"闭环清单"（已修复/可接受附理由/仍开口附责任人+计划日）；③ 清洗格式。

### 直接可跑的 openpyxl 审计脚本

```python
import openpyxl, collections
PATH = "/tmp/shuangpao.xlsx"  # 换成实际文件
wb = openpyxl.load_workbook(PATH, data_only=True)
STATUS_NAMES = ["验证状态","状态","结论","是否一致","割接上线状态",
                "对象级校验状态","复核"]
def col_index(hdr, name_part):
    for i,h in enumerate(hdr):
        if h and name_part in str(h): return i
    return None
for ws in wb.worksheets:
    rows = list(ws.iter_rows(values_only=True))
    if len(rows) < 2: continue
    hdr = rows[0]
    print(f"\n=== {ws.title} ({len(rows)-1} 数据行) ===")
    for name in STATUS_NAMES:
        ci = col_index(hdr, name)
        if ci is None: continue
        cnt = collections.Counter(
            ("" if r[ci] is None else str(r[ci])) for r in rows[1:])
        print(f"  [{name}] {cnt.most_common(12)}")

# 开口项检测（适用"导入sr-非核心"类 sheet）
ws = wb["导入sr-非核心"]  # 换成实际 sheet 名
rows = list(ws.iter_rows(values_only=True)); hdr = rows[0]
cm = {h:i for i,h in enumerate(hdr) if h}
src, fail = cm["源表"], cm["失败字段数"]
minc, avg = cm["最低一致率"], cm["平均一致率"]
owner, fixed = cm["责任人"], cm["是否已修复"]
blank = low_no_owner = 0
for r in rows[1:]:
    o, fx = r[owner], r[fixed]
    if (o is None or str(o).strip()=="") and (fx is None or str(fx).strip()==""):
        blank += 1
    try: avn = float(r[avg]) if r[avg] not in (None,"") else 100
    except: avn = 100
    if avn < 90 and (o is None or str(o).strip()==""):
        low_no_owner += 1
print(f"\n开口项(责任人+是否已修复同空): {blank}, 均一致率<90%无人认领: {low_no_owner}")
```

## 常见陷阱
- 只搬主机不搬依赖，割接后连环故障
- 数据增量没算清，割接丢数据
- 旧环境割完立刻销毁，回滚无门
- 低估跨云网络成本（出网流量/专线）
- 双跑报告只登记不结论：开口项无人认领、总览判通过但明细不通过未解释、低一致率表淹没在"已上线"多数里
