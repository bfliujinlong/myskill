# 多云中立 profile（目标云未定 / 跨云）

| 字段 | 值 |
|---|---|
| **角色** | **默认入口**：RFP 未指定目标云、或多云并存时的路由层 |
| **成熟度** | 🟡 骨架（治理/成本方法论已有；跨云映射表缺） |
| **适用判断** | 客户同时用 ≥2 家云；或 RFP 只写「上云」未定厂商；或要做跨云容灾/互备/比价 |

## 选型路由（必须先定云，再进阶段 skill）

1. `presales/pcs-arch-selection` — 云选型决策（输出选型依据 + 落选云理由）
2. `presales/pcs-lz-discovery` / `pcs-lz-estimate` — Landing Zone 调研与估算
3. `cloud/landing-zone-pm` — LZ 项目管理
4. `cloud/multi-cloud` — 统一身份 / 跨云网络 / 成本对账 / 容灾互备
5. `business/multi-cloud-pricing.md` + `business/cloud-pricing-tools` — 比价底图
6. 定云后 → 切到对应 `cloud_profiles/{alicloud|aws|azure|huawei|oci|gcp}.md`，再按 Y 轴阶段 skill 走

## 跨云横切关注点（方案必带）

| 关注点 | 要点 |
|---|---|
| 互联 | 专线 / VPN / 云企业网（CEN / TGW / NCC）；跨云流量单价高，尽量同云内闭环 |
| 身份联邦 | 企业 IdP（Azure AD / Okta / 钉钉）联邦到各云 SSO，一套账号体系 |
| 数据复制 | 跨云同步的 RTO/RPO + 合规（数据出境）+ 成本三重权衡 |
| 出网成本 | 隐性大头，账单按 `costcenter/env/owner` 标签分云汇总 |
| 治理 | 多云 = 多套账单 + 多套运维，无统一治理反而更贵 |
| IaC | 用 Terraform 等抹平 API/SDK 差异；区域命名先建映射表 |

## 红线

- **价格一律「待确认」**：跨云比价只能作为选型参考进入 `pcs-arch-selection`，**不得直接进报价单**；报价走 `pcs-quotation` 且以目标云实测单价为准
- 容灾**必须演练**并写入验收用例（只配不练 = 切不过去）
- 未定目标云时，禁止在 HLD/SOW 里写具体产品型号（写成能力描述 + 待定清单）

## 本机可用工具

- 治理/成本：`cloud/multi-cloud`、`business/finance-ops`、`finops/`、`cloud/gcp-*`
- 选型/估算：`presales/pcs-arch-selection`、`pcs-lz-*`、`cloud/landing-zone-pm`
- 待建：跨云产品映射对照表（P2）
