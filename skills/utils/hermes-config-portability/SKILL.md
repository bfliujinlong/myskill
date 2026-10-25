---
name: hermes-config-portability
description: "Hermes 配置/skill 跨云备份与迁移：git 备份、GitHub 密钥扫描清理、新机重建。"
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [hermes, 备份, 迁移, git, 密钥清理, 跨云, skill]
    related_skills: [overseas-model-hub, multi-cloud, landing-zone-pm]
---

# Hermes 配置与技能可移植性（备份 / 迁移 / 跨云重建）

## When to Use（何时使用）

- 要把 Hermes 的 skills / config 备份到 Git 仓库（换机器、换云、防丢）
- push 到 GitHub 被 **secret scanning 拒绝**（仓库规则拦了历史里的密钥）
- 在新云/新机器上快速重建整套 Hermes 环境
- 用户说「上传到我的仓库 / 之后迁移到其他云可以快速配置」

## 标准工作流

### 1. 初始化仓库（本地）

```bash
cd ~/.hermes
git init -q
git config user.name "<your-name>"
git config user.email "<your-email>"
```

### 2. 先写 .gitignore，排除凭证与缓存（必做，防误传）

```
credentials/
cache/
blocked-scripts/
skills/.hub/
*.db
jobs.json
.executions.db
.env
.env.*
# 可重装二进制工具(Hermes tools/, bin/)含 100MB+ 二进制(chromium/ffmpeg/node/python)
# 一旦 git add 进历史, GitHub 100MB 硬限(GH001)拒收, 连带 skills/mem 全卡死
# 必须用白名单 add, 不能 git add -A
tools/
bin/
*.tmp
*.lock
.gateway_state_*.tmp
.hermes_history
.cloud-docs/
skills/.locks/
skills/.usage.json
```
> 任何含真实 key 的 skill 文件也要加进来（见下方坑 1）。

### 3. 扫描是否误含明文密钥（粗扫）

```bash
grep -rIl -E "BEGIN (RSA|OPENSSH|PRIVATE)|sk-ant-|AIza[0-9A-Za-z_-]{20}" skills/ 2>/dev/null
```
命中若是文档示例（如 `sk-ant-...`、`AIzaSyDxxx...` 占位）可传；**真实 key 必须清除**。

### 4. add + commit

```bash
git add skills/ .gitignore
git commit -q -m "backup: hermes skills for cloud migration portability"
```

### 5. push（推荐用 SSH Deploy Key，无 token 落盘）

**不要**把 classic PAT 写进脚本/remote（明文风险）。改用 GitHub Deploy Key：

```bash
# 本机生成专用 key(无密码)
ssh-keygen -t ed25519 -C "oci-hermes-backup" -f ~/.ssh/github_backup -N ""
# 公钥加到 GitHub 仓库 Settings → Deploy keys(勾 Allow write access)
#   cat ~/.ssh/github_backup.pub
# 写 ~/.ssh/config 指定 github.com 走此 key
#   Host github.com
#     IdentityFile ~/.ssh/github_backup
#     IdentitiesOnly yes
git remote set-url origin git@github.com:<user>/<repo>.git
git push -u origin master
```
> 也可用 API 加 deploy key(免网页): `curl -X POST -H "Authorization: Bearer <PAT>" -H "Accept: application/vnd.github+json" -d '{"title":"oci-hermes-backup","key":"<PUBKEY>","read_only":false}' https://api.github.com/repos/<user>/<repo>/keys`
> Deploy Key 无过期、无账号级权限，cron 自动同步最稳。

**若临时用 classic PAT**（ghp_ 勾 repo）：`git remote set-url origin https://<TOKEN>@github.com/<user>/<repo>.git` → push → 立刻 `git remote set-url origin https://github.com/<user>/<repo>.git` 清痕迹 → GitHub 页面 revoke。token 文件 `chmod 600`，绝不明文贴聊天。

### 6. 被 secret scanning 拦截时的清理（关键）

GitHub 拦的是**整个历史**里的密钥，`git rm` 只清工作区没用。必须用 `git-filter-repo` 重写历史：

```bash
pip install git-filter-repo
# 删除整个文件（从历史+工作区）
git filter-repo --force --invert-paths \
  --path skills/utils/gemini_setup.py \
  --path skills/utils/hermes-platform-config/SKILL.md
# 或仅替换某个 key 为占位（保留文件）
printf '真实KEY==><PLACEHOLDER>\n' > /tmp/repl.txt
git filter-repo --force --replace-text /tmp/repl.txt
```
> `filter-repo` 会移除 origin remote（正常），重写后重新 `git remote add` + `git push --force`。

### 7. 新云重建

```bash
git clone https://github.com/<user>/<repo>.git ~/.hermes/skills-migrated
cp -r skills-migrated/skills/* ~/.hermes/skills/
```

