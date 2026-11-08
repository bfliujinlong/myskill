#!/usr/bin/env python3
# Plan B 轻量本体运行时：对象存储 + 受控动作 + 人类在环 + 审计 lineage
# 零依赖（仅标准库）。单次任务 = 一个临时 reasoning subject，不常驻。
import json, time, hashlib, uuid, os
from pathlib import Path

ROOT = Path(__file__).parent
# 运行时数据落在专用目录（与 skill 代码分离，避免把 demo 数据塞进 skill 本身）
STORE = Path.home() / ".hermes" / "planb-ontology" / "store"
STORE.mkdir(parents=True, exist_ok=True)
GRAPH = STORE / "objects.jsonl"      # 对象实例（含边）
AUDIT = STORE / "audit.jsonl"         # 全链路 lineage

def _ts(): return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())

def _log_audit(subject, action, target_type, target_id, decision, detail=""):
    rec = {
        "ts": _ts(), "subject": subject, "action": action,
        "target_type": target_type, "target_id": target_id,
        "decision": decision, "detail": detail,
        "hash": hashlib.sha256(f"{_ts()}{subject}{action}{target_id}".encode()).hexdigest()[:12],
    }
    with open(AUDIT, "a") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return rec

def save_object(obj):
    obj.setdefault("id", obj["type"][0].lower() + "-" + uuid.uuid4().hex[:6])
    obj["_created"] = _ts()
    with open(GRAPH, "a") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")
    return obj["id"]

def get_objects(otype=None):
    out = []
    if GRAPH.exists():
        for line in GRAPH.read_text(encoding="utf-8").splitlines():
            if line.strip():
                o = json.loads(line)
                if otype is None or o["type"] == otype:
                    out.append(o)
    return out

def update_state(oid, new_state, by):
    objs = get_objects()
    for o in objs:
        if o["id"] == oid:
            o["state"] = new_state
            o["_approved_by"] = by
    with open(GRAPH, "w") as f:
        for o in objs:
            f.write(json.dumps(o, ensure_ascii=False) + "\n")

# ── 受控动作执行器（核心是 human_approval 闸门）─────────
class OntologyEngine:
    def __init__(self):
        self.spec = self._load_spec()
        self.subject = None  # 临时 reasoning subject

    def _load_spec(self):
        # 优先读随 skill 一起的 ontology.yaml（单一事实源随身走）
        local_yaml = ROOT / "ontology.yaml"
        try:
            import yaml
            if local_yaml.exists():
                return yaml.safe_load(local_yaml.read_text())
        except Exception:
            pass
        return self._fallback_spec()

    @staticmethod
    def _fallback_spec():
        return {
            "actions": {
                "GenerateQuote":   {"human_approval": "required", "rollback": True},
                "GenerateSOW":     {"human_approval": "required", "rollback": True},
                "DraftCutoverPlan":{"human_approval": "required", "rollback": True},
                "RecordRisk":      {"human_approval": "none",    "rollback": False},
                "Approve":         {"human_approval": "none",    "rollback": True},
            }
        }

    def spawn_subject(self, task):
        """任务来了才造 subject，不常驻。"""
        self.subject = f"rs-{uuid.uuid4().hex[:6]}"
        _log_audit(self.subject, "SPAWN", "Subject", self.subject, "ok", f"task={task}")
        return self.subject

    def propose(self, action_name, payload):
        """Agent 只能提议 Action，不直接落盘。"""
        if self.subject is None:
            raise RuntimeError("no subject; call spawn_subject first")
        rid = save_object({**payload, "type": payload["type"], "state": "draft",
                           "_proposed_by": self.subject})
        ap = self.spec["actions"][action_name] if self.spec else None
        need = ap["human_approval"] == "required" if ap else True
        _log_audit(self.subject, f"PROPOSE:{action_name}", payload["type"], rid,
                   "pending_human" if need else "auto", json.dumps(payload, ensure_ascii=False)[:200])
        return {"object_id": rid, "needs_approval": need,
                "message": "已起草，待人类审批" if need else "已自动落盘（无需人批）"}

    def approve(self, oid, by_user="jinlongliu"):
        """人类把关：只有 Approve 动作代表审批，写回才生效。"""
        o = next((x for x in get_objects() if x["id"] == oid), None)
        if not o:
            return {"ok": False, "msg": "对象不存在"}
        update_state(oid, "approved", by_user)
        _log_audit(by_user, "APPROVE", o["type"], oid, "ok", "人类审批通过")
        return {"ok": True, "object_id": oid, "state": "approved"}

    def reject(self, oid, by_user="jinlongliu", reason=""):
        update_state(oid, "rejected", by_user)
        _log_audit(by_user, "REJECT", oid.split("-")[0], oid, "ok", reason)
        return {"ok": True, "object_id": oid, "state": "rejected"}

    def audit_trail(self, oid=None):
        rows = [json.loads(l) for l in AUDIT.read_text().splitlines() if l.strip()]
        if oid:
            rows = [r for r in rows if r["target_id"] == oid]
        return rows

    def show(self):
        """对象视图：agent 推理时读对象而非 skill 列表。"""
        objs = get_objects()
        print(f"\n=== 本体对象清单 ({len(objs)} 个) ===")
        for o in objs:
            edges = {k: v for k, v in o.items() if k.endswith("_id") or k in ("belongs_to","generated_from")}
            print(f"[{o['type']}] {o['id']} state={o.get('state','-')} edges={edges}")
        print("✅ 对象视图就绪（agent 读这个，不读 skill 列表）")


if __name__ == "__main__":
    print("Plan B Ontology Engine — 直接 python3 actions.py 仅做自测")
    eng = OntologyEngine()
    eng.spawn_subject("test")
    r = eng.propose("RecordRisk", {"type":"Risk","proj_id":"QY-DubaiFintech",
                                    "level":"high","desc":"RTO 未确认"})
    print("propose:", r)
    print("audit:", eng.audit_trail())
