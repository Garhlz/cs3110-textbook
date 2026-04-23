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

# 数组和循环

{{ video_embed | replace("%%VID%%", "-k4rM1viJH4")}}

数组是固定长度的可变序列，具有恒定时间的访问和更新。
因此它们在很多方面与引用、列表和元组相似。和裁判一样，他们
是可变的。与列表一样，它们是（有限）序列。就像元组一样，它们的长度
是预先固定的，不能调整大小。

数组的语法与列表类似：

```{code-cell} ocaml
let v = [|0.; 1.|]
```

该代码创建一个数组，其长度固定为 2，其内容为
初始化为 `0.` 和 `1.`。关键字 `array` 是一个类型构造函数，很多
像`list`。

稍后可以使用 `<-` 运算符更改这些内容：

```{code-cell} ocaml
v.(0) <- 5.
```

```{code-cell} ocaml
v
```

正如你在该示例中看到的，对数组进行索引使用以下语法
`array.(index)`，其中括号是强制性的。

[`Array` module][array] 在数组上有许多有用的函数。

[array]: https://ocaml.org/api/Array.html

**语法。**

* 数组创建：`[|e0; e1; ...; en|]`

* 数组索引：`e1.(e2)`

* 数组赋值：`e1.(e2) <- e3`

**动态语义。**

* 要评估 `[|e0; e1; ...; en|]`，请将每个 `ei` 评估为值 `vi`，创建
长度为 `n+1` 的新数组，并将数组中的每个值存储在其索引处。

* 要计算 `e1.(e2)`，请将 `e1` 计算为数组值 `v1`，并将 `e2` 计算为数组值
整数 `v2`。如果 `v2` 不在数组的范围内（即 `0` 到
  `n-1`，其中 `n` 是数组的长度），引发 `Invalid_argument`。
  否则，索引到 `v1` 以获取索引 `v2` 处的值 `v`，并返回 `v`。

* 要计算 `e1.(e2) <- e3`，请将每个表达式 `ei` 计算为值 `vi`。
检查 `v2` 是否在范围内，如索引语义所示。变异
  索引 `v2` 处 `v1` 的元素为 `v3`。

**静态语义。**

* `[|e0; e1; ...; en|] : t array` 如果 `ei : t` 对于所有 `ei`。

* `e1.(e2) : t` 如果 `e1 : t array` 和 `e2 : int`。

* `e1.(e2) <- e3 : unit` 如果 `e1 : t array` 和 `e2 : int` 和 `e3 : t`。

**循环。**

OCaml 有 while 循环和 for 循环。它们的语法如下：

```ocaml
while e1 do e2 done
for x=e1 to e2 do e3 done
for x=e1 downto e2 do e3 done
```

这三个表达式中的每一个都计算 `do` 和 `done` 之间的表达式
对于循环的每次迭代；当 `e1` 变为 false 时，`while` 循环终止；
`for` 循环对从 `e1` 到 `e2` 的每个整数执行一次； `for..to` 循环
每次迭代从 `e1` 开始评估并递增 `x` ； `for..downto`
循环从 `e1` 开始计算，每次迭代递减 `x` 。全部三个
循环终止后表达式的计算结果为 `()` 。因为他们
始终求值为 `()`，它们不如 fold、map 或递归那么通用
函数。

循环本身并不可变，但它们最常用于
与数组等可变函数结合&mdash;通常是
循环会产生副作用。我们还可以使用像 `Array.iter` 这样的函数，
`Array.map` 和 `Array.fold_left` 而不是循环。

{{ video_embed | replace("%%VID%%", "GkIgGhqHI7M")}}
