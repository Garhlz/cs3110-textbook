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

map 函数为我们提供了一种单独变换 a 的每个元素的方法
列表。过滤函数为我们提供了一种单独决定是否
保留或丢弃列表中的每个元素。但这两者都只是
一次查看一个元素。如果我们想以某种方式结合所有怎么办
列表的元素？这就是 *fold* 函数的用途。事实证明
它有两个版本，我们将在本节中研究。但要
首先，我们看一个相关的函数&mdash;实际上不在标准中
库&mdash;我们称之为*组合*。

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

当我们使用`map` 和 `filter`进行类似的练习时，函数
具有很多共同的结构。这里的区别是：

* 空列表的情况返回不同的初始值，`0` 与 `""`

* 非空列表的情况使用不同的运算符来组合头
具有递归调用结果的元素，`+` 与 `^`。

那么我们可以再次应用抽象原则吗？当然！但这一次我们需要
分解出*两个*参数：一个用于这两个差异中的每一个。

首先，我们只考虑初始值：
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
现在 `sum'` 和 `concat'` 之间唯一真正的区别是运算符
用于将头部与尾部的递归调用结合起来。该运算符可以
也成为我们称为 `combine` 的统一函数的参数：
```{code-cell} ocaml
let rec combine op init = function
  | [] -> init
  | h :: t -> op h (combine op init t)

let sum = combine ( + ) 0
let concat = combine ( ^ ) ""
```

思考 `combine` 的一种方法是：

- 列表中的 `[]` 值被 `init` 替换，并且

- 每个 `::` 构造函数都被 `op` 替换。

例如，`[a; b; c]` 只是 `a :: (b :: (c :: []))` 的语法糖。所以
如果我们用 `0` 替换 `[]`，用 `(+)` 替换 `::`，我们得到 `a + (b + (c + 0))`。
这就是列表的总和。

抽象原则再次引导我们得出一个令人惊讶的简单和
简洁的计算表达式。

## Fold Right

{{ video_embed | replace("%%VID%%", "WKKkIGncRn8")}}

`combine` 函数是实际 OCaml 库函数的基本思想。
为了实现这一目标，我们需要对现有的实现进行一些更改
到目前为止。

首先，让我们重命名一些参数：我们将 `op` 更改为 `f` 以强调
实际上我们可以传入任何函数，而不仅仅是像这样的内置运算符
`+`。我们将把 `init` 更改为 `acc`，它通常代表“累加器”。
得出：

```{code-cell} ocaml
let rec combine f acc = function
  | [] -> acc
  | h :: t -> f h (combine f acc t)
```

其次，我们要做出一个诚然动机不那么好的改变。我们将交换
使用 `init` 参数将隐式列表参数传递给 `combine` ：

```{code-cell} ocaml
let rec combine' f lst acc = match lst with
  | [] -> acc
  | h :: t -> f h (combine' f t acc)

let sum lst = combine' ( + ) lst 0
let concat lst = combine' ( ^ ) lst ""
```

以这种方式编写函数有点不太方便，因为我们没有
不再利用 `function` 关键字，也不再利用部分
应用程序定义 `sum` 和 `concat`。但算法没有改变。

我们现在得到的是标准库函数的实际实现
`List.fold_right`。我们剩下要做的就是更改函数名称
并添加手动类型注释：

```{code-cell} ocaml
let rec fold_right f lst (acc : 'acc) = match lst with
  | [] -> acc
  | h :: t -> f h (fold_right f t acc)
```

为什么这个函数叫“向右折叠”？直觉是它的工作方式
是从右到左“折叠”列表的元素，将每个元素组合起来
使用运算符的新元素。例如，`fold_right ( + ) [a; b; c] 0`
结果是表达式 `a + (b + (c + 0))` 的计算结果。括号里
从最右边的子表达式到左边关联。

