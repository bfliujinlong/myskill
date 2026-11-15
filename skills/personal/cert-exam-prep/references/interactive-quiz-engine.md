# 交互式自测引擎（cert-exam-prep 第 8 步配套）

从静态模拟卷 docx 延伸出的**离线练习闭环**：结构化题库单源 + 零依赖 Python 引擎，支持自答判分、错题本持久化、查解析、按域/随机/错题专练。

## 数据模型（bank.json）

```json
{
  "id": 1,
  "d": "D1 Fundamentals",
  "t": "single",        // single | multi | order | match | case
  "q": "题干...",
  "o": ["A选项","B选项","C选项","D选项"],
  "a": 1,                // single: int；multi/order: int 数组
  "e": "解析：为什么选B，其他选项为何错"
}
```

docx 生成器与 quiz 引擎**都** `json.load('bank.json')`，加题只改这一个文件。

## 答案解析规则（写进引擎，别让用户手输序号）

```python
def letters_to_idxs(s):
    out = []
    s = s.upper().replace(",", " ")
    toks = s.split() if " " in s else list(s)
    for tok in toks:
        tok = tok.strip()
        if len(tok) == 1 and "A" <= tok <= "Z":
            out.append(ord(tok) - ord("A"))
    return out

def parse_answer(t, s):
    idx = letters_to_idxs(s)
    if t == "single":
        return idx[0] if idx else None
    return idx                      # multi / order

def is_correct(t, got, ans):
    if t == "single":
        return got == ans
    if t == "multi":
        return sorted(got) == sorted(ans)   # 顺序无关、集合相等
    if t == "order":
        return got == ans                    # 顺序敏感
    return False
```

- multi 容错：连写 `AB` 必须识别（否则用户手输 `AB` 直接判错，体验崩）。
- order 必须顺序一致才判对。

## CLI 模式（sys.argv，无需 argparse）

| 调用 | 行为 |
|------|------|
| `python3 quiz.py` | 全卷按 id 顺序自测，输入 `q` 退出 |
| `python3 quiz.py wrong` | 只遍历 wrongbook.json 里的 id，答对则 `del` 并落盘 |
| `python3 quiz.py d3` | 按域过滤（bank 的 d 字段匹配 `D3`） |
| `python3 quiz.py random 10` | 随机抽 10 题 |
| `python3 quiz.py explain 12` | 打印第 12 题答案 + 解析 |
| `python3 quiz.py stats` | 错题本按域计数 |
| `python3 quiz.py reset` | 清空 wrongbook（二次确认） |

## 错题本持久化

`wrongbook.json` = `{ "<id>": <wrong_count_or_1> }`，与 quiz.py 同目录；退出/答对即时写盘，跨会话保留。

## 交付前验证（确定性、不手敲）

```bash
printf 'A\nq\n' | python3 quiz.py         # 加错题
printf 'B\n'   | python3 quiz.py wrong     # 答对移除
python3 -c "import quiz; ..."                # import 验证 multi/order 判分(用真实 t 筛选 id)
python3 quiz.py reset                        # 清空再打包
```

## 打包

`zip` 二进制可能不在 PATH，用标准库：

```python
import zipfile
with zipfile.ZipFile('quiz.zip','w',zipfile.ZIP_DEFLATED) as z:
    for f in ['bank.json','quiz.py','计划.docx','模拟卷.docx']:
        if os.path.exists(f): z.write(f, f)
```
