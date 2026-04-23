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

# 回调

要让程序受益于异步 I/O 和 Promise 提供的并发性，
程序需要一种方式来使用已经解析的 Promise。例如，如果 Web 服务器异步地
读取多个文件并将其提供给多个客户端，服务器需要
一种方法 (i) 意识到读取已完成，并且 (ii) 然后执行
新的异步写入与读取结果。换句话说，
程序需要一种机制来管理 Promise 之间的依赖关系。

Lwt 中提供的机制称为 *callback*。
回调是一个函数：当它被“注册”到某个 Promise 上时，
会在该 Promise 履行后的某个时间运行。
回调会接收已履行 Promise 的内容作为输入。
可以把它想象成让你的朋友为你做一些数学题：他们
答应会这么做，并在完成后的某个时间给你回电话并提供答案。
在等待他们给你回电时，你可以做其他事情，当他们给你回电时，你可以使用他们给你的答案。

## 注册回调

这是一个使用 Lwt 打印字符串的函数
`printf` 函数的版本：
```ocaml
let print_the_string str = Lwt_io.printf "The string is: %S\n" str
```

这里重复上一节中的代码，它返回一个 Promise，
对于从标准输入读取的字符串：
```ocaml
let p = read_line stdin
```

要将打印函数注册为 Promise `p` 的回调，我们使用
函数 `Lwt.bind`，把回调绑定到 Promise：

```ocaml
Lwt.bind p print_the_string
```

在 `p` 被履行后的某个时间，它会包含一个字符串；
回调将以该字符串作为输入运行，从而打印该字符串。

这是一个完整的 utop 成绩单作为示例：
```text
# let print_the_string str = Lwt_io.printf "The string is: %S\n" str;;
val print_the_string : string -> unit Lwt.t = <fun>
# let p = read_line stdin in Lwt.bind p print_the_string;;
- : unit Lwt.t = <abstr>
  <type Camels are bae followed by Enter>
# The string is: "Camels are bae"
```

## Bind

理解 `Lwt.bind` 的类型很重要：
```ocaml
'a Lwt.t -> ('a -> 'b Lwt.t) -> 'b Lwt.t
```

`bind` 函数将 Promise 作为第一个参数。这个 Promise 是否已经履行并不重要。
作为第二个参数，`bind` 接收一个回调。回想一下，回调是一个函数：
这里的回调接收与 Promise 内容相同类型的输入，也就是 `'a`。
二者类型相同并非偶然：整个想法就是最终在已完成的 Promise 内容上运行回调，
因此 Promise 所包含值的类型必须与回调期望的输入类型相同。

在 Promise 和回调上调用后，例如 `bind p c`、`bind`
函数执行以下三件事之一，具体取决于 `p` 的状态：

* 如果 `p` 已履行，则立即在 `p` 的内容上运行 `c`。
返回的 Promise 可能会或可能不会处于待处理状态，具体取决于
  `c` 做什么。

* 如果 `p` 已被拒绝，则 `c` 不会运行。返回的 Promise 也会被拒绝，
并带有与 `p` 相同的异常。

* 如果 `p` 待处理，则 `bind` 不会等待 `p` 被解析，也不会等待
`c` 运行。相反，`bind` 只是注册一个将来要运行的回调，
  当（或如果）Promise 被履行时运行。因此，`bind` 函数会返回一个新的 Promise。
  当（或如果）回调在未来某个时间完成运行时，这个 Promise 可能会被解析。
  它的内容可以是回调本身返回的 Promise 中包含的任何内容。

```{note}
对于上面的第一种情况：Lwt 源代码声称这种行为可能
更改：在高负载下，`c` 可能会被注册运行
稍后。但截至 [v5.5.0][lwt-bind-src] 该行为尚未激活。所以，不要
担心它&mdash;这一段只是为了面向未来
讨论。
```

[lwt-bind-src]: https://github.com/ocsigen/lwt/blob/73f1a0f0acd5540f25e58bc410e1f63271189c6c/src/core/lwt.ml#L1820

让我们更详细地考虑最后一种情况。我们有一个类型为
`'a Lwt.t` 的 Promise，以及两个类型为 `'b Lwt.t` 的 Promise：

