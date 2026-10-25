---
name: tender-docx-assembly
description: "组装中文投标/技术标 docx：多源素材抽取、黑灰版式、python-docx 插图坑、matplotlib 图表。"
version: 0.2.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [投标, 技术标, docx, 售前, 文档组装, python-docx, matplotlib]
    related_skills: [presales-architect, solution-delivery, spreadsheet-delivery]
support_files:
  - scripts/compress_tender_docx.py: 压缩成稿 docx 到 <20MB（重采样 word/media 图片），交付前必跑
  - references/pm-templates.md: 15个免费PM模板（替代Template22付费版）的openpyxl坑和代码示例
---

# 投标 / 技术标 docx 组装（Tender Docx Assembly）

## 用户铁律（来自 jinlongliu，多次强调 — 必须内嵌）
- **不改原格式**：输出模板格式要和客户/源文件「之前一致」，不要另起炉灶；用 `python-docx` 时沿用源 docx 的字体/标题层级/表格样式（读 `styles.xml` 确认宋体/雅黑/黑灰）。
- **无 AI 感**：不出现蓝色等 AI 感配色、正文禁写「AI/人工智能/大模型」；进一步——「格式不要 AI 感觉那么强」= 去模板腔（删过度排比 bullet、绝对化承诺如「零降级/平迁无需重构」、教科书式小标题、高频「端到端/闭环/基线」），图表去网格线/硬边框改浅灰手绘感。
- **只更新要求的部分、格式统一**：用户说「素材你不用管，只需要更新要求你的部分格式要统一」「让你查的是这个文件」→ 拿**客户原 docx** 精确落位改（如只换偏离表那一格），不要整篇重建；重建只在「只有素材无原稿」时走。拿不到原文件时第一时间问用户传（飞书/dsh/分卷），不要凭空重写然后假装对齐。
- 大文件通道：Telegram bot 限 20MB，>20MB 被拦（报 "Maximum: 20 MB"）。绕法：① 飞书通道（100MB）直接发；② dsh 网页上传（走 Cloudflare 隧道，不限 20MB，但需公网域名，域名在 CF 控制台 Tunnels 拿，本地读不到）；③ 本地 `split -b 15m file.docx part_` 分卷逐个发再 `cat` 合并。收到后先全盘搜文件名确认落盘（飞书文件在 `~/.hermes/cache/documents/`）。

## 标准流程
1. **素材抽取**（zip/docx/pdf 混源）
   - docx 文本：`zipfile` 读 `word/document.xml`，`re.sub(r'<w:p[ >]', '\n')` + 去标签 + 去 `w14:paraId` + 合并空行。
   - PDF：`pip install pypdf` 后 `pypdf.PdfReader(fn).pages` 抽文本（无 pypdf 时 `pdftotext -layout` 兜底）。
   - zip：`ZipFile.extractall(dst)` 后遍历。
   - JWT 类 token（如 cloudflared token）：`base64` 解 payload 三段拿 TunnelID，但**命名隧道公网域名在 Cloudflare 云端，本地读不到**。
2. **起草章节**：Azure gpt-5-mini（delegate）起草长文；**坑**：该模型经某些通道会把 token 烧进 reasoning 致 content 空或子任务挂起（实测 252s 无响应）→ 兜底改用主模型 hy3 在 `execute_code` 里 `write_file` 直接写，格式与素材一致即可。无论谁起草，AI 只产内容，版式/配色必须脚本控制。
3. **画图**（matplotlib，黑灰无蓝）：`FancyBboxPatch`+`FancyArrowPatch` 手绘拓扑/流程/甘特/决策树；字体 `Microsoft YaHei`→`SimHei`→`DejaVu Sans` 回退；`savefig(dpi=150, bbox_inches='tight')`。
4. **组装 docx**（python-docx）：宋体正文 / 微软雅黑标题，`RGBColor(0x22,0x22,0x22)` 近黑；表格 `Table Grid` 样式。

