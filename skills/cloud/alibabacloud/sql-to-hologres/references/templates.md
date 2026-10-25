# 输出模板：SQL 转换到 Hologres

`<>` 为占位符，产出时替换。

## 模板 1：转换总报告

```markdown
# SQL → Hologres 转换报告

- 源引擎：<Oracle 19c>
- SQL 总数：<N>
- 转换时间：<YYYY-MM-DD>

## 转换分布
| 结果 | 数量 | 占比 |
| --- | --- | --- |
| 自动转换（高置信） | <A> | <x%> |
| 人工标注 | <B> | <x%> |
| 不可转换 | <C> | <x%> |
```

## 模板 2：逐条对照表（Excel 列头）

```markdown
| ID | 源 SQL | Hologres SQL | 差异类型 | 置信度 | 人工复核点 |
| --- | --- | --- | --- | --- | --- |
| 1 | <NVL(a,b)> | <COALESCE(a,b)> | 函数替换 | 高 | - |
| 2 | <CONNECT BY...> | <WITH RECURSIVE...> | 语法重写 | 中 | <递归深度> |
```

## 模板 3：函数替换速查表

```markdown
| 源函数 | Hologres 等价 | 示例 |
| --- | --- | --- |
| NVL(a,b) | COALESCE(a,b) | <一行示例> |
| DECODE(...) | CASE WHEN ... END | <一行示例> |
| SYSDATE | CURRENT_TIMESTAMP | |
| ROWNUM | ROW_NUMBER() OVER() | |
| GROUP_CONCAT | STRING_AGG | |
| LIMIT m,n | LIMIT n OFFSET m | |
```

## 模板 4：不可转换清单

```markdown
| ID | 源 SQL | 原因 | 业务建议 |
| --- | --- | --- | --- |
| 7 | <DBMS_LOB.CREATETEMPORARY...> | <无对应包> | <改标准 LOB API，需开发> |
```
