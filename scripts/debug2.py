#!/usr/bin/env python3
from pathlib import Path

p = Path("/home/elaine/work/courses/cs3110-textbook/zh-cn/chapters/basics/expressions.md")
t = p.read_text(encoding="utf-8")

# 提取23-27行（0-indexed 22-26）
lines = t.splitlines()
chunk = "\n".join(lines[22:27])
print(repr(chunk))
