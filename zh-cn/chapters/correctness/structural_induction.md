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

# 结构归纳法

到目前为止，我们已经证明了自然数递归函数的正确性。
我们也可以对变体类型上的递归函数进行正确性证明。
这需要我们弄清楚归纳法如何作用于变体。我们会这样做，
接下来，从表示自然数的变体类型开始，然后
推广到列表、树和其他变体。这种归纳证明技术
有时被称为“结构归纳法”而不是“数学”
归纳*。但这只是一个术语而已。不要纠结于此。
核心思想是完全一样的。

## 自然数归纳法

{{ video_embed | replace("%%VID%%", "Lkb-eTUrHTs")}}

我们使用 OCaml 的 `int` 类型作为自然数的表示。当然，那
类型有些不匹配：负 `int` 值不代表自然数，
我们可以用 `int` 表示的自然数有一个上限。

让我们通过定义我们自己的变体来代表自然来解决这些问题
数字：

```{code-cell} ocaml
type nat = Z | S of nat
```

构造函数`Z`代表零；构造函数 `S` 代表
另一个自然数的后继。所以，

- 0用`Z`表示，
- 1 由 `S Z` 提供，
- 2 由 `S (S Z)` 提供，
- 3 由`S (S (S Z))`，

等等。因此，该变体是*一元*（与二进制或十进制相反）
自然数的表示： `S` 在某个值中出现的次数
`n : nat` 是 `n` 代表的自然数。

我们可以使用以下函数定义自然数的加法：

```{code-cell} ocaml
let rec plus a b =
  match a with
  | Z -> b
  | S k -> S (plus k b)
```

我们可以立即证明以下相当微不足道的主张：

```text
Claim:  plus Z n = n

Proof:

  plus Z n
=   { evaluation }
  n

QED
```

但假设我们想证明这个看似微不足道的主张：

```text
Claim:  plus n Z = n

Proof:

  plus n Z
=
  ???
```

我们不能只评估 `plus n Z`，因为 `plus` 与其第一个匹配
论点，不是第二个。一种可能性是进行案例分析：如果
`n` 是 `Z`，而对于某些 `k` 则为 `S k`？让我们尝试一下。

```text
Proof:

By case analysis on n, which must be either Z or S k.

Case:  n = Z

  plus Z Z
=   { evaluation }
  Z

Case:  n = S k

  plus (S k) Z
=   { evaluation }
  S (plus k Z)
=
  ???
```

我们再次陷入困境，并且出于同样的原因：再次无法评估 `plus`
任何进一步。

当你发现自己需要解决编程中的相同子问题时，你
使用递归。当它发生在证明中时，你可以使用归纳法！

我们需要 `nat` 的归纳原理。这是：

```text
forall properties P,
  if P(Z),
  and if forall k, P(k) implies P(S k),
  then forall n, P(n)
```

与我们之前用于自然数的归纳原理相比，
当我们使用 `int` 代替自然数时：

```text
forall properties P,
  if P(0),
  and if forall k, P(k) implies P(k + 1),
  then forall n, P(n)
```

两者没有本质区别：我们只是用 `Z` 代替
`0` 和 `S k` 代替 `k + 1`。

利用归纳原理，我们可以进行证明：

```text
Claim:  plus n Z = n

Proof: by induction on n.
P(n) = plus n Z = n

Base case: n = Z
Show: plus Z Z = Z

  plus Z Z
=   { evaluation }
  Z

Inductive case: n = S k
IH: plus k Z = k
Show: plus (S k) Z = S k

  plus (S k) Z
=   { evaluation }
  S (plus k Z)
=   { IH }
  S k

QED
```

## 列表归纳法

{{ video_embed | replace("%%VID%%", "Xo3rW_dTqEg")}}

事实证明，自然数和列表非常相似
作为数据类型。  以下是两者的定义，为了比较而对齐：

```ocaml
type    nat  = Z  | S      of nat
type 'a list = [] | ( :: ) of 'a * 'a list
```

两种类型都有一个代表“无”概念的构造函数。两种类型
还有一个构造函数，表示比该类型的另一个值“多一个”：
`S n` 比 `n` 多 1 个，而 `h :: t` 是一个列表，比 `n` 多 1 个元素
`t`。

列表的归纳原理同样与归纳法非常相似
自然数原理。列表的原理如下：

```text
forall properties P,
  if P([]),
  and if forall h t, P(t) implies P(h :: t),
  then forall lst, P(lst)
```

