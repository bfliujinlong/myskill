# KB Manifest 机制 · 影子验证记录（2026-09-07）

## 机制（替代原 M10 的"写死校验脚本"）

```
插件侧（不变量）                KB 侧（变量，KB Owner 维护）
────────────────────           ─────────────────────────────
锚点文件名 STRUCTURE.yaml   ←→  STRUCTURE.yaml（zones/assets/aliases/contract_version）
语义键注册表 REQUIRED_KEYS      路径映射、改名历史、L1/L2 标记
resolve_kb.py（adapters/）
```

## 四场景实测

| 场景 | 模拟 | resolver 行为 | 结果 |
|------|------|--------------|------|
| A | 当前真实 KB（无 manifest） | BLOCK exit 3："缺少锚点文件，不扫描不猜不用内置快照兜底" | ✅ 正确拒绝 |
| B | manifest 就位（当前结构） | 全量体检：8 zone + 5 asset 全 OK，missing_keys 无 | ✅ |
| C | **KB 改名 07-资质与案例证据 + 换索引文件，manifest 改 2 行，插件 0 改动** | 两键解析均 OK（新路径 exists=true） | ✅ **核心证明** |
| D | KB 改名但忘改 manifest | WARN exists=false 当场暴露漂移 | ✅ |

## 对 M 清单的影响

- **M10 作废重定义**：check_kb_contract.sh（写死路径快照）废弃 → 由 manifest 机制替代；
- M1/M4/M7 从"改路径字符串"升级为"改用语义键"：Agent 约定 2 与 Skill 步骤中的路径全部换成 `resolve_kb.py --key xxx` 的解析结果；
- M5（policy 先行）不变，policy 文件名列表由 manifest `policies.dir_policy_files` 提供；
- M9 版本号建议顺延：这批改动并入 **rc.7**（契约代数 v1→v2 是 KB 侧声明，不占插件版本）。

## 分工（Dev / KB 两条线）

| 侧 | 动作 | 何时 |
|----|------|------|
| KB 仓库 | 在根新增 `STRUCTURE.yaml`（可从本草稿直接取，删 aliases 收尾后清理） | 下次周同步 |
| 插件 Dev | `adapters/kb-manifest/resolve_kb.py` 入 adapters；Agent 约定 2 改为锚点+语义键描述；各 Skill 路径改语义键 | rc.7 施工 |
| 协商 | 新增语义键 = 插件能力诉求 → 提插件仓库；破坏性变更升 contract_version | 持续 |

---

## 二、consume/discover 分离机制（2026-09-07 第二轮，回应用户口述需求）

> 用户需求：「KB 更新素材地图就好；插件决定用什么；注册表没有时重新扫描读取最新素材 + 提醒更新 RC 迭代」。
> 采纳：KB 侧只更新 manifest（素材地图）✅；插件决定消费 ✅；发现→报告→RC 迭代闭环 ✅。
> 修正：**"扫描后自动读取"改为"扫描后报告 + 逃生门"**——新类型素材缺消费语义（哪个 Skill/什么纪律），自动消费 = 无纪律上下文的静默绑定（典型事故：SLA 承诺库数字流入新标书，违反 SLA 不自造）。晚拿到素材是成本，绑错素材是事故。

### 机制定稿

```
consume（消费）                  discover（发现）
只走注册语义键                    只读扫描 manifest
未注册键 → BLOCK                 新键 → 报告 + RC 迭代建议
不扫描/不猜/不兜底                broken → 提醒 KB 修 manifest
                                不绑定/不消费
逃生门：用户显式指定路径 → 本次会话可用（语义由人断言）→ 下 RC 固化为语义键
```

### 场景5–8 实测（resolver v2）

| 场景 | 模拟 | 结果 |
|------|------|------|
| 5 | consume 注册键（case_index/sla_master） | OK，路径来自 manifest（KB 改地图即生效） |
| 6 | consume 完全未知的键 | BLOCK，提示两条出路（显式注入 / discover 报告） |
| 7 | KB 在 manifest 加新素材（security_compliance_master），跑 --discover | 报告进 new_assets + proposal（"建议加入下一 RC 注册表"）+ escape_hatch 说明；registered_ok 5 键正常 |
| 8 | consume 该新键 | **BLOCK**——discover 报告 ≠ 消费授权（首轮脚本此处有绕过 bug：assets 分支漏注册表校验，已修复并回归验证） |

### 发现的自身缺陷（本轮真实 catch，证明影子验证必要性）

- **Bug**：首轮 resolver 的 assets 分支只查"manifest 里有没有"，没查"插件注册表里有没有"——manifest 新键可绕过注册表直接消费，恰好复现了要防的事故路径。已修复：assets 分支补 `key not in REGISTRY → BLOCK`。回归：注册键不受影响。

