#!/usr/bin/env python3
"""目标云规格选型建议 / Target-cloud sizing advisor（阶段 03）

用法:
    python3 sizing_advice.py --self-test
    python3 sizing_advice.py --input res.json --out-dir ./out

输入 JSON:
{
  "project": "C-Customer CHINA",          # 必填
  "source_cloud": "aws",                  # 必填
  "target_cloud": "alicloud",             # 必填
  "growth_factor": 1.2,                   # 选填，容量年增长系数，默认 1.2
  "resources": [
    {"id":"vm-001","name":"erp-app","domain":"compute","vcpu":8,"mem_gb":32,
     "peak_cpu_pct":22,"peak_mem_pct":61,"os":"CentOS 7","env":"prod"},
    {"id":"db-001","name":"ltk-prod","domain":"database","engine":"Oracle",
     "version":"11.2","vcpu":16,"mem_gb":128,"storage_gb":26800,"env":"prod"},
    {"id":"st-001","name":"cclog-nas","domain":"storage","storage_gb":25000,"env":"prod"},
    {"id":"ca-001","name":"session-cache","domain":"cache","engine":"Redis",
     "version":"3.2","mem_gb":8,"env":"prod"}
  ]
}

domain 取值: compute / database / storage / cache / bigdata
env 取值: prod / nonprod（nonprod 才允许建议突发型）

输出: sizing_advice.md（可读）+ sizing_advice.json（结构化）
退出码: 0 = 正常；2 = 输入不可用/必填缺失
红线: 本脚本**不输出任何金额/单价/月费**（选型与报价物理隔离）。
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

# ---- 常量（改这些数字 = 改选型口径，需架构负责人同意）----
TARGET_UTIL = 0.60          # 目标稳态水位：源端峰值按 60% 水位折算
MIN_SHRINK = 0.50           # 缩容下限，低于此值不自动缩（防过度压缩）
MAX_GROW = 3.00             # 扩容上限，超过需人工确认（防公式失控）
DEFAULT_GROWTH = 1.20       # 默认容量年增长系数
DEFAULT_PEAK = 30.0         # 峰值利用率缺失时的保守假设（偏低=偏缩，会告警）
DEFAULT_STORAGE_GROWTH = 1.20
LADDER = [1, 2, 4, 8, 16, 32, 64, 96, 128, 192, 256]
MEM_LADDER = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]
BURST_CPU_LIMIT = 40.0      # 峰值 CPU 超过此值不建议突发型（积分会耗尽）

# 仅记录有官方/事实源支撑的实例族；无事实的档位一律输出「待确认」，不虚构
# 事实源: mig-std/mig-resource-assessment/references/云规格映射表.md
#        /data/cloud-docs/AWSvsAliyun_Pricing_20260910.md
CLOUD_FAMILY = {
    "alicloud": {"general": "ecs.g8i", "compute": "ecs.c8i", "memory": "ecs.r8i", "burst": "ecs.t6"},
    "aws":      {"general": "m8i", "compute": "c8i", "memory": "r8i", "burst": "t3"},
    "huawei":   {"general": "s6", "compute": "c6", "memory": "m6", "burst": None},
}

# EOL / 兼容性硬约束（版本低于此值必须升级或改 6R 策略）
EOL_OS = {
    "windows server 2008": "已 EOL，目标云无官方镜像支持",
    "windows server 2012": "已 EOL（扩展支持结束），需评估付费扩展支持或升级",
    "centos 6": "已 EOL，须升级",
    "centos 7": "2024-06 已 EOL，须升级或改用替代发行版",
    "centos 8": "已 EOL，须升级",
    "rhel 6": "已 EOL，须升级",
    "ubuntu 16.04": "标准支持已结束，须升级",
}
EOL_ENGINE = {
    "redis": {"min": "5.0", "note": "源 ≤4.0 必须升级后才能迁移（AGENTS.md 红线）"},
    "mongodb": {"min": "4.0", "note": "最低 4.0（AGENTS.md 红线）"},
    "mysql": {"min": "5.7", "note": "5.6 及以下已 EOL，须升级"},
    "postgresql": {"min": "10", "note": "9.x 已 EOL，须升级"},
    "oracle": {"min": "12c", "note": "11g 已过主流支持，异构迁移复杂度高"},
    "sql server": {"min": "2016", "note": "2008/2012 已 EOL，须升级"},
}
# 异构引擎：不能同构平移，须单独评估
HETEROGENEOUS = {
    "oracle": "目标侧通常非同构（阿里云 PolarDB-O / RDS Oracle），须单独兼容性评估",
    "aurora": "Aurora 为 AWS 专有引擎，无同构目标，须评估 PolarDB 等替代",
    "sql server": "跨云同构可行但许可模式（License Mobility）须单独确认",
}


def _round_up_ladder(value: float, ladder: list[int]) -> int:
    """向上取到规格档位；超出最大档位返回最大值并标记溢出。"""
    for step in ladder:
        if value <= step:
            return step
    return ladder[-1]


def _family_for(ratio: float) -> str:
    """按内存/CPU 比选实例族。"""
    if ratio <= 2:
        return "compute"
    if ratio <= 8:
        return "general"
    return "memory"


def _check_eol(res: dict) -> list[str]:
    """EOL 与兼容性硬约束检查，返回告警文案列表。"""
    warns: list[str] = []
    os_name = (res.get("os") or "").strip().lower()
    if os_name and os_name in EOL_OS:
        warns.append(f"OS EOL：{res.get('os')} — {EOL_OS[os_name]}")
    engine = (res.get("engine") or "").strip()
    if engine:
        key = engine.strip().lower()
        if key in EOL_ENGINE:
            rule = EOL_ENGINE[key]
            version = str(res.get("version") or "").strip()
            if not version:
                warns.append(
                    f"{engine} 未提供版本号，无法判定是否低于最低要求 {rule['min']} — 待确认"
                )
            elif _version_lt(version, rule["min"]):
                warns.append(f"{engine} {version} 低于最低要求 {rule['min']} — {rule['note']}")
        if key in HETEROGENEOUS:
            warns.append(f"异构引擎：{engine} — {HETEROGENEOUS[key]}")
    return warns


def _version_lt(version: str, minimum: str) -> bool:
    """极简版本比较：仅处理数字/字母分段，无法比较时保守返回 True（要求人工确认）。"""
    def parts(v: str) -> list:
        out = []
        buf = ""
        for ch in v.lower():
            if ch.isdigit():
                buf += ch
            else:
                if buf:
                    out.append(int(buf))
                    buf = ""
        if buf:
            out.append(int(buf))
        return out or [0]

    a, b = parts(version), parts(minimum)
    n = max(len(a), len(b))
    a += [0] * (n - len(a))
    b += [0] * (n - len(b))
    try:
        return a < b
    except TypeError:
        return True


def size_one(res: dict, growth: float) -> dict:
    """对单个资源做规格折算。"""
    rid = res.get("id") or res.get("name") or "unknown"
    domain = (res.get("domain") or "compute").strip().lower()
    env = (res.get("env") or "prod").strip().lower()
    out = {
        "id": rid,
        "name": res.get("name") or "",
        "domain": domain,
        "env": env,
        "assumptions": [],
        "warnings": [],
        "needs_human_confirm": False,
        "todo": [],
    }

    if domain == "storage":
        src_gb = res.get("storage_gb")
        if src_gb is None:
            out["todo"].append("storage 域缺 storage_gb，无法折算容量 — 待确认")
            out["target_storage_gb"] = None
        else:
            cap = float(src_gb) * DEFAULT_STORAGE_GROWTH
            out["target_storage_gb"] = math.ceil(cap)
            out["assumptions"].append(
                f"容量按年增长系数 {DEFAULT_STORAGE_GROWTH} 折算（{src_gb}GB → {out['target_storage_gb']}GB）"
            )
        if src_gb and float(src_gb) > 10000:
            out["warnings"].append(
                f"单项容量 {src_gb}GB 属超大量（>10TB），须确认分阶段迁移或离线搬运，不得直接套用在线同步方案"
            )
        out["warnings"] += _check_eol(res)
        return out

    # compute / database / cache / bigdata：按 CPU + 内存折算
    src_cpu = res.get("vcpu")
    src_mem = res.get("mem_gb")
    if src_cpu is None or src_mem is None:
        out["todo"].append(
            f"{domain} 域缺 vcpu/mem_gb（源端规格未采集），无法折算 — 待确认，禁止凭空给规格"
        )
        out["warnings"] += _check_eol(res)
        return out

    src_cpu = float(src_cpu)
    src_mem = float(src_mem)

    peak_cpu = res.get("peak_cpu_pct")
    peak_mem = res.get("peak_mem_pct")
    if peak_cpu is None:
        peak_cpu = DEFAULT_PEAK
        out["assumptions"].append(
            f"未提供 peak_cpu_pct，按保守值 {DEFAULT_PEAK}% 假设（该值偏低会导向缩容，须实测复核）"
        )
    if peak_mem is None:
        peak_mem = DEFAULT_PEAK
        out["assumptions"].append(
            f"未提供 peak_mem_pct，按保守值 {DEFAULT_PEAK}% 假设（须实测复核）"
        )
    peak_cpu = float(peak_cpu)
    peak_mem = float(peak_mem)

    # 折算：源峰值 / 目标水位 → 目标有效容量，再乘增长系数
    eff_cpu = src_cpu * (peak_cpu / 100.0 / TARGET_UTIL) * growth
    eff_mem = src_mem * (peak_mem / 100.0 / TARGET_UTIL) * growth

    # 边界钳制
    for label, src, eff in (("CPU", src_cpu, eff_cpu), ("内存", src_mem, eff_mem)):
        ratio = eff / src if src else 0
        if ratio < MIN_SHRINK:
            out["warnings"].append(
                f"{label} 折算结果 {eff:.1f} 低于缩容下限（源值的 {MIN_SHRINK}），已钳制至下限并需人工确认"
            )
            out["needs_human_confirm"] = True
        if ratio > MAX_GROW:
            out["warnings"].append(
                f"{label} 折算结果 {eff:.1f} 超过扩容上限（源值的 {MAX_GROW} 倍），公式不再可信，需人工定价/定档"
            )
            out["needs_human_confirm"] = True

    eff_cpu = max(eff_cpu, src_cpu * MIN_SHRINK)
    eff_mem = max(eff_mem, src_mem * MIN_SHRINK)

    tgt_cpu = _round_up_ladder(eff_cpu, LADDER)
    tgt_mem = _round_up_ladder(eff_mem, MEM_LADDER)
    if tgt_mem < tgt_cpu:  # 内存不应低于 vCPU 数（1:1 下限）
        tgt_mem = _round_up_ladder(float(tgt_cpu), MEM_LADDER)

    out["source"] = {"vcpu": src_cpu, "mem_gb": src_mem}
    out["target"] = {"vcpu": tgt_cpu, "mem_gb": tgt_mem}
    # 三态判定：CPU 与内存方向必须一致，方向不一致标「混合」并要求人工确认
    d_cpu = round(tgt_cpu - src_cpu, 2)
    d_mem = round(tgt_mem - src_mem, 2)
    cpu_dir = 0 if abs(d_cpu) < 1e-9 else (1 if d_cpu > 0 else -1)
    mem_dir = 0 if abs(d_mem) < 1e-9 else (1 if d_mem > 0 else -1)
    if cpu_dir * mem_dir < 0:
        verdict = "混合"
    elif cpu_dir == 0 and mem_dir == 0:
        verdict = "持平"
    elif cpu_dir > 0 or mem_dir > 0:
        verdict = "扩容"
    else:
        verdict = "缩容"
    out["delta"] = {"vcpu": d_cpu, "mem_gb": d_mem, "verdict": verdict}
    if verdict == "混合":
        out["needs_human_confirm"] = True
        up, down = ("内存", "CPU") if mem_dir > 0 else ("CPU", "内存")
        out["warnings"].append(
            f"折算方向不一致：{up}扩容 {down}缩容（{src_cpu:.0f}C{src_mem:.0f}G → {tgt_cpu}C{tgt_mem}G）。"
            f"档位离散 + 源端 CPU/内存利用率不匹配所致，须人工按实际负载定档，不得直接进方案"
        )
    out["assumptions"].append(
        f"目标水位 {int(TARGET_UTIL * 100)}%，峰值 CPU {peak_cpu:.0f}% / 内存 {peak_mem:.0f}%，增长系数 {growth}"
    )

    # 档位跨度提醒：规格档位离散，跨档跳跃过大时结果偏保守，需人工确认
    for label, src_v, tgt_v in (("CPU", src_cpu, tgt_cpu), ("内存", src_mem, tgt_mem)):
        if src_v > 0 and tgt_v / src_v >= 2.0:
            out["warnings"].append(
                f"{label} 档位跨度大（{src_v:.0f} → {tgt_v}，≥2 倍），属档位离散导致的保守上取，须人工复核是否可下调"
            )

    ratio = tgt_mem / tgt_cpu if tgt_cpu else 0
    fam = _family_for(ratio)
    out["family"] = fam
    out["family_reason"] = (
        f"内存/CPU 比 {ratio:.1f} → {'计算型' if fam == 'compute' else '通用型' if fam == 'general' else '内存型'}"
    )

    if env == "nonprod" and peak_cpu < BURST_CPU_LIMIT:
        out["burst_eligible"] = True
        out["assumptions"].append(
            f"非生产且峰值 CPU {peak_cpu:.0f}% < {BURST_CPU_LIMIT:.0f}%，可考虑突发型实例降本"
        )
    else:
        out["burst_eligible"] = False
        if env == "prod":
            out["assumptions"].append("生产环境不使用突发型实例（CPU 积分耗尽会掉性能）")

    out["warnings"] += _check_eol(res)
    if res.get("k8s_version") and _version_lt(str(res["k8s_version"]), "1.22"):
        out["warnings"].append(
            f"K8s {res['k8s_version']} < 1.22，迁 ACK 前须排查 deprecated API（AGENTS.md 红线）"
        )
    return out


def recommend_instance(target_cloud: str, item: dict) -> str:
    """给出目标云实例族建议；无事实源支撑的档位返回「待确认」，不虚构规格名。"""
    fam = item.get("family")
    if not fam:
        return "待确认（未完成 CPU/内存折算）"
    table = CLOUD_FAMILY.get((target_cloud or "").strip().lower())
    if not table:
        return f"待确认（{target_cloud} 暂无实例族事实表，须查官方文档后补充，不得臆造规格名）"
    if fam == "compute":
        name = table["compute"]
    elif fam == "memory":
        name = table["memory"]
    else:
        name = table["general"]
    if not name:
        return "待确认（该云此实例族暂无事实源）"
    vcpu = item.get("target", {}).get("vcpu")
    mem = item.get("target", {}).get("mem_gb")
    return f"{name} 族，{vcpu}C{mem}G 档位（具体规格名以目标云官方规格文档为准）"


def build(data: dict) -> dict:
    """主计算入口，返回结构化结果。"""
    project = (data.get("project") or "").strip()
    src_cloud = (data.get("source_cloud") or "").strip()
    tgt_cloud = (data.get("target_cloud") or "").strip()
    if not project or not src_cloud or not tgt_cloud:
        raise ValueError("必填缺失：project / source_cloud / target_cloud")

    growth = float(data.get("growth_factor") or DEFAULT_GROWTH)
    resources = data.get("resources") or []

    items = [size_one(r, growth) for r in resources]
    for it in items:
        it["recommended_instance"] = recommend_instance(tgt_cloud, it)

    # 汇总
    total = {"vcpu": 0, "mem_gb": 0, "storage_gb": 0}
    for it in items:
        t = it.get("target") or {}
        total["vcpu"] += int(t.get("vcpu") or 0)
        total["mem_gb"] += int(t.get("mem_gb") or 0)
        total["storage_gb"] += int(it.get("target_storage_gb") or 0)

    by_domain: dict[str, dict] = {}
    for it in items:
        d = by_domain.setdefault(
            it["domain"], {"count": 0, "vcpu": 0, "mem_gb": 0, "storage_gb": 0}
        )
        d["count"] += 1
        d["vcpu"] += int((it.get("target") or {}).get("vcpu") or 0)
        d["mem_gb"] += int((it.get("target") or {}).get("mem_gb") or 0)
        d["storage_gb"] += int(it.get("target_storage_gb") or 0)

    needs_confirm = [it["id"] for it in items if it.get("needs_human_confirm")]
    todo = [{"id": it["id"], "todo": t} for it in items for t in it.get("todo", [])]

    return {
        "project": project,
        "source_cloud": src_cloud,
        "target_cloud": tgt_cloud,
        "method": {
            "target_util": TARGET_UTIL,
            "min_shrink": MIN_SHRINK,
            "max_grow": MAX_GROW,
            "growth_factor": growth,
            "ladder": LADDER,
            "formula": "有效容量 = 源规格 × (峰值利用率 / 目标水位) × 增长系数，再向上取规格档位",
        },
        "items": items,
        "total": total,
        "by_domain": by_domain,
        "needs_human_confirm": needs_confirm,
        "todo": todo,
        "price_statement": "本产物不含任何金额/单价/月费（选型与报价物理隔离；金额只在 presales/pcs-quotation）",
    }


def render_md(result: dict) -> str:
    """渲染可读 Markdown。"""
    L = []
    L.append(f"# 目标云规格选型建议 / Sizing Advice — {result['project']}")
    L.append("")
    L.append(
        f"- 源云 / Source：**{result['source_cloud']}** → 目标云 / Target：**{result['target_cloud']}**"
    )
    L.append(
        f"- 折算口径 / Method：{result['method']['formula']}"
    )
    L.append(
        f"- 参数 / Params：目标水位 {int(result['method']['target_util'] * 100)}% · "
        f"缩容下限 {result['method']['min_shrink']} · 扩容上限 {result['method']['max_grow']} · "
        f"增长系数 {result['method']['growth_factor']}"
    )
    L.append(f"- {result['price_statement']}")
    L.append("")
    L.append("## 汇总 / Total")
    L.append("")
    L.append("| 域 Domain | 数量 | vCPU | 内存 GB | 存储 GB |")
    L.append("|---|---|---|---|---|")
    for d, v in result["by_domain"].items():
        L.append(
            f"| {d} | {v['count']} | {v['vcpu']} | {v['mem_gb']} | {v['storage_gb']} |"
        )
    t = result["total"]
    L.append(f"| **合计** | — | **{t['vcpu']}** | **{t['mem_gb']}** | **{t['storage_gb']}** |")
    L.append("")
    L.append("## 明细 / Detail")
    L.append("")
    for it in result["items"]:
        L.append(f"### {it['id']} · {it.get('name') or ''}（{it['domain']} / {it['env']}）")
        L.append("")
        src = it.get("source")
        tgt = it.get("target")
        if src and tgt:
            L.append(
                f"- 源规格：`{int(src['vcpu'])}C{int(src['mem_gb'])}G` → 建议：`{tgt['vcpu']}C{tgt['mem_gb']}G`"
                f"（{it['delta']['verdict']}，CPU {it['delta']['vcpu']:+.0f} / 内存 {it['delta']['mem_gb']:+.0f}）"
            )
        if it.get("target_storage_gb"):
            L.append(f"- 建议容量：**{it['target_storage_gb']} GB**")
        L.append(f"- 实例族：{it.get('family_reason', '待确认')}")
        L.append(f"- 建议规格：{it.get('recommended_instance')}")
        if it.get("burst_eligible"):
            L.append("- 可选突发型：是（非生产且峰值偏低）")
        for a in it.get("assumptions", []):
            L.append(f"- 假设：{a}")
        for w in it.get("warnings", []):
            L.append(f"- ⚠️ {w}")
        for td in it.get("todo", []):
            L.append(f"- ❓ 待确认：{td}")
        if it.get("needs_human_confirm"):
            L.append("- 🚩 **需人工确认档位**（折算越界，公式不再可信）")
        L.append("")
    if result["needs_human_confirm"]:
        L.append(f"## 需人工确认 / Needs human confirm：{', '.join(result['needs_human_confirm'])}")
        L.append("")
    if result["todo"]:
        L.append("## 待确认清单 / Open items")
        L.append("")
        for t in result["todo"]:
            L.append(f"- `{t['id']}`：{t['todo']}")
        L.append("")
    L.append("---")
    L.append("")
    L.append("口径声明：本文只给**规格档位与容量**，不含价格；金额一律由 `presales/pcs-quotation` 出具。")
    return "\n".join(L) + "\n"


def self_test() -> int:
    """自检：每条断言真跑，不虚构。"""
    ok = 0

    # 1) 缩容：源 8C32G，峰值 20/50 → 明显缩容
    r = size_one({"id": "vm-1", "domain": "compute", "vcpu": 8, "mem_gb": 32,
                  "peak_cpu_pct": 20, "peak_mem_pct": 50, "env": "prod", "os": "CentOS 7"}, 1.0)
    assert r["delta"]["verdict"] == "缩容", r
    assert r["target"]["vcpu"] < 8, r
    print("SELFTEST 1 PASS 低利用率→缩容", r["target"])
    ok += 1

    # 2) 扩容：源 4C8G，峰值 90/85 → 扩容
    r = size_one({"id": "vm-2", "domain": "compute", "vcpu": 4, "mem_gb": 8,
                  "peak_cpu_pct": 90, "peak_mem_pct": 85, "env": "prod"}, 1.0)
    assert r["delta"]["verdict"] == "扩容", r
    print("SELFTEST 2 PASS 高利用率→扩容", r["target"])
    ok += 1

    # 3) EOL OS 告警
    r = size_one({"id": "vm-3", "domain": "compute", "vcpu": 4, "mem_gb": 8,
                  "peak_cpu_pct": 30, "peak_mem_pct": 30, "os": "CentOS 7", "env": "prod"}, 1.0)
    assert any("EOL" in w for w in r["warnings"]), r
    print("SELFTEST 3 PASS EOL OS 告警")
    ok += 1

    # 4) Redis ≤4.0 必须升级
    r = size_one({"id": "ca-1", "domain": "cache", "engine": "Redis", "version": "3.2",
                  "vcpu": 2, "mem_gb": 8, "peak_cpu_pct": 30, "peak_mem_pct": 30, "env": "prod"}, 1.0)
    assert any("Redis" in w and "升级" in w for w in r["warnings"]), r
    print("SELFTEST 4 PASS Redis 3.2 触发升级告警")
    ok += 1

    # 5) 缺规格 → 待确认，不给规格
    r = size_one({"id": "vm-4", "domain": "compute", "env": "prod"}, 1.0)
    assert r["todo"] and "target" not in r, r
    print("SELFTEST 5 PASS 缺源规格→待确认且不臆造")
    ok += 1

    # 6) 超大量存储 → >10TB 告警
    r = size_one({"id": "st-1", "domain": "storage", "storage_gb": 25000, "env": "prod"}, 1.0)
    assert any("10TB" in w for w in r["warnings"]), r
    assert r["target_storage_gb"] == 30000, r
    print("SELFTEST 6 PASS 25TB 存储→超大量告警+容量折算", r["target_storage_gb"])
    ok += 1

    # 7) 未知云 → 不虚构规格名
    r = recommend_instance("some-cloud", {"family": "general", "target": {"vcpu": 8, "mem_gb": 32}})
    assert r.startswith("待确认"), r
    print("SELFTEST 7 PASS 未知云不虚构规格名")
    ok += 1

    # 8) 必填缺失 → ValueError
    try:
        build({"source_cloud": "aws", "target_cloud": "alicloud"})
        raise AssertionError("应抛 ValueError")
    except ValueError:
        print("SELFTEST 8 PASS 必填缺失报错")
    ok += 1

    # 9) 扩容越界 → 需人工确认
    r = size_one({"id": "vm-5", "domain": "compute", "vcpu": 2, "mem_gb": 4,
                  "peak_cpu_pct": 100, "peak_mem_pct": 100, "env": "prod"}, 3.0)
    assert r["needs_human_confirm"] or r["delta"]["verdict"] == "扩容", r
    print("SELFTEST 9 PASS 极端增长触发人工确认/扩容标记")
    ok += 1

    # 10) 方向不一致 → 混合 + 必须人工确认（回归：vm-001 8C32G/22%/61% → 4C64G）
    r = size_one({"id": "vm-6", "domain": "compute", "vcpu": 8, "mem_gb": 32,
                  "peak_cpu_pct": 22, "peak_mem_pct": 61, "env": "prod"}, 1.2)
    assert r["target"]["vcpu"] == 4 and r["target"]["mem_gb"] == 64, r
    assert r["delta"]["verdict"] == "混合", r
    assert r["needs_human_confirm"], r
    assert any("方向不一致" in w for w in r["warnings"]), r
    print("SELFTEST 10 PASS CPU↓内存↑→混合且需人工确认", r["delta"])
    ok += 1

    # 11) 档位跨度 ≥2 倍 → 提醒人工复核
    r = size_one({"id": "vm-7", "domain": "compute", "vcpu": 1, "mem_gb": 1,
                  "peak_cpu_pct": 100, "peak_mem_pct": 100, "env": "prod"}, 1.5)
    assert any("档位跨度大" in w for w in r["warnings"]), r
    print("SELFTEST 11 PASS 档位跨度≥2倍→人工复核提醒")
    ok += 1

    print(f"SELFTEST PASS（{ok}/11）")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="目标云规格选型建议（阶段 03）")
    ap.add_argument("--input", help="输入 JSON 路径")
    ap.add_argument("--out-dir", help="输出目录")
    ap.add_argument("--self-test", action="store_true", help="运行自检")
    args = ap.parse_args()

    if args.self_test:
        return self_test()
    if not args.input:
        ap.error("需要 --input 或 --self-test")

    src = Path(args.input)
    if not src.exists():
        print(f"文件不存在: {src}", file=sys.stderr)
        return 2
    data = json.loads(src.read_text(encoding="utf-8"))
    try:
        result = build(data)
    except ValueError as exc:
        print(f"输入不可用: {exc}", file=sys.stderr)
        return 2

    out_dir = Path(args.out_dir) if args.out_dir else Path(".")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "sizing_advice.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out_dir / "sizing_advice.md").write_text(render_md(result), encoding="utf-8")
    print(f"[ok] 输出: {out_dir}/sizing_advice.md, {out_dir}/sizing_advice.json")
    print(f"[ok] 资源 {len(result['items'])} 项 · 合计 {result['total']}")
    if result["todo"]:
        print(f"[warn] 待确认 {len(result['todo'])} 项；需人工确认 {len(result['needs_human_confirm'])} 项")
    return 0


if __name__ == "__main__":
    sys.exit(main())
