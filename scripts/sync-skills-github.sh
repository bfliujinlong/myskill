#!/bin/bash
# sync-skills-github.sh - 每周把本地 ~/.hermes/skills 同步到 GitHub
# 认证: SSH Deploy Key (~/.ssh/myskill_deploy), 无 token 落盘。
# 注意: HERMES_HOME 用 $HOME 推导, 兼容 GCP(/home/bfyalong) 与 OCI(/home/ubuntu) 双机。
set -uo pipefail

HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
REPO="bfliujinlong/myskill"
REMOTE="git@github.com:${REPO}.git"
KEY="${SKILLS_DEPLOY_KEY:-$HOME/.ssh/id_ed25519_github}"
BRANCH="main"

cd "$HERMES_HOME" || { echo "ERROR: $HERMES_HOME 不存在"; exit 1; }

export GIT_SSH_COMMAND="ssh -i $KEY -o IdentitiesOnly=yes -o BatchMode=yes -o StrictHostKeyChecking=accept-new"

# 确保 remote 指向 SSH 地址
CUR=$(git remote get-url origin 2>/dev/null || true)
if [ "$CUR" != "$REMOTE" ]; then
  git remote remove origin 2>/dev/null || true
  git remote add origin "$REMOTE"
fi

# 连通性预检: 认证不通就早失败, 绝不静默报成功
if ! timeout 40 git ls-remote --exit-code origin >/dev/null 2>&1; then
  echo "[$(date)] ERROR: SSH 认证失败(git ls-remote 不通), 无法同步"
  echo "  排查: ssh -i $KEY -T git@github.com"
  echo "  修复: 把 $(cat "$KEY.pub" 2>/dev/null || echo "$KEY.pub") 加到 GitHub → $REPO → Settings → Deploy keys (勾 Allow write access)"
  git remote remove origin 2>/dev/null || true
  exit 2
fi

# 拉取远端(ff-only), 避免冲突
git fetch -q origin "$BRANCH" 2>/dev/null || true
git merge --ff-only "origin/$BRANCH" 2>/dev/null || true

# 白名单暂存(绝不用 git add -A, 防 tools/bin 等大二进制进历史触发 GitHub 100MB 拒收)
git add skills/ .gitignore 2>&1

# 若无变更则跳过提交
if git diff --cached --quiet; then
  echo "[$(date)] 无变更，跳过提交"
else
  CHANGED=$(git diff --cached --name-only | wc -l)
  git commit -q -m "weekly sync: hermes skills $(date -u +%Y-%m-%d) ($CHANGED 文件)" 2>&1
  echo "[$(date)] 已提交 $CHANGED 个文件"
fi

# 推送(本地分支可能是 master, 统一推到远端 main)
PUSH_OUT=$(git push -u origin "HEAD:$BRANCH" 2>&1)
PUSH_RC=$?
echo "$PUSH_OUT" | tail -5
if [ "$PUSH_RC" -ne 0 ]; then
  echo "[$(date)] ERROR: push 失败 (rc=$PUSH_RC)"
  git remote remove origin 2>/dev/null || true
  exit 1
fi
echo "[$(date)] 同步完成 → $REMOTE ($BRANCH)"

# 清理 remote 痕迹
git remote remove origin 2>/dev/null || true
