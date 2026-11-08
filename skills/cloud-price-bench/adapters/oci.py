"""Oracle Cloud (OCI) 匿名定价适配器 —— 零凭据。

数据源：Oracle 官方价目 API（apexapps.oracle.com/cetools），完全匿名，公开 PAY_AS_YOU_GO 价。
实测 2026-10-31：668 个 SKU，含 Compute - Virtual Machine 39 条。

计价模型与 x86 云不同：OCI 按 OCPU + 内存分开计价，1 OCPU = 2 vCPU（超线程两个执行线程）。
因此 4c16g => 2 OCPU + 16 GB。换算口径在 to_hourly() 里统一，保证与其他云可比。
"""
import json
import os
import time
import urllib.request

BASE = "https://apexapps.oracle.com/pls/apex/cetools/api/v1/products/"
UA = "Mozilla/5.0 (compatible; cloud-price-bench/1.0)"
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cache", "oci_products.json")
CACHE_TTL = 7 * 86400  # 价目表更新很慢，缓存 7 天

# 通用型 x86 shape → (OCPU partNumber, Memory partNumber, 计价方式, 备注)
# kind=flex  : OCPU 与内存可任意配比，按单价×数量计（OCI 主流报价方式）
# kind=fixed : 固定套餐，内存 = OCPU × mem_per_ocpu，不可任选配比
SHAPES = {
    "E5":  ("B97384", "B97385", "flex",  None, "VM.Standard.E5.Flex"),
    "E4":  ("B93113", "B93114", "flex",  None, "VM.Standard.E4.Flex"),
    "E3":  ("B92306", "B92307", "flex",  None, "VM.Standard.E3.Flex"),
    "X9":  ("B94176", "B94177", "flex",  None, "VM.Standard.X9.Flex"),
    "E2":  ("B90425", None,     "fixed", 8,    "VM.Standard.E2.{n}"),   # 1/2/4/8 OCPU，内存=8×OCPU
    "A1":  ("B93297", "B93298", "flex",  None, "VM.Standard.A1.Flex"),  # ARM，免费额度内为 0
}
DEFAULT_SHAPE = "E5"


def _fetch(timeout: int = 120) -> dict:
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    if os.path.exists(CACHE) and time.time() - os.path.getmtime(CACHE) < CACHE_TTL:
        with open(CACHE) as f:
            return json.load(f)
    req = urllib.request.Request(BASE, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    with open(CACHE, "w") as f:
        json.dump(data, f)
    return data


def _part_index(data: dict) -> dict:
    return {i["partNumber"]: i for i in data.get("items", [])}


def _usd(item: dict) -> float:
    """取 PAY_AS_YOU_GO 的 USD 价。有区间价时取第一段（通常即免费额度/基础档）。"""
    for c in item.get("currencyCodeLocalizations", []):
        if c.get("currencyCode") != "USD":
            continue
        for p in c.get("prices", []):
            if p.get("model") == "PAY_AS_YOU_GO":
                return float(p.get("value", 0) or 0)
    raise KeyError("该 SKU 无 USD PAY_AS_YOU_GO 价")


def query(shape: str = DEFAULT_SHAPE, vcpu: int = 0, mem: int = 0, **_) -> dict:
    """返回 {'shape','ocpu','mem_gb','usd_hr','unit','exact','raw'}；usd_hr 为 USD/hr。

    exact=False 表示该 shape 只能按固定套餐供给，实际内存高于请求值（超配）。
    """
    ocpu_pn, mem_pn, kind, mem_per_ocpu, tpl = SHAPES[shape]
    idx = _part_index(_fetch())

    if ocpu_pn not in idx:
        raise KeyError(f"partNumber 不在价目表: {ocpu_pn}（价目表可能已改版）")

    ocpu_unit = _usd(idx[ocpu_pn])
    mem_unit = _usd(idx[mem_pn]) if mem_pn and mem_pn in idx else 0.0

    # vCPU → OCPU：1 OCPU = 2 vCPU（两个超线程执行线程）
    ocpu = max(1, (vcpu + 1) // 2)
    req_gb = mem or 0

    if kind == "fixed":
        # 固定套餐：向上取到能满足内存需求的整数 OCPU
        while ocpu * mem_per_ocpu < req_gb:
            ocpu += 1
        gb = ocpu * mem_per_ocpu
        total = ocpu * ocpu_unit
    else:
        gb = req_gb
        total = ocpu * ocpu_unit + gb * mem_unit

    return {
        "shape": tpl.format(n=ocpu) if kind == "fixed" else tpl,
        "ocpu": ocpu,
        "mem_gb": gb,
        "usd_hr": round(total, 6),
        "unit": "Hrs",
        # 固定套餐且实际内存 ≠ 请求内存 → 超配，比价时需披露
        "exact": (kind == "flex") or (gb == req_gb),
        "raw": {"ocpu_unit": ocpu_unit, "mem_unit": mem_unit, "kind": kind},
    }


def list_shapes(vcpu: int = 4, mem: int = 16) -> list:
    """列出所有通用型 shape 在同一规格下的 USD/hr，便于选最低价。"""
    idx = _part_index(_fetch())
    out = []
    for k, (ocpu_pn, mem_pn, kind, mem_per_ocpu, tpl) in SHAPES.items():
        if ocpu_pn not in idx:
            continue
        try:
            r = query(shape=k, vcpu=vcpu, mem=mem)
            out.append({"shape": k, "display": r["shape"], "usd_hr": r["usd_hr"],
                        "exact": r["exact"]})
        except Exception:
            continue
    return sorted(out, key=lambda r: r["usd_hr"])