## 常见陷阱（实测）

1. **skill 文档里写真实 key 当示例** → GitHub 判定为 GCP/飞书/Lark 密钥直接拦 push。文档示例必须用 `<PLACEHOLDER>`，真实 key 用 filter-repo 替换。
2. **token 类型错（fine-grained PAT 推不动）** → 这是 2026-08 实战最常踩的坑：**fine-grained PAT（`github_pat_...`）能过 API 认证（curl 读 user/repos 返回 200、甚至 API 显示 `admin:True`），但 `git push` 一律 403 Permission denied**。原因：fine-grained PAT 的 repo 写权限对 git 操作需单独授权，且常未覆盖目标仓库。✅ **必须用 classic PAT（`ghp_...`）并勾选 `repo` 全权** 才能 git push。手机 GitHub App 不能生成 token——只能在网页 github.com → Settings → Developer settings → Tokens(classic) 生成（或手机浏览器开网页版）。
3. **本地分支叫 master、仓库默认 main** → `git push` 报 `src refspec main does not match`。用 `git push -u origin HEAD:main`。
4. **无头环境无法交互输密码** → 必须用 token 写进 remote URL，不能等弹窗。
5. **filter-repo 拒绝非 fresh clone** → 加 `--force`（本地新建单 commit 仓库安全）。
6. credentials/ 目录务必进 .gitignore，否则 API key / 私钥会被传上去。

7. **secret scanning 拦的是仓库历史 hash，不是本次 commit** → 一旦某次 push 尝试把疑似密钥（含 Hermes 自带 skill 里的示例 `client_secret`、二进制 `bin/tirith` 匹配、`ghp_`/`github_pat_` 字样）送进了仓库，GitHub 记住该 hash，**之后任何 token 对同一仓库 push 都被 `push declined due to repository rule violations` 拒**（本地怎么改历史都没用，是服务端策略）。两种解法：① 在 GitHub 网页关掉该仓库 Settings → Code security → Secret scanning，再 force push；② 换一个从没被标记过的新仓库推（实战最终用 `hermes-backup` 新仓库成功，`free` 仓库已标记拒推）。**`git filter-branch`/`filter-repo` 重写本地历史只能清你自己的真实 token，清不掉 GitHub 服务端已记的 hash，也清不掉 Hermes 系统文件里的示例字符串**——那些示例误报必须靠 .gitignore 排除 `bin/tirith`、`skills/productivity/google-workspace/scripts/` 等，或换干净仓库。

8. **filter-repo 未装时退回 filter-branch**：本机 `pip install git-filter-repo` 失败，改用 `git filter-branch --force --index-filter 'git rm --cached --ignore-unmatch <file>' --prune-empty -- --all` 删文件，或 `--tree-filter 'sed -i "s/KEY/[REDACTED]/g" {} +'` 替换字符串。注意 filter-branch 前必须 `git reset --hard` + `git checkout -- .` 清掉未暂存改动，否则报 `Cannot rewrite branches: You have unstaged changes`。跑完 `git for-each-ref refs/original/ | xargs -n1 git update-ref -d` + `git reflog expire --expire=now --all` + `git gc --prune=now` 清备份引用，再 force push。

9. **`git add -A` 是备份同步的隐性脚枪** → 它会把 `.gitignore` 漏写的二进制大目录（如 Hermes 自动生成的 `tools/`，含 448MB chromium、107MB ffmpeg/node/python）抓进暂存并写进历史。**GitHub 100MB 硬限（GH001）会在 push 时拒收整个提交，且不区分文件大小——一个超界文件就能让 skills/memories 全链路卡死数周**。✅ sync 脚本必须用**白名单 `git add skills/ memories/ config.yaml cron/jobs.json .gitignore SOUL.md scripts/`**，并在 `.gitignore` 显式排除 `tools/ bin/ cloud-docs/ *.tmp *.lock skills/.locks/` 等运行态/二进制目录。改完用 `git rev-list --all --objects | git cat-file --batch-check=... | awk '$3>100000000'` 核验历史里无 >100MB blob，再 force push。

10. **大二进制已进历史 → 必须 `git filter-repo` 重写，不可 `git rm`** → `git filter-repo --force --invert-paths --path tools/ --path bin/ --path-glob '*.tmp'` 等逐路径剔除；filter-repo 会移除 origin remote，重写后重新 `git remote add` + `git push --force`。远程跟踪引用滞后时 `git fetch origin <branch>` 再 `git ls-tree -r --name-only origin/<branch>` 验证远端真实内容（别信 `git ls-tree origin/main` 在 remote 被清后的 0 结果）。

