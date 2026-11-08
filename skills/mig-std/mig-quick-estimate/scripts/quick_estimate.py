#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 第 1 次调研粗估 driver：资源表 -> 规模因子 x 平均复杂度 -> 人天 -> 周期 -> 成本区间
# 算法来源：用户模板「云迁移售前工时评估系统 V6」（/tmp/FEC86FCE-*.html），公式与常量一一对应
# 纪律：缺必填 -> rc=2 并说明原因（不猜数）；不出对外报价（金额口径唯一在 presales/pcs-quotation）
# 依赖：stdlib only（md/json 输出）
"""mig-quick-estimate driver.

输入 JSON：
{
  "project": "客户名-项目名",
  "source_cloud": "aws", "target_cloud": "alicloud",
  "resources": {
    "business_systems": 10,      # 业务系统数量（权重 10，影响极高）
    "vms": 80,                   # 虚拟机（权重 0.2）
    "kubernetes_nodes": 0,       # K8s 节点（权重 0.3）
    "container_instances": 0,    # 容器实例（权重 0.1）
    "databases": {"mysql": 4, "oracle": 2, "sqlserver": 0, "redis": 3, "mongodb": 0}
  },
  "complexity": {                # 各维度 1-5；缺项默认取 3（中性）并在告警中列出
    "technical_complexity": 3.5, # 技术栈（语言/前端/多语言/架构/第三方集成）
    "business_complexity": 3.5,
    "integration_complexity": 3.0,
    "security_complexity": 4.0,
    "compliance_complexity": 4.5
  },
  "rates": {"junior": 2000, "mid": 2500, "senior": 3500, "pm": 4000},   # 选填，日成本
  "headcount": {"junior": 0.3, "mid": 0.45, "senior": 0.2, "pm": 0.05}, # 选填，人力占比
  "other_costs": {"training": 45000, "contingency": 75000, "resource": 100000},  # 选填
  "band": 0.25,                  # 选填，价格区间带宽（默认 ±25%）
  "out_dir": "./out"
}
输出：快速估算.md / 快速估算.json
"""
from __future__ import annotations

import argparse, json, math, os, sys
from datetime import date

TBD = "待确认"

# ---------- 常量（与 V6 模板 CONFIG 一致；改动这些数字 = 改报价口径，需商务同意） ----------
WORK_DAYS_PER_WEEK = 5

# 资源权重：业务系统 10 / 虚拟机 0.2 / K8s 节点 0.3 / 容器实例 0.1 / 数据库实例 1.0
RESOURCE_WEIGHTS = {
    "business_systems": 10.0,
    "vms": 0.2,
    "kubernetes_nodes": 0.3,
    "container_instances": 0.1,
}

# 阶段工时占比（合计 1.0）
HOUR_RATIOS = [
    ("需求调研", 0.12),
    ("方案规划", 0.18),
    ("实施部署", 0.45),
    ("测试验证", 0.15),
    ("验收交付", 0.10),
]

# 复杂度维度（中文名, key, 默认中性值）
COMPLEXITY_DIMS = [
    ("技术复杂度", "technical_complexity", 3.0),
    ("业务复杂度", "business_complexity", 3.0),
    ("集成复杂度", "integration_complexity", 3.0),
    ("安全要求", "security_complexity", 3.0),
    ("合规等级", "compliance_complexity", 3.0),
]

# 资源项中文标签（表格展示用）
RES_LABEL = {
    "business_systems": "业务系统数量",
    "vms": "虚拟机数量",
    "kubernetes_nodes": "Kubernetes 节点数量",
    "container_instances": "容器实例数量",
    "databases(合计)": "数据库实例合计",
}

DEFAULT_RATES = {"junior": 2000, "mid": 2500, "senior": 3500, "pm": 4000}
DEFAULT_HEADCOUNT = {"junior": 0.30, "mid": 0.45, "senior": 0.20, "pm": 0.05}
ROLE_LABEL = {"junior": "初级工程师", "mid": "中级工程师",
              "senior": "高级工程师", "pm": "项目经理"}


