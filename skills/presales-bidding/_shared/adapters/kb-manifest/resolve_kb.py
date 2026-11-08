#!/usr/bin/env python3
"""KB manifest resolver — 插件侧唯一入口（rc.7 建议）。

消费（consume）与发现（discover）严格分离：
  consume  — 只走注册语义键，BLOCK 未注册键。绝不扫描、绝不猜、绝不用内置快照兜底。
  discover — 只读扫描 manifest，产出「新素材待注册报告」供人决策与 RC 迭代，不绑定、不消费。

为什么 discover 不自动消费：
  新类型素材缺消费语义（哪个 Skill/什么纪律/什么优先级），自动读取 =
  无纪律上下文的静默绑定（如 SLA 承诺库流入新标书）。
  逃生门（产品决策 2026-09-07：入口全开）：用户显式指定路径的素材今天就能用
  （各 Skill 的显式输入通道），无路径级限制、无数量配额——推广期以"好用"为第一目标，
  把关放在出口（外发前的脱敏门禁，见 KB GOVERNANCE），不放在读取入口。
  由人断言语义，跑顺后在下一 RC 固化为语义键。
"""
from __future__ import annotations
import argparse, json, sys, os
from pathlib import Path
try:
    import yaml
except ImportError:
    sys.exit("BLOCKED: PyYAML 不可用（受限环境可换 json 版 manifest）")

MANIFEST_NAME = "STRUCTURE.yaml"
# 语义键注册表：插件声明"会用什么"（REQUIRED = 缺失即 BLOCK 的核心键）
REGISTRY = {
    "case_index":             "04-脱敏案例库 唯一检索入口（service-solution / technical-proposal 佐证）",
    "service_catalog_master": "服务目录母版（service-solution 优先级1）",
    "sla_master":             "SLA-SLO 母版（service-solution/引用纪律）",
    "sow_libraries":          "SOW四库（sow-support 步骤0.7）",
    "bidding_narrative":      "应标叙事引导表（service-solution 步骤0.6 应标策略）",
    # --- v2 对外方案层素材键（technical-proposal 步骤0.5 显式注入）---
    "company_intro":          "公司介绍+资质清单（technical-proposal 01章 / rfp-analyze 资质匹配）",
    "bid_chapters":           "服务型投标章节素材（technical-proposal 分段生成参考）",
    "architecture_images":    "部署/服务架构图（technical-proposal 图示层）",
    "tender_templates":       "招标模板库（rfp-analyze 结构对位）",
}
# CORE = 缺失即核心告警的键（每个服务型项目都应有）；
# OPTIONAL = 按交付物触发的键，缺失只标"待补充"不阻断。
CORE = ("case_index", "service_catalog_master", "sla_master")
OPTIONAL = ("sow_libraries", "bidding_narrative", "company_intro",
            "bid_chapters", "architecture_images", "tender_templates")
REQUIRED = CORE  # 仅 CORE 计入 missing_keys 的 WARN；OPTIONAL 单独提示
SUPPORTED_CONTRACT = 2

def load_manifest(kb_root: str):
    root = Path(kb_root)
    anchor = root / MANIFEST_NAME
    if not anchor.is_file():
        return None, ("BLOCK", f"BLOCKED: KB 根缺少锚点文件 {MANIFEST_NAME}（加载契约未声明）。"
                     "插件不扫描、不猜路径、不用内置快照兜底。请 KB 侧提供 manifest。")
    m = yaml.safe_load(anchor.read_text(encoding="utf-8"))
    cv = m.get("contract_version")
    if cv != SUPPORTED_CONTRACT:
        return m, ("WARN", f"契约代数不匹配：插件支持 v{SUPPORTED_CONTRACT}，KB 声明 v{cv}；按 manifest 继续解析。")
    return m, None

def diagnostic_candidates(root: Path, missing_rel: str) -> list[str]:
    """路径失效时的诊断候选（只给人看，不自动绑定）。按 basename 在 KB 内做只读模糊定位。"""
    base = Path(missing_rel).name
    stem = base.split("-v0")[0].rsplit(".", 1)[0]
    hits = []
    for dirpath, _dirs, files in os.walk(root):
        for f in files:
            if stem[:6] in f and f.endswith((".md", ".yaml")):
                hits.append(str(Path(dirpath, f).relative_to(root)))
        if len(hits) >= 3:
            break
    return hits[:3]

