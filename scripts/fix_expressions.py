#!/usr/bin/env python3
"""修复 expressions.md 的断行段落和损坏链接"""
from pathlib import Path

path = Path("/home/elaine/work/courses/cs3110-textbook/zh-cn/chapters/basics/expressions.md")
text = path.read_text(encoding="utf-8")

old = ("OCaml 语法的主要部分是*表达式*。就像程序中的\n"
       "命令式语言主要由*命令*、程序组成\n"
       "函数式语言主要是由表达式构建的。例子\n"
       "表达式包括 `2+2` 和 `increment 21`。\n\n"
       "OCaml 手册对 [ 中的所有表达式都有完整的定义\n"
       "语言][表达式]。尽管该页面以相当神秘的概述开头，但如果你\n"
       "向下滚动，你会看到一些英文解释。不用担心\n"
       "现在正在研究该页面；只是知道它可供参考。\n\n"
       "[exprs]:  https://ocaml.org/manual/expr.html\n\n"
       "函数式语言中计算的主要任务是\"评估\"一个\n"
       "表达式到*值*。值是一个没有任何表达式的表达式\n"
       "仍有待执行的计算。所以，所有值都是表达式，但不是\n"
       "所有表达式都是值。值的示例包括 `2`、`true` 和\n"
       "`\"yay!\"`。\n\n"
       "OCaml 手册也有 [all the values][values] 的定义，不过\n"
       "同样，该页面主要用于参考而不是学习。\n\n"
       "[values]: https://ocaml.org/manual/values.html\n\n"
       "有时表达式可能无法计算出某个值。有两个原因\n"
       "这可能会发生：\n\n"
       "1. 表达式的求值引发异常。\n"
       "2. 表达式的求值永远不会终止（例如，它进入\"无限\n"
       "循环\"）。")

new = ("OCaml 语法的主要组成部分是*表达式*。命令式语言中的程序主要由*命令*构成，而函数式语言中的程序则主要由表达式构建。表达式的例子包括 `2+2` 和 `increment 21`。\n\n"
       "OCaml 手册有语言中所有[表达式][exprs]的完整定义。该页面开头相当晦涩，但如果你向下滚动，会看到一些英文解释。现在不必深入研究那个页面；只需知道它可以作为参考即可。\n\n"
       "[exprs]:  https://ocaml.org/manual/expr.html\n\n"
       "函数式语言中计算的主要任务是把表达式\u201c求值\u201d为*值*。值是一个不再有任何待计算步骤的表达式。所以，所有值都是表达式，但不是所有表达式都是值。值的示例包括 `2`、`true` 和 `\"yay!\"`。\n\n"
       "OCaml 手册也有[所有值][values]的定义，同样，该页面主要用于参考，而不是学习。\n\n"
       "[values]: https://ocaml.org/manual/values.html\n\n"
       "有时表达式可能无法计算出某个值。这有两种可能的原因：\n\n"
       "1. 表达式的求值引发了异常。\n"
       "2. 表达式的求值永远不会终止（例如，它进入了\u201c无限循环\u201d）。")

if old in text:
    text = text.replace(old, new, 1)
    path.write_text(text, encoding="utf-8")
    print("SUCCESS")
else:
    # 逐行对比找到差异
    for i, line in enumerate(text.splitlines()):
        if "OCaml 手册对" in line:
            print(f"Line {i}: {repr(line)}")
    print("NOT FOUND - see debug above")
