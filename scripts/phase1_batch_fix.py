#!/usr/bin/env python3
"""
Phase 1: 批量自动修复 zh-cn/chapters 中的系统性翻译错误。
- 您 → 你（跳过 front matter、代码块、行内代码）
- 奥卡米尔 → OCaml
- 图书馆 → 库（仅在上下文确为 library 语义时）
- Ocamllex → OCamllex
"""

import re
import sys
from pathlib import Path

CHAPTERS_DIR = Path(__file__).parent.parent / "zh-cn" / "chapters"


def is_code_fence_line(line: str) -> bool:
    return bool(re.match(r"^(`{3,}|~{3,})", line.strip()))


def split_blocks(text: str):
    """
    将文档分割为 (block_type, content) 序列。
    block_type: 'front_matter' | 'code' | 'text'
    """
    lines = text.splitlines(keepends=True)
    blocks = []
    i = 0
    n = len(lines)

    # YAML front matter
    if lines and lines[0].strip() == "---":
        j = 1
        while j < n and lines[j].strip() != "---":
            j += 1
        fm = "".join(lines[0 : j + 1])
        blocks.append(("front_matter", fm))
        i = j + 1

    while i < n:
        line = lines[i]
        if is_code_fence_line(line):
            # 找到匹配的结束围栏
            fence_match = re.match(r"^(`{3,}|~{3,})", line.strip())
            fence_str = fence_match.group(1)
            j = i + 1
            while j < n:
                if re.match(r"^" + re.escape(fence_str) + r"\s*$", lines[j].strip()):
                    break
                j += 1
            code_block = "".join(lines[i : j + 1])
            blocks.append(("code", code_block))
            i = j + 1
        else:
            # 收集连续的文本行
            start = i
            while i < n and not is_code_fence_line(lines[i]):
                i += 1
            text_block = "".join(lines[start:i])
            blocks.append(("text", text_block))

    return blocks


def fix_text_block(text: str) -> str:
    """对普通文本块应用修复，保护行内代码。"""
    # 把行内代码暂时替换为占位符
    inline_codes = []

    def save_inline_code(m):
        idx = len(inline_codes)
        inline_codes.append(m.group(0))
        return f"\x00INLINECODE{idx}\x00"

    text = re.sub(r"`[^`]+`", save_inline_code, text)

    # 修复 1: 您 → 你
    text = text.replace("您", "你")

    # 修复 2: 奥卡米尔 → OCaml
    text = text.replace("奥卡米尔", "OCaml")

    # 修复 3: 图书馆 → 库（仅当紧跟在技术语境中）
    # 不能无脑替换"图书馆"，因为可能有"图书馆员"、"图书馆学"等
    # 这里匹配：句中"图书馆"前后不是"员"、"学"
    text = re.sub(r"图书馆(?![员学])", "库", text)

    # 修复 4: Ocamllex → OCamllex（大小写修正）
    text = re.sub(r"\bOcamllex\b", "OCamllex", text)
    text = re.sub(r"\bOcamlyacc\b", "OCamlyacc", text)

    # 恢复行内代码
    for idx, code in enumerate(inline_codes):
        text = text.replace(f"\x00INLINECODE{idx}\x00", code)

    return text


def process_file(path: Path) -> tuple[int, list[str]]:
    """返回 (变更数, [变更描述])"""
    original = path.read_text(encoding="utf-8")
    blocks = split_blocks(original)

    result_parts = []
    changes = []

    for block_type, content in blocks:
        if block_type in ("front_matter", "code"):
            result_parts.append(content)
        else:
            fixed = fix_text_block(content)
            if fixed != content:
                # 记录每种变更
                if "您" in content and "你" not in content or content.count("您") > 0:
                    n = content.count("您")
                    if n:
                        changes.append(f"  您→你: {n} 处")
                if "奥卡米尔" in content:
                    changes.append(f"  奥卡米尔→OCaml: {content.count('奥卡米尔')} 处")
                if re.search(r"图书馆(?![员学])", content):
                    n = len(re.findall(r"图书馆(?![员学])", content))
                    changes.append(f"  图书馆→库: {n} 处")
                if re.search(r"\bOcamllex\b|\bOcamlyacc\b", content):
                    changes.append(f"  大小写修正")
            result_parts.append(fixed)

    new_content = "".join(result_parts)

    if new_content != original:
        path.write_text(new_content, encoding="utf-8")
        return len(changes), changes
    return 0, []


def main():
    md_files = sorted(CHAPTERS_DIR.rglob("*.md"))
    total_files = 0
    total_changes = 0

    for f in md_files:
        count, descs = process_file(f)
        if count > 0:
            rel = f.relative_to(CHAPTERS_DIR.parent.parent)
            print(f"[修改] {rel}")
            for d in descs:
                print(d)
            total_files += 1
            total_changes += count

    print(f"\n完成：共修改 {total_files} 个文件，{total_changes} 类变更。")


if __name__ == "__main__":
    main()
