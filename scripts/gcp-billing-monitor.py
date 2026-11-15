#!/usr/bin/env python3
"""
GCP 账单监控脚本 — 真实双通道通知 (Telegram + SMS) + 异常告警

行为:
  1. 检查 GCP 账单状态 / 项目计费 / 实例 / 存储桶
  2. 若可取到当月费用, 超过 ANOMALY_THRESHOLD (默认 $0.1) 则发紧急通知
  3. 发送 Telegram 通知 (经 `hermes send`, 需已配置 telegram 渠道)
  4. 发送短信通知 (经环境变量配置的短信网关; 未配置则如实报告不可用, 不伪造成功)

依赖:
  - gcloud 已安装且已 `gcloud auth login` / 服务账号已配置 -> 才能查询 GCP
  - hermes send 已配置 telegram -> 才能发 Telegram
  - 短信网关 (SMS_GATEWAY_URL 或 TWILIO_*) -> 才能发短信

退出码: 0=正常, 1=监控/通知失败, 2=用法错误
"""

import subprocess
import sys
import os
import json
from datetime import datetime

# ---------- 配置 ----------
TELEGRAM_TARGET = "telegram:5701842056"   # jinlongliu (dm)
SMS_TARGET = "15102159929"                # 短信接收号
ANOMALY_THRESHOLD = 0.1                   # USD, 当月累计费用超此值即紧急通知
PROJECT_ID = "cryptic-bivouac-471612-t0"
BILLING_ACCOUNT = "0137DE-0D1BAB-37E0B4"


def run(cmd, timeout=60):
    """运行 shell 命令, 返回 (stdout, error)。error 为空表示成功。"""
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        if r.returncode == 0:
            return r.stdout.strip(), None
        return "", (r.stderr.strip() or f"exit={r.returncode}")
    except Exception as e:
        return "", str(e)


def send_telegram(message):
    """真实发送 Telegram (经 hermes send)。返回 (ok, detail)。"""
    try:
        r = subprocess.run(
            ["hermes", "send", "--to", TELEGRAM_TARGET, "-s", "[GCP账单监控]", message],
            capture_output=True, text=True, timeout=90,
        )
        out = (r.stdout or r.stderr).strip()
        if r.returncode == 0 and "error" not in out.lower():
            return True, out or "delivered"
        return False, out or "unknown error"
    except Exception as e:
        return False, str(e)


def send_sms(message):
    """真实发送短信。需通过环境变量配置网关, 否则如实报告不可用。"""
    gw = os.environ.get("SMS_GATEWAY_URL")
    if not gw:
        return False, "SMS 未配置: 无 SMS_GATEWAY_URL / Twilio 凭证, 短信通道不可用"
    # 具体网关接入按需扩展; 当前环境未配置, 不伪造成功
    return False, f"SMS 网关已配置 ({gw}) 但本环境未实现该提供商的发送逻辑"


def fetch_billing_cost():
    """真实当月费用: 经 Cloud Billing REST API (billingAccounts.transactions.list) 取交易累加。
    返回 (transactions_text, error)。无凭证/不可达时 error 非空, transactions_text 为 None。"""
    token, e = run("gcloud auth print-access-token")
    if e:
        return None, f"gcloud 未认证, 无法取得访问令牌: {e}"
    url = (
        f"https://cloudbilling.googleapis.com/v1/"
        f"billingAccounts/{BILLING_ACCOUNT}/transactions"
    )
    # 把真实 token 写入临时 header 文件, 用 curl -H @file 读取, 避免 token 出现在进程参数/ps 中
    import tempfile as _tf
    import os as _os
    _hf = _tf.NamedTemporaryFile(mode="w", delete=False, suffix=".hdr")
    _hf.write("Authorization: Bearer " + token + "\n")
    _hf.close()
    try:
        out, e = run(
            f"curl -s -m 30 -H @{_hf.name} '{url}'",
            timeout=40,
        )
    finally:
        try:
            _os.unlink(_hf.name)
        except OSError:
            pass
    if e:
        return None, f"REST 调用失败: {e}"
    if not out:
        return None, "REST 返回空"
    try:
        obj = json.loads(out)
        txns = obj.get("transactions", [])
        now = datetime.now()
        total = 0.0
        lines = []
        for t in txns:
            amt = t.get("amount", {})
            units = amt.get("units")
            nanos = amt.get("nanos", 0) or 0
            if units is None:
                continue
            val = float(units) + float(nanos) / 1e9
            td = t.get("transactionDate") or t.get("createTime") or ""
            if td and td[:7] == now.strftime("%Y-%m"):
                total += abs(val)
            lines.append(f"{td}\t{val}")
        if lines:
            return "\n".join(lines) + f"\n(当月累计估算: ${round(total, 4)})", None
        return "(本月无交易记录)", None
    except Exception as ex:
        return None, f"解析失败: {ex}"


