# Google Gemini API 密钥类型与迁移指南（2026年）

## API Key 类型

### Standard API Key（旧版）

- 格式示例：`<AQ.YOUR_AGENT_PLATFORM_KEY>`
- 特点：与 Google Cloud 服务账号无关，独立凭据
- **状态：2026年9月起将被拒绝**（Google 官方公告）

### Auth API Key（新版）

- 格式示例：`AIzaSyDxxxxxxxxxxxxxxxxxxxxxxx`
- 特点：直接绑定到 Google Cloud 服务账号
- 默认限制为 Generative Language API (Gemini API)
- 提供快速泄露密钥封禁机制
- **推荐使用此类型**

## 迁移步骤

### 1. 创建新的 Auth 类型 API Key

**方法一：Google AI Studio**
1. 访问 [Google AI Studio](https://aistudio.google.com/)
2. 登录 Google 账号
3. 点击「Get API key in Google AI Studio」或「Create API key」
4. 选择你的 GCP 项目
5. 创建并复制新的 key

**方法二：Google Cloud Console**
1. 访问 [API Credentials](https://console.cloud.google.com/apis/credentials)
2. 选择你的 GCP 项目
3. 点击「创建凭据」→「API 密钥」
4. 命名（例如 `gemini-api-key`）
5. 创建后复制密钥值

### 2. 验证新 Key 的格式

新创建的 Auth 类型 Key 通常以 `AIzaSy` 开头。

### 3. 更新应用程序配置

将新的 API Key 替换到所有配置中：

```bash
# 更新环境变量
export GEMINI_API_KEY="AIzaSyXXXXXXX"

# 或更新 Hermes 配置
# ~/.hermes/.env 文件中
GEMINI_API_KEY=AIzaSyXXXXXXX
```

### 4. 测试新 Key

```bash
curl -s -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=AIzaSyXXXXXXX" \
  -H "Content-Type: application/json" \
  -d '{"contents": [{"parts": [{"text": "你好"}]}]}'
```

预期返回正常的响应结果，而非 401 错误。

### 5. 删除旧 Key

确认新 Key 正常工作后，删除或吊销旧的 Standard 类型 Key，防止误用。

## 常见问题

### Q: 我现在的 Key 是什么类型？

A: 查看 Key 格式：
- `AQ.xxx` → 很可能是 Standard 类型（旧版）
- `AIzaSyxxx` → Auth 类型（新版）

### Q: 调用返回 401 错误怎么办？

A: 可能原因：
1. 使用了 Standard 类型 Key（2026年9月后被拒绝）
2. Key 无效或已吊销
3. 项目未启用 Generative Language API

解决：创建新的 Auth 类型 Key，确保项目已启用相关 API。

### Q: 能否继续使用 Standard Key？

A: 短期可以，但**2026年9月起将被拒绝**。建议尽快迁移到 Auth 类型 Key。

## 免费层可用模型

| 模型 | RPM | 每日请求 | 状态 |
|------|-----|---------|------|
| gemini-2.0-flash | 15 | ~1000 | ✅ 免费 |
| gemini-2.5-flash | 5-15 | ~1000 | ✅ 免费 |
| gemini-3-flash-preview | 10 | ~1500 | ✅ 免费 |
| gemini-3.1-flash-lite-preview | 15 | ~1000 | ✅ 免费 |
| gemini-2.5-pro | 5 | 50 | ❌ 2026年4月起不再免费 |
| gemini-3.1-pro-preview | - | - | ❌ 付费 |

> ⚠️ 速率限制按**项目**计算，不是按 API Key。

## 参考

- [Gemini API 密钥文档](https://ai.google.dev/gemini-api/docs/api-key)
- [OAuth 认证文档](https://ai.google.dev/gemini-api/docs/oauth)