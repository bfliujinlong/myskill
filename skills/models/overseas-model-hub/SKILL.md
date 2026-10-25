---
name: overseas-model-hub
description: "海外免费模型 hub：Nous/Z.AI/Google 等免费模型的可用清单、Hermes 配置、限速与避坑。"
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [海外模型, 免费模型, nous, zai, gemini, 模型配置, model-hub]
    related_skills: [presales-architect, business-development, sales]
---

# 海外免费模型 Hub（Overseas Free Model Hub）

## When to Use（何时使用）

- 用户想用**海外免费模型**且不想产生信用卡费用
- 需要在 Hermes 里切换/配置不同免费模型
- 想知道某个海外模型是否免费、限速多少、怎么配
- 排查「模型调不通 / 401 / 403」类认证问题

## 核心原则

1. **免费优先**：先用能白嫖的，绝不碰付费
2. **不绑卡冲动**：GCP 免费额度要盯紧，告警设 $0.1
3. **Claude/Anthropic 有封号风险**：同一账号换客户端不改底层 API，封过就别硬刚
4. **配置写进 config.yaml 才持久**，Portal 实时切换重启会回退

## 一、已验证可用的免费模型

### ✅ Nous Inference API（最稳，推荐主力）
Hermes 默认走 Nous，以下均免费：

| 模型 | 特点 | 适用 |
|------|------|------|
| `upstage/solar-pro4:free` | 综合强、稳 | 通用问答 |
| `tencent/hy3:free` | 中文好、快 | 中文对话 |
| `longcat-2.0` | 长上下文 | 长文处理 |
| `zhipu/glm-4-flash` | 中文推理 | 中文任务 |
| `stepfun/step-3.7-flash` | 均衡 | 通用 |
| `upstage/solar-pro4` | 非 free 版（慎用，可能计费） | — |

切换方式（写 config.yaml，持久）：
```yaml
model:
  default: tencent/hy3:free
  provider: nous
  base_url: ''
```

### ✅ Z.AI（智谱开放平台，免费层）
| 模型 | 特点 |
|------|------|
| `glm-4.5-flash` | 中文好、免费、快 |

config.yaml：
```yaml
model:
  default: glm-4.5-flash
  provider: zai
  base_url: ''
```
> 注：当前会话通过 Nous Portal 实时切到 hy3，配置文件仍是 solar-pro4；要固化需改 config.yaml。

## 二、已验证「暂不可用」的海外模型

### ❌ Google Gemini（generativelanguage.googleapis.com）
本次会话踩坑全记录：
- API Key（`AQ.` 开头，Standard 类型）→ **401**，Google 正迁移到 Auth 类型 Key
- Service Account + `Generative Language Service Agent` 角色 → **403**（scope/权限仍不足）
- Vertex AI 端点 → **403 / 404**
- 根因：Generative Language API 对认证要求极严，免费调用通道基本堵死

**结论**：当前账号/项目下 Gemini 免费 API 不可用。替代方案：
- 走 Vertex AI（需绑卡，有免费额度但小）
- 等 Google 9 月后 Auth Key 政策明朗
- 或直接用 Nous/Z.AI 免费模型替代

### ⚠️ Anthropic Claude
- API Key 实测 **401**（Key 已失效/账号受限）
- 用户曾因 CC 被封，换 Hermes 不改底层 API，**封号风险仍在**
- 不建议在免费诉求下使用

## 三、Hermes 配置速查

查看当前模型：
```bash
cat ~/.hermes/config.yaml | grep -A 4 '^model:'
```

切换模型（用 python 改 yaml 更稳）：
```bash
cd ~/.hermes && python3 -c "
import yaml
c=yaml.safe_load(open('config.yaml'))
c['model']={'default':'tencent/hy3:free','provider':'nous','base_url':''}
yaml.dump(c,open('config.yaml','w'),allow_unicode=True,sort_keys=False)
print('done')
"
```
改完需重启网关：`sudo systemctl restart hermes-gateway`（在 Cloud Shell 执行，不能从网关内重启）。

## 四、GCP 费用安全（用户强关注）

- 项目 `cryptic-bivouac-471612-t0`，账单 `0137DE-0D1BAB-37E0B4`
- 当前月费用 ~$0.0001（几乎为 0），VM 用免费层
- 已配每日 9:00 监控任务 → Telegram(5701842056) + 短信(15102159929) 双通知
- Budget API 与 $0.1 告警需在 Cloud Shell 手动跑（见 gcp-billing-monitor 相关）
- 临时实例 `instance-20260817-023723` 已删除

## 五、选型决策树

```
要免费海外模型？
├─ 中文为主 → Nous: tencent/hy3:free 或 Z.AI: glm-4.5-flash
├─ 综合/英文 → Nous: upstage/solar-pro4:free
├─ 长上下文 → Nous: longcat-2.0
├─ 想用 Gemini → 当前不可用，先用替代
└─ 想用 Claude → 有封号风险，不推荐
```

## 常见陷阱
- 只看模型名带「free」就以为安全，Nous 上非 free 版（如 solar-pro4 无 :free）可能计费
- Portal 实时切换不写配置，重启网关回退
- Google AQ. Key 当万能钥匙，实际已失效
- GCP 不配 Budget 告警，免费额度超了才发现