def js_round(x: float) -> int:
    """复刻 JS Math.round 语义（四舍五入，负数半值向上），而非 Python banker's rounding。

    模板 V6 用 Math.round(462.5)=463，Python round(462.5)=462，差 1 人天，必须对齐。
    """
    import math
    return int(math.floor(x + 0.5))


def rc2(msg: str) -> int:
    """缺必填 -> rc=2 并说明原因（绝不猜数）"""
    print("ERROR rc=2: %s" % msg)
    return 2


def validate(cfg: dict) -> list:
    """返回告警清单；致命问题由调用方 rc=2 处理"""
    warns = []
    res = cfg.get("resources")
    if not isinstance(res, dict) or not res:
        return ["resources 缺失或为空"]
    # business_systems 是核心驱动，缺失即无法估
    if res.get("business_systems") is None:
        return ["resources.business_systems 缺失（权重 10，缺失无法估算）"]
    for k, v in res.items():
        if k == "databases":
            continue
        if not isinstance(v, (int, float)) or v < 0:
            warns.append("resources.%s 非数值或为负：%r（按 0 处理需确认）" % (k, v))
    cx = cfg.get("complexity") or {}
    for label, key, dflt in COMPLEXITY_DIMS:
        if key not in cx:
            warns.append("complexity.%s 未提供，按中性值 %s 计入（需客户确认）" % (key, dflt))
        else:
            v = cx[key]
            if not isinstance(v, (int, float)) or not (1 <= v <= 5):
                warns.append("complexity.%s 越界：%r（应 1-5）" % (key, v))
    band = cfg.get("band", 0.25)
    if not isinstance(band, (int, float)) or not (0 < band < 1):
        warns.append("band=%r 越界（应 0-1），回退 0.25" % band)
    return warns


