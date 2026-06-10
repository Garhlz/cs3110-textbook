# OCaml Programming: Correct + Efficient + Beautiful

This repository contains the course textbook for CS 3110 at Cornell University.

## Chinese Edition

The Chinese edition is maintained in `zh-cn/`. It mirrors the original Jupyter
Book structure under `src/`, preserving MyST Markdown, Jupytext metadata, code
cells, links, and build configuration as much as possible.

The Chinese edition is based on the Spring 2026 edition of the English book. It
was prepared with AI assistance. The English source remains authoritative for course
requirements, licensing, and technical details.

Chinese edition repository:

<https://github.com/Garhlz/cs3110-textbook>

Useful checks:

```bash
python scripts/check_translation_structure.py
python scripts/check_markdown_refs.py
```

To build the book with the original Conda workflow, first create and activate
the textbook environment described in `BUILDING.md`, then run:

```bash
make html
```

The Chinese edition HTML output is generated under `zh-cn/_build/html/`.

If you prefer `uv` instead of Conda, create a local virtual environment and
install the pinned build dependencies, then build with the existing OPAM switch:

```bash
uv venv .venv
uv pip install --python .venv/bin/python -r requirements.txt
OPAMSWITCH=textbook .venv/bin/jupyter-book build zh-cn
```

Note that this repository currently expects `jupyter-book==0.15.1`. Newer
Jupyter Book releases use a different toolchain and may fail to build this repo
without additional Node/NPM setup.

## 中文版说明

本仓库维护了《OCaml 编程：正确、高效、优美》的中文翻译版本，内容位于
`zh-cn/`。中文版基于 2026 年春季版英文原书整理而成，尽量保留原书的
Jupyter Book、MyST Markdown、Jupytext 元数据、可执行代码单元、链接和构建
配置。

中文版的翻译和润色使用 AI 辅助，目标
是在保持原书技术细节准确性的同时，提供更适合中文读者的阅读体验。涉及课程
要求、许可条款或技术细节时，请以英文原书为准。

中文版仓库：

<https://github.com/Garhlz/cs3110-textbook>

常用检查命令：

```bash
python scripts/check_translation_structure.py
python scripts/check_markdown_refs.py
```

构建中文版网页：

```bash
make html BOOK=zh-cn
```

生成的静态网页位于 `zh-cn/_build/html/`。

如果你不再使用 Conda，也可以改用 `uv`：

```bash
uv venv .venv
uv pip install --python .venv/bin/python -r requirements.txt
OPAMSWITCH=textbook .venv/bin/jupyter-book build zh-cn
```

注意：这个仓库当前实际依赖 `jupyter-book==0.15.1`。如果直接安装较新的
Jupyter Book 版本，会切换到不同的构建链路，并可能额外要求 Node / npm，
从而导致构建失败。
