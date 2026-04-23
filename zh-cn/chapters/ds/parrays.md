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

# 持久数组

OCaml 的内置 `array` 类型提供恒定时间的获取和设置操作。但它是一种短暂的数据结构。这就引出了一个问题：我们是否可以拥有持久数组，如果可以，我们可以获得多好的性能？

这是我们想要实现的接口：

```{code-cell} ocaml
module type PersistentArray = sig
  type 'a t
  (** The type of persistent arrays whose elements have type ['a]. The
      array indexing is zero based, meaning that the first element is at
      index [0], and the last element is at index [n - 1], where [n] is 
      the length of the array. Any index less than [0] or greater
      than [n - 1] is out of bounds. *)

  val make : int -> 'a -> 'a t
  (** [make n x] is a persistent array of length [n], with each element
      initialized to [x]. Raises [Invalid_argument] if [n] is negative
      or too large for the system. *)

  val length : 'a t -> int
  (** [length a] is the number of elements in [a]. *)

  val get : 'a t -> int -> 'a
  (** [get a i] is the element at index [i] in [a]. Raises [Invalid_argument]
      if [i] is out of bounds. *)

  val set : 'a t -> int -> 'a -> 'a t
  (** [set a i x] is an array that stores [x] at index [i] and otherwise is
      the same as [a]. Raises: [Invalid_argument] if [i] is out of bounds. *)
end
```

该接口本质上与 OCaml 的 `Array` 模块相同，但减少到只有四个基本函数。

接下来我们将看到该接口的三个实现。每个实现都会逐步改善性能。
最终实现基于 Conchon 和 Filliâtre (2007)；参见本节末尾的引用。

## Copy-On-Set 数组

持久数组最简单的实现是在每个 `set` 操作上复制整个数组。这样，数组的旧副本将保留下来——它们不会被以后的 `set` 操作更改。这是实现：

```{code-cell} ocaml
module CopyOnSetArray : PersistentArray = struct
  type 'a t = 'a array

  (** Efficiency: O(n). *)
  let make = Array.make

  (** Efficiency: O(1). *)
  let length = Array.length

  (** Efficiency: O(1). *)
  let get = Array.get
  
  (** Efficiency: O(n). *)
  let set a i x =
    let a' = Array.copy a in (* copy the array *)
    a'.(i) <- x; (* mutate one element *)
    a'
end
```

在这个实现中，我们为 `set` 付出了很大的代价：它不像 `array` 那样是 $O(1)$，
而是 $O(n)$。我们将在下一个实现中对此进行改进。

```{note}
在继续之前，让我们暂停一下并考虑一下 `CopyOnSetArray` 与我们之前见过的任何数据结构不同的一个方面。它满足的接口是用函数式风格编写的，但实现却使用命令式特性。请注意，`set` 操作不会返回 `unit`；相反，它从旧数组中生成一个新数组。在底层，尽管使用了短暂的数据结构 `array`，但它还是实现了持久性。我们可以学到的一个教训是，可以使用命令式语言提供的功能来构建持久数据结构。
```

## 版本树数组

copy-on-set 中昂贵的 `set` 操作做了太多工作。即使只更改一个数组元素，
也会复制所有数组元素。为了获得更好的性能，我们可以消除复制，
改为保留所有已发生 `set` 操作的简短日志。日志中的每个条目只需要记录一项更改。
例如，假设我们有以下操作序列：

```
let a0 = make 3 0
let a1 = set a0 1 7
let a2 = set a1 2 8
let a3 = set a1 2 9
```

我们的日志会说：

- `a0` 是 `[|0; 0; 0|]`。这需要线性空间来存储。
- `a1` 与 `a0` 相同，只是索引 `1` 是 `7`。这只需要恒定的空间来存储。
- `a2` 与 `a1` 相同，只是索引 `2` 是 `8`。再次，恒定的空间。
- `a3` 与 `a1` 相同，只是索引 `2` 是 `9`。再次，恒定的空间。

请注意 `a2` 和 `a3` 如何共享相同的基数组 `a1`，但通过将索引 `2` 设置为 `8` 或 `9` 来以不同的方式进行区分。因此，该日志的结构最好不要表示为列表，而是表示为树：

```text
       (entry for a0)
             |
       (entry for a1)
       /            \
(entry for a2)     (entry for a3)
```

该树中的每个节点都告诉我们数组的不同_版本_应该是什么。这个想法引导我们引入以下树类型：

```{code-cell} ocaml
type 'a version_tree =
  | Base of 'a array
  | Diff of int * 'a * 'a version_tree
```

`Base` 节点包含数组的基本版本；在上面的示例中，该值是 `a0`。 `Diff` 节点记录由 `set` 操作创建的差异。上面示例的版本树如下所示：

