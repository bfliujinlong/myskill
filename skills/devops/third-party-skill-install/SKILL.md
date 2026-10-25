---
name: third-party-skill-install
description: Use when 安装 GitHub 第三方 skill：克隆数据盘、装依赖、验证、软链三处。
version: 0.1.0
author: Hermes Agent
license: MIT
category: devops
tags: [skill安装, github, 数据盘, 软链]
---

# 第三方 GitHub Skill 安装

## When to Use
- 用户丢来 GitHub 仓库链接说「装好这个 skill / 安装 / 部署这套工具」
- 安装对象是 AI agent 生态的 skill 包、CLI 工具链、agent workspace（career-ops、consulting-report-forge、fde-toolkit 类）
- 需要把已装仓库接入 Hermes / Claude Code / Codex 三个 Agent
- 反触发：仓库只是业务代码要 review/跑测试（走 github / systematic-debugging）；纯 Hermes 自配置（走 hermes-config-tuning）

用户说「装好这个：<GitHub URL>」时的标准流程。铁律：**克隆成功≠可用，必须真实验证**（doctor/冒烟测试跑通）才向用户报「装好」。

## 流程

1. **摸底**：`curl -s https://api.github.com/repos/<owner>/<repo>` 看语言/大小/最近推送；README 里 grep 安装章节（`grep -iE "^## (Quick|Install|Getting)" README.md`）。
2. **克隆到数据盘**：`git clone --depth 1 <url> /data/skills-src/<name>`。系统盘只有 45G，node_modules/浏览器缓存/venv 一律不进系统盘。
3. **装依赖**（按仓库语言分流）：
   - Node：有 lockfile 用 `npm ci`，否则 `npm install`；大安装走 terminal background + notify。需要 PDF/截图能力的补 `npx playwright install chromium`（ARM64 有对应构建，可直接装）。
   - Python：看 README 要求的版本，**用 uv 建指定版本 venv**（`uv venv --python 3.12 .venv` → `uv pip install -e '.[extras]'`）——本机 `python3` 可能是 3.14，直接用会装不上或导入失败；venv 内命令用 `.venv/bin/<cmd>` 调用，不依赖 activate。
   - 两者都走 terminal background + notify，完成后**单独确认关键产物存在**（`ls node_modules | wc -l`、`ls ~/.cache/ms-playwright/`、`.venv/bin/<cmd> --help`），别只看 exit code。
4. **个性化配置**：把模板配置（profile/example 文件）填成用户真实数据（见下「配置来源」），绝不保留模板默认值交付。
5. **验证**：优先找**无需凭证的官方 demo/自检命令**（如 `<tool>-demo`、`npm run doctor`、最小 init 命令）——它能在不配模型/云凭证的前提下跑通核心链路，是「装好了」的最强证据；跑通后把真实输出（任务数/通过项）报给用户。全绿（或仅剩已如实说明的可选组件警告）才算装好。
   需要云凭证/付费账号才能跑的部分（Vertex/gcloud、Docker、付费 API）先**不阻塞交付**：说明差什么、装好无凭证部分的能力边界，让用户决定是否继续。
6. **软链三处**（单一真源，改一处三端生效）：
   ```bash
   ln -sfn /data/skills-src/<name> ~/.hermes/skills/<name>
   ln -sfn /data/skills-src/<name> ~/.claude/skills/<name>
   ln -sfn /data/skills-src/<name> ~/.codex/skills/<name>
   ```
7. **交付话术**：报「安装位置 + 验证结果（doctor 输出摘要）+ 一句话怎么用」，并主动给一个可立即试跑的最小任务让用户验收。

## Pitfalls

- Playwright 类工具在无系统 Chrome 的 ARM 主机上会找 `/opt/google/chrome/chrome` 报错 → 设 `CHROME_CHANNEL=chromium` 用 playwright 自带 chromium，并写进 `~/.bashrc` 持久化（consulting-report-forge 实测）。
- 仓库自带多 Agent 的 skills 子目录（.agents/.claude/.grok/.kimi/...）时，软链整个仓库根会让 skills_list 出现多份重复条目——无害噪音；agent-workspace 类仓库（要求在目录内开 AI CLI，如 career-ops）必须链根，纯 skill 仓库可只链 canonical 子目录。
- doctor 剩 1 个可选组件警告（如外部 MCP 未配）可接受：确认主链路（评估/生成/PDF）不受影响、如实告知用户，不要卡住交付。
- npm postinstall 可能静默失败（下载浏览器/字体）：安装后单独确认关键产物存在（`ls node_modules | wc -l`、`ls ~/.cache/ms-playwright/`），别只看 exit code。
- 密钥/token 类配置文件一律 chmod 600、内容不进聊天；用户丢来的 key 文件先移到安全位置（如 ~/.bailian/）再引用。
- 背景安装完成通知（INTERNAL NOTIFICATION）到达时安装可能早已验证完毕——只需一句话确认收尾，不重跑流程。
- **不要把 `mv`/`rm -rf` 与重型安装、网络探活拼成一条大命令**：含目录移动/删除的命令会触发确认护栏，用户不在时整条超时作废，连带后面本可成功的安装一起丢掉。拆成「迁移→安装→探活」三个小步，每步独立可重试。
- Python 仓库的 extras（`.[render,bridge]` 类）常拉起 litellm/浏览器等重依赖，先装核心包 `-e .` 验证主链路，确认用户真要那些能力再补 extras。

## 配置来源（个性化不编造）

- 简历/履历类字段：从 `~/personal/resume/*.docx` 用 python zipfile 读 `word/document.xml`，正则提取 `<w:t>` 文本按段落转 md（career-ops cv.md 即此法生成，doctor 验证段落识别数）。
- 用户画像/目标岗位/薪酬锚点：取 memory 中真实数据（如 AC-MIG $350/人天）；未核实的数字标「待核实」，不硬填。
- 装完后把「工具链入口 + 已个性化文件清单」补进对应领域 skill（如求职类 → resume-optimizer），让下次会话不用重新摸索。
