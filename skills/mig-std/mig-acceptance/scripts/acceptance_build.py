#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 项目验收（阶段 05）driver：SOW 交付物清单 + 系统清单 -> UAT 用例清单 + 验收报告
# stdlib only，无外部依赖；不执行任何生产变更
"""mig-acceptance driver.

输入 JSON：
{
  "project": "客户名-项目名",
  "target_cloud": "alicloud",
  "deliverables": [{"id": "D-01", "name": "HLD 设计文档"}],
  "systems": [{"name": "订单系统", "domains": ["网络", "数据库"]}],
  "results": [{"case_id": "UAT-NET-01", "status": "pass", "note": ""}]
}
输出：uat_cases.md / acceptance_report.md / acceptance.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date

# 域顺序：与 learning/_shared/cloud_profiles/README.md 保持一致
DOMAIN_ORDER = ["网络", "安全", "IAM", "计算", "存储", "数据库", "大数据", "监控运维"]

# 每域的通用用例骨架（检查点），目标云产品名由 profile 注入，未取到则写「待确认」
DOMAIN_CHECKS = {
    "网络": ["VPC/子网划分与 CIDR 与设计方案一致", "跨地域/跨 VPC 互联连通性",
             "负载均衡后端健康检查全绿", "公网入口 DNS 解析指向新环境"],
    "安全": ["边界防护（WAF/抗DDoS）策略已生效", "主机/容器安全 agent 在线",
             "高危端口未对公网开放", "堡垒机可审计登录"],
    "IAM": ["账号/角色按最小权限分配", "特权账号有审批与审计记录",
            "密钥托管在 KMS，无明文凭据", "操作审计日志可回溯"],
    "计算": ["实例规格/数量与设计清单一致", "应用进程健康且自愈（重启后恢复）",
             "弹性伸缩策略按预期触发", "镜像/启动模板可复现"],
    "存储": ["对象存储桶权限与生命周期策略正确", "文件存储挂载点与权限正确",
             "数据校验（对象数/校验和）与源端一致"],
    "数据库": ["实例版本与参数与设计一致", "主从/高可用切换演练成功",
               "数据一致性校验（行数/校验和）通过", "备份与恢复演练成功"],
    "大数据": ["作业调度链路可正常触发", "数据产出时效满足 SLA",
               "表结构/分区与源端一致", "血缘与权限已重建"],
    "监控运维": ["监控指标采集完整（CPU/内存/磁盘/网络）", "告警规则与通知渠道生效",
                 "日志采集链路完整可检索", "审计日志已开启"],
}

# 域 -> ASCII 用例编号前缀（中文做编号会导致 results 回填匹配不上，必须固定 ASCII）
DOMAIN_CODE = {
    "网络": "NET", "安全": "SEC", "IAM": "IAM", "计算": "COM",
    "存储": "STO", "数据库": "DBA", "大数据": "BIG", "监控运维": "MON",
    "业务功能": "BIZ",
}

STATUS_LABEL = {"pass": "通过", "fail": "不通过", "blocked": "阻塞", "skip": "未执行"}


def load_input(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    # 明确校验：缺失即抛错说明原因（不吞异常）
    for key in ("project", "target_cloud", "deliverables", "systems"):
        if key not in data:
            raise ValueError("输入缺少必填字段 %s，无法建立交付物追溯，终止" % key)
    if not data["deliverables"]:
        raise ValueError("deliverables 为空：无 SOW 交付物清单则无法验收，终止并升级")
    return data


def build_cases(data: dict) -> list:
    """按域展开用例；只展开 systems 实际声明的域，未声明不生成（不编造）。"""
    deliverable_ids = {str(d.get("id", "")).strip() for d in data["deliverables"]}
    cases = []
    counters = {}
    for sysinfo in data["systems"]:
        sname = sysinfo.get("name", "未命名系统")
        for domain in sysinfo.get("domains", []):
            if domain not in DOMAIN_CHECKS:
                # 未知域：不静默丢弃，记为待确认
                cases.append({
                    "case_id": "UAT-UNK-%03d" % (len(cases) + 1),  # 未知域：落点待确认
                    "system": sname, "domain": domain,
                    "title": "%s-%s验收（域未在模板中，落点待确认）" % (sname, domain),
                    "precondition": "系统已部署至目标环境",
                    "steps": ["确认该域的验收口径（待确认）"],
                    "expected": "验收口径经客户确认后补充（待确认）",
                    "deliverable_ref": "待确认",
                })
                continue
            seq = counters.get(domain, 0) + 1
            counters[domain] = seq
            code = DOMAIN_CODE.get(domain, "UNK")
            cases.append({
                "case_id": "UAT-%s-%03d" % (code, seq),
                "system": sname,
                "domain": domain,
                "title": "%s %s域验收" % (sname, domain),
                "precondition": "系统已完成迁移部署，测试数据已就绪",
                "steps": DOMAIN_CHECKS[domain],
                "expected": "上述检查项全部通过；未通过的项进入遗留问题",
                "deliverable_ref": _pick_deliverable(domain, data["deliverables"], deliverable_ids),
            })
        # 每个系统 1 条业务功能用例
        cases.append({
            "case_id": "UAT-BIZ-%03d" % (len([c for c in cases if c["domain"] == "业务功能"]) + 1),
            "system": sname,
            "domain": "业务功能",
            "title": "%s 核心业务链路功能验收" % sname,
            "precondition": "系统已部署且数据已同步",
            "steps": ["按客户提供的业务场景执行主流程", "校验关键页面/接口返回", "校验写操作落库"],
            "expected": "主流程可用、数据正确、性能满足约定（待客户确认具体场景）",
            "deliverable_ref": _pick_deliverable("业务", data["deliverables"], deliverable_ids),
        })
    return cases


def _pick_deliverable(keyword: str, deliverables: list, idset: set) -> str:
    """按关键字匹配交付物 id；无匹配返回「待确认」，绝不伪造 id。"""
    for d in deliverables:
        name = str(d.get("name", ""))
        if keyword in name:
            return str(d.get("id", "待确认")).strip() or "待确认"
    return "待确认"


def apply_results(cases: list, results: list) -> dict:
    """回填执行结果并汇总；有 fail/blocked 即不通过。"""
    rmap = {str(r.get("case_id")): r for r in results or []}
    for c in cases:
        r = rmap.get(c["case_id"])
        if r:
            c["status"] = STATUS_LABEL.get(r.get("status", ""), r.get("status", "未执行"))
            c["note"] = r.get("note", "")
        else:
            c["status"] = "未执行"
            c["note"] = ""
    summary = {"total": len(cases)}
    for label in STATUS_LABEL.values():
        summary[label] = len([c for c in cases if c.get("status") == label])
    executed = summary["total"] - summary["未执行"]
    summary["executed"] = executed
    summary["pass_rate"] = round(summary["通过"] / executed, 4) if executed else 0.0
    failed = summary["不通过"] + summary["阻塞"]
    summary["conclusion"] = "不通过" if (failed or not executed) else "通过"
    summary["blocking_reason"] = ("存在 %d 条不通过/阻塞用例" % failed) if failed else (
        "用例未执行，无法判定" if not executed else "")
    return summary


def render_md(data: dict, cases: list, summary: dict | None) -> tuple:
    today = date.today().isoformat()
    lines = ["# UAT 验收测试用例清单", "",
             "| 字段 | 值 |", "|---|---|",
             "| 项目 | %s |" % data["project"],
             "| 目标云 | %s |" % data["target_cloud"],
             "| 生成日期 | %s |" % today,
             "| 用例总数 | %d |" % len(cases), "",
             "| 用例编号 | 系统 | 域 | 用例标题 | 前置条件 | 步骤 | 预期结果 | 对应交付物 | 状态 | 备注 |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for c in cases:
        lines.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            c["case_id"], c["system"], c["domain"], c["title"], c["precondition"],
            "；".join(c["steps"]), c["expected"], c["deliverable_ref"],
            c.get("status", "未执行"), c.get("note", "")))
    uat_md = "\n".join(lines) + "\n"

    rl = ["# 项目验收报告", "",
          "| 字段 | 值 |", "|---|---|",
          "| 项目 | %s |" % data["project"],
          "| 目标云 | %s |" % data["target_cloud"],
          "| 日期 | %s |" % today, "",
          "## 1. 交付物逐项对照", "",
          "| 交付物编号 | 交付物名称 | 对应用例 | 验收结论 |",
          "|---|---|---|---|"]
    for d in data["deliverables"]:
        did = str(d.get("id", "")).strip()
        refs = [c["case_id"] for c in cases if c["deliverable_ref"] == did]
        rl.append("| %s | %s | %s | %s |" % (
            did, d.get("name", ""), "、".join(refs) or "无（待确认）",
            "已验证" if refs else "待确认"))
    rl += ["", "## 2. UAT 执行汇总", ""]
    if summary:
        rl += ["| 指标 | 值 |", "|---|---|",
               "| 用例总数 | %d |" % summary["total"],
               "| 已执行 | %d |" % summary["executed"],
               "| 通过 | %d |" % summary["通过"],
               "| 不通过 | %d |" % summary["不通过"],
               "| 阻塞 | %d |" % summary["阻塞"],
               "| 未执行 | %d |" % summary["未执行"],
               "| 通过率 | %.2f%% |" % (summary["pass_rate"] * 100),
               "| **验收结论** | **%s** |" % summary["conclusion"], ""]
        if summary["blocking_reason"]:
            rl += ["> 阻塞原因：%s" % summary["blocking_reason"], ""]
    else:
        rl += ["未回填执行结果（`results` 为空），仅生成用例清单，验收结论待定。", ""]
    rl += ["## 3. 遗留问题与处理计划", "",
           "| 编号 | 问题描述 | 责任人 | 计划完成日期 | 状态 |", "|---|---|---|---|---|"]
    open_items = [c for c in cases if c.get("status") in ("不通过", "阻塞")]
    if open_items:
        for c in open_items:
            rl.append("| %s | %s | 待确认 | 待确认 | 待整改 |" % (c["case_id"], c.get("note") or c["title"]))
    else:
        rl.append("| — | 无遗留问题（或未回填执行结果） | — | — | — |")
    rl += ["", "## 4. 客户签字", "",
           "| 角色 | 姓名 | 签字 | 日期 |", "|---|---|---|---|",
           "| 客户方代表 | | | |", "| 交付方项目经理 | | | |", "",
           "> 本报告不含价格、单价、人天与月费信息（与报价物理隔离）。",
           "> 未核实项一律标注「待确认」，不得虚构人员、案例与证书。", ""]
    return uat_md, "\n".join(rl) + "\n"


def self_test() -> int:
    """内置自检：用最小输入跑通全链路，证明脚本可用。"""
    sample = {
        "project": "自检项目",
        "target_cloud": "alicloud",
        "deliverables": [{"id": "D-01", "name": "网络 HLD 设计文档"},
                         {"id": "D-02", "name": "数据库迁移方案"}],
        "systems": [{"name": "订单系统", "domains": ["网络", "数据库", "监控运维"]}],
        "results": [{"case_id": "UAT-NET-001", "status": "pass", "note": ""},
                    {"case_id": "UAT-DBA-001", "status": "pass", "note": ""},
                    {"case_id": "UAT-MON-001", "status": "fail", "note": "一致性校验差 2 行"},
                    {"case_id": "UAT-BIZ-001", "status": "pass", "note": ""}],
    }
    cases = build_cases(sample)
    summary = apply_results(cases, sample["results"])
    uat_md, rep_md = render_md(sample, cases, summary)
    assert len(cases) == 4, "用例数应为 3 域 + 1 业务，实际 %d" % len(cases)
    assert summary["executed"] == 4, "results 全部命中时执行数应为 4，实际 %d（case_id 前缀可能不一致）" % summary["executed"]
    assert summary["conclusion"] == "不通过", "存在 fail 时结论必须为不通过"
    assert summary["pass_rate"] == 0.75, "通过率应为 0.75，实际 %s" % summary["pass_rate"]
    assert "待确认" in uat_md, "未匹配交付物应标待确认"
    print("[self-test] 用例数=%d 结论=%s 通过率=%.2f%% UAT_MD=%dB REPORT_MD=%dB" % (
        len(cases), summary["conclusion"], summary["pass_rate"] * 100, len(uat_md.encode()),
        len(rep_md.encode())))
    print("[self-test] PASS")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="mig-acceptance driver（阶段 05 验收）")
    ap.add_argument("--input", help="输入 JSON 路径")
    ap.add_argument("--out-dir", default=".", help="输出目录")
    ap.add_argument("--self-test", action="store_true", help="内置自检")
    args = ap.parse_args()

    if args.self_test:
        return self_test()
    if not args.input:
        print("ERROR: 需指定 --input 或 --self-test", file=sys.stderr)
        return 2

    try:
        data = load_input(args.input)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        # 明确说明失败原因，不吞异常
        print("ERROR: 读取输入失败：%s" % exc, file=sys.stderr)
        return 2

    cases = build_cases(data)
    summary = apply_results(cases, data.get("results")) if data.get("results") else None
    uat_md, rep_md = render_md(data, cases, summary)

    os.makedirs(args.out_dir, exist_ok=True)
    paths = {}
    for name, content in (("UAT用例清单.md", uat_md), ("验收报告.md", rep_md)):
        p = os.path.join(args.out_dir, name)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(content)
        paths[name] = p

    payload = {
        "conclusion": summary["conclusion"] if summary else "待定（未回填执行结果）",
        "confidence": "高" if summary and summary["executed"] == summary["total"] else "低",
        "suggested_action": "与客户确认用例并回填 results" if not summary else (
            "整改遗留问题后重新验收" if summary["conclusion"] == "不通过" else "提交客户签字"),
        "escalation_reason": "",
        "deliverables_check": [{"id": str(d.get("id", "")).strip(), "name": d.get("name", ""),
                                "covered": any(c["deliverable_ref"] == str(d.get("id", "")).strip()
                                               for c in cases)}
                               for d in data["deliverables"]],
        "uat_cases": cases,
        "summary": summary,
        "open_items": [{"case_id": c["case_id"], "desc": c.get("note") or c["title"]}
                       for c in cases if c.get("status") in ("不通过", "阻塞")],
        "artifacts": paths,
    }
    jp = os.path.join(args.out_dir, "acceptance.json")
    with open(jp, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)

    print("OK 用例=%d 结论=%s -> %s" % (len(cases), payload["conclusion"], jp))
    return 0


if __name__ == "__main__":
    sys.exit(main())
