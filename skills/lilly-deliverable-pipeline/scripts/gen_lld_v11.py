# -*- coding: utf-8 -*-
"""生成 PM-05 LLD V1.1 (DOCX), 并入圆桌 R1–R6 与第 9–11 章。

设计源文: Lilly_AIOps_LLD_Codex_V1.1.md (2026-11-15)。
本脚本复用 _style.py 的样式助手 (黑/灰/安畅红, 禁蓝), 但显式指定输出路径,
因 _style.py 的 BASE 指向已过时的旧目录, 不可直接使用其 OUT_DIR。
配色与字体由 _style.py 统一: 微软雅黑 + w:eastAsia, 内置标题样式 (可出导航窗格/目录)。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _style as S

from docx import Document

# 显式正确路径 (绕开 _style.BASE 旧目录)
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = "/home/ubuntu/客户项目/Lilly_AIOps/02_项目方案/codex/Lilly_AIOps_实现包_2026-11-14"
OUT = os.path.join(BASE, "deliverables", "Lilly_AIOps_LLD_PM05_V1.1.docx")


def h1(doc, t):
    doc.add_heading(t, level=1)


def h2(doc, t):
    doc.add_heading(t, level=2)


def h3(doc, t):
    doc.add_heading(t, level=3)


def main():
    doc = S.new_doc()
    S.set_doc_fonts(doc)

    # ---------- 封面 ----------
    S.cover(
        doc,
        "Lilly AIOps · AgentCore 四场景详细设计 (LLD) V1.1",
        "低层设计 · 圆桌增订 R1–R6 并入 · 对应 WBS 4.3.1–4.3.6 / WBS 10.x",
        "版本 V1.1  |  日期 2026-11-15  |  编制 实施方 PM（刘金龙）  |  状态 评审稿（待客户确认）",
    )
    S.para(doc, "本稿在 PM05 V1.0（2026-11-11）基线上，并入圆桌增订 V1.1（2026-11-12）的 R1–R6 红线共识与第 9–11 章；设计源文见 Lilly_AIOps_LLD_Codex_V1.1.md。", size=10, color=(0x59, 0x59, 0x59))

    # ---------- 0 设计过程 ----------
    h1(doc, "0. 设计过程与输入源")
    S.para(doc, "本稿不是全文重写，而是在 PM05 V1.0 低层设计基线上，按圆桌六轮轮值共识做增量合并与红线澄清。设计链路可追溯：")
    S.add_table(
        doc,
        ["环节", "输入/输出", "状态"],
        [
            ["架构基线", "HLD PM04 V1.0 六层架构/四场景/三级管控", "已并入"],
            ["低层基线", "LLD PM05 V1.0 WBS 4.3.1–4.3.6 六项详细设计", "本稿基础"],
            ["圆桌轮值", "Codex→CEO→Hermes→Claude（2026-11-12）R1–R6 共识", "已并入 §1"],
            ["红线闸门", "禁删/不自动改生产/双人四眼/RWD SELECT-only/HITL/不虚构/零费用", "已并入 §2"],
            ["可行性证据", "本地仿真 orchestrator 四场景 4/4 PASS（2026-11-14）", "已实测"],
        ],
        widths_cm=[3.0, 9.5, 3.5],
    )
    S.para(doc, "接口契约来源：本稿 MCP 工具名与参数（adb_search / cost_query / cost_anomaly / sn_create_change / sn_callback / aad_check_access / OpenAgent）均取自 handbook/simulation 与 gen_lld.py 真实契约，不虚构接口。R-002 接口当前 Mock 双轨、三灯 RED 为预期状态，11/20 硬闸门前转 live 复测。", size=10, color=(0x59, 0x59, 0x59))

    # ---------- 1 修订清单 ----------
    h1(doc, "1. 修订冲突清单（V1.0 → V1.1，R1–R6）")
    S.add_table(
        doc,
        ["#", "V1.0 表述", "圆桌红线/共识", "V1.1 修订动作", "落点"],
        [
            ["R1", "§7.2 高风险动作审批后由 OpenAgent 执行", "不自动改生产", "重启/规格变更本期不自动执行；Agent 仅出取证+预案+SN建议(HITL)，客户运维人工执行；OpenAgent 仅限 P1 非生产+双人四眼+禁删", "§3.1/§4.2"],
            ["R2", "§3.2 准确率≥80% 含拒答率", "禁对外 SLA 承诺", "加注内部验收口径，非对外 SLA，不写入客户合同", "§3.2"],
            ["R3", "无自主处置/路线图分界", "自主处置/自动剧本→路线图", "新增 §9.1 本期/路线图分界接口契约", "第9章"],
            ["R4", "§6/§7 单节点 HITL", "升级双人四眼", "新增 SN 双节点审批+审计字段", "§9.2"],
            ["R5", "未列 RWD 最小权限", "不碰 RWD 写路径", "新增 RWD SELECT-only 最小权限清单", "§9.3"],
            ["R6", "无治理/自恢复/审计独立章", "三章新增", "新增 LLD 第 9–11 章", "第9–11章"],
        ],
        widths_cm=[1.0, 3.2, 3.0, 6.5, 2.0],
    )

    # ---------- 2 红线合规 ----------
    h1(doc, "2. 红线合规对照（LLD 视角）")
    S.add_table(
        doc,
        ["红线", "实现机制", "代码/仿真证据"],
        [
            ["禁删除(WBS 8.5)", "apply 遇 delete 返回 ok=False；delete() raise", "iac_simulator.py L3/L72-77/L104-105"],
            ["越权100%拦截", "_check_access 按用户组→资源组判定", "aad_mcp.py L8/L55-63（实测 deny）"],
            ["HITL+双人四眼", "高风险先过 SN 双审批，双 approved 才执行", "servicenow_mcp.py L44/L62-65/L78；§9.2"],
            ["不自动改生产(R1)", "重启/规格变更/删除本期一律不自动执行", "§9.1/§10.1/§10.3"],
            ["RWD SELECT-only(R5)", "只读副本仅 SELECT，禁写", "§9.3"],
            ["零费用/不花信用卡", "仿真纯标准库；真实联调 RAM 只读", "AGENTS.md 安全红线"],
            ["不虚构人员/案例", "仿真 Agent 均角色化名", "agent_configs/*.json"],
        ],
        widths_cm=[3.0, 6.5, 6.5],
    )
    S.para(doc, "一票否决项：当前方案未触发任何一项（删除硬拒、越权必拦、HITL 缺双审批不执行、零费用、无虚构）。", bold=True)

    # ---------- 3 精确改文 ----------
    h1(doc, "3. 对 V1.0 的精确改文（评审确认后生效）")
    h2(doc, "3.1 §7.2 高风险动作段（R1）")
    S.para(doc, "改为：高风险动作（如重启主实例、变更生产规格）本期不自动执行；Agent 仅输出根因取证 + 恢复预案 + ServiceNow 变更建议（HITL），由客户运维在审批后人工执行。OpenAgent 受控执行仅限 P1 非生产动作（如非生产 ECS 重启演练、配置回滚），且须双人四眼 + 禁删白名单。")
    h2(doc, "3.2 §3.2 准确率句（R2）")
    S.para(doc, "改为：准确率 ≥80% 含拒答率（阈值待客户确认）（内部验收口径，非对外 SLA 承诺，不写入客户合同）。")

    # ---------- 4 第 9 章 ----------
    h1(doc, "4. 新增第 9 章 · 智能体运行与治理详细设计（WBS 10.x）")
    h2(doc, "9.1 本期/路线图分界接口契约")
    S.para(doc, "沿用现有 MCP 工具集。本期 OpenAgent 受控执行仅限 P1 非生产动作，且须双人四眼 + 禁删。")
    S.add_table(
        doc,
        ["能力", "本期交付", "路线图", "接口/约束"],
        [
            ["① 知识库咨询", "✅", "", "adb_search，doc_id 100% 可追溯"],
            ["② FinOps 成本优化", "✅", "", "cost_query + cost_anomaly"],
            ["③ 自服务部署", "✅", "", "plan/apply，禁删白名单"],
            ["④ 告警修复-根因取证", "✅", "", "Analysis 出根因+证据"],
            ["④ 告警修复-P1 非生产受控执行", "✅", "", "双人四眼+禁删"],
            ["④ 生产自处置(重启等)", "", "🚫 本期", "不自动改生产"],
            ["自动剧本/受控自恢复(P2)", "", "🗺️ 路线图", "需 BIA/R-003"],
            ["知识图谱自动构建", "", "🗺️ 路线图", "采集依赖 Lilly 配合"],
        ],
        widths_cm=[5.0, 2.0, 2.0, 7.0],
    )
    h2(doc, "9.2 双人四眼审批流程（ServiceNow 双节点）")
    S.para(doc, "流程：Analysis 输出根因+预案 → sn_create_change(risk=high) → 节点1 技术审批(运维负责人) → 节点2 业务/安全审批(Lilly 指定) → 双通过生成 CR# → 执行(人工 或 OpenAgent P1 非生产) → 任一拒绝则 pending + 升级人工。")
    S.para(doc, "审计字段：cr_id / trigger_alert / approver_tech / approver_biz / approve_ts / trace_id。三类 Agent 职责固化（tl-alert-recovery / analysis-agent / recovery-agent）；AgentIdentity 短期授权最小权限、到期失效；高风险动作 100% HITL，技术+业务/安全两人均留痕。")
    h2(doc, "9.3 RWD SELECT-only 最小权限清单")
    S.add_table(
        doc,
        ["资源", "权限", "说明"],
        [
            ["RWD 库(只读副本)", "SELECT", "禁 INSERT/UPDATE/DELETE/DDL"],
            ["ADB 知识库", "只读检索", "adb_search"],
            ["云监控/操作审计", "只读", "监控与审计读取"],
            ["生产变更", "无", "本期不授权自动执行"],
        ],
        widths_cm=[5.0, 3.0, 8.0],
    )
    h2(doc, "9.4 运行可观测")
    S.para(doc, "AgentLoop Trace 全链路留存，覆盖编排→检索→建议→审批→执行（若有）每跳；监控覆盖度/响应 SLA 仅指建议生成时延，不含处置闭环时间（避免解读为端到端时效承诺）。")

    # ---------- 5 第 10 章 ----------
    h1(doc, "5. 新增第 10 章 · 受控自恢复详细设计（路线图，非本期）")
    h2(doc, "10.1 候选动作矩阵")
    S.add_table(
        doc,
        ["动作", "级", "本期处理"],
        [
            ["诊断取证/根因假设", "P0", "Agent 执行，出证据"],
            ["恢复预案生成", "P1", "建议 + HITL，人执行"],
            ["非生产配置回滚", "P1", "OpenAgent 受控 + 双人四眼"],
            ["生产重启/规格变更", "P2", "🚫 本期不自动执行"],
            ["自动扩缩容剧本", "P2", "🗺️ 路线图"],
        ],
        widths_cm=[6.0, 2.0, 8.0],
    )
    S.para(doc, "演进前置条件：BIA 完成（RTO/RPO 由客户定）、SOP 确认（R-003 首批告警场景）、审批 SLA 敲定（待确认）。")
    S.para(doc, "禁区（硬约束）：不自动改生产（重启/规格变更/删除一律不自动执行）；RWD 写路径零接触（仅 SELECT）。", bold=True)

    # ---------- 6 第 11 章 ----------
    h1(doc, "6. 新增第 11 章 · 审计与合规证据详细设计（GxP 语境）")
    h2(doc, "11.1 CR# 生成与关联字段")
    S.add_table(
        doc,
        ["字段", "来源"],
        [
            ["cr_id", "ServiceNow 变更工单号"],
            ["trigger_alert", "告警 ID / 时间戳"],
            ["root_cause", "Analysis agent doc_id 证据"],
            ["metric_source", "原始监控指标源 + 时间戳"],
            ["approval", "双人四眼记录（技术+业务/安全）"],
            ["trace_id", "AgentLoop Trace"],
        ],
        widths_cm=[5.0, 11.0],
    )
    S.para(doc, "每条建议动作生成 CR#，关联原始监控时间戳 + 指标源；证据卡须可回溯，否则可追溯链条在证据层断裂。")
    h2(doc, "11.2 审计留存与导出")
    S.para(doc, "ActionTrail 等价（阿里云操作审计）+ AgentLoop Trace 双写，不可篡改；导出 CSV / 客户 QA 指定格式供 GxP 审计。保留期建议对齐行业通行审计周期，需客户 QA 确认后写入 SOW（本期不自行给定数值）。")
    h2(doc, "11.3 CSV / IQ-OQ 框架模板索引")
    S.para(doc, "IQ 模板=环境/组件安装确认表；OQ 模板=功能验证用例（对齐 D01–D18）。仅出框架，GxP 签字由客户 QA/CSV 主导。")
    h2(doc, "11.4 数据驻留与最小权限")
    S.para(doc, "RWD 库仅 SELECT，列入最小权限清单（§9.3）；任何写路径零授权。")

    # ---------- 7 待确认 ----------
    h1(doc, "7. 待确认与验收边界")
    for t in [
        "首批告警场景与 SOP（D15–D18 / R-003）待与 Lilly 确认后固化到 recovery-runbook.md。",
        "准确率阈值可协商性、文档版权/保密限制（R-002 接口就绪后联动 D01）。",
        "AAD 最终组名与资源组命名、SessionPolicy 时长（当前仿真映射 lilly-finops/ops/audit）。",
        "审批 SLA、IM 值守渠道与告警卡片样式。",
        "审计日志保留期（需客户 QA 确认后写入 SOW，本期不自行给定）。",
        "未确认场景（R-003）不纳入本期；R-002 未就绪期间 Mock 双轨联调，11/20 硬闸门后转 live 复测。",
    ]:
        S.bullet(doc, t)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    doc.save(OUT)
    print("saved:", OUT)


if __name__ == "__main__":
    main()
