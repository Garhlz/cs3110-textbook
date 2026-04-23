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

# 函数式数据结构

{{ video_embed | replace("%%VID%%", "CLeXXZDkkCI")}}

“函数式数据结构”是一种不利用可变性的数据结构。
可以用函数式语言构建函数式数据结构
以及命令式语言。例如，你可以构建
通过创建 `Node` 相当于 OCaml 的 `list` 类型的 Java
其字段通过使用而不可变的类
`final` 关键字。

函数式数据结构具有*持久*的属性：更新
数据结构及其操作之一不会更改现有版本
的数据结构，而是产生一个新版本。两者都存在并且两者
仍然可以访问。良好的语言实现将确保任何部分
未被操作更改的数据结构将被*共享*
旧版本和新版本之间。任何发生变化的部分都会
*复制*以便旧版本可以保留。与持久数据相反
结构是一种*短暂的*数据结构：更改具有破坏性，因此
任何时候都只有一个版本。持久数据和短暂数据
结构可以用函数式语言和命令式语言构建。

## 列表

OCaml 中内置的单链接 `list` 数据结构是有效的。我们知道
因为我们已经了解了如何使用代数数据类型来实现它。这是
也是持久的，我们可以证明：

```{code-cell} ocaml
let lst = [1; 2];;
let lst' = List.tl lst;;
lst;;
```

获取 `lst` 的尾部不会更改列表。 `lst` 和 `lst'`
共存而不互相影响。

## 堆栈

{{ video_embed | replace("%%VID%%", "LWmGzSCpvVY")}}

我们在本章前面实现了堆栈。这是其中之一的简洁变体
这些实现中，我们添加了 `to_list` 操作以使其更容易
查看示例中堆栈的内容：

```{code-cell} ocaml
:tags: ["hide-output"]
module type Stack = sig
  type 'a t
  exception Empty
  val empty : 'a t
  val is_empty : 'a t -> bool
  val push : 'a -> 'a t -> 'a t
  val peek : 'a t -> 'a
  val pop : 'a t -> 'a t
  val size : 'a t -> int
  val to_list : 'a t -> 'a list
end

module ListStack : Stack = struct
  type 'a t = 'a list
  exception Empty
  let empty = []
  let is_empty = function [] -> true | _ -> false
  let push = List.cons
  let peek = function [] -> raise Empty | x :: _ -> x
  let pop = function [] -> raise Empty | _ :: s -> s
  let size = List.length
  let to_list = Fun.id
end
```

正如上面所看到的，该实现是函数式的，并且也是持久的：

```{code-cell} ocaml
open ListStack;;
let s = empty |> push 1 |> push 2;;
let s' = pop s;;
to_list s;;
to_list s';;
```

创建 `s'` 的 `pop` 操作不会更改值 `s`。两者都
堆栈的版本共存。

`Stack` 模块类型给了我们一个强烈的暗示，即数据结构是
持久化它为 `push` 和 `pop` 提供的类型：

```ocaml
val push : 'a -> 'a t -> 'a t
val pop : 'a t -> 'a t
```

两者都以堆栈作为参数并返回一个新堆栈作为结果。安
临时数据结构通常不会费心返回堆栈。在Java，
例如，类似的方法可能具有 `void` 返回类型；相当于
OCaml 将返回 `unit`。

## Option 与异常

{{ video_embed | replace("%%VID%%", "tbMU_pv0p9o")}}

到目前为止，我们所有的堆栈实现都会在 `peek` 时引发异常
或 `pop` 应用于空堆栈。另一种可能性是使用
`option` 作为返回值。如果输入堆栈为空，则 `peek` 和
`pop`返回`None`；否则，它们返回 `Some`。

```{code-cell} ocaml
:tags: ["hide-output"]
module type Stack = sig
  type 'a t
  val empty : 'a t
  val is_empty : 'a t -> bool
  val push : 'a -> 'a t -> 'a t
  val peek : 'a t -> 'a option
  val pop : 'a t -> 'a t option
  val size : 'a t -> int
  val to_list : 'a t -> 'a list
end

module ListStack : Stack = struct
  type 'a t = 'a list
  exception Empty
  let empty = []
  let is_empty = function [] -> true | _ -> false
  let push = List.cons
  let peek = function [] -> None | x :: _ -> Some x
  let pop = function [] -> None | _ :: s -> Some s
  let size = List.length
  let to_list = Fun.id
end
```

