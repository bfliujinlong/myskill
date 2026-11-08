#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 应用级迁移工作量估算 driver：四维度评分 -> L1-L5 等级 -> 基准人天 -> 修正系数 -> 阶段拆分 -> 角色人天 -> 金额
# 纪律：缺必填 -> rc=2 并说明原因（不猜数）；不虚构人员/案例；单价缺失则只出人天不出金额
# 依赖：openpyxl（缺失时降级为 md/json，并显式说明，不静默）
"""mig-app-effort driver.

输入 JSON：
{
  "project": "客户名-项目名",
  "source_cloud": "aws", "target_cloud": "alicloud",
  "apps": [
    {"id":"A01","name":"订单系统","team":"团队1",
     "d1":3,"d2":4,"d3":2,"d4":2,
     "d1_note":"...","d2_note":"...","d3_note":"...","d4_note":"...",
     "factors":{"automation":false,"doc_missing":true,"bandwidth":false,"compliance":false},
     "other_factor":null}
  ],
  "price_mode": "cost",           # cost=成本价 / list=刊例价；省略则不折金额
  "out_dir": "./out"
}
输出：应用工作量评估.md / 应用工作量评估.xlsx / app_effort.json
"""
from __future__ import annotations

import argparse, json, os, sys
from datetime import date

TBD = "待确认"

# ---------------- 基准常量（与 references/baseline-params.md 同源，改动该文件=改报价口径） ----------------
LEVELS = [  # (等级, 下限含, 上限不含, 基准人天低, 基准人天高)
    ("L1-简单型",   1.0, 1.8,  5,  7),
    ("L2-普通型",   1.8, 2.6,  7, 12),
    ("L3-中等型",   2.6, 3.4, 15, 25),
    ("L4-复杂型",   3.4, 4.2, 30, 50),
    ("L5-极高难度", 4.2, 6.01, 60, 90),
]

# 交付阶段权重（合计 1.0），与 LZ/迁移服务目录口径一致
PHASES = [
    ("调研与方案设计", 0.20),
    ("环境准备与迁移实施", 0.30),
    ("应用适配与调试", 0.30),
    ("验收与割接", 0.20),
]

# 修正系数（连乘）
FACTORS = {
    "automation":  ("使用自动化迁移工具", 0.8),
    "doc_missing": ("文档/源码缺失", 1.5),
    "bandwidth":   ("网络/带宽限制", 1.2),
    "compliance":  ("合规/安全额外要求", 1.3),
}

# 角色单价：(岗位, 占比, 成本价, 刊例价)；占比合计 1.0
ROLES = [
    ("项目经理 PM",            0.1329, 3300, 4200),
    ("云架构师 Architecture",  0.2601, 3300, 4200),
    ("云工程师 Cloud Engineer", 0.5256, 1900, 2500),
    ("DBA",                    0.0814, 2500, 3300),
]


def die(msg: str) -> "None":
    """拒绝产出并说明原因（不吞异常）。"""
    sys.stderr.write("BLOCKED: %s\n" % msg)
    sys.exit(2)


def level_of(avg: float):
    for name, lo, hi, mdlo, mdhi in LEVELS:
        if lo <= avg < hi:
            return name, mdlo, mdhi
    return LEVELS[-1][0], LEVELS[-1][3], LEVELS[-1][4]


