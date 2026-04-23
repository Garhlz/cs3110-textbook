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

树是一种非常有用的数据结构。正如你所记得的，*二叉树*
CS 2110 是一个包含一个值和两个子树的节点。一个二进制
树也可以是一棵空树，我们也用它来表示不存在
子节点。

## 用元组表示

这是二叉树数据类型的定义：
```{code-cell} ocaml
type 'a tree =
| Leaf
| Node of 'a * 'a tree * 'a tree
```

节点携带类型为 `'a` 的数据项，并具有左子树和右子树。  一片叶子
是空的。  将此定义与列表的定义进行比较，并注意如何
类似的它们的结构是：

```ocaml
type 'a tree =                        type 'a mylist =
  | Leaf                                | Nil
  | Node of 'a * 'a tree * 'a tree      | Cons of 'a * 'a mylist
```

唯一本质的区别是 `Cons` 携带一个子列表，而 `Node`
带有两个子树。

这是构造一棵小树的代码：
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

树的*大小*是其中的节点数（即 `Node`s，而不是
`Leaf`s)。例如，上面的树`t`的大小是7。这是一个函数
`size : 'a tree -> int` 返回树中的节点数：
```
let rec size = function
  | Leaf -> 0
  | Node (_, l, r) -> 1 + size l + size r
```

## 记录表示

接下来，让我们修改树类型以使用记录类型来表示树节点。
在 OCaml 中，我们必须定义两种相互递归的类型，一种代表一棵树
节点，一个代表一棵（可能是空的）树：

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

我们可以使用模式匹配来编写常用的递归算法
穿越树木。例如，这是对树的递归搜索：

```{code-cell} ocaml
(** [mem x t] is whether [x] is a value at some node in tree [t]. *)
let rec mem x = function
  | Leaf -> false
  | Node {value; left; right} -> value = x || mem x left || mem x right
```
函数名 `mem` 是“member”的缩写；标准库经常使用
该名称的函数是通过集合数据结构实现搜索
确定某个元素是否是该集合的成员。

这是一个计算树的*预序*遍历的函数，其中
通过构造一个列表，每个节点在其任何子节点之前被访问
这些值按照访问顺序出现：
```{code-cell} ocaml
let rec preorder = function
  | Leaf -> []
  | Node {value; left; right} -> [value] @ preorder left @ preorder right
```
```{code-cell} ocaml
preorder t
```
虽然从上面的代码来看该算法非常清晰，但它需要
由于 `@` 运算符，不平衡树上的二次时间。  那
问题可以通过引入额外的参数 `acc` 来累积来解决
每个节点的值，但代价是使代码不太清晰：
```{code-cell} ocaml
let preorder_lin t =
  let rec pre_acc acc = function
    | Leaf -> acc
    | Node {value; left; right} -> value :: (pre_acc (pre_acc acc right) left)
  in pre_acc [] t
```
上面的版本对树中的每个 `Node` 只使用一次 `::` 操作，
使其成为线性时间。
