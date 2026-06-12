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

数组是固定长度的可变序列，支持常数时间的访问和更新。因此它们在很多方面与引用、列表和元组相似。和 ref 一样，它们是可变的。与列表一样，它们是（有限）序列。与元组一样，它们的长度是预先固定的，不能调整大小。

数组的语法与列表类似：

```{code-cell} ocaml
let v = [|0.; 1.|]
```

这段代码创建了一个长度固定为 2 的数组，其内容初始化为 `0.` 和 `1.`。`array` 是一个类型构造器，和 `list` 很像。

稍后可以使用 `<-` 运算符修改这些内容：

```{code-cell} ocaml
v.(0) <- 5.
```

```{code-cell} ocaml
v
```

正如你在该示例中看到的，对数组进行索引的语法是 `array.(index)`，其中括号是强制性的。

[`Array` 模块][array] 提供了许多有用的数组操作函数。

[array]: https://ocaml.org/api/Array.html

**语法。**

* 数组创建：`[|e0; e1; ...; en|]`

* 数组索引：`e1.(e2)`

* 数组赋值：`e1.(e2) <- e3`

**动态语义。**

* 对 `[|e0; e1; ...; en|]` 求值时，将每个 `ei` 求值为值 `vi`，创建一个长度为 `n+1` 的新数组，并将每个值存储在对应的索引位置。

* 对 `e1.(e2)` 求值时，将 `e1` 求值为数组值 `v1`，将 `e2` 求值为整数 `v2`。如果 `v2` 不在数组的范围内（即 `0` 到 `n-1`，其中 `n` 是数组长度），则引发 `Invalid_argument`。否则，在 `v1` 中索引到 `v2` 位置获得值 `v`，并返回 `v`。

* 对 `e1.(e2) <- e3` 求值时，将每个表达式 `ei` 求值为值 `vi`。按索引语义检查 `v2` 是否在范围内。将 `v1` 中索引 `v2` 处的元素修改为 `v3`。

**静态语义。**

* `[|e0; e1; ...; en|] : t array`，如果对所有 `ei` 都有 `ei : t`。

* `e1.(e2) : t`，如果 `e1 : t array` 且 `e2 : int`。

* `e1.(e2) <- e3 : unit`，如果 `e1 : t array` 且 `e2 : int` 且 `e3 : t`。

**循环。**

OCaml 有 while 循环和 for 循环。它们的语法如下：

```ocaml
while e1 do e2 done
for x=e1 to e2 do e3 done
for x=e1 downto e2 do e3 done
```

这三个表达式都会对循环的每次迭代求值 `do` 与 `done` 之间的表达式；当 `e1` 变为 false 时，`while` 循环终止；`for` 循环对从 `e1` 到 `e2` 的每个整数执行一次；`for..to` 循环从 `e1` 开始求值，每次迭代递增 `x`；`for..downto` 循环从 `e1` 开始求值，每次迭代递减 `x`。三个循环在终止后均求值为 `()`。由于它们始终求值为 `()`，因此不如 fold、map 或递归函数通用。

循环本身并不带来可变性，但它们最常与数组这类可变特性结合使用——通常循环会引发副作用。我们也可以使用 `Array.iter`、`Array.map` 和 `Array.fold_left` 等函数来代替循环。

{{ video_embed | replace("%%VID%%", "GkIgGhqHI7M")}}