def score_app(a: dict, idx: int) -> dict:
    """单应用评分 -> 等级 -> 基准人天 -> 修正 -> 阶段拆分。"""
    missing = []
    for k in ("id", "name"):
        if not a.get(k):
            missing.append(k)
    for d in ("d1", "d2", "d3", "d4"):
        v = a.get(d)
        if v is None:
            missing.append(d)
        elif not (isinstance(v, (int, float)) and 1 <= v <= 5):
            die("应用[%s] 的 %s 必须是 1-5 的数字，当前=%r（四维度评分不得越界）" % (a.get("id", idx), d, v))
    if missing:
        die("应用[%s] 缺必填字段：%s（不猜数、不补默认值）" % (a.get("id", idx), ", ".join(missing)))

    # 评分依据：允许留空，但留空必须标 TBD 而非静默 0 分
    notes = {d: (a.get(d + "_note") or TBD) for d in ("d1", "d2", "d3", "d4")}
    scores = {d: float(a[d]) for d in ("d1", "d2", "d3", "d4")}
    total = sum(scores.values())
    avg = round(total / 4.0, 4)
    lvl, md_lo, md_hi = level_of(avg)

    fac = dict(a.get("factors") or {})
    applied, coeffs = [], []
    for key, (label, coef) in FACTORS.items():
        if fac.get(key):
            applied.append(label)
            coeffs.append(coef)
    other = a.get("other_factor")
    if other is not None:
        ov = float(other)
        if ov <= 0:
            die("应用[%s] other_factor 必须 > 0，当前=%r" % (a["id"], other))
        reason = (a.get("other_factor_reason") or "").strip()
        if not reason:
            die("应用[%s] 填了 other_factor 但缺 other_factor_reason（自定义系数必须写理由）" % a["id"])
        applied.append("其他：%s" % reason)
        coeffs.append(ov)

    prod = 1.0
    for c in coeffs:
        prod *= c
    prod = round(prod, 4)

    adj_lo = round(md_lo * prod, 2)
    adj_hi = round(md_hi * prod, 2)

    phases = []
    for pname, w in PHASES:
        phases.append({"阶段": pname, "权重": w,
                       "人天_低": round(adj_lo * w, 2), "人天_高": round(adj_hi * w, 2)})

    return {
        "id": a["id"], "name": a["name"], "团队": a.get("team") or TBD,
        "scores": scores, "notes": notes,
        "总分": int(total), "平均分": avg, "等级": lvl,
        "基准人天_低": md_lo, "基准人天_高": md_hi,
        "修正项": applied, "总修正系数": prod,
        "调整后人天_低": adj_lo, "调整后人天_高": adj_hi,
        "阶段拆分": phases, "备注": a.get("remark") or "",
    }


def aggregate(apps: list) -> dict:
    """按团队汇总 + 全体合计。"""
    by_team = {}
    for r in apps:
        t = r["团队"]
        b = by_team.setdefault(t, {"团队": t, "应用数量": 0, "人天_低": 0.0, "人天_高": 0.0,
                                   "阶段": {p: [0.0, 0.0] for p, _ in PHASES}})
        b["应用数量"] += 1
        b["人天_低"] += r["调整后人天_低"]
        b["人天_高"] += r["调整后人天_高"]
        for p in r["阶段拆分"]:
            b["阶段"][p["阶段"]][0] += p["人天_低"]
            b["阶段"][p["阶段"]][1] += p["人天_高"]
    for b in by_team.values():
        b["人天_低"] = round(b["人天_低"], 2)
        b["人天_高"] = round(b["人天_高"], 2)
        for k, v in b["阶段"].items():
            b["阶段"][k] = [round(v[0], 2), round(v[1], 2)]
    tot_lo = round(sum(r["调整后人天_低"] for r in apps), 2)
    tot_hi = round(sum(r["调整后人天_高"] for r in apps), 2)
    return {"按团队": sorted(by_team.values(), key=lambda x: x["团队"]),
            "合计": {"应用数量": len(apps), "人天_低": tot_lo, "人天_高": tot_hi,
                   "人天_中": round((tot_lo + tot_hi) / 2, 2),
                   "阶段": {p: [round(sum(rp["人天_低"] for rp in r["阶段拆分"] if rp["阶段"] == p), 2),
                                round(sum(rp["人天_高"] for rp in r["阶段拆分"] if rp["阶段"] == p), 2)]
                            for p, _ in PHASES}}}


def to_money(agg: dict, price_mode: str):
    """人天 -> 角色人天 -> 金额。price_mode 缺失/非法则只出人天。"""
    if price_mode not in ("cost", "list"):
        return None
    pi = 2 if price_mode == "cost" else 3
    tot_lo, tot_hi = agg["合计"]["人天_低"], agg["合计"]["人天_高"]
    roles = []
    for name, ratio, cost, lst in ROLES:
        rate = cost if price_mode == "cost" else lst
        roles.append({"岗位": name, "占比": ratio, "单价": rate,
                      "人天_低": round(tot_lo * ratio, 2), "人天_高": round(tot_hi * ratio, 2),
                      "金额_低": round(tot_lo * ratio * rate, 2),
                      "金额_高": round(tot_hi * ratio * rate, 2)})
    return {"价格口径": "成本价" if price_mode == "cost" else "刊例价",
            "角色": roles,
            "金额_低": round(sum(r["金额_低"] for r in roles), 2),
            "金额_高": round(sum(r["金额_高"] for r in roles), 2)}


