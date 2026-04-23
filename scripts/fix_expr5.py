#!/usr/bin/env python3
from pathlib import Path

p = Path("/home/elaine/work/courses/cs3110-textbook/zh-cn/chapters/basics/expressions.md")
t = p.read_text(encoding="utf-8")
lines = t.splitlines(keepends=True)

# 找到第22行（0-indexed）开始的段落
# 第22行是空行，第23行是 函数式...
# 用行号定位并直接替换
start_marker = "\u51fd\u6570\u5f0f\u8bed\u8a00\u4e2d\u8ba1\u7b97\u7684\u4e3b\u8981\u4efb\u52a1\u662f\u201c\u8bc4\u4f30\u201d\u4e00\u4e2a"
new_para = "\u51fd\u6570\u5f0f\u8bed\u8a00\u4e2d\u8ba1\u7b97\u7684\u4e3b\u8981\u4efb\u52a1\u662f\u628a\u8868\u8fbe\u5f0f\u201c\u6c42\u5024\u201d\u4e3a*\u5024*\u3002\u5024\u662f\u4e00\u4e2a\u4e0d\u518d\u6709\u4efb\u4f55\u5f85\u8ba1\u7b97\u6b65\u9aa4\u7684\u8868\u8fbe\u5f0f\u3002\u6240\u4ee5\uff0c\u6240\u6709\u5024\u90fd\u662f\u8868\u8fbe\u5f0f\uff0c\u4f46\u4e0d\u662f\u6240\u6709\u8868\u8fbe\u5f0f\u90fd\u662f\u5024\u3002\u5024\u7684\u793a\u4f8b\u5305\u62ec `2`\u3001`true` \u548c `\"yay!\"`\u3002\n"

result = []
i = 0
while i < len(lines):
    if lines[i].startswith(start_marker[:10]):
        # 找到起始行，收集直到 `"yay!"`
        j = i
        while j < len(lines) and not lines[j].startswith('`\u201c') and not lines[j].strip().startswith('`"yay'):
            j += 1
        # j is the last line of this paragraph
        result.append(new_para)
        i = j + 1  # skip all old lines
    else:
        result.append(lines[i])
        i += 1

new_text = "".join(result)
if new_text != t:
    p.write_text(new_text, encoding="utf-8")
    print("SUCCESS")
else:
    print("NO CHANGE")
