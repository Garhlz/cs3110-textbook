# CS 3110 Textbook Markdown 中文翻译指南

本文档专门用于指导当前仓库 `cs3110-textbook` 的中文翻译工作。仓库是一个 Jupyter Book 项目，正文使用 MyST Markdown 和 Jupytext 组织，翻译时要优先保护书稿结构、可执行代码单元、交叉引用和构建配置。

目标不是从网页、PDF 或 HTML 逆向抽取内容，而是直接翻译仓库中的 Markdown 源文件，生成适合中文读者本地阅读、并尽量保留 Jupyter Book 构建能力的中文稿件。

## 仓库结构判断

当前仓库的核心内容如下：

```text
README.md
BUILDING.md
translation-guidance.md
src/
  _config.yml
  _toc.yml
  cover.md
  chapters/
    preface/
    intro/
    basics/
    data/
    hop/
    modules/
    mut/
    conc/
    correctness/
    ds/
    interp/
    adv/
    appendix/
  assets/
  _static/
```

主要翻译对象是 `src/cover.md` 和 `src/chapters/**/*.md`。当前约有 109 个 Markdown 源文件。`README.md`、`BUILDING.md` 可以后续按需翻译，但不属于教材正文的第一优先级。

`src/_config.yml` 和 `src/_toc.yml` 是 Jupyter Book 配置，默认不要全文翻译。需要中文构建版本时，只改少量展示字段，例如 `title`、`language`、`parts.caption`，并保留所有 `file` 路径、构建选项和 substitution 配置。

## 推荐输出方式

建议不要直接覆盖英文源文件。采用镜像目录输出中文稿：

```text
zh-cn/
  _config.yml
  _toc.yml
  cover.md
  chapters/
    ...
```

处理原则：

* 从 `src/` 复制目录结构到 `zh-cn/`。
* 翻译 `cover.md` 和 `chapters/**/*.md` 中的可见自然语言。
* 保留图片、代码附件、CSS 和其他静态资源路径关系。
* 如果要构建中文 Jupyter Book，可以复制并局部调整 `_config.yml` 与 `_toc.yml`。
* 不要修改 `src/assets/code/*.ml`、zip 文件、图片、CSS，除非后续明确要求本地化资源。

如果只追求本地 Markdown 阅读，也可以只生成：

```text
translation-work/
  source/
  draft/
  polished/
  final/
  glossary.yml
  logs/
```

但最终交付时仍建议把 `final/` 整理成与 `src/` 同构的 `zh-cn/`，方便按原目录定位章节。

## 翻译范围

应该翻译：

* 标题文本，例如 `# Functions`。
* 普通段落。
* 列表项里的自然语言。
* 引用块里的自然语言。
* MyST admonition 块里的自然语言内容。
* 表格单元格中的说明性文本。
* 链接可见文本。
* 图片 alt 文本和正文中的图注。
* `cover.md` 中的版权、作者、视频说明等可见文本。

默认不翻译：

* 代码块和代码单元内容。
* 行内代码。
* YAML front matter 的键和值，除非值明确是页面标题类展示文本。
* 链接 URL、引用式链接定义、图片路径。
* 文件路径、模块名、包名、命令名、环境变量。
* 数学公式。
* Jinja 或 MyST substitution 表达式。
* HTML 标签、属性名、属性值中的 URL 或路径。

## 本仓库必须保护的语法

### Jupytext front matter

很多章节以如下 YAML 块开头：

```yaml
---
jupytext:
  cell_metadata_filter: -all
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.10.3
kernelspec:
  display_name: OCaml
  language: OCaml
  name: ocaml-jupyter
---
```

这个块必须原样保留。不要翻译 `display_name`、`language`、`name`，否则可能影响 Jupyter 执行和构建。

### MyST 代码单元

本书大量使用：

````markdown
```{code-cell} ocaml
let x = 42
```
````

要求：

* 围栏行原样保留。
* 代码内容原样保留。
* 不翻译 OCaml 注释中的规格说明，除非后续明确要求“代码注释也中文化”。默认保留代码单元完全不动。
* 不改变代码单元顺序，因为 Jupyter Book 可能按顺序执行。

普通代码块也同样保护：

````markdown
```ocaml
let f x = x + 1
```
````