因此，列表的归纳证明具有以下结构：

```text
Proof: by induction on lst.
P(lst) = ...

Base case: lst = []
Show: P([])

Inductive case: lst = h :: t
IH: P(t)
Show: P(h :: t)
```

让我们尝试举一个此类证明的例子。回想一下附加的定义
操作员：

```{code-cell} ocaml
let rec append lst1 lst2 =
  match lst1 with
  | [] -> lst2
  | h :: t -> h :: append t lst2

let ( @ ) = append
```

我们将证明append是关联的。

```text
Theorem: forall xs ys zs, xs @ (ys @ zs) = (xs @ ys) @ zs

Proof: by induction on xs.
P(xs) = forall ys zs, xs @ (ys @ zs) = (xs @ ys) @ zs

Base case: xs = []
Show: forall ys zs, [] @ (ys @ zs) = ([] @ ys) @ zs

  [] @ (ys @ zs)
=   { evaluation }
  ys @ zs
=   { evaluation }
  ([] @ ys) @ zs

Inductive case: xs = h :: t
IH: forall ys zs, t @ (ys @ zs) = (t @ ys) @ zs
Show: forall ys zs, (h :: t) @ (ys @ zs) = ((h :: t) @ ys) @ zs

  (h :: t) @ (ys @ zs)
=   { evaluation }
  h :: (t @ (ys @ zs))
=   { IH }
  h :: ((t @ ys) @ zs)

  ((h :: t) @ ys) @ zs
=   { evaluation of inner @ }
  (h :: (t @ ys)) @ zs
=   { evaluation of outer @ }
  h :: ((t @ ys) @ zs)

QED
```

{{ video_embed | replace("%%VID%%", "4B2jF2zHSCs")}}


## 关于 `fold` 的定理

当我们研究 `List.fold_left` 和 `List.fold_right` 时，我们讨论了它们如何
有时会计算相同的函数，但通常不会。例如，

```
  List.fold_left ( + ) 0 [1; 2; 3]
= (((0 + 1) + 2) + 3
= 6
= 1 + (2 + (3 + 0))
= List.fold_right ( + ) [1; 2; 3] 0
```

但是

```
  List.fold_left ( - ) 0 [1; 2; 3]
= (((0 - 1) - 2) - 3
= -6
<> 2
= 1 - (2 - (3 - 0))
= List.fold_right ( - ) [1; 2; 3] 0
```

基于上面的等式，看起来 `+` 是可交换的并且
关联性，而 `-` 不是，解释了两者之间的差异
折叠函数得到相同的答案。让我们证明一下！

首先，回顾一下折叠函数的定义：

```{code-cell} ocaml
let rec fold_left f acc lst =
  match lst with
  | [] -> acc
  | h :: t -> fold_left f (f acc h) t

let rec fold_right f lst acc =
  match lst with
  | [] -> acc
  | h :: t -> f h (fold_right f t acc)
```

其次，回想一下函数 `f : 'a -> 'a` 可交换的含义以及
联想：

```text
Commutative:  forall x y, f x y = f y x
Associative:  forall x y z, f x (f y z) = f (f x y) z
```

这些可能看起来与正常配方略有不同
属性，因为我们使用 `f` 作为前缀运算符。如果我们要写
`f` 相反作为中缀运算符 `op`，它们看起来会更熟悉：

```text
Commutative:  forall x y, x op y = y op x
Associative:  forall x y z, x op (y op z) = (x op y) op z
```

当 `f` 既可交换又可结合时，我们就有了这个小小的交换
引理让我们交换两个参数：

```
Lemma (interchange): f x (f y z) = f y (f x z)

Proof:

  f x (f y z)
=   { associativity }
  f (f x y) z
=   { commutativity }
  f (f y x) z
=   { associativity }
  f y (f x z)

QED
```

现在我们准备好陈述并证明该定理。

```text
Theorem: If f is commutative and associative, then
  forall lst acc,
    fold_left f acc lst = fold_right f lst acc.

Proof: by induction on lst.
P(lst) = forall acc,
  fold_left f acc lst = fold_right f lst acc

Base case: lst = []
Show: forall acc,
  fold_left f acc [] = fold_right f [] acc

  fold_left f acc []
=   { evaluation }
  acc
=   { evaluation }
  fold_right f [] acc

Inductive case: lst = h :: t
IH: forall acc,
  fold_left f acc t = fold_right f t acc
Show: forall acc,
  fold_left f acc (h :: t) = fold_right f (h :: t) acc

  fold_left f acc (h :: t)
=   { evaluation }
  fold_left f (f acc h) t
=   { IH with acc := f acc h }
  fold_right f t (f acc h)

  fold_right f (h :: t) acc
=   { evaluation }
  f h (fold_right f t acc)
```