但这使得管道化变得更加困难：

```{code-cell} ocaml
:tags: ["raises-exception"]
ListStack.(empty |> push 1 |> pop |> peek)
```

管道的类型在 `pop` 之后立即分解，因为
现在返回 `'a t option`，但 `peek` 期望的输入仅仅是
`'a t`。

可以定义一些额外的运算符来帮助恢复能力
到管道。事实上，这些函数已经在`Option`模块中定义了
在标准库中，尽管不是作为中缀运算符：

```{code-cell} ocaml
(* Option.map aka fmap *)
let ( >>| ) opt f =
  match opt with
  | None -> None
  | Some x -> Some (f x)

(* Option.bind *)
let ( >>= ) opt f =
  match opt with
  | None -> None
  | Some x -> f x
```

我们可以根据需要使用它们来进行管道传输：

```{code-cell} ocaml
ListStack.(empty |> push 1 |> pop >>| push 2 >>= pop >>| push 3 >>| to_list)
```

但每一步都要想清楚该使用三个运算符中的哪一个，并不太愉快。

因此，接口设计上存在一种权衡：

* 使用 option 可以确保运行时永远不会因为空堆栈而出现意外异常。
  因此程序更加稳健。但方便的管道写法也随之丢失了。

* 使用异常意味着程序员不必编写那么多代码。如果
他们确信不会发生异常，他们可以省略代码
  处理它。该程序不太健壮，但编写起来更方便。

因此，我们需要在“更早写更多代码（使用 option）”和
“稍后做更多调试（使用异常）”之间取舍。OCaml 标准库最近
开始在数据结构中提供两个版本的接口，以便
客户端可以选择他们想要的使用方式。例如，我们可以
为 `peek` 和 `peek_opt` 提供 `peek` 和 `peek_opt`，对于 `pop` 也是如此，对于
我们的堆栈模块：

```{code-cell} ocaml
:tags: ["hide-output"]
module type Stack = sig
  type 'a t
  exception Empty
  val empty : 'a t
  val is_empty : 'a t -> bool
  val push : 'a -> 'a t -> 'a t
  val peek : 'a t -> 'a
  val peek_opt : 'a t -> 'a option
  val pop : 'a t -> 'a t
  val pop_opt : 'a t -> 'a t option
  val size : 'a t -> int
  val to_list : 'a t -> 'a list
end

module ListStack : Stack = struct
  type 'a t = 'a list
  exception Empty
  let empty = []
  let is_empty = function [] -> true | _ -> false
  let push = List.cons
  let peek = function [] -> raise Empty | x :: _ -> x
  let peek_opt = function [] -> None | x :: _ -> Some x
  let pop = function [] -> raise Empty | _ :: s -> s
  let pop_opt = function [] -> None | _ :: s -> Some s
  let size = List.length
  let to_list = Fun.id
end
```

此实现的一个好处是它非常高效。所有的
除 `size` 之外的操作都是常数时间。我们在本章前面看到
`size` 也可以设置为恒定时间，但需要一些额外的空间
&mdash; 虽然只是一个常数因子，但更多的是 &mdash; 通过缓存的大小
堆栈在列表中的每个节点。

## 队列

{{ video_embed | replace("%%VID%%", "rCiBfZO67A4")}}

队列和堆栈是非常相似的接口。这里我们暂时继续使用异常，
而不是 option。

```{code-cell} ocaml
:tags: ["hide-output"]
module type Queue = sig
  (** An ['a t] is a queue whose elements have type ['a]. *)
  type 'a t

  (** Raised if [front] or [dequeue] is applied to the empty queue. *)
  exception Empty

  (** [empty] is the empty queue. *)
  val empty : 'a t

  (** [is_empty q] is whether [q] is empty. *)
  val is_empty : 'a t -> bool

  (** [enqueue x q] is the queue [q] with [x] added to the end. *)
  val enqueue : 'a -> 'a t -> 'a t

  (** [front q] is the element at the front of the queue. Raises [Empty]
      if [q] is empty. *)
  val front : 'a t -> 'a

  (** [dequeue q] is the queue containing all the elements of [q] except the
      front of [q]. Raises [Empty] if [q] is empty. *)
  val dequeue : 'a t -> 'a t

  (** [size q] is the number of elements in [q]. *)
  val size : 'a t -> int

  (** [to_list q] is a list containing the elements of [q] in order from
      front to back. *)
  val to_list : 'a t -> 'a list
end
```

