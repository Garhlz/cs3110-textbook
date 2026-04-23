#!/usr/bin/env python3
"""Translate the CS 3110 MyST Markdown source tree to zh-cn.

The script is intentionally conservative: it preserves notebook metadata,
code cells, code fences, Jinja substitutions, reference definitions, URLs,
inline code, HTML tags, and math spans. Only visible prose is sent to the
translation backend.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import shutil
import sys
import time
from pathlib import Path
from typing import Callable

import requests
import yaml


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
OUT = ROOT / "zh-cn"
CACHE_PATH = ROOT / ".translation-cache.json"
LOG_PATH = ROOT / "translation-failures.log"

TRANSLATABLE_DIRECTIVES = {
    "admonition",
    "attention",
    "caution",
    "danger",
    "epigraph",
    "error",
    "hint",
    "important",
    "note",
    "seealso",
    "tip",
    "warning",
}

PROTECT_RE = re.compile(
    r"(`[^`\n]+`)"
    r"|(\$\$.*?\$\$)"
    r"|(\$[^$\n]+\$)"
    r"|(\{\{.*?\}\})"
    r"|(<[^>\n]+>)"
    r"|(&[A-Za-z0-9#]+;)"
    r"|(!?\[[^\]\n]*\]\([^)]+\))"
    r"|(!?\[[^\]\n]*\]\[[^\]\n]*\])"
    r"|(https?://[^\s)]+)",
    re.S,
)

ASCII_ONLY_RE = re.compile(r"^[\W\d_A-Za-z]+$")
REF_DEF_RE = re.compile(r"^\s{0,3}\[[^\]]+\]:\s+\S+")
MYST_TARGET_RE = re.compile(r"^\s*\([A-Za-z0-9_-]+\)=\s*$")
JINJA_LINE_RE = re.compile(r"^\s*\{\{.*\}\}\s*$")
HTML_COMMENT_RE = re.compile(r"^\s*<!--.*-->\s*$")
FENCE_RE = re.compile(r"^(\s*)(`{3,}|~{3,})(.*)$")


def load_cache(path: Path) -> dict[str, str]:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def save_cache(path: Path, cache: dict[str, str]) -> None:
    path.write_text(
        json.dumps(cache, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def should_translate(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return False
    if JINJA_LINE_RE.match(stripped):
        return False
    if HTML_COMMENT_RE.match(stripped):
        return False
    if REF_DEF_RE.match(stripped):
        return False
    if MYST_TARGET_RE.match(stripped):
        return False
    if ASCII_ONLY_RE.match(stripped) and not re.search(r"[A-Za-z]{2,}", stripped):
        return False
    return bool(re.search(r"[A-Za-z]{2,}", stripped))


def protect(text: str) -> tuple[str, dict[str, str]]:
    mapping: dict[str, str] = {}

    def repl(match: re.Match[str]) -> str:
        token = f"__KEEP_{len(mapping):04d}__"
        mapping[token] = match.group(0)
        return token

    return PROTECT_RE.sub(repl, text), mapping


def unprotect(text: str, mapping: dict[str, str]) -> str:
    for token, original in mapping.items():
        text = text.replace(token, original)
    return text


def postprocess_translation(text: str, source: str) -> str:
    replacements = {
        "蟒蛇": "Python",
        "爪哇": "Java",
        "奥卡姆": "OCaml",
        "沙丘": "Dune",
        "朱皮特": "Jupyter",
        "视觉工作室代码": "Visual Studio Code",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    if re.search(r"\bfunctions?\b", source, re.I):
        text = text.replace("功能", "函数")
        text = text.replace("职能", "函数")
    if re.search(r"\btype inference\b", source, re.I):
        text = text.replace("类型推理", "类型推断")
    return text


def google_translate(text: str, session: requests.Session, retries: int = 4) -> str:
    params = {
        "client": "gtx",
        "sl": "en",
        "tl": "zh-CN",
        "dt": "t",
        "q": text,
    }
    url = "https://translate.googleapis.com/translate_a/single"
    last_error = ""
    for attempt in range(retries):
        try:
            response = session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            translated = "".join(part[0] for part in data[0] if part and part[0])
            return html.unescape(translated)
        except Exception as exc:  # noqa: BLE001 - log and retry external failures.
            last_error = repr(exc)
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(last_error)


class BatchTranslator:
    def __init__(
        self,
        translate_backend: Callable[[str], str],
        cache: dict[str, str],
        failures: list[str],
        batch_chars: int = 4500,
        batch_items: int = 24,
    ) -> None:
        self.translate_backend = translate_backend
        self.cache = cache
        self.failures = failures
        self.batch_chars = batch_chars
        self.batch_items = batch_items
        self.pending: dict[str, tuple[str, dict[str, str], bool, str]] = {}

    @staticmethod
    def marker(key: str) -> str:
        return f"@@ZH_SEG_{key}@@"

    def translate_text(self, text: str, context: str) -> str:
        has_trailing_newline = text.endswith("\n")
        if not should_translate(text):
            return text

        protected, mapping = protect(text)
        if not should_translate(protected):
            return text

        key = hashlib.sha256(protected.encode("utf-8")).hexdigest()
        if key in self.cache:
            translated = unprotect(self.cache[key], mapping)
            translated = postprocess_translation(translated, text)
            if has_trailing_newline and not translated.endswith("\n"):
                translated += "\n"
            return translated

        self.pending[key] = (protected, mapping, has_trailing_newline, context)
        return self.marker(key)

    def resolve(self, text: str) -> str:
        if not self.pending:
            return text

        items = list(self.pending.items())
        for batch in self._batches(items):
            self._translate_batch(batch)

        for key, (_protected, mapping, has_trailing_newline, _context) in items:
            marker = self.marker(key)
            if marker not in text:
                continue
            translated = unprotect(self.cache.get(key, _protected), mapping)
            translated = postprocess_translation(translated, _protected)
            if has_trailing_newline and not translated.endswith("\n"):
                translated += "\n"
            text = text.replace(marker, translated)

        self.pending.clear()
        return text

    def _batches(
        self, items: list[tuple[str, tuple[str, dict[str, str], bool, str]]]
    ) -> list[list[tuple[str, tuple[str, dict[str, str], bool, str]]]]:
        batches: list[list[tuple[str, tuple[str, dict[str, str], bool, str]]]] = []
        current: list[tuple[str, tuple[str, dict[str, str], bool, str]]] = []
        current_chars = 0
        for item in items:
            protected = item[1][0]
            if (
                current
                and (
                    len(current) >= self.batch_items
                    or current_chars + len(protected) > self.batch_chars
                )
            ):
                batches.append(current)
                current = []
                current_chars = 0
            current.append(item)
            current_chars += len(protected)
        if current:
            batches.append(current)
        return batches

    def _translate_batch(
        self, batch: list[tuple[str, tuple[str, dict[str, str], bool, str]]]
    ) -> None:
        if len(batch) == 1:
            key, (protected, _mapping, _has_newline, context) = batch[0]
            try:
                self.cache[key] = self.translate_backend(protected)
            except Exception as exc:  # noqa: BLE001
                self.failures.append(f"{context}: {exc}")
                self.cache[key] = protected
            return

        delimiters = [f"<<<ZHSEG{i:04d}_{key[:12]}>>>" for i, (key, _data) in enumerate(batch)]
        joined_parts: list[str] = []
        for delimiter, (_key, (protected, _mapping, _has_newline, _context)) in zip(
            delimiters, batch
        ):
            if joined_parts:
                joined_parts.append(delimiter)
            joined_parts.append(protected)
        joined = "\n\n".join(joined_parts)

        try:
            translated = self.translate_backend(joined)
        except Exception as exc:  # noqa: BLE001
            for key, (protected, _mapping, _has_newline, context) in batch:
                self.failures.append(f"{context}: {exc}")
                self.cache[key] = protected
            return

        pieces = [translated]
        for delimiter in delimiters[1:]:
            next_pieces: list[str] = []
            for piece in pieces:
                next_pieces.extend(piece.split(delimiter))
            pieces = next_pieces

        if len(pieces) != len(batch):
            for key, (protected, _mapping, _has_newline, context) in batch:
                try:
                    self.cache[key] = self.translate_backend(protected)
                except Exception as exc:  # noqa: BLE001
                    self.failures.append(f"{context}: {exc}")
                    self.cache[key] = protected
            return

        for (key, _data), piece in zip(batch, pieces):
            self.cache[key] = piece.strip()


def directive_name(fence_info: str) -> str | None:
    info = fence_info.strip()
    match = re.match(r"^\{([A-Za-z0-9_-]+)\}", info)
    if not match:
        return None
    return match.group(1)


def translate_markdown_lines(
    lines: list[str],
    translator: BatchTranslator,
    context: str,
    in_front_matter: bool = False,
) -> list[str]:
    out: list[str] = []
    paragraph: list[str] = []

    def flush_paragraph() -> None:
        nonlocal paragraph
        if not paragraph:
            return
        text = "".join(paragraph)
        out.append(translator.translate_text(text, context))
        paragraph = []

    i = 0
    if in_front_matter:
        while i < len(lines):
            out.append(lines[i])
            if i > 0 and lines[i].strip() == "---":
                i += 1
                break
            i += 1

    while i < len(lines):
        line = lines[i]
        fence = FENCE_RE.match(line)
        if fence:
            flush_paragraph()
            fence_marker = fence.group(2)
            directive = directive_name(fence.group(3))
            block = [line]
            i += 1
            inner: list[str] = []
            while i < len(lines):
                current = lines[i]
                if current.lstrip().startswith(fence_marker):
                    break
                inner.append(current)
                i += 1
            closing = lines[i] if i < len(lines) else ""
            if directive in TRANSLATABLE_DIRECTIVES:
                block.extend(
                    translate_markdown_lines(
                        inner,
                        translator,
                        context,
                    )
                )
            else:
                block.extend(inner)
            if closing:
                block.append(closing)
                i += 1
            out.extend(block)
            continue

        stripped = line.strip()
        if (
            not stripped
            or JINJA_LINE_RE.match(stripped)
            or HTML_COMMENT_RE.match(stripped)
            or REF_DEF_RE.match(stripped)
            or MYST_TARGET_RE.match(stripped)
            or stripped.startswith("<")
        ):
            flush_paragraph()
            out.append(line)
            i += 1
            continue

        if re.match(r"^\s{0,3}#{1,6}\s+", line):
            flush_paragraph()
            prefix, title, ending = re.match(
                r"^(\s{0,3}#{1,6}\s+)(.*?)(\n?)$", line
            ).groups()
            out.append(
                prefix
                + translator.translate_text(title, context)
                + ending
            )
            i += 1
            continue

        if re.match(r"^\s{0,3}([-+*]|\d+\.)\s+", line):
            flush_paragraph()
            prefix, item, ending = re.match(
                r"^(\s{0,3}(?:[-+*]|\d+\.)\s+)(.*?)(\n?)$", line
            ).groups()
            out.append(
                prefix
                + translator.translate_text(item, context)
                + ending
            )
            i += 1
            continue

        paragraph.append(line)
        i += 1

    flush_paragraph()
    return out


def translate_markdown_file(
    src: Path,
    dst: Path,
    translator: BatchTranslator,
) -> None:
    lines = src.read_text(encoding="utf-8").splitlines(keepends=True)
    has_front_matter = bool(lines and lines[0].strip() == "---")
    translated = translate_markdown_lines(
        lines,
        translator,
        str(src.relative_to(ROOT)),
        in_front_matter=has_front_matter,
    )
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(translator.resolve("".join(translated)), encoding="utf-8")


def copy_tree_skeleton(src_root: Path, out_root: Path) -> None:
    if out_root.exists():
        shutil.rmtree(out_root)
    for path in src_root.rglob("*"):
        rel = path.relative_to(src_root)
        target = out_root / rel
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        elif path.suffix != ".md":
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)


def write_config_files() -> None:
    config_path = OUT / "_config.yml"
    if config_path.exists():
        config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        config["title"] = "OCaml 编程：正确、高效、优美"
        config.setdefault("sphinx", {}).setdefault("config", {})["language"] = "zh_CN"
        config_path.write_text(
            yaml.safe_dump(config, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )

    toc_path = OUT / "_toc.yml"
    if toc_path.exists():
        toc = yaml.safe_load(toc_path.read_text(encoding="utf-8"))
        captions = {
            "Preface": "前言",
            "Introduction": "导论",
            "OCaml Programming": "OCaml 编程",
            "Correctness and Efficiency": "正确性与效率",
            "Language Implementation": "语言实现",
            "Lagniappe": "附录专题",
            "Appendix": "附录",
        }
        for part in toc.get("parts", []):
            if part.get("caption") in captions:
                part["caption"] = captions[part["caption"]]
        toc_path.write_text(
            yaml.safe_dump(toc, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0, help="Translate only N files.")
    parser.add_argument("--sleep", type=float, default=0.15, help="Delay between files.")
    parser.add_argument("--force", action="store_true", help="Recreate zh-cn.")
    args = parser.parse_args()

    cache = load_cache(CACHE_PATH)
    failures: list[str] = []
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})

    def backend(text: str) -> str:
        return google_translate(text, session=session)

    if args.force or not OUT.exists():
        copy_tree_skeleton(SRC, OUT)
        write_config_files()

    md_files = [SRC / "cover.md"] + sorted((SRC / "chapters").glob("**/*.md"))
    if args.limit:
        md_files = md_files[: args.limit]

    for index, src in enumerate(md_files, start=1):
        rel = src.relative_to(SRC)
        dst = OUT / rel
        print(f"[{index}/{len(md_files)}] {rel}", flush=True)
        translator = BatchTranslator(backend, cache, failures)
        translate_markdown_file(src, dst, translator)
        if index % 5 == 0:
            save_cache(CACHE_PATH, cache)
        time.sleep(args.sleep)

    if not args.limit:
        root_docs = [ROOT / "README.md", ROOT / "BUILDING.md"]
        for src in root_docs:
            if not src.exists():
                continue
            rel = Path("repo-docs") / src.name
            print(f"[repo-docs] {src.name}", flush=True)
            translator = BatchTranslator(backend, cache, failures)
            translate_markdown_file(src, OUT / rel, translator)

    save_cache(CACHE_PATH, cache)
    if failures:
        LOG_PATH.write_text("\n".join(failures) + "\n", encoding="utf-8")
        print(f"Failures: {len(failures)}; see {LOG_PATH}", file=sys.stderr)
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