```text
              (Base [|0; 0; 0|])      <---- a0
                      |
                  (Diff 1 7)          <---- a1
                 /          \
a2 ----> (Diff 2 8)        (Diff 2 9) <---- a3
```

树本身显示在该图的中间。 `a0` 到 `a3` 的指针指向该树的各个节点，并捕获数组的每个持久版本。

```{tip}
在理解此版本树类型时，与关联列表的类比可能会有所帮助。每个 `Diff` 节点就像关联列表中的 cons 单元：都包含一对键（数组索引）和一个值（该索引处的元素）。此外，每个 cons 单元然后继续到另一个 cons 单元，直到最终达到 nil 的基本情况，就像版本树最终到达 `Base` 节点的基本情况一样。不过 `Base` 节点比空列表更有趣，因为它包含整个数组。
```

**设置。** 要实现 `set a i x`，我们所要做的就是创建一个新的 `Diff` 节点：

```{code-cell} ocaml
let set a i x = Diff (i, x, a)
```

其效率仅为 $O(1)$，这比按集复制数组有很大改进。

**Get.** 要实现`get a i`，我们只需在树中从`a`开始走一条路径，找到第一个记录索引`i`变化的`Diff`。如果从未发现此类更改，我们可以返回 `Base` 节点中该索引处的值：

```{code-cell} ocaml
let rec get a i =
  match a with
  | Base b -> b.(i)
  | Diff (j, v, a') ->
      if i = j then v else get a' i
```

该实现的效率为 $O(k)$，其中 $k$ 是已在持久数组上执行的 `set` 操作的数量。在最坏的情况下，所有这些 `set` 操作都是在与我们想要的 `get` 不同的索引上执行的，并且它们都是在没有在树中创建任何分支的情况下执行的 - 例如，`make 2 0 |> set 0 1 |> set 0 2 |> ... |> set 0 k |> get 1`。然后树退化为链表，并且 `get` 被迫沿着整个链表走到 `Base` 节点以查找原始值。

请注意，$k$ 可能比数组的大小 $n$ 大得多或小得多。因此，在提高 `set` 的性能时，我们可能会恶化 `get` 的性能。在下一个实现中，我们将回到这个问题并提高 `get` 的性能。

**版本树实现。** 将所有内容放在一起，这里是使用版本树的持久数组的实现：

```{code-cell} ocaml
module VersionTreeArray : PersistentArray = struct
  (** AF: A rep such as [Diff (i, x, Diff (j, y, Base a))] represents the 
      array [a] except element [j] is [y] and element [i] is [x]. If there 
      are multiple diffs for an index, the outermost wins. E.g.,
      [Diff (i, x, Diff (i, y, Base a))] represents an array whose 
      element [i] is [x], not [y]. *)
  type 'a t =
    | Base of 'a array
    | Diff of int * 'a * 'a t

  (** Efficiency: O(n). *)
  let make n x = Base (Array.make n x)

  (** Efficiency: O(k), where k is the number of [set] operations that have
      been performed on the array. *)
  let rec length = function
    | Base b -> Array.length b
    | Diff (_, _, a) -> length a

  (** Efficiency: O(k). *)
  let rec get a i =
    match a with
    | Base b -> b.(i)
    | Diff (j, x, a') ->
        if i = j then x else get a' i

  (** Efficiency: O(1). *)
  let set a i x = Diff (i, x, a)
end
```

## 版本树数组变基

使用版本树后，持久数组的 `set` 操作变成了常数时间，但 `get` 操作不再是常数时间：
它们是 $O(k)$，其中 $k$ 是已执行的 `set` 操作数量。
有没有办法让两个操作都保持常数时间，同时仍然持久？答案是：几乎可以！

现在，存储在 `Base` 节点中的数组原始版本是 _primary_，
并且始终可以通过 `get` 常数时间访问。我们将引入一个新的 _rebasing_ 操作，
它可以让数组的任何其他版本成为主版本。这样，该版本就能获得常数时间的 `get` 访问，
即使其他版本仍然是 $O(k)$。当访问数组版本 $v$ 时（使用 `length` 或 `set`），
我们会修改版本树，使 $v$ 成为主版本。这意味着要改变 `Base` 节点，
使其根据 $v$ 存储内容，并按需调整 `Diff` 节点，以补偿基础数组中的更改。

由于我们现在要改变树，因此需要更改表示类型以添加间接级别：

```{code-cell} ocaml
type 'a rebasing_tree = 'a node ref
and 'a node =
  | Base of 'a array
  | Diff of int * 'a * 'a rebasing_tree
```

**创建和设置。** `make` 和 `set` 操作只需要插入对 `ref` 的调用即可适应新的表示类型：