def consume(kb_root: str, key: str | None) -> dict:
    m, err = load_manifest(kb_root)
    if err: return {"level": err[0], "message": err[1]}
    root = Path(kb_root)
    zones, assets = m.get("zones", {}), m.get("assets", {})
    if key:
        if key in zones:
            z = zones[key]; p = root / z["path"]
            return {"level": "OK" if p.exists() else "WARN", "key": key, "path": str(p),
                    "access": z.get("access"), "exists": p.exists()}
        if key in assets:
            if key not in REGISTRY:   # manifest 有但插件注册表没有 → 同样是未注册键，不消费
                return {"level": "BLOCK", "message": f"BLOCKED: 语义键 '{key}' 在 KB manifest 中存在，但不在本插件 RC 注册表内（未注册消费语义）。"
                        f"不消费：① 用户显式指定路径注入本次会话；② --discover 已将其列入新素材报告，纳入下一 RC。"}
            p = root / assets[key]
            r = {"level": "OK" if p.exists() else "WARN", "key": key, "path": str(p), "exists": p.exists()}
            if not p.exists():
                r["diagnostic_candidates"] = diagnostic_candidates(root, assets[key])  # 仅诊断，供人修 manifest
                r["message"] = "WARN: manifest 声明的路径不存在（KB 改名/迁移后未同步 manifest？）。候选仅作诊断，不自动绑定。"
            return r
        return {"level": "BLOCK", "message": f"BLOCKED: 未注册的语义键 '{key}'。"
                f"该素材不在本插件 RC 的注册表内，不做扫描读取（防无纪律消费）。"
                f"可用路径：① 用户显式指定路径注入本次会话；② 跑 --discover 生成新素材报告，纳入下一 RC。"}
    report = {"zones": [], "assets": [], "missing_keys": [], "missing_optional": []}
    for k, z in zones.items():
        p = root / z["path"]
        report["zones"].append({"key": k, "path": z["path"], "access": z.get("access"), "exists": p.exists()})
    for k in REGISTRY:
        rel = assets.get(k)
        if not rel:
            # CORE 缺失 → WARN；OPTIONAL 缺失 → 仅提示（按交付物触发，未做该交付物属正常）
            (report["missing_keys"] if k in CORE else report["missing_optional"]).append(k)
            continue
        e = (root / rel).exists()
        entry = {"key": k, "path": rel, "exists": e, "tier": "core" if k in CORE else "optional"}
        if not e: entry["diagnostic_candidates"] = diagnostic_candidates(root, rel)
        report["assets"].append(entry)
    report["level"] = "OK" if not report["missing_keys"] else "WARN"
    return report

def discover(kb_root: str) -> dict:
    """只读发现：manifest 里插件注册表没有的素材 → 报告，不消费。"""
    m, err = load_manifest(kb_root)
    if err: return {"level": err[0], "message": err[1]}
    root = Path(kb_root)
    zones, assets = m.get("zones", {}), m.get("assets", {})
    new_assets = [{"key": k, "path": rel, "exists": (root / rel).exists(),
                   "note": "新素材类型：本 RC 注册表无此键，未消费"}
                  for k, rel in assets.items() if k not in REGISTRY]
    broken = [{"key": k, "path": rel, "exists": False}
              for k, rel in assets.items() if k in REGISTRY and not (root / rel).exists()]
    optional_unmapped = [k for k in OPTIONAL if k not in assets]
    unregistered_zones = [{"key": k, "path": z["path"], "access": z.get("access")}
                          for k, z in zones.items() if k not in
                          ("system_docs", "templates", "offerings", "bidding", "cases",
                           "faq", "restricted", "credentials")]
    return {
        "level": "OK",
        "mode": "discover",
        "registered_ok": [k for k in REGISTRY if k in assets and (root / assets[k]).exists()],
        "new_assets": new_assets,          # → 提醒：建议下一 RC 注册
        "broken": broken,                  # → 提醒：KB 侧修 manifest
        "new_zones": unregistered_zones,
        "optional_unmapped": optional_unmapped,   # OPTIONAL 键 KB 侧尚未提供路径（按需交付物，非漂移）
        "proposal": ("以下键建议加入下一 RC 注册表（dev 机械施工）：" +
                     "; ".join(f"{a['key']} → {a['path']}" for a in new_assets)) if new_assets
                    else "无新增，注册表与 KB manifest 一致",
        "escape_hatch": "新素材在 RC 注册前可由用户显式指定路径注入（各 Skill 显式输入通道），语义由人断言",
    }

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--kb-root", required=True)
    ap.add_argument("--key", default=None)
    ap.add_argument("--discover", action="store_true")
    a = ap.parse_args()
    r = discover(a.kb_root) if a.discover else consume(a.kb_root, a.key)
    print(json.dumps(r, ensure_ascii=False, indent=2))
    sys.exit({"OK": 0, "WARN": 0, "BLOCK": 3}.get(r.get("level"), 1))
