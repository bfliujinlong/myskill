---
name: ontology-governance
description: >-
  给 agent 高危产出加人批闸门与全链路审计时激活。对齐 Palantir 的轻量本体治理层。
version: 2026-11-01.001
status: active
allowed-tools: Read, Write, Bash
---

# 轻量行业本体治理层（Plan B，非 Palantir Foundry）

> 定位：team-agent-binding 管「岗位能不能调某 skill/MCP」(静态白名单、最小授权)。
> 本 skill 管「调了之后是否需人批才落盘」(运行时治理)。两者正交互补, 不冲突。

## 0. 何时用
- 要給 agent 的高危产出(报价 / SOW / 割接方案)加人批闸门
- 要全链路审计:谁 / 何时 / 基于什么对象 / 做了什么
- 想引入 Palantir 式「对象视图 + 受控动作 + 人在环」但不上重型底座

## 1. 设计四要素(对齐 Palantir, 单人轻量化)
1. **对象模型**:业务实体建成带边对象(SalesOpp→MigrationProject→Quote/SOW/CutoverPlan→Risk)。
   agent 推理读对象关联, 不读 skill 列表。
2. **受控动作**:每个 skill 概念升级成 Action, 带 `human_approval` 字段。
   required = 必须人批才落盘; none = 可直接落盘(只读/记录类)。
3. **临时 subject**:任务来才 spawn reasoning subject, agent 无人格、不常驻; 只许读对象 + propose Action。
4. **审计 lineage**:每次 spawn/propose/approve/reject 写一条带 sha256 短哈希记录, 全链路可追溯。

## 2. 动作分级(默认策略)
| 动作 | 输入→输出 | human_approval | 说明 |
|---|---|---|---|
| GenerateQuote | MigrationProject→Quote | required | 对外报价, 强把关 |
| GenerateSOW | Quote→SOW | required | 基于已批报价, 再独立人批 |
| DraftCutoverPlan | MigrationProject→CutoverPlan | required | 割接=生产变更, 最强把关 |
| RecordRisk | MigrationProject→Risk | none | 记录类, 免批 |
| Approve | Quote/SOW/CutoverPlan→approved | none | 该动作本身就是"人批"这一行为 |

## 3. 落地实现(已实测跑通, 零依赖零费用)
脚本与本 SKILL.md 同目录 scripts/ 下:
- scripts/ontology.yaml — 对象类型 / 受控动作 / 人类角色(单一事实源)
- scripts/actions.py — 零依赖运行时:对象存储(jsonl) + 动作闸门 + 审计(jsonl)
- scripts/demo_e2e.py — QY-DubaiFintech 真实数据跑通 起草→人批→落盘→审计
运行时数据落在 ~/.hermes/planb-ontology/store/(与 skill 代码分离, 不污染 skill 本身)

跑法:
```
cd ~/.hermes/skills/ai-agent/ontology-governance/scripts
python3 demo_e2e.py                 # 内置 QY-DubaiFintech 示例, 全链路
python3 demo_e2e.py --reset         # 清空 store 重跑
python3 demo_e2e.py --proj X --scope "76 EC2" --total 385000  # 换项目
```

## 4. Pitfalls(构建本体运行时)
- 零依赖优先:pyyaml 在部分 venv 缺失 → 运行时 try import yaml, 失败回退内嵌 spec 字典, 保证标准库可跑。
- 先改内存再落盘:update_state 必须先把所有对象读进内存、改内存里的对象、再整体重写 jsonl, 否则重写文件用的是旧快照, 落盘仍是旧 state(draft 不翻转、show() 与磁盘不一致)。
- 写入分工:propose() 只走审计+闸门(对象停 draft), 对象本体真正写入用 save_object(); 别把 propose 当通用写入器。
- 代码与数据分离:运行时 store 必须落在 skill 目录之外(如 ~/.hermes/planb-ontology/store), 否则 skill 自包含/进版本库时会把 demo 垃圾带进去, 或被误 rm 清掉真实状态。
- 固化要收代码:把 skill 收进正式目录时, 把运行时脚本复制进 skill 的 scripts/ 后, 立即删掉原松散目录里的副本——两份并存会漂移、混淆, 下次不知改哪份。
- demo 可参数化:验证脚本带 --proj/--scope/--total/--reset 等 CLI 参数, 别把示例项目数据写死; 否则 skill 退化成一次性脚本, 换个真实项目就跑不了。
- 并发:jsonl 当前无锁, 单机单进程 demo 级; 生产化需加写锁 + schema 校验 + MCP→对象 ingest 适配层。

## 5. 与 team-agent-binding 的关系
白名单决定 agent *能不能调* skill; 本层决定调了之后 *是否需人批落盘*。
先加载 team-agent-binding 定绑定, 再按本 skill 挂治理闸门。
