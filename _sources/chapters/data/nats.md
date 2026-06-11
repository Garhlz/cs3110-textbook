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

我们可以用递归变体来定义类似于数字的东西，这证明了我们并不真的需要将数字内置于 OCaml 中！（当然，出于效率考虑，内建数字是一件好事。）

*自然数*要么是*零*，要么是其他自然数的*后继*（successor）。这正是在数理逻辑中定义自然数的方式，而它自然引出了以下 OCaml 类型 `nat`：
```{code-cell} ocaml
type nat = Zero | Succ of nat
```
我们定义了一个新类型 `nat`，其中 `Zero` 和 `Succ` 是该类型的构造函数。这允许我们构建任意多层嵌套 `Succ` 构造函数的表达式。这些值的行为就像自然数一样：

```{code-cell} ocaml
let zero = Zero
let one = Succ zero
let two = Succ one
let three = Succ two
let four = Succ three
```

现在我们可以编写函数来操作这种类型的值。下面的代码中我们会写很多类型标注，以帮助读者区分哪些值是 `nat`，哪些值是 `int`；当然，编译器不需要我们的帮助。

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
