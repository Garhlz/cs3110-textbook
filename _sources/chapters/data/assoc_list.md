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

# 关联列表

*映射*（map）是一种将*键*（key）映射到*值*（value）的数据结构。映射也被称为*字典*（dictionary）。映射的一种简单实现是*关联列表*（association list），它就是一个"对"的列表。例如，下面是一个关联列表，将一些形状名称映射到它们的边数：
```{code-cell} ocaml
let d = [("rectangle", 4); ("nonagon", 9); ("icosagon", 20)]
```
注意，关联列表与其说是 OCaml 中的内置数据类型，不如说是另外两种类型（列表和对）的组合。

下面是两个在关联列表中实现插入和查找的函数：
```{code-cell} ocaml
(** [insert k v lst] is an association list that binds key [k] to value [v]
    and otherwise is the same as [lst] *)
let insert k v lst = (k, v) :: lst

(** [lookup k lst] is [Some v] if association list [lst] binds key [k] to
    value [v]; and is [None] if [lst] does not bind [k]. *)
let rec lookup k = function
| [] -> None
| (k', v) :: t -> if k = k' then Some v else lookup k t
```
`insert` 函数只是将一个新的键值映射添加到列表的最前面，它不会费心去检查键是否已经在列表中。`lookup` 函数从左到右扫描列表。因此，如果列表中恰好存在同一个键的多个映射，只有最近插入的那个会被返回。

关联列表的插入是常数时间操作，而查找是线性时间。虽然字典肯定有更高效的实现——我们将在本课程后面学习一些——但对于小型且非性能关键的字典来说，关联列表是一个非常简单的有用实现。OCaml 标准库的 [`List` 模块][list] 中提供了用于关联列表的函数；可以查找 `List.assoc` 及其下方的函数。我们刚刚写的 `lookup` 实际上已经以 `List.assoc_opt` 的名字定义在了库中。库中没有预定义的 `insert` 函数，因为用一对（pair）来实现同样简单。

[list]: https://ocaml.org/api/List.html
