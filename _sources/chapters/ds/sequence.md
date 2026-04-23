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

# 序列

*序列*是一个无限列表。例如，所有自然的无限列表
数字将是一个序列。所有素数列表或所有斐波那契列表也是如此
数字。我们如何有效地表示无限列表？显然我们不能
将整个列表存储在内存中。

我们已经知道 OCaml 允许我们创建递归函数&mdash;
也就是说，函数是根据其自身定义的。事实证明我们可以定义其他
也体现在自身的价值观上。

```{code-cell} ocaml
let rec ones = 1 :: ones
```

```{code-cell} ocaml
let rec a = 0 :: b and b = 1 :: a
```

上面的表达式创建*递归值*。列表 `ones` 包含一个
`1` 的无限序列，并且列表 `a` 和 `b` 在之间无限交替
`0` 和 `1`。由于列表是无限的，顶层无法在其列表中打印它们
整体。相反，它表示一个*循环*：列表循环回到它的位置
开始。尽管这些列表代表了无限的值序列，
它们在内存中的表示是有限的：它们是带有返回值的链表
创建这些循环的指针。

除了数字序列之外，还有其他类型的无限数学
我们可能想要用有限数据结构表示的对象：

* 从文件、网络套接字或用户读取的输入流。所有这些
长度是无限的，因此我们可以认为它们的长度是无限的
  长度。事实上，许多 I/O 库将到达 I/O 流的末尾视为
  意外情况并引发异常。

* *游戏树*是一棵树，其中游戏的位置（例如，国际象棋或
tic-tac-toe)_ 是节点，边是可能的移动。对于某些游戏
  这棵树实际上是无限的（想象一下，例如，棋盘上的棋子
  可能会永远互相追逐），而对于其他游戏来说，它是如此之深以至于
  我们永远不想显现整棵树，因此它实际上是
  无限。

## 如何不定义序列

假设我们想要表示第一个例子：所有的序列
自然数。我们可能尝试的一些显而易见的事情根本行不通：

```{code-cell} ocaml
(** [from n] is the infinite list [[n; n + 1; n + 2; ...]]. *)
let rec from n = n :: from (n + 1)
```

```ocaml
(** [nats] is the infinite list of natural numbers [[0; 1; ...]]. *)
let nats = from 0
```

```text
Stack overflow during evaluation (looping recursion?).
```

该尝试的问题在于 `nats` 尝试计算整个
自然数的无限序列。因为该函数不是尾递归，
它很快就会溢出堆栈。如果是尾递归，它会进入
无限循环。

这是另一种尝试，使用我们上面发现的有关递归值的内容：

```{code-cell} ocaml
:tags: ["raises-exception"]
let rec nats = 0 :: List.map (fun x -> x + 1) nats
```

由于更微妙的原因，这种尝试不起作用。在a的定义中
递归值，我们不允许在完成之前使用一个值
定义的。问题在于 `List.map` 应用于 `nats`，因此
模式匹配以提取 `nats` 的头部和尾部。但我们在中间
定义 `nats`，因此不允许使用 `nats`。

## 如何正确定义序列

我们可以尝试通过类比定义（有限）列表来定义序列。
回想一下这个定义：

```{code-cell} ocaml
type 'a mylist = Nil | Cons of 'a * 'a mylist
```

我们可以尝试将其转换为序列的定义：

```{code-cell} ocaml
type 'a sequence = Cons of 'a * 'a sequence
```

请注意，我们删除了 `Nil` 构造函数，因为空列表是有限的，
但我们只想要无限的列表。

该定义的问题在于它实际上并不比内置的更好
OCaml 中的列表，因为我们仍然无法定义 `nats`：

```{code-cell} ocaml
let rec from n = Cons (n, from (n + 1))
```

```ocaml
let nats = from 0
```

```text
Stack overflow during evaluation (looping recursion?).
```

和以前一样，该定义尝试开始计算整个无限
自然序列。

我们需要的是一种“暂停”评估的方法，以便在任何时间点，只有
已经计算出无限序列的有限近似。幸运的是，
我们已经知道该怎么做了！

考虑以下定义：
```{code-cell} ocaml
:tags: ["raises-exception"]
let f1 = failwith "oops"
```

```{code-cell} ocaml
let f2 = fun x -> failwith "oops"
```

```{code-cell} ocaml
:tags: ["raises-exception"]
f2 ();;
```