### 附件 4-7 整理子流程（青少年科创 / 雏鹰杯 / 青创赛，2026-09-25 验证）
- 参考：`references/youth-science-attachment-rules.md`（提取规则/铁律/典型输出结构/已知坑）
- 提取：`zipfile`/`pypdf`/`unrar` → `/tmp/` 备查 → 记录真实字段（项目名/日期/传感器/结论）；RAR 无工具时直接告知，勿猜测
- 铁律：不编人员/证书，签名栏留空并标注“请签字盖章”；教师仅写“指导教师/访谈对象”待补签；项目名/实验日期/传感器型号/距离阈值必须源自已提取文本
- 输出：`python-docx`，`RGBColor(30,32,35)` 近黑，无蓝，宋体/微软雅黑，`FancyBboxPatch` 手绘风；禁高频 AI 词见 `references/deai-text-rewrite.md`
- 委托：内容起草可 `delegate_task`（Azure `gpt-4o` `azure-foundry`），格式/配色必须脚本控制；已验证输出 `/home/ubuntu/雏鹰杯_附件4-7_整理.docx`
- 交付：`docx`，>20MB 先 `compress_tender_docx.py`（q72）；大文件优先飞书/dsh

## Feishu 文档操作限制（必记）

### MCP 工具限制
飞书 MCP 工具（`fetch-doc`/`update-doc`）**仅支持 docx/wiki 文档，不支持电子表格（Spreadsheet）**。
- 调用 `fetch-doc` 传 sheet token → 返回 `[VALIDATION:1005] Unsupported document type: Spreadsheet`
- **绕过方案**：让用户导出 Excel 发我（飞书 → 右上角菜单 → 导出 → Excel），本地用 `openpyxl`/`pandas` 处理后生成报告
- 电子表格的浏览器自动化也极不稳定（LuckySheet 对象难加载）

### 飞书文件下载（已验证）
飞书 `drive/v1/files/{token}/download` 可下载文件（需应用有 `drive:drive` 或 `drive:drive:readonly` 权限）。
```python
# 1. 获取 tenant_access_token
r = httpx.post('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
    json={'app_id': creds['app_id'], 'app_secret': creds['app_secret']})
token = r.json()['tenant_access_token']

# 2. 下载文件
r2 = httpx.get(f'https://open.feishu.cn/open-apis/drive/v1/files/{file_token}/download',
    headers={'Authorization': f'Bearer {token}'})
with open('/tmp/file.docx', 'wb') as f:
    f.write(r2.content)
```

### 飞书应用权限坑
- 应用身份权限（`drive:drive:readonly`、`wiki:wiki:readonly` 等）勾选后必须**创建版本+发布**才生效，只勾选不发布=持续报 `99991672 Access denied`
- 应用需被加为目标文档/空间的**协作者**才有权限（应用身份 ≠ 用户身份）
- 权限参考：`search:docs:read`（搜索）、`docx:document:readonly`（读文档）、`drive:drive:readonly`（下载文件）
- ❌ 不要在 md 解析里用「正文含『附图 X-X』就插图」的正则——图标题文字易与正文挤同行，path 取到整段 → `FileNotFoundError` 静默失败，只插进部分图。
- ✅ 插图位置放**独立一行** `!IMG[/绝对路径.png]`，解析器遇 `line.strip().startswith('!IMG[')` 即 `add_image(doc, path)`，`path=line.strip()[5:-1]`。
- ✅ 更稳：不靠 md 解析插图，在 `__main__` 按章节硬编码插图列表（读该章 md 后 `for im in imgs: add_image(doc,im)`），图落章节末也完全可接受。
- ✅ 验证：`zipfile.ZipFile(out).namelist()` 中 `word/media/` 数量 == 预期图数；`doc.inline_shapes` 会重复计数，以 media 目录为准。

## 投标审查→修订闭环（V12 审查报告模式）
收「审查与优化建议」文档时按 P0→P1→P2 改：
- P0：清【填写】占位符、删重复段、补必填图（拓扑/时序表/案例）、删内部备注（「建议drawio」「须由团队补充」「禁止虚构」）、填日期。
- P1：补甘特图/决策树/风险五列/监控四列、增值服务扩项、偏离表逐条补全（S-01~S-04 + 运维锚点）。
- P2：量化价值句、流程图可视化、行业基准示例（标「行业基准参考」非承诺）。
- 最佳：拿到审查对象原 docx 精确落位改；只有素材无原稿则走「重建优化版」。

