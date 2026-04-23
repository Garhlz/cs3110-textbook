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

# 代数数据类型

迄今为止，我们把变体简单地看作是枚举一组常量值，比如：

```ocaml
type day = Sun | Mon | Tue | Wed | Thu | Fri | Sat

type ptype = TNormal | TFire | TWater

type peff = ENormal | ENotVery | Esuper
```

但变体的威力远远不止这些。

## 携带数据的变体

{{ video_embed | replace("%%VID%%", "u6P5XdRta04")}}

作为一个贯穿示例，这里是一个变体类型 `shape`，它不仅仅是枚举值：

```{code-cell} ocaml
type point = float * float
type shape =
  | Point of point
  | Circle of point * float (* center and radius *)
  | Rect of point * point (* lower-left and upper-right corners *)
```

这个类型 `shape` 代表一个形状，它可以是点、圆或矩形。一个点由构造函数 `Point` 表示，它*携带*一些额外的数据，即 `point` 类型的一个值。一个圆由构造函数 `Circle` 表示，它携带两部分数据：一个是 `point` 类型，另一个是 `float` 类型。这些数据分别代表圆的中心和半径。矩形由构造函数 `Rect` 表示，它也携带两个点。

{{ video_embed | replace("%%VID%%", "K_eA-8LhlVY")}}
{{ video_embed | replace("%%VID%%", "SpuQfO_597E")}}

以下是使用 `shape` 类型的几个函数：
```{code-cell} ocaml
let area = function
  | Point _ -> 0.0
  | Circle (_, r) -> Float.pi *. (r ** 2.0)
  | Rect ((x1, y1), (x2, y2)) ->
      let w = x2 -. x1 in
      let h = y2 -. y1 in
      w *. h

let center = function
  | Point p -> p
  | Circle (p, _) -> p
  | Rect ((x1, y1), (x2, y2)) -> ((x2 +. x1) /. 2.0, (y2 +. y1) /. 2.0)
```

`shape` 变体类型与我们之前看到的变体类似：它由一组构造函数定义。
不同之处在于，这些构造函数附带了额外的数据。
`shape` 类型的每个值都恰好由这些构造函数之一形成。
我们有时说构造函数带有一个 *tag*，
因为它把所携带的数据标记为来自某个特定构造函数。

变体类型有时称为“标记联合”。该类型的每个值都是
来自一组值，该值是基础类型的所有值的并集
构造函数携带的。例如，对于 `shape` 类型，每个值都是
带有 `Point` 或 `Circle` 或 `Rect` 标记，并带有以下值：

- 所有 `point` 值的集合，与
- 所有 `point * float` 值的集合，与
- 所有 `point * point` 值的集合。

这些变体类型的另一个名称是“代数数据类型”。这里的“代数”
指的是变体类型同时包含和类型与积类型，正如
上一讲中已经定义过的那样。和类型来自这样一个事实：
变体的一个值由“若干构造函数之一”形成。积类型来自这样一个事实：
构造函数可以携带元组或记录，而这些值包含来自其*每个*
组成类型的子值。

使用变体，我们可以表达一个代表其他几个的联合的类型
类型，但以类型安全的方式。例如，这里是一个代表的类型
`string` 或 `int`：
```{code-cell} ocaml
type string_or_int =
  | String of string
  | Int of int
```
如果我们愿意，我们可以使用这种类型来编码包含以下内容的列表（例如）
字符串或整数：
```{code-cell} ocaml
type string_or_int_list = string_or_int list

let rec sum : string_or_int list -> int = function
  | [] -> 0
  | String s :: t -> int_of_string s + sum t
  | Int i :: t -> i + sum t

let lst_sum = sum [String "1"; Int 2]
```
因此，变体提供了一种类型安全的方法来执行以前可能执行的操作
似乎不可能。

变体还可以区分一个值是由哪个标签构造出来的，
即使多个构造函数携带相同的类型。例如：
```{code-cell} ocaml
type t = Left of int | Right of int
let x = Left 1
let double_right = function
  | Left i -> i
  | Right i -> 2 * i
```

## 语法和语义

{{ video_embed | replace("%%VID%%", "3A_PNz5njt0")}}

**语法。**

要定义变体类型：
```ocaml
type t = C1 [of t1] | ... | Cn [of tn]
```
上面的方括号表示 `of ti` 是可选的。每个构造函数
都可以独立地选择是否携带数据。我们把不携带数据的构造函数
称为*常量*构造函数；把携带数据的构造函数称为*非常量*构造函数。

要编写一个变体表达式：
```ocaml
C e
```
或者：
```ocaml
C
```
取决于构造函数名称 `C` 是非常量还是常量。

**动态语义。**

* 如果 `e ==> v` 则 `C e ==> C v`，假设 `C` 是非常量。
* 假设 `C` 是常量，`C` 已经是一个值。

**静态语义。**

