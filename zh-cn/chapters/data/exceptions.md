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

# 异常

{{ video_embed | replace("%%VID%%", "0zZNEJvcZqg")}}

OCaml 具有与许多其他编程语言类似的异常机制。一个
新类型的 OCaml 异常使用以下语法定义：
```ocaml
exception E of t
```
其中 `E` 是构造函数名称，`t` 是类型。 `of t` 是可选的。
请注意，这与定义变体类型的构造函数有何相似之处。对于
示例：
```{code-cell} ocaml
exception A
exception B
exception Code of int
exception Details of string
```

要创建异常值，请使用与创建异常值相同的语法
变体值。例如，这里是一个异常值，其构造函数是
`Failure`，带有 `string`：
```{code-cell} ocaml
Failure "something went wrong"
```
这个构造函数是在[标准库中预定义][stdlib-exn]的，也是较常见的异常之一
OCaml 程序员使用。

[stdlib-exn]: https://ocaml.org/manual/core.html#ss:predef-exn

要引发异常值 `e`，只需编写
```ocaml
raise e
```

标准库中有一个方便的函数 `failwith : string -> 'a`
这会引发 `Failure`。即 `failwith s` 相当于
`raise (Failure s)`。

{{ video_embed | replace("%%VID%%", "XTdT1zdF2IY")}}

要捕获异常，请使用以下语法：
```ocaml
try e with
| p1 -> e1
| ...
| pn -> en
```
表达式 `e` 可能引发异常。如果没有，则整个
`try` 表达式的计算结果为 `e` 的值。如果 `e` 确实引发异常
值 `v`，该值 `v` 与提供的模式完全匹配
就像 `match` 表达式一样。

## 异常是可扩展的变体

所有异常值都具有类型 `exn`，它定义在
[core][core] 中。不过，这是一种不寻常的变体，称为“可扩展”
变体：即使变体类型本身已经定义完成，它仍然允许之后再定义新的构造函数。
如果你感兴趣，更多信息请参阅 OCaml 手册中关于
[可扩展变体][extvar]的说明。

[core]: https://ocaml.org/manual/core.html
[extvar]: https://ocaml.org/manual/extn.html

## 异常语义

由于异常只是变体，因此它们的大部分语法和语义已经
由变体的语法和语义覆盖。只有一个例外：也就是
如何处理“引发异常”的动态语义。

**动态语义。** 正如我们最初所说，每个 OCaml 表达式要么

* 求值为一个值

* 引发异常

* 或无法终止（即“无限循环”）。

到目前为止，我们只介绍了处理动态语义的部分
这三种情况中的第一种。当我们加入异常之后会发生什么？现在，
表达式的求值要么生成一个值，要么生成一个*异常包*。
数据包不是正常的 OCaml 值；唯一的语言片段
识别它们的是 `raise` 和 `try`。例如，异常值
`Failure "oops"` 是由以下命令生成的异常包的一部分
`raise (Failure "oops")`，但数据包不仅仅包含异常
值；例如，它还可以包含栈跟踪。

对于 `try` 以外的任何表达式 `e`，如果计算 `e` 的某个子表达式
产生异常包 `P`，那么求值 `e` 也会产生包 `P`。

但现在我们第一次遇到一个问题：子表达式按照什么顺序
求值？有时该问题的答案由语义提供，
我们已经给出了。例如，对于 let 表达式，我们知道
绑定表达式必须在主体表达式之前求值。所以
以下代码引发 `A`：
```{code-cell} ocaml
:tags: ["raises-exception"]
let _ = raise A in raise B;;
```
对于函数，OCaml 并没有正式指定函数的求值顺序
及其参数，但当前实现会在函数之前求值参数。
因此，除了产生一些编译器警告之外，以下代码还会引发 `A`
第一个表达式实际上永远不会作为函数应用到
参数上：
```{code-cell} ocaml
:tags: ["raises-exception", "hide-output"]
(raise B) (raise A)
```
这两段代码都会引发相同的异常，这是有道理的，
鉴于我们知道 `let x = e1 in e2` 是 `(fun x -> e2) e1` 的语法糖。

