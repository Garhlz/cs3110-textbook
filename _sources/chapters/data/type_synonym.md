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

# 类型同义词

*类型同义词*是现有类型的新名称。例如，这里
是一些类型的同义词，可能有助于表示来自
线性代数：
```{code-cell} ocaml
type point = float * float
type vector = float list
type matrix = float list list
```

在任何需要 `float * float` 的地方，你都可以使用 `point`，并且
反之亦然。两者是完全可以互换的。在
下面的代码， `get_x` 不关心你是否传递给它一个值
注释为一个与另一个：

```{code-cell} ocaml
let get_x = fun (x, _) -> x

let p1 : point = (1., 2.)
let p2 : float * float = (1., 3.)

let a = get_x p1
let b = get_x p2
```

类型同义词很有用，因为它们让我们可以为复杂的对象提供描述性名称
类型。它们是使代码更加自我记录的一种方式。