def calc(cfg: dict) -> dict:
    """核心：resourceFactor * avgComplexity -> 总人天 -> 阶段拆分 -> 周期 -> 成本区间"""
    res = cfg["resources"]
    db = res.get("databases") or {}
    db_total = sum(v for v in db.values() if isinstance(v, (int, float)))

    # 1) 资源规模因子
    factor_breakdown = []
    resource_factor = 0.0
    for key, weight in RESOURCE_WEIGHTS.items():
        cnt = res.get(key) or 0
        cnt = cnt if isinstance(cnt, (int, float)) else 0
        contrib = cnt * weight
        resource_factor += contrib
        factor_breakdown.append({"项": key, "数量": cnt, "权重": weight, "贡献": round(contrib, 2)})
    resource_factor += db_total * 1.0
    factor_breakdown.append({"项": "databases(合计)", "数量": db_total, "权重": 1.0,
                             "贡献": round(db_total * 1.0, 2)})

    # 2) 平均复杂度（5 维取均值，缺失用中性值）
    cx = cfg.get("complexity") or {}
    dims = []
    total_cx = 0.0
    for label, key, dflt in COMPLEXITY_DIMS:
        v = cx.get(key)
        v = v if isinstance(v, (int, float)) and 1 <= v <= 5 else dflt
        total_cx += v
        dims.append({"维度": label, "key": key, "分值": v, "来源": "客户填写" if key in cx else "默认中性"})
    avg_complexity = total_cx / len(COMPLEXITY_DIMS)

    # 3) 总人天 = round(资源因子 * 平均复杂度)（与 V6 baseHours 一致）
    base_days = js_round(resource_factor * avg_complexity)

    # 4) 阶段拆分（权重 x 总人天）；逐项四舍五入会产生尾差，统一归入占比最大的阶段
    phases = []
    for name, ratio in HOUR_RATIOS:
        phases.append({"阶段": name, "占比": ratio, "人天": js_round(base_days * ratio)})
    delta = base_days - sum(p["人天"] for p in phases)
    if delta and phases:
        biggest = max(phases, key=lambda p: p["占比"])
        biggest["人天"] += delta
        biggest["含尾差"] = delta

    # 5) 周期（周）= 总人天 / 每周工作日，向上取整（对齐 JS Math.ceil）
    total_weeks = int(math.ceil(base_days / WORK_DAYS_PER_WEEK)) if base_days else 0

    # 6) 成本区间（内部测算参考，非对外报价）
    band = cfg.get("band", 0.25)
    band = band if isinstance(band, (int, float)) and 0 < band < 1 else 0.25
    rates = dict(DEFAULT_RATES); rates.update(cfg.get("rates") or {})
    head = dict(DEFAULT_HEADCOUNT); head.update(cfg.get("headcount") or {})
    other = cfg.get("other_costs") or {}
    other_total = sum(v for v in other.values() if isinstance(v, (int, float)))

    blended_rate = sum(rates[r] * head.get(r, 0) for r in DEFAULT_RATES)
    labor = base_days * blended_rate
    cost_mid = labor + other_total
    money = {
        "口径": "内部成本测算参考（非对外报价）",
        "混合日成本": round(blended_rate, 2),
        "成本_低": round(cost_mid * (1 - band), 2),
        "成本_中": round(cost_mid, 2),
        "成本_高": round(cost_mid * (1 + band), 2),
        "带宽": band,
        "其他成本": {k: v for k, v in other.items()},
        "其他成本合计": other_total,
        "角色明细": [{"角色": ROLE_LABEL[r], "占比": head.get(r, 0),
                    "日成本": rates[r], "人天": round(base_days * head.get(r, 0), 1)}
                   for r in DEFAULT_RATES],
    }

    return {
        "project": cfg.get("project", TBD),
        "source_cloud": cfg.get("source_cloud", TBD),
        "target_cloud": cfg.get("target_cloud", TBD),
        "generated": str(date.today()),
        "resource_factor": round(resource_factor, 2),
        "factor_breakdown": factor_breakdown,
        "avg_complexity": round(avg_complexity, 3),
        "complexity_dims": dims,
        "man_days": base_days,
        "phases": phases,
        "duration_weeks": total_weeks,
        "money": money,
    }


