#!/usr/bin/env python3
from pathlib import Path

p = Path("/home/elaine/work/courses/cs3110-textbook/zh-cn/chapters/basics/expressions.md")
t = p.read_text(encoding="utf-8")

old = '\n函数式语言中计算的主要任务是\u201c评估\u201d一个\n表达式到*值*。值是一个没有任何表达式 的表达式\n仍有待执行的计算。所以，所有值都是表达式，但不是\n所有表达式都是值。值的示例包括 `2`、`true` 和\n`\u201cyay!\u201d`。'
new = '\n函数式语言中计算的主要任务是把表达式\u201c求值\u201d为*值*。值是一个不再有任何待计算步骤的表达式。所以，所有值都是表达式，但不是所有表达式都是值。值的示例包括 `2`、`true` 和 `"yay!"`。'

if old in t:
    t = t.replace(old, new, 1)
    p.write_text(t, encoding="utf-8")
    print("SUCCESS")
else:
    print("NOT FOUND")
