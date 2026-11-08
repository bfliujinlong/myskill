#!/usr/bin/env python3
"""匿名获取 AWS 官方定价（无需 AK/SK，零费用，只读）。

数据源：AWS 公开 Pricing Calculator 静态端点 + Bulk API 索引。
详见同目录 SKILL.md。
"""
import argparse
import gzip
import io
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/ec2/USD/current/ec2-ondemand-without-sec-sel"
BULK_INDEX = "https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/index.json"
UA = "Mozilla/5.0 (compatible; aws-pricing-anon/1.0)"


def fetch(url: str, timeout: int = 90) -> bytes:
    """下载并按需解压。服务端返回 gzip，urllib 不会自动解码。"""
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "gzip"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read()
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    return raw


def load_json(url: str) -> dict:
    return json.loads(fetch(url).decode("utf-8", errors="replace"))


def cmd_services(_args: argparse.Namespace) -> int:
    d = load_json(BULK_INDEX)
    offers = d.get("offers", {})
    print(f"publicationDate: {d.get('publicationDate')}")
    print(f"offers: {len(offers)}")
    for code in sorted(offers)[:40]:
        print(" ", code)
    return 0


def cmd_regions(args: argparse.Namespace) -> int:
    d = load_json(f"{BASE}/index.json") if False else None
    # Calculator 端点没有统一 region 清单，改从 Bulk index 的 EC2 offer 取常见 region
    wellknown = [
        "US East (N. Virginia)", "US East (Ohio)", "US West (Oregon)",
        "US West (N. California)", "EU (Ireland)", "EU (Frankfurt)",
        "EU (London)", "Asia Pacific (Tokyo)", "Asia Pacific (Singapore)",
        "Asia Pacific (Sydney)", "Asia Pacific (Mumbai)", "Canada (Central)",
        "South America (Sao Paulo)",
    ]
    print("常用 Calculator region 名（URL 需 percent-encode 括号）：")
    for r in wellknown:
        print(" ", r)
    return 0


def cmd_ec2(args: argparse.Namespace) -> int:
    region = args.region
    url = f"{BASE}/{urllib.parse.quote(region)}/{urllib.parse.quote(args.os)}/index.json"
    try:
        d = load_json(url)
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {url}", file=sys.stderr)
        print("region 名可能不匹配，先跑 `regions` 看可用名。", file=sys.stderr)
        return 2

    reg = d.get("regions", {}).get(region)
    if not reg:
        print(f"region 未在返回中: {region}", file=sys.stderr)
        print(f"可用: {list(d.get('regions', {}))[:5]}", file=sys.stderr)
        return 2

    rows = []
    for key, val in reg.items():
        if not isinstance(val, dict):
            continue
        it = val.get("Instance Type")
        if not it:
            continue
        if args.match and args.match.lower() not in it.lower():
            continue
        rows.append({
            "instanceType": it,
            "vCPU": val.get("vCPU"),
            "memory": val.get("Memory"),
            "price": val.get("price"),
            "unit": val.get("Unit", "Hrs"),
            "family": val.get("Instance Family"),
            "storage": val.get("Storage"),
        })

    rows.sort(key=lambda r: (r["instanceType"] or ""))
    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
    else:
        print(f"region={region} os={args.os} 匹配={len(rows)}")
        print(f"{'instanceType':<22}{'vCPU':>6}{'memory':>12}{'USD/hr':>14}  family")
        for r in rows[: args.limit]:
            print(f"{r['instanceType']:<22}{str(r['vCPU']):>6}{str(r['memory']):>12}{str(r['price']):>14}  {r['family']}")
        if len(rows) > args.limit:
            print(f"... 还有 {len(rows) - args.limit} 条，用 --limit 调整")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="AWS 匿名定价查询（零凭据）")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("services", help="列出可匿名访问的 AWS 服务 code")
    sp.set_defaults(fn=cmd_services)

    sp = sub.add_parser("regions", help="列出常用 Calculator region 名")
    sp.set_defaults(fn=cmd_regions)

    sp = sub.add_parser("ec2", help="查 EC2 On-Demand 单价")
    sp.add_argument("--region", default="US East (N. Virginia)")
    sp.add_argument("--os", default="Linux", help="Linux / Windows / RHEL 等")
    sp.add_argument("--match", default="", help="机型子串，如 t3.micro / m5")
    sp.add_argument("--limit", type=int, default=40)
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(fn=cmd_ec2)

    args = p.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
