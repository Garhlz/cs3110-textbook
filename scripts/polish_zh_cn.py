#!/usr/bin/env python3
"""Conservative polishing pass for the generated zh-cn Markdown.

This fixes frequent machine-translation artifacts without touching fenced code
blocks, Jupytext front matter, reference definitions, or Jinja lines.
"""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ZH = ROOT / "zh-cn"

FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")
REF_DEF_RE = re.compile(r"^\s{0,3}\[[^\]]+\]:\s+\S+")
JINJA_LINE_RE = re.compile(r"^\s*\{\{.*\}\}\s*$")
MYST_TARGET_RE = re.compile(r"^\s*\([A-Za-z0-9_-]+\)=\s*$")

LITERAL_REPLACEMENTS = [
    ("Creative 公共资源\n归属-非商业-NoDerivatives 4.0 国际许可证", "Creative Commons\n署名-非商业性使用-禁止演绎 4.0 国际许可协议"),
    ("Creative 公共资源", "Creative Commons"),
    ("归属-非商业-NoDerivatives", "署名-非商业性使用-禁止演绎"),
    ("谷歌搜索", "Google 搜索"),
    ("谷歌文档", "Google 文档"),
    ("谷歌研究", "Google Research"),
    ("微软", "Microsoft"),
    ("视觉工作室代码", "Visual Studio Code"),
    ("朱皮特", "Jupyter"),
    ("奥卡姆", "OCaml"),
    ("蟒蛇", "Python"),
    ("爪哇", "Java"),
    ("沙丘", "Dune"),
    ("窗户", "Windows"),
    ("麦克", "Mac"),
    ("Unix开发环境", "Unix 开发环境"),
    ("安装OPAM", "安装 OPAM"),
    ("OCaml编程", "OCaml 编程"),
    ("OCaml 手册", "OCaml 手册"),
    ("[manual]", "[手册]"),
    ("[the manual]", "[手册]"),
    ("[Dune manual]", "[Dune 手册]"),
    ("[Lwt manual]", "[Lwt 手册]"),
    ("[the section on exceptions]", "[异常一节]"),
    ("[section on association lists]", "[关联列表一节]"),
    ("[later section]", "[后面的小节]"),
    ("[Preface]", "[前言]"),
    ("[Install OPAM]", "[安装 OPAM]"),
    ("NoDerivatives", "禁止演绎"),
    ("生活质量", "便利性"),
    ("如果你没有建立在坚实的基础上，整个事情可能会崩溃。的\n好消息是", "如果没有建立在坚实的基础上，整个安装过程可能会崩溃。\n好消息是"),
    ("当然，一定要批判性地思考随机陌生人在网站上提出的建议\n互联网。", "当然，对互联网上陌生人给出的建议一定要保持批判性。"),
    ("这本书适合你。", "这本书就是为你准备的。"),
    ("是时候了\n学习函数式语言", "是时候学习一门函数式语言了："),
    ("提供了与传统编程不同的视角\n到目前为止你已经经历过。", "提供了一种不同于你迄今所熟悉方式的编程视角。"),
    ("旧思想：赋值语句、循环、类和对象等等。", "旧观念：赋值语句、循环、类和对象，等等。"),
    ("功能性\n语言", "函数式\n语言"),
    ("功能性语言", "函数式语言"),
    ("功能程序", "函数式程序"),
    ("功能角度", "函数式角度"),
    ("功能性的", "函数式的"),
    ("功能性", "函数式"),
    ("命令式功能", "命令式特性"),
    ("语言功能", "语言特性"),
    ("语言函数", "语言特性"),
    ("高级功能", "高级特性"),
    ("内置与 Lwt 相关的功能", "内置的 Lwt 相关特性"),
    ("可变功能", "可变特性"),
    ("新功能", "新特性"),
    ("一些基本功能", "一些基本特性"),
    ("核心功能", "核心功能"),
    ("抽象原理", "抽象原则"),
    ("类型推理", "类型推断"),
    ("算法上的推理", "算法化地解决类型推断"),
    ("精神演绎能力", "推理能力"),
    ("研究。定义不是表达式", "学习。定义不是表达式"),
    ("定义&mdash;它们是", "定义 &mdash; 它们是"),
    ("函数\n定义", "函数定义"),
    ("类型\n算法化地解决类型推断*问题", "类型推断*问题"),
    ("*type\n算法化地解决类型推断*问题", "*类型推断*问题"),
    ("[rules for lowercase identifiers]", "[小写标识符的规则]"),
    ("有兴趣的读者", "感兴趣的读者"),
    ("作为\n架构不断发展", "随着\n架构不断发展"),
    ("因此，这些的表示会窃取一位", "因此，它们的表示会借用一位"),
    ("一个单词是否是一个\n整数或指针", "一个机器字是\n整数还是指针"),
    ("对象，并且它隐式有一个接收器", "对象的一部分，并且隐式带有一个接收者"),
    ("对象，并且它们没有接收器", "对象的一部分，也没有接收者"),
    ("术语。 **", "术语。**"),
    ("OCaml 函数不是方法：它们不是组件\n对象", "OCaml 函数不是方法：它们不是对象的一部分"),
    ("有意义的值，例如", "有意义的值，例如"),
    ("Python。", "Python。"),
    ("Windows 的 Windows 子系统", "Windows Subsystem for Linux"),
    ("Linux 的 Windows 子系统", "Windows Subsystem for Linux"),
    ("玻璃市", "Perlis"),
    ("缺点语法", "cons 语法"),
    ("缺点操作", "cons 操作"),
    ("有缺点）", "使用 cons）"),
    ("然后缺点", "然后 cons"),
    ("发件箱中的缺点", "发件箱中的 cons"),
    ("每个 `Node` 都有一个缺点", "每个 `Node` 都有一次 cons"),
    ("并反对缺点", "并匹配 cons"),
    ("* 缺点", "* cons"),
    ("过滤器的概念", "`filter` 的概念"),
    ("映射和过滤器", "`map` 和 `filter`"),
    ("地图、过滤器、折叠", "`map`、`filter`、`fold`"),
    ("过滤器、折叠", "`filter`、`fold`"),
    ("泛函映射、折叠和过滤器", "`map`、`fold` 和 `filter`"),
    ("。  的", "。"),
    ("。 的", "。"),
    ("。的", "。"),
    ("前言", "前言"),
]

