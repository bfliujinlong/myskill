---
name: agentcore-cleanup
description: >-
  停/删阿里云 AgentCore workspace 省费用：ROA 签名脚本与删除顺序。
---

# 阿里云 AgentCore 停费清理

## 核心事实（2026-10 实测）

- **没有"暂停"接口**：API 155 个动作只有 Create/Update/Delete，无 Stop/Pause/Disable。
  `InstallWorkspacePlugin` 的 PUT 只接受 `config`，传 `enabled:false` 仍返回 `enabled:true`——
  **协作管控面只能靠删 Workspace 停**。
- **计费（上海，按量）**：算力 CU ¥0.0000694/CU（1 vCPU×1秒=1CU，1GB内存×1秒=0.5CU）、
  网关 CU ¥0.0000015/CU、存储 CU ¥0.00025/GB·h、协作专享管控面 ¥3/h（限免 2026-10-18 已结束）、
  公网流量 ¥0.8/GB。一个 3 agent + 协作的 workspace 全天挂着约 ¥20+/天，**当天必须删**。

## 签名脚本

`/home/ubuntu/.hermes/cache/scratch/ac.py`（`roa(method, path, body)`）。关键点：

- AK/SK 读 `~/.aliyun/config.json` 的 default profile
- **SK 用原值，不要追加 `&`**，加了必 400 `SignatureDoesNotMatch`
- `x-acs-version: 2026-08-04` 必须进 canonical headers 并参与签名
- GET 无 body 时 Content-MD5 = `1B2M2Y8AsgTpgAmY7PhCfg==`（空串 md5）
- 端点 `agentcore.cn-shanghai.aliyuncs.com`，风格 ROA
- 用 `/home/ubuntu/.hermes/hermes-install/venv/bin/python3` 跑（脚本已改 urllib，无 requests 依赖）

## 删除顺序（乱序会 409）

```
1. DELETE /workspaces/{ws}/teams/{teamId}           # 先删 team，否则 agent 报 Agent.Delete.Conflict
2. DELETE /workspaces/{ws}/managed-agents/{agentId} # 逐个删，沙箱随之释放
3. DELETE /workspaces/{ws}/models/{modelId}
4. DELETE /workspaces/{ws}/model-connections/{cid}  # 有模型引用时不能删
5. DELETE /workspaces/{ws}/users/{userId}
6. DELETE /workspaces/{ws}                          # 连带 ServiceEndpoint/协作管控面/PrivateLink
```

- `UpdateTeam` 不接受空 agents（要求 exactly one LEADER），也不接受空 users（要求 exactly one ADMIN）——**直接 DELETE team 更快**。
- Workspace 删除异步：`Deleting` → `Deleted` 约 **2–4 分钟**。轮询 `GET /workspaces/{ws}` 到 `totalCount=0`。
- Agent 删完立即从 list 消失，再查 sandbox 会 `Agent.NotFound`。

## 查证费用（不要口头断言）

```bash
aliyun bssopenapi QueryInstanceBill --BillingCycle $(date +%Y-%m) \
  --Granularity DAILY --BillingDate $(date +%F) --PageSize 100
```

- 参数是 `--PageSize`，**不是** `--MaxResults`/`--MaxResultNum`（会报 not a valid parameter）。
- AgentCore 的 PipCode 是 `agentteams`，CommodityCode `agentteams_agentcore_public_cn`。
- 随 workspace 删除的还有 PrivateLink（`ep-uf6...`），用
  `aliyun privatelink ListVpcEndpoints --RegionId cn-shanghai` 验证归零。

## 上下文归档

删前把 `/tmp/agentcore_ctx.json`（workspaceId/connectionId/agents/models/users/vpc/teamId）
备份到 `/data/agentcore_ctx.deleted.<YYYYMMDD>.json`，重建时直接复用。

## 本轮实例

2026-10-23 建的 `travel-salon-ws2`（ws-a5dd3c2ed0ab4886a4e72，cn-shanghai 沙龙实操）当天全删，出账 ¥22.31。
