---
name: resume-screener
description: Screen resumes vs JD. Strict scoring, pass/fail.
trigger: 筛选简历 / 初筛 / JD匹配 / 简历评分
---

# 简历初筛 Skill

## 硬性要求 (1项❌=直接淘汰)
- K8s / ACK / 容器运维
- Linux & 网络 & 云平台
- 向量数据库 (Milvus/ES/Pinecone等)
- RAG 知识库建设
- API 集成治理

## 加分项
- 量产级 RAG 上线
- 阿里云 PAI/灵积/百炼
- DevSecOps / SRE
- ACP/RHCE/CKA 认证
- AI 安全 (Prompt Injection/内容过滤)
- AIOps / 监控

## 判定规则
```
✅ 可推: 硬性项全✅或最多1项⚠️(无❌)
⚠️ 备选: 硬性项1项❌但加分项丰富
❌ 不合适: 硬性项≥2项❌
```

## Output Format
```
## 初筛结论
[✅/❌/⚠️]

## JD匹配详情
| JD要求 | 简历对应 | 评分 | 说明 |

## 加分项匹配
| 加分项 | 简历对应 | 评分 |

## 亮点
- ...

## 风险点
- ...

## 综合评语
[2-3句客观描述]
```

## Rules
- "了解"不算满足; 无细节降一档
- 不编信息,不确定写⚠️
- 量产级RAG上线 > 做过培训 > 了解RAG
