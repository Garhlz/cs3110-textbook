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

# 2-3 树

*二三树*或 *2-3 树*是另一种平衡树数据结构，可用于实现集合和映射。
与红黑树一样，2-3 树在避免可变性的同时实现了对数时间性能。
Cormen 等人在*算法导论*中认为 2-3 树由 John Hopcroft 发明（1990 年，第 280 页）。

## 表示类型

2-3 树概括了二叉树，因为 2-3 树中的每个节点都有两个子节点或三个子节点。
这些分别称为 *2-nodes* 和 *3-nodes*。
2 节点包含一个值，3 节点包含两个值：

```{code-cell} ocaml
type 'a t =
  | Leaf
  | Two of {
      lt : 'a t; (* left subtree *)
      v : 'a;    (* value *)
      rt : 'a t  (* right subtree *)
    }
  | Three of {
      lt : 'a t; (* left subtree *)
      vl : 'a;   (* left value *)
      mt : 'a t; (* middle subtree *)
      vr : 'a;   (* right value *)
      rt : 'a t  (* right subtree *)
    }

let empty = Leaf
```

当用于表示集合时，抽象函数会把节点中存储的值（类型为 `'a`）解释为集合中的元素。

2-3 树的表示不变量有两部分。
第一部分是“排序不变量”，它概括了 BST 不变量。
排序不变量表示：

- 对于任何 2 节点 `{lt; v; rt}`，值按 `lt < v < rt` 排序。
  其中 `lt < v` 表示 `lt` 中的所有值都小于 `v`，`v < rt` 的含义类似。

- 对于任何 3 节点 `{lt; vl; mt; vr; rt}`，值按 `lt < vl < mt < vr < rt` 排序。

表示不变量的第二部分是*平衡不变量*，它可以用三种等效的方式表示：

1. 树上的每片叶子都处于相同的深度。
2. 树中的每个兄弟姐妹都处于相同的高度。
3. 树中的每条完整路径（即从根到叶子）都具有相同的长度。

如果我们想与红黑树进行比较，后者可能是陈述平衡不变量的最有用的方法。
回想一下，红黑树允许路径长度相差最多两倍。
因此，2-3 树比红黑树对平衡的要求更严格。

2-3 树中每条完整路径的长度与树中节点的数量成对数，这将产生对数时间运算。

## 成员查询

为了检查 2-3 树中的成员资格，我们使用 BST 成员资格算法的推广。
排序不变量告诉我们，在每个分支，该往哪个方向寻找元素。

```{code-cell} ocaml
let rec mem x = function
 | Leaf -> false
 | Two { lt; v; rt } ->
     if x < v then mem x lt else if x > v then mem x rt else true
 | Three { lt; vl; mt; vr; rt } ->
     if x < vl then mem x lt
     else if x > vr then mem x rt
     else if x > vl && x < vr then mem x mt
     else true
```

## 插入：Appel 算法

要插入元素，像往常一样，我们使用与 `mem` 中相同的搜索过程来查找元素应该在的位置。
如果该元素已在树中，则不进行任何更改。
如果该元素不在树中，则搜索在叶子处结束。
但是我们如何在保持平衡不变的情况下将新元素插入该叶子呢？
以下用于完成该任务的算法可能是民间传说；如果有读者知道可靠的引用，请告诉我们。
但现在，由于迈克尔·克拉克森是从安德鲁·阿佩尔那里学到的，我们将其称为阿佩尔算法。

使用 Appel 算法，我们将搜索结束的叶子转换为一个新的 2 节点，其中没有包含插入值的子节点。
这保持了排序不变式，但通常违反了平衡不变式，因为新的 2 节点导致搜索路径的长度增加一。
另一种说法是：树的高度增加一倍。

因此，我们递归备份树以恢复平衡不变量并确保所有路径具有相同的长度。
如果可能的话，我们的目标是找到一个“吸收”高度变化的地方。
由于我们刚刚创建了一个新的 2 节点，因此当我们向上递归时，需要考虑两种情况：
新节点的父节点是 2 节点，在这种情况下我们执行 *merge* 操作；或者它是一个 3 节点，在这种情况下我们执行 *split* 操作。
这些操作的工作原理如下所述。

### 合并

回想一下，我们试图解决的问题是 2 节点可能变得太高 &mdash; 它的高度可能比其兄弟节点的高度大一。
我们将这样的 2 节点称为“高”节点。
下面，标有星号的节点是高节点。
如果一个高的 2 节点有一个 2 节点父节点，那么父节点可以通过自身变成 3 节点来吸收高度的变化。
如下图所示：

