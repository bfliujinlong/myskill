#!/bin/bash

echo "=== GCP 配置脚本 ==="
echo "第1步：登录 GCloud"
gcloud auth login

echo "第2步：启用 Budget API"
gcloud services enable billingbudgets.googleapis.com

echo "第3步：创建 0.1 美元预算告警"
gcloud billing budgets create \
  --billing-account=0137DE-0D1BAB-37E0B4 \
  --display-name="0.1美元告警" \
  --amount=0.1 \
  --currency=USD \
  --threshold-type=percent \
  --threshold-percent=100 \
  --alert-pubsub-topic="projects/cryptic-bivouac-471612-t0/topics/gcp-budget-alerts"

echo "=== 配置完成 ==="
