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

OCaml 具有与许多其他编程语言类似的异常机制。一个新类型的 OCaml 异常使用以下语法定义：
```ocaml
exception E of t
```
其中 `E` 是构造函数名称，`t` 是类型。`of t` 是可选的。注意这与定义变体类型的构造函数十分相似。例如：
```{code-cell} ocaml
exception A
exception B
exception Code of int
exception Details of string
```

创建异常值时，使用的语法与创建变体值相同。例如，下面是一个异常值，其构造函数是 `Failure`，携带一个 `string`：
```{code-cell} ocaml
Failure "something went wrong"
```
这个构造函数是在[标准库中预定义][stdlib-exn]的，也是 OCaml 程序员较常使用的异常之一。

[stdlib-exn]: https://ocaml.org/manual/core.html#ss:predef-exn

要引发异常值 `e`，只需写：
```ocaml
raise e
```

标准库中有一个方便的函数 `failwith : string -> 'a`，它会引发 `Failure` 异常。也就是说，`failwith s` 等价于 `raise (Failure s)`。

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

所有异常值都具有类型 `exn`，这个类型定义在[核心库][core]中。不过，它是一种特殊类型的变体，称为”可扩展变体”（extensible variant）：即使变体类型本身已经定义完成，仍然允许之后定义新的构造函数。如果你感兴趣，可以参阅 OCaml 手册中关于[可扩展变体][extvar]的说明。

[core]: https://ocaml.org/manual/core.html
[extvar]: https://ocaml.org/manual/extn.html

## 异常语义

由于异常本质上就是变体，它们的大部分语法和语义已经被变体的语法和语义所覆盖。只有一个例外：如何处理”引发异常”的动态语义。

**动态语义。** 正如我们最初所说，每个 OCaml 表达式要么：

* 求值为一个值

* 引发异常

* 无法终止（即”无限循环”）

到目前为止，我们只介绍了这三种情况中第一种的动态语义。加入异常之后会怎样？现在，表达式的求值要么产生一个值，要么产生一个*异常包*（exception packet）。异常包不是普通的 OCaml 值；唯一能识别它的语言构造是 `raise` 和 `try`。例如，异常值 `Failure “oops”` 是 `raise (Failure “oops”)` 所创建异常包的一部分，但异常包中不仅仅包含异常值，还可能包含栈追踪等信息。

对于任何非 `try` 表达式 `e`，如果求值 `e` 的某个子表达式时产生了异常包 `P`，那么求值 `e` 也会产生异常包 `P`。

但这里我们第一次遇到了一个问题：子表达式按什么顺序求值？有时这个问题的答案已经由我们之前给出的语义所确定。例如，对于 let 表达式，我们知道绑定表达式必须在主体表达式之前求值。因此下面的代码引发 `A`：
```{code-cell} ocaml
:tags: [“raises-exception”]
let _ = raise A in raise B;;
```
对于函数应用，OCaml 没有正式规定函数与其参数之间的求值顺序，但当前实现的策略是先求值参数再求值函数。因此，除了产生一些编译器警告外，下面的代码会引发 `A`，而第一个表达式实际上永远不会被作为函数应用到参数上：
```{code-cell} ocaml
:tags: [“raises-exception”, “hide-output”]
(raise B) (raise A)
```
这两段代码引发相同的异常，而这在意料之中——因为我们知道 `let x = e1 in e2` 是 `(fun x -> e2) e1` 的语法糖。

但下面的代码会引发哪个异常呢？
```{code-cell} ocaml
:tags: [“raises-exception”, “hide-output”]
(raise A, raise B)
```
答案很微妙。语言规范没有规定元组的各组件应该按什么顺序求值，我们的语义也没有精确指定这个顺序。因此程序员实际上不能依赖它。当前 OCaml 的实现恰好是从右向左求值的，所以上面的代码实际上会引发 `B`。如果你真的想强制求值顺序，就需要使用 let 表达式：
```{code-cell} ocaml
:tags: [“raises-exception”]
let a = raise A in
let b = raise B in
(a, b)
```
这段代码保证会引发 `A` 而不是 `B`。