## 原 docx 精确落位修改（不重建整篇）
用户给的是成稿（如 44.8MB 的 `泉峰技术标框架_v19.docx`），只要改其中一章/一表 → **必须 in-place 改，保留封面/公章/业绩页/其他章**：
```python
from docx import Document
d=Document(src)
# 定位目标表: 按表头关键字 + 列数
target=None
for t in d.tables:
    hdr=' '.join(c.text for c in t.rows[0].cells)
    if '偏离说明' in hdr and len(t.columns)==4:
        target=t; break
# 清空数据行(保留表头), 填入新行
while len(target.rows)>1:
    target._tbl.remove(target.rows[1]._tr)
for seq,req,resp,dev in rows:
    new=target.add_row()
    for j,c in enumerate(new.cells): c.text=[str(seq),req,resp,dev][j]
d.save(out)
```
- ⚠️ **坑**：改完用 `d.tables.index(target)` 查行数会 `ValueError`（对象引用在删行后失效）。要验证就重新 `Document(out)` 打开后再数。
- 偏离表扩行技巧：招标审查要求「全量索引」→ 把 DTS 提额≥12、NACOS/MSE 定案、SQS 18 队列改造、OMS 1.2TB、25 类×4 区域、G0-G7 工期等所有硬约束都入表（20–28 行），每行锚定条款号（SOW 1.1 / S-01 / 招标运维 2.5 等）+ 响应页码；SLA 分档写准（To Business≥99.9% / To Customer IoT≥99.95% / 基础架构≥99.5%，笼统写低=负偏离）；S-01 VPN 双隧道措辞显式声明「招标既定长期生产方案、非割接回退手段」消除负偏离风险。

## PPTX 合并（XML/zipfile 级别，已验证）

### 场景
将孙玉洲 PPTX（5案例/10页）合并到 E3 主案例库（46页）→ 最终51-56页。

### 合并脚本（已验证）
脚本路径：`/home/ubuntu/merge_pptx.py`、`/home/ubuntu/merge_pptx2.py`、`/home/ubuntu/merge_sun_into_v13.py`

**核心流程**：
1. 用 `zipfile` 读取两个 pptx 内部的 `ppt/slides/slide*.xml`
2. 计算源 PPTX 的 slide rId 和目标 PPTX 的最大 rId，避免冲突
3. 将源 slide XML 注入目标 zip 的 `ppt/slides/` 目录
4. 更新 `[Content_Types].xml` 注册新 slide
5. 更新 `ppt/_rels/presentation.xml.rels` 添加 slide relationship
6. 更新 `ppt/presentation.xml` 的 `<p:sldIdLst>` 插入新 sldId
7. 媒体文件（图片）重命名（`image{N}` 递增）避免冲突

**关键坑**：
- rId 必须唯一且递增，否则 PPTX 损坏
- slide 插入位置由 `sldIdLst` 的 index 决定（`insert(pos, elem)`）
- 合并后总页数 = 原页数 + 新增页数，尾页（如"懂云更懂服务"）需保留在最后
- 验证：`pymupdf.open(merged)` 能正常读取且页数正确

### PPTX 素材提取
- **PyMuPDF 可读取 PPTX 文本**（`pymupdf.open(pptx)` → `page.get_text()`）
- 但只能提取文本，**不能保留格式/图片**用于合并
- 合并必须走 XML/zipfile 级别操作

## 会议纪要 docx 生成（从模板克隆）

### 场景
客户发来会议纪要模板（如爱普生会议纪要 .docx），要求按模板格式填入新会议内容。

### 流程
1. 下载模板：飞书 `drive/v1/files/{token}/download` → 保存到 `/tmp/`
2. 读取结构：`python-docx` 读取 paragraphs + tables，分析模板布局
3. 定位单元格：按关键字（如"出席人员"、"会议讨论内容"、"新动作条目"）定位 table.row/col
4. 清空+填入：`cell.text = ''` 清空后填入新内容
5. 留空处理：用户要求"参会人留空"→ 填入 `'\n'` 保持单元格存在但视觉空白
6. 生成新文档：`doc.save('/tmp/output.docx')`
7. 发送：Telegram Bot API `sendDocument` 直接发送文件

### 模板结构示例（安畅会议纪要）
```
Table 0: 会议基本信息
  R0: 开始时间 | 14:00 | 会议日期 | 主持人 | 主持人
  R1: 结束时间 | 15:50 | 地点   | 记录人 | 记录人
  R2: 出席人员 | 客户+安畅 | ...
  R3: 会议讨论内容 | ...
  R4: 1. 议题1 | ...
  R5: 2. 议题2 | ...
  R6: 3. 议题3 | ...
  R7: 本次会议新动作条目 | ... | 负责人 | 时限

Table 1: 动作项明细
  R0: 1 | 动作描述 | 负责人 | 时限
  R1: 2 | ...
  R2: 3 | ...
```

