#!/usr/bin/env python3
"""多云统一比价 CLI —— 8 朵云，统一插口，输出可比对结构。

设计：新增一朵云只需在 clouds.yaml 登记 + adapters/<云>.py 实现 query()，
CLI 与报告层无需改动。等用户提供凭据时直接填 adapter 即可启用。

比价口径（保证跨云可比）：
  - Linux、On-Demand、按小时、通用型（非突发/GPU/裸金属）
  - x86 架构（排除 AWS Graviton 的 *g 系列，避免架构不对等）
  - 排除 Spot / 预留 / DevTestConsumption
  - 每档选该云「符合 vCPU/内存」的候选里最低价
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# 云厂商 SDK 装在这里（不污染 system site-packages，也不影响其它工具）
# 需要 SDK 的云：腾讯云(tencentcloud-sdk-python-cvm)、火山(volcenginesdk-billing)
# 其余 6 朵纯 HTTP 匿名取价，不需要任何 SDK。
VENV_DIR = os.path.expanduser("~/.hermes/cloud-mcp-venvs/pricebench")
if os.path.isdir(VENV_DIR):
    sys.path.insert(0, VENV_DIR)

# 归一化规格 → 各云候选 SKU（按 vCPU/内存核对过，非猜测）
# 2026-10-31 实测核对：AWS 取 x86 通用 t3 系；Azure 取 Dv3 通用（2c4g 无 D 系，用 F2s v2）
# 阿里云取企业级 g5/c5 通用（非 t5/t6 突发）
SHAPE = {
    "2c4g": {
        "vcpu": 2, "mem": 4,
        "aws": ["t3.medium"],
        "azure": ["F2s v2", "B2s"],
        "alicloud": ["ecs.c6.large", "ecs.c7.large", "ecs.c5.large"],
        "oci": ["E4", "E3", "E5", "E2"],
        "huawei": ["s6", "s7", "s3"],
        "gcp": ["e2-medium", "e2-standard-2", "e2-custom-2-4096"],
    },
    "2c8g": {
        "vcpu": 2, "mem": 8,
        "aws": ["t3.large", "m5.large"],
        "azure": ["D2 v3", "B2ms"],
        "alicloud": ["ecs.g6.large", "ecs.g7.large", "ecs.g5.large"],
        "oci": ["E4", "E3", "E5", "E2"],
        "huawei": ["s6", "s7", "s3"],
        "gcp": ["e2-standard-2", "e2-standard-4", "n2-standard-2"],
    },
    "4c16g": {
        "vcpu": 4, "mem": 16,
        "aws": ["t3.xlarge", "m5.xlarge"],
        "azure": ["D4 v3", "B4ms"],
        "alicloud": ["ecs.g6.xlarge", "ecs.g7.xlarge", "ecs.g5.xlarge"],
        "oci": ["E4", "E3", "E5", "E2"],
        "huawei": ["s6", "s7", "s3"],
        "gcp": ["e2-standard-4", "e2-standard-8", "n2-standard-4"],
    },
    "8c32g": {
        "vcpu": 8, "mem": 32,
        "aws": ["t3.2xlarge", "m5.2xlarge"],
        "azure": ["D8 v3", "B8ms"],
        "alicloud": ["ecs.g6.2xlarge", "ecs.g7.2xlarge", "ecs.g5.2xlarge"],
        "oci": ["E4", "E3", "E5", "E2"],
        "huawei": ["s6", "s7", "s3"],
        "gcp": ["e2-standard-8", "e2-standard-16", "n2-standard-8"],
    },
}

# AWS Graviton（ARM）与 Azure Windows/Spot 排除规则
AWS_ARM_RE = re.compile(r"^[a-z]+\d+g\.")


def _load_registry() -> dict:
    import yaml
    with open(os.path.join(HERE, "clouds.yaml")) as f:
        return yaml.safe_load(f)


def cmd_status(args) -> int:
    reg = _load_registry()["clouds"]
    if args.json:
        print(json.dumps({k: v["status"] for k, v in reg.items()}, indent=2))
        return 0
    print(f"{'云':<12}{'code':<14}{'status':<12}{'auth':<10}说明")
    print("-" * 78)
    for k, v in reg.items():
        print(f"{v['name']:<12}{k:<14}{v['status']:<12}{v.get('auth','-'):<10}{v.get('note','')[:40]}")
    return 0


def _usd_per_hour(cloud: str, raw: dict) -> float:
    """归一到 USD/hr。阿里云返回 CNY，需换算。"""
    if cloud == "aws":
        return float(raw["price"])
    if cloud == "azure":
        return float(raw["retailPrice"])
    if cloud == "alicloud":
        rate = float(os.environ.get("CNY_USD_RATE", "0.14"))
        return round(float(raw["total"]) * rate, 6)
    if cloud == "oci":
        return float(raw["usd_hr"])
    if cloud == "huawei":
        return float(raw["usd_hr"])
    if cloud == "gcp":
        return float(raw["usd_hr"])
    return float("nan")


def _pick_aws(rows, skus):
    """x86、Linux、按小时；候选里取最低价。"""
    ok = [r for r in rows
          if r["instanceType"] in skus and not AWS_ARM_RE.match(r["instanceType"])]
    ok = [r for r in ok if r.get("price") not in (None, "", "0")]
    return min(ok, key=lambda r: float(r["price"])) if ok else None


def _pick_azure(rows, skus):
    """Linux、Consumption（非 Spot/预留/DevTest）；候选里取最低价。

    注意：Azure 的 productName 带 'Windows' 的行里也混有 Linux 价，
    因此必须同时排除 productName 与 meterName 含 Windows 的项。
    """
    ok = []
    for r in rows:
        if r["skuName"] not in skus:
            continue
        blob = f"{r.get('productName','')} {r.get('meterName','')}"
        if "Windows" in blob or "Spot" in blob:
            continue
        if r.get("unitOfMeasure") != "1 Hour":
            continue
        ok.append(r)
    return min(ok, key=lambda r: float(r["retailPrice"])) if ok else None


def _query_cloud(cloud, skus, args):
    mod = __import__(f"adapters.{cloud}", fromlist=["query"])
    if cloud == "aws":
        rows = mod.query(region=args.aws_region, os_name=args.os)
        return _pick_aws(rows, skus)
    if cloud == "azure":
        # 逐个候选精确查询：全量查询会被 API 分页截断成 Spot/Low Priority 噪音
        for sku in skus:
            try:
                rows = mod.query(sku_name=sku, region=args.azure_region)
            except Exception:
                continue
            hit = _pick_azure(rows, [sku])
            if hit:
                return hit
        return None
    if cloud == "oci":
        cands = []
        for sh in skus:
            try:
                r = mod.query(shape=sh, vcpu=args.vcpu, mem=args.mem)
            except Exception:
                continue
            # 排除 0 价（A1 免费额度档不代表通用商用价），避免污染比价
            if r and r.get("usd_hr", 0) > 0:
                cands.append(r)
        if not cands:
            return None
        # 优先精确匹配（非超配）的最低价的；全超配时才退而用最低价超配项
        exact = [r for r in cands if r.get("exact")]
        pool = exact or cands
        return min(pool, key=lambda r: r["usd_hr"])
    if cloud == "huawei":
        # 匿名价目表：按 (vCPU, 内存) 精确匹配，候选族里取最低价
        cands = []
        rows_h = mod.list_shapes(vcpu=args.vcpu, mem=args.mem, limit=200)
        for r in rows_h:
            if r.get("burst"):
                continue  # 排除突发型，口径对齐其它云的通用型
            if any(r["spec"].startswith(f + ".") for f in skus):
                cands.append(r)
        if not cands:
            return None
        best = min(cands, key=lambda r: r["price"])
        return dict(mod.query(vcpu=args.vcpu, mem=args.mem, family=best["family"]),
                    shape=best["spec"])
    if cloud == "gcp":
        # 匿名机型页：候选机型里挑 vCPU/内存精确匹配（不超配）的最低价
        cands = []
        for mtype in skus:
            try:
                r = mod.query(mtype=mtype)
            except Exception:
                continue
            if not r:
                continue
            v, m = r.get("vcpu"), r.get("mem_gb")
            if v == args.vcpu and m is not None and abs(m - args.mem) < 1e-6:
                cands.append(r)
        if not cands:
            return None
        return min(cands, key=lambda r: r["usd_hr"])
    if cloud == "alicloud":
        for sku in skus:
            try:
                raw = mod.query(sku, region=args.ali_region)
                if raw.get("total"):
                    return raw
            except Exception:
                continue
        return None
    if cloud in ("tencent", "volcengine"):
        # 需要凭据：候选机型逐个试，凭据缺失时统一报 NEED_CRED 而非静默 None
        for sku in skus:
            try:
                raw = mod.query(sku, region=getattr(args, f"{cloud}_region"))
            except mod.CredentialError:
                raise
            except Exception:
                continue
            if raw and raw.get("total"):
                return dict(raw, shape=sku)
        return None
    return None


def cmd_compare(args) -> int:
    reg = _load_registry()["clouds"]
    rows = []

    shapes = list(SHAPE) if args.shape == "all" else [args.shape]

    for sh in shapes:
        shape = SHAPE[sh]
        for cloud in ["aws", "azure", "alicloud", "oci", "huawei", "gcp"]:
            st = reg.get(cloud, {}).get("status")
            skus = shape.get(cloud) or []
            if st != "READY" or not skus:
                rows.append({"shape": sh, "cloud": cloud, "status": st, "sku": skus, "usd_hr": None})
                continue
            try:
                # 把规格的 vCPU/内存挂到 args 上，供 OCI 这类按 OCPU+内存计价的云使用
                args.vcpu, args.mem = shape["vcpu"], shape["mem"]
                raw = _query_cloud(cloud, skus, args)
                rows.append({"shape": sh, "cloud": cloud, "status": "READY",
                             "sku": (raw.get("instanceType") or raw.get("skuName")
                                     or raw.get("shape")) if raw else skus[0],
                             "usd_hr": _usd_per_hour(cloud, raw) if raw else None, "raw": raw})
            except Exception as e:
                rows.append({"shape": sh, "cloud": cloud, "status": "ERR", "sku": skus[0],
                             "usd_hr": None, "error": f"{type(e).__name__}: {str(e)[:90]}"})

    if args.json:
        print(json.dumps({"rows": rows}, ensure_ascii=False, indent=2))
        return 0

    for sh in shapes:
        shape = SHAPE[sh]
        print(f"\n规格 {sh}（{shape['vcpu']}vCPU / {shape['mem']}GiB）  Linux · On-Demand · x86")
        print(f"{'云':<12}{'规格':<24}{'USD/hr':>12}{'USD/月(730h)':>16}")
        print("-" * 66)
        got = [r for r in rows if r["shape"] == sh]
        ready = sorted([r for r in got if r.get("usd_hr") is not None], key=lambda x: x["usd_hr"])
        for r in ready:
            print(f"{r['cloud']:<12}{str(r['sku']):<24}{r['usd_hr']:>12.4f}{r['usd_hr']*730:>16.2f}")
        for r in got:
            if r.get("usd_hr") is None:
                why = r.get("error") or f"status={r['status']}"
                print(f"{r['cloud']:<12}{str(r['sku'])[:24]:<24}{'—':>12}{'':>16}  {why[:44]}")
        if len(ready) >= 2:
            lo, hi = ready[0], ready[-1]
            print(f"  → 最低 {lo['cloud']} ${lo['usd_hr']:.4f}/hr · 最高 {hi['cloud']} ${hi['usd_hr']:.4f}/hr"
                  f" · 差 {hi['usd_hr']/lo['usd_hr']:.2f}x")
    print("\n注：公开 On-Demand 单价；阿里云 CNY 按 CNY_USD_RATE 换算；均未含 RI/SP/EDP 折扣。")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="8 朵云统一比价")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("status", help="列出 8 云接入状态")
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(fn=cmd_status)

    sp = sub.add_parser("compare", help="按规格跨云比价")
    sp.add_argument("--shape", default="2c4g", choices=list(SHAPE) + ["all"])
    sp.add_argument("--aws-region", default="US East (N. Virginia)")
    sp.add_argument("--azure-region", default="eastus")
    sp.add_argument("--ali-region", default="cn-hangzhou")
    sp.add_argument("--tencent-region", default="ap-guangzhou")
    sp.add_argument("--volcengine-region", default="cn-beijing")
    sp.add_argument("--os", default="Linux")
    sp.add_argument("--family", default="general", choices=["general", "burstable"])
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(fn=cmd_compare)

    a = p.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