def render_md(r: dict, warns: list) -> str:
    L = []
    A = L.append
    A("# 迁移工作量快速估算（第 1 次调研）")
    A("")
    A("| 项 | 值 |")
    A("|---|---|")
    A("| 项目 | %s |" % r["project"])
    A("| 源云 → 目标云 | %s → %s |" % (r["source_cloud"], r["target_cloud"]))
    A("| 生成日期 | %s |" % r["generated"])
    A("| 资源规模因子 | %.2f |" % r["resource_factor"])
    A("| 平均复杂度 | %.2f / 5.00 |" % r["avg_complexity"])
    A("| 估算总人天 | %d 人天 |" % r["man_days"])
    A("| 估算周期 | %d 周（按每周 5 工作日） |" % r["duration_weeks"])
    A("")
    A("> 口径声明：本文档为**第 1 次调研级粗估**，用于给客户「大致架构 + 价格范围」的沟通输入；")
    A("> **不是对外报价**，对外金额/单价/折扣唯一口径为 `presales/pcs-quotation`。")
    A("")
    A("## 一、资源规模因子拆解")
    A("")
    A("| 资源项 | 数量 | 权重 | 贡献 |")
    A("|---|---:|---:|---:|")
    for f in r["factor_breakdown"]:
        A("| %s | %s | %s | %.2f |" % (RES_LABEL.get(f["项"], f["项"]),
                                       f["数量"], f["权重"], f["贡献"]))
    A("| **合计** | | | **%.2f** |" % r["resource_factor"])
    A("")
    A("## 二、复杂度评分")
    A("")
    A("| 维度 | 分值 | 来源 |")
    A("|---|---:|---|")
    for d in r["complexity_dims"]:
        A("| %s | %s | %s |" % (d["维度"], d["分值"], d["来源"]))
    A("| **平均** | **%.2f** | |" % r["avg_complexity"])
    A("")
    A("## 三、阶段人天拆分")
    A("")
    A("| 阶段 | 占比 | 人天 |")
    A("|---|---:|---:|")
    for p in r["phases"]:
        A("| %s | %.0f%% | %d |" % (p["阶段"], p["占比"] * 100, p["人天"]))
    A("| **合计** | **100%%** | **%d** |" % r["man_days"])
    A("")
    A("## 四、成本区间（内部测算参考）")
    A("")
    m = r["money"]
    A("| 档位 | 金额（元） |")
    A("|---|---:|")
    A("| 低（-%d%%） | %s |" % (round(m["带宽"] * 100), format(m["成本_低"], ",")))
    A("| 中 | %s |" % format(m["成本_中"], ","))
    A("| 高（+%d%%） | %s |" % (round(m["带宽"] * 100), format(m["成本_高"], ",")))
    A("")
    A("混合日成本：%s 元/人天；其他成本（培训/应急/硬件）合计：%s 元" %
      (format(m["混合日成本"], ","), format(m["其他成本合计"], ",")))
    A("")
    A("| 角色 | 占比 | 日成本 | 人天 |")
    A("|---|---:|---:|---:|")
    for d in m["角色明细"]:
        A("| %s | %.0f%% | %s | %s |" % (d["角色"], d["占比"] * 100,
                                        format(d["日成本"], ","), d["人天"]))
    A("")
    if warns:
        A("## 五、告警与待确认")
        A("")
        for w in warns[:10]:
            A("- %s" % w)
        if len(warns) > 10:
            A("- …… 其余 %d 条见 JSON" % (len(warns) - 10))
        A("")
    A("## 下一步")
    A("")
    A("1. 用 `mig-survey-table` 收全资源表与 NFR，补齐缺失的复杂度评分事实依据；")
    A("2. 用 `mig-app-effort` 做第 2 次应用级深化估算（D1-D4 四维度 → L1-L5）；")
    A("3. 对外报价统一走 `presales/pcs-quotation`。")
    A("")
    return "\n".join(L)


