#!/usr/bin/env python3
from pathlib import Path

p = Path("/home/elaine/work/courses/cs3110-textbook/zh-cn/chapters/basics/expressions.md")
t = p.read_text(encoding="utf-8")

old = '函数式语言中计算的主要任务是\u201c评估\u201d一个\n表达式到*值*。值是一个没有任何表达式的表达式\n仍有待执行的计算。所以，所有值都是表达式，但不是\n所有表达式都是值。值的示例包括 `2`、`true` 和\n`\u201cyay!\u201d`。'

# 先检查文件中实际的引号
idx = t.find("函数式语言中计算的主要任务是")
snippet = t[idx:idx+20]
print("Actual chars:", [hex(ord(c)) for c in snippet])
print("Repr:", repr(snippet))