### 关键坑
- 模板中单元格可能跨列合并，`len(table.columns)` ≠ 实际列数
- 定位"出席人员"单元格后，`cells[1]` 可能跨3列，直接赋值会覆盖合并单元格 → 应只赋值左上角单元格
- 清空行用 `cell.text = ''`，保留表头行不动
- 新增行用 `table.add_row()` 或定位已有空行填入

## Feishu 文档操作限制（必记）
**场景**：客户发来单个案例 PPTX（如 `SmartCare-案例集-孙玉洲.pptx`），需合并到主案例库（`SmartCare案例集-完整版.pptx`）或主控模板（`SmartCare案例集-合并版.pptx`）。

**文件结构习惯（安畅 SmartCare 案例库）**：
| 文件 | 说明 |
|------|------|
| `SmartCare案例集-完整版.pptx` | 主案例库，北区+东1+东2 三组分组合并 |
| `SmartCare案例集-合并版.pptx` | 模板框架，每页标题+单行占位文字 |
| `SmartCare-案例集-{姓名}.pptx` | 单人案例集，含多个子案例 |

**合并流程**：
1. 提取源 PPTX 每页文本：`pymupdf.open(pptx)` → `page.get_text()`，按案例名切分页范围
2. 提取目标 MS 的页数和结构（完整版通常 50 页，每案例 5~10 页）
3. 确认目标 MS 中是否已有该案例（搜索关键字如「拜耳」「新城」等）
4. 如已有 → 替换对应页；如无 → 追加到末尾
5. 如需追加「新章节」（如「最后那个章节」）→ 找最后一页位置，在其**前或后**插入新内容
6. 输出前确认边界，避免覆盖MS的目录页/封面

**关键坑**：
- PPTX 每页 `.get_text()` 可能跨页合并 → 用案例关键字边界判断页归属
- 合并版是模板（125页）不适合直接追加内容；应合并到完整版（50页）
- 案例人名 ≠ 案例名（如「孙玉洲」是顾问名，真正案例是「拜耳/新城/卡特彼勒/TST/米其林」）

---
## docx 压缩（交付前必做，<20MB 才能聊天发）
`zip` 命令常未安装 → 用 Pillow 重采样 `word/media/*`。**已验证脚本** `scripts/compress_tender_docx.py`（统一转 JPEG q72 + 超大图>2400px 缩边 + 仅在更小才覆盖防膨胀 + 打开校验）。
```bash
python3 scripts/compress_tender_docx.py 泉峰技术标框架_v19.docx   # 输出 _compressed.docx
```
- 实测: 43.69MB → 10.39MB (↓76%)，段落/表格/文本零改动，文档可正常打开（不含 A4 纸级清晰度损失，证书截图肉眼无差）。
- 阈值说明: q72 比 q82 在证书扫描件上体积砍更多且肉眼无损；>2400px 缩边专治巨型证书/架构图撑体积。若清晰度不够可把 72 提到 80、2400 提到 3000。
- 验证：`Document(out)` 能打开且目标表行数正确即 OK；`zipfile` 看 `word/media/` 数 == 原图数。


```python
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.oxml.ns import qn
INK=RGBColor(0x22,0x22,0x22)
def set_cjk(run, font='微软雅黑'):
    run.font.name=font; r=run._element; r.rPr.rFonts.set(qn('w:eastAsia'), font)
def add_heading(doc,t,lv):
    p=doc.add_paragraph(); p.style=doc.styles[f'heading {lv}']
    run=p.add_run(t); run.font.color.rgb=INK; set_cjk(run,'微软雅黑'); run.bold=True
    run.font.size=Pt(16 if lv==1 else 13 if lv==2 else 11)
def add_para(doc,t):
    p=doc.add_paragraph(); run=p.add_run(t); run.font.size=Pt(10.5)
    run.font.color.rgb=INK; set_cjk(run,'宋体')
def add_table(doc,hdr,rows):
    n=len(hdr); tb=doc.add_table(rows=1,cols=n); tb.style='Table Grid'
    for i,h in enumerate(hdr):
        r=tb.rows[0].cells[i].paragraphs[0].add_run(h); r.bold=True
        r.font.size=Pt(9.5); r.font.color.rgb=INK; set_cjk(r,'微软雅黑')
    for row in rows:
        row=list(row)+['']*(n-len(row)); row=row[:n]
        for i in range(n):
            r=tb.add_row().cells[i].paragraphs[0].add_run(str(row[i]))
            r.font.size=Pt(9); r.font.color.rgb=INK; set_cjk(r,'宋体')
def add_image(doc,path,w=6.0):
    p=doc.add_paragraph(); p.add_run().add_picture(path, width=Inches(w))
```