现在，我们似乎陷入了困境：
我们想要展示的平等未能“在中间相遇”。但我们其实是
与我们之前证明 `facti` 的正确性时类似的情况：
有一些东西（将 `f` 应用于 `h` 和另一个参数）我们想要
推入最后一行的累加器（这样我们就有 `f acc h`）。

让我们尝试用它自己的引理来证明这一点：

```text
Lemma: forall lst acc x,
  f x (fold_right f lst acc) = fold_right f lst (f acc x)

Proof: by induction on lst.
P(lst) = forall acc x,
  f x (fold_right f lst acc) = fold_right f lst (f acc x)

Base case: lst = []
Show: forall acc x,
  f x (fold_right f [] acc) = fold_right f [] (f acc x)

  f x (fold_right f [] acc)
=   { evaluation }
  f x acc

  fold_right f [] (f acc x)
=   { evaluation }
  f acc x
=   { commutativity of f }
  f x acc

Inductive case: lst = h :: t
IH: forall acc x,
  f x (fold_right f t acc) = fold_right f t (f acc x)
Show: forall acc x,
  f x (fold_right f (h :: t) acc) = fold_right f (h :: t) (f acc x)

  f x (fold_right f (h :: t) acc)
=  { evaluation }
  f x (f h (fold_right f t acc))
=  { interchange lemma }
  f h (f x (fold_right f t acc))
=  { IH }
  f h (fold_right f t (f acc x))

  fold_right f (h :: t) (f acc x)
=   { evaluation }
  f h (fold_right f t (f acc x))

QED
```

现在引理已经完成，我们可以继续证明定理。我们会
在归纳情况开始时重新开始：

```text
Inductive case: lst = h :: t
IH: forall acc,
  fold_left f acc t = fold_right f t acc
Show: forall acc,
  fold_left f acc (h :: t) = fold_right f (h :: t) acc

  fold_left f acc (h :: t)
=   { evaluation }
  fold_left f (f acc h) t
=   { IH with acc := f acc h }
  fold_right f t (f acc h)

  fold_right f (h :: t) acc
=   { evaluation }
  f h (fold_right f t acc)
=   { lemma with x := h and lst := t }
  fold_right f t (f acc h)

QED
```

证明这个定理需要两次归纳，但我们成功了！现在我们知道了
我们观察到的 `+` 行为并非侥幸：任何可交换且
关联运算符导致 `fold_left` 和 `fold_right` 得到相同的答案。

## 树归纳法

{{ video_embed | replace("%%VID%%", "UJyE8ylHFA0")}}

当作为数据类型来看时，列表和二叉树是相似的。  以下是
两者的定义，对齐进行比较：

```{code-cell} ocaml
type 'a list = []   | ( :: ) of           'a * 'a list
type 'a tree = Leaf | Node   of 'a tree * 'a * 'a tree
```

两者都有一个代表“空”的构造函数，并且都有一个构造函数
将 `'a` 类型的值与另一个实例结合在一起
数据类型。  唯一真正的区别是 `( :: )` 仅需要*一个*列表，
而 `Node` 需要“两棵”树。

因此，二叉树的归纳原理与
列表的归纳原理，除了二叉树之外，我们得到
*两个*归纳假设，每个子树一个：

```text
forall properties P,
  if P(Leaf),
  and if forall l v r, (P(l) and P(r)) implies P(Node (l, v, r)),
  then forall t, P(t)
```

因此，二叉树的归纳证明具有以下结构：

```text
Proof: by induction on t.
P(t) = ...

Base case: t = Leaf
Show: P(Leaf)

Inductive case: t = Node (l, v, r)
IH1: P(l)
IH2: P(r)
Show: P(Node (l, v, r))
```

让我们尝试举一个此类证明的例子。这是一个创建的函数
树的镜像，在所有级别交换其左右子树：

```{code-cell} ocaml
let rec reflect = function
  | Leaf -> Leaf
  | Node (l, v, r) -> Node (reflect r, v, reflect l)
```

例如，这两棵树是彼此的反射：

```text
     1               1
   /   \           /   \
  2     3         3     2
 / \   / \       / \   / \
4   5 6   7     7   6 5   4
```

