---
name: pcs-sow
---

# 云迁移 SOW 生成（pcs-sow）

| 字段 | 值 |
|---|---|
| **description** | 云迁移 SOW（工作说明书）生成 - 触发条件：已有 Fact Sheet，需要产出标准 14 章工作说明书（范围/交付物/里程碑/验收/付款等）用于客户签约前确认时触发；完成判据：14 章节全部产出，每章含 `key_points` 与 `open_items`（待确认项）。不负责报价金额计算（`pcs-quotation`），不负责 Landing Zone 专属 SOW（见 `pcs-sow-lz`，LZ 项目用那个，不用本 skill）。 |
| **风险等级** | 低风险写（生成合同前置文档，不是正式合同，不触达客户系统） |
| **输入参数** | `facts`（Fact Sheet 结构化对象，必填，来自 `pcs-factsheet` 输出） |
| **依赖工具** | aicc.execute_skill |
| **版本** | 2026-10-29.001 |

对应 AICC 后端内置能力 `Generate-SOW`。
对应「云迁移Agent构建计划与排期-V1.xlsx」Skill 清单中的 **SOW 生成**（项目启动阶段，刘金龙负责，
输入=项目信息+评估，输出=SOW，模板=SOW 模板）——该表里的"项目信息+评估"即本 skill 的 `facts` 输入，
来自 `pcs-factsheet` 的产出。

## 触发条件 / 完成判据

- 触发：`facts` 已就位，用户要求出 SOW / 工作说明书 / 签约前文档。
- 完成：标准 14 章全部有内容（项目背景/项目范围/交付物清单/假设与前提/工作说明/里程碑计划/
  双方责任/变更管理/验收标准/付款条款/知识产权/保密/违约责任/其它条款），且 `open_items` 汇总清楚。

## 判断逻辑（正文）

1. **输入完整性检查**：`facts` 是否存在。
   - 交互模式：缺失时提示先跑 `pcs-factsheet` 或让用户直接提供 Fact Sheet 内容。
   - 无头模式：若上游刚产出过 `pcs-factsheet` 的输出，直接取用（调工具取数）；若完全没有，
     **终止并升级**（SOW 没有 Fact Sheet 作为依据没有意义，不能靠猜测生成合同前置文档）。
2. **调用依赖工具**：`aicc.execute_skill("Generate-SOW", {"facts": facts})`。
3. **降级判定**：`llm_used=false` 时 14 章内容为 mock 占位，**不可直接给客户**，`confidence` 记为低，
   `suggested_action` = "人工按 `facts` 内容逐章改写，尤其是第 2 章项目范围和第 9 章验收标准"。
   - `aicc.execute_skill` **不可达**（本机默认状态）：改走本地链路，不等待、不重试：
     1. 以 `~/.hermes/skills/mig-std/mig-sow-generator/templates/SOW模板.md` 的 14 章骨架为唯一出处，
        按 `facts` 逐章写 `key_points`（3-5 条）与 `open_items`；章节结构不复制、不并章；
     2. 先产出各章二级标题 + 要点，确认后再展开正文，不要一次写满 14 章全文；
     3. `~/.hermes/skills/mig-std/mig-sow-generator/scripts/build_docx.py <SOW.md> -o <SOW.docx>`
        渲染成 docx（黑灰版式、禁蓝，符合投标口径）；
     4. `confidence` = 低，`suggested_action` 写明「本地生成，需人工复核后交付」。
     红线不变：不虚构人名/角色/证书/案例（废标风险）；未核实数字写「待确认」。
   - `aicc.execute_skill` **不可达**（本机默认状态）：改走本地链路，不等待、不重试：
     1. 以 `~/.hermes/skills/mig-std/mig-sow-generator/templates/SOW模板.md` 的 14 章骨架为唯一出处，
        按 `facts` 逐章写 `key_points`（3-5 条）与 `open_items`；章节结构不复制、不并章；
     2. 先产出各章二级标题 + 要点，确认后再展开正文，不要一次写满 14 章全文；
     3. `~/.hermes/skills/mig-std/mig-sow-generator/scripts/build_docx.py <SOW.md> -o <SOW.docx>`
        渲染成 docx（黑灰版式、禁蓝，符合投标口径）；
     4. `confidence` = 低，`suggested_action` 写明「本地生成，需人工复核后交付」。
     红线不变：不虚构人名/角色/证书/案例（废标风险）；未核实数字写「待确认」。
4. **open_items 处理**：无论是否降级，每章的 `open_items` 都要原样保留并汇总到结构化输出顶层，
   方便后续走审批/飞书通知（如「云迁移Agent构建计划与排期-V1.xlsx」系统提示词里提到的"关键产出与
   审批节点通过飞书通知对应负责人"，具体通知机制不在本 skill 边界内）。

## 输出双形态

**结构化 JSON**：

```json
{
  "conclusion": "SOW 14 章已生成，共 N 个待确认项",
  "confidence": "高 | 低",
  "suggested_action": "可进入客户确认环节 | 需人工改写后再给客户",
  "escalation_reason": null,
  "chapters": [{"title": "...", "key_points": [], "open_items": []}],
  "open_items_summary": []
}
```

**人类可读**：AICC 后端自动生成的 DOCX（`document.download_url`）。

## 升级契约

- **触发条件**：`facts` 完全缺失且无头模式不可反问；或 `aicc.execute_skill` 工具不可达。
- **升级打包**：
  - 已排除：是否已检查过上游 `pcs-factsheet` 是否已执行过；
  - 剩余假设：若走了降级，哪几章是纯模板占位、哪几章是基于 `facts` 真实生成；
  - 建议先看哪里：`open_items_summary`，这是客户最可能卡住的点。
- **组合语义**：被 `pcs-presales-orch` 调用时，若 `pcs-factsheet` 已升级（无输出），
  本 skill 应直接跳过执行并把升级原因标记为"上游 pcs-factsheet 未产出"，不重复升级一次空转。
