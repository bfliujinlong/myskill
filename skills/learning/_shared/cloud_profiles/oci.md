# OCI profile（目标云：Always Free 档）

| 字段 | 值 |
|---|---|
| **角色** | 目标云（AGENTS.md 指定：OCI Always Free / 阿里云） |
| **成熟度** | 🟡 骨架（免费档申请/部署已实操；作为正式迁移目标的产品映射待补） |
| **识别线索** | VCN / Subnet / DRG / Compute Instance / Block Volume / Object Storage / Autonomous Database / Load Balancer / IAM Policy / compartment；Region 形如 `eu-frankfurt-1`、`us-ashburn-1`；OCID 前缀 `ocid1.` |
| **唯一事实源** | `cloud/oci-free-tier/SKILL.md` + `references/deploy-scripts.md`（配额数字**以 Console 实测为准**，本文件不复述硬编码数字） |
| **采集日期** | 2026-10-31（本机 oci-free-tier 会话结论） |

## 8 域目标产品锚点

| 域 | OCI 产品 | 备注 |
|---|---|---|
| 网络 | VCN / Subnet / DRG / Internet Gateway / NAT Gateway / Load Balancer / FastConnect | AD 名称按租户各异，**不可抄网上** |
| 安全 | WAF / Network Firewall / Cloud Guard / Bastion / Vault | Vault ≈ KMS |
| IAM | IAM（compartment / policy / group）/ Vault | **compartment 是 OCI 特有隔离模型**，方案里必须先定 compartment 结构 |
| 计算 | Compute（VM.Standard.A1.Flex 等，含 ARM）/ Container Instances / Functions | ARM 免费档容量极紧张，需抢 |
| 存储 | Object Storage / Block Volume / File Storage | — |
| 数据库 | Autonomous Database(ATP/ADW) / MySQL HeatWave / PostgreSQL / NoSQL Database | 版本兼容**待确认** |
| 大数据 | OCI Data Flow（Spark）/ GoldenGate / Analytics Cloud | 迁移场景下较少见，**待确认** |
| 监控运维 | Monitoring / Logging / Logging Analytics / Audit（审计） | — |

## 迁移/落地红线

- **零费用红线**：只走 Always Free 档，**绝不开付费资源、绝不绑信用卡**（AGENTS.md 安全红线）
- Always Free ARM 容量随机释放，抢注需多 AD 重试 + 429 指数退避；黄金时间假设已废弃（v5 结论）
- 私钥 `private_key.pem` 权限 **600**，绝不进聊天/压缩包（`cloud/oci-free-tier` 已明列）
- 免费档规格上限 **以 Console 实测为准**，写方案时必须标「待确认」，不得引用网上数字
- AD 名称从自己租户 Console 复制，抄网上必失败
- 抢到后立刻保存公网 IP 与 SSH 私钥，否则登不进去

## 本机可用工具

- OCI CLI：`/home/ubuntu/.hermes/hermes-install/venv/bin/oci`
- 抢注/部署：`cloud/oci-free-tier`（脚本在 `~/.hermes/overseas-deploy/`）
- 待建：OCI 作为正式迁移目标的产品映射表（P2，需 Console 实测后补）
