# OCI 免费实例相关脚本清单与运行要点

本文件补充 `oci-free-tier` SKILL.md 中引用的部署脚本细节。所有脚本位于 `~/.hermes/overseas-deploy/`。

## 脚本清单

| 文件 | 作用 | 关键依赖 |
|------|------|----------|
| `oci-grabber/oci_grab_instance.py` | v4 抢注脚本，配置硬编码在 CONFIG（法兰克福 3 AD） | `oci` SDK、`private_key.pem`、`ssh-key-2026-08-14.pub` |
| `extracted_v5/oci_grab_instance_v5.py` | v5 抢注，凭证从 env/`~/.oci/config`，多 AD 并发 | `oci` SDK、本地 `~/.oci/config` |
| `oci-claim.py` | 自制法兰克福单区域版，成功后调 notify.sh | `oci` SDK、`~/.oci/config` 或 `OCI_*` 环境变量 |
| `notify.sh` | 占位通知（写日志+打印），预留 Telegram 片段 | 无 |
| `setup-native.sh` | 原生部署 Hermes 网关：venv + systemd + Nginx Basic Auth，不用 Docker | python3.11、nginx、ufw |
| `setup.sh` | Docker 版部署（重机器备用） | docker、docker-compose |

## 运行 v4 抢注脚本

```bash
cd ~/.hermes/overseas-deploy/oci-grabber
# 必须本地放好：
#   private_key.pem         (权限 600)
#   ssh-key-2026-08-14.pub  (已生成，脚本自动读)
nohup python3 oci_grab_instance.py > grab.log 2>&1 &
# 菜单选 2 开始抢；Ctrl+C 停止
```

## 运行 v5 / 自制版（推荐）

```bash
pip install oci
# 配置 ~/.oci/config (含 user/tenancy/fingerprint/key_file + region=eu-frankfurt-1)
# 或导出 OCI_USER_OCID / OCI_TENANCY_OCID / OCI_FINGERPRINT / OCI_KEY_FILE / OCI_COMPARTMENT_OCID / OCI_SUBNET_OCID / OCI_IMAGE_OCID / OCI_SSH_PUBLIC_KEY
python3 oci_grab_instance_v5.py          # 多 AD 并发，自适应退避
# 或
nohup python3 oci-claim.py > claim.log 2>&1 &   # 自制法兰克福版
```

## 原生部署网关（抢到实例后）

```bash
sudo bash setup-native.sh --target-vps        # 交互填 API Key
# 或 sudo bash setup-native.sh --target-vps --https   # 带 HTTPS
```
安全底线：Nginx 反代 + Basic Auth，防火墙只放 22/80/443，8080 不暴露公网。

## AD 名称注意

法兰克福 AD 形如 `jBix:EU-FRANKFURT-1-AD-1/2/3`，从你自己的 OCI Console 复制，不要抄网上的。