* `'a Lwt.t` 类型的 Promise（称为 Promise X）是 `bind` 的输入。它
当调用 `bind` 以及 `bind` 返回时，该函数处于挂起状态。

* 第一个类型为 `'b Lwt.t` 的 Promise，称为 Promise Y，由 `bind` 创建，
  并立即返回给用户。此时它仍然处于待处理状态。

* 第二个类型为 `'b Lwt.t` 的 Promise，称为 Promise Z，此时还没有创建。
  它稍后才会出现：如果 Promise X 得到履行，回调就会用 X 的内容运行，
  而回调会返回 Promise Z。Z 的状态没有任何保证；回调返回时，
  Z 很可能仍处于待处理状态。

* 如果 Z 最终被履行，Y 的内容就会更新为 Z 的内容。如果 Z 被拒绝，
  Y 也会因同一个异常被拒绝。如果 Z 一直待处理，Y 也会一直待处理。
  回想一下，Y 已经返回给用户了。把 Z 的结果“转发”给 Y，
  可以确保用户最终得到从 Promise X 开始的整条操作链的结果。

`bind` 之所以设计成这种类型，是为了让程序员可以设置
回调的*顺序链*。例如下面的代码
异步读取一个字符串；然后当该字符串被读取后，继续
异步读取第二个字符串；然后打印两者的串联
字符串：

```ocaml
Lwt.bind (read_line stdin) (fun s1 ->
  Lwt.bind (read_line stdin) (fun s2 ->
    Lwt_io.printf "%s\n" (s1^s2)));;
```

如果你在 utop 中运行它，会再次发生一些令人困惑的事情：
在第一个字符串末尾按 Enter 键，Lwt 将允许 utop 读取一个
字符。问题在于，我们把 Lwt 的输入操作和 utop 自己的输入操作混在了一起。
最好创建一个独立程序并从命令行运行。

为此，请将以下代码放入名为 `read2.ml` 的文件中：
```ocaml
open Lwt_io

let p =
  Lwt.bind (read_line stdin) (fun s1 ->
    Lwt.bind (read_line stdin) (fun s2 ->
      Lwt_io.printf "%s\n" (s1^s2)))

let _ = Lwt_main.run p
```

这里加入了一个新函数：`Lwt_main.run : 'a Lwt.t -> 'a`。它会等待输入的
Promise 被履行，然后返回其中的内容。整个程序通常只在主文件末尾附近
调用一次这个函数；它的输入通常是一个 Promise，而这个 Promise 的解析
表示所有执行都已经完成。

创建Dune文件：
```text
(executable
 (name read2)
 (libraries lwt.unix))
```

运行程序，输入几个字符串：
```console
dune exec ./read2.exe
My first string
My second string
My first stringMy second string
```

现在尝试删除 `read2.ml` 的最后一行。  你会看到该程序
立即退出，无需等待你输入。

## 作为运算符的 Bind

`Lwt.Infix` 模块定义了一个
中缀运算符写为 `>>=` ，与 `bind` 相同。也就是说，而不是
写 `bind p c`，你可以写 `p >>= c`。这个运算符让代码更容易书写，
不需要像前面的例子那样加许多额外的括号和缩进：

```ocaml
open Lwt_io
open Lwt.Infix

let p =
  read_line stdin >>= fun s1 ->
  read_line stdin >>= fun s2 ->
  Lwt_io.printf "%s\n" (s1^s2)

let _ = Lwt_main.run p
```

直观地解析 `p` 定义的方法是将每一行视为
计算某个 Promise 值。第一行 `read_line stdin >>= fun s1 ->`
表示创建一个 Promise；当它被履行后，取出其中的内容并命名为 `s1`。
第二行含义相同，只是内容被命名为 `s2`。第三行创建最终的 Promise，
它的内容最终由 `Lwt_main.run` 取出，程序此时可能终止。

`>>=` 运算符可能是函数式语言 Haskell 中最著名的，
它广泛地将它用于单子。我们将在后面的部分中介绍 monad。

## 作为 Let 语法的 Bind

OCaml 有一个*语法扩展*，可以使用
绑定甚至比中缀运算符 `>>=` 更简单。安装语法
扩展，运行以下命令：