def check_gcp_billing():
    """检查 GCP 账单。返回 dict。"""
    # gcloud 可用性
    _, err = run("command -v gcloud")
    if err:
        return {
            "status": "unavailable",
            "reason": "gcloud 未安装或未认证, 本机无法查询 GCP 账单 (需在 GCP 主机或配置服务账号后运行)",
        }

    data = {}
    accounts, e1 = run("gcloud billing accounts list")
    data["billing_accounts"] = accounts if accounts else f"(查询失败: {e1})"

    proj, e2 = run(f"gcloud billing projects describe {PROJECT_ID}")
    data["project_billing"] = proj if proj else f"(查询失败: {e2})"

    inst, e3 = run(f"gcloud compute instances list --project={PROJECT_ID}")
    data["instances"] = inst if inst else "(无实例 / 查询失败)"

    buckets, e4 = run(f"gcloud storage buckets list --project={PROJECT_ID}")
    data["storage"] = buckets if buckets else "(无存储桶 / 查询失败)"

    # 真实当月费用: 走 Cloud Billing REST API (billingAccounts.transactions.list)
    cost, cerr = fetch_billing_cost()
    data["recent_transactions"] = cost if cost else f"(未取到: {cerr})"

    # 解析近似当月费用 (从 transactions 累加 USD 正值) — 尽力而为
    month_cost = parse_month_cost(cost)
    data["estimated_month_cost_usd"] = month_cost

    return {"status": "success", "data": data}


def parse_month_cost(transactions_text):
    """从 transactions 文本尽力解析当月累计费用 (USD)。失败返回 None。"""
    if not transactions_text:
        return None
    # 形如 "(本月无交易记录)" / "(未取到: ...)" 等非真实数据 -> 不可解析
    if transactions_text.lstrip().startswith("("):
        return None
    try:
        total = 0.0
        for line in transactions_text.splitlines():
            parts = line.split()
            if not parts:
                continue
            # 末段通常为金额, 形如 12.34 或 -1.23
            amt = parts[-1].replace("$", "").replace(",", "")
            try:
                total += abs(float(amt))
            except ValueError:
                continue
        return round(total, 4)
    except Exception:
        return None


