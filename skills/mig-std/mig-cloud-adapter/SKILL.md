---
name: mig-cloud-adapter
description: "项目启动阶段，当用户要求「采集云上资源/核对清单/查真实配置」时，按源云类型分派到对应云的 MCP 服务器，只读采集并输出统一 Inventory JSON。触发条件：已有云账号凭据、要求采集源端真实资源、核对系统清单与云上实际是否一致。能力边界：只做只读采集与统一格式输出，不做规模评估与选型（mig-resource-assessment）、不修改任何云上资源、不做写操作。"
依赖工具: [mcp__alicloud, mcp__aws, mcp__azure, mcp__hwecs, mcp__hwrds, mcp__hwevs, mcp__hwvpc, mcp__hwobs, mcp__awslabs_aws_pricing_mcp_server__get_pricing, read_file, write_file, terminal]
风险等级: 只读
skill依赖: []
输入: 源云类型 + regions[] + expected_ids[] + 云账号凭据（必填）
输出: inventory.json（统一格式）
上游: mig-resource-assessment
下游: 无（适配层是最底层）
版本: 2026-10-27.001
维护者: jinlongliu
最后校验: 2026-10-27
---

# 云资源适配层

## 定位

四阶段流水线最底层。把各云厂商差异封装掉，向上只吐统一格式的 Inventory JSON。

```
mig-resource-assessment（要数据）
        │
        ▼
mig-cloud-adapter（分派 + 采集 + 归一化）
        │
        ▼
  各云 MCP 服务器（真实调用）
```

上游调我，我不调上游。

## 必填输入

| 输入 | 来源 | 缺失时 |
|---|---|---|
| `cloud` | 上游传入 | 反问，不猜 |
| `regions[]` | 项目信息表 | 反问，不猜 |
| `expected_ids[]` | 系统清单 | 允许空（全量采集模式） |
| 凭据 | 环境/凭据文件 | **报错停止，不猜不编** |

## 分派矩阵（实测 2026-10-27 全部握手通过）

| 源云 | MCP 标识符 | 实测工具数 | 覆盖 |
|---|---|---|---|
| 阿里云 | `mcp__alicloud` | 26 | ECS/RDS/OSS 等 |
| AWS | `mcp__aws` | 2 | `call_aws` 通用透传 |
| Azure | `mcp__azure` | 71 | 全服务分组 |
| 华为云 ECS | `mcp__hwecs` | 106 | 计算 |
| 华为云 RDS | `mcp__hwrds` | 232 | 数据库 |
| 华为云 EVS | `mcp__hwevs` | 31 | 云硬盘 |
| 华为云 VPC | `mcp__hwvpc` | 184 | 网络 |
| 华为云 OBS | `mcp__hwobs` | 81 | 对象存储 |

> 华为云是**分服务 MCP**，五个都要调，不能只调一个。
> AWS 只有 2 个工具，`call_aws` 走 CLI 透传，参数按 AWS CLI 语法拼。

## 归一化输出

统一 Inventory JSON，字段固定，缺值写 `null` + 进 `gaps`：

```json
{
  "cloud": "huaweicloud",
  "regions": ["cn-north-4"],
  "collected": [
    {"id": "vm-001", "domain": "compute", "region": "cn-north-4",
     "spec": "s6.large.2", "cpu": 2, "mem_gb": 8, "disk_gb": 100}
  ],
  "gaps": [
    {"id": "db-003", "reason": "只读账号无该地域权限", "domain": "database"}
  ],
  "collected_at": "2026-10-27T14:20:00+08:00"
}
```

`domain` 取值固定：`compute` / `database` / `storage` / `network` / `other`。

## 执行步骤

1. 校验输入齐不齐，缺凭据**立即停止**
2. 按上表选 MCP 标识符（华为云选全部五个）
3. 只读采集，逐个地域拉清单
4. 归一化成统一 JSON
5. 跑 `scripts/aggregate.py` 算覆盖率
6. 写入 `inventory.json`

## 硬约束

