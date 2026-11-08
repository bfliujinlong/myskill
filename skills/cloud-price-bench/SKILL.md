---
name: cloud-price-bench
description: 8 朵云统一比价框架。按规格（2c4g/4c16g/8c32g）跨云取真实公开单价，输出 USD/hr 与月费，用于迁移选型、TCO 对比、报价输入。触发词：多云比价、云选型、TCO、迁移成本、哪家云便宜、报价、AWS/Azure/阿里云/OCI/GCP/腾讯云/华为云/火山引擎 价格对比。
---

# 8 朵云统一比价（cloud-price-bench）

## 用法

```bash
# 1. 先看哪几朵云现在能取价
python3 ~/.hermes/skills/cloud-price-bench/bench.py status

# 2. 按规格比价（自动跳过未接入的云）
python3 ~/.hermes/skills/cloud-price-bench/bench.py compare --shape 2c4g
python3 ~/.hermes/skills/cloud-price-bench/bench.py compare --shape all   # 四档全跑
python3 ~/.hermes/skills/cloud-price-bench/bench.py compare --shape 8c32g --json
```

规格档位：`2c4g` `2c8g` `4c16g` `8c32g`（见 `bench.py` 的 `SHAPE`，可加）。

## 8 云接入状态（2026-10-31 实测，非推测）

| 云 | status | auth | 说明 |
|---|---|---|---|
| AWS | **READY** | none | Pricing Calculator 静态端点，匿名免费 |
| Azure | **READY** | none | 官方 Retail Prices API，完全匿名 |
| 阿里云 | **READY** | ak | ECS `DescribePrice`，凭据取 `~/.aliyun/config.json` |
| GCP | **READY** | none | **2026-10-31 攻破**：官方通道全废（cloudbilling 403 / 静态表 404 / 官网纯 JS 渲染），改用匿名机型页 `gcloud-compute.com/<机型>.html`，一页 42 区域 on-demand USD/hr 直读，7 天缓存。**零凭据，不需要 API Key** |
| OCI | **READY** | none | 官方价目 API（apexapps cetools），完全匿名，668 SKU |
| **华为云** | **READY** | **none** | **2026-10-31 攻破**：`portal-intl.huaweicloud.com/api/calculator/.../productInfo?urlPath=ecs` 完全匿名，intl 站直读 USD（418 行），cn 站 CNY（747 行）；7 天本地缓存。**零凭据，不需要 AK/SK** |
| 腾讯云 | NEED_CRED | ak | 端点 200，需 TC3 签名 |
| 火山引擎 | NEED_CRED | ak | open.volcengineapi.com 需签名 |

**已自配 6/8**（AWS / Azure / OCI / 华为云 / **GCP** 全零凭据匿名；阿里云走已有 `~/.aliyun` AK）。
**剩余 2 朵**：腾讯云（SecretId/SecretKey）、火山引擎（AK/SK）—— 两朵均已确认无匿名旁路。
| 火山引擎 | NEED_CRED | ak | open.volcengineapi.com 需签名 |

## 关键设计：插口已留好，给凭据即可启用

新增/启用一朵云只需两步，CLI 与报告层**不用改**：
1. `clouds.yaml` 里把 `status` 改成 `READY`
2. `adapters/<云>.py` 实现 `query()`，返回 dict 或 list

归一到 USD/hr 见 `bench.py::_usd_per_hour()`。阿里云返回 CNY，按 `CNY_USD_RATE`（默认 0.14）换算，
需要准确汇率时用 `CNY_USD_RATE=0.137 python3 bench.py compare ...` 覆盖。

## 已验证事实（2026-10-31 实测）

- AWS 匿名（x86 各档最低）：t3.micro **0.0104** / t3.medium 0.0416 / t3.large 0.0832 / t3.xlarge 0.1664 / t3.2xlarge 0.3328 USD/hr
- AWS 多 region 可用：m5.large 东京 = 0.1240 USD/hr；Windows 例 t3.medium = 0.0600
- Azure 匿名（Linux）：B2s 0.0416 / F2s v2 0.0846 / D2 v3 0.096 / D4 v3 0.192 / D8 v3 0.384 USD/hr
- 阿里云（cn-hangzhou，按量含系统盘）：ecs.c6.large 0.3998 / g6.large 0.5098 / g6.xlarge 1.0098 / g6.2xlarge 2.0098 CNY/hr
- OCI 匿名单价（USD/hr）：E4 Flex **OCPU 0.025 + 内存 0.0015/GB**；E5 OCPU 0.03 + 内存 0.002/GB；
  E2 固定套餐 0.03/OCPU（内存固定=OCPU×8GB）；A1 为 ARM 且有 3000 OCPU·h 免费额度（**价为 0，禁止参与通用比价**）