`f1` 的定义立即引发异常，而定义
`f2` 没有。为什么？因为 `f2` 将 `failwith` 包装在匿名内部
函数。回想一下，根据 OCaml 的动态语义，**函数
已经是值**。所以函数体内没有进行任何计算
直至应用。这就是 `f2 ()` 引发异常的原因。

我们可以利用求值的这个性质来实现延迟求值，
并在定义序列时从中受益：把序列的尾部包裹在函数中。
由于这个函数接收什么参数并不重要，我们不妨让它接收 unit。
这种只用于延迟计算、尤其是以 unit 作为输入的函数，称为 *thunk*。

```{code-cell} ocaml
(** An ['a sequence] is an infinite list of values of type ['a].
    AF: [Cons (x, f)] is the sequence whose head is [x] and tail is [f ()].
    RI: none. *)
type 'a sequence = Cons of 'a * (unit -> 'a sequence)
```

事实证明这个定义非常有效。  最后我们可以定义`nats`：

```{code-cell} ocaml
let rec from n = Cons (n, fun () -> from (n + 1))
let nats = from 0
```

我们不会遇到无限循环或堆栈溢出。 `nats` 的评估有
停了下来。仅计算了它的第一个元素 `0`。剩余的
元素在被请求之前不会被计算。为此，我们可以
定义函数来访问序列的一部分，类似于我们如何访问
列表的一部分：

```{code-cell} ocaml
(** [hd s] is the head of [s]. *)
let hd (Cons (h, _)) = h
```

```{code-cell} ocaml
(** [tl s] is the tail of [s]. *)
let tl (Cons (_, t)) = t ()
```

请注意，在 `tl` 的定义中，我们必须将函数 `t` 应用于 `()` 来
获取序列的尾部。也就是说，我们必须*强制* thunk 来评估
到那时，而不是继续延迟其计算。

为了方便起见，我们可以编写多次应用 `hd` 或 `tl` 的函数
获取或删除序列的某些有限前缀：
  
```{code-cell} ocaml
(** [take n s] is the list of the first [n] elements of [s]. *)
let rec take n s =
  if n = 0 then [] else hd s :: take (n - 1) (tl s)

(** [drop n s] is all but the first [n] elements of [s]. *)
let rec drop n s =
  if n = 0 then s else drop (n - 1) (tl s)
```

例如：

```{code-cell} ocaml
take 10 nats
```

## 使用序列编程

让我们编写一些操作序列的函数。拥有一个
用作文档一部分的序列符号。让我们使用
`<a; b; c; ...>` 表示在 处具有元素 `a`、`b` 和 `c` 的序列
它的头部，后面是无数其他元素。

以下是对序列求平方以及对两个序列求和的函数：

```{code-cell} ocaml
(** [square <a; b; c; ...>] is [<a * a; b * b; c * c; ...]. *)
let rec square (Cons (h, t)) =
  Cons (h * h, fun () -> square (t ()))

(** [sum <a1; a2; a3; ...> <b1; b2; b3; ...>] is
    [<a1 + b1; a2 + b2; a3 + b3; ...>]. *)
let rec sum (Cons (h1, t1)) (Cons (h2, t2)) =
  Cons (h1 + h2, fun () -> sum (t1 ()) (t2 ()))
```

请注意定义这两个函数的基本模板是如何相同的：

* 与输入序列进行模式匹配，该序列必须是 `Cons`
头函数和尾函数（thunk）。

* 构造一个序列作为输出，该序列必须是新头和一个
新的尾部函数（thunk）的 `Cons`。

* 在构造新的尾部函数时，将尾部的求值延迟
立即从 `fun () -> ...` 开始。

* 在该 thunk 的主体内，递归地应用正在定义的函数
（平方或总和）到强制 thunk （或多个 thunk）求值的结果。

当然，平方和求和只是映射函数的两种可能的方式
跨越一个或多个序列。这表明我们可以编写一个高阶映射
函数，很像列表：

```{code-cell} ocaml
(** [map f <a; b; c; ...>] is [<f a; f b; f c; ...>]. *)
let rec map f (Cons (h, t)) =
  Cons (f h, fun () -> map f (t ()))

(** [map2 f <a1; b1; c1;...> <a2; b2; c2; ...>] is
    [<f a1 b1; f a2 b2; f a3 b3; ...>]. *)
let rec map2 f (Cons (h1, t1)) (Cons (h2, t2)) =
  Cons (f h1 h2, fun () -> map2 f (t1 ()) (t2 ()))

let square' = map (fun n -> n * n)
let sum' = map2 ( + )
```