```text
    y              x,y              x
   / \           /  |  \           / \
 *x*  c   ==>   a   b   c  <==    a  *y*
 / \                                 / \
a   b                               b   c
```

在该图中，`a`、`b` 和 `c` 表示子树。
有两种情况：从左边合并一个高节点`*x*`，从右边合并一个高节点`*y*`。
无论哪种情况，tall 节点的值都会合并到其父节点中，从而将父节点从 2 节点转换为 3 节点。
额外的高度被吸收，从而恢复平衡不变性。

合并发生后，我们就完成了插入操作，并且可以一直递归到根，而无需进行进一步的更改。

### 拆分

如果一个高的 2 节点有一个 3 节点父节点怎么办？
那么我们就不能合并，因为那会创建一个 4 节点。

```{Note}
There are such things as *2-3-4 trees*, and perhaps surprisingly they are closely related to red-black trees.
But here we will stick with 2-3 trees.
```

相反，我们将 3 节点父节点“拆分”为两个 2 节点。
与已经存在的 high 2 节点一起，将具有两个 2 节点和一个 3 节点的树更改为具有三个 2 节点的树，如下所示：

```text
    y,z             *y*              x,y
   / | \           /   \            / | \
 *x* c  d  ==>    x     z    <==   a  b *z*
 / \             / \   / \              / \
a   b           a   b c   d            c   d

                     ⇑

                    x,z
                   / | \
                  a *y* d
                    / \
                   b   c
```

需要考虑三种情况：拆分以容纳左侧 (`*x*`)、中间 (`*y*`) 或右侧 (`*z*`) 的高节点。
无论如何，分裂之后，我们都取得了进步。
以 `*y*` 为根的树的所有子树现在都具有相同的高度，因此以 `*y*` 为根的子树内已恢复平衡。
然而，节点 `*y*` 已经变得*高*。
如果 `*y*` 是整个树的根，那不是问题：不变量仍然成立。
但如果 `*y*` 不是根，则 `*y*` 有某个兄弟节点，并且 `*y*` 变得比该兄弟节点更高。
为了解决这个问题，我们需要向上递归。
要么 `*y*` 的父节点会执行合并并吸收高度差异；或者，父级将执行分裂，本身变高，并将高度差异进一步向上传播。

### 完成插入

为了回顾一下，我们决定在每次插入新值时创建一个高的 2 节点。
我们看到一个高的 2 节点可以合并到一个 2 节点父节点中，从而恢复平衡；或者，可以拆分 3 节点父节点，从而创建一个新的高 2 节点，我们继续尝试在树中吸收更高的高度。
请注意，我们从未因任何这些插入、合并或拆分操作而生成高的 3 节点。
因此，我们不必考虑任何与高 3 节点合并或分裂的情况。
这意味着我们已经完成了算法的设计。

我们可以如下所示实现插入。
每个辅助函数返回一对树和一个布尔值，其中布尔值指示树是否已经生长 &mdash; 即返回的树的根是否很高。
（实现这一点的另一种方法是引入自定义变体类型来跟踪树是否生长。）

该代码比红黑树插入要长得多。
部分原因是我们添加了所有注释来解释它。
而且，具有两种不同的节点形状（2 节点与 3 节点）本质上会使代码更加复杂，并且使用记录而不是元组来存储节点携带的数据会使代码更加冗长。
更简洁的实现是可能的。