def check_host_quotas():
    """账单 API 不可达时的降级数据源: 从本机(就是那台 GCP 免费层 VM)直接读真实资源消耗,
    对照 Google Cloud Free Tier 额度做核算。返回 dict。

    Free Tier 额度(官方文档 cloud.google.com/free/docs/gcp-free-tier#compute):
      - 1 台非抢占 e2-micro, 限 us-west1 / us-central1 / us-east1, 按小时计(当月小时数内免费)
      - 30 GB-month 标准持久磁盘(HDD), 限上述区域
      - 每月 1 GB 北美出向流量(排除中国/澳大利亚)
    """
    def sh(cmd):
        try:
            r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=25)
            return (r.stdout or "").strip()
        except Exception:
            return ""

    def meta(p):
        return sh(f"curl -s -m 5 -H 'Metadata-Flavor: Google' "
                  f"http://metadata.google.internal/computeMetadata/v1/{p}")

    def cnt(p):
        v = sh(f"cat {p}")
        try:
            return int(v.split()[0])
        except Exception:
            return 0

    zone_full = meta("instance/zone")
    zone = zone_full.rsplit("/", 1)[-1] if zone_full else "?"
    mtype_full = meta("instance/machine-type")
    mtype = mtype_full.rsplit("/", 1)[-1] if mtype_full else "?"
    preemptible = (meta("instance/scheduling/preemptible") or "?").upper()

    # 区域是否落在免费额度内
    free_regions = ("us-west1", "us-central1", "us-east1")
    region = zone.rsplit("-", 1)[0] if "-" in zone else zone
    region_ok = any(region.startswith(r) for r in free_regions)

    # 磁盘: 取所有 PersistentDisk 之和 (不含 boot/efi 小分区重复计数)
    disk_gb = 0.0
    for line in sh("lsblk -bd -o SIZE,TYPE,MODEL").splitlines()[1:]:
        parts = line.split(None, 2)
        if len(parts) >= 3 and "PersistentDisk" in parts[2]:
            try:
                disk_gb += int(parts[0]) / (1024 ** 3)
            except ValueError:
                pass

    # 出向流量: 仅物理网卡 (排除 lo)
    tx_total = 0
    for iface in sh("ls /sys/class/net").split():
        if iface == "lo":
            continue
        tx_total += cnt(f"/sys/class/net/{iface}/statistics/tx_bytes")

    uptime_s = 0.0
    try:
        uptime_s = float(sh("cat /proc/uptime").split()[0])
    except Exception:
        pass
    up_days = uptime_s / 86400 if uptime_s else 0.0
    tx_gib = tx_total / (1024 ** 3)
    egress_month_est = round(tx_gib / up_days * 30, 2) if up_days > 0 else None

    alerts = []
    if mtype and mtype != "e2-micro":
        alerts.append(f"机型 {mtype} 非 e2-micro, 不在免费额度内")
    if preemptible == "TRUE":
        alerts.append("实例为抢占式, 不适用免费额度")
    if not region_ok:
        alerts.append(f"区域 {region} 不在免费额度区域(us-west1/us-central1/us-east1)")
    if disk_gb > 30.5:
        alerts.append(f"持久磁盘 {disk_gb:.1f} GB > 30 GB 免费额度")
    if egress_month_est is not None and egress_month_est > 1.0:
        alerts.append(
            f"出向外推 {egress_month_est} GiB/月 > 1 GiB 免费额度 "
            f"(注意: 该计数器含同区域内网流量, 只有跨区/出公网部分才计费)"
        )

    return {
        "zone": zone,
        "machine_type": mtype,
        "preemptible": preemptible,
        "region_free_tier_ok": region_ok,
        "persistent_disk_gb": round(disk_gb, 1),
        "tx_total_gib": round(tx_gib, 3),
        "uptime_days": round(up_days, 2),
        "egress_month_est_gib": egress_month_est,
        "alerts": alerts,
        "mem": sh("free -h | sed -n 2p"),
        "root_used": sh("df -h / | tail -1"),
    }


def build_degraded_report(host, ts):
    """账单 API 不可达 -> 用本机真实资源状态 + 免费层额度对照出报告。"""
    flag = "🟡 降级模式: Billing API 不可达, 改用本机实测免费层额度核算"
    if host["alerts"]:
        flag += " — ⚠️ 有超额度信号"
    else:
        flag += " — ✅ 未发现超额度信号"
    lines = [
        f"📊 GCP 账单监控(降级模式) — {ts}",
        "",
        f"💰 账单费用: 未知 — Cloud Billing API 在本项目被禁用, 无法取到金额",
        f"   (不等于 $0; 需人工启用 API 才能出真实数字)",
        "",
        flag,
        "",
        "🖥️ 本机实测 (该机即为被监控的 GCP 实例):",
        f"   区域/机型: {host['zone']} / {host['machine_type']} (抢占={host['preemptible']})",
        f"   免费层区域: {'✅ 合规' if host['region_free_tier_ok'] else '❌ 不合规'}",
        f"   持久磁盘:   {host['persistent_disk_gb']} GB  (免费额度 30 GB)",
        f"   运行天数:   {host['uptime_days']} 天",
        f"   出向累计:   {host['tx_total_gib']} GiB → 外推 {host['egress_month_est_gib']} GiB/月 (免费额度 1 GiB, 含内网)",
        f"   内存: {host['mem']}",
        f"   根盘: {host['root_used']}",
    ]
    if host["alerts"]:
        lines += ["", "⚠️ 超额度信号:"]
        lines += [f"   • {a}" for a in host["alerts"]]
    else:
        lines += ["", "   (各项均在免费层额度内, 未发现计费风险信号)"]
    return "\n".join(lines)