## 去AI感文本改写
收「去除AI感觉」「去AI味」「读起来像人写」类需求时，用正则批量替换法（详见 `references/deai-text-rewrite.md`）。
- 核心规则：删预告式开头（本章将/下面/值得注意的是）、AI高频词（端到端/闭环/赋能/抓手）、绝对化措辞（确保→争取/必须→需要）、冗余助词（XX了）。
- **保留不改**：标题行、纯数据行（IP/端口/版本号/时间节点）、列表标记。
- ⚠️ **坑**：长文档（>200行）改写任务，delegate子任务易超时（实测2次失败：144s/12s均中断）。**正确做法=主进程直接Python脚本跑**，不依赖delegate。
- 脚本模板见 `references/deai-text-rewrite.md`。

## PM Templates（项目管理模板）

投标/交付时常需配套的项目管理模板（Project Charter、RACI、风险登记册、甘特图、状态报告等）。替代 Template22 付费版（$99.99）。

### 快速创建

```python
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from docx.shared import Pt, Inches, Cm, RGBColor

# 颜色定义（黑灰商务风，无蓝色）
C = {'dg': '333333', 'mg': '555555', 'lg': '888888', 'bh': '444444', 'bs': '666666', 'ba': 'EAEAEA', 'ac': 'D4AF37'}
```

### 15 个模板清单

| 序号 | 模板 | 核心列/结构 |
|------|------|-------------|
| 1 | Project Charter | 项目信息、背景、范围、里程碑、干系人、审批 |
| 2 | RACI Matrix | 任务 × 角色矩阵，R/A/C/I 分配 |
| 3 | Risk Register | 风险ID、描述、类别、可能性、影响、等级、应对策略 |
| 4 | Gantt Chart | 任务、负责人、起止日期、工期、完成%、周维度进度条 |
| 5 | Status Report | 进展、下周计划、风险问题 |
| 6 | Issue Tracker | 问题ID、标题、优先级、类型、状态 |
| 7 | Budget Tracker | 类别、预算、实际、剩余、使用率（含SUM公式） |
| 8 | Resource Plan | 角色、人员、投入比例、工时、成本 |
| 9 | Action Plan | 行动项、负责人、优先级、状态、完成% |
| 10 | Change Log | 变更ID、内容、申请人、审批人、影响 |
| 11 | WBS | WBS编码、工作包、工期 |
| 12 | Kanban Board | 待办/进行中/待验证/已完成 四列 |
| 13 | Cost Benefit | 成本项、收益项、ROI公式 |
| 14 | Stakeholder | 干系人、影响力、态度、沟通策略 |
| 15 | Dashboard | KPI卡片 + 里程碑进度 |

### openpyxl 关键坑

#### Alignment 参数验证
```python
# ❌ 错误：horizontal='top' 会 ValueError
Alignment(horizontal='top', vertical='left')  # 报错！

# ✅ 正确：horizontal 和 vertical 取值范围不同
Alignment(horizontal='left', vertical='top')  # horizontal: left/center/right/general/fill/distributed/justify/centerContinuous
                                            # vertical: top/center/bottom/justify/distributed
```

#### Cell Shading（单元格背景色）
```python
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

# ❌ 错误：qn('w:shd') 返回字符串，无 .set() 方法
shd = qn('w:shd')  # AttributeError: 'str' object has no attribute 'set'

# ✅ 正确：用 OxmlElement 创建元素
shd = OxmlElement('w:shd')
shd.set(qn('w:fill'), 'E0E0E0')
shd.set(qn('w:val'), 'clear')
cell._tc.get_or_add_tcPr().append(shd)
```

