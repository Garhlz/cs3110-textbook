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

像 map 和 fold 这样的函数并不局限于列表。它们对几乎任何类型的数据集合都有意义。例如，回想一下树的表示：

```{code-cell} ocaml
type 'a tree =
  | Leaf
  | Node of 'a * 'a tree * 'a tree
```

## 树上的 `map`

这个很容易。我们只需将函数 `f` 应用到每个节点的值 `v` 上：

```{code-cell} ocaml
let rec map_tree f = function
  | Leaf -> Leaf
  | Node (v, l, r) -> Node (f v, map_tree f l, map_tree f r)
```

## 树上的 `fold`

这个只稍微难一点。让我们为 `'a tree` 开发一个 fold 函数，类似 `fold_right` 之于 `'a list`。一种理解 `List.fold_right` 的思路是：列表中的 `[]` 值被替换为 `acc` 参数，每个 `::` 构造函数被替换为 `f` 参数。例如，`[a; b; c]` 是 `a :: (b :: (c :: []))` 的语法糖。因此，如果我们把 `[]` 替换为 `0`，把 `::` 替换为 `( + )`，就得到 `a + (b + (c + 0))`。沿着这条思路，我们可以重写 `fold_right`，帮助自己更清晰地思考：

```{code-cell} ocaml
type 'a mylist =
  | Nil
  | Cons of 'a * 'a mylist

let rec fold_mylist f acc = function
  | Nil -> acc
  | Cons (h, t) -> f h (fold_mylist f acc t)
```

算法是一样的。我们只是把列表的定义改成了用字母而不是标点符号书写的构造函数，并调整了 fold 函数的参数顺序。

对于树，我们希望 `acc` 的初始值替换每个 `Leaf` 构造函数，就像它替换列表中的 `[]` 一样。我们希望每个 `Node` 构造函数被某个运算符替换。但这次运算符需要是*三元*的（ternary）而不是*二元*的（binary）——也就是说，它需要三个参数而不是两个——因为树节点有一个值和两个子节点（左孩子和右孩子），而列表的 cons 只有头部和尾部。

受这些观察的启发，下面是树上的 fold 函数：
```{code-cell} ocaml
let rec fold_tree f acc = function
  | Leaf -> acc
  | Node (v, l, r) -> f v (fold_tree f acc l) (fold_tree f acc r)
```
如果你将这个函数与 `fold_mylist` 比较，会发现它们几乎一模一样。区别仅仅是第二个模式匹配分支中多了一次递归调用，对应 `'a tree` 类型定义中多出的那一个自引用。

然后我们可以用 `fold_tree` 来实现我们以前见过的一些树函数：
```{code-cell} ocaml
let size t = fold_tree (fun _ l r -> 1 + l + r) 0 t
let depth t = fold_tree (fun _ l r -> 1 + max l r) 0 t
let preorder t = fold_tree (fun x l r -> [x] @ l @ r) [] t
```

为什么我们在这次推导中选择 `fold_right` 而不是 `fold_left`？因为 `fold_left` 是尾递归的，而这在二叉树上永远无法实现。假设我们先处理左分支，那么在返回之前还必须处理右分支。所以在一个分支的递归调用之后，总还有剩余工作要做。因此，`fold_right` 在树上的等价物就是我们能得到的最好的了。

我们用来推导 `fold_tree` 的技术适用于任意 OCaml 变体类型 `t`：

* 编写一个递归 `fold` 函数，为 `t` 的每个构造函数各取一个参数。

* 该 `fold` 函数匹配各个构造函数，对遇到的任何类型为 `t` 的值递归调用自身。

* 使用 `fold` 的适当参数，将所有递归调用的结果以及每个构造函数中不属于类型 `t` 的数据组合起来。

这种技术构建了一种称为"catamorphism"（又名"广义折叠操作"）的东西。要了解更多，可以去学范畴论。

## 树上的 `filter`

这个可能是最难设计的。问题在于：如果我们决定过滤掉某个节点，应该如何处理它的子节点？

- 我们可以对子节点递归。如果过滤后只有一个子节点留下，可以让它提升到父节点的位置。但如果两个子节点都留下，或两个都不留，怎么办？我们就必须以某种方式重塑树的形状。如果不了解更多关于这棵树的具体用途——即它所代表的数据类型——我们就会陷入困境。

- 另一种做法是，直接连同子节点一起全部删掉。这样，决定过滤某个节点就意味着修剪掉以该节点为根的整棵子树。

后者很容易实现：

```{code-cell} ocaml
let rec filter_tree p = function
  | Leaf -> Leaf
  | Node (v, l, r) ->
    if p v then Node (v, filter_tree p l, filter_tree p r) else Leaf
```