11. **本地分支与远端默认分支不一致 → 统一为 main 后用 `git push --force origin HEAD:main`** → 双分支（本地 master / 远端 main）会让分散脚本各推各的、互相冲突。统一一条分支 + 一条每日增量 cron（删掉旧的多条每周/每日重复任务），避免重复提交噪音。

## 实战：零配置换机全套备份（2026-08 验证通过）

用户要求「换任何机器一键拉起，不重新调教」。最终落地方案：

- **仓库**：`bfliujinlong/hermes-backup`（private）
- **认证**：GitHub **Deploy Key**（SSH ed25519，无 token 落盘，cron 自动同步无感知）
- **进备份**：skills/（全部，单一真源）、memories/（MEMORY.md/USER.md）、config.yaml、SOUL.md、channel_directory.json、cron/jobs.json、scripts/、oci-monitor/*.sh（含 sync_github.sh + restore_hermes.sh）
- **不进备份**（.gitignore 排除 + 手动配）：
  - 密钥：`.env`、`.env.aliyun`（Azure/阿里 AK）
  - 大源码：`hermes-install/`（1.6G）、`deploy/dsh-src/`（1.5G，新机重装）
  - 运行时态：`sessions/`、`gateway*.log/pid/lock`、`cron/executions.db`、聊天 dump
  - 输出物：`cloud-docs/`（251M，存 /data 盘）
- **sync_github.sh**（增量同步脚本）：**白名单 `git add` 具体目录**（见下方坑 9），**绝不用 `git add -A`** → 有变更才 commit → SSH push。无明文 token（靠 SSH key）。日志 `~/.hermes/scripts/sync-github.log`
- **cron 自动同步**：`0 16 * * 0`（= 上海周日 24:00，机器时区 UTC）跑 `sync_github.sh`。用**系统 crontab**（非 Hermes cron，避免网关依赖）
- **restore_hermes.sh**（换机恢复）：`git clone` → 重建 skills→cc/codex 软链（187个，单一真源）→ 提示手动补密钥/服务。支持 `curl raw.githubusercontent.com` 一键拉跑

### 换机必须手动配置的 key（不在仓库）
| 文件 | 内容 | 去哪拿 |
|------|------|--------|
| `~/.hermes/.env` | 邮件/钉钉/飞书/各平台 token | 原机 note.txt + 各平台后台重生成 |
| `~/.hermes/.env.aliyun` | 阿里云 AK | 阿里云 RAM → AccessKey |
| `~/.oci/config` | OCI CLI 密钥 | OCI 控制台 → 用户 → API Keys |
| `~/.ssh/github_backup` | GitHub deploy key（后续同步） | 新机 `ssh-keygen` + 公钥加 GitHub Deploy keys |
| Cloudflare token | dsh 外网隧道 | Cloudflare 控制台 → Tunnels → 复制 token |
| dsh-src 源码 | gitignore 排除 | 重新 `git clone` + `pnpm install` |
| 系统服务 | dsh/cloudflared/nginx unit | 从原机 `/etc/systemd/system/` 拷贝或重建 |

### 恢复命令
```bash
git clone git@github.com:bfliujinlong/hermes-backup.git ~/.hermes
bash ~/.hermes/oci-monitor/restore_hermes.sh
# 然后按上面表格手动补密钥 + systemctl enable 服务
```

⚠️ **不要备份 dsh 源码 `dsh-src/`（含 node_modules 1.5G）**——只备份配置，源码新机重装。
⚠️ **机器时区确认**：cron 按 UTC，上海周日24:00 = UTC 周日16:00。若机器时区是 Asia/Shanghai 需换算。

## 与 overseas-model-hub 的配合

海外模型 key（OpenRouter / Nous / Z.AI）也走 token 文件，不要写进 skill 文档或 commit。换云后在新机器重新生成 token 即可，skill 本身不含密钥。

## 硬规则（用户 2026-08-30 明确重申）：绝不明文保存 token

- 用户多次强调「别明文保存」「别明文保存 token」。任何需要凭证的操作：
  - **不要**把 PAT/token 写进脚本、`note.txt`、`.env`（已受保护）、聊天记录、或 git。
  - 临时用：environment variable 注入 remote URL，push 完立刻 `git remote set-url origin <clean https>` 清痕迹，网页 revoke。
  - 长期：优先 SSH Deploy Key（本会话实战方案，cron 无感知、无过期、无账号级权限）。
  - 用户给 token 只为一次性 push 时，用完即清，且建议其去 GitHub revoke（见实战段 deploy key 接管后 PAT 应删）。
- 这条是用户零费用红线的一部分（信用卡/密钥泄露风险），优先级高于便利。

## 延伸：手机语音助理桥接（Siri/iPhone → Hermes）

换机/移动端要用 Hermes 当语音助理，见独立 skill `hermes-mobile-bridge`（CF 隧道中继 + iOS 快捷指令配方，已实战验证）。
