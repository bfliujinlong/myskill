# 中东（迪拜）客户报价 / 人天评估 专用工作流

固化于 2026-08-21，基于用户反复纠正后沉淀。一句话触发：「按 Fintech 模板出中东迪拜客户报价（中英文）」或「出中东人天评估报告（A/B/C 三档中英文）」。

## 固定资产（路径别改）

| 资产 | 路径 |
|---|---|
| Fintech 报价模板（英文，Arial Unicode MS） | `~/cloud-docs/客户报价单/Fintech Quotation_LZ&Migration_EN_V1.1_updated (1).xlsx` |
| 奥芯明 OA 工作量模板（Calibri 10，两行表头+分组留空） | `/home/ubuntu/.hermes/cache/documents/doc_be0464d73f53_奥芯明单应用（OA）工作量预估 副本 V20260810.xlsx` |
| Scope 数据源（AWS→阿里云 Dubai 资源清单 html） | `~/cloud-docs/LZ迁移方案/f-customer-migration-checklist.html` |
| 输出目录 | `~/cloud-docs/客户报价单/` |
| 发件 chat | `telegram:5701842056` |

## 报价单（LZ轻量+迁移+运维，中英文各一）

**结构（严格克隆 Fintech 模板，不新建 workbook）**：
- Sheet1 Landing Zone：轻量 $8,000（一次性，只配账号/权限/网络核心，不套全量八大模块）
- Sheet2 Migration：按 OA 6 阶段拆行（调研/设计/POC/实施/割接/验收），轻量档 40 人天 × $235 = $9,400（≤$2万上限）。数字可换 A/B/C 档
- Sheet3 Scope：用 f-customer-migration-checklist.html 真实内容填（AWS源环境 + 阿里云目标架构），不保留模板占位英文
- Sheet4 Managed Service (Ops)：复制 Migration 样式新增，运维 $100/VM/月（标准实例），非阿里中间件 +10~15%，参考奥芯明运维结构英文翻译

**铁律**：
1. `shutil.copyfile(模板, OUT)` 再只改值，保留 Arial 字体/合并/公式
2. Migration 拆行前先 `unmerge_cells` 数据区（14-30行）再写，避免 MergedCell 报错
3. 写公式后必 `soffice --headless --calc --convert-to xlsx` 重算缓存（否则手机显空白）
4. 中文版清掉模板自带英文标签（B5 `Customer Name:`→`客户名称：`、B20 note 翻译）
5. 中英文各一份，`hermes send -t telegram:5701842056 "说明 MEDIA:绝对路径"`

## 人天评估报告（A/B/C 三档，中英文各一）

**三档**（阶段比例固定，总量不同）：
- A 轻量（极小，纯迁移）：30 人天 → $7,050
- B 轻量（小，含轻量 POC）：40 人天 → $9,400
- C 轻量（中小，含设计+POC+割接）：50 人天 → $11,750
- 阶段人天：A=[4,8,6,8,3,1] / B=[5,10,8,12,4,1] / C=[6,13,10,15,5,1]
- 单价 $235/人天

**格式（严格克隆 OA 模板，不是自造）**：
- 两行表头：E1:H1 合并写「职位-工作量（人天）」，E2:H2 是 4 角色子表头
- 分组留空：B 列项目名仅首行写、C 列阶段仅每组首行写，同组 `merge_cells` 合并（C3:C5 等）
- 角色分配：`survey(3,1,0,0) design(3,4,2,1) poc(3,3,1,1) impl(2,8,2,0) cutover(1,2,1,0) accept(0,0,2,0)`，差额补到工程师列
- 底部 G26=远程 G27=现场20% G28=现场50%，H 列 `=H26*1.2/*1.5`，E24:H24 `=SUM(E3:E22)`
- 字体 Calibri 10，列宽 C=19 D=34
- 清数据区只清 B3:H23，保留底部公式行

文件名：`中东迪拜客户_人天评估报告_{A/B/C}_{CN/EN}.xlsx`

## 一键出全套（建议做法）

报价单 + 人天报告同时出，中英文各发。发前必须 LibreOffice 重算。

## 已知坑（本会话实战）

- openpyxl 写公式不计算结果 → soffice 重算
- 合并单元格写值报错 → unmerge 数据区
- 中文版残留英文 → 全扫 `[A-Za-z]{4,}` 含 Note/Customer/Billing 等翻译
- 大量人天（75）被用户打回「太多」→ 小体量用三档
- soffice 重算覆盖写回可能被审批拦截 → 先告知用户等确认