```{tip}
对于函数的正确实现而言，手动类型注释不是必需的。
其目的是提供更好的类型。
如果没有注释，`fold_right` 的推断类型将为 `('a -> 'b -> 'b) -> 'a list -> 'b -> 'b`，其中编译器选择 `'b` 作为累加器的类型。
通过使用自描述名称手动注释该参数，我们得到了更具可读性的类型 `('a -> 'acc -> 'acc) -> 'a list -> 'acc -> 'acc`。
```

## 尾递归和 Combine

`fold_right` 和 `combine` 都不是尾递归：在递归调用之后
返回，在应用函数参数 `f` 或
`op`。让我们回到 `combine` 并将其重写为尾递归。所有这些
需要的是更改 cons 分支：

```{code-cell} ocaml
let rec combine_tr f acc = function
  | [] -> acc
  | h :: t -> combine_tr f (f acc h) t  (* only real change *)
```

（细心的读者会注意到 `combine_tr` 的类型与
`combine` 的类型。我们很快就会解决这个问题。）

现在函数 `f` 应用于头元素 `h` 和累加器
`acc` *在*进行递归调用之前，从而确保没有工作
呼叫返回后仍有待完成的工作。  如果这看起来有点神秘的话
这是两个可能有帮助的函数的重写：

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

请密切注意这两个版本中新的累加器 `acc'` 是如何定义的：

- 在原始版本中，我们推迟处理头元素 `h`。首先，
我们将所有剩余的尾部元素组合起来得到 `acc'`。之后才使用
  `f` 把头元素折叠进去。因此，作为 `acc` 初始值传入的值
  结果对于 `combine` 的每次递归调用都是相同的：
  一直传递到需要的地方，即最右边的元素
  列表，然后在那里只使用一次。

- 但在尾递归版本中，我们立即把 `h` 和旧累加器 `acc`
折叠在一起。然后再把这个结果和所有尾部
  元素。因此，在每次递归调用时，作为参数传递的值
  `acc` 可以不同。

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

- 它们以相反的顺序组合列表元素，如其名称所示。
函数 `fold_right` 从右向左组合，而 `fold_left`
  从左向右进行。

- 函数 `fold_left` 是尾递归，而 `fold_right` 是
不。

- 函数的类型不同。在 `fold_X` 中，累加器参数转到列表参数的 `X` 中。这是标准库做出的选择，而不是必要的实现差异。

如果你发现很难跟踪参数顺序，
标准库中的 [`ListLabels` module][listlabels] 可以提供帮助。它使用
带标签的参数为组合运算符命名（称为 `f`）
和初始累加器值（称为 `init`）。在内部，
实现实际上与 `List` 模块相同。

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

## 关于标记参数和 Fold 的题外话

可以编写我们自己的 fold 函数版本，为
组合运算符的参数，所以我们甚至不必记住它们
顺序：

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

问题是内置的 `+` 运算符没有带标签的参数，
所以我们不能将它作为组合运算符传递给我们的标记函数。
我们必须定义我们自己的标记版本：

```
let add ~acc ~elt = acc + elt
let s = fold_left ~op:add ~init:0 [1; 2; 3]
```

但现在我们必须记住，`add` 的 `~acc` 参数将变成
`( + )` 的左侧参数。  这并不是真正的进步
相比最初需要记住的内容，这并没有真正带来改进。

## 使用 Fold 实现其他函数

fold 函数非常强大，我们可以用下面的方式根据
`fold_left` 或 `fold_right`。例如，

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

到这里，究竟应该用 fold 表达上面的计算，还是用我们已经见过的方式表达，
就开始变得有争议了。即使对经验丰富的函数式程序员来说，
理解 fold 的作用也可能比阅读简单的递归实现更耗时。
如果你仔细阅读
[source code of the standard library][list-src]，你会发现没有一个
`List` 模块内部没有一个函数是用 fold 实现的，这或许
说明了 fold 的可读性问题。另一方面，使用 fold 可以确保
程序员不会意外地编写递归遍历
写错。对于比列表更复杂的数据结构，
稳健性可能是一种胜利。

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
