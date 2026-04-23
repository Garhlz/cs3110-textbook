#!/usr/bin/env python3
"""
Phase 3: 中文 Markdown 段落合并 + 语言润色脚本。

对每个文件的普通文本段落，将因英文行宽限制而产生的
中途换行合并为单行（中文不需要行内换行）。
代码块、front matter、admonition 块、标题、列表保持不变。
"""

import re
from pathlib import Path


def is_special_line(line: str) -> bool:
    """是否为不应合并的特殊结构行"""
    stripped = line.strip()
    return (
        not stripped  # 空行
        or re.match(r"^#{1,6} ", stripped)  # 标题
        or re.match(r"^(\s*[-*+]|\s*\d+\.\s)", line)  # 列表
        or re.match(r"^\[.+\]:", stripped)  # 引用式链接定义
        or stripped.startswith("{{")  # Jinja substitution
        or re.match(r"^\(.+\)=$", stripped)  # MyST anchor
        or stripped.startswith("<!-")  # HTML 注释
        or stripped.startswith("<")  # HTML 标签
        or stripped.startswith("|")  # 表格
        or stripped.startswith("(install")  # 锚点
    )


def merge_paragraph_lines(lines: list[str]) -> list[str]:
    """
    将段落内的续行合并到上一行。
    规则：连续的非空、非特殊行，且上一行末尾不是完整句子结束符，则合并。
    中文句子结束符：。！？；（注意：，: 不是结束符）
    """
    result = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if is_special_line(line):
            result.append(line)
            i += 1
            continue

        # 尝试合并后续续行
        merged = line.rstrip("\n")
        j = i + 1
        while j < len(lines):
            next_line = lines[j]
            if not next_line.strip():
                break  # 空行，段落结束
            if is_special_line(next_line):
                break
            prev = merged.rstrip()
            if not prev:
                break
            last = prev[-1]
            # 如果上一行以完整标点结束，不合并
            if last in "。！？；.!?;":
                break
            # 合并，去掉首尾空白后直接拼接（无空格，因为中文不需要）
            next_stripped = next_line.strip()
            # 如果上一行末尾是 ASCII 字符且下一行开头也是 ASCII，加空格
            if (re.match(r"[a-zA-Z0-9`)\]>\"']", prev[-1])
                    and re.match(r"[a-zA-Z0-9`(\[<\"'\\]", next_stripped[0] if next_stripped else " ")):
                merged = prev + " " + next_stripped
            else:
                merged = prev + next_stripped
            j += 1

        if j > i + 1:
            result.append(merged + "\n")
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
        result.extend(lines[0 : j + 1])
        i = j + 1

    while i < n:
        line = lines[i]
        stripped = line.strip()
        fence_m = re.match(r"^(`{3,}|~{3,})", stripped)
        if fence_m:
            fence = fence_m.group(1)
            block = [line]
            i += 1
            while i < n:
                block.append(lines[i])
                if re.match(r"^" + re.escape(fence) + r"\s*$", lines[i].strip()):
                    i += 1
                    break
                i += 1
            # 判断是否是 admonition（含指令名如 {note}）
            is_admonition = bool(re.match(r"^(`{3,}|~{3,})\s*\{", stripped))
            if is_admonition:
                # admonition 内部也做段落合并（对其中的文本行）
                inner = block[1:-1]
                merged_inner = merge_paragraph_lines(inner)
                result.append(block[0])
                result.extend(merged_inner)
                result.append(block[-1])
            else:
                result.extend(block)
        else:
            result.append(line)
            i += 1

    # 对整个结果做段落合并（处理 front matter 之外的普通文本）
    final = merge_paragraph_lines(result)
    new_content = "".join(final)

    if new_content != original:
        path.write_text(new_content, encoding="utf-8")
        return True
    return False


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 phase3_merge_paragraphs.py <file_or_dir> ...")
        sys.exit(1)

    total = 0
    for arg in sys.argv[1:]:
        p = Path(arg)
        if p.is_dir():
            for f in sorted(p.rglob("*.md")):
                if process_file(f):
                    print(f"[合并] {f}")
                    total += 1
        elif p.is_file():
            if process_file(p):
                print(f"[合并] {p}")
                total += 1

    print(f"\n完成：{total} 个文件已合并段落换行。")
