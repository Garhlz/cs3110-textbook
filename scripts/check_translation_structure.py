#!/usr/bin/env python3
"""Check that zh-cn Markdown preserves source MyST/Jupyter structure."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
OUT = ROOT / "zh-cn"


PATTERNS = {
    "fences": re.compile(r"^\s*(`{3,}|~{3,})", re.M),
    "code_cell": re.compile(r"^\s*```\{code-cell\}.*$", re.M),
    "directives": re.compile(r"^\s*```\{(note|tip|warning|important|epigraph|admonition)\}.*$", re.M),
    "jinja": re.compile(r"\{\{.*?\}\}"),
    "refdefs": re.compile(r"^\s{0,3}\[[^\]]+\]:\s+\S+", re.M),
    "myst_targets": re.compile(r"^\s*\([A-Za-z0-9_-]+\)=\s*$", re.M),
    "html_comments": re.compile(r"<!--.*?-->", re.S),
}

MINIMUM_PATTERNS = {"fences", "directives", "refdefs"}


def count(pattern: re.Pattern[str], text: str) -> int:
    return len(pattern.findall(text))


def front_matter(text: str) -> str:
    if not text.startswith("---\n"):
        return ""
    end = text.find("\n---", 4)
    if end == -1:
        return "BROKEN"
    return text[: end + 4]


def main() -> int:
    errors: list[str] = []
    files = [SRC / "cover.md"] + sorted((SRC / "chapters").glob("**/*.md"))
    for src in files:
        rel = src.relative_to(SRC)
        dst = OUT / rel
        if not dst.exists():
            errors.append(f"missing: {rel}")
            continue
        s = src.read_text(encoding="utf-8")
        d = dst.read_text(encoding="utf-8")
        for name, pattern in PATTERNS.items():
            sc = count(pattern, s)
            dc = count(pattern, d)
            if name in MINIMUM_PATTERNS:
                if dc < sc:
                    errors.append(f"{rel}: {name} count {sc} -> {dc}")
            elif sc != dc:
                errors.append(f"{rel}: {name} count {sc} -> {dc}")
        if front_matter(s) and front_matter(s) != front_matter(d):
            errors.append(f"{rel}: front matter changed")

    if errors:
        print("\n".join(errors))
        return 1
    print(f"OK: {len(files)} files preserve checked structures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
