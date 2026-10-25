# 输出模板：Hive MetaStore 迁移

`<>` 为占位符，产出时替换。

## 模板 1：元数据导出报告

```markdown
# Hive MetaStore 导出报告

- 源 MetaStore：<MySQL 5.7，Hive 2.3>
- 导出时间：<YYYY-MM-DD>
- 库 / 表 / 分区 / UDF / SerDe：<X / Y / Z / U / S>

## 导出清单
| 类型 | 数量 | 备注 |
| --- | --- | --- |
| Database | <N> | <排除系统库> |
| Table（内/外） | <N / M> | |
| Partition | <N> | |
| UDF | <N> | <含自定义> |
| 异常对象 | <N> | <损坏/无 LOCATION> |
```

## 模板 2：Schema 转换清单

```markdown
| Hive 概念 | DLF / MaxCompute 对应 | 转换规则 | 注意 |
| --- | --- | --- | --- |
| Database | <Database / Project> | <命名映射> | <大小写> |
| Table | Table | <类型映射> | <列类型差异> |
| Partition | Partition | <dt=YYYYMMDD 格式统一> | |
| SerDe | Library | <ORC/Parquet 直迁> | <TextFile 自定义 SerDe 需重写> |
```

## 模板 3：数据位置映射表

```markdown
| 表名 | 源 LOCATION | 目标 LOCATION | 数据迁移状态 |
| --- | --- | --- | --- |
| <dwd_order> | hdfs://ns1/user/hive/warehouse/dwd_order | oss://<bucket>/hive/dwd_order | ✅ 已迁 |
```

## 模板 4：业务验证报告

```markdown
| 验证项 | 命令 | 期望 | 实际 | 结果 |
| --- | --- | --- | --- | --- |
| 库列表 | SHOW DATABASES | <N 个> | <N 个> | ✅ |
| 表结构 | DESCRIBE <table> | <字段一致> | <一致> | ✅ |
| 抽样查询 | SELECT * FROM <t> LIMIT 10 | <10 行> | <10 行> | ✅ |
```