现在我们有了序列的映射函数，我们可以成功定义 `nats`
以我们最初尝试的一种聪明的方式：

```{code-cell} ocaml
let rec nats = Cons (0, fun () -> map (fun x -> x + 1) nats)
```

```{code-cell} ocaml
take 10 nats
```

为什么这有效？直观上，`nats` 是 `<0; 1; 2; 3; ...>`，因此映射
`nats` 上的增量函数是 `<1; 2; 3; 4; ...>`。如果我们将 `0` 复制到
从 `<1; 2; 3; 4; ...>` 开始，我们根据需要得到 `<0; 1; 2; 3; ...>` 。
允许递归值定义，因为我们从不尝试使用 `nats`
直到其定义完成之后。特别是，thunk 会延迟对 `nats`
定义右侧的求值。

这是另一个巧妙的定义。考虑斐波那契数列
`<1; 1; 2; 3; 5; 8; ...>`。如果我们取它的尾巴，我们会得到
`<1; 2; 3; 5; 8; 13; ...>`。如果我们将这两个序列相加，我们得到
`<2; 3; 5; 8; 13; 21; ...>`。那无非是尾巴的尾巴
斐波那契数列。因此，如果我们要在其前面加上 `[1; 1]` ，我们就会得到
实际的斐波那契数列。这就是这个定义背后的直觉：

```{code-cell} ocaml
let rec fibs =
  Cons (1, fun () ->
    Cons (1, fun () ->
      sum fibs (tl fibs)))
```

它有效！

```{code-cell} ocaml
take 10 fibs
```

不幸的是，它的效率非常低。每次我们强制计算
下一个元素，需要重新计算所有前面的元素，两次：一次
定义最后一行中的 `fibs` 和一次 `tl fibs` 。尝试一下
自己运行代码。当我们到达第 30 个数字时，
计算速度明显慢；到第 100 次时，它似乎会持续下去
永远。

我们可以做得更好吗？是的，在新语言特性的帮助下：
懒惰。我们接下来讨论一下。

## 惰性

斐波那契数列的示例表明，如果
thunk 的计算只发生一次：当它被强制时，结果
值可以被记住；如果再次强制求值 thunk，该值
可以立即返回而不是重新计算它。这就是背后的想法
OCaml `Lazy` 模块：

```ocaml
module Lazy :
  sig
    type 'a t = 'a lazy_t
    val force : 'a t -> 'a
    ...
  end
```

`'a Lazy.t` 类型的值是 `'a` 类型的值，其计算已通过
延迟了。直观地说，该语言在评估它时“懒惰”：它不会
直到有特别要求为止进行计算。需求的表达方式
通过*强制*使用 `Lazy.force` 进行评估，它采用 `'a Lazy.t` 和
导致其内部的 `'a` 最终被生成。第一次惰性值是
如果强制的话，计算可能需要很长时间。但结果是*缓存*又名
*memoized*，以及任何后续强制惰性值的时间，memoized
结果将立即返回，无需重新计算。

```{note}
“Memoized”确实是这个词的正确拼写。我们没有拼错
“记住”，尽管看起来可能是这样。
```

`Lazy` 模块不包含生成 `'a Lazy.t` 的函数。
相反，OCaml 语法中有一个内置关键字可以执行此操作：`lazy e`。

* **语法：** `lazy e`

* **静态语义：** 如果 `e : u`，则 `lazy e : u Lazy.t`。

* **动态语义：** `lazy e` 不会将 `e` 计算为值。相反，它
产生一个*暂停*，当稍后强制时，会将 `e` 评估为一个值
  `v` 并返回 `v`。此外，该暂停会记住 `v` 是其强制的
  值。如果再次强制暂停，它会立即返回 `v`
  而不是重新计算它。

```{note}
OCaml 通常的评估策略是 *eager* 又名 *strict*：它总是评估
函数应用之前的参数。如果你想延迟计算一个值，
你必须使用 `lazy` 关键字明确请求。其他函数
语言，尤其是 Haskell，默认情况下是惰性的。当懒惰可以令人愉快
使用无限数据结构进行编程。但懒惰的评估会让事情变得更加困难
推理空间和时间，并且与侧面有不愉快的相互作用
影响。
```