REGEX_REPLACEMENTS = [
    (re.compile(r"(?<![A-Za-z])OPAM (?:交换机|开关)"), "OPAM switch"),
    (re.compile(r"(?<![A-Za-z])switch(?=\\s|\\*|，|。|$)"), "switch"),
    (re.compile(r"(?<![A-Za-z])utop(?=\\s|，|。|$)"), "utop"),
    (re.compile(r"(?<![A-Za-z])toplevel(?=\\s|，|。|$)"), "toplevel"),
    (re.compile(r"([\\u4e00-\\u9fff]) ([，。；：！？、])"), r"\1\2"),
    (re.compile(r"([（【])\\s+"), r"\1"),
    (re.compile(r"\\s+([）】])"), r"\1"),
    (re.compile(r"。\\s+（"), "。（"),
    (re.compile(r"\\bOCaml\\s+"), "OCaml "),
    (re.compile(r"\\bJava\\s+"), "Java "),
    (re.compile(r"\\bPython\\s+"), "Python "),
]


def polish_line(line: str) -> str:
    original_newline = "\n" if line.endswith("\n") else ""
    body = line[:-1] if original_newline else line

    if (
        REF_DEF_RE.match(body)
        or JINJA_LINE_RE.match(body)
        or MYST_TARGET_RE.match(body)
    ):
        return line

    for old, new in LITERAL_REPLACEMENTS:
        body = body.replace(old, new)
    for pattern, replacement in REGEX_REPLACEMENTS:
        body = pattern.sub(replacement, body)
    return body + original_newline


def polish_file(path: Path) -> None:
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    out: list[str] = []
    in_fence = False
    fence_marker = ""
    in_front_matter = bool(lines and lines[0].strip() == "---")

    for idx, line in enumerate(lines):
        if in_front_matter:
            out.append(line)
            if idx > 0 and line.strip() == "---":
                in_front_matter = False
            continue

        fence = FENCE_RE.match(line)
        if fence:
            marker = fence.group(1)
            if not in_fence:
                in_fence = True
                fence_marker = marker
            elif line.lstrip().startswith(fence_marker):
                in_fence = False
                fence_marker = ""
            out.append(line)
            continue

        if in_fence:
            out.append(line)
        else:
            out.append(polish_line(line))

    path.write_text("".join(out), encoding="utf-8")


def main() -> int:
    for path in sorted(ZH.rglob("*.md")):
        polish_file(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
