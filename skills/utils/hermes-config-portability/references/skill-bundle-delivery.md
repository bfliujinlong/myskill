# Skill 导出交付包构建（本地 tar.gz → Telegram）

本文件是 `hermes-config-portability` 中「打包交付包」小节的命令级配方。用户口述「把某 skill 打包发我」时按此执行。

## 0. 取真实改动清单（权威源，不信任旧 manifest）
```bash
# 目标时间窗（例：10-31 全天 + 次日凌晨）
find ~/.hermes/skills -maxdepth 2 -type d \
  -newermt "2026-10-31 00:00" ! -newermt "2026-11-01 06:00" \
  2>/dev/null | sed 's#^\./##' | awk -F/ 'NF>=1{print $1}' | sort -u > /tmp/ysk.txt
cat /tmp/ysk.txt
```
> 用此清单比对旧 bundle 宣称范围，缺哪些补哪些（陷阱 12）。

## 1. 组装到临时源目录
```bash
rm -rf /tmp/bundle && mkdir -p /tmp/bundle
cd ~/.hermes/skills
# 纯 skill 包：只拷技能
for s in $(cat /tmp/ysk.txt); do
  [ -d "$s" ] && cp -r "$s" /tmp/bundle/ && echo "+ $s" || echo "! 缺失 $s"
done
# 全量（含 memory）包：
# cp -r ~/.hermes/skills /tmp/bundle/skills
# cp -r ~/.hermes/memory /tmp/bundle/memory   # 见步骤 2 剔台账
```

## 2. 剔除内部拓扑（红线）
```bash
rm -f /tmp/bundle/memory/HERMES_ENV-REGISTRY.md   # GCP IP / OCI ID / CF 隧道 ID
```

## 3. 剔除膨胀物（避免 >50MB 发不出）
```bash
find /tmp/bundle/skills -name ".git" -type d -exec rm -rf {} + 2>/dev/null
rm -rf /tmp/bundle/skills/translate-book/tests            # 大体积测试 PDF/Epub
rm -f /tmp/bundle/skills/cloud-price-bench/adapters/.cache/*.json
# 定位剩余大目录：du -sh /tmp/bundle/skills/* | sort -rh | head
```

## 4. 内容级敏感扫描（扫值，非文件名）
```bash
grep -rIlE "(sk-[a-zA-Z0-9]{20,}|AKID[0-9A-Z]{10,}|-----BEGIN|api[_-]?key[\"'= :]{0,4}[A-Za-z0-9_\-]{16,})" \
  /tmp/bundle 2>/dev/null | head
# 空 = clean；命中真实 key 值必须清除，文档占位符可保留
```

## 5. 打包（本机无 zip，用 tar.gz）
```bash
tar czf /home/ubuntu/skills_export.tar.gz -C /tmp/bundle .
ls -la /home/ubuntu/skills_export.tar.gz
# <50MB 才送 Telegram；超出回步骤 3 再瘦身
# Windows 兼容 zip 备选：python3 -c "import zipfile,shutil; ..."
```

## 6. 校验 + 发送
```bash
echo "MEDIA:/home/ubuntu/skills_export.tar.gz"   # 触发 Telegram 附件
```

## 7. 交付前核对清单
- [ ] `tar tzf <pkg>` 列出成员，对照宣称范围无遗漏（陷阱 12）
- [ ] 无 `HERMES_ENV-REGISTRY.md` / 内部 IP（陷阱 13）
- [ ] `du -sh skills/*` 已瘦身，整包 <50MB（陷阱 14）
- [ ] 内容级敏感扫描零命中真实密钥值（陷阱 15）