def build_report(result, anomaly=False):
    ts = datetime.now().isoformat(timespec="seconds")
    if result["status"] == "unavailable":
        body = (
            f"⚠️ GCP 账单监控 — 无法获取 (UNREACHABLE)\n"
            f"时间: {ts}\n\n"
            f"原因: {result['reason']}\n\n"
            f"本机 (OCI Always-Free) 未安装/未认证 gcloud, 也无 GCP 凭证, "
            f"无法查询账单。请在 GCP 主机或配置服务账号后运行本脚本。\n"
            f"Telegram 通知: 已发送 | 短信通知: 见下方状态。"
        )
        return body
    d = result["data"]
    cost = d.get("estimated_month_cost_usd")
    if anomaly:
        flag = f"🚨 异常: 当月费用 ${cost} 超阈值 ${ANOMALY_THRESHOLD:.2f}"
    elif cost is None:
        flag = "⚠️ 费用未知: 无法获取真实 GCP 账单数据 (gcloud 未认证 / 凭证缺失)"
    else:
        flag = f"✅ 费用正常: 当月估算 ${cost} ≤ 阈值 ${ANOMALY_THRESHOLD:.2f}"
    body = (
        f"📊 GCP 账单监控报告 — {ts}\n\n"
        f"💰 当月估算费用: {('$' + str(cost)) if cost is not None else '未知 (无法获取)'}\n"
        f"{flag}\n\n"
        f"📋 账单账户:\n{d['billing_accounts']}\n\n"
        f"🏢 项目计费:\n{d['project_billing']}\n\n"
        f"💻 实例:\n{d['instances']}\n\n"
        f"📦 存储桶:\n{d['storage']}\n\n"
        f"🧾 近期交易:\n{d['recent_transactions']}\n"
    )
    return body


def main():
    print("🚀 GCP 账单监控启动...")
    result = check_gcp_billing()

    report = None
    anomaly = False

    if result["status"] == "success":
        cost = result["data"].get("estimated_month_cost_usd")
        if isinstance(cost, (int, float)) and cost > ANOMALY_THRESHOLD:
            anomaly = True
            print(f"🚨 检测到异常费用: ${cost} > ${ANOMALY_THRESHOLD}")
        elif cost is None:
            print("⚠️ 无法获取真实 GCP 账单费用")
    else:
        print("⚠️ 账单 API 不可达")

    # 真实费用取不到 (不可达 或 success 但 cost 为 None) -> 降级到本机实测额度核算
    cost = None
    if result["status"] == "success":
        cost = result["data"].get("estimated_month_cost_usd")
    if result["status"] != "success" or cost is None:
        print("🔄 启用降级模式: 从本机实测资源对照 GCP 免费层额度")
        host = check_host_quotas()
        ts = datetime.now().isoformat(timespec="seconds")
        report = build_degraded_report(host, ts)
        anomaly = bool(host["alerts"])   # 超额度信号即视为需关注

    if report is None:
        report = build_report(result, anomaly)

    print("─" * 40)
    print(report)
    print("─" * 40)

    # 双通道通知
    ok_tg, det_tg = send_telegram(report)
    ok_sms, det_sms = send_sms(report)

    print(f"📱 Telegram: {'✅ 已发送' if ok_tg else '❌ 失败'} — {det_tg}")
    print(f"📲 SMS:      {'✅ 已发送' if ok_sms else '⚠️ 未发送'} — {det_sms}")

    if result["status"] == "unavailable":
        # 数据不可达本身即需人工关注, 但 Telegram 已通知 -> 退出 0 (通知已送达)
        # 若 Telegram 也失败则退出 1
        sys.exit(0 if ok_tg else 1)

    if anomaly:
        # 异常已通过异常报告通知; 视为需关注但已送达
        sys.exit(0 if (ok_tg and ok_sms) else (0 if ok_tg else 1))

    sys.exit(0 if ok_tg else 1)


if __name__ == "__main__":
    main()
