#!/usr/bin/env python3
# Plan B 端到端可落地性验证 + 可复用入口
# 用法:
#   python3 demo_e2e.py                              # 内置 QY-DubaiFintech 示例跑全链路
#   python3 demo_e2e.py --proj X --scope "76 EC2" --total 385000
#   python3 demo_e2e.py --reset                      # 清空 store 重跑
import sys, os, argparse, pathlib
sys.path.insert(0, os.path.dirname(__file__))
from actions import OntologyEngine, save_object

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--proj", default="QY-DubaiFintech")
    ap.add_argument("--scope", default="76 EC2/27 DB/45 Redis/51TB/5源区")
    ap.add_argument("--total", type=int, default=385000)
    ap.add_argument("--reset", action="store_true")
    args = ap.parse_args()

    store = pathlib.Path.home()/".hermes"/"planb-ontology"/"store"
    if args.reset:
        for f in ("objects.jsonl","audit.jsonl"):
            (store/f).unlink(missing_ok=True)
        print("✅ store 已清空")

    eng = OntologyEngine()
    print("── STEP 0 临时 reasoning subject ──")
    rs = eng.spawn_subject(f"出 {args.proj} 报价+SOW")
    print("subject =", rs)

    print("\n── STEP 1 对象：SalesOpp → MigrationProject ──")
    opp_id = save_object({"type":"SalesOpp","opp_id":"OPP-QY","customer":"xx fintech",
                          "region":"Dubai","source_cloud":"AWS",
                          "target_cloud":"Aliyun me-east-1","state":"won"})
    proj_id = save_object({"type":"MigrationProject","proj_id":args.proj,
                           "name":f"{args.proj} 云迁移","belongs_to":opp_id,
                           "scope":args.scope,"target_arch":"2AZ 双活","state":"active"})
    print("opp_id =", opp_id, "| proj_id =", proj_id)

    print("\n── STEP 2 受控动作 GenerateQuote（需人批）──")
    q = eng.propose("GenerateQuote",
                    {"type":"Quote","proj_id":proj_id,"total_usd":args.total,
                     "lines":[{"role":"迁移架构师","days":120,"rate":350,"sub":42000},
                              {"role":"交付工程师","days":480,"rate":350,"sub":168000},
                              {"role":"PM","days":160,"rate":350,"sub":56000}],
                     "version":"v0.1-基线","state":"draft"})
    print("quote drafted:", q)
    assert q["needs_approval"] is True
    print("⚠️ 闸门生效：agent 无法直接落盘报价")

    print("\n── STEP 3 人类在环：审批通过 ──")
    ap2 = eng.approve(q["object_id"], by_user="jinlongliu")
    print("approve:", ap2); assert ap2["ok"]

    print("\n── STEP 4 受控动作 GenerateSOW（再人批）──")
    s = eng.propose("GenerateSOW",
                    {"type":"SOW","proj_id":proj_id,"generated_from":q["object_id"],
                     "chapters":["范围","WBS","SLA","割接","验收","商务"]*2+["待确认"],
                     "version":"v0.1","state":"draft"})
    print("sow drafted:", s)
    eng.approve(s["object_id"], by_user="jinlongliu")

    print("\n── STEP 5 受控动作 RecordRisk（免批）──")
    r = eng.propose("RecordRisk",
                    {"type":"Risk","proj_id":proj_id,"level":"high",
                     "desc":"RTO/RPO 客户未确认；停机窗口待定","mitigation":"首轮调研补确认"})
    print("risk:", r); assert r["needs_approval"] is False

    print("\n── STEP 6 对象视图 ──")
    eng.show()

    print("\n── STEP 7 审计 lineage ──")
    for t in eng.audit_trail():
        print(f"  {t['ts']} | {t['subject']:>10} | {t['action']:<22} | {t['target_type']:<17} | {t['decision']} | {t['hash']}")

    from actions import get_objects
    quotes=[o for o in get_objects("Quote") if o["state"]=="approved"]
    sows=[o for o in get_objects("SOW") if o["state"]=="approved"]
    print(f"\n✅ 已批报价 {len(quotes)} / 已批SOW {len(sows)} / 风险 {len(get_objects('Risk'))}")
    print("✅ Plan B 最小化本体：零依赖、零费用、可跑通 起草→人批→落盘→审计")

if __name__ == "__main__":
    main()
