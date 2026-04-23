#!/usr/bin/env python3
"""
Phase 1b: 修复 Phase 1 遗漏的 admonition 块中的 您→你 等替换。
Admonition 块格式如 ```{note}...``` 属于自然语言，Phase 1 错误地将其
当作代码块跳过了。
"""

import re
from pathlib import Path

CHAPTERS_DIR = Path(__file__).parent.parent / "zh-cn" / "chapters"

# 真正的代码块（含语言标识符，如 ocaml、console、python 等）
CODE_LANG_RE = re.compile(r"^(`{3,}|~{3,})\s*(\w+)\s*$")
# admonition 块（含指令名，如 {note}、{tip} 等）
ADMONITION_RE = re.compile(r"^(`{3,}|~{3,})\s*\{")
# 纯代码块 ``` 无标识
BARE_FENCE_RE = re.compile(r"^(`{3,}|~{3,})\s*$")


def is_admonition_fence(line: str) -> bool:
    return bool(ADMONITION_RE.match(line.strip()))


def is_code_fence(line: str) -> bool:
    stripped = line.strip()
    return bool(CODE_LANG_RE.match(stripped)) or bool(BARE_FENCE_RE.match(stripped))


def fix_admonition_text(text: str) -> str:
    text = text.replace("您", "你")
    text = text.replace("奥卡米尔", "OCaml")
    text = re.sub(r"图书馆(?![员学])", "库", text)
    return text


def process_file(path: Path) -> bool:
    original = path.read_text(encoding="utf-8")
    lines = original.splitlines(keepends=True)
    result = []
    i = 0
    n = len(lines)

    # Skip front matter
    if lines and lines[0].strip() == "---":
        j = 1
        while j < n and lines[j].strip() != "---":
            j += 1
        result.extend(lines[0 : j + 1])
        i = j + 1

    while i < n:
        line = lines[i]
        stripped = line.strip()
        if is_admonition_fence(stripped):
            # admonition block: collect content and fix natural language
            fence_match = re.match(r"^(`{3,}|~{3,})", stripped)
            fence_str = fence_match.group(1)
            result.append(line)
            i += 1
            block_lines = []
            while i < n:
                if re.match(r"^" + re.escape(fence_str) + r"\s*$", lines[i].strip()):
                    break
                block_lines.append(lines[i])
                i += 1
            # Fix natural language in block
            block_text = "".join(block_lines)
            fixed = fix_admonition_text(block_text)
            result.append(fixed)
            if i < n:
                result.append(lines[i])  # closing fence
                i += 1
        elif is_code_fence(stripped) or CODE_LANG_RE.match(stripped):
            # true code block: skip as-is
            fence_match = re.match(r"^(`{3,}|~{3,})", stripped)
            fence_str = fence_match.group(1)
            result.append(line)
            i += 1
            while i < n:
                result.append(lines[i])
                if re.match(r"^" + re.escape(fence_str) + r"\s*$", lines[i].strip()):
                    i += 1
                    break
                i += 1
        else:
            result.append(line)
            i += 1

    new_content = "".join(result)
    if new_content != original:
        path.write_text(new_content, encoding="utf-8")
        return True
    return False


def main():
    md_files = sorted(CHAPTERS_DIR.rglob("*.md"))
    total = 0
    for f in md_files:
        if process_file(f):
            print(f"[修改] {f.relative_to(CHAPTERS_DIR.parent.parent)}")
            total += 1
    print(f"\n完成：共修改 {total} 个文件。")


if __name__ == "__main__":
    main()