`$ opam install lwt_ppx`

通过该扩展，你可以使用专门编写的 `let` 表达式
`let%lwt x = e1 in e2`，相当于 `bind e1 (fun x -> e2)` 或
`e1 >>= fun x -> e2`。我们可以重写我们的运行示例如下：

```ocaml
open Lwt_io

let p =
  let%lwt s1 = read_line stdin in
  let%lwt s2 = read_line stdin in
  Lwt_io.printf "%s\n" (s1^s2)

let _ = Lwt_main.run p
```

````{note}
要将代码编译为 Dune 项目的一部分，请使用 `dune` 文件，如下所示：
```
(executable
 (public_name ...)
 (name ...)
 (libraries lwt.unix ...)
 (preprocess (pps lwt_ppx)))
```
`libraries` 节加载 `lwt.unix` 以便我们可以使用 `Lwt_io`，而 `preprocess` 节则通过 `lwt_ppx` 使 `let%lwt` 可用。
````

现在代码看起来与它的等效同步代码几乎一模一样
版本会是。但不要被愚弄了：所有的异步 I/O、Promise、
和回调仍然存在。因此，对 `p` 求值时，首先会给 Promise 注册回调，
然后继续求值 `Lwt_main.run`，并不会等待第一个字符串读取完成。
要亲自验证这一点，可以运行下面的代码：

```ocaml
open Lwt_io

let p =
  let%lwt s1 = read_line stdin in
  let%lwt s2 = read_line stdin in
  Lwt_io.printf "%s\n" (s1 ^ s2)

let _ = Lwt_io.printf "Got here first\n"

let _ = Lwt_main.run p
```

在你有机会输入任何内容之前，就会看到打印出 “Got here first”。

**另一种 `let` 语法。**
我们可以使用 `Lwt.Syntax` 提供的类似 `let*` 语法，而不是加载附加库 `lwt_ppx` 来使 `let%lwt` 可用：

```ocaml
open Lwt_io
open Lwt.Syntax

let p =
  let* s1 = read_line stdin in
  let* s2 = read_line stdin in
  Lwt_io.printf "%s\n" (s1 ^ s2)
```

但我们通常更喜欢使用 `lwt_ppx`，因为它还提供了一些其他有用的语法。
例如，`lwt_ppx` 还使 `try%lwt` 可用，这对于涉及 Promise 的异常处理非常有用。

## 并发组合

`Lwt.bind` 函数提供了一种按顺序组合回调的方式：先运行一个回调，
再运行另一个回调，然后继续下去。库中还提供了其他函数，
用来把许多回调作为一个整体来组合。例如，

* `Lwt.map : 'a Lwt.t -> ('a -> 'b) -> 'b Lwt.t` 很像 `Lwt.bind`，
  但它的回调会立即返回一个 `'b` 类型的*值*，而不是一个类型为
  `'b Lwt.t` 的 *Promise*。`Lwt.map p f` 会返回一个待处理的 Promise，
  直到 `p` 被解析。如果 `p` 因拒绝而解析，回调永远不会被调用，
  待处理的 Promise 也会因同一个异常被拒绝。如果 `p` 因履行而解析
  （例如值为 `v`），待处理的 Promise 就会用 `f v` 解析。注意，
  `f` 本身可能引发异常；此时待处理的 Promise 会因该异常被拒绝。

* `Lwt.join : unit Lwt.t list -> unit Lwt.t` 允许等待多个
  Promise。`Lwt.join ps` 返回一个待处理的 Promise，直到 `ps` 中所有
  Promise 都被解析。你可以在 `join` 返回的 Promise 上注册回调，
  处理那些需要一组 Promise **全部**完成后才能进行的计算。

* `Lwt.pick : 'a Lwt.t list -> 'a Lwt.t` 还可以等待多个
  Promise，但 `Lwt.pick ps` 返回的待处理 Promise 只需要等到
  `ps` 中至少一个 Promise 被解析。你可以在 `pick` 返回的 Promise
  上注册回调，处理那些只需要一组 Promise 中任意一个完成、
  而不关心具体是哪一个的计算。
