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

# 示例：树

{{ video_embed | replace("%%VID%%", "WV9DGpRTAE0")}}

树是一种非常有用的数据结构。你可能还记得，CS 2110 中的*二叉树*（binary tree）是一个包含一个值和两棵子树的节点。二叉树也可以是一棵空树，我们用空树来表示不存在子节点的情况。

## 用元组表示

下面是二叉树数据类型的定义：
```{code-cell} ocaml
type 'a tree =
| Leaf
| Node of 'a * 'a tree * 'a tree
```

节点携带一个类型为 `'a` 的数据项，并拥有左子树和右子树。叶子（Leaf）是空的。将此定义与列表的定义进行比较，注意它们的结构有多么相似：

```ocaml
type 'a tree =                        type 'a mylist =
  | Leaf                                | Nil
  | Node of 'a * 'a tree * 'a tree      | Cons of 'a * 'a mylist
```

唯一的本质区别是 `Cons` 携带一棵子树，而 `Node` 携带两棵子树。

下面是构造一棵小树的代码：
```{code-cell} ocaml
(* the code below constructs this tree:
         4
       /   \
      2     5
     / \   / \
    1   3 6   7
*)
let t =
  Node(4,
    Node(2,
      Node(1, Leaf, Leaf),
      Node(3, Leaf, Leaf)
    ),
    Node(5,
      Node(6, Leaf, Leaf),
      Node(7, Leaf, Leaf)
    )
  )
```

树的*大小*（size）是其中节点的数量（即 `Node` 的数量，不包括 `Leaf`）。例如，上面的树 `t` 的大小是 7。下面这个函数 `size : 'a tree -> int` 返回一棵树中的节点数：
```
let rec size = function
  | Leaf -> 0
  | Node (_, l, r) -> 1 + size l + size r
```

## 用记录表示

接下来，我们将树类型修改为用记录类型来表示树节点。在 OCaml 中，我们必须定义两种相互递归的类型：一种表示树节点，另一种表示（可能为空的）树：

```{code-cell} ocaml
type 'a tree =
  | Leaf
  | Node of 'a node

and 'a node = {
  value: 'a;
  left: 'a tree;
  right: 'a tree
}
```

这是一个示例树：
```{code-cell} ocaml
(* represents
      2
     / \
    1   3  *)
let t =
  Node {
    value = 2;
    left = Node {value = 1; left = Leaf; right = Leaf};
    right = Node {value = 3; left = Leaf; right = Leaf}
  }
```

我们可以使用模式匹配来编写遍历树的常见递归算法。例如，下面是对树的递归搜索：

```{code-cell} ocaml
(** [mem x t] is whether [x] is a value at some node in tree [t]. *)
let rec mem x = function
  | Leaf -> false
  | Node {value; left; right} -> value = x || mem x left || mem x right
```
函数名 `mem` 是"member"（成员）的缩写；标准库经常以此命名那些在集合数据结构中搜索、判断某个元素是否是集合成员的函数。

下面是一个计算树的*前序*（preorder）遍历的函数：每个节点在其子节点之前被访问，并按访问顺序将值收集到列表中：
```{code-cell} ocaml
let rec preorder = function
  | Leaf -> []
  | Node {value; left; right} -> [value] @ preorder left @ preorder right
```
```{code-cell} ocaml
preorder t
```
虽然从上面的代码来看算法非常清晰，但由于 `@` 运算符的存在，在不平衡树上它需要二次方时间。这个问题可以通过引入一个额外的参数 `acc` 来累积每个节点的值来解决，代价是代码可读性有所下降：
```{code-cell} ocaml
let preorder_lin t =
  let rec pre_acc acc = function
    | Leaf -> acc
    | Node {value; left; right} -> value :: (pre_acc (pre_acc acc right) left)
  in pre_acc [] t
```
上面的版本对树中每个 `Node` 只使用一次 `::` 操作，因此是线性时间的。
