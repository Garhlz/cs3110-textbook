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

*映射*是一种将*键*映射到*值*的数据结构。映射也被称为
*词典*。映射的一种简单实现是*关联列表*，它
是一个对的列表。例如，这里是一个关联列表，它映射了一些
形状名称与其边数相关：
```{code-cell} ocaml
let d = [("rectangle", 4); ("nonagon", 9); ("icosagon", 20)]
```
请注意，关联列表与其说是 OCaml 中的内置数据类型，不如说是
其他两种类型的组合：列表和对。

下面是两个在关联中实现插入和查找的函数
列表：
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
`insert` 函数只是在前面添加一个从键到值的新映射
列表中的。它不会费心去检查密钥是否已经在列表中。
`lookup` 函数从左到右查看列表。所以如果有的话
列表中某个给定键恰好有多个映射，只有最近的一个
插入的一个将被返回。

因此，关联列表中的插入是常数时间，而查找是
线性时间。尽管肯定有更有效的实现
字典&mdash;我们将在本课程后面学习一些&mdash;关联
对于小型字典来说，列表是一个非常简单且有用的实现，
不是性能关键。OCaml 标准库具有以下函数
[`List` module][list] 中的关联列表；寻找 `List.assoc` 和
文档中其下方的函数。我们刚刚写的 `lookup` 是
实际上已经定义为 `List.assoc_opt`。没有预定义的 `insert`
函数在库中，因为仅仅使用一对就很简单了。

[list]: https://ocaml.org/api/List.html
