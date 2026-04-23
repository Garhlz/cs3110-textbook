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

# 异步输入和输出

既然我们已经把 Promise 理解为一种数据抽象，下面看看它们如何用于并发。
在 Lwt 中，Promise 的典型用途是并发输入和输出 (I/O)。

OCaml 标准库中的 I/O 函数是*同步*
又名 *阻塞*：当你调用这样的函数时，它不会返回，直到 I/O
已完成。这里的“同步”指的是之间的同步
你的代码和 I/O 函数：你的代码不会再次执行，直到
I/O 代码完成。“阻塞”是指你的代码必须等待&mdash;也就是被阻塞&mdash;
直到 I/O 完成。

例如，`Stdlib.input_line : in_channel -> string` 函数读取
从*输入通道*开始的字符直到到达换行符，然后
返回读取到的字符。类型 `in_channel` 是抽象的；它代表可以读取的数据源，
例如文件、网络或键盘。值 `Stdlib.stdin : in_channel` 代表*标准输入*
通道，通常默认提供键盘输入。

如果你在 utop 中运行以下代码，你将观察到阻塞行为：

```text
# ignore(input_line stdin); print_endline "done";;
<type your own input here>
done
- : unit = ()
```

直到输入操作完成后才会打印字符串 `"done"`，
输入 Enter 后会发生这种情况。

同步 I/O 会让程序在等待 I/O 操作完成时无法进行其他计算。
对某些程序来说这没有问题。例如，文字冒险游戏没有必须在后台执行的计算。
但电子表格或服务器等程序，如果能在后台继续计算，而不是等待输入时完全阻塞，
就会受益很多。

*异步*又名*非阻塞* I/O 是 I/O 的相反风格。异步
I/O 操作会立即返回，无论输入或输出是否已经完成。
这使程序能够启动 I/O 操作，继续进行其他计算，然后再回来使用已经完成的操作结果。

Lwt 库在 `Lwt_io` 模块中提供了自己的 I/O 函数，该模块
在 `lwt.unix` 包中。函数
`Lwt_io.read_line : Lwt_io.input_channel -> string Lwt.t` 是异步的
版本，相当于 `Stdlib.input_line`。同样，`Lwt_io.input_channel`
相当于 OCaml 标准库的 `in_channel`，而 `Lwt_io.stdin`
代表标准输入通道。

在 utop 中运行此代码以观察非阻塞行为：

```text
# #require "lwt.unix";;
# open Lwt_io;;
# ignore(read_line stdin); printl "done";;
done
- : unit = ()
# <type your own input here>
```

字符串 `"done"` 会立即由 `Lwt_io.printl` 打印出来；它是 Lwt 中
对应 `Stdlib.print_endline` 的函数，甚至会在你输入之前执行。
请注意，最好只使用一个库的 I/O 函数，不要混用多个库。

当你键入输入内容时，不会看到它回显到屏幕上，因为读取发生在后台。
Utop 仍在执行&mdash;它没有被阻塞&mdash;但你的输入被发送给那个
`read_line` 函数，而不是发送给 utop。当你最终输入 Enter 时，
输入操作完成，你又可以继续与 utop 交互。

现在想象这个程序不是异步读取一行，而是一个网络服务器正在读取要提供给客户端的文件。
在等待某个文件读取完成时，服务器可以把另一个已经读完的文件内容发送给另一个客户端。
这就是异步 I/O 如此有用的原因：它有助于*隐藏延迟*。
这里的“延迟”是指等待数据从一个地方转移到另一个地方，
例如从磁盘到内存。隐藏延迟是并发的典型用途。

请注意，这里的所有并发实际上都来自操作系统，
它提供了底层异步 I/O 基础设施。Lwt 只是通过库把这套基础设施暴露给你。

## Promise 和异步 I/O

`Lwt_io.read_line` 的输出类型是 `string Lwt.t`，这意味着
函数返回一个 `string` Promise。让我们研究一下这个 Promise 的状态如何变化。

当 Promise 从 `read_line` 返回时，它处于待处理状态：

```text
# let p = read_line stdin in Lwt.state p;;
- : string Lwt.state = Lwt.Sleep
# <now you have to type input and Enter to regain control of utop>
```

当按下 Enter 键并完成输入时，`read_line` 返回的 Promise 应该得到履行。
例如，假设你输入 “Camels are bae”：

```text
# let p = read_line stdin;;
val p : string Lwt.t = <abstr>
<now you type Camels are bae followed by Enter>
# p;;
- : string = "Camels are bae"
```

但是，如果你仔细研究该输出，你会发现一些非常奇怪的事情
刚刚发生了！在 `let` 语句之后，`p` 的类型为 `string Lwt.t`，如下
预期。但是当我们求值 `p` 时，它返回的类型却是 `string`。就好像
Promise 消失了。

实际发生的情况是 utop 有一些特殊的 &mdash; 并且可能
令人困惑的 &mdash; 内置的 Lwt 相关特性。
具体来说，每当你尝试直接求值顶层的 Promise 时，
*utop 会给你 Promise 的内容，而不是 Promise 本身；
如果 Promise 尚未解析，utop 会阻塞，直到 Promise 被解析，以便返回其中的内容。*

所以输出 `- : string = "Camels are bae"` 实际上意味着 `p` 包含一个
已履行的 `string`，其值为 `"Camels are bae"`；这并不是说 `p` 本身是一个
`string`。事实上，`#show_val` 指令会表明 `p` 是一个 Promise：

```text
# #show_val p;;
val p : string Lwt.t
```

要禁用或重新启用 utop 的这个功能，请调用函数
`UTop.set_auto_run_lwt : bool -> unit`。它会改变 utop 求值顶层
Lwt Promise 的方式。下面的代码展示了行为变化：

```text
# UTop.set_auto_run_lwt false;;
- : unit = ()
<now you type Camels are bae followed by Enter>
# p;;
- : string Lwt.state = <abstr>
# Lwt.state p;;
- : string Lwt.state = Lwt.Return "Camels are bae"
```

如果你重新启用此“自动运行”功能，并直接尝试评估
`read_line` 返回的 Promise，你会发现它的行为完全一样
同步 I/O，即 `Stdlib.input_line`：

```text
# UTop.set_auto_run_lwt true;;
- : unit = ()
# read_line stdin;;
Camels are bae
- : string = "Camels are bae"
```

由于潜在的混乱，我们今后将假设自动运行
已禁用。实现这一点的一个好方法是将以下行放入你的
`.ocamlinit` 文件：

```text
UTop.set_auto_run_lwt false;;
```
