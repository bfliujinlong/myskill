"""华为云 ECS 定价适配器 —— 完全匿名，零凭据。

数据源：华为云价格计算器的 productInfo 接口（portal.huaweicloud.com），
实测 2026-10-31 无需任何认证即可 GET，返回 ECS 全部规格的各计费模式价目。

两个站点：
  - intl（默认）：portal-intl.huaweicloud.com，region=ap-southeast-1，币种 USD，可直接比价
  - cn     ：portal.huaweicloud.com，region=cn-north-4，币种 CNY，需按 CNY_USD_RATE 换算

注意：接口不支持按 region 过滤（实测 urlPath/regId 参数无效），
返回的始终是站点默认区域的价格快照 —— 华为云各区域同规格价差极小，可接受。

计价口径（对齐 bench.py）：Linux 镜像、x86 架构、ONDEMAND（按需）、小时单价。
"""
import json
import os
import re
import time
import urllib.request

UA = "Mozilla/5.0 (compatible; cloud-price-bench/1.0)"

# 站点 → (productInfo 端点, 币种, 默认区域)
SITES = {
    "intl": ("https://portal-intl.huaweicloud.com/api/calculator/rest/cbc/"
             "portalcalculatornodeservice/v4/api/productInfo?urlPath=ecs",
             "USD", "ap-southeast-1"),
    "cn": ("https://portal.huaweicloud.com/api/calculator/rest/cbc/"
           "portalcalculatornodeservice/v4/api/productInfo?urlPath=ecs",
           "CNY", "cn-north-4"),
}
DEFAULT_SITE = "intl"

# 排除突发性能实例（T 系列），与其他云的"通用型（非突发）"口径一致
BURST_RE = re.compile(r"^a?t\d", re.I)

CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cache")
CACHE_TTL = 7 * 86400  # 价目表更新慢，缓存 7 天


def _cache_path(site: str) -> str:
    return os.path.join(CACHE_DIR, f"huawei_ecs_{site}.json")


def _fetch(site: str = DEFAULT_SITE, timeout: int = 180) -> dict:
    """拉取 ECS 价目全表（约 5~7 MB），本地缓存 7 天。"""
    os.makedirs(CACHE_DIR, exist_ok=True)
    path = _cache_path(site)
    if os.path.exists(path) and time.time() - os.path.getmtime(path) < CACHE_TTL:
        with open(path) as f:
            return json.load(f)
    url = SITES[site][0]
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    # 7 MB 响应偶发截断，失败时抛异常由调用方处理，不静默吞掉
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    with open(path, "w") as f:
        json.dump(data, f)
    return data


def _num(v) -> int:
    """cpu/mem 字段形如 '4dataInfo_36_' / '16BSSUNIT.pluralUnit.102'，取前导数字。"""
    m = re.match(r"(\d+)", v or "")
    return int(m.group(1)) if m else 0


def _ondemand(item: dict):
    """取按需小时单价。billingEvent 必须是 vmduration（按时长），排除一次性/预留。"""
    for p in item.get("planList") or []:
        if p.get("billingMode") == "ONDEMAND" and p.get("billingEvent") == "event.type.vmduration":
            return float(p["amount"])
    return None


def _rows(site: str) -> list:
    """筛出 Linux + x86 + 有按需价的 ECS 规格。"""
    data = _fetch(site)
    items = data.get("product", {}).get("ec2_vm") or []
    out = []
    for i in items:
        code = i.get("resourceSpecCode") or ""
        # 只取 Linux 镜像规格（.linux 后缀）；x86 架构，排除鲲鹏 ARM
        if not code.endswith(".linux") or i.get("instanceArch") != "x86":
            continue
        price = _ondemand(i)
        if price is None:
            continue
        out.append({
            "spec": code,
            "vcpu": _num(i.get("cpu")),
            "mem": _num(i.get("mem")),
            "price": price,
            "currency": SITES[site][1],
            "region": data.get("region") or SITES[site][2],
            "family": i.get("series") or "",
            "perform": i.get("performType") or "",
            "burst": bool(BURST_RE.match(code)),   # T 系列突发性能实例
        })
    return out


def query(vcpu: int = 4, mem: int = 16, site: str = DEFAULT_SITE,
          allow_burst: bool = False, **_) -> dict:
    """按 vCPU/内存取该规格下最低价的华为云 SKU。

    返回 {'spec','vcpu','mem_gb','usd_hr','cny_hr','unit','exact','raw'}。
    usd_hr 为归一后的 USD/hr（cn 站点用 CNY_USD_RATE 换算，与 bench.py 阿里云口径一致）。
    """
    cands = [r for r in _rows(site) if r["vcpu"] == vcpu and r["mem"] == mem]
    if not allow_burst:
        cands = [r for r in cands if not r["burst"]]
    if not cands:
        raise KeyError(f"华为云无匹配规格: {vcpu}c{mem}g（site={site}）")
    best = min(cands, key=lambda r: r["price"])

    currency = best["currency"]
    if currency == "CNY":
        rate = float(os.environ.get("CNY_USD_RATE", "0.14"))
        usd = round(best["price"] * rate, 6)
        cny = best["price"]
    else:
        usd = best["price"]
        cny = None

    return {
        "spec": best["spec"],
        "vcpu": best["vcpu"],
        "mem_gb": best["mem"],
        "usd_hr": usd,
        "cny_hr": cny,
        "currency": currency,
        "region": best["region"],
        "unit": "Hrs",
        "exact": True,      # 华为云规格固定 cpu/mem 配比，命中即精确
        "raw": {"site": site, "family": best["family"],
                "performType": best["perform"], "burst": best["burst"]},
    }


def list_shapes(vcpu: int = 4, mem: int = 16, site: str = DEFAULT_SITE,
                limit: int = 10) -> list:
    """列出该规格下全部候选（含价格），便于人工核对与选最低价。"""
    rows = [r for r in _rows(site) if r["vcpu"] == vcpu and r["mem"] == mem]
    rows.sort(key=lambda r: r["price"])
    # price 为站点原币金额（intl=USD / cn=CNY），换算在 query() 里统一处理
    return [{"spec": r["spec"], "price": r["price"], "currency": r["currency"],
             "family": r["family"], "burst": r["burst"]} for r in rows[:limit]]
