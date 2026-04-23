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

# 柯里化

我们已经看到一个 OCaml 函数接受两个类型为 `t1` 的参数
和 `t2` 并返回类型为 `t3` 的值，其类型为 `t1 -> t2 -> t3`。我们使用
let 表达式中函数名后面的两个变量：

```{code-cell} ocaml
let add x y = x + y
```

定义带有两个参数的函数的另一种方法是编写一个函数
这需要一个元组：

```{code-cell} ocaml
let add' t = fst t + snd t
```

我们可以在中使用元组模式，而不是使用 `fst` 和 `snd`
函数的定义，导致第三种实现：

```{code-cell} ocaml
let add'' (x, y) = x + y
```

调用使用第一种样式（类型为 `t1 -> t2 -> t3`）编写的函数
*柯里化*函数，以及使用第二种风格的函数（类型
`t1 * t2 -> t3`) 被称为*非柯里化*。打个比方，柯里化函数是
“更辣”，因为你可以部分应用它们（这是你不能做的
非柯里化函数：不能传入一半的函数）。事实上，咖喱这个词
不是指香料，而是指一位名叫 [Haskell Curry][curry] 的逻辑学家（其中之一）
一小群拥有以他们的名字命名的编程语言的人
名字和姓氏）。

[curry]: https://en.wikipedia.org/wiki/Haskell_Curry

有时你会遇到提供非柯里化版本的库
函数，但你希望在你自己的代码中使用它的柯里化版本；或恶习
反之亦然。因此了解如何在两种类型之间进行转换是很有用的
函数，就像我们上面对 `add` 所做的那样。

你甚至可以编写几个高阶函数来进行转换
给你：

```{code-cell} ocaml
let curry f x y = f (x, y)
let uncurry f (x, y) = f x y
```

```{code-cell} ocaml
let uncurried_add = uncurry add
let curried_add = curry add''
```
