---
name: weixin-voice
description: "微信(Weixin)通道对话约定: 用户主用微信(iLink bot o9cq80-GasGeoTVkNBnN3yHlaxO4@im.wechat)文字聊天, 但长回复(>~200字或含多段结构)需自动用TTS转mp3附在文字后发微信, 实现半语音体验(用户不愿换Telegram). TTS用OpenAI via Nous订阅(text_to_speech), 发送用hermes send -t weixin:<id> 'MEDIA:<path>'. 微信通道实测可收语音文件(sent成功). 短回复不附语音省token."
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [微信, 语音, tts, 半语音体验]
    related_skills: [model-router]
---

# 微信语音附回约定（Weixin Voice）

## 背景
用户主通道是微信(Weixin, iLink bot)。选了"保留微信文字 + 长回复转语音"方案(非Telegram语音对话)。
微信实测可收语音文件: `hermes send -t "weixin:o9cq80-GasGeoTVkNBnN3yHlaxO4@im.wechat" "MEDIA:/path/tts.mp3"` 返回 sent 成功。

## 语音通道能力对比（重要，别混淆）
| 通道 | 收语音(STT) | 发语音(TTS) | 像豆包程度 |
|---|---|---|---|
| **Telegram** | ✅ 原生语音气泡，能 STT 识别 | ✅ 已验证 TTS 能发（send MEDIA mp3 sent 成功） | **完全双向** |
| **微信(Weixin)** | ❌ iLink bot 收不到语音输入 | ✅ 我能发语音给你听 | 半语音（只能我读给你） |

**结论**：真正"像豆包"的语音对话必须走 **Telegram**（用户按住说话→我 STT→我 TTS 回）。微信侧只能我发语音、不能收用户语音。用户若想双向语音，引导去 Telegram 找同一个 Hermes bot 发语音。

## 规则
- **短回复**(<200字, 单段): 直接文字, 不附语音
- **长回复**(>200字/多段/列表结构): 文字发完后, 用 text_to_speech 生成 mp3, 再发一条 MEDIA 语音到微信
- **用户明确要求"语音"/"读给我听"**: 任何长度都附语音
- TTS: provider 默认 openai(nous订阅), 中文语音
- 发送目标固定: `weixin:o9cq80-GasGeoTVkNBnN3yHlaxO4@im.wechat`

## 执行步骤(长回复时)
1. 正常生成文字回复, 通过微信发文字
2. 调 text_to_speech(text=回复正文, output_path=~/oci-monitor/tts_<timestamp>.mp3)
3. hermes send -t "weixin:o9cq80-GasGeoTVkNBnN3yHlaxO4@im.wechat" "MEDIA:<path>"
4. 清理临时mp3(可选)

## 注意
- 微信走 iLink bot, 群聊通常不通, 仅DM
- 不要每条都TTS(浪费token/time), 仅长回复触发
- 若 MEDIA 发送失败(sent之外的错误), 降级为纯文字并提示
- 微信长回复自动附语音是 2026-08-23 用户选的方案2；方案1(Telegram语音)能力也在，随时可验证双向
