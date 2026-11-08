#!/usr/bin/env python3
"""迁移交付运维手册（Runbook 集）生成 / Operation manual builder（阶段 03）

用法:
    python3 operation_manual.py --self-test
    python3 operation_manual.py --input manual.json --out-dir ./out

输入 JSON:
{
  "project": "C-Customer CHINA M2C (2026SR1149)",   # 必填
  "target_cloud": "alicloud",                        # 必填
  "source_cloud": "on-premise",                      # 选填
  "owner": "交付团队",                                # 选填，缺省→待确认
  "domains": ["compute","network","database"],       # 选填，缺省=全部 7 域
  "runbooks": [                                      # 选填：项目特有的补充 runbook
    {"id":"RB-XXX","title":"切换 DNS 到目标云","domain":"network","env":"prod",
     "trigger":"...","precheck":["..."],"steps":["..."],
     "verify":"...","rollback":"...","owner":"网络工程师"}
  ]
}

输出: operation_manual.md（可读）+ operation_manual.json（结构化）

设计口径:
- 每个 runbook **必须** 五要素齐全：trigger / precheck / steps / verify / rollback。
  任一缺失 -> 该 runbook 标 incomplete 并进 todo，**不伪造步骤**。
- 无 rollback 的 runbook 视为不可执行（割接红线），单独列入 no_rollback 清单。
- 云特有命令只在有事实源（CLOUD_CMD）时输出；无事实源 -> 「待确认（须查目标云官方文档）」，
  **绝不臆造 CLI 命令**。
退出码: 0 = 正常；2 = 输入不可用/必填缺失
红线: 本脚本**不输出任何金额/单价/月费**；不执行任何生产变更（只产出文档）。
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# ---- 七域标准 runbook 骨架（domain -> [runbook 模板]）----
# 每个模板给出 title/trigger/precheck/steps/verify/rollback 的**占位要求**，
# 具体命令若目标云有事实源则从 CLOUD_CMD 取，否则留「待确认」。
DOMAIN_RUNBOOKS: dict[str, list[dict]] = {
    "network": [
        {"id": "RB-NET-01", "title": "VPC / 子网与安全组开通",
         "trigger": "目标云环境初始化，或新增业务网段需要放通时",
         "precheck": ["已确认 CIDR 与源端及现有云上网段无重叠",
                      "已确认安全组最小端口清单（禁止 0.0.0.0/0 全放通）"],
         "steps": ["按 LLD 网段规划创建 VPC 与子网", "创建安全组并按端口清单加白", "配置路由表与 NAT/EIP"],
         "verify": "从源端探测目标子网连通性；安全组规则数与 LLD 一致",
         "rollback": "删除新建子网/安全组（须确认无资源挂载）"},
        {"id": "RB-NET-02", "title": "专线 / VPN 通道建立与切换",
         "trigger": "需要源端与目标云二层/三层互通，或割接前建立数据同步通道",
         "precheck": ["物理专线已施工完成或 VPN 网关已开通", "两端路由无冲突", "带宽满足同步窗口要求"],
         "steps": ["配置 VPN/专线网关与路由宣告", "小流量试跑并测延迟丢包", "逐步加大至生产流量"],
         "verify": "ping/iperf 达标；业务侧可访问目标端服务",
         "rollback": "回退路由指向源端，保留通道备用"},
    ],
    "security": [
        {"id": "RB-SEC-01", "title": "IAM 子账号与最小权限配置",
         "trigger": "新成员入职、新系统接入，或权限审计发现越权时",
         "precheck": ["已有角色-权限矩阵（来自 LLD）", "已确认不使用主账号 AK 做日常操作"],
         "steps": ["按角色创建 RAM 用户/角色", "绑定最小权限策略", "开启 MFA 与操作审计"],
         "verify": "用子账号验证仅能访问授权资源；审计日志可查",
         "rollback": "解绑策略并禁用账号（保留审计记录）"},
        {"id": "RB-SEC-02", "title": "密钥与证书轮换",
         "trigger": "定期轮换（建议 90 天）或疑似泄露时",
         "precheck": ["已梳理使用方清单", "确认新密钥已下发到所有消费方"],
         "steps": ["生成新密钥/证书", "灰度切换消费方", "旧密钥保留观察期后禁用"],
         "verify": "全部消费方调用正常；旧密钥调用量为 0",
         "rollback": "恢复旧密钥启用状态（仅观察期内有效）"},
    ],
    "compute": [
        {"id": "RB-COM-01", "title": "ECS 实例创建与基线配置",
         "trigger": "迁移实施期按选型结果开通目标端主机",
         "precheck": ["已确认规格档位（来自 mig-sizing-advice）", "镜像已通过安全基线扫描",
                      "OS 非 EOL 版本"],
         "steps": ["按规格创建实例并加入指定子网/安全组", "执行基线加固脚本", "安装监控与日志 Agent"],
         "verify": "实例可登录；监控 Agent 上报正常；基线扫描通过",
         "rollback": "释放实例（须确认无数据盘残留需保留）"},
        {"id": "RB-COM-02", "title": "实例规格升降配",
         "trigger": "监控发现持续超水位或长期低利用率",
         "precheck": ["已确认目标规格在当前可用区有库存", "已评估停机影响（部分规格变更需重启）"],
         "steps": ["对无状态实例先摘流量", "执行变配", "验证业务后挂回流量"],
         "verify": "业务健康检查通过；资源水位回到目标区间",
         "rollback": "变回原规格（须确认库存）"},
    ],
    "storage": [
        {"id": "RB-STO-01", "title": "对象存储迁移与校验",
         "trigger": "文件/对象数据从源端搬到目标云对象存储",
         "precheck": ["已确认数据总量与清单", "已确认同步窗口与带宽", ">10TB 须评估离线搬运或分阶段"],
         "steps": ["全量同步", "增量追平", "校验对象数量与 MD5 抽样", "切换应用指向"],
         "verify": "源/目标对象数与抽样校验和一致",
         "rollback": "应用指回源端；保留目标端副本观察"},
        {"id": "RB-STO-02", "title": "存储扩容与生命周期策略配置",
         "trigger": "容量水位接近阈值，或冷数据需要降本归档",
         "precheck": ["已确认扩容上限与配额", "生命周期规则已在非生产验证"],
         "steps": ["调整容量或挂载新卷", "配置生命周期转储规则", "观察 7 天成本与访问"],
         "verify": "容量水位回落；归档数据可正常取回",
         "rollback": "关闭生命周期规则（已转储数据须回迁）"},
    ],
    "database": [
        {"id": "RB-DBA-01", "title": "数据库迁移（全量 + 增量追平）",
         "trigger": "数据库从源端迁移到目标云数据库/自建",
         "precheck": ["已确认引擎版本满足最低要求", "异构引擎已完成兼容性评估",
                      "已确认字符集与时区一致", "备份可恢复性已验证"],
         "steps": ["搭建目标实例并建库建用户", "全量导出导入", "配置增量同步", "追平后停写切换"],
         "verify": "表数量/行数/抽样校验和一致；应用连通性正常",
         "rollback": "应用连回源库；保留目标库只读副本"},
        {"id": "RB-DBA-02", "title": "数据库备份与恢复演练",
         "trigger": "定期演练（建议每季度）或重大变更前",
         "precheck": ["备份策略已配置（全量+增量+PITR）", "演练环境已准备，不影响生产"],
         "steps": ["触发备份", "恢复到演练实例", "校验数据时间点与完整性"],
         "verify": "恢复实例可对外服务；RTO/RPO 达标（须与合同口径一致）",
         "rollback": "演练环境释放（生产不受影响）"},
    ],
    "monitoring": [
        {"id": "RB-MON-01", "title": "监控告警接入与阈值设定",
         "trigger": "资源上线后接入统一监控，或告警阈值需要调整",
         "precheck": ["已确认监控项清单（CPU/内存/磁盘/连接数/业务黄金指标）",
                      "告警接收人与升级路径已确认"],
         "steps": ["安装配置监控 Agent", "创建告警规则与通知渠道", "做一次告警触达测试"],
         "verify": "人为触发一次告警，确认通知到达且可定位",
         "rollback": "停用告警规则（保留历史数据）"},
        {"id": "RB-MON-02", "title": "日志采集与留存配置",
         "trigger": "统一日志平台接入，或合规要求调整留存期",
         "precheck": ["已确认留存期（等保/审计要求）", "已确认敏感字段脱敏规则"],
         "steps": ["配置采集端与索引", "设置脱敏与留存策略", "验证检索与导出"],
         "verify": "可检索到最新日志；敏感字段已脱敏",
         "rollback": "停止采集（已采集数据按留存策略处理）"},
    ],
    "cutover": [
        {"id": "RB-CUT-01", "title": "割接演练（Dry-run）",
         "trigger": "正式割接前必须至少一次完整演练",
         "precheck": ["割接 Checklist 已评审通过", "回滚方案已演练过", "停机窗口已书面确认"],
         "steps": ["按 Checklist 全量执行一遍", "记录每步耗时与问题", "执行回滚验证"],
         "verify": "演练总耗时在窗口内；回滚可成功",
         "rollback": "演练环境问题按缺陷流程处理，不进生产"},
        {"id": "RB-CUT-02", "title": "正式割接与回滚决策",
         "trigger": "停机窗口开始，且 Go/No-Go 检查项全部通过",
         "precheck": ["Go/No-Go 决策会已召开并签字", "回滚触发条件与决策人已明确",
                      "关键干系人在线"],
         "steps": ["停写并确认数据追平", "切换流量到目标端", "逐级验证业务功能", "观察期监控"],
         "verify": "核心业务全绿；监控无异常告警",
         "rollback": "达到回滚触发条件即执行回退（决策人独断，不再讨论）"},
    ],
}

DOMAIN_ORDER = ["network", "security", "compute", "storage", "database", "monitoring", "cutover"]
DOMAIN_CN = {
    "network": "网络", "security": "安全", "compute": "计算", "storage": "存储",
    "database": "数据库", "monitoring": "监控运维", "cutover": "割接",
}

# 云特有命令事实源：只收录有官方文档支撑的；无事实源一律「待确认」，绝不臆造 CLI
CLOUD_CMD: dict[str, dict[str, list[str]]] = {
    "alicloud": {
        "compute": ["aliyun ecs RunInstances --InstanceType <规格> --VSwitchId <vsw-id>"],
        "storage": ["ossutil cp -r <src> oss://<bucket>/<path> --update",
                    "ossutil ls oss://<bucket>/<path> | wc -l  # 校验对象数"],
        "monitoring": ["# 云监控控制台配置或 aliyun cms PutMetricRule（参数以官方文档为准）"],
    },
    "aws": {
        "compute": ["aws ec2 run-instances --instance-type <type> --subnet-id <subnet-id>"],
        "storage": ["aws s3 sync <src> s3://<bucket>/<path>",
                    "aws s3 ls s3://<bucket>/<path> --recursive | wc -l  # 校验对象数"],
        "monitoring": ["# CloudWatch 告警：aws cloudwatch put-metric-alarm（参数以官方文档为准）"],
    },
}
NO_FACT_NOTE = "待确认（本 skill 无该云该域的官方命令事实源，须查目标云官方文档后补充，不得臆造）"

REQUIRED_FIVE = ("trigger", "precheck", "steps", "verify", "rollback")


def _nonempty(v) -> bool:
    """判定要素是否真正填写（空串/空列表/None 均视为缺失）。"""
    if v is None:
        return False
    if isinstance(v, str):
        return bool(v.strip())
    if isinstance(v, (list, tuple)):
        return any(_nonempty(x) for x in v)
    return True


def _cmds_for(cloud: str, domain: str) -> list[str]:
    table = CLOUD_CMD.get((cloud or "").strip().lower())
    if not table:
        return [NO_FACT_NOTE]
    return table.get(domain, [NO_FACT_NOTE])


def normalize_rb(rb: dict, cloud: str) -> dict:
    """把 runbook 规范化为统一结构，并检查五要素完整性。"""
    out = {
        "id": (rb.get("id") or "").strip() or "待确认-ID",
        "title": (rb.get("title") or "").strip() or "待确认标题",
        "domain": (rb.get("domain") or "").strip().lower(),
        "env": (rb.get("env") or "prod").strip().lower(),
        "owner": (rb.get("owner") or "").strip(),
        "trigger": (rb.get("trigger") or "").strip(),
        "precheck": [str(x) for x in (rb.get("precheck") or [])],
        "steps": [str(x) for x in (rb.get("steps") or [])],
        "verify": (rb.get("verify") or "").strip(),
        "rollback": (rb.get("rollback") or "").strip(),
    }
    missing = [k for k in REQUIRED_FIVE if not _nonempty(out.get(k))]
    out["missing"] = missing
    out["incomplete"] = bool(missing)
    if not out["owner"]:
        out["owner"] = "待确认（未指定责任人，交付前必须落实到人）"
    if "rollback" in missing:
        out["no_rollback"] = True
    out["commands"] = _cmds_for(cloud, out["domain"])
    return out


def build(data: dict) -> dict:
    project = (data.get("project") or "").strip()
    cloud = (data.get("target_cloud") or "").strip()
    if not project:
        raise ValueError("缺必填字段 project")
    if not cloud:
        raise ValueError("缺必填字段 target_cloud")

    domains = [d.strip().lower() for d in (data.get("domains") or [])]
    if not domains:
        domains = list(DOMAIN_ORDER)
    unknown = [d for d in domains if d not in DOMAIN_RUNBOOKS]
    if unknown:
        raise ValueError(f"未知 domain: {unknown}（可选: {DOMAIN_ORDER}）")

    items: list[dict] = []
    for d in domains:
        for tpl in DOMAIN_RUNBOOKS[d]:
            # 骨架模板不带 domain 字段，此处注入，否则命令查表与分组都会落空
            merged = dict(tpl)
            merged.setdefault("domain", d)
            items.append(normalize_rb(merged, cloud))
    for extra in (data.get("runbooks") or []):
        items.append(normalize_rb(extra, cloud))

    todo = [it["id"] for it in items if it["incomplete"]]
    no_rb = [it["id"] for it in items if it.get("no_rollback")]

    return {
        "project": project,
        "source_cloud": (data.get("source_cloud") or "待确认").strip(),
        "target_cloud": cloud,
        "owner": (data.get("owner") or "").strip() or "待确认（未指定，交付前须落实到人）",
        "domains": domains,
        "items": items,
        "todo": todo,
        "no_rollback": no_rb,
        "stats": {
            "total": len(items),
            "complete": len(items) - len(todo),
            "incomplete": len(todo),
            "no_rollback": len(no_rb),
        },
    }


def render_md(r: dict) -> str:
    cn = lambda d: f"{DOMAIN_CN.get(d, d)}（{d}）"
    L: list[str] = []
    L.append(f"# 运维手册 / Operation Manual — {r['project']}")
    L.append("")
    L.append(f"- 源云 / Source：**{r['source_cloud']}** → 目标云 / Target：**{r['target_cloud']}**")
    L.append(f"- 手册责任人 / Owner：**{r['owner']}**")
    L.append(f"- 覆盖域 / Domains：{', '.join(cn(d) for d in r['domains'])}")
    st = r["stats"]
    L.append(f"- 统计：Runbook 共 **{st['total']}** 条 · 五要素齐全 **{st['complete']}** · "
             f"待补 **{st['incomplete']}** · 无回滚方案 **{st['no_rollback']}**")
    L.append("")
    L.append("本手册**不执行任何生产变更**，仅为操作指引；所有命令须在变更窗口内、经审批后执行。")
    L.append("本产物不含任何费用信息（运维与报价分离，金额一律由 pcs-quotation 出具）。")
    L.append("")

    L.append("## 汇总 / Summary")
    L.append("")
    L.append("| 域 Domain | Runbook 数 | 齐全 | 待补 | 无回滚 |")
    L.append("|---|---|---|---|---|")
    for d in r["domains"]:
        sub = [i for i in r["items"] if i["domain"] == d]
        inc = sum(1 for i in sub if i["incomplete"])
        nr = sum(1 for i in sub if i.get("no_rollback"))
        L.append(f"| {cn(d)} | {len(sub)} | {len(sub) - inc} | {inc} | {nr} |")
    L.append("")

    L.append("## Runbook 明细 / Detail")
    L.append("")
    for d in r["domains"]:
        L.append(f"### {cn(d)}")
        L.append("")
        for it in [i for i in r["items"] if i["domain"] == d]:
            flag = " ⚠️ **要素待补**" if it["incomplete"] else ""
            L.append(f"#### {it['id']} · {it['title']}{flag}")
            L.append("")
            L.append(f"- 环境 / Env：`{it['env']}` · 责任人 / Owner：{it['owner']}")
            L.append(f"- **触发条件 / Trigger**：{it['trigger'] or '❓ 待确认'}")
            L.append("- **前置检查 / Precheck**：")
            if it["precheck"]:
                for n, p in enumerate(it["precheck"], 1):
                    L.append(f"  {n}. {p}")
            else:
                L.append("  - ❓ 待确认")
            L.append("- **操作步骤 / Steps**：")
            if it["steps"]:
                for n, s in enumerate(it["steps"], 1):
                    L.append(f"  {n}. {s}")
            else:
                L.append("  - ❓ 待确认")
            L.append(f"- **验证 / Verify**：{it['verify'] or '❓ 待确认'}")
            L.append(f"- **回滚 / Rollback**：{it['rollback'] or '❓ 待确认（无回滚方案不得进割接）'}")
            L.append("- **参考命令 / Commands**：")
            for c in it["commands"]:
                L.append(f"  - `{c}`")
            if it["incomplete"]:
                L.append(f"- ⚠️ 缺失要素：`{'、'.join(it['missing'])}` — 须补齐后方可交付")
            L.append("")

    if r["no_rollback"]:
        L.append("## 🚩 无回滚方案（割接红线）")
        L.append("")
        for i in r["no_rollback"]:
            L.append(f"- `{i}` — 缺 `rollback`，**不得进入正式割接清单**")
        L.append("")
    if r["todo"]:
        L.append("## 待确认清单 / Open items")
        L.append("")
        for i in r["todo"]:
            L.append(f"- `{i}`")
        L.append("")

    L.append("---")
    L.append("")
    L.append("口径声明：本手册只给**操作步骤与验证/回滚口径**，不含价格；"
             "金额一律由 `pcs-quotation` 出具。命令中 `<...>` 为占位符，"
             "执行前须替换为实际资源标识并在非生产验证。")
    return "\n".join(L) + "\n"


def self_test() -> int:
    ok = 0

    # 1) 七域默认全量 → 14 条骨架
    r = build({"project": "T", "target_cloud": "alicloud"})
    assert r["stats"]["total"] == 14, r["stats"]
    assert set(r["domains"]) == set(DOMAIN_ORDER)
    print("SELFTEST 1 PASS 七域默认 → 14 条 runbook")
    ok += 1

    # 2) 骨架五要素齐全 → 无 todo
    assert r["todo"] == [], r["todo"]
    assert r["stats"]["complete"] == 14
    print("SELFTEST 2 PASS 骨架五要素齐全，无待补")
    ok += 1

    # 3) 自定义 runbook 缺 rollback → 标 incomplete + 进 no_rollback
    r2 = build({"project": "T", "target_cloud": "alicloud", "domains": ["compute"],
                "runbooks": [{"id": "RB-X1", "title": "危险操作", "domain": "compute",
                              "trigger": "t", "precheck": ["p"], "steps": ["s"], "verify": "v"}]})
    rb = [i for i in r2["items"] if i["id"] == "RB-X1"][0]
    assert rb["incomplete"] and rb["missing"] == ["rollback"], rb
    assert rb.get("no_rollback") and "RB-X1" in r2["no_rollback"]
    print("SELFTEST 3 PASS 缺 rollback → incomplete + 割接红线清单")
    ok += 1

    # 4) 空列表 steps 视为缺失（不得被当成已填）
    r3 = build({"project": "T", "target_cloud": "aws", "domains": ["network"],
                "runbooks": [{"id": "RB-X2", "title": "空步骤", "domain": "network",
                              "trigger": "t", "precheck": [], "steps": ["  "],
                              "verify": "v", "rollback": "r"}]})
    rb2 = [i for i in r3["items"] if i["id"] == "RB-X2"][0]
    assert "steps" in rb2["missing"] and "precheck" in rb2["missing"], rb2
    print("SELFTEST 4 PASS 空串/空列表视为缺失，不伪造")
    ok += 1

    # 5) 未知云 → 命令不臆造
    r4 = build({"project": "T", "target_cloud": "some-cloud", "domains": ["compute"]})
    assert all(i["commands"] == [NO_FACT_NOTE] for i in r4["items"]), r4["items"][0]["commands"]
    print("SELFTEST 5 PASS 未知云不臆造 CLI 命令")
    ok += 1

    # 6) 骨架 domain 已注入（否则命令查表与分组落空）
    r_dom = build({"project": "T", "target_cloud": "alicloud"})
    assert all(i["domain"] in DOMAIN_ORDER for i in r_dom["items"]), [
        i["domain"] for i in r_dom["items"]]
    print("SELFTEST 5.5 PASS 骨架 domain 已注入")
    ok += 1

    # 6) 有事实源的云 → 给出命令
    r5 = build({"project": "T", "target_cloud": "aws", "domains": ["storage"]})
    assert any("aws s3 sync" in c for i in r5["items"] for c in i["commands"])
    print("SELFTEST 6 PASS aws storage 给出官方命令")
    ok += 1

    # 7) 必填缺失 → ValueError
    for bad in ({"target_cloud": "aws"}, {"project": "T"}, {}):
        try:
            build(bad)
            raise AssertionError("应抛 ValueError")
        except ValueError:
            pass
    print("SELFTEST 7 PASS 必填缺失报错")
    ok += 1

    # 8) 未知 domain → ValueError（不静默忽略）
    try:
        build({"project": "T", "target_cloud": "aws", "domains": ["blockchain"]})
        raise AssertionError("应抛 ValueError")
    except ValueError:
        pass
    print("SELFTEST 8 PASS 未知 domain 报错不静默")
    ok += 1

    # 9) 无 owner → 待确认
    r6 = build({"project": "T", "target_cloud": "alicloud", "domains": ["security"]})
    assert "待确认" in r6["owner"], r6["owner"]
    print("SELFTEST 9 PASS 无 owner → 待确认")
    ok += 1

    # 10) 渲染产物含关键段落且无价格字样
    md = render_md(r)
    for key in ("## Runbook 明细", "触发条件", "回滚 / Rollback", "口径声明"):
        assert key in md, key
    for word in ("¥", "月费", "单价", "人天"):
        assert word not in md, word
    print("SELFTEST 10 PASS 渲染完整且零金额")
    ok += 1

    print(f"SELFTEST PASS（{ok}/11）")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="迁移交付运维手册生成（阶段 03）")
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
    (out_dir / "operation_manual.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out_dir / "operation_manual.md").write_text(render_md(result), encoding="utf-8")
    print(f"[ok] 输出: {out_dir}/operation_manual.md, {out_dir}/operation_manual.json")
    print(f"[ok] Runbook {result['stats']['total']} 条 · 齐全 {result['stats']['complete']} · "
          f"待补 {result['stats']['incomplete']} · 无回滚 {result['stats']['no_rollback']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