为了说明惰性值的使用，让我们尝试计算第 30 个斐波那契数
使用 `fibs` 定义的数字：

```{code-cell} ocaml
let rec fibs =
  Cons (1, fun () ->
    Cons (1, fun () ->
      sum fibs (tl fibs)))
```

```{tip}
如果你以交互方式运行接下来的几个示例，它们将会更有意义，
而不仅仅是阅读此页。
```

如果我们尝试获取第 30 个斐波那契数，则需要很长时间来计算：

```{code-cell} ocaml
let fib30long = take 30 fibs |> List.rev |> List.hd
```

但是如果我们用 `lazy` 包装对其的评估，它将立即返回，
因为对该数字的评估已暂停：

```{code-cell} ocaml
let fib30lazy = lazy (take 30 fibs |> List.rev |> List.hd)
```

稍后我们可以强制评估该惰性值，这将需要
计算时间很长，`fib30long` 也是如此：

```{code-cell} ocaml
let fib30 = Lazy.force fib30lazy
```

但是如果我们尝试重新计算相同的惰性值，它将返回
立即，因为结果已被记住：

```{code-cell} ocaml
let fib30fast = Lazy.force fib30lazy
```

尽管如此，我们仍然没有完全成功。该特定计算
第 30 个斐波那契数已被记住，但如果我们稍后定义其他数
另一个的计算在第一次计算时不会加速：

```{code-cell} ocaml
let fib29 = take 29 fibs |> List.rev |> List.hd
```

我们真正想要的是改变序列本身的表示
使用惰性值。

### 惰性序列

这是使用惰性值的无限列表的表示：

```{code-cell} ocaml
type 'a lazysequence = Cons of 'a * 'a lazysequence Lazy.t
```

我们已经摆脱了 thunk，而是使用惰性值作为尾部
惰性序列。如果我们想要计算尾部，我们会强制它。

为了便于比较，以下两个模块实现了斐波那契数列
序列与序列，然后与惰性序列。尝试计算第 30 个
斐波那契数列与两个模块，你会看到惰性序列
实现比标准序列实现快得多。

```{code-cell} ocaml
module SequenceFibs = struct
  type 'a sequence = Cons of 'a * (unit -> 'a sequence)

  let hd : 'a sequence -> 'a =
    fun (Cons (h, _)) -> h

  let tl : 'a sequence -> 'a sequence =
    fun (Cons (_, t)) -> t ()

  let rec take_aux n (Cons (h, t)) lst =
    if n = 0 then lst
    else take_aux (n - 1) (t ()) (h :: lst)

  let take : int -> 'a sequence -> 'a list =
    fun n s -> List.rev (take_aux n s [])

  let nth : int -> 'a sequence -> 'a =
    fun n s -> List.hd (take_aux (n + 1) s [])

  let rec sum : int sequence -> int sequence -> int sequence =
    fun (Cons (h_a, t_a)) (Cons (h_b, t_b)) ->
      Cons (h_a + h_b, fun () -> sum (t_a ()) (t_b ()))

  let rec fibs =
    Cons(1, fun () ->
      Cons(1, fun () ->
        sum (tl fibs) fibs))

  let nth_fib n =
    nth n fibs

end

module LazyFibs = struct

  type 'a lazysequence = Cons of 'a * 'a lazysequence Lazy.t

  let hd : 'a lazysequence -> 'a =
    fun (Cons (h, _)) -> h

  let tl : 'a lazysequence -> 'a lazysequence =
    fun (Cons (_, t)) -> Lazy.force t

  let rec take_aux n (Cons (h, t)) lst =
    if n = 0 then lst else
      take_aux (n - 1) (Lazy.force t) (h :: lst)

  let take : int -> 'a lazysequence -> 'a list =
    fun n s -> List.rev (take_aux n s [])

  let nth : int -> 'a lazysequence -> 'a =
    fun n s -> List.hd (take_aux (n + 1) s [])

  let rec sum : int lazysequence -> int lazysequence -> int lazysequence =
    fun (Cons (h_a, t_a)) (Cons (h_b, t_b)) ->
      Cons (h_a + h_b, lazy (sum (Lazy.force t_a) (Lazy.force t_b)))

  let rec fibs =
    Cons(1, lazy (
      Cons(1, lazy (
        sum (tl fibs) fibs))))

  let nth_fib n =
    nth n fibs
end
```