* 如果 `t = ... | C | ...` 则 `C : t`。
* 如果 `t = ... | C of t' | ...` 并且如果 `e : t'` 则 `C e : t`。

**模式匹配。**

我们将以下新模式形式添加到合法模式列表中：

* `C p`

我们扩展了模式何时匹配一个值并产生的定义
绑定如下：

* 如果 `p` 匹配 `v` 并生成绑定 $b$，则 `C p` 匹配 `C v` 并且
生成绑定 $b$。

## 通配情况

用模式匹配变体时，需要注意 *Real World OCaml*
所说的“通配情况”。下面这个简单例子展示了可能出错的地方。
假设你编写了这个变体和函数：
```{code-cell} ocaml
type color = Blue | Red

(* a thousand lines of code in between *)

let string_of_color = function
  | Blue -> "blue"
  | _ -> "red"
```
看起来不错，对吧？但有一天你发现世界上还有更多颜色：
你需要表示绿色。于是你回去把绿色添加到变体中：
```{code-cell} ocaml
type color = Blue | Red | Green

(* a thousand lines of code in between *)

let string_of_color = function
  | Blue -> "blue"
  | _ -> "red"
```
但因为中间隔着数千行代码，你忘记了
`string_of_color` 也需要更新。现在，它突然变得
红绿不分：
```{code-cell} ocaml
string_of_color Green
```
问题出在 `string_of_color` 中模式匹配的 *catch-all* 情况：
最后一个使用通配符模式的分支会匹配任何东西。
这类代码面对变体类型未来的变化并不稳健。

相反，如果你一开始这样编写该函数，情况就会好得多：
```{code-cell} ocaml
let string_of_color = function
  | Blue -> "blue"
  | Red  -> "red"
```
OCaml 类型检查器现在会提醒你尚未更新
`string_of_color` 来处理新的构造函数。

这个故事的寓意是：通配情况可能导致有错误的代码。应当避免使用它们。

## 递归变体

{{ video_embed | replace("%%VID%%", "gDh217oAfnY")}}

变体类型可能会在自身定义中提到自己的名字。例如，
这是一个变体类型，可以用来表示类似的东西
`int list`：
```{code-cell} ocaml
type intlist = Nil | Cons of int * intlist

let lst3 = Cons (3, Nil)  (* similar to 3 :: [] or [3] *)
let lst123 = Cons(1, Cons(2, lst3)) (* similar to [1; 2; 3] *)

let rec sum (l : intlist) : int =
  match l with
  | Nil -> 0
  | Cons (h, t) -> h + sum t

let rec length : intlist -> int = function
  | Nil -> 0
  | Cons (_, t) -> 1 + length t

let empty : intlist -> bool = function
  | Nil -> true
  | Cons _ -> false
```
请注意，在 `intlist` 的定义中，我们将 `Cons` 构造函数定义为
携带一个包含 `intlist` 的值。这使得类型 `intlist` 成为
*递归*：它是根据自身定义的。

如果使用 `and` 关键字，类型可能是相互递归的：
```{code-cell} ocaml
type node = {value : int; next : mylist}
and mylist = Nil | Node of node
```

任何此类相互递归必须至少涉及一种变体或记录类型
递归“通过”。  例如，以下行为是不允许的：
```{code-cell} ocaml
:tags: ["raises-exception"]
type t = u and u = t
```
但这是：
```{code-cell} ocaml
type t = U of u and u = T of t
```

记录类型也可以是递归的：
```{code-cell} ocaml
type node = {value : int; next : node}
```
但普通的旧类型同义词可能不是：
```{code-cell} ocaml
:tags: ["raises-exception"]
type t = t * t
```

虽然 `node` 是合法的类型定义，但无法构造值
属于这种类型，因为涉及循环：构造第一个
`node` 值存在，你已经需要 `node` 类型的值来
存在。稍后，当我们介绍命令式特性时，我们会看到使用类似的想法
（但成功）对于可变链表。

## 参数化变体

变体类型可以在其他类型上“参数化”。  例如，
上面的 `intlist` 类型可以概括为提供列表（编码为
我们自己）超过任何类型：
```{code-cell} ocaml
type 'a mylist = Nil | Cons of 'a * 'a mylist

let lst3 = Cons (3, Nil)  (* similar to [3] *)
let lst_hi = Cons ("hi", Nil)  (* similar to ["hi"] *)
```
这里， `mylist` 是一个*类型构造函数*，但不是一个类型：没有办法写
类型为 `mylist` 的值。但我们可以写入 `int mylist` 类型的值（例如，
`lst3`) 和 `string mylist` (例如 `lst_hi`)。将类型构造函数视为
就像一个函数，但是将类型映射到类型，而不是将值映射到
值。