### 实测比价结果（2026-10-31，6 云：AWS / Azure / 阿里云 / OCI / 华为云 / GCP）

口径：Linux · On-Demand · x86 · 通用型（非突发/GPU/Spot/预留）；阿里云/华为云 CNY 按 0.14 换算。

| 规格 | OCI | GCP | 阿里云 | 华为云 | AWS | Azure | 极差 |
|---|---|---|---|---|---|---|---|
| 2c4g | **0.0310** | 0.0335 | 0.0560 | 0.0600 | 0.0416 | 0.0846 | 2.73x |
| 2c8g | **0.0300** | 0.0670 | 0.0714 | 0.0800 | 0.0832 | 0.0960 | 3.20x |
| 4c16g | **0.0600** | 0.1340 | 0.1414 | 0.1600 | 0.1664 | 0.1920 | 3.20x |
| 8c32g | **0.1200** | 0.2680 | 0.2814 | 0.3200 | 0.3328 | 0.3840 | 3.20x |

（机型：OCI E4.Flex/E2.1/E2.2/E2.4；GCP e2-medium/e2-standard-2/4/8；阿里云 c6.large、g6.large/xlarge/2xlarge；
华为云 s3.large.2、s6.large.4/xlarge.4/2xlarge.4；AWS t3.medium/large/xlarge/2xlarge；Azure F2s v2、D2/D4/D8 v3）

月度（730h）：4c16g 从 OCI $43.8 到 Azure $140.2。

**读法**（GCP 接入后格局稳定）：
- **OCI 全档最低**（约 AWS 的 36%~75%、Azure 的 40%）
- **GCP 全档第二**（仅次于 OCI；含 2c4g：e2-medium $0.0335 < AWS t3.medium $0.0416）
- 阿里云、华为云居中；**AWS 与 Azure 垫底，Azure 全档最贵**
- 极差 2.73x ~ 3.20x —— 迁移 ROI 最有说服力的一个数

校准记录：早期版本曾用 `D2 v3` 充当 2c4g（实为 2vCPU/8GiB）、阿里云复用 2c4g 机型充当 2c8g，
导致比价失真，已于 2026-10-31 校准（见 `bench.py` 的 `SHAPE`）。

**OCI 计价口径（与其他云不同，比价时必须披露）**：OCI 按 OCPU + 内存**分开计价**，
1 OCPU = 2 vCPU。4c16g = 2 OCPU + 16GB。E2 是固定套餐（内存=OCPU×8GB），在 2c4g 档会**超配**
到 2c8g，此时 `adapters/oci.py` 返回 `exact=False`，比价时优先选精确匹配项。

**华为云口径（必须披露）**：intl 站 `ap-southeast-1` 直读 USD；接口返回**站点默认区域快照，
无法按区域过滤**；已排除突发型 T 系列。

**GCP 口径（必须披露）**：数据源是**第三方聚合站 gcloud-compute.com**，非 Google 官方
（官方匿名通道全部不可用）。区域默认 `us-central1`（GCP 定价基准区）。
`e2-medium` 是 2vCPU/4GB 但属共享核，与 AWS t3 突发型同性质，比价时已保留但需知情。

## 数据边界（报价时必须声明）

- 全是**公开 On-Demand 单价**，未含 RI / SP / EDP / 企业折扣
- 阿里云为 CNY 换算值，汇率是环境变量默认值，**非实时汇率**，正式报价需核
- Azure 存在多 meter（Linux/Windows/Spot/Low Priority），已按 `productName`+`meterName` 双字段排除 Windows 与 Spot
  （坑：Azure 的 `productName` 含 "Windows" 的行里也混有 Linux 价，只看 productName 会选错）
- Azure 全量查询会被 API 分页截断成 Spot/Low Priority 噪音，故按候选 SKU **逐个精确查询**
- 当前 4 云可用（AWS/Azure/阿里云/OCI），**不可声称是"8 云全对比"**；缺 GCP/腾讯/华为/火山
- OCI 与其他云计价模型不同（OCPU+内存分开、OCPU=2vCPU），跨云比较时须注明换算口径
- OCI A1 为 ARM 架构且有免费额度（价为 0），已从通用比价候选中排除，不可当作商用最低价

## 安全

- 只读、匿名端点为主、零费用
- 阿里云 AK 只在运行时从 `~/.aliyun/config.json` 读，不落进本 skill 任何文件