```{important}
与 `peek` 和 `pop` 类似，请注意 `front` 和 `dequeue` 如何划分
获取第一个元素与获取所有其余元素的责任
元素。
```

用列表实现队列很容易，就像实现
堆栈：

```{code-cell} ocaml
module ListQueue : Queue = struct
  (** The list [x1; x2; ...; xn] represents the queue with [x1] at its front,
      followed by [x2], ..., followed by [xn]. *)
  type 'a t = 'a list
  exception Empty
  let empty = []
  let is_empty = function [] -> true | _ -> false
  let enqueue x q = q @ [x]
  let front = function [] -> raise Empty | x :: _ -> x
  let dequeue = function [] -> raise Empty | _ :: q -> q
  let size = List.length
  let to_list = Fun.id
end
```

但是，尽管很简单，但这种实现并不像我们的那样有效
基于列表的堆栈。出队是一个恒定时间的操作
表示，但排队是线性时间操作。那是因为
`dequeue` 执行单个模式匹配，而 `enqueue` 必须遍历
整个列表在末尾附加新元素。

有一个非常聪明的方法可以提高效率。我们可以使用两个列表
代表单个队列。这种表示法是由罗伯特·梅尔维尔发明的
他在康奈尔大学的博士论文的一部分（*迭代的渐近复杂性
计算*，1981 年 1 月），由 David Gries 教授提供建议。克里斯·冈崎
（*纯函数式数据结构*，剑桥大学出版社，1988 年）调用
这些*批量队列*。有时你会看到引用了相同的实现
相当于“用两个堆栈实现队列”。那是因为堆栈和列表
非常相似（正如我们已经看到的），你可以将 `pop` 重写为
`List.tl` 等等。

核心思想有A部分和B部分。A部分是：我们使用两个列表来
将队列分成两部分，*收件箱*和*发件箱*。当新元素出现时
排队后，我们将它们放入收件箱。最终（我们很快就会知道如何）元素
从收件箱转移到发件箱。当请求出列时，
元素从发件箱中删除；或者当请求前面的元素时，我们
检查发件箱。例如，如果收件箱当前有 `[3; 4; 5]` 并且
发件箱有 `[1; 2]`，那么前面的元素将是 `1`，即头部
发件箱。出列将删除该元素并留下发件箱
只是`[2]`。同样，入队 `6` 将使收件箱变成 `[3; 4; 5; 6]`。

到目前为止，`front` 和 `dequeue` 的效率非常好。我们只需要
分别取发件箱的头部或尾部，假设它非空。
这些是恒定时间操作。但`enqueue`的效率仍然是
不好。这是线性时间，因为我们必须将新元素附加到末尾
名单。可惜我们必须使用追加运算符，这本质上是
线性时间。如果我们能使用 cons 就更好了，cons 是常数
时间。

所以这是核心思想的 B 部分：让我们以相反的顺序保留收件箱。  对于
例如，如果我们将 `3` 入队，然后 `4` 然后 `5` 入队，收件箱实际上会
是 `[5; 4; 3]`，而不是 `[3; 4; 5]`。  然后如果 `6` 接下来入队，我们可以
将其放在收件箱的开头，即变为 `[6; 5; 4; 3]`。
因此，由收件箱 `i` 和发件箱 `o` 表示的队列是 `o @ List.rev i`。
因此 `enqueue` 现在可以始终是恒定时间操作。

但是 `dequeue` （和 `front`）呢？它们也是恒定的时间，**只要
发件箱不为空。** 如果它是空的，我们就有问题了。我们需要转移
此时收件箱中的任何内容都会发送到发件箱中。  例如，如果
发件箱为空，收件箱为`[6; 5; 4; 3]`，那么我们需要切换它们
周围，使发件箱为 `[3; 4; 5; 6]` 并且收件箱为空。  那是
其实很简单：我们只需颠倒列表即可。

不幸的是，我们刚刚重新引入了线性时间操作。但与一个
关键区别：我们不必对每个都进行线性时间反转
`dequeue`，而对于上面的 `ListQueue`，我们必须执行线性时间追加
每`enqueue`。相反，我们只需要在极少数情况下做相反的事情
当发件箱变空时。

