#!/bin/bash
# sync-memory-github.sh - 每周日增量同步 Hermes 资产到 GitHub bfliujinlong/myskill
# 目标: memory 增量 + 配置/skills, 保证新虚拟机 clone 即开箱即用。
#
# 认证: ~/.ssh/id_ed25519_github (账号级 key, ssh -T 回 "Hi bfliujinlong!")。
#       myskill 必须用账号 key, 不能用 github_backup(单仓 deploy key, 推 myskill 必拒)。
#
# 关键修复(2026-11-15):
#  1) 绝不 git add -A —— 旧版把 tools/ bin/ 的 918MB 二进制(chromium/libpython/ffmpeg/node)
#     塞进历史, push repack 在 955MiB VM 上 OOM(signal 9) 且触发 GH001。改为白名单 add。
#  2) myskill/main 有分支保护 —— force/non-ff push 必被拒。每次先 fetch + reset --soft
#     到 origin/main, 保持 fast-forward, 再普通 push。
#  3) 远端 main 同时被另一个 skills-sync job 更新 —— 以远端为基线, 只叠加本 job 的资产。

set -euo pipefail

HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
REMOTE_URL="git@github.com:bfliujinlong/myskill.git"
BRANCH="main"
DATE=$(date +%Y-%m-%d)
SSH_KEY="$HOME/.ssh/id_ed25519_github"
export GIT_SSH_COMMAND="ssh -i $SSH_KEY -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new"

cd "$HERMES_HOME"

# 0b. 关闭自动 gc(918MB 不可达 blob 会在 push 时触发 repack, 在 955MiB VM 上 OOM signal 9)
git config gc.auto 0
git config maintenance.auto false
rm -f .git/gc.log

# 0. 前置: 认证健康检查(key 失效直接失败, 不做假成功)
#    注意: ssh -T git@github.com 即使认证成功也永远 exit 1(无 shell 访问),
#    绝不能直接接 pipefail 管道, 否则假判失败。先取输出到变量再 grep。
AUTH_MSG=$(ssh -T -o BatchMode=yes -o IdentitiesOnly=yes -i "$SSH_KEY" git@github.com 2>&1 || true)
if ! printf '%s' "$AUTH_MSG" | grep -q "Hi bfliujinlong!"; then
  echo "[$(date)] ❌ GitHub 认证失败: $SSH_KEY 无法以 bfliujinlong 认证, 终止" >&2
  echo "auth msg: $AUTH_MSG" >&2
  exit 1
fi

# 1. 纠正 remote
if git remote get-url origin >/dev/null 2>&1; then
  CUR=$(git remote get-url origin)
  if [[ "$CUR" != "$REMOTE_URL" ]]; then git remote set-url origin "$REMOTE_URL"; fi
else
  git remote add origin "$REMOTE_URL"
fi

# 2. 拉取远端最新(分支保护要求 fast-forward)
git fetch -q origin "$BRANCH"

# 3. 以远端为基线重建索引(--mixed 保留工作区但清空暂存区; 旧版 --soft 把
#    分叉线的 18996 个二进制暂存项留在 index, 是 OOM 的帮凶)
git reset --mixed -q "origin/$BRANCH"

# 5. 白名单 add —— 绝不用 git add -A
#    .gitignore 已排除 tools/ bin/ node/ *.db-* / cron/output 及全部凭证
git add -A -- \
  .gitignore \
  config.yaml \
  SOUL.md \
  channel_directory.json \
  memories/ \
  skills/ \
  scripts/

# 6. 无变更则跳过
if git diff --cached --quiet; then
  echo "[$(date)] 无变更, 跳过提交"
  exit 0
fi

# 7. memory 有变更则写日期增量 CHANGELOG(去重: 同一天不重复追加)
if git diff --cached --name-only | grep -q "^memories/"; then
  if ! grep -qxF "## $DATE" memories/CHANGELOG.md 2>/dev/null; then
    {
      echo ""
      echo "## $DATE"
      echo ""
      echo "memory 变更文件:"
      git diff --cached --name-only | grep "^memories/" | grep -v "CHANGELOG.md" | sed 's/^/- /'
      echo ""
    } >> memories/CHANGELOG.md
    git add memories/CHANGELOG.md
  fi
fi

# 8. 推送前安全闸门: 白名单资产里不得有明文密钥 / >100MB blob
if git diff --cached --name-only -z | xargs -0 -r grep -IlE "ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}|BEGIN (RSA|OPENSSH|EC) PRIVATE KEY" 2>/dev/null | grep -q .; then
  echo "[$(date)] ❌ 安全闸门: 暂存区命中疑似明文密钥, 终止推送" >&2
  exit 1
fi
BIG=$(git diff --cached --name-only -z | xargs -0 -r -I{} sh -c 'test -f "$1" && [ $(stat -c%s "$1") -gt 100000000 ] && echo "$1"' _ {} || true)
if [ -n "$BIG" ]; then
  echo "[$(date)] ❌ 安全闸门: 暂存区含 >100MB 文件(GH001 会拒收): $BIG" >&2
  exit 1
fi

# 9. 提交(日期增量标记)
CHANGED=$(git diff --cached --name-only | wc -l)
MSG="sync: $DATE 增量更新 ($CHANGED 文件)"
if git diff --cached --name-only | grep -q "^memories/"; then
  MSG="$MSG [含memory调教]"
fi
git commit -q -m "$MSG"

# 10. 普通 push(fast-forward, 兼容分支保护); 本地分支名是 master, 远端是 main,
#     故用 HEAD:main 显式映射。pipefail 保证失败即非零。
git push origin "HEAD:$BRANCH" 2>&1 | tail -5

echo "[$(date)] ✅ 已推送 $DATE 增量 ($CHANGED 文件) -> $REMOTE_URL"
