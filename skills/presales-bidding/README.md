# PCS 售前 Skill 包（Axon 导入用）

安畅 PCS 服务型 New Bidding 的售前 Skill 集合，共 **13 个 Skill**：7 个售前交付物 Skill（来自 `pcs-presales-text-cycle` 插件 v0.1.0-rc.10）+ 6 个知识库脱敏 Skill（来自 PCS 售前知识库 `00-系统说明与索引/脱敏Skills/`）。

## 包结构

```
<skill-name>/
├── SKILL.md            # Skill 定义（YAML frontmatter: name + description）
├── references/         # 输出模板 + contract.json 契约 + 适配点 + 参考实例
├── scripts/            # 确定性脚本（python3）
├── templates/          # 目录/报告模板
└── examples/           # 输入参数示例

_shared/
├── 脱敏-标识符规则参考.md     # 6 个脱敏 Skill 共享的标识符替换规则
├── AGENT-pcs-pre-sale.md     # 售前编排 Agent（纪律 + 调用时序），支持 Agent 的平台可一并导入
└── adapters/                 # Company KB 路径解析适配层（显式注入，不猜路径）
```

---

## 一、7 个售前 Skill

| # | Skill | 做什么 | 触发词 | 输出位置 |
|:--:|-------|--------|--------|---------|
| 1 | `ms-project-init` | 建七区项目骨架 + `project.yaml` | 初始化项目 / 新建 Workspace / 检查项目结构 | Workspace 根 |
| 2 | `ms-customer-communication` | 把粘贴的客户沟通文字整理成结构化沟通记录 | 会议纪要 / 客户沟通 / 沟通记录 | `01_客户输入/03_会议访谈与沟通/` |
| 3 | `ms-rfp-analyze` | RFP 逐条拆成要求清单（R01–Rnn）+ 招标分析报告（资质/覆盖度/评分/竞争/投标决策） | RFP分析 / 招标分析 / 需求拆解 / 要不要投 | `03_方案与应答/02_RFP应答与总控/` |
| 4 | `ms-service-solution` | 内化应标策略（赢单主线/取舍/不承诺项）→ 范围锚定的服务方案 | 服务方案 / 方案设计 / 应标策略 | `03_方案与应答/01_服务方案/01_共通设计/` |
| 5 | `ms-technical-proposal` | 分段生成对外投标技术方案书章节（01~09+附录）→ 整合 → 四维自检 | 投标技术方案 / 技术标书 / 技术方案书 | `03_方案与应答/01_服务方案/技术方案/[项目代号]/` |
| 6 | `ms-pricing-support` | 显式参数经脚本确定性计算，产报价测算表 | 报价测算 / 价格测算 / pricing | `04_商务与合同/01_报价与测算/` |
| 7 | `ms-sow-support` | 方案 + 报价汇总为 SOW，范围守恒 | SOW / 工作说明书 / 范围定义 | `04_商务与合同/03_Service-Catalog与SOW/` |

### 调用时序（主线）

```
ms-project-init                        ← 一切前置，没有 project.yaml 则全部 BLOCKED
   └─ ms-rfp-analyze                   ← 要求清单 + 投标决策 PROCEED/HOLD/DECLINE
        └─ ms-service-solution         ← 以 RFP 要求清单为覆盖契约（缺则 BLOCKED）
             └─ ms-technical-proposal  ← 以服务方案六段工作稿为分段生成基准
             └─ ms-pricing-support     ← 以方案范围为报价基准
                  └─ ms-sow-support    ← 范围必须是方案 In-Scope 的子集或等集

ms-customer-communication              ← 旁路，任意阶段吸收客户澄清（含 pre-RFP 沟通）
```

### 使用方法（典型一轮应答）

```text
1) 初始化
   「初始化项目」→ 逐项确认 project_id / customer_name / opportunity_name /
   engagement_type（managed-service | build-implementation |
   consulting-assessment | hybrid-integration）/ owner / sensitivity
   未确认字段保持 unconfirmed，不推断。

2) 招标分析
   把 RFP 原文粘贴或放到 01_客户输入/01_RFP与采购文件/，说「做 RFP 分析」。
   产出两份物理分离的文件：要求清单（只提取不评估）+ 招标分析报告（我方视角判断）。

3) 服务方案
   「写服务方案」→ Skill 先内化应标策略（步骤 0.52），再按 RFP 清单逐条覆盖。
   SLA 数字只引用 KB 权威值或标「待商务/交付确认」。

4) 对外技术方案书
   「写投标技术方案」→ 分章节生成后用 scripts/merge_chapters.py 整合。
   每个数字必须标源：<客户文件>/<版本·日期> 或「待商务/客户确认」。

5) 报价
   准备 examples/pricing-input.json 同构的参数 JSON（quantity / unit_price
   必须是显式数字），「做报价测算」。

6) SOW
   「写 SOW」→ 汇总方案 + 报价；上游冲突时 BLOCKED，不静默修正。
```

### 脚本（需平台开启代码执行权限）

