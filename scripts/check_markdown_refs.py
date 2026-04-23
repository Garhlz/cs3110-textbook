#!/usr/bin/env python3
"""Check Markdown reference-style links in zh-cn files."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ZH = ROOT / "zh-cn"

REF_DEF_RE = re.compile(r"^\s{0,3}\[([^\]]+)\]:", re.M)
REF_USE_RE = re.compile(r"(?<!!)\[[^\]\n]+\]\[([^\]\n]*)\]")


def main() -> int:
    errors: list[str] = []
    for path in sorted(ZH.rglob("*.md")):
        if "_build" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        defs = {m.group(1) for m in REF_DEF_RE.finditer(text)}
        for match in REF_USE_RE.finditer(text):
            label = match.group(1)
            if not label:
                continue
            if "." in label:
                continue
            if label not in defs:
                rel = path.relative_to(ROOT)
                errors.append(f"{rel}: undefined reference label [{label}]")
    if errors:
        print("\n".join(errors))
        return 1
    print("OK: reference-style links resolve within each file")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