### 需求满足对照

| 用户诉求 | 满足方式 |
|---------|---------|
| KB 只更新素材地图 | manifest 即素材地图，KB 改 1 行 = 生效 |
| 插件决定用什么 | REGISTRY 在插件侧，RC 发版 = 注册新消费语义 |
| 注册表没有 → 拿到最新素材 | **不自动读**（防无纪律消费）；提供 discover 报告 + 用户显式路径逃生门，当次会话即可用 |
| 提醒更新，RC 迭代 | discover 的 proposal 自动生成"建议注册清单"，Dev 机械施工 |

---

## 三、产品决策记录（2026-09-07 第三轮）

**决策**：显式注入逃生门**全开**——不加白名单、不加数量配额、不限制路径。
**理由**（用户原话）：现阶段目标是让大家把售前 Skill 用起来、觉得好用；限制堆多了产出自薄，就没人在真实打单中使用了。
**架构含义**：把关从入口（读取限制）移到出口（外发前脱敏门禁，KB GOVERNANCE 已有），与"成品是缓存不是资产"的治理模型一致。
**推广配套**：演示套件已建（`07_临时工作区/演示套件-全链demo/`）——一键脚本 + 3 个夹具（沟通记录/RFP/报价参数），虚拟客户全链路 5 分钟出 8 工件。

---

## 四、"范围锚定式丰满"原则（2026-09-07 第四轮，用户核心纠偏）

**用户原话要义**：丰满的前提是方案准确——RFP 有准确要求和应标策略，据此做服务目录映射和案例佐证；不是全部 load 进来导致 scope 过大承诺。要"准确前提下的内部丰满"，不是"为篇幅多而多"。

**原则固化**：
1. 链路唯一合法顺序：RFP→策略→In-Scope 锁定→项级映射→项级佐证（不得倒置）；
2. 母版 = 反查字典（按 In-Scope 项查结构），不是填充素材库（126 条不许整表入方案）；
3. 案例 = 项级佐证（代号+量化事实+历史参考口径），不是案例级搬运（整报告不进方案）；
4. 丰满度度量 = 映射覆盖率 × 佐证覆盖率（趋近 1），不是页数/条目数；
5. 反面模式清单写入 Skill 自检（案例整包/母版全量/为篇幅加节/佐证承诺化）。

**影子验证**：影子服务方案-范围锚定丰满-rc7验证件.md —— 3 项 In-Scope 不变（范围守恒 ✅），映射 5 条母版编号（实存核对通过）+ 佐证 4 条（与索引-新版逐字核对通过），无主题漂移。
**同时作废**：第三轮讨论中"案例自动佐证行（案例级自动嵌入）"的提法——方向相反，以本轮为准。

---

## 五、v2 素材键补齐 + CORE/OPTIONAL 分层（2026-09-12，随 rc.9 对外方案层）

**背景**：新增 ms-technical-proposal（对外技术方案书），其步骤 0.5 需消费公司介绍/资质、投标章节素材、架构图等对外素材键；原注册表只有内部 5 键。

**改动（插件侧 REGISTRY）**：新增 4 键
| 键 | 用途 | 消费方 |
|----|------|--------|
| `company_intro` | 公司介绍 + 资质清单 | technical-proposal 01章 / rfp-analyze 资质匹配 |
| `bid_chapters` | 服务型投标章节素材 | technical-proposal 分段生成参考 |
| `architecture_images` | 部署/服务架构图 | technical-proposal 图示层 |
| `tender_templates` | 招标模板库 | rfp-analyze 结构对位 |

**分层修正（解决"全 REQUIRED 噪声"）**：
- `REQUIRED = tuple(REGISTRY)` 原为死变量（consume 用 `for k in REGISTRY` 全量判缺，所有键缺失都进 missing_keys→WARN）；
- 改为 **CORE**（case_index / service_catalog_master / sla_master）缺失才 WARN；
- **OPTIONAL**（sow_libraries / bidding_narrative + 4 新键）按交付物触发，缺失进 `missing_optional`（提示"待补充"，不拉低整体 level）；
- consume 报告每条 asset 标 `tier: core|optional`；discover 增 `optional_unmapped`（KB 侧尚未提供路径的 OPTIONAL 键，属正常非漂移）。

**KB 侧待办（不占插件版本）**：KB Owner 在 STRUCTURE.yaml 的 `assets` 增这 4 键的路径映射后即生效；未提供时 technical-proposal 步骤 0.5 按"未注入→WARN 待补充，不虚构"降级。

**回归**：`python3 -c "import ast; ast.parse(...)"` 语法通过；消费语义不变（未注册键仍 BLOCK，逃生门不变）。
