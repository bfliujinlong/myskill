---
name: aiccp-platform
description: "AICCP（AI Cloud Consulting Platform）平台架构与开发规范：Vue3/FastAPI/PostgreSQL16/Redis/MinIO，Docker 5 容器，三层架构，AI 四段式调用。开发、排障、部署 AICCP 时触发。"
version: 1.0.0
author: jinlongliu
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [AICCP, FastAPI, Vue3, 三层架构]
    related_skills: [workbuddy-rules]
---

# When to Use
用户提到 AICCP / AI-CCP 仓库 / 平台开发、部署、排障、功能注入时。

# 架构约束（不可违反）
- 技术栈：Vue3 + FastAPI + PostgreSQL 16（UUID 主键）+ Redis + MinIO
- 部署：Docker 5 容器（aicc-frontend/aicc-backend/aicc-postgres/aicc-redis/minio）
- 主机：阿里云 ECS（cn-shanghai, 139.196.171.8, InstanceId=i-uf65uz7ssmvcqla865kf, ARM64 Ubuntu 24.04）
- SSH：`ssh ali` 或 `ssh aicc`（别名，密钥 id_ed25519_github）
- 仓库：bfliujinlong/AI-CCP
- 后端代码路径：容器内 `/app/app/`（注意双层 app/，非 `/app/`）
- 分层：Service / Repository / Controller 三层严格隔离，禁止跨层调用
- 权限：RBAC；设计原则：Fact Sheet First
- AI 能力实现：必须通过 Skill → Prompt → LLM → Structured Output 流程，禁止直接裸调 LLM
- 安全组仅开放 22 + 80，后端/DB/Redis/MinIO 仅内网可达

# 无侵入式功能注入（不重建镜像）
添加前端/后端功能时，优先用 docker cp + nginx sub_filter，避免改源码和重建镜像：
1. 写静态文件（CSS/JS）→ `docker cp` 到 aicc-frontend 的 `/usr/share/nginx/html/`
2. 修改 nginx conf 加 `sub_filter "</head>" "<link...><script...></head>"` + `gzip off`
3. `nginx -s reload` 立即生效
4. 后端新增 Python 模块 → `docker cp` 到 aicc-backend 的 `/app/app/services/` 或 `/app/app/api/`，更新 `__init__.py` 注册 router，`docker restart`

# ARM64 架构陷阱
ECS 是 aarch64，容器也是 aarch64。从 x86 宿主机 `docker cp` 二进制进去会 SIGSEGV（exit 139）。装 CLI 工具必须下载对应架构版本或用纯 Python 方案替代。

# 云资源监控 API 模式
查询云资源用 Python httpx 直调 OpenAPI（签名 + AK/SK），不依赖 CLI 或 pip 装 SDK：
- 凭据从 `~/.aliyun/config.json` 读取（需先 docker cp 进容器）
- 内存缓存 TTL=600s 防限流
- API 路由前缀 `/api/v1/cloud-resources/`（summary/instances/billing）
- 前端 dashboard 通过 `fetch` 自动加载，nginx sub_filter 注入 JS

# 参考文件
- `references/dashboard-integration.md` — 阿里云资源 Dashboard 集成详细步骤
