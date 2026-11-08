"""AWS 匿名定价适配器 —— 零凭据。

数据源：AWS 公开 Pricing Calculator 静态端点（官方发布数据）。
注意：AWS Price List API (pricing.amazonaws.com) 必须有 AK/SK，本环境无凭据，故不走那条路。
"""
import gzip
import json
import urllib.error
import urllib.parse
import urllib.request

BASE = ("https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/ec2/USD/current/"
        "ec2-ondemand-without-sec-sel")
UA = "Mozilla/5.0 (compatible; cloud-price-bench/1.0)"
DEFAULT_REGION = "US East (N. Virginia)"


def _fetch(url: str, timeout: int = 90) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "gzip"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read()
    # urllib 不自动解码 gzip，手动处理
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    return raw


def fetch_ec2(region: str = DEFAULT_REGION, os_name: str = "Linux") -> dict:
    url = f"{BASE}/{urllib.parse.quote(region)}/{urllib.parse.quote(os_name)}/index.json"
    return json.loads(_fetch(url).decode("utf-8", errors="replace"))


def query(region: str = DEFAULT_REGION, os_name: str = "Linux", match: str = "") -> list:
    """返回 [{'instanceType','vCPU','memory','price','unit','family'}]，price 为 USD/hr 字符串。"""
    d = fetch_ec2(region, os_name)
    reg = d.get("regions", {}).get(region)
    if not reg:
        raise KeyError(f"region 不在返回中: {region}（可用: {list(d.get('regions', {}))[:5]}）")

    rows = []
    for val in reg.values():
        if not isinstance(val, dict):
            continue
        it = val.get("Instance Type")
        if not it:
            continue
        if match and match.lower() not in it.lower():
            continue
        rows.append({
            "instanceType": it,
            "vCPU": val.get("vCPU"),
            "memory": val.get("Memory"),
            "price": val.get("price"),
            "unit": val.get("Unit", "Hrs"),
            "family": val.get("Instance Family"),
        })
    rows.sort(key=lambda r: r["instanceType"])
    return rows