一个有趣的边界情况是当 `raise` 表达式本身包含会引发异常的子表达式时：
```{code-cell} ocaml
:tags: [“raises-exception”]
exception C of string;;
exception D of string;;
raise (C (raise (D “oops”)))
```
这段代码最终引发 `D`，因为首先要将 `C (raise (D “oops”))` 求值为一个值，为此又需要将 `raise (D “oops”)` 求值为一个值。后者产生包含 `D “oops”` 的异常包，然后该异常包向上传播，成为求值 `C (raise (D “oops”))` 的结果，进而又成为求值 `raise (C (raise (D “oops”)))` 的结果。

一旦表达式求值产生了异常包 `P`，该包就会一直向上传播，直到遇到 `try` 表达式：
```ocaml
try e with
| p1 -> e1
| ...
| pn -> en
```
`P` 中的异常值会按照模式匹配的常规求值规则与提供的模式进行匹配，但有一个例外：如果没有任何模式匹配成功，并不会产生包含 `Match_failure` 的新异常包——原来的异常包 `P` 会继续传播，直到到达下一个 `try` 表达式。

## 异常模式

异常也有一种模式形式。下面是一个使用示例：
```{code-cell} ocaml
match List.hd [] with
  | [] -> “empty”
  | _ :: _ -> “non-empty”
  | exception (Failure s) -> s
```
注意上面的代码是一个标准的 `match` 表达式，而非 `try` 表达式。它将 `List.hd []` 的结果与提供的三个模式进行匹配。众所周知，`List.hd []` 会引发包含 `Failure “hd”` 的异常。*异常模式* `exception (Failure s)` 会匹配这个异常包。因此上面的代码求值结果为 `”hd”`。

异常模式是一种语法糖。考虑下面的代码：
```ocaml
match e with
  | p1 -> e1
  | exception p2 -> e2
  | p3 -> e3
  | exception p4 -> e4
```

我们可以重写为消除异常模式的形式：
```ocaml
try 
  match e with
    | p1 -> e1
    | p3 -> e3
with
  | p2 -> e2
  | p4 -> e4
``` 

一般来说，如果同时存在异常模式和非异常模式，求值过程如下：尝试求值 `e`。如果产生异常包，则用原始匹配表达式中的异常模式来处理该异常包。如果产生的是非异常值，则用原始匹配表达式中的非异常模式来匹配该值。

## 异常与 OUnit

如果函数的规格说明中包含”会引发异常”这一行为，你可能想编写 OUnit 测试来验证函数确实如此。具体做法如下：
```ocaml
open OUnit2

let tests = “suite” >::: [
    “empty” >:: (fun _ -> assert_raises (Failure “hd”) (fun () -> List.hd []));
  ]

let _ = run_test_tt_main tests
```
表达式 `assert_raises exn (fun () -> e)` 检查表达式 `e` 是否引发了异常 `exn`。如果是，OUnit 测试用例成功；否则失败。

注意，`assert_raises` 的第二个参数是一个类型为 `unit -> 'a` 的*函数*，有时称为”thunk”。写一个输入只能为 `()` 的函数可能看起来有些奇怪，但在函数式语言中，这是一种常见的用于*暂停*或*延迟*求值的模式。这里我们希望 `assert_raises` 在合适的时机再求值 `List.hd []`。如果立即求值，`assert_raises` 就无法检查是否引发了正确的异常。我们会在后面的章节进一步了解 thunk。

```{warning}
一个常见的错误是忘记在 `e` 外面包裹 `(fun () -> ...)`。如果你犯了这个错误，程序可能仍然通过类型检查，但 OUnit 测试用例会失败：没有额外的匿名函数包裹，异常会在 `assert_raises` 处理它之前就被引发。
```