def render_md(cfg, apps, agg, money, warnings) -> str:
    L = []
    L.append("# 应用迁移工作量评估 — %s" % cfg.get("project", TBD))
    L.append("")
    L.append("| 项 | 值 |")
    L.append("|---|---|")
    L.append("| 源云 | %s |" % cfg.get("source_cloud", TBD))
    L.append("| 目标云 | %s |" % cfg.get("target_cloud", TBD))
    L.append("| 应用数量 | %d |" % len(apps))
    L.append("| 生成日期 | %s |" % date.today().isoformat())
    L.append("| 价格口径 | %s |" % (money["价格口径"] if money else "未折金额（未提供 price_mode）"))
    L.append("")
    L.append("> 口径：四维度（架构/数据/耦合/改造深度）1-5 分 → 平均分 → L1-L5 等级 → 基准人天 → 修正系数连乘 → 阶段拆分。")
    L.append("> 红线：本表只给**工作量**，金额由 `pcs-quotation` 出；未核实项一律「待确认」。")
    L.append("")
    L.append("## 一、逐应用明细")
    L.append("")
    L.append("| 应用ID | 应用名称 | D1架构 | D2数据 | D3耦合 | D4改造 | 平均分 | 等级 | 修正系数 | 人天(低) | 人天(高) | 团队 |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in apps:
        L.append("| %s | %s | %g | %g | %g | %g | %.2f | %s | %g | %.2f | %.2f | %s |" % (
            r["id"], r["name"], r["scores"]["d1"], r["scores"]["d2"],
            r["scores"]["d3"], r["scores"]["d4"], r["平均分"], r["等级"],
            r["总修正系数"], r["调整后人天_低"], r["调整后人天_高"], r["团队"]))
    L.append("")
    L.append("### 评分依据（不得只给分不给依据）")
    L.append("")
    for r in apps:
        L.append("- **%s %s**：D1=%g（%s）；D2=%g（%s）；D3=%g（%s）；D4=%g（%s）" % (
            r["id"], r["name"], r["scores"]["d1"], r["notes"]["d1"],
            r["scores"]["d2"], r["notes"]["d2"],
            r["scores"]["d3"], r["notes"]["d3"],
            r["scores"]["d4"], r["notes"]["d4"]))
        if r["修正项"]:
            L.append("  - 修正：%s → 系数 %g" % ("、".join(r["修正项"]), r["总修正系数"]))
    L.append("")
    L.append("## 二、团队汇总")
    L.append("")
    L.append("| 团队 | 应用数量 | 人天(低) | 人天(高) |")
    L.append("|---|---|---|---|")
    for b in agg["按团队"]:
        L.append("| %s | %d | %.2f | %.2f |" % (b["团队"], b["应用数量"], b["人天_低"], b["人天_高"]))
    c = agg["合计"]
    L.append("| **合计** | **%d** | **%.2f** | **%.2f** |" % (c["应用数量"], c["人天_低"], c["人天_高"]))
    L.append("")
    L.append("## 三、阶段拆分（合计）")
    L.append("")
    L.append("| 阶段 | 权重 | 人天(低) | 人天(高) |")
    L.append("|---|---|---|---|")
    for p, w in PHASES:
        v = c["阶段"][p]
        L.append("| %s | %g | %.2f | %.2f |" % (p, w, v[0], v[1]))
    L.append("")
    if money:
        L.append("## 四、角色与金额")
        L.append("")
        L.append("| 岗位 | 占比 | 单价 | 人天(低) | 人天(高) | 金额(低) | 金额(高) |")
        L.append("|---|---|---|---|---|---|---|")
        for r in money["角色"]:
            L.append("| %s | %g | %d | %.2f | %.2f | %.2f | %.2f |" % (
                r["岗位"], r["占比"], r["单价"], r["人天_低"], r["人天_高"], r["金额_低"], r["金额_高"]))
        L.append("")
        L.append("**合计：¥%s ~ ¥%s（%s，不含税）**" % (
            format(money["金额_低"], ","), format(money["金额_高"], ","), money["价格口径"]))
        L.append("")
    if warnings:
        L.append("## 五、待确认 / 升级项")
        L.append("")
        for w in warnings:
            L.append("- %s" % w)
        L.append("")
    return "\n".join(L)


def build_xlsx(path, apps, agg, money):
    try:
        import openpyxl
        from openpyxl.styles import Font, Alignment
    except ImportError:
        return None  # 调用方会显式说明降级，不静默
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "应用评估"
    hdr = ["应用ID", "应用名称", "D1架构", "D2数据", "D3耦合", "D4改造", "总分", "平均分", "等级",
           "基准人天_低", "基准人天_高", "总修正系数", "修正项", "调整后人天_低", "调整后人天_高", "团队", "备注"]
    for ph, _ in PHASES:
        hdr += [ph + "(低)", ph + "(高)"]
    ws.append(hdr)
    for c in ws[1]:
        c.font = Font(bold=True)
        c.alignment = Alignment(horizontal="center")
    for r in apps:
        row = [r["id"], r["name"], r["scores"]["d1"], r["scores"]["d2"],
               r["scores"]["d3"], r["scores"]["d4"], r["总分"], r["平均分"], r["等级"],
               r["基准人天_低"], r["基准人天_高"], r["总修正系数"], "、".join(r["修正项"]),
               r["调整后人天_低"], r["调整后人天_高"], r["团队"], r["备注"]]
        for ph, _ in PHASES:
            v = next((x for x in r["阶段拆分"] if x["阶段"] == ph), None)
            row += [v["人天_低"] if v else 0, v["人天_高"] if v else 0]
        ws.append(row)

    wt = wb.create_sheet("团队汇总")
    wt.append(["团队", "应用数量"] + [x for ph, _ in PHASES for x in [ph + "(低)", ph + "(高)"]] + ["人天_低", "人天_高"])
    for c in wt[1]:
        c.font = Font(bold=True)
    for b in agg["按团队"]:
        row = [b["团队"], b["应用数量"]]
        for ph, _ in PHASES:
            row += b["阶段"][ph]
        row += [b["人天_低"], b["人天_高"]]
        wt.append(row)
    c = agg["合计"]
    row = ["合计", c["应用数量"]]
    for ph, _ in PHASES:
        row += c["阶段"][ph]
    row += [c["人天_低"], c["人天_高"]]
    wt.append(row)

    if money:
        wm = wb.create_sheet("角色与金额")
        wm.append(["岗位", "占比", "单价", "人天_低", "人天_高", "金额_低", "金额_高"])
        for cc in wm[1]:
            cc.font = Font(bold=True)
        for r in money["角色"]:
            wm.append([r["岗位"], r["占比"], r["单价"], r["人天_低"], r["人天_高"], r["金额_低"], r["金额_高"]])
        wm.append(["合计", "", "", "", "", money["金额_低"], money["金额_高"]])
    wb.save(path)
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input")
    ap.add_argument("--out-dir", default="./out")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()

    if a.self_test:
        return self_test()

    if not a.input:
        die("缺 --input（或改用 --self-test 跑内置自检）")
    if not os.path.exists(a.input):
        die("输入文件不存在: %s" % a.input)
    with open(a.input, encoding="utf-8") as f:
        cfg = json.load(f)
    if not cfg.get("apps"):
        die("apps 为空，无可测算内容（至少提供 1 个应用的四维度评分）")

    apps = [score_app(x, i) for i, x in enumerate(cfg["apps"], 1)]
    agg = aggregate(apps)
    money = to_money(agg, cfg.get("price_mode"))

    warnings = []
    no_note = []
    for r in apps:
        miss_d = [d.upper() for d in ("d1", "d2", "d3", "d4") if r["notes"][d] == TBD]
        if miss_d:
            no_note.append((r["id"], r["name"], miss_d))
    if no_note:
        # 聚合统计 + 只列前 10 条样例，避免 186 个应用刷屏淹没其他升级项
        warnings.append("缺评分依据：%d/%d 个应用只有分数没有事实依据（评审会被打回），样例：%s" % (
            len(no_note), len(apps),
            "；".join("%s %s 缺 %s" % (i, n, "/".join(m)) for i, n, m in no_note[:10])))
    if cfg.get("price_mode") not in ("cost", "list"):
        warnings.append("未提供 price_mode（cost/list），本次只出人天不出金额；金额口径唯一在 presales/pcs-quotation")

    os.makedirs(a.out_dir, exist_ok=True)
    md = render_md(cfg, apps, agg, money, warnings)
    p_md = os.path.join(a.out_dir, "应用工作量评估.md")
    with open(p_md, "w", encoding="utf-8") as f:
        f.write(md)

    p_x = os.path.join(a.out_dir, "应用工作量评估.xlsx")
    xok = build_xlsx(p_x, apps, agg, money)

    out = {"project": cfg.get("project"), "apps": apps, "aggregate": agg,
           "money": money, "warnings": warnings,
           "artifacts": [p_md] + ([p_x] if xok else [])}
    p_j = os.path.join(a.out_dir, "app_effort.json")
    with open(p_j, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print("合计人天 低 %.2f 中 %.2f 高 %.2f" % (agg["合计"]["人天_低"], agg["合计"]["人天_中"], agg["合计"]["人天_高"]))
    if money:
        print("金额(%s) ¥%s ~ ¥%s" % (money["价格口径"], format(money["金额_低"], ","), format(money["金额_高"], ",")))
    else:
        print("未折金额（price_mode 缺失）")
    if not xok:
        print("WARN: openpyxl 缺失，已降级为仅 md/json（未写 xlsx）")
    for w in warnings:
        print("TODO: %s" % (w if len(w) < 800 else w[:800] + " …（截断）"))
    print("CREATED: %s" % p_md)
    if xok:
        print("CREATED: %s" % p_x)
    print("CREATED: %s" % p_j)


def self_test():
    """内置自检：正向全链路 + 越界/缺字段错误路径，必须真跑。"""
    ok = True

    # 用例1：L1 简单应用，无修正
    r = score_app({"id": "A1", "name": "静态门户", "d1": 1, "d2": 1, "d3": 1, "d4": 1}, 0)
    assert r["平均分"] == 1.0 and r["等级"] == "L1-简单型", r
    assert r["调整后人天_低"] == 5 and r["调整后人天_高"] == 7, r
    print("SELFTEST 1 PASS L1无修正 -> 5~7 人天")

    # 用例2：L3 中等 + 文档缺失×1.5 + 合规×1.3
    r = score_app({"id": "A2", "name": "订单系统", "d1": 3, "d2": 4, "d3": 2, "d4": 2,
                   "factors": {"doc_missing": True, "compliance": True}}, 0)
    assert r["等级"] == "L3-中等型", r
    assert abs(r["总修正系数"] - 1.95) < 1e-6, r
    assert abs(r["调整后人天_低"] - 29.25) < 1e-6 and abs(r["调整后人天_高"] - 48.75) < 1e-6, r
    print("SELFTEST 2 PASS L3 ×1.95 -> 29.25~48.75 人天")

    # 用例3：L5 上界
    r = score_app({"id": "A3", "name": "核心账务", "d1": 5, "d2": 5, "d3": 5, "d4": 5}, 0)
    assert r["等级"] == "L5-极高难度" and r["调整后人天_高"] == 90, r
    print("SELFTEST 3 PASS L5 -> 60~90 人天")

    # 用例4：阶段权重合计必须为 1.0（否则人天会被放大/缩小）
    assert abs(sum(w for _, w in PHASES) - 1.0) < 1e-9
    # 角色占比合计必须为 1.0
    assert abs(sum(x[1] for x in ROLES) - 1.0) < 1e-9
    print("SELFTEST 4 PASS 阶段权重/角色占比合计=1.0")

    # 用例5：错误路径——评分越界
    import subprocess
    tmp = "/tmp/_app_effort_neg.json"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({"project": "t", "apps": [{"id": "X", "name": "n", "d1": 9, "d2": 1, "d3": 1, "d4": 1}]}, f)
    p = subprocess.run([sys.executable, __file__, "--input", tmp, "--out-dir", "/tmp/_ae_neg"],
                       capture_output=True, text=True)
    assert p.returncode == 2 and "1-5" in p.stderr, (p.returncode, p.stderr)
    print("SELFTEST 5 PASS 评分越界 rc=2 且说明原因")

    # 用例6：错误路径——自定义系数缺理由
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({"project": "t", "apps": [{"id": "X", "name": "n", "d1": 1, "d2": 1, "d3": 1, "d4": 1,
                                             "other_factor": 1.2}]}, f)
    p = subprocess.run([sys.executable, __file__, "--input", tmp, "--out-dir", "/tmp/_ae_neg"],
                       capture_output=True, text=True)
    assert p.returncode == 2 and "other_factor_reason" in p.stderr, (p.returncode, p.stderr)
    print("SELFTEST 6 PASS 自定义系数缺理由 rc=2")

    print("SELFTEST PASS（6/6）")
    return ok


if __name__ == "__main__":
    main()
