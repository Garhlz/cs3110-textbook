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

# Fold

map 函数让我们可以单独变换列表中的每个元素。filter 函数让我们可以单独决定保留还是丢弃列表中的每个元素。但两者都只是一次查看一个元素。如果我们想以某种方式把列表的所有元素组合在一起，该怎么做？这就是 *fold* 函数的用途。实际上它有两个版本，我们将在本节中研究。不过首先，我们来看一个相关的函数——它实际上不在标准库中——我们称之为*组合*（combine）。

## Combine

{{ video_embed | replace("%%VID%%", "uYJVwW2BFPg")}}

我们再次编写两个函数：

```{code-cell} ocaml
(** [sum lst] is the sum of all the elements of [lst]. *)
let rec sum = function
  | [] -> 0
  | h :: t -> h + sum t

let s = sum [1; 2; 3]
```

```{code-cell} ocaml
(** [concat lst] is the concatenation of all the elements of [lst]. *)
let rec concat = function
  | [] -> ""
  | h :: t -> h ^ concat t

let c = concat ["a"; "b"; "c"]
```

和之前 `map` 和 `filter` 的练习一样，这两个函数有很多共同的结构。区别在于：

* 空列表时返回不同的初始值：`0` vs. `""`

* 非空列表时使用不同的运算符来组合头部元素与递归调用的结果：`+` vs. `^`。

那么我们能再次应用抽象原则吗？当然！但这一次我们需要提取出*两个*参数：分别对应这两个差异。

首先，只考虑初始值：
```{code-cell} ocaml
let rec sum' init = function
  | [] -> init
  | h :: t -> h + sum' init t

let sum = sum' 0

let rec concat' init = function
  | [] -> init
  | h :: t -> h ^ concat' init t

let concat = concat' ""
```
现在 `sum'` 和 `concat'` 之间唯一真正的区别就是那个用于将头部与递归调用结果组合起来的运算符。这个运算符也可以提取为参数，得到我们称为 `combine` 的统一函数：
```{code-cell} ocaml
let rec combine op init = function
  | [] -> init
  | h :: t -> op h (combine op init t)

let sum = combine ( + ) 0
let concat = combine ( ^ ) ""
```

一种思考 `combine` 的方式是：

- 列表中的 `[]` 值被替换为 `init`，并且

- 每个 `::` 构造函数被替换为 `op`。

例如，`[a; b; c]` 只是 `a :: (b :: (c :: []))` 的语法糖。所以如果我们用 `0` 替换 `[]`，用 `(+)` 替换 `::`，就得到 `a + (b + (c + 0))`。这正是列表的总和。

抽象原则再次引导我们得到了一个令人惊讶的简洁而优雅的计算表达式。

## Fold Right

{{ video_embed | replace("%%VID%%", "WKKkIGncRn8")}}

`combine` 函数是实际 OCaml 库函数的基本思想。为了与库一致，我们需要对我们目前的实现做一些调整。

首先，重命名一些参数：将 `op` 改为 `f` 以强调我们实际上可以传入任何函数，而不仅仅是 `+` 这样的内置运算符。将 `init` 改为 `acc`，这个命名通常代表"累加器"（accumulator）。得到：

```{code-cell} ocaml
let rec combine f acc = function
  | [] -> acc
  | h :: t -> f h (combine f acc t)
```

其次，我们要做一个动机不那么充分的调整：把隐式的列表参数与 `init` 参数交换位置：

```{code-cell} ocaml
let rec combine' f lst acc = match lst with
  | [] -> acc
  | h :: t -> f h (combine' f t acc)

let sum lst = combine' ( + ) lst 0
let concat lst = combine' ( ^ ) lst ""
```

以这种方式编写函数稍显不便，因为我们不再能利用 `function` 关键字，也不再用部分应用来定义 `sum` 和 `concat`。但算法本身没有改变。

我们现在得到的就是标准库函数 `List.fold_right` 的实际实现。剩下的就是改一下函数名，并添加手动的类型标注：

```{code-cell} ocaml
let rec fold_right f lst (acc : 'acc) = match lst with
  | [] -> acc
  | h :: t -> f h (fold_right f t acc)
```

为什么这个函数叫"向右折叠"？直觉是它的工作方式
是从右到左"折叠"列表的元素，将每个元素组合起来
使用运算符的新元素。例如，`fold_right ( + ) [a; b; c] 0`
结果是表达式 `a + (b + (c + 0))` 的计算结果。括号里
从最右边的子表达式到左边关联。