以下是 `'a mylist` 上的一些函数：
```{code-cell} ocaml
let rec length : 'a mylist -> int = function
  | Nil -> 0
  | Cons (_, t) -> 1 + length t

let empty : 'a mylist -> bool = function
  | Nil -> true
  | Cons _ -> false
```
请注意，每个函数的主体与之前的定义相比没有变化
对于 `intlist`。我们改变的只是类型注释。这甚至可以
安全地省略：
```{code-cell} ocaml
let rec length = function
  | Nil -> 0
  | Cons (_, t) -> 1 + length t

let empty = function
  | Nil -> true
  | Cons _ -> false
```

我们刚刚编写的函数展示了一种语言特性，称为
**参数多态性**。这些函数不关心 `'a` 是什么
`'a mylist`，因此他们非常乐意在 `int mylist` 上工作或
`string mylist` 或任何其他 `(whatever) mylist`。 “多态性”这个词是
基于希腊词根“poly”（许多）和“morph”（形式）。类型的值
`'a mylist` 可以有多种形式，具体取决于实际类型 `'a`。

不过，当你对 `'a` 类型施加约束时，你
放弃一些多态性。例如，
```{code-cell} ocaml
let rec sum = function
  | Nil -> 0
  | Cons (h, t) -> h + sum t
```
我们将 `( + )` 运算符与列表头一起使用这一事实限制了
该头元素是 `int`，因此所有元素都必须是 `int`。这意味着
`sum` 必须采用 `int mylist`，而不是任何其他类型的 `'a mylist`。

参数化类型也可以有多个类型参数，
在这种情况下需要括号：
```{code-cell} ocaml
type ('a, 'b) pair = {first : 'a; second : 'b}
let x = {first = 2; second = "hello"}
```

## 多态变体

到目前为止，每当你想要定义变体类型时，你都必须给出
它是一个名称，例如 `day`、`shape` 或 `'a mylist`：

```{code-cell} ocaml
type day = Sun | Mon | Tue | Wed | Thu | Fri | Sat

type shape =
  | Point of point
  | Circle of point * float
  | Rect of point * point

type 'a mylist = Nil | Cons of 'a * 'a mylist
```

有时，你可能仅需要变量类型作为返回值
单一函数。例如，这里有一个函数 `f` ，它可以返回一个
`int` 或 $\infty$；你被迫定义一个变体类型来表示
结果：
```{code-cell} ocaml
type fin_or_inf = Finite of int | Infinity

let f = function
  | 0 -> Infinity
  | 1 -> Finite 1
  | n -> Finite (-n)
```
这个定义的缺点是你被迫定义
`fin_or_inf` 即使它不会在你的程序的大部分内容中使用。

OCaml 中还有另一种变体支持这种编程：
*多态性变体*。多态变体与变体一样，除了：

1. 在使用它们之前，你不必声明它们的类型或构造函数。

2. 多态变体类型没有名称。（所以这个特性的另一个名字
可能是“匿名变体”。）

3. 多态变体的构造函数以反引号字符开头。

使用多态变体，我们可以重写 `f`：
```{code-cell} ocaml
let f = function
  | 0 -> `Infinity
  | 1 -> `Finite 1
  | n -> `Finite (-n)
```

该类型表示 `f` 要么返回 `` `Finite n`` for some `n : int` 要么
`` `Infinity``。方括号并不表示列表，而是表示一组
可能的构造函数。 `>` 符号表示模式匹配的任何代码
针对该类型的值必须“至少”处理构造函数
`` `Finite`` and `` `Infinity`，甚至可能更多。例如，我们可以写：
```{code-cell} ocaml
match f 3 with
  | `NegInfinity -> "negative infinity"
  | `Finite n -> "finite"
  | `Infinity -> "infinite"
```
模式匹配包含除以下之外的构造函数是完全可以的
`` `Finite`` or `` `Infinity``, because `f` 保证永远不会返回任何
除此之外的构造函数。

我们将会看到多态变体还有其他更引人注目的用途
稍后在课程中。它们在库中特别有用。目前，我们
通常会引导你远离多态变体的广泛使用，
因为它们的类型可能变得难以管理。

## 内置变体

OCaml 的内置列表数据类型实际上是一种递归的参数化变体。它
定义如下：
```{code-cell} ocaml
:tags: ["remove-output"]
type 'a list = [] | ( :: ) of 'a * 'a list
```
所以 `list` 实际上只是一个类型构造函数，带有（值）构造函数
`[]` （我们发音为“nil”）和 `::` （我们发音为“cons”）。

OCaml 的内置选项数据类型实际上也是参数化变体。这是
定义如下：
```{code-cell} ocaml
:tags: ["remove-output"]
type 'a option = None | Some of 'a
```
所以 `option` 实际上只是一个类型构造函数，带有（值）构造函数
`None` 和 `Some`。

你可以看到 [core OCaml library][core] 中定义了 `list` 和 `option`。

[core]: https://ocaml.org/manual/core.html