#### 表格插入到指定段落后
```python
# ❌ 错误：Paragraph 无 _tbl 属性
target_para._tbl.addnext(table._tbl)  # AttributeError

# ✅ 正确：用 _element
target_para._element.addnext(table._tbl)
```

#### 合并单元格顺序
```python
# ❌ 错误：先 merge 再赋值 → MergedCell 只读
ws.merge_cells('A1:B1')
ws['A1'].value = 'x'  # AttributeError: 'MergedCell' object attribute 'value' is read-only

# ✅ 正确：先赋值左上角，再 merge
ws['A1'].value = 'x'
ws.merge_cells('A1:B1')
```

### 中文字体设置

```python
from matplotlib.font_manager import FontProperties

# 使用 Noto Sans CJK（本机已装）
font_prop = FontProperties(fname='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
font_prop_bold = FontProperties(fname='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc')

# 全局设置
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['Noto Sans CJK SC', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
```

### Logo 设计（页眉用）

```python
from matplotlib.patches import FancyBboxPatch

# AC 字母设计 + 安畅网络/SmartCare 品牌
fig, ax = plt.subplots(figsize=(4, 0.9))
box = FancyBboxPatch((0.1, 0.15), 0.55, 0.55, boxstyle="round,pad=0.05",
                     facecolor='#333333', edgecolor='#555555', linewidth=1.5)
ax.add_patch(box)
ax.text(0.375, 0.425, 'A C', ha='center', va='center', fontsize=16,
        fontweight='bold', color='#FFFFFF', fontproperties=font_prop_bold)
ax.text(0.85, 0.55, '安畅网络', fontproperties=font_prop_bold, fontsize=16, color='#333333')
ax.text(2.75, 0.55, 'SmartCare', fontproperties=font_prop_bold, fontsize=12, color='#D4AF37')
```

### 页眉页脚（专业初阶方案必备）

客户要求「显得更专业」「初阶方案」时，加页眉页脚：
- **页眉**：公司 logo（AC字母设计或图片）+ 文档类型（如「详细设计方案」）
- **页脚**：客户名 + 项目名 + 文档类型，居中或左右分布
- **实现**：`section.header.is_linked_to_previous = False` → `header.paragraphs[0].add_run().add_picture(logo, width=Inches(2.0))`；footer同理
- **坑**：matplotlib 中文字体用 `FontProperties(fname='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')`，否则方块乱码
- **坑**：logo 用 `FancyBboxPatch` 画 AC 字母 + 安畅网络/SmartCare 品牌标识，黑灰配色+金色点缀（#D4AF37），无蓝色
- **每页自动重复**：设置 `is_linked_to_previous = False` 后所有页均显示

## 附录内容生成
客户要求「附录加上」时，按方案内容自动生成结构化表格：
- **附录A 资源对比**：源环境→目标环境 IP/端口/网段对照表，含备注列
- **附录B 系统集成清单**：外部系统名 + 集成方式 + 协议/端口 + 迁移注意事项
- **附录C 缩略语**：缩略语 + 全称 + 说明（按方案中出现的专业术语提取）
- **实现**：`doc.add_table(rows=1+len(data), cols=len(headers))` → 表头灰色底纹（`OxmlElement('w:shd')` + `fill='E0E0E0'`）→ 数据行
- **坑**：`target_para._element.addnext(table._tbl)` 把表格插到指定段落后（`Paragraph` 无 `_tbl` 属性，须用 `_element`）
- **坑**：添加表格后段落索引会变，需重新 `find_section()` 定位后续附录

## matplotlib 架构图 → docx 插入
当无 drawio 工具或需快速出图时，用 matplotlib 画架构图再插入 docx：
- **画图**：`FancyBboxPatch` 画服务器/VPC区域，`annotate(arrowprops=...)` 画箭头，黑灰配色无蓝色
- **中文字体**：`FontProperties(fname=NotoSansCJK)` 全局设置，避免方块
- **插入**：`run.add_picture('/tmp/arch.png', width=Inches(6.5))`，`paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER`
- **位置**：找到目标章节段落（如「网络架构」前），`target_para._element.addnext()` 或 `insert_paragraph_before()`
- **图注**：图片下方加居中灰色小字「图1：XXX」
- **验证**：`Document(out)` 打开后检查 `word/media/` 图片数 == 预期
