#!/usr/bin/env python3
"""
修复 phase3_merge_paragraphs.py 造成的代码块破坏。
恢复被错误合并的 fence 行与内容行。
"""

import re
from pathlib import Path


def repair_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    result = []
    changed = False

    for line in lines:
        stripped = line.strip()
        # 检测是否是一行里同时包含 fence 开始和内容（被错误合并的）
        # Pattern 1: ```{directive}content  (admonition fence + content merged)
        m = re.match(r"^(`{3,})\{([^}]+)\}(.+)$", stripped)
        if m:
            fence = m.group(1)
            directive = m.group(2)
            content = m.group(3).strip()
            result.append(f"{fence}{{{directive}}}\n")
            if content:
                result.append(f"{content}\n")
            changed = True
            continue

        # Pattern 2: ```lang content...```  (code fence + content + closing fence)
        m = re.match(r"^(`{3,})(\w+)\s+(.+?)(`{3,})$", stripped)
        if m:
            fence_open = m.group(1)
            lang = m.group(2)
            content = m.group(3).strip()
            fence_close = m.group(4)
            result.append(f"{fence_open}{lang}\n")
            if content:
                result.append(f"{content}\n")
            result.append(f"{fence_close}\n")
            changed = True
            continue

        # Pattern 3: ```lang content (code fence + content, no closing fence on same line)
        m = re.match(r"^(`{3,})(\w+)\s+(.+)$", stripped)
        if m:
            fence = m.group(1)
            lang = m.group(2)
            content = m.group(3).strip()
            # Verify it's not just ```ocaml :tags: ...``` style
            if not content.startswith(":"):
                result.append(f"{fence}{lang}\n")
                if content:
                    result.append(f"{content}\n")
                changed = True
                continue

        # Pattern 4: content``` (content + closing fence merged)
        m = re.match(r"^(.+?)(`{3,})\s*$", stripped)
        if m and not stripped.startswith("`"):
            content = m.group(1).strip()
            fence = m.group(2)
            result.append(f"{content}\n")
            result.append(f"{fence}\n")
            changed = True
            continue

        result.append(line)

    if changed:
        path.write_text("".join(result), encoding="utf-8")
    return changed


if __name__ == "__main__":
    import sys
    base = Path("/home/elaine/work/courses/cs3110-textbook")
    targets = [
        base / "zh-cn/chapters/preface/about.md",
        base / "zh-cn/chapters/preface/install.md",
        base / "zh-cn/chapters/intro/3110.md",
        base / "zh-cn/chapters/intro/future.md",
        base / "zh-cn/chapters/intro/intro.md",
        base / "zh-cn/chapters/intro/past.md",
        base / "zh-cn/chapters/intro/present.md",
        base / "zh-cn/chapters/intro/summary.md",
    ]
    for p in targets:
        if repair_file(p):
            print(f"[修复] {p.relative_to(base)}")
        else:
            print(f"[无变更] {p.relative_to(base)}")
