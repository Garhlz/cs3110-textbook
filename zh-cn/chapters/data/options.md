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
托尼·霍尔爵士称他的 `null` 发明为
["billion-dollar mistake"][null-mistake]。
```

[null-mistake]: https://www.infoq.com/presentations/Null-References-The-Billion-Dollar-Mistake-Tony-Hoare/
英国计算机科学家托尼·霍尔爵士把他发明的 `null` 称为
除了这些可能之外，OCaml 还提供了一个更好的解决方案，叫做*选项*。（Haskell 的使用者会把选项识别为 Maybe 单子。）

你可以把选项想象成一个密封的盒子。盒子里可能有东西，也可能是空的。在打开盒子之前，我们不知道是哪种情况。如果打开盒子发现里面有东西，我们可以把它取出来使用。因此，选项提供了一种"可选类型"，本质上是一个二选一的类型：盒子要么满满当当，要么空空如也。

在上面的 `list_max` 例子中，我们希望在列表为空时返回一个空盒子，或者在列表非空时返回一个包含最大元素的盒子。

下面是创建一个里面装有 `42` 的选项的方法：

```{code-cell} ocaml
Some 42
```

下面是创建一个像空盒子一样的选项的方法：

```{code-cell} ocaml
None
```

`Some` 表示盒子里有东西，值是 `42`。`None` 表示盒子是空的。

与 `list` 一样，我们把 `option` 称为*类型构造器*：给定一个类型，它产生一个新的类型；但它本身不是一个类型。所以对于任何类型 `t`，我们可以写 `t option` 作为一个类型。但 `option` 单独不能用作类型。`t option` 类型的值可能包含一个 `t` 类型的值，也可能什么都不包含。`None` 的类型是 `'a option`，因为它不受任何类型约束——因为里面没有东西。

你可以使用模式匹配来访问选项值 `e` 的内容。下面是一个从选项中提取 `int`（如果存在的话）并将其转换为字符串的函数：

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
`begin`..`end` 包装上面的嵌套模式匹配并不严格
这里是必需的，但这不是一个坏习惯，因为它会阻止潜在的语法
更复杂的代码中的错误。关键字 `begin` 和 `end` 是等效的
至 `(` 和 `)`。
```

在 Java 中，每个对象引用都是隐式的一个选项。要么有一个
引用内的对象，或者那里什么也没有。那个“没什么”是
由值 `null` 表示。Java 并不强制程序员显式地
检查 null 情况，这会导致空指针异常。OCaml 选项
强制程序员在 `None` 的模式匹配中包含一个分支，从而
确保程序员在出现问题时能够考虑到正确的做法
那里什么也没有。所以我们可以将选项视为消除的原则性方法
`null` 来自语言。使用选项通常被认为是更好的编码
练习而不是引发异常，因为它迫使调用者做某事
在 `None` 情况下是明智的。

**选项的语法和语义。**

 - `t option` 是每个类型 `t` 的一个类型。

 - `None` 是 `'a option` 类型的值。

 - 如果 `e : t`，则 `Some e` 是 `t option` 类型的表达式。如果 `e ==> v` 那么
`Some e ==> Some v`
