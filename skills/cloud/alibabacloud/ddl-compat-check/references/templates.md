# 输出模板：DDL 兼容度检测

`<>` 为占位符，产出时替换。

## 模板 1：兼容度报告

```markdown
# DDL 兼容度检测报告

- 目标引擎：<PolarDB MySQL 8.0>
- DDL 总数：<N>（DDL <x> / DML <y> / DCL <z>）

## 兼容度分布
| 等级 | 数量 | 说明 |
| --- | --- | --- |
| ✅ 直接兼容 | <A> | 零改动 |
| ⚠️ 语法兼容 | <B> | 自动等价改写 |
| ❌ 不兼容 | <C> | 手工改造 |
```

## 模板 2：逐条评估表（Excel 列头）

```markdown
| ID | 文件 | 行号 | 对象名 | DDL 类型 | 兼容度 | 差异点 | 改写建议 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 3 | <schema.sql> | 88 | <ORDERS> | CREATE TABLE | ⚠️ | <VARCHAR2> | <改 VARCHAR> |
```

## 模板 3：自动改写结果

```sql
-- 源（Oracle）
CREATE TABLE orders (
  id NUMBER(10) PRIMARY KEY,
  created_at DATE DEFAULT SYSDATE
) TABLESPACE users;

-- 目标（PolarDB MySQL）
CREATE TABLE orders (
  id DECIMAL(10) PRIMARY KEY,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 模板 4：不兼容改造清单

```markdown
| ID | 对象 | 差异点 | 改造方案 | 工作量 |
| --- | --- | --- | --- | --- |
| 5 | <TRG_AUDIT> | <DDL 触发器> | <改事件订阅> | <2 人天> |
```
