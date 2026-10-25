---
name: document-library-ingest
description: "批量文档入库：用户一次性丢来多份 xlsx/docx（调研表、LLD、交付物、checklist 等），提取全文/结构生成索引、归档到统一目录、把清单写进 memory，供后续按需引用产出方案/架构图/报价。"
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [文档入库, 知识库, xlsx, docx, 索引, 迁移, landing-zone, 资料]
    related_skills: [solution-delivery, ai-demo-builder, roles-database, roles-bigdata]
---

# 文档资料库入库（Document Library Ingest）

用户经常一次性发来**一批文档**（云迁移调研表、LLD 设计、交付物、checklist、能力矩阵等），要求"存好，后续按这些给我产出内容/文件"。本 skill 把这批文档变成**可检索、可引用的本地资料库**。

## When to Use
- 用户发来 ≥2 份 xlsx/docx，且说"存起来/后续要用/按这个输出"
- 用户在做售前/迁移/方案，需要把客户或历史材料归档为知识库
- 后续要用这些素材画架构图、做报价、写方案、答客户问题

## 工作流（4 步，全部本地、零成本）
1. **依赖检查**：`openpyxl` + `python-docx`。缺则 `pip3 install --quiet openpyxl python-docx`。
2. **归档**：建 `~/cloud-docs/`（或用户指定目录），把文档复制进去（保留原名防混淆）。
3. **提取索引**：跑 `templates/extract_docs.py <目录>`，生成 `_INDEX.md`（每份文档的 sheet/表头/正文/表格摘要）。脚本只取前若干行看结构，不会爆上下文。
4. **写 memory**：把"资料库路径 + 文档清单（文件名→用途）"写入 memory（一条 entry 即可），后续会话直接检索 `_INDEX.md` 引用真实素材，不从零编。

## 关键踩坑
- **xlsx 空壳**：很多 LZ 调研表/计划表前几行只有表头（如"LZ模块"），数据在更后面。索引取前 8 行看结构即可，别误判为"空文档"。
- **大 docx（>20MB 含图）**：python-docx 只读文字层，图片不提取；正文足够做索引。别用 vision 逐页扫，贵且没必要。
- **docx 表格**：`Document.tables` 遍历 rows/cells，每张表取前 5 行看结构。
- **memory 额度**：清单用"文件名→用途"一行式，不要贴全文（token 宝贵，且 _INDEX.md 已存全文）。
- **重复入库**：先看 `~/cloud-docs/` 是否已有同名/同主题，避免建多份。
- **权限**：文档可能含客户敏感信息，存实例本地即可，不要外传/上传。

## 后续引用方式
用户说"画架构图/做报价/出方案"时：先 `read_file ~/cloud-docs/_INDEX.md` 定位相关文档，再用 `extract_docs.py` 已提取的结构或 `read_file` 原文件具体段落，结合 `solution-delivery` / `roles-*` skill 产出真实文件。

## 与 solution-delivery / ai-demo-builder 的关系
本 skill 负责"**资料进得来**"，那两个 skill 负责"**产物出得去**"。三者串成：入库 → 检索 → 产出 .drawio/.html/.md 交付物。