```{code-cell} ocaml
let impossible () = failwith "impossible: grow returns Two"

(** [ins x t] inserts [x] into [t] using Appel's algorithm. Returns:
    [new_t, grew], where [new_t] is the new tree (including [x]) and [grew] is
    whether the tree height grew. *)
let rec ins (x : 'a) (t : 'a t) : 'a t * bool =
  match t with
  | Leaf ->
      (* Insertion into a leaf creates a new 2-node, which grows the
          height. *)
      (Two { lt = Leaf; v = x; rt = Leaf }, true)
  | Two { lt; v; rt } ->
      if x = v then
        (* If [x] is already in the tree, no change is needed. *)
        (t, false)
      else
        (* Otherwise, insert [x] into the left or right subtree, and
            incorporate the current 2-node into the result *)
        ins_sub2 x lt v rt
  | Three { lt; vl; mt; vr; rt } ->
      if x = vl || x = vr then
        (* If [x] is already in the tree, no change is needed. *)
        (t, false)
      else
        (* Otherwise, insert [x] into the left, middle, or right subtree, and
            incorporate the current 3-node into the result*)
        ins_sub3 x lt vl mt vr rt

(** [ins_sub2 x lt v rt] inserts [x] into one of the subtrees of a 2-node,
    where that two-node is [Two {lt; v; rt}]. Returns [new_t, grew], where
    [new_t] is the new tree (including [lt], [v], and [rt]) and [grew] is
    whether the tree height grew as a result of the insert. Requires:
    [x <> v]. *)
and ins_sub2 (x : 'a) (lt : 'a t) (v : 'a) (rt : 'a t) : 'a t * bool =
  if x < v then
    (* [x] belongs in [lt]. *)
    ins_sub2_left x lt v rt
  else if x > v then (* [x] belongs in [rt]. *)
    ins_sub2_right x lt v rt
  else
    (* [x] belongs in neither [lt] nor [rt], but then we should never have
        called [ins_sub2] on it. *)
    failwith "precondition violated"

(** [ins_sub2_left x lt v rt] inserts [x] into the left subtree of a 2-node,
    where that two-node is [Two {lt; v; rt}]. Returns [new_t, grew], where
    [new_t] is the new tree (including [lt], [v], and [rt]) and [grew] is
    whether the tree height grew as a result of the insert. *)
and ins_sub2_left (x : 'a) (lt : 'a t) (v : 'a) (rt : 'a t) : 'a t * bool =
  match ins x lt with
  | new_lt, false ->
      (* [x] was inserted into [lt] without growing the height, so we can
          safely reattach the resulting subtree without doing any more work to
          rebalance. *)
      (Two { lt = new_lt; v; rt }, false)
  | Two { lt = child_lt; v = child_v; rt = child_rt }, true ->
      (* [x] was inserted into [lt], and that caused [lt] to grow in height
          and have a 2-node at its root. We can merge that 2-node into the
          current 2-node to form a 3-node, which absorbs the change in
          height. *)
      (Three { lt = child_lt; vl = child_v; mt = child_rt; vr = v; rt }, false)
  | _, true ->
      (* Growth must produce a 2-node at the root, which would have been
          handled by the previous branch. *)
      impossible ()

(** [ins_sub2_right x lt v rt] inserts [x] into the right subtree of a 2-node,
    where that two-node is [Two {lt; v; rt}]. Returns [new_t, grew], where
    [new_t] is the new tree (including [lt], [v], and [rt]) and [grew] is
    whether the tree height grew as a result of the insert. *)
and ins_sub2_right (x : 'a) (lt : 'a t) (v : 'a) (rt : 'a t) : 'a t * bool =
  match ins x rt with
  | new_rt, false ->
      (* [x] was inserted into [rt] without growing the height, so we can
          safely reattach the resulting subtree without doing any more work to
          rebalance. *)
      (Two { lt; v; rt = new_rt }, false)
  | Two { lt = child_lt; v = child_v; rt = child_rt }, true ->
      (* [x] was inserted into [rt], and that caused [rt] to grow in height
          and have a 2-node at its root. We can merge that 2-node into the
          current 2-node to form a 3-node, which absorbs the change in
          height. *)
      (Three { lt; vl = v; mt = child_lt; vr = child_v; rt = child_rt }, false)
  | _, true -> impossible ()

(** [ins_sub3 x lt vl mt vr rt] inserts [x] into one of the subtrees of a
    3-node, where that 3-node is [Three {lt; vl; mt; vr; rt}]. Returns
    [new_t, grew], where [new_t] is the new tree (including [lt], [vl], [mt],
    [vr], and [rt]) and [grew] is whether the tree height grew as a result of
    the insert. Requires: [x <> vl && x <> vr]. *)
and ins_sub3 (x : 'a) (lt : 'a t) (vl : 'a) (mt : 'a t) (vr : 'a) (rt : 'a t)
    : 'a t * bool =
  if x < vl then
    (* [x] belongs in [lt]. *)
    ins_sub3_left x lt vl mt vr rt
  else if x > vr then
    (* [x] belongs in [rt]. *)
    ins_sub3_right x lt vl mt vr rt
  else if x > vl && x < vr then
    (* [x] belongs in [mt]. *)
    ins_sub3_middle x lt vl mt vr rt
  else
    (* [x] belongs in neither [lt] nor [mt] nor [rt], but then we should never
        have called [ins_sub3] on it. *)
    failwith "precondition violated"

(** [ins_sub3_left x lt vl mt vr rt] inserts [x] into the left subtree of a
    3-node, where that 3-node is [Three {lt; vl; mt; vr; rt}]. Returns
    [new_t, grew], where [new_t] is the new tree (including [lt], [vl], [mt],
    [vr], and [rt]) and [grew] is whether the tree height grew as a result of
    the insert. *)
and ins_sub3_left
    (x : 'a)
    (lt : 'a t)
    (vl : 'a)
    (mt : 'a t)
    (vr : 'a)
    (rt : 'a t) : 'a t * bool =
  match ins x lt with
  | new_lt, false ->
      (* [x] was inserted into [lt] without growing the height, so we can
          safely reattach the resulting subtree without doing any more work to
          rebalance. *)
      (Three { lt = new_lt; vl; mt; vr; rt }, false)
  | Two { lt = child_lt; v = child_v; rt = child_rt }, true ->
      (* [x] was inserted into [lt], and that caused [lt] to grow in height
          and have a 2-node at its root. We cannot merge that 2-node into the
          current 3-node. Instead, we split the 3-node into 2-nodes, which
          causes the growth to continue upward in the tree. *)
      ( Two
          {
            lt = Two { lt = child_lt; v = child_v; rt = child_rt };
            v = vl;
            rt = Two { lt = mt; v = vr; rt };
          },
        true )
  | _, true ->
      (* Growth must produce a 2-node at the root, which would have been
          handled by the previous branch. *)
      impossible ()

(** [ins_sub3_right x lt vl mt vr rt] inserts [x] into the right subtree of a
    3-node, where that 3-node is [Three {lt; vl; mt; vr; rt}]. Returns
    [new_t, grew], where [new_t] is the new tree (including [lt], [vl], [mt],
    [vr], and [rt]) and [grew] is whether the tree height grew as a result of
    the insert. *)
and ins_sub3_right
    (x : 'a)
    (lt : 'a t)
    (vl : 'a)
    (mt : 'a t)
    (vr : 'a)
    (rt : 'a t) : 'a t * bool =
  match ins x rt with
  | new_rt, false ->
      (* [x] was inserted into [rt] without growing the height, so we can
          safely reattach the resulting subtree without doing any more work to
          rebalance. *)
      (Three { lt; vl; mt; vr; rt = new_rt }, false)
  | Two { lt = child_lt; v = child_v; rt = child_rt }, true ->
      (* [x] was inserted into [rt], and that caused [rt] to grow in height
          and have a 2-node at its root. We cannot merge that 2-node into the
          current 3-node. Instead, we split the 3-node into 2-nodes, which
          causes the growth to continue upward in the tree. *)
      ( Two
          {
            lt = Two { lt; v = vl; rt = mt };
            v = vr;
            rt = Two { lt = child_lt; v = child_v; rt = child_rt };
          },
        true )
  | _, true ->
      (* Growth must produce a 2-node at the root, which would have been
          handled by the previous branch. *)
      impossible ()

(** [ins_sub3_middle x lt vl mt vr rt] inserts [x] into the middle subtree of
    a 3-node, where that 3-node is [Three {lt; vl; mt; vr; rt}]. Returns
    [new_t, grew], where [new_t] is the new tree (including [lt], [vl], [mt],
    [vr], and [rt]) and [grew] is whether the tree height grew as a result of
    the insert. *)
and ins_sub3_middle
    (x : 'a)
    (lt : 'a t)
    (vl : 'a)
    (mt : 'a t)
    (vr : 'a)
    (rt : 'a t) : 'a t * bool =
  match ins x mt with
  | new_mt, false ->
      (* [x] was inserted into [mt] without growing the height, so we can
          safely reattach the resulting subtree without doing any more work to
          rebalance. *)
      (Three { lt; vl; mt = new_mt; vr; rt }, false)
  | Two { lt = child_lt; v = child_v; rt = child_rt }, true ->
      (* [x] was inserted into [mt], and that caused [mt] to grow in height
          and have a 2-node at its root. We cannot merge that 2-node into the
          current 3-node. Instead, we split the 3-node into 2-nodes, which
          causes the growth to continue upward in the tree. *)
      ( Two
          {
            lt = Two { lt; v = vl; rt = child_lt };
            v = child_v;
            rt = Two { lt = child_rt; v = vr; rt };
          },
        true )
  | _, true ->
      (* Growth must produce a 2-node at the root, which would have been
          handled by the previous branch. *)
      impossible ()

let insert x s =
  let new_tree, _grew = ins x s in
  new_tree
```