```bash
# 项目初始化 / 检查 / 补齐
python3 ms-project-init/scripts/init_workspace.py \
  --mode init|inspect|repair --workspace "$PWD" \
  --config /path/to/confirmed-project-input.json \
  --company-kb-path "$KB_PATH"

python3 ms-project-init/scripts/validate_workspace.py \
  --workspace "$PWD" --engagement-type managed-service --company-kb-path "$KB_PATH"

# 报价确定性计算（退出码非 0 = 参数不全，必须 BLOCKED，不得手工凑数）
python3 ms-pricing-support/scripts/compute_pricing.py --config pricing-input.json

# 技术方案书章节整合
python3 ms-technical-proposal/scripts/merge_chapters.py --dir <技术方案目录>

# Company KB 路径解析（只接受显式注入，不扫描、不猜目录）
python3 _shared/adapters/knodo/company_kb_resolver.py --company-kb-path <KB路径>
PCS_COMPANY_KB_PATH=<KB路径> python3 _shared/adapters/knodo/company_kb_resolver.py
```

### 运行前提

1. **当前目录必须是已初始化的 PCS Project**（根有 `project.yaml`），否则所有 Skill 输出 `BLOCKED`；
2. **Company KB 需显式注入路径**（`--company-kb-path` 或 `PCS_COMPANY_KB_PATH`）。Skill 不扫描 Workspace、不按目录名猜测、不虚构默认路径；未注入则 WARN 并把权威数字标「待确认」；
3. KB 为**只读**挂载，严禁写入；受限区（`06-项目材料-受限`，access L2）Skill 一律不读；
4. 案例检索唯一入口：`04-脱敏案例库/案例索引-新版.md`（旧版 `案例索引.md` 已废弃）；
5. Python 3 可用。

### 核心纪律（违反即 BLOCK）

- **确定性报价** — 价格数字只能来自显式输入 + 脚本计算，不推断单价、不套默认价目；
- **范围守恒** — SOW ⊆ 服务方案 In-Scope；下游不得扩大上游范围；
- **SLA 不自造** — 只引用 KB 权威值或标「待确认」；
- **上游一致性** — 上下游冲突 → `BLOCKED`，不静默修正；
- **只提取不补造** — RFP 要求清单只抄采购方要求，我方判断另存到分析报告；
- **不覆盖** — 目标文件已存在即 BLOCKED；所有写入 create-if-missing；
- **默认 PREVIEW** — 先出预览，用户确认后才落盘；
- **内部痕迹不外泄** — 纠错史、内部代号、KB 内部路径不进客户交付物。

---

## 二、6 个脱敏 Skill

把 L2 受限原件加工成 L1 可自动加载的脱敏版本，按文件格式分工：

| Skill | 处理格式 | 依赖 | 覆盖面 |
|-------|---------|------|--------|
| `ms-desensitize-markdown` | `.md` | — | 正文全文 |
| `ms-desensitize-word` | `.docx` | python-docx | 正文、表格、页眉页脚、批注、文本框、文档属性 |
| `ms-desensitize-excel` | `.xlsx` | openpyxl | 所有 Sheet、单元格、图表标题、批注（保留公式与数值） |
| `ms-desensitize-ppt` | `.pptx` | python-pptx | 所有幻灯片、文本框、表格、备注 |
| `ms-desensitize-pdf` | `.pdf` | pdfplumber / PyPDF2 / reportlab（扫描版另需 OCR） | 提取 → 脱敏 → 重新生成 |
| `ms-desensitize-design-doc` | HLD/LLD（md/docx） | 同上 | 网络拓扑、IP 规划、主机名、配置块、安全策略 |

### 使用方法

```text
1) 前置检查：源文件在 L2 区、目标目录在 L1 区，读两侧 .kb-policy.yaml；
2) 按格式选对应 Skill，依 _shared/脱敏-标识符规则参考.md 做替换；
3) 验证：重新打开成品，搜索真实客户名/IP/域名应无命中；SLA 数值、公式、
   RACI 矩阵应完整保留；
4) 重命名输出：<主题>-<客户代号>-脱敏.<ext>；
5) 成品头部写 desensitize-meta 溯源块（原件路径 + rule-version）。
```

### 核心原则

> **脱敏的对象是「标识符」，不是「信息」。**

- 必须替换：客户名、IP、主机名、账号、邮箱、AK/SK、域名、实例/集群名、联系人；
- 必须保留：SLA 数值、指标结构、排除条款、计算方法、规模基线、RACI 矩阵、计价公式；
- **成品是缓存不是资产** — 发现漏脱/脱过头，不改成品：先修规则（递增 rule-version），再从原件重新生成；按 `rule-version` grep 定位待重生成清单。

---

## 导入说明

每个 Skill 目录自带 `SKILL.md`（YAML frontmatter 含 `name`、`description`），符合 Agent Skills 通用格式。若 Axon 要求「一个 zip = 一个 Skill」，直接把对应子目录单独压缩即可（注意 6 个脱敏 Skill 需随包携带 `_shared/脱敏-标识符规则参考.md`）。
