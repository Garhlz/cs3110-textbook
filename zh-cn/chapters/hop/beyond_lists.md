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

# 超越列表

{{ video_embed | replace("%%VID%%", "5Yyk-l-cUNI")}}

像map和fold这样的函数并不局限于列表。它们有意义
几乎任何类型的数据收集。例如，回想一下这棵树
代表：

```{code-cell} ocaml
type 'a tree =
  | Leaf
  | Node of 'a * 'a tree * 'a tree
```

## 树上的 `map`

这个很容易。  我们所要做的就是将函数 `f` 应用于
每个节点的值 `v` ：

```{code-cell} ocaml
let rec map_tree f = function
  | Leaf -> Leaf
  | Node (v, l, r) -> Node (f v, map_tree f l, map_tree f r)
```

## 树上的 `fold`

这个只稍微难一点。让我们为 `'a tree` 开发一个 fold 函数
与我们的 `fold_right` 和 `'a list` 类似。一种思考方式
`List.fold_right` 是列表中的 `[]` 值被替换为
`acc` 参数，并且每个 `::` 构造函数都被替换为
`f` 参数。例如， `[a; b; c]` 是语法糖
`a :: (b :: (c :: []))`。因此，如果我们将 `[]` 替换为 `0`，将 `::` 替换为 `( + )`，
我们得到`a + (b + (c + 0))`。沿着这些思路，我们可以重写以下方法
`fold_right` 这将帮助我们更清晰地思考：

```{code-cell} ocaml
type 'a mylist =
  | Nil
  | Cons of 'a * 'a mylist

let rec fold_mylist f acc = function
  | Nil -> acc
  | Cons (h, t) -> f h (fold_mylist f acc t)
```

算法是一样的。我们所做的只是改变列表的定义
使用用字母字符而不是标点符号编写的构造函数，
并更改 fold 函数的参数顺序。

对于树，我们希望 `acc` 的初始值替换每个 `Leaf`
构造函数，就像它替换列表中的 `[]` 一样。我们想要每个 `Node`
构造函数被运算符替换。但现在操作员需要
*ternary* 而不是 *binary*&mdash; 也就是说，它需要三个
参数而不是两个 &mdash; 因为树节点有一个值，一个左子节点，
和一个右孩子，而列表 cons 只有头和尾。

受这些观察的启发，下面是树上的 fold 函数：
```{code-cell} ocaml
let rec fold_tree f acc = function
  | Leaf -> acc
  | Node (v, l, r) -> f v (fold_tree f acc l) (fold_tree f acc r)
```
如果你将该函数与 `fold_mylist` 进行比较，你会注意到它非常接近
相同。第二次模式匹配中只多了一次递归调用
分支，对应于定义中又出现一次 `'a tree`
那种类型的。

然后我们可以使用 `fold_tree` 来实现我们已经实现的一些树函数
以前见过：
```{code-cell} ocaml
let size t = fold_tree (fun _ l r -> 1 + l + r) 0 t
let depth t = fold_tree (fun _ l r -> 1 + max l r) 0 t
let preorder t = fold_tree (fun x l r -> [x] @ l @ r) [] t
```

为什么我们选择 `fold_right` 而不是 `fold_left` 来进行此开发？因为
`fold_left` 是尾递归，这是我们永远无法实现的
在二叉树上。假设我们先处理左分支；那我们还得
在我们返回之前处理正确的分支。所以总会有工作剩下
在一个分支上进行递归调用后执行的操作。因此，在树上相当于
`fold_right` 是我们所希望的最好的。

我们用来派生 `fold_tree` 的技术适用于任何 OCaml 变体类型
`t`：

* 编写一个递归 `fold` 函数，每个函数接受一个参数
`t` 的构造函数。

* 该 `fold` 函数与构造函数匹配，调用自身
递归地处理它遇到的任何 `t` 类型的值。

* 使用 `fold` 的适当参数来组合所有递归的结果
调用以及每个构造函数中不属于 `t` 类型的所有数据。

这种技术构建了一种称为“变形”的东西，又名“广义”
折叠操作*。要了解有关变形的更多信息，请参加类别课程
理论。

## 树上的 `filter`

这可能是最难设计的。  问题是：如果我们决定
要过滤一个节点，我们应该对其子节点做什么？

- 我们可以对孩子们进行递归。如果过滤后只有一个孩子
仍然存在，我们可以推广它来代替它的父级。但如果两个孩子都
  留下，还是都不留下？然后我们就必须以某种方式重塑树的形状。没有
  了解有关如何使用该树的更多信息&mdash;也就是说，
  它代表的数据类型&mdash;我们被卡住了。

- 相反，我们可以完全消除孩子们。于是决定
过滤节点意味着修剪以该节点为根的整个子树。

后者很容易实现：

```{code-cell} ocaml
let rec filter_tree p = function
  | Leaf -> Leaf
  | Node (v, l, r) ->
    if p v then Node (v, filter_tree p l, filter_tree p r) else Leaf
```
