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

# 示例：自然数

我们可以定义一个像数字一样的递归变体，证明我们
实际上不必将数字内置到 OCaml 中！ （为了效率，
不过，这是一件好事。）

*自然数*要么是*零*，要么是其他自然数的*后继*
数量。这就是在数理逻辑中定义自然数的方式
当然，它自然会导致以下 OCaml 类型 `nat`：
```{code-cell} ocaml
type nat = Zero | Succ of nat
```
我们定义了一个新类型`nat`，`Zero`和`Succ`是构造函数
该类型的值。这允许我们构建具有任意值的表达式
嵌套 `Succ` 构造函数的数量。这些值就像自然数一样：

```{code-cell} ocaml
let zero = Zero
let one = Succ zero
let two = Succ one
let three = Succ two
let four = Succ three
```

现在我们可以编写函数来操作这种类型的值。
我们将在下面的代码中写很多类型注释来帮助读者
跟踪哪些值是 `nat` 和 `int`；当然，编译器
不需要我们的帮助。

```{code-cell} ocaml
let iszero = function
  | Zero -> true
  | Succ _ -> false

let pred = function
  | Zero -> failwith "pred Zero is undefined"
  | Succ m -> m
```

同样，我们可以定义一个函数来添加两个数字：

```{code-cell} ocaml
let rec add n1 n2 =
  match n1 with
  | Zero -> n2
  | Succ pred_n -> add pred_n (Succ n2)
```

我们可以将 `nat` 值转换为 `int` 类型，反之亦然：
```{code-cell} ocaml
let rec int_of_nat = function
  | Zero -> 0
  | Succ m -> 1 + int_of_nat m

let rec nat_of_int = function
  | i when i = 0 -> Zero
  | i when i > 0 -> Succ (nat_of_int (i - 1))
  | _ -> failwith "nat_of_int is undefined on negative ints"
```

为了判断一个自然数是偶数还是奇数，我们可以写一个
一对相互递归函数：

```{code-cell} ocaml
let rec even = function Zero -> true | Succ m -> odd m
and odd = function Zero -> false | Succ m -> even m
```