如果你拍摄的是镜像的镜像，你应该得到的是原图
回来。这意味着反射是一个*对合*，它是任何函数 `f` 这样
那个`f (f x) = x`。另一个对合的例子是乘以
整数上的负数。

让我们证明 `reflect` 是一个对合。

```text
Claim: forall t, reflect (reflect t) = t

Proof: by induction on t.
P(t) = reflect (reflect t) = t

Base case: t = Leaf
Show: reflect (reflect Leaf) = Leaf

  reflect (reflect Leaf)
=   { evaluation }
  reflect Leaf
=   { evaluation }
  Leaf

Inductive case: t = Node (l, v, r)
IH1: reflect (reflect l) = l
IH2: reflect (reflect r) = r
Show: reflect (reflect (Node (l, v, r))) = Node (l, v, r)

  reflect (reflect (Node (l, v, r)))
=   { evaluation }
  reflect (Node (reflect r, v, reflect l))
=   { evaluation }
  Node (reflect (reflect l), v, reflect (reflect r))
=   { IH1 }
  Node (l, v, reflect (reflect r))
=   { IH2 }
  Node (l, v, r)

QED
```

对树的归纳实际上并不比对列表或
自然数。只需使用我们的程式化方法跟踪归纳假设即可
证明符号，一点也不难。

{{ video_embed | replace("%%VID%%", "aiJDQeWL2G0")}}

## 所有变体的归纳原则

我们现在已经了解了 `nat`、`list` 和 `tree` 的归纳原理。概括
从我们所看到的来看，变体的每个构造函数要么生成一个基本情况
用于归纳证明或归纳案例。并且，如果构造函数本身
携带该数据类型的值，每个值都会生成一个归纳
假设。例如：

- `Z`、`[]` 和 `Leaf` 所有生成的基本情况。

- `S`、`::` 和 `Node` 都是生成的归纳案例。

- `S` 和 `::` 各生成一个 IH，因为它们各自携带一个值
数据类型。

- `Node` 生成两个 IH，因为它携带该数据类型的两个值。

作为更复杂类型的归纳原理的示例，让我们
考虑一种表示数学表达式语法的类型。你
可能还记得之前的数据结构课程中，树可以用于
那个目的。

假设我们有下面的 `expr` 类型，它是一种树，来表示
具有整数、布尔值、一元运算符和二元运算符的表达式：

```{code-cell} ocaml
:tags: ["hide-output"]
type uop =
  | UMinus

type bop =
  | BPlus
  | BMinus
  | BLeq

type expr =
  | Int of int
  | Bool of bool
  | Unop of uop * expr
  | Binop of expr * bop * expr
```

例如，表达式 `5 < 6` 将表示为
`Binop (Int 5, BLeq, Int 6)`。我们会看到更多这样的例子
当我们研究解释器时，本书后面会提到这一点。

`expr` 的归纳原理是：

```text
forall properties P,
  if forall i, P(Int i)
  and forall b, P(Bool b)
  and forall u e, P(e) implies P(Unop (u, e))
  and forall b e1 e2, (P(e1) and P(e2)) implies P(Binop (e1, b, e2))
  then forall e, P(e)
```

有两种基本情况，对应于两个不携带的构造函数
`expr`。有两种归纳情况，对应两个构造函数
确实带有 `expr`s。 `Unop` 获得 1 个 IH，而 `Binop` 获得 2 个 IH，因为
每个携带的 `expr` 的数量。

## 归纳与递归

{{ video_embed | replace("%%VID%%", "J-x9hcNqRhY")}}

归纳证明和递归程序有着惊人的相似之处。从某种意义上说，
归纳证明*是*一个递归程序，展示如何构建证据
涉及代数数据类型 (ADT) 的定理。 ADT 的**结构**决定了证明和程序的结构：

- ADT 的 **构造函数** 是两个证明的组织原则
和程序。在证明中，我们为每个情况都有一个基础或归纳案例
  构造函数。在程序中，我们为每个实例都有一个模式匹配案例
  构造函数。

- ADT 中**递归类型**的使用决定了递归发生的位置
证明和程序。通过“递归类型”，我们的意思是发生
  输入它自己的定义，例如第二个 `'a list`
  `type 'a list = [] | ( :: ) 'a * 'a list`。此类事件的发生会导致“变小”
  出现在较大值内的类型的值。在证明中，我们应用
  达到如此小的值时的归纳假设。在一个程序中，我们
  对较小的值进行递归。