```{tip}
对于函数的正确实现而言，手动类型注释不是必需的。
其目的是提供更好的类型。
如果没有注释，`fold_right` 的推断类型将为 `('a -> 'b -> 'b) -> 'a list -> 'b -> 'b`，其中编译器选择 `'b` 作为累加器的类型。
通过使用自描述名称手动注释该参数，我们得到了更具可读性的类型 `('a -> 'acc -> 'acc) -> 'a list -> 'acc -> 'acc`。
```

## 尾递归与 Combine

`fold_right` 和 `combine` 都不是尾递归：递归调用返回之后，还有应用函数参数 `f` 或 `op` 的工作要做。让我们回到 `combine`，将其改写为尾递归。只需要修改 cons 分支：

```{code-cell} ocaml
let rec combine_tr f acc = function
  | [] -> acc
  | h :: t -> combine_tr f (f acc h) t  (* 唯一实质性的改动 *)
```

（细心的读者会注意到 `combine_tr` 的类型与 `combine` 不同。我们很快就会解决这个问题。）

现在函数 `f` 在递归调用*之前*被应用到头部元素 `h` 和累加器 `acc`，从而确保调用返回后没有任何剩余工作。如果这看起来有点神秘，下面是两个函数的对比重写，可能有助于理解：

```{code-cell} ocaml
let rec combine f acc = function
  | [] -> acc
  | h :: t ->
    let acc' = combine f acc t in
    f h acc'

let rec combine_tr f acc = function
  | [] -> acc
  | h :: t ->
    let acc' = f acc h in
    combine_tr f acc' t
```

请密切注意这两个版本中新累加器 `acc'` 的定义方式：

- 在原始版本中，我们推迟对头部元素 `h` 的处理。首先将所有剩余尾部元素组合起来得到 `acc'`，之后再用 `f` 将头部元素折叠进去。因此，作为 `acc` 初始值传入的值在 `combine` 的每次递归调用中都是相同的：它被一路传递到需要的地方——列表的最右端，然后仅在那里被使用一次。

- 但在尾递归版本中，我们立即将 `h` 与旧累加器 `acc` 折叠在一起，然后再用这个结果去处理所有尾部元素。因此，每次递归调用时，作为 `acc` 传递的值可能不同。

组合的尾递归版本对于求和来说效果很好（并且
连接，我们省略）：

```{code-cell} ocaml
let sum = combine_tr ( + ) 0
let s = sum [1; 2; 3]
```

但减法可能会发生一些令人惊讶的事情：

```{code-cell} ocaml
let sub = combine ( - ) 0
let s = sub [3; 2; 1]

let sub_tr = combine_tr ( - ) 0
let s' = sub_tr [3; 2; 1]
```

两者的结果是不一样的！

- 使用 `combine` 我们计算 `3 - (2 - (1 - 0))`。首先我们折叠 `1`，然后折叠 `2`，
然后`3`。我们从右到左处理列表，将初始的
  累加器在最右边。

- 但是使用 `combine_tr` 我们计算 `(((0 - 3) - 2) - 1)`。我们正在处理
从左到右处理列表，并把初始累加器放在最左边。

通过加法，我们处理列表的顺序并不重要，因为
加法是结合律和交换律。但减法则不然，所以两者
方向导致不同的答案。

实际上，如果我们回想一下我们创建 `map` 的时候，这应该不会太令人惊讶。
是尾递归的。然后，我们发现尾递归可以使我们
从非尾递归版本开始以相反的顺序处理列表
相同的函数。这就是这里发生的事情。

## Fold Left

我们的 `combine_tr` 函数也在标准库中，名称为
`List.fold_left`：

```{code-cell} ocaml
let rec fold_left f (acc : 'acc) = function
  | [] -> acc
  | h :: t -> fold_left f (f acc h) t

let sum = fold_left ( + ) 0
let concat = fold_left ( ^ ) ""
```

我们再次成功地应用了抽象原则。

## Fold Left 与 Fold Right

我们来回顾一下 `fold_right` 和 `fold_left` 之间的区别：

- 它们以相反的顺序组合列表元素，从名字就能看出来：`fold_right` 从右向左组合，而 `fold_left` 从左向右进行。

- `fold_left` 是尾递归的，而 `fold_right` 不是。

- 两个函数的类型不同。在 `fold_X` 中，累加器参数位于列表参数的 `X` 一侧。这是标准库的设计选择，并非实现上的必然要求。

如果你发现参数顺序难以记忆，标准库中的 [`ListLabels` 模块][listlabels] 可以提供帮助。它用带标签的参数来命名组合运算符（名为 `f`）和初始累加器值（名为 `init`）。内部实现实际上与 `List` 模块相同。

```{code-cell} ocaml
ListLabels.fold_left ~f:(fun x y -> x - y) ~init:0 [1; 2; 3];;
```

```{code-cell} ocaml
ListLabels.fold_right ~f:(fun y x -> x - y) ~init:0 [1; 2; 3];;
```

请注意，在上面的两个 Fold 应用中，由于有标签，
我们可以用统一的顺序编写参数。然而，我们仍然必须注意：
组合运算符的哪个参数是列表元素，哪个参数是累加器值。

[listlabels]: https://ocaml.org/api/ListLabels.html

## 关于标签参数与 Fold 的题外话

我们也可以自己编写 fold 函数版本，为组合运算符的参数加上标签，这样甚至不用记住它们的顺序：

```{code-cell} ocaml
let rec fold_left ~op:(f: acc:'a -> elt:'b -> 'a) ~init:acc lst =
  match lst with
  | [] -> acc
  | h :: t -> fold_left ~op:f ~init:(f ~acc:acc ~elt:h) t

let rec fold_right ~op:(f: elt:'a -> acc:'b -> 'b) lst ~init:acc =
  match lst with
  | [] -> acc
  | h :: t -> f ~elt:h ~acc:(fold_right ~op:f t ~init:acc)
```

但这些函数并不像看起来那么有用：

```{code-cell} ocaml
:tags: ["raises-exception"]
let s = fold_left ~op:( + ) ~init:0 [1;2;3]
```

问题在于内置的 `+` 运算符没有带标签的参数，因此不能直接作为组合运算符传给我们的带标签函数。我们必须自己定义一个带标签的版本：

```
let add ~acc ~elt = acc + elt
let s = fold_left ~op:add ~init:0 [1; 2; 3]
```

但现在我们又必须记住，`add` 的 `~acc` 参数将成为 `( + )` 的左侧参数。相比原先需要记住的东西，这并没有真正的改进。

## 用 Fold 实现其他函数

fold 函数非常强大，我们可以用 `fold_left` 或 `fold_right` 来实现许多其他函数。例如：

```{code-cell} ocaml
let length lst =
  List.fold_left (fun acc _ -> acc + 1) 0 lst

let rev lst =
  List.fold_left (fun acc x -> x :: acc) [] lst

let map f lst =
  List.fold_right (fun x acc -> f x :: acc) lst []

let filter f lst =
  List.fold_right (fun x acc -> if f x then x :: acc else acc) lst []
```

到这里，究竟应该用 fold 表达上述计算还是用我们已经见过的方式表达，就开始有争议了。即使对经验丰富的函数式程序员来说，理解 fold 的作用可能也比阅读简单的递归实现更耗时。如果你去阅读[标准库的源码][list-src]，会发现 `List` 模块内部没有一个函数是用 fold 实现的，这或许说明了 fold 的可读性问题。另一方面，使用 fold 可以确保程序员不会在递归遍历的实现中意外犯错。对于比列表更复杂的数据结构，这种稳健性可能是一种优势。

[list-src]: https://github.com/ocaml/ocaml/blob/trunk/stdlib/list.ml

## Fold、递归与库

我们现在已经看到了编写操作列表的函数的三种不同方法：

- 直接使用模式匹配的递归函数，分别匹配空列表和 cons，
- 使用 `fold` 函数，以及
- 使用其他库函数。

让我们尝试使用每种方法来解决问题，以便我们能够理解
它们。

考虑编写一个函数 `lst_and: bool list -> bool`，这样
`lst_and [a1; ...; an]` 返回列表的所有元素是否都是 `true`。
也就是说，它的计算结果与 `a1 && a2 && ... && an` 相同。当应用于
空列表，其计算结果为 `true`。

以下是编写此类函数的三种可能的方法。我们给每一种方式一个
为了清楚起见，函数名称略有不同。

```{code-cell} ocaml
let rec lst_and_rec = function
  | [] -> true
  | h :: t -> h && lst_and_rec t

let lst_and_fold =
	List.fold_left (fun acc elt -> acc && elt) true

let lst_and_lib =
	List.for_all (fun x -> x)
```

所有三个函数的最坏情况运行时间与长度成线性关系
列表。但：

- 第一个函数 `lst_and_rec` 的优点是不需要处理
整个列表。第一次使用时，它将立即返回 `false`
  在列表中发现 `false` 元素。

- 第二个函数 `lst_and_fold` 将始终处理
列表。

- 至于第三个函数`lst_and_lib`，根据文档
`List.for_all`，它返回`(p a1) && (p a2) && ... && (p an)`。所以喜欢
  `lst_and_rec` 它不需要处理每个元素。
