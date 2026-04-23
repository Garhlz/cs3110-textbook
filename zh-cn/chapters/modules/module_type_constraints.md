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

# 模块类型限制

我们赞扬了封装的优点。现在我们要做点什么
这可能看起来违反直觉：选择性地违反封装。

作为一个激励示例，这里是一个模块类型，它表示以下值：
支持算术中常见的加法和乘法运算，或更准确地说，支持 *[ring][]*：

[ring]: https://en.wikipedia.org/wiki/Ring_(mathematics)

```{code-cell} ocaml
module type Ring = sig
  type t
  val zero : t
  val one : t
  val ( + ) : t -> t -> t
  val ( * ) : t -> t -> t
  val ( ~- ) : t -> t  (* additive inverse *)
  val to_string : t -> string
end
```

回想一下，我们必须写 `( * )` 而不是 `(*)` 因为后者会
解析为注释的开始。我们在 `( ~- )` 中写入 `~` 来指示
*一元*运算符。

这是一个有点奇怪的例子。我们通常不认为数字是数据
结构。但是，除了一组值和之外，数据结构是什么？
对他们进行操作？ `Ring` 模块类型清楚地表明这就是我们所拥有的。

这是实现该模块类型的模块：

```{code-cell} ocaml
module IntRing : Ring = struct
  type t = int
  let zero = 0
  let one = 1
  let ( + ) = Stdlib.( + )
  let ( * ) = Stdlib.( * )
  let ( ~- ) = Stdlib.( ~- )
  let to_string = string_of_int
end
```

因为 `t` 是抽象的，所以顶层不能给我们提供关于什么的良好输出。
一和一的和是：

```{code-cell} ocaml
IntRing.(one + one)
```

但我们可以将其转换为字符串：

```{code-cell} ocaml
IntRing.(one + one |> to_string)
```

我们甚至可以安装一台漂亮的打印机，以避免手动调用
`to_string`：

```{code-cell} ocaml
let pp_intring fmt i =
  Format.fprintf fmt "%s" (IntRing.to_string i);;

#install_printer pp_intring;;

IntRing.(one + one)
```

我们也可以实现其他类型的环：

```{code-cell} ocaml
module FloatRing : Ring = struct
  type t = float
  let zero = 0.
  let one = 1.
  let ( + ) = Stdlib.( +. )
  let ( * ) = Stdlib.( *. )
  let ( ~- ) = Stdlib.( ~-. )
  let to_string = string_of_float
end
```

然后我们还必须为其安装打印机：

```{code-cell} ocaml
let pp_floatring fmt f =
  Format.fprintf fmt "%s" (FloatRing.to_string f);;

#install_printer pp_floatring;;

FloatRing.(one + one)
```

真的需要在上面的环示例中使类型 `t` 抽象吗？
可以说不是。如果它不是抽象的，我们就不必这么麻烦
将抽象值转换为字符串，或安装打印机。我们来追求
这个想法，接下来。

## 特化模块类型

在过去，我们已经看到我们可以省略模块类型注释，
然后进行单独的检查以确保结构满足签名：

```{code-cell} ocaml
:tags: ["hide-output"]
module IntRing = struct
  type t = int
  let zero = 0
  let one = 1
  let ( + ) = Stdlib.( + )
  let ( * ) = Stdlib.( * )
  let ( ~- ) = Stdlib.( ~- )
  let to_string = string_of_int
end

module _ : Ring = IntRing
```

```{code-cell} ocaml
IntRing.(one + one)
```

有一种更复杂的方法可以实现相同的目标。我们可以
专门化 `Ring` 模块类型以指定 `t` 必须是 `int` 或 `float`。
我们通过使用 `with` 关键字添加*约束*来做到这一点：

```{code-cell} ocaml
module type INT_RING = Ring with type t = int
```

请注意 `INT_RING` 模块类型现在如何指定 `t` 和 `int` 是
相同类型。它向世界揭露或“分享”这一事实，因此我们可以
称这些为“共享约束”。

现在 `IntRing` 可以被赋予该模块类型：

```{code-cell} ocaml
module IntRing : INT_RING = struct
  type t = int
  let zero = 0
  let one = 1
  let ( + ) = Stdlib.( + )
  let ( * ) = Stdlib.( * )
  let ( ~- ) = Stdlib.( ~- )
  let to_string = string_of_int
end
```

由于 `t` 和 `int` 的相等性已公开，因此顶层可以打印
`t` 类型的值，无需漂亮打印机的任何帮助：

```{code-cell} ocaml
IntRing.(one + one)
```

程序员甚至可以将内置 `int` 值与提供的值混合和匹配
通过 `IntRing`：

```{code-cell} ocaml
IntRing.(1 + one)
```

对于浮动也可以做同样的事情：

```{code-cell} ocaml
module type FLOAT_RING = Ring with type t = float

module FloatRing : FLOAT_RING = struct
  type t = float
  let zero = 0.
  let one = 1.
  let ( + ) = Stdlib.( +. )
  let ( * ) = Stdlib.( *. )
  let ( ~- ) = Stdlib.( ~-. )
  let to_string = string_of_float
end
```

事实证明，没有必要单独定义 `INT_RING` 和 `FLOAT_RING`。
`with` 关键字可以用作 `module` 定义的一部分，尽管
由于两个 `=` 很接近，语法变得有点难以阅读
迹象：

```{code-cell} ocaml
module FloatRing : Ring with type t = float = struct
  type t = float
  let zero = 0.
  let one = 1.
  let ( + ) = Stdlib.( +. )
  let ( * ) = Stdlib.( *. )
  let ( ~- ) = Stdlib.( ~-. )
  let to_string = string_of_float
end
```

## 约束

**语法。**

有两种限制。一种是我们上面看到的类型，带有 `type`
方程：

- `T with type x = t`，其中 `T` 是模块类型，`x` 是类型名称，并且
`t` 是一种类型。

另一种是 `module` 方程，它是用于指定的语法糖
两个模块中*所有*类型的相等性：

- `T with module M = N`，其中 `M` 和 `N` 是模块名称。

可以使用 `and` 关键字添加多个约束：

- `T with constraint1 and constraint2 and ... constraintN`

**静态语义。**

受约束模块类型 `T with type x = t` 与 `T` 相同，不同之处在于
`T` 中的 `type x` 声明被 `type x = t` 替换。例如，
比较下面的两个签名输出：

```{code-cell} ocaml
module type T = sig type t end
module type U = T with type t = int
```

同样，`T with module M = N` 与 `T` 相同，除了任何
`M` 模块类型中的声明 `type x` 被替换为
`type x = N.x`。 （对于任何嵌套模块，递归都是相同的。）需要更多
努力给出并理解这个例子：

```{code-cell} ocaml
module type XY = sig
  type x
  type y
end

module type T = sig
  module A : XY
end

module B = struct
  type x = int
  type y = float
end

module type U = T with module A = B

module C : U = struct
  module A = struct
    type x = int
    type y = float
    let x = 42
  end
end
```

重点关注模块类型 `U` 的输出。请注意，`x` 和 `y` 的类型
由于 `module A = B` 约束，它已变成 `int` 和 `float` 。还有
注意模块 `B` 和 `C.A` *不是*同一个模块；后者有一个
其中有额外的项目 `x` 。因此语法 `module A = B` 可能会令人困惑。
约束并不指定两个*模块*相同。相反，它
指定它们的所有*类型*都被限制为相等。

**动态语义。**

约束没有动态语义，因为它们仅针对类型
检查。
