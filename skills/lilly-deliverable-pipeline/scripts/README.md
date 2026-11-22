# scripts 使用说明

## gen_lld_v11.py
LLD V1.1 DOCX 生成器的可复用种子。当前为 Lilly AIOps 定制版，含全部章节内容。

**依赖**：`_style.py`（共享样式层，位于项目 `generators/` 目录）。运行前把本脚本放到 `generators/` 目录，或调整 `sys.path.insert` 指向 `_style.py` 所在目录。

**运行**：
```bash
cd /home/ubuntu/客户项目/Lilly_AIOps/02_项目方案/codex/AgentCore_Scenario_Design/generators
python3 gen_lld_v11.py
```

**关键**：`_style.BASE` 指向已过时的旧目录，脚本内用显式 `BASE` 覆盖，勿改回 `S.BASE/S.OUT_DIR`。

**复用到其他交付物**：复用 `S.new_doc()/set_doc_fonts()/cover()/para()/bullet()/add_table()`，保持黑灰禁蓝 + w:eastAsia + 内置标题样式；只替换章节内容，输出路径显式指定。
