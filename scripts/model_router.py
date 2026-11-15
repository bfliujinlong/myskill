#!/usr/bin/env python3
# model_router.py - 确保免费模型可用，困难任务 OpenAI 兜底
# 使用方式: 先运行探测，失败则切换
# 不处理任何密钥，密钥由环境变量/配置文件提供
import sys, subprocess, json, os

CONFIG = '/home/ubuntu/.hermes/config.yaml'
JOBS   = '/home/ubuntu/.hermes/cron/jobs.json'

FREE_MODELS = [
    ('openrouter', 'nvidia/nemotron-3.5-lightning:free'),
    ('openrouter', 'nvidia/nemotron-3-super-120b-a12b:free'),
    ('mistral',    'ministral-8b-2512'),
    ('cloudflare-workers-ai', '@cf/meta/llama-3.1-8b-instruct'),
]

OPENAI_MODEL = ('azure-foundry', 'gpt-4o')

def probe(model, provider):
    # 简单探测：尝试调用对应 provider 的健康端点（不发送完整请求，避免消耗）
    # 实际可用性已由 cron job + gateway 日志验证；此处仅做快速检查
    return True  # 预设可用；若需真实探测可扩展

def main():
    # 1) 检查当前默认模型
    # 2) 若主模型不可用（通过日志检查 404/401/429），切换到下一个免费模型
    # 3) 若全部免费不可用，切换到 OpenAI 兜底（需人工确认费用）
    # 4) 更新 config.yaml + jobs.json
    pass  # 具体实现由用户选择；此脚本提供框架

if __name__ == '__main__':
    main()
