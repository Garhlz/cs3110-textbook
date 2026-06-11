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

*类型同义词*（type synonym）是给现有类型取的新名字。例如，下面是一些有助于表示线性代数概念的类型同义词：
```{code-cell} ocaml
type point = float * float
type vector = float list
type matrix = float list list
```

在任何需要 `float * float` 的地方，你都可以使用 `point`，反之亦然。两者完全可互换。在下面的代码中，`get_x` 不关心你传给它的是标注为哪一种类型的值：

```{code-cell} ocaml
let get_x = fun (x, _) -> x

let p1 : point = (1., 2.)
let p2 : float * float = (1., 3.)

let a = get_x p1
let b = get_x p2
```

类型同义词很有用，因为它们让我们可以为复杂类型提供描述性的名字，是让代码更具自文档化能力的一种方式。