因此，即使在最坏的情况下 `dequeue` （和 `front`）将是线性时间，
大多数时候他们不会。事实上，在本书后面我们学习的时候
*摊销分析*我们将证明，从长远来看，它们可以被理解为
恒定时间操作。现在，有一个直觉可以支持这一点
声明：每个单独的元素进入收件箱一次（使用 cons），然后移动到
发件箱一次（使用模式匹配然后 cons），并离开发件箱一次（使用
模式匹配）。其中每一个都是恒定时间。所以每个元素只有
从自己的角度体验恒定时间的操作。

现在，让我们继续实现这些想法。在实现过程中，我们将
添加一个想法：发件箱中始终必须有一个元素，除非
队列为空。换句话说，如果发件箱是空的，我们保证
收件箱也是。对于批处理队列来说，这个要求不是必需的，但确实如此
通过减少我们必须检查是否存在的次数来使代码更简单
列表为空。微小的权衡是，如果队列为空，现在 `enqueue`
必须直接将元素放入发件箱。不管怎样，这仍然是一个
恒定时间运行。

```{code-cell} ocaml
module BatchedQueue : Queue = struct
  (** [{o; i}] represents the queue [o @ List.rev i]. For example,
      [{o = [1; 2]; i = [5; 4; 3]}] represents the queue [1, 2, 3, 4, 5],
      where [1] is the front element. To avoid ambiguity about emptiness,
      whenever only one of the lists is empty, it must be [i]. For example,
      [{o = [1]; i = []}] is a legal representation, but [{o = []; i = [1]}]
      is not. This implies that if [o] is empty, [i] must also be empty. *)
  type 'a t = {o : 'a list; i : 'a list}

  exception Empty

  let empty = {o = []; i = []}

  let is_empty = function
    | {o = []} -> true
    | _ -> false

  let enqueue x = function
    | {o = []} -> {o = [x]; i = []}
    | {o; i} -> {o; i = x :: i}

  let front = function
    | {o = []} -> raise Empty
    | {o = h :: _} -> h

  let dequeue = function
    | {o = []} -> raise Empty
    | {o = [_]; i} -> {o = List.rev i; i = []}
    | {o = _ :: t; i} -> {o = t; i}

  let size {o; i} = List.(length o + length i)

  let to_list {o; i} = o @ List.rev i
end
```

批处理队列的效率是以可读性为代价的。如果我们比较
`ListQueue` 和 `BatchedQueue`，希望清楚 `ListQueue` 是一个
队列数据结构的简单且正确的实现。大概很远
不太清楚 `BatchedQueue` 是正确的实现。看看如何
上面写了很多段文字来解释它！

## 映射

回想一下，*map*（又名*dictionary*）将键绑定到值。这是一个模块
类型的映射。映射可能支持许多其他操作，但是
现在这些就足够了。

```{code-cell} ocaml
module type Map = sig
  (** [('k, 'v) t] is the type of maps that bind keys of type ['k] to
      values of type ['v]. *)
  type ('k, 'v) t

  (** [empty] does not bind any keys. *)
  val empty  : ('k, 'v) t

  (** [insert k v m] is the map that binds [k] to [v], and also contains
      all the bindings of [m].  If [k] was already bound in [m], that old
      binding is superseded by the binding to [v] in the returned map. *)
  val insert : 'k -> 'v -> ('k, 'v) t -> ('k, 'v) t

  (** [lookup k m] is the value bound to [k] in [m]. Raises: [Not_found] if [k]
      is not bound in [m]. *)
  val lookup : 'k -> ('k, 'v) t -> 'v

  (** [bindings m] is an association list containing the same bindings as [m].
      The keys in the list are guaranteed to be unique. *)
  val bindings : ('k, 'v) t -> ('k * 'v) list
end
```

请注意 `Map.t` 如何在两种类型 `'k` 和 `'v` 上进行参数化，这两种类型被编写为
放在括号中并用逗号分隔。虽然 `('k, 'v)` 可能看起来像
值对，它不是：它是编写多个类型变量的语法。

回想一下，关联列表是成对的列表，其中第一个元素
每对都是一个键，第二个元素是它绑定的值。例如，
这是一个关联列表，将一些众所周知的名称映射到近似值
它们的数值：

```
[("pi", 3.14); ("e", 2.718); ("phi", 1.618)]
```

当然，我们可以使用关联列表来实现 `Map` 模块类型：

