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

我们已经看到，一个接受两个参数（类型分别为 `t1` 和 `t2`）并返回类型 `t3` 的值的 OCaml 函数，其类型为 `t1 -> t2 -> t3`。我们在 let 表达式中将两个变量写在函数名后面：

```{code-cell} ocaml
let add x y = x + y
```

另一种定义双参数函数的方式是写一个接受元组的函数：

```{code-cell} ocaml
let add' t = fst t + snd t
```

我们还可以在函数定义中使用元组模式，而不是使用 `fst` 和 `snd`，得到第三种实现：

```{code-cell} ocaml
let add'' (x, y) = x + y
```

使用第一种风格（类型为 `t1 -> t2 -> t3`）的函数称为*柯里化*函数（curried function），而使用第二种风格（类型为 `t1 * t2 -> t3`）的函数称为*非柯里化*函数（uncurried function）。打个比方，柯里化函数更"辣"（hotter），因为你可以部分应用它们（这是非柯里化函数不能做的：不能只传入一半的参数）。"Curry"这个词并非指香料咖喱，而是来自逻辑学家 [Haskell Curry][curry] 的名字——他是少数既有名又有姓被用来命名编程语言的人之一。

[curry]: https://en.wikipedia.org/wiki/Haskell_Curry

有时你会遇到库提供了函数的非柯里化版本，但你想在自己的代码中使用柯里化版本，或者反过来。因此了解如何在两种函数形式之间转换会很有用，就像我们上面为 `add` 所做的那样。

你甚至可以编写两个高阶函数来自动完成这种转换：

```{code-cell} ocaml
let curry f x y = f (x, y)
let uncurry f (x, y) = f x y
```

```{code-cell} ocaml
let uncurried_add = uncurry add
let curried_add = curry add''
```