### MyST admonition 和 epigraph

仓库中常见：

````markdown
```{important}
...
```

```{note}
...
```

```{tip}
...
```

```{warning}
...
```

```{epigraph}
...
```
````

围栏和指令名必须原样保留，块内部的自然语言可以翻译。翻译时不要把整个块改写成普通引用或普通段落。

### Jinja substitution

仓库中使用：

```markdown
{{ video_embed | replace("%%VID%%", "vCxIlagS7kA")}}
{{ solutions }}
{{ ex1 | replace("%%NAME%%", "values")}}
```

这些表达式必须原样保留。特别是练习名如 `"values"`、`"double fun"` 是替换参数，默认不要翻译。练习正文可以翻译。

### HTML 片段

仓库中有 HTML 注释、链接、图片、下划线和实体，例如：

```html
<!--------------------------------------------------------------------------->
<a rel="license" href="http://creativecommons.org/licenses/by-nc-nd/4.0/">
Pok&eacute;<u>mon</u>
```

要求：

* HTML 标签和属性原样保留。
* `href`、`src`、`style` 等属性值原样保留。
* HTML 注释分隔线原样保留。
* HTML 实体如 `&mdash;`、`&starf;`、`&hearts;`、`&spades;` 原样保留，除非人工确认替换后不会影响显示。

### 链接和引用定义

正文中有内联链接、引用式链接和相对章节链接：

```markdown
[the manual][man]
[later section](records_tuples)
[install instructions](../preface/install.md)
[man]: https://ocaml.org/manual/values.html
```

要求：

* 链接可见文本可以翻译。
* 目标地址、引用标签和 `.md` 路径原样保留。
* 不要把 `records_tuples`、`../preface/install.md` 等路径翻译成中文。
* 不要改动引用式链接定义的标签名和 URL。

### 数学公式

仓库使用 dollar math 和 amsmath：

```markdown
$O(n \log n)$
$$
\lambda x. x
$$
```

公式体和分隔符原样保留。含公式段落可以翻译公式外的自然语言，但不要改写公式符号。

## 翻译流程

推荐采用两段式流程。

### 第一阶段：结构化机器翻译

用 Markdown/MyST 感知的脚本把文档拆成块，只把可见自然语言送入机器翻译。不要把整章直接作为纯文本翻译。

建议粒度：

* 标题级。
* 段落级。
* 列表项级。
* admonition 内部段落级。
* 表格单元格级。

应跳过或特殊处理：

* fenced code 和 `{code-cell}`。
* YAML front matter。
* Jinja substitution 行。
* HTML 块和 HTML 注释。
* 引用式链接定义。
* 含大量行内代码或数学符号的段落，必要时人工处理。

### 第二阶段：LLM 受约束润色

LLM 的任务是基于英文原文和中文初稿做校订，不是自由重写。

推荐提示词：

```text
你是 OCaml 技术教材的中文编辑。

任务：
根据英文原文和中文机器翻译初稿，输出润色后的中文 Markdown 片段。

要求：
1. 忠实原意，不新增、不删减技术事实。
2. 语言自然，适合中文技术教材阅读。
3. 保持术语统一，遵循术语表。
4. 保留原有 Markdown/MyST 结构。
5. 不修改代码块、行内代码、链接目标、图片路径、数学公式、Jinja 表达式、HTML 标签。
6. 专有名词和 OCaml 语法对象必要时保留英文。
7. 只输出润色后的片段，不要解释。

术语表：
{glossary}

英文原文：
{source_text}

中文初稿：
{draft_text}
```

不要一次润色整章。长章节应按块处理，并记录块编号、源文件路径和行号范围，方便追踪错误。

## 术语表建议

翻译前维护 `glossary.yml`。初始建议如下：

```yaml
OCaml: OCaml
Jupyter Book: Jupyter Book
MyST Markdown: MyST Markdown
Jupytext: Jupytext
toplevel: 顶层
utop: utop
REPL: REPL
expression: 表达式
definition: 定义
value: 值
type: 类型
type inference: 类型推断
type annotation: 类型注解
static semantics: 静态语义
dynamic semantics: 动态语义
function: 函数
method: 方法
argument: 实参
parameter: 形参
recursive: 递归的
recursion: 递归
tail recursion: 尾递归
pattern matching: 模式匹配
variant: 变体
constructor: 构造器
record: 记录
tuple: 元组
list: 列表
option: option
module: 模块
signature: 签名
functor: functor
monad: monad
promise: promise
callback: 回调
interpreter: 解释器
parser: 解析器
compiler: 编译器
runtime: 运行时
immutable: 不可变
mutable: 可变
side effect: 副作用
specification: 规格说明
precondition: 前置条件
postcondition: 后置条件
abstraction: 抽象
data structure: 数据结构
```

