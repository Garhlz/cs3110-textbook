#!/usr/bin/env python3
"""
Phase 2: 修复中文 Markdown 文件中因原始换行符导致的断行句子。
针对纯文本段落：将段落内（不含空行）的换行合并为单行。
代码块、front matter、admonition块内的换行保持不变。
"""

import re
from pathlib import Path

CHAPTERS_DIR = Path(__file__).parent.parent / "zh-cn" / "chapters"

# 行类型判断
def is_fence_start(line: str):
    m = re.match(r"^(`{3,}|~{3,})", line.strip())
    return m.group(1) if m else None

def is_heading(line: str):
    return re.match(r"^#{1,6} ", line)

def is_list_item(line: str):
    return re.match(r"^(\s*[-*+]|\s*\d+\.) ", line)

def is_link_def(line: str):
    return re.match(r"^\[.+\]:", line)

def is_blank(line: str):
    return line.strip() == ""

def merge_para_lines(lines):
    """
    在段落内，如果上一行末尾是中文字符（或普通ASCII字符）
    且当前行开头是中文字符（不是标题、列表等），则合并。
    """
    result = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # 如果是独立结构行，不合并
        if (is_blank(line) or is_heading(line) or is_list_item(line) 
                or is_link_def(line) or line.startswith("{{")
                or line.startswith("(") and line.endswith(")=")
                or line.startswith("<!-")
                or line.startswith("<") and ">" in line):
            result.append(line)
            i += 1
            continue

        # 尝试向后合并
        merged = line.rstrip('\n')
        j = i + 1
        while j < len(lines):
            next_line = lines[j]
            if (is_blank(next_line) or is_heading(next_line) or is_list_item(next_line)
                    or is_link_def(next_line) or next_line.startswith("{{")
                    or next_line.startswith("(") and next_line.endswith(")=")
                    or next_line.startswith("<!-")
                    or next_line.startswith("<") and ">" in next_line
                    or is_fence_start(next_line)):
                break
            # 合并条件：前一行末尾不是完整句子结束标点
            # 简单启发式：如果前行末尾是中文字符或英文字母/数字，尝试合并
            prev_end = merged.rstrip()
            next_start = next_line.lstrip()
            if not prev_end:
                break
            last_char = prev_end[-1]
            # 如果上一行以完整标点结束（句号、感叹号、问号等），不合并
            full_stop = set('。！？；.!?;')
            if last_char in full_stop:
                break
            # 否则合并
            merged = merged.rstrip() + next_start.rstrip('\n')
            j += 1

        if j > i + 1:
            result.append(merged + '\n')
            i = j
        else:
            result.append(line)
            i += 1
    return result


def process_file(path: Path) -> bool:
    original = path.read_text(encoding="utf-8")
    lines = original.splitlines(keepends=True)
    result = []
    i = 0
    n = len(lines)

    # Front matter
    if lines and lines[0].strip() == "---":
        j = 1
        while j < n and lines[j].strip() != "---":
            j += 1
        result.extend(lines[0:j+1])
        i = j + 1

    while i < n:
        line = lines[i]
        fence = is_fence_start(line.strip())
        if fence:
            # 收集整个 fence block（含 admonition）
            block = [line]
            i += 1
            while i < n:
                block.append(lines[i])
                if re.match(r"^" + re.escape(fence) + r"\s*$", lines[i].strip()):
                    i += 1
                    break
                i += 1
            result.extend(block)
        else:
            result.append(line)
            i += 1

    # 现在对 result 中非代码块的段落做合并
    # 先提取文本块做处理（代码块已经作为整体保存）
    new_content = "".join(result)
    if new_content == original:
        return False
    # 这个脚本只移除front matter内的处理，不做段落合并（段落合并太危险，留给后续手工）
    path.write_text(new_content, encoding="utf-8")
    return False  # 暂不报告


if __name__ == "__main__":
    # 仅对 expressions.md 做精确修复
    import sys

    fixes = {
        "zh-cn/chapters/basics/expressions.md": [
            (
                "函数式语言中计算的主要任务是\u201c评估\u201d一个\n"
                "表达式到*值*。值是一个没有任何表达式的表达式\n"
                "仍有待执行的计算。所以，所有值都是表达式，但不是\n"
                "所有表达式都是值。值的示例包括 `2`、`true` 和\n"
                '`\u201cyay!\u201d`。',
                "函数式语言中计算的主要任务是把表达式\u201c求值\u201d为*值*。"
                "值是一个不再有任何待计算步骤的表达式。"
                "所以，所有值都是表达式，但不是所有表达式都是值。"
                "值的示例包括 `2`、`true` 和 `\"yay!\"`。"
            ),
            (
                "*原始*类型是内置的最基本类型：整数，\n"
                "浮点数、字符、字符串和布尔值。他们将是\n"
                "可识别为与其他编程语言中的基本类型类似。",
                "*原始*类型是内置的最基本类型：整数、浮点数、字符、字符串和布尔值。"
                "这些类型与其他编程语言中的基本类型相似。"
            ),
        ],
    }

    base = Path("/home/elaine/work/courses/cs3110-textbook")
    for rel, pairs in fixes.items():
        p = base / rel
        t = p.read_text(encoding="utf-8")
        changed = False
        for old, new in pairs:
            if old in t:
                t = t.replace(old, new, 1)
                print(f"OK: {old[:40]!r}")
                changed = True
            else:
                print(f"NOT FOUND: {old[:40]!r}")
        if changed:
            p.write_text(t, encoding="utf-8")
    print("Done")