def self_test() -> int:
    """内置自检：对齐 V6 模板默认场景（10 业务系统 / 80 VM / 9 数据库实例 / 复杂度均值）"""
    base = {
        "project": "self-test", "source_cloud": "aws", "target_cloud": "alicloud",
        "resources": {"business_systems": 10, "vms": 80, "kubernetes_nodes": 0,
                      "container_instances": 0,
                      "databases": {"mysql": 4, "oracle": 2, "redis": 3}},
        "complexity": {"technical_complexity": 3.5, "business_complexity": 3.5,
                       "integration_complexity": 3.0, "security_complexity": 4.0,
                       "compliance_complexity": 4.5},
    }
    ok = 0
    # 1) 资源因子：10*10 + 80*0.2 + 9*1.0 = 100 + 16 + 9 = 125
    r = calc(dict(base))
    assert abs(r["resource_factor"] - 125.0) < 1e-6, "资源因子应为 125，实际 %s" % r["resource_factor"]
    print("SELFTEST 1 PASS 资源因子=%.2f" % r["resource_factor"]); ok += 1
    # 2) 平均复杂度：(3.5+3.5+3.0+4.0+4.5)/5 = 3.7
    assert abs(r["avg_complexity"] - 3.7) < 1e-6, "平均复杂度应为 3.7，实际 %s" % r["avg_complexity"]
    print("SELFTEST 2 PASS 平均复杂度=%.2f" % r["avg_complexity"]); ok += 1
    # 3) 总人天 = round(125 * 3.7) = 463
    assert r["man_days"] == 463, "总人天应为 463，实际 %s" % r["man_days"]
    print("SELFTEST 3 PASS 总人天=%d" % r["man_days"]); ok += 1
    # 4) 阶段人天合计 == 总人天
    s = sum(p["人天"] for p in r["phases"])
    assert s == r["man_days"], "阶段合计 %d != 总人天 %d" % (s, r["man_days"])
    print("SELFTEST 4 PASS 阶段合计=%d" % s); ok += 1
    # 5) 周期 = ceil(463/5) = 93
    assert r["duration_weeks"] == 93, "周期应为 93，实际 %s" % r["duration_weeks"]
    print("SELFTEST 5 PASS 周期=%d 周" % r["duration_weeks"]); ok += 1
    # 6) 缺 business_systems -> rc=2
    bad = dict(base); bad["resources"] = {"vms": 80}
    tmp = "/tmp/_qe_bad.json"
    json.dump(bad, open(tmp, "w"))
    rc = main(["--input", tmp, "--out-dir", "/tmp/_qe_bad_out"])
    assert rc == 2, "缺 business_systems 应 rc=2，实际 %s" % rc
    print("SELFTEST 6 PASS 缺核心资源 rc=2"); ok += 1
    # 7) 复杂度越界告警
    bad2 = dict(base); bad2["complexity"] = {"technical_complexity": 9}
    w = validate(bad2)
    assert any("越界" in x for x in w), "复杂度越界应告警，实际 %s" % w
    print("SELFTEST 7 PASS 复杂度越界告警"); ok += 1
    print("SELFTEST PASS（%d/%d）" % (ok, 7))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="mig-quick-estimate driver（第 1 次调研粗估）")
    ap.add_argument("--input", help="输入 JSON 路径")
    ap.add_argument("--out-dir", default="./out", help="输出目录")
    ap.add_argument("--self-test", action="store_true", help="内置自检")
    a = ap.parse_args(argv)

    if a.self_test:
        return self_test()
    if not a.input:
        return rc2("缺少 --input（或用 --self-test）")

    try:
        cfg = json.load(open(a.input, encoding="utf-8"))
    except Exception as e:  # catch 必须说明为什么：输入不可读时终止而非猜数
        return rc2("输入 JSON 读取失败（%s），终止以避免基于错误数据估算" % e)

    for k in ("project", "source_cloud", "target_cloud"):
        if not cfg.get(k):
            return rc2("必填 %s 缺失" % k)

    warns = validate(cfg)
    if warns and any("无法估算" in w or "缺失（权重" in w for w in warns):
        return rc2("；".join(warns))

    r = calc(cfg)
    r["warnings"] = warns
    r["conclusion"] = "初估可用" if not warns else "初估可用（有 %d 条待确认）" % len(warns)
    r["suggested_action"] = "补资源表与复杂度事实 → mig-app-effort 第 2 次深化 → pcs-quotation 对外报价"
    r["escalation_reason"] = None

    os.makedirs(a.out_dir, exist_ok=True)
    md = render_md(r, warns)
    open(os.path.join(a.out_dir, "快速估算.md"), "w", encoding="utf-8").write(md)
    json.dump(r, open(os.path.join(a.out_dir, "quick_estimate.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

    print("项目：%s（%s → %s）" % (r["project"], r["source_cloud"], r["target_cloud"]))
    print("资源因子=%.2f 平均复杂度=%.2f" % (r["resource_factor"], r["avg_complexity"]))
    print("总人天=%d 周期=%d 周" % (r["man_days"], r["duration_weeks"]))
    print("成本区间（内部参考）：%s ~ %s 元" %
          (format(r["money"]["成本_低"], ","), format(r["money"]["成本_高"], ",")))
    print("告警 %d 条；产物 -> %s" % (len(warns), a.out_dir))
    return 0


if __name__ == "__main__":
    sys.exit(main())
