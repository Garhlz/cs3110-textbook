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

# Promise

在函数式编程范式中，用于并发的一个著名抽象是 *Promise*。
这个想法还有其他名称，包括 *future*、*deferred* 和 *delay*。
所有这些名称都指向同一个概念：一个尚未完成的计算。
它保证将来最终会完成，但计算结果被推迟到未来才可用。
许多这样的值可能会同时计算；当某个值最终可用时，
可能已经有依赖它的计算准备好执行。

这个想法已被许多语言和库广泛采用，包括
Java、JavaScript 和 .NET。事实上，现代 JavaScript 添加了 `async` 关键字，
使函数返回 Promise；还添加了 `await` 关键字，用于等待 Promise 完成。
OCaml 中有两个广泛使用的 Promise 库：Async 和 Lwt。
Async 由 Jane Street 开发。Lwt 是 Ocsigen 项目的一部分，
而 Ocsigen 是 OCaml 的 Web 框架。

我们现在更深入地研究 Lwt 中的 Promise。库的名字是
“轻量级线程”的缩写。但这是用词不当，因为
[GitHub page][lwt-github] 承认（截至 2018 年 10 月 22 日）：

> 当前手册的大部分内容都提到......“轻量级线程”或
只是“线程”。这将在新手册中修复。[Lwt 实现] Promise，
与系统或抢占式线程无关。

因此，不要认为 Lwt 与线程有什么关系：它实际上是一个
Promise 库。

[lwt-github]: https://github.com/ocsigen/lwt

在 Lwt 中，*Promise* 是一种引用：它所包含的值最多只允许改变一次。
创建时，它就像一个空盒子，里面什么也没有。我们说这个 Promise 是“待处理”的。
最终，Promise 可以被*履行*，就像把东西放进盒子里一样。
除了履行之外，Promise 也可以被“拒绝”；在这种情况下，盒子里装入的是一个异常。
无论是履行还是拒绝，我们都说 Promise 已经被*解析*。
Promise 一旦被解析，盒子里的内容就永远不会再改变。

现在，我们基本上先把并发本身放在一边，稍后再回来整合它。
但我们现在就需要引入并发设计中的一个部分。
当我们稍后开始使用操作系统提供的并发函数时，
例如对文件进行并发读写，就需要划分职责：

* 想要利用并发的客户端代码需要*访问*
Promise：查询它们是已解析还是待处理，并使用
  解析出的值。

* 实现并发的库和操作系统代码将需要“改变”
Promise&mdash;即实际履行或拒绝它。客户端代码没有
  需要那个能力。

因此，我们将引入一种额外的抽象，称为“解析器”。
Promise 和解析器之间将存在一对一的关联。
Promise 的解析器将由并发库内部使用，但是
不向客户端透露。客户端只能获得 Promise。

例如，假设并发库支持以下操作：
同时从网络读取一个字符串。库将实现这一点
操作如下：

* 创建一个新的 Promise 及其关联的解析器。该 Promise 尚未解析。

* 调用一个操作系统函数，该函数将同时读取字符串，然后调用
该字符串上的解析器。

* 将 Promise（但不包括解析器）返回给客户端。同时操作系统
继续读取字符串。

你可以把解析器看作主要由库使用的“私有且可写”的值，
而把 Promise 看作主要由客户端使用的“公开且只读”的值。