术语策略：

* OCaml 关键字、标准库模块、类型名、构造器名、函数名保持英文原样。
* `functor` 和 `monad` 首次出现可写作 `functor（函子）`、`monad（单子）`，后续优先保留英文，避免和数学语境混淆。
* `toplevel` 在 OCaml 语境中译为“顶层”，但命令或工具名如 `utop` 保持英文。
* `argument` 和 `parameter` 如果原文语境没有严格区分，可统一译为“参数”。在解释函数调用和函数定义时，再分别使用“实参”和“形参”。
* 章节名、练习名和目录标题要保持全书一致。

## 中文风格

采用清晰、克制、教材式的中文。

要求：

* 不硬贴英文语序。
* 保留原文的教学节奏，不擅自扩写。
* 技术解释优先准确，其次流畅。
* 可以把第二人称 “you” 译为“你”或“我们”，但同一章节内尽量统一。
* 不把轻松表达全部抹平，原文有明显幽默或口语时可适度保留。
* 代码前后的说明要和代码保持贴合，不要为了中文流畅改变指代对象。

示例：

```text
The compiler infers them for us automatically.
```

可译为：

```text
编译器会自动为我们推断出它们。
```

不要译为：

```text
编译器为我们自动地推断它们。
```

## 章节处理顺序

建议按 `_toc.yml` 的顺序推进，而不是按文件名排序：

1. `cover.md`
2. `chapters/preface/`
3. `chapters/intro/`
4. `chapters/basics/`
5. `chapters/data/`
6. `chapters/hop/`
7. `chapters/modules/`
8. `chapters/mut/`
9. `chapters/conc/`
10. `chapters/correctness/`
11. `chapters/ds/`
12. `chapters/interp/`
13. `chapters/adv/`
14. `chapters/appendix/`

优先翻译正文和 summary，再翻译 exercises。练习题中常有 Jinja exercise macro 和 HTML 分隔线，自动化时要额外保护。

## 检查清单

每个文件翻译后至少检查：

* fenced code 开闭数量一致。
* `{code-cell}`、`{note}`、`{tip}`、`{warning}`、`{important}`、`{epigraph}` 指令名未改变。
* YAML front matter 没有被翻译或破坏。
* `{{ ... }}` 表达式数量和内容一致。
* 引用式链接定义数量一致。
* Markdown 链接目标和图片路径未改变。
* 行内代码反引号成对。
* 数学公式分隔符完整。
* HTML 标签没有被翻译或拆坏。
* 标题层级没有异常变化。

如果要验证 Jupyter Book 构建：

```bash
make html
```

或在中文目录单独构建时运行对应的 `jupyter-book build zh-cn`。如果只是生成本地阅读 Markdown，至少运行自定义结构检查脚本，并抽样打开重点章节检查渲染效果。

## 不建议的做法

不要：

* 从线上网页复制 HTML 再转 Markdown。
* 把整本书一次性丢给翻译器。
* 覆盖英文 `src/` 原文。
* 翻译 OCaml 代码、Jupyter kernel 配置、Jinja 参数和路径。
* 为了中文化而重命名文件或目录。
* 把 substitution、admonition、code-cell 改成普通 Markdown。
* 在未检查许可证和语义的情况下改写版权说明。

## 当前仓库的第一步建议

后续实施翻译时，先做一个小范围试点：

1. 生成 `zh-cn/` 镜像目录。
2. 先翻译 `src/cover.md`、`src/chapters/intro/intro.md`、`src/chapters/basics/functions.md` 三个代表性文件。
3. 对比英文和中文文件，确认代码块、Jinja、链接和 front matter 全部保持稳定。
4. 固化术语表和检查脚本。
5. 再按 `_toc.yml` 顺序批量推进。
