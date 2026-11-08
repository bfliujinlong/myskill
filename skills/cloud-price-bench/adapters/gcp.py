"""Google Cloud (GCP) Compute Engine 定价适配器 —— 完全匿名，零凭据。

数据源：gcloud-compute.com 的机型详情页（按区域给出 on-demand USD/hr）。
实测 2026-10-31：HTTP 200，一个机型页覆盖 42 个区域，正则可解析，无需任何 API Key。

为什么不用官方通道（已三重实测排除）：
  - cloudbilling.googleapis.com：匿名 403 unregistered callers，必须 API Key
  - 官方 /products/compute/pricing：纯 JS 渲染，静态抓取拿不到价
  - gstatic / cloudbillingstorage 静态价目表：404 已下线

口径对齐 bench.py：Linux · on-demand · USD/hr。
默认区域 us-central1（GCP 定价基准区，与 AWS us-east-1 / Azure eastus 对齐）。
"""
import os
import re
import time
import urllib.request

UA = "Mozilla/5.0 (compatible; cloud-price-bench/1.0)"
BASE = "https://gcloud-compute.com"
DEFAULT_REGION = "us-central1"

# 从 title 属性里精确抓 "Costs per hour for machine type X in region Y: Z USD"
# 用 [^ ]+ 而非机型名，避免机型族前缀误匹配；首个匹配即 on-demand（其后是 spot/month/CUD）
_HR_RE = re.compile(
    r"Costs per hour for machine type (?P<mtype>[^\s]+) in region "
    r"(?P<region>[a-z0-9\-]+): (?P<price>\d+(?:\.\d+)?) USD"
)
# 机型规格在 meta description 里："... with 2 vCPU and 4 GB memory."
_SPEC_RE = re.compile(
    r"with\s+(?P<vcpu>\d+)\s*vCPU[s]?\s+and\s+(?P<mem>[\d\.]+)\s*GB\s+memory", re.I
)

CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cache")
CACHE_TTL = 7 * 86400  # 价目表更新慢，缓存 7 天

# vCPU → 默认机型；e2 是 GCP 通用型主力，与 AWS t3 / Azure D v3 / OCI E2 同一档位
SHAPES = ["e2-medium", "e2-standard-2", "e2-standard-4", "e2-standard-8",
          "e2-standard-16", "n2-standard-2", "n2-standard-4", "n2-standard-8"]


def _http(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "ignore")


def _cache_path(mtype: str) -> str:
    os.makedirs(CACHE_DIR, exist_ok=True)
    return os.path.join(CACHE_DIR, f"gcp_{mtype}.html")


def _fetch(mtype: str) -> str:
    """带 7 天本地缓存地拉取机型页，避免每次比价都打对方站点。"""
    p = _cache_path(mtype)
    try:
        if os.path.exists(p) and time.time() - os.path.getmtime(p) < CACHE_TTL:
            with open(p, encoding="utf-8") as f:
                return f.read()
    except OSError as e:
        print(f"[gcp] 读缓存失败（继续走网络）: {e}")
    html = _http(f"{BASE}/{mtype}.html")
    try:
        with open(p, "w", encoding="utf-8") as f:
            f.write(html)
    except OSError as e:
        print(f"[gcp] 写缓存失败（忽略，不阻断取价）: {e}")
    return html


def prices(mtype: str) -> dict:
    """返回 {region: usd_hr}，只取 on-demand（每个 region 首条 hour 记录）。"""
    html = _fetch(mtype)
    out = {}
    for m in _HR_RE.finditer(html):
        # 同 region 第一条是 on-demand，后续为 spot，用 setdefault 保住第一条
        out.setdefault(m.group("region"), float(m.group("price")))
    if not out:
        raise RuntimeError(f"gcp: 机型 {mtype} 未解析到任何价格，页面结构可能变了")
    return out


def spec(mtype: str) -> dict:
    """返回 {'vcpu': int, 'mem_gb': float}；解析不到返回空 dict。"""
    html = _fetch(mtype)
    m = _SPEC_RE.search(html)
    if not m:
        return {}
    return {"vcpu": int(m.group("vcpu")), "mem_gb": float(m.group("mem"))}


def list_shapes(region: str = DEFAULT_REGION, limit: int = 20) -> list:
    """列出已知机型的规格与单价，供 bench 选最低价机型。"""
    out = []
    for mtype in SHAPES[:limit]:
        try:
            p = prices(mtype).get(region)
            s = spec(mtype)
        except Exception as e:  # 单个机型拉取失败不阻断整体比价
            print(f"[gcp] {mtype} 取价失败（跳过）: {e}")
            continue
        if p is None:
            continue
        out.append({"shape": mtype, "vcpu": s.get("vcpu"), "mem_gb": s.get("mem_gb"),
                    "usd_hr": p, "region": region})
    return out


def query(mtype: str = "e2-standard-2", region: str = DEFAULT_REGION, **_) -> dict:
    """单机型取价，返回 bench.py 归一所需的字段。"""
    p = prices(mtype).get(region)
    if p is None:
        raise KeyError(f"gcp: 机型 {mtype} 在 {region} 无价（可能未在该区域开放）")
    s = spec(mtype)
    return {
        "shape": mtype,
        "vcpu": s.get("vcpu"),
        "mem_gb": s.get("mem_gb"),
        "usd_hr": p,
        "region": region,
        "currency": "USD",
        "unit": "hour",
        "exact": True,
        "raw": {"regions": len(prices(mtype))},
    }