- **只读**：不调任何写操作工具（`RunInstances` / `PutObject` / `DeleteXxx` 一律禁用）
- **不猜数据**：采不到就进 `gaps`，绝不填占位值
- **不编凭据**：凭据缺失报错停止，不编造 AccessKey
- 采集结果落 `inventory.json`，不进聊天正文

## 输出双形态

### 结构化 JSON（schema 固定）

```json
{
  "skill": "mig-cloud-adapter",
  "conclusion": "complete | partial | failed",
  "confidence": 0.0,
  "confidence_reason": "",
  "cloud": "",
  "coverage": 0.0,
  "collected_count": 0,
  "gaps": [{"id": "", "reason": "", "domain": ""}],
  "inventory_ref": "",
  "suggested_actions": [],
  "escalation": {
    "required": false,
    "reason": "",
    "ruled_out": [],
    "remaining_hypotheses": [],
    "first_checks": [],
    "chain": {
      "leaf_skill": "mig-cloud-adapter",
      "step": "",
      "state_at_escalation": ""
    }
  }
}
```

`confidence` 取值：全量采集成功 0.9；有 `gaps` 按覆盖率折算（`coverage × 0.9`）；
凭据缺失直接 failed，不产出（confidence 不赋分）。

### 人类可读

覆盖率统计表（按 `domain` 分组：已采集 / 缺口 / 覆盖率）+ `gaps` 清单，落
`~/cloud-docs/delivery/<项目>/assessment/inventory-report.md`。
JSON 是唯一数据源，渲染是其投影，不反向读取。

## 升级契约

**触发**：

- **凭据缺失/失效** → 停止采集，**阻塞**（不降级、不猜、不编造 AccessKey）
- **风险等级与授权不匹配**：本次要求调用任何 create/update/delete 类云 API，超出本 skill
  `风险等级`（只读）与租户授权范围 → 立即终止并升级
- **源云不在分派矩阵** → 停止，提示需先接入对应云 MCP
- **MCP 服务器连不上** → 重试 1 次仍失败 → 升级（注明 MCP 标识符与失败码）
- **覆盖率 < 80%** → 不阻塞，降级继续（缺口进 `gaps`，置信度按覆盖率折算），由上游
  `mig-resource-assessment` 决定是否需要升级

**升级包三要素**（缺一不可，同时进 JSON 的 `escalation` 对象）：

```json
{
  "ruled_out": ["已排除的假设，如：非跨账号采集（凭据已明确限定单账号）"],
  "remaining_hypotheses": ["剩余假设，如：cn-north-4 无实例是因为确实为空，而非权限不足"],
  "first_checks": ["建议人先看哪，最多三条按优先级：①… ②… ③…"]
}
```

- `ruled_out` — 已排除了什么（哪些假设已被凭据/返回证伪或确认不适用）
- `remaining_hypotheses` — 剩余哪些假设（未验证、影响覆盖率判断的假设）
- `first_checks` — 建议人先看哪里（最多三条，按优先级排序）

### 场景对照表

| 触发条件 | 动作 | 阻塞 | 置信度 | 输出 |
|---|---|---|---|---|
| 凭据缺失/失效 | 停止采集 | 是 | 不产出 | 升级包 + 需客户提供的凭据清单 |
| 权限不足（部分地域采不到） | 继续采集其余，缺口进 `gaps` | 否 | `coverage × 0.9` | inventory.json + `gaps` 数组 + 提权申请清单 |
| MCP 服务器连不上 | 重试 1 次，仍失败 | 是 | 不产出 | 升级包 + 建议检查 venv/网络 |
| 源云不在分派矩阵 | 停止 | 是 | 不产出 | 升级包 + 需接入的云 MCP 清单 |
| 覆盖率 < 80% | 降级继续 | 否 | 按覆盖率折算 | inventory.json + 差异项（上游决定是否升级） |

## 相关

- [云规格映射表](references/云规格映射表.md) — 量级换算参考
- `scripts/aggregate.py` — 覆盖率计算
- 上游: `mig-resource-assessment`