但是下面的代码会引发什么异常呢？
```{code-cell} ocaml
:tags: ["raises-exception", "hide-output"]
(raise A, raise B)
```
答案很微妙。语言规范没有规定元组的各个组成部分
应该按照什么顺序求值。我们的语义也没有精确
指定这个顺序。所以程序员实际上不能依赖它。目前的
OCaml 实现恰好是从右到左求值的，因此上面的代码
实际上会引发 `B`。如果你真的想强制求值顺序，
需要使用 let 表达式：
```{code-cell} ocaml
:tags: ["raises-exception"]
let a = raise A in
let b = raise B in
(a, b)
```
该代码保证引发 `A` 而不是 `B`。

一个有趣的极端情况是当 raise 表达式本身具有
引发以下问题的子表达式：
```{code-cell} ocaml
:tags: ["raises-exception"]
exception C of string;;
exception D of string;;
raise (C (raise (D "oops")))
```
该代码最终会引发 `D`，因为首先要做的是
把 `C (raise (D "oops"))` 求值为一个值。为此需要把
`raise (D "oops")` 求值为一个值。这样会产生包含 `D "oops"` 的异常包，
然后该异常包传播，并成为求值 `C (raise (D "oops"))` 的结果，
因此求值
`raise (C (raise (D "oops")))`。

一旦表达式的计算产生异常包 `P`，该包
传播直到到达 `try` 表达式：
```ocaml
try e with
| p1 -> e1
| ...
| pn -> en
```
`P` 内的异常值与使用提供的模式进行匹配
模式匹配的常规求值规则来匹配，但有一个例外。
如果没有任何模式匹配，则不会生成
包含 `Match_failure` 的新异常包，原来的异常包 `P`
继续传播，直到到达下一个 `try` 表达式。

## 模式匹配

异常也有一种模式形式。下面是一个使用示例：
```{code-cell} ocaml
match List.hd [] with
  | [] -> "empty"
  | _ :: _ -> "non-empty"
  | exception (Failure s) -> s
```
请注意，上面的代码只是一个标准的 `match` 表达式，而不是 `try`
表达式。它会把 `List.hd []` 的结果与提供的三个
模式匹配。众所周知，`List.hd []` 会引发包含
`Failure "hd"` 的异常。*异常模式* `exception (Failure s)` 会匹配这个值。
因此上面的代码会求值为 `"hd"`。

异常模式是一种语法糖。例如考虑以下代码：
```ocaml
match e with
  | p1 -> e1
  | exception p2 -> e2
  | p3 -> e3
  | exception p4 -> e4
```

我们可以重写代码来消除异常模式：
```ocaml
try 
  match e with
    | p1 -> e1
    | p3 -> e3
with
  | p2 -> e2
  | p4 -> e4
``` 

一般来说，如果同时存在异常模式和非异常模式，求值过程如下：
尝试求值 `e`。如果它产生异常包，就使用原始匹配表达式中的
异常模式来处理该包。如果它没有产生异常包，而是产生一个
非异常值，就使用原始匹配表达式中的非异常模式来匹配该值。

## 异常和 OUnit

如果函数的规格说明包含“会引发异常”这一行为，那么你
可能想编写 OUnit 测试来检查函数是否确实如此。
具体做法如下：
```ocaml
open OUnit2

let tests = "suite" >::: [
    "empty" >:: (fun _ -> assert_raises (Failure "hd") (fun () -> List.hd []));
  ]

let _ = run_test_tt_main tests
```
表达式 `assert_raises exn (fun () -> e)` 检查是否
表达式 `e` 引发异常 `exn`。如果是这样，则 OUnit 测试用例成功，
否则会失败。

请注意，`assert_raises` 的第二个参数是一个类型为 `unit -> 'a`
的*函数*，有时称为“thunk”。编写这种类型的函数可能看起来很奇怪：
唯一可能的输入是 `()`。但在函数式语言中，这是一种用于
暂停或延迟程序求值的常见模式。在这里，我们希望 `assert_raises`
在合适的时候再求值 `List.hd []`。如果立即求值 `List.hd []`，
`assert_raises` 就无法检查是否引发了正确的异常。
我们将在后面的章节进一步了解 thunk。

```{warning}
一个常见的错误是忘记 `e` 周围的 `(fun () -> ...)`。如果你做这个
错误，程序仍可能进行类型检查，但 OUnit 测试用例将失败：
没有额外的匿名函数，异常会在之前引发
`assert_raises` 有机会处理它。
```
