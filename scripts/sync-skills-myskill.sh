#!/bin/bash
# sync-skills-github.sh - 每周把本地 ~/.hermes/skills 同步到 GitHub bfliujinlong/myskill
# 使用 SSH deploy key 认证 (~/.ssh/github_backup)，无 token 落盘
set -e

HERMES_HOME="/home/ubuntu/.hermes"
SKILLS_SRC="${HERMES_HOME}/skills"
REPO_DIR="/home/ubuntu/myskill"
REPO="bfliujinlong/myskill"
REMOTE="git@github.com:${REPO}.git"

# 确保 myskill 目录存在
if [ ! -d "$REPO_DIR/.git" ]; then
  echo "ERROR: $REPO_DIR 不是 git 仓库"
  exit 1
fi

cd "$REPO_DIR"

# 确保 remote 指向 SSH 地址
git remote set-url origin "$REMOTE" 2>/dev/null || git remote add origin "$REMOTE"

# 清空现有 skills 目录（保留 .git 和 .gitignore）
find . -maxdepth 1 -not -name '.git' -not -name '.gitignore' -not -name '.' -exec rm -rf {} +

# 复制 skills 到 myskill 目录
cp -a "$SKILLS_SRC" ./skills

# 确保 .gitignore 包含常见忽略项
cat >> .gitignore << 'EOF'

# 忽略 skills 内部缓存/凭证
skills/.hub/
skills/.usage.json
**/.env
**/credentials/
**/__pycache__/
**/*.pyc
**/node_modules/
EOF

# 暂存所有变更
git add -A 2>&1

# 检查是否有变更
if git diff --cached --quiet; then
  echo "[$(date)] 无变更，跳过提交"
else
  SKILLS_COUNT=$(find skills -mindepth 1 -maxdepth 1 -type d -o -type l | wc -l)
  CHANGES=$(git diff --cached --stat | tail -1)
  git commit -q -m "weekly sync: hermes skills ${SKILLS_COUNT} skills $(date -u +%Y-%m-%d)" 2>&1
  echo "[$(date] 已提交: $CHANGES"
fi

# 推送
GIT_SSH_COMMAND="ssh -i /home/ubuntu/.ssh/github_backup -o StrictHostKeyChecking=no" \
  git push --force -u origin HEAD:main 2>&1 | tail -8

PUSH_RC=${PIPESTATUS[0]}
if [ "$PUSH_RC" -ne 0 ]; then
  echo "[$(date)] ERROR: push 失败 (rc=$PUSH_RC)"
  exit 1
fi

echo "[$(date)] 同步完成: $REPO"
