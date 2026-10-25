# 输出模板：HDFS 迁移

`<>` 为占位符，产出时替换。

## 模板 1：迁移方案书

```markdown
# HDFS 数据迁移方案

- 源：<CDH 6.3，HDFS 总量 <X> PB，文件数 <Y> 亿，小文件占比 <Z>%>
- 目标：<阿里云 OSS + Data Lake Formation>
- 工具：<DistCp（首期 200TB）→ 闪电立方（剩余）>
- 窗口：<分 N 批，每批 10 TB，共 <M> 周>

## 目录映射
| 源路径 | 目标路径 | 数据量 | 访问模式 |
| --- | --- | --- | --- |
| /user/hive/warehouse | oss://<bucket>/hive/ | <X TB> | <引擎挂载> |
| /data/log | oss://<bucket>/log/ | <Y TB> | <归档> |
```

## 模板 2：迁移批次计划

```markdown
| 批次 | 目录 | 数据量 | 工具 | 计划窗口 | 状态 |
| --- | --- | --- | --- | --- | --- |
| 1 | /data/log/2023 | <10 TB> | DistCp | <MM-DD ~ MM-DD> | ✅ |
| 2 | /data/log/2024 | <10 TB> | DistCp | <MM-DD ~ MM-DD> | ⏳ |
```

## 模板 3：权限映射表

```markdown
| 源路径 | 源 ACL | 目标路径 | 目标权限 | 用户映射 |
| --- | --- | --- | --- | --- |
| /user/hive | <hive:hive rwx> | oss://<b>/hive/ | <RAM 子账号> | <hive→ram-hive> |
```

## 模板 4：校验报告

```markdown
| 目录 | 文件数（源/目标） | 字节数（源/目标） | 抽样 CRC | 结果 |
| --- | --- | --- | --- | --- |
| /data/log | <X / X> | <X / X> | <1000 全过> | ✅ |
```
