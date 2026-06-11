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

# 选项

{{ video_embed | replace("%%VID%%", "lByoIw5wpao")}}

假设你想编写一个*通常*返回类型 `t` 的值、但*有时*什么也不返回的函数。例如，你可能想定义一个函数 `list_max`，返回列表中的最大值，但对于空列表，返回什么都不合适：

```ocaml
let rec list_max = function
  | [] -> ???
  | h :: t -> max h (list_max t)
```

有几种可能的解决方案：

- 返回 `min_int`？但这样 `list_max` 就只能用于整数了，不能用于浮点数或其他类型。
- 抛出异常？但函数的使用者必须记得捕获异常。
- 返回 `null`？这在 Java 中可以，但 OCaml 有意不提供 `null` 值。这其实是件好事：调试空指针错误并不有趣。

```{note}
托尼·霍尔爵士（Sir Tony Hoare）称他的 `null` 发明为
["十亿美元的错误"][null-mistake]（billion-dollar mistake）。
```

[null-mistake]: https://www.infoq.com/presentations/Null-References-The-Billion-Dollar-Mistake-Tony-Hoare/

除了上述可能性之外，OCaml 还提供了一种更好的解决方案，叫做*选项*（option）。（Haskell 使用者会将选项识别为 Maybe 单子。）

你可以把选项想象成一个密封的盒子。盒子里可能有东西，也可能是空的。在打开盒子之前，我们不知道是哪种情况。如果打开盒子发现里面有东西，就可以把它取出来使用。因此，选项提供了一种"可选类型"：本质上是一个二选一的类型——盒子要么满满当当，要么空空如也。

在上面的 `list_max` 例子中，当列表为空时我们希望返回一个空盒子，当列表非空时返回一个装有最大元素的盒子。

下面是如何创建一个装有 `42` 的选项：

```{code-cell} ocaml
Some 42
```

下面是如何创建一个空盒子的选项：

```{code-cell} ocaml
None
```

`Some` 表示盒子里有东西，其值是 `42`。`None` 表示盒子是空的。

与 `list` 一样，`option` 是一个*类型构造器*：给定一个类型，它产生一个新的类型；但它本身不是一个类型。因此，对任意类型 `t`，我们可以写 `t option` 作为一个类型，但单独的 `option` 不能用作类型。`t option` 类型的值要么包含一个 `t` 类型的值，要么什么都不包含。`None` 的类型是 `'a option`，因为它不对内容施加任何类型约束——毕竟里面没有东西。

你可以使用模式匹配来访问选项值的内容。下面是一个函数，从选项中提取 `int`（如果存在的话）并将其转换为字符串：

```{code-cell} ocaml
let extract o =
  match o with
  | Some i -> string_of_int i
  | None -> "";;
```

下面是这个函数的几个使用示例：

```{code-cell} ocaml
extract (Some 42);;
extract None;;
```

下面是用选项实现 `list_max` 的方法：

```{code-cell} ocaml
let rec list_max = function
  | [] -> None
  | h :: t -> begin
      match list_max t with
        | None -> Some h
        | Some m -> Some (max h m)
      end
```

```{tip}
上面用 `begin`..`end` 包裹嵌套模式匹配在这里并非严格必需，但这是一个好习惯，因为在更复杂的代码中它可以避免潜在的语法错误。关键字 `begin` 和 `end` 等价于 `(` 和 `)`。
```

在 Java 中，每个对象引用都隐式地是一个选项：要么引用指向某个对象，要么那里什么也没有。那个"什么也没有"用值 `null` 来表示。Java 并不强制程序员显式检查 null 的情况，这导致了空指针异常。而 OCaml 的选项强制程序员在模式匹配中包含 `None` 分支，从而确保程序员在"什么也没有"的情况下必须考虑正确的处理方式。因此，我们可以将选项视为一种有原则地消除语言中 `null` 的方法。使用选项通常被认为是比抛出异常更好的编程实践，因为它强制调用者在 `None` 情况下做出合理的处理。

**选项的语法和语义。**

 - `t option` 是对每个类型 `t` 都存在的类型。

 - `None` 是 `'a option` 类型的值。

 - 如果 `e : t`，则 `Some e` 是 `t option` 类型的表达式。如果 `e ==> v`，则 `Some e ==> Some v`。