```{code-cell} ocaml
module AssocListMap : Map = struct
  (** The list [(k1, v1); ...; (kn, vn)] binds key [ki] to value [vi].
      If a key appears more than once in the list, it is bound to the
      the left-most occurrence in the list. *)
  type ('k, 'v) t = ('k * 'v) list
  let empty = []
  let insert k v m = (k, v) :: m
  let lookup k m = List.assoc k m
  let keys m = List.(m |> map fst |> sort_uniq Stdlib.compare)
  let bindings m = m |> keys |> List.map (fun k -> (k, lookup k m))
end
```

映射的这种实现是持久的。例如，添加一个新的
绑定到下面的映射 `m` 不会改变 `m` 本身：

```{code-cell} ocaml
open AssocListMap
let m = empty |> insert "pi" 3.14 |> insert "e" 2.718
let m' = m |> insert "phi" 1.618
let b = bindings m
let b' = bindings m'
```

`insert` 操作是恒定时间，这很棒。但是 `lookup`
操作是线性时间。可以做得比这更好。在后来的一个
本章，我们将看看如何做得更好。可实现对数时间性能
具有平衡二叉树，以及诸如恒定时间性能之类的东西
哈希表。然而，这些都没有实现代码的简单性
上面。

`bindings` 操作因列表中潜在的重复键而变得复杂。
它使用 `keys` 辅助函数来提取唯一的键列表
库函数`List.sort_uniq`的帮助。该函数对输入列表进行排序并
在此过程中丢弃重复项。它需要一个比较函数作为输入。

```{note}
如果比较函数的参数比较相等，则比较函数必须返回 0
如果第一个更大，则为正整数；如果第一个更大，则为负整数
较小。
```

这里我们使用标准库的比较函数`Stdlib.compare`，它
其行为与内置比较运算符 `=`、`<`、`>` 基本相同，
等等。如果你想有一个轻松的想法，自定义比较函数很有用
重复意味着什么。例如，也许你想忽略
字符串的大小写，或数字的符号等。

`List.sort_uniq` 的运行时间是线性的，它产生一个线性的
作为输出的键数。  对于每个键，我们都会进行线性时间查找
操作。  所以 `bindings` 的总运行时间是 $O(n \log n) + O(n) \cdot
O(n)$, which is $O(n^2)$。  我们绝对可以做得更好
更高级的数据结构。

实际上，即使有关联，我们也可以进行恒定时间的 `bindings` 操作
列出，如果我们愿意为线性时间 `insert` 操作付费：

```{code-cell} ocaml
module UniqAssocListMap : Map = struct
  (** The list [(k1, v1); ...; (kn, vn)] binds key [ki] to value [vi].
      No duplicate keys may occur. *)
  type ('k, 'v) t = ('k * 'v) list
  let empty = []
  let insert k v m = (k, v) :: List.remove_assoc k m
  let lookup k m = List.assoc k m
  let bindings m = m
end
```

该实现在插入之前删除 `k` 的任何重复绑定
一个新的绑定。

## 集合

这是集合的模块类型。一组数据还有很多其他操作
结构可能会提供支持，但目前这些就足够了。

```{code-cell} ocaml
module type Set = sig
  (** ['a t] is the type of sets whose elements are of type ['a]. *)
  type 'a t

  (** [empty] is the empty set. *)
  val empty : 'a t

  (** [mem x s] is whether [x] is an element of [s]. *)
  val mem : 'a -> 'a t -> bool

  (** [add x s] is the set that contains [x] and all the elements of [s]. *)
  val add : 'a -> 'a t -> 'a t

  (** [elements s] is a list containing the elements of [s].  No guarantee
      is made about the ordering of that list, but each element is guaranteed
      to be unique. *)
  val elements : 'a t -> 'a list
end
```

下面是该接口的实现，使用列表来表示集合。
此实现确保列表永远不包含任何重复元素，
因为集合本身不：

```{code-cell} ocaml
module UniqListSet : Set = struct
  type 'a t = 'a list
  let empty = []
  let mem = List.mem
  let add x s = if mem x s then s else x :: s
  let elements = Fun.id
end
```

请注意 `add` 如何确保表示形式不包含任何重复项，因此
`elements` 的实现很容易。当然，这伴随着
`add` 是线性时间的权衡。

这是第二个实现，它允许列表中存在重复项：
```{code-cell} ocaml
module ListSet : Set = struct
  type 'a t = 'a list
  let empty = []
  let mem = List.mem
  let add = List.cons
  let elements s = List.sort_uniq Stdlib.compare s
end
```

在该实现中， `add` 操作现在是恒定时间，并且
`elements` 操作是线性时间。