```{code-cell} ocaml
let make n x = ref (Base (Array.make n x))
let set a i x = ref (Diff (i, x, a))
```

它们的效率保持不变：$O(n)$ 对应 `make`，$O(1)$ 对应 `set`。

**变基。** 为了对树进行变基，我们引入了一个新的递归辅助函数 `rebase : 'a rebasing_tree -> 'a rebasing tree` ，以便 `rebase t` 改变树 `t` ，使 `t` 表示的数组版本成为主要版本。因此，当 `rebase` 返回时 `t` 保证是对 `Base` 节点的引用。

有两种情况需要考虑。首先，如果 `t` 是对 `Base` 节点的引用，那么我们的工作就已经完成了。该版本已经是主要版本。

其次，如果 `t` 是对 `Diff` 节点的引用，那么我们还有工作要做。该节点的形式为 `Diff(i, x, t')`，其中 `t'` 表示数组的另一个版本。我们在 `t'` 上调用 `rebase` 使其成为主要的；之后， `t'` 必须是对 `Base` 节点的引用。这意味着我们有以下情况，其中 `a` 是一个数组：

```text
t  ---> Diff (i, x, t')
t' ---> Base a
```

要使 `t` 成为主节点，我们只需交换这些节点，并交换索引 `i` 处的值。
假设在 `Base` 节点中 `a.(i)` 是 `y`。我们将 `a.(i)` 修改为 `x`；
把该数组称为 `a'`。然后用 `y` 创建一个新的 `Diff` 节点：

```text
t  ---> Base a'
t' ---> Diff (i, y, t)
```

现在 `t` 是主要的，代表与变基之前相同的数组版本。

下面是实现变基的代码：

```{code-cell} ocaml
let rec rebase a =
  match !a with
  | Base b -> b
  | Diff (i, x, a') ->
      let b = rebase a' in
      let old_x = b.(i) in
      b.(i) <- x;
      a := Base b;
      a' := Diff (i, old_x, a);
      b
```

`rebase` 的效率是 $O(k)$，因为 `t` 与其原始 `Base` 之间最多可能存在 $k$ 个 `Diff` 节点。
调用 `rebase t` 之后，再次调用 `rebase t` 只需 $O(1)$，因为 `t` 现在已经是主节点。

**获取和长度。** 现在我们有了 `rebase`，只需对 `length` 和 `get` 进行一点小小的修改即可调用 `rebase`：

```{code-cell} ocaml
let length a = Array.length (rebase a)
let get a i = (rebase a).(i)
```

它们的效率与 `rebase` 相同：第一次调用是 $O(k)$，
之后只要没有同时访问该数组的其他版本，后续调用就是 $O(1)$。

**变基版本树实现：** 将所有内容放在一起，这里是使用变基版本树的持久数组的实现：

```{code-cell} ocaml
module RebasingVersionTreeArray : PersistentArray = struct
  type 'a t = 'a node ref
  (** See [VersionTreeArray]. *)

  and 'a node =
    | Base of 'a array
    | Diff of int * 'a * 'a t

  (** Efficiency: O(n). *)
  let make n x = ref (Base (Array.make n x))

  (** Efficiency: O(k), where k is the number of diffs between this version
      of the array and its base. At most, that is the number of [set] 
      operations performed on all versions of the array. If there aren't 
      any diffs, O(1). After a [rebase], remains O(1) until a different 
      version of the array is accessed. Not tail recursive. *)
  let rec rebase a =
    match !a with
    | Base b -> b
    | Diff (i, x, a') ->
        let b = rebase a' in
        let old_x = b.(i) in
        b.(i) <- x;
        a := Base b;
        a' := Diff (i, old_x, a);
        b

  (** Efficiency: Same as [rebase]. *)
  let length a = Array.length (rebase a)

  (** Efficiency: Same as [rebase]. *)
  let get a i = (rebase a).(i)

  (** Efficiency: O(1). *)
  let set a i v = ref (Diff (i, v, a))
end
```

通过变基，我们现在可以对数组的主（最近访问的版本）进行 $O(1)$ `get` 和 `set` 操作。我们支付 $O(k)$ 价格来更改为新的主版本，但之后，对其的访问仍保持 $O(1)$ 直到另一个变基发生。

## 引用

我们的最终实现与 Sylvain Conchon 和 Jean-Christophe Filliâtre 的实现最为相似（_持久并查数据结构_，ACM 机器学习研讨会，2007 年）。他们将版本树的想法归功于 Henry Baker（LISP 1.5 中的浅绑定，_CACM_ 21:7, 1978）和变基（浅绑定使函数数组更快，_SIGPLAN Not._, 26(8):145-147, 1991）。
