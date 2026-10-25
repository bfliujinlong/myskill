#!/bin/bash
# Config Guard - 防 config.yaml 被还原脚本
# 每次重启网关前运行，确保模型路由不会被覆盖

set -e

# 期望的默认模型（2026-09 更新）
EXPECTED_MODEL="meituan/longcat-2.0:free"
EXPECTED_PROVIDER="nous"

# 检查当前配置
CURRENT=$(grep "model.default:" ~/.hermes/config.yaml | sed 's/.*: *//' | tr -d '"')

echo "当前默认模型：$CURRENT"
echo "期望默认模型：$EXPECTED_MODEL"

if [ "$CURRENT" != "$EXPECTED_MODEL" ]; then
    echo "⚠️ 检测到配置偏离，自动修复..."
    hermes config set model.default "$EXPECTED_MODEL"
    hermes config set model.provider "$EXPECTED_PROVIDER"
    echo "✅ 修复完成"
else
    echo "✅ 配置正常"
fi

# 同步 cron jobs.json 中的模型（防止老 job 撞废弃模型）
if [ -f ~/.hermes/cron/jobs.json ]; then
    echo "同步 cron jobs 模型配置..."
    python3 -c "
import json
with open('~/.hermes/cron/jobs.json', 'r') as f:
    jobs = json.load(f)
updated = 0
for job in jobs.get('tasks', []):
    if 'model' in job:
        old_model = job['model']
        # 已下架的模型列表
        dead_models = [
            'tencent/hy3:free', 'upstage/solar-pro4:free', 
            'z-ai/glm-5.2:free', 'stepfun/step-3.7-flash:free'
        ]
        if old_model in dead_models:
            job['model'] = '$EXPECTED_MODEL'
            job['provider'] = '$EXPECTED_PROVIDER'
            updated += 1
with open('~/.hermes/cron/jobs.json', 'w') as f:
    json.dump(jobs, f, indent=2, ensure_ascii=False)
print(f'同步完成，更新 {updated} 个 job')
"
fi

echo "🛡️ Config Guard 完成"