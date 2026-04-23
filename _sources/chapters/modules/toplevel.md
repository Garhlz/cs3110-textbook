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

# 模块和顶层

```{note}
下面的视频使用旧版构建系统 ocamlbuild，而不是新的
构建系统，Dune。一些细节随着Dune的变化而改变，如
下面的文字。
```

{{ video_embed | replace("%%VID%%", "4yo-04VVzIw")}}

有几个涉及模块和顶层的语用学：
掌握如何有效地结合使用两者很重要。

## 加载编译模块

编译 OCaml 文件会生成一个与该文件同名的模块，但是
第一个字母大写。这些编译好的模块可以加载到
顶层使用 `#load`。

例如，假设你创建一个名为 `mods.ml` 的文件，并输入以下内容
里面的代码：

```ocaml
let b = "bigred"
let inc x = x + 1
module M = struct
  let y = 42
end
```

请注意，周围没有 `module Mods = struct ... end` 。代码位于
可以说是文件的最顶层。

然后假设你输入 `ocamlc mods.ml` 来编译它。新创建的其中之一
文件是`mods.cmo`：这是一个<u>c</u>编译的<u>m</u>odule <u>o</u>bject文件，
又名字节码。

你可以使用以下命令使该字节码可在顶层使用
指令。回想一下，指令前面需要 `#` 字符。
它不是提示的一部分。

```ocaml
# #load "mods.cmo";;
```

该指令加载在 `mods.cmo` 中找到的字节码，从而创建一个模块
名为 `Mods` 可供使用。就好像你已经输入了这个一样
代码：

```{code-cell} ocaml
module Mods = struct
  let b = "bigred"
  let inc x = x + 1
  module M = struct
    let y = 42
  end
end
```

因此，这两个表达式都将成功求值：

```{code-cell} ocaml
Mods.b;;
Mods.M.y;;
```

但这会失败：
```{code-cell} ocaml
:tags: ["raises-exception"]
inc
```

它失败是因为 `inc` 位于 `Mods` 的命名空间中。
```{code-cell} ocaml
Mods.inc
```

当然，如果打开模块，可以直接命名为`inc`：

```{code-cell} ocaml
open Mods;;
inc;;
```

## Dune

Dune 提供了一个命令，可以更轻松地启动带有库的 utop
已加载。假设我们将此Dune文件添加到与 `mods.ml` 相同的目录中：

```text
(library
 (name mods))
```

这告诉Dune从 `mods.ml` （以及任何其他
同一目录中的文件（如果存在）。  然后我们可以运行这个命令
启动 utop 并加载该库：

```console
$ dune utop
```

现在我们可以立即访问 `Mods` 的组件，而无需发出
`#load` 指令：
```{code-cell} ocaml
Mods.inc
```

如果你愿意，`dune utop` 命令接受目录名称作为参数
在源代码的特定子目录中加载库。

## 初始化顶层

如果你正在对某个特定模块进行大量测试，那么这可能会很烦人
每次启动 utop 时都必须输入指令。你确实想要初始化
顶层在启动时包含一些代码，这样你就不必保留
输入该代码。

解决方案是在工作目录中创建一个文件并调用该文件
`.ocamlinit`。请注意，该文件名前面的 `.` 是必需的，并且
使其成为 [hidden file][hidden] ，不会出现在目录列表中，除非
明确请求（例如，使用 `ls -a`）。 `.ocamlinit` 中的所有内容都将是
加载时由 utop 处理。

[hidden]: https://en.wikipedia.org/wiki/Hidden_file_and_hidden_directory

例如，假设你在同一目录中创建一个名为 `.ocamlinit` 的文件
作为 `mods.ml`，并在该文件中放入以下代码：

```ocaml
open Mods;;
```

现在使用 `dune utop` 重新启动 utop。 `Mods` 中定义的所有名称都已经
处于范围内。例如，这些都会成功：

```{code-cell} ocaml
inc;;
M.y;;
```

## 引入库

假设你想在 utop 中试验一些 OUnit 代码。你不能
实际上打开它：

```{code-cell} ocaml
:tags: ["raises-exception"]
open OUnit2;;
```

问题是 OUnit 库尚未加载到 utop 中。它可以
符合以下指令：

```{code-cell} ocaml
:tags: ["remove-cell"]
#use "topfind";;
```

```{code-cell} ocaml
:tags: ["remove-output"]
#require "ounit2";;
```

现在你可以成功加载自己的模块而不会出现错误。

```ocaml
open OUnit2;;
```

<!--
MRC 8/12/21：我认为我们不再需要此部分。`dune utop` 应该
  自动处理递归加载，不需要为这个功能额外分配工作。
  此外，如果没有 ocamlbuild，也不清楚该怎样做到这一点。
  我们必须使用 ocamlc，或者设置一种奇怪的 Dune 层次结构。
  所以我现在先把它注释掉，打算一年后删除，
  如果一切顺利的话。

## 依赖关系

编译文件时，构建系统会自动找出其他文件
它依赖的文件并根据需要重新编译它们。然而，顶层是
不那么复杂：你必须确保加载 a 的所有依赖项
文件。

假设你在与 `mods.ml` 相同的目录中有一个名为 `mods2.ml` 的文件
从上面，`mods2.ml` 包含以下代码：

```ocaml
open Mods
let x = inc 0
```

如果运行`ocamlbuild -pkg ounit2 mods2.byte`，编译就会成功。
你不必在命令行上命名 `mods.byte`，即使 `mods2.ml`
取决于模块 `Mod`。这样构建系统就很智能了。

还假设 `.ocamlinit` 恰好包含以下内容：

```ocaml
#directory "_build";;
#require "ounit2";;
```

如果重新启动 utop 并尝试加载 `mods2.cmo`，你将收到错误：

```text
# #load "mods2.cmo";;
Error: Reference to undefined global `Mods'
```

问题是顶层不会自动加载模块
`Mods2` 取决于。有两种方法可以解决这个问题。
首先，你可以手动加载依赖项，如下所示：

```ocaml
# #load "mods.cmo";;
# #load "mods2.cmo";;
```

其次，你可以告诉顶层加载 `Mods2` 并递归地
加载它所依赖的所有内容：

```ocaml
# #load_rec "mods2.cmo";;
```

这可能是更好的解决方案。
-->

## `load` 与 `use`

`#load`-编译的模块文件和
`#use`-ing 未编译的源文件。前者加载字节码并使其
可供使用。例如，加载 `mods.cmo` 导致 `Mod` 模块被
可用，我们可以使用 `Mod.b` 等表达式访问其成员。
后者（`#use`）是*文本包含*：就像输入
文件直接进入顶层。因此，使用 `mods.ml` 不会**导致 `Mod`
模块可用，并且可以访问文件中的定义
直接，例如 `b`。

例如，在下面的交互中，我们可以直接引用`b`，但是
不能使用限定名称 `Mods.b`：

```text
# #use "mods.ml"

# b;;
val b : string = "bigred"

# Mods.b;;
Error: Unbound module Mods
```

而在这种互动中，情况正好相反：

```text
# #directory "_build";;
# #load "mods.cmo";;

# Mods.b;;
- : string = "bigred"

# b;;
Error: Unbound value b
```

因此，当你使用顶层来试验代码时，通常会
更好地使用 `#load` 而不是 `#use`。 `#load` 指令准确
反映了你的模块如何相互交互以及与外部世界交互。
