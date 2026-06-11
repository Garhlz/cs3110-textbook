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

`shape` 变体类型与我们之前看到的变体类似：它由一组构造函数定义。不同之处在于，这些构造函数可以附带额外的数据。`shape` 类型的每个值都恰好由这些构造函数之一构成。我们有时说构造函数带有一个*标签*（tag），因为它把所携带的数据标记为来自某个特定构造函数。

变体类型有时称为"带标签的联合类型"（tagged union）。该类型的每个值都来自多个集合的并集，这些集合分别对应各构造函数所携带的基础类型。例如，对于 `shape` 类型，每个值都带有 `Point`、`Circle` 或 `Rect` 标签，并携带来自以下集合之一的值：

- 所有 `point` 值的集合，或
- 所有 `point * float` 值的集合，或
- 所有 `point * point` 值的集合。

这些变体类型还有一个名字叫"代数数据类型"（algebraic data type）。这里的"代数"是指变体类型同时包含和类型与积类型，正如上一节中已经定义过的那样。和类型来自"变体的每个值由多个构造函数*之一*构成"，积类型则来自"构造函数可以携带元组或记录，而这些值包含来自其*每个*组成类型的子值"。

使用变体，我们可以以一种类型安全的方式来表达"一个类型是其他若干类型的联合"。例如，下面的类型表示 `string` 或 `int`：
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
因此，变体提供了一种类型安全的方式来做到以前看似不可能的事情。

变体还可以区分一个值是由哪个标签构造出来的，即使多个构造函数携带相同的类型。例如：
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

我们扩展模式匹配值并产生绑定的定义如下：

* 如果 `p` 匹配 `v` 并产生绑定 $b$，则 `C p` 匹配 `C v` 并产生绑定 $b$。

## 通配分支的陷阱

用模式匹配处理变体时，需要注意 *Real World OCaml* 一书中所说的"通配分支"问题。下面这个简单例子展示了可能出错的地方。假设你编写了这样一个变体和函数：
```{code-cell} ocaml
type color = Blue | Red

(* 中间隔着上千行代码 *)

let string_of_color = function
  | Blue -> "blue"
  | _ -> "red"
```
看起来没问题，对吧？但有一天你发现世界上的颜色不止这两种——你还需要表示绿色。于是你回过头把绿色加到变体定义中：
```{code-cell} ocaml
type color = Blue | Red | Green

(* 中间隔着上千行代码 *)

let string_of_color = function
  | Blue -> "blue"
  | _ -> "red"
```
但因为中间隔着上千行代码，你忘记了 `string_of_color` 也需要更新。现在，它突然间分不清红和绿了：
```{code-cell} ocaml
string_of_color Green
```
问题出在 `string_of_color` 中模式匹配的 *catch-all*（通配）分支：最后一个使用通配符模式的分支会匹配任何值。这类代码面对变体类型未来的变化是脆弱的。

相反，如果你一开始就这样写，情况会好得多：
```{code-cell} ocaml
let string_of_color = function
  | Blue -> "blue"
  | Red  -> "red"
```
OCaml 类型检查器现在就能提醒你：`string_of_color` 还没有针对新构造函数进行更新。

这个故事的寓意是：通配分支可能导致有缺陷的代码，应当避免使用。

## 递归变体

{{ video_embed | replace("%%VID%%", "gDh217oAfnY")}}

变体类型可以在自身的定义中引用自己的名字。例如，下面是一个可以用来表示类似 `int list` 的变体类型：
```{code-cell} ocaml
type intlist = Nil | Cons of int * intlist

let lst3 = Cons (3, Nil)  (* 类似 3 :: [] 或 [3] *)
let lst123 = Cons(1, Cons(2, lst3)) (* 类似 [1; 2; 3] *)

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
注意在 `intlist` 的定义中，我们将 `Cons` 构造函数定义为携带一个包含 `intlist` 的值。这使得类型 `intlist` 成为*递归类型*——它用自身来定义自身。

使用 `and` 关键字，类型可以相互递归：
```{code-cell} ocaml
type node = {value : int; next : mylist}
and mylist = Nil | Node of node
```

任何相互递归都必须至少有一种变体或记录类型来承担"递归传递"的角色。例如，下面的写法是不允许的：
```{code-cell} ocaml
:tags: ["raises-exception"]
type t = u and u = t
```
但这样可以：
```{code-cell} ocaml
type t = U of u and u = T of t
```

记录类型也可以是递归的：
```{code-cell} ocaml
type node = {value : int; next : node}
```
但普通的类型同义词不行：
```{code-cell} ocaml
:tags: ["raises-exception"]
type t = t * t
```

虽然 `node` 是合法的类型定义，但却无法构造出这种类型的值，因为这里存在循环依赖：要构造第一个 `node` 值，你首先需要有一个 `node` 类型的值存在。稍后介绍命令式特性时，我们会看到用类似的想法（成功地）实现可变链表。

## 参数化变体

变体类型可以在其他类型上进行*参数化*。例如，上面的 `intlist` 类型可以推广为提供任意类型的列表（用我们自己编码的方式）：
```{code-cell} ocaml
type 'a mylist = Nil | Cons of 'a * 'a mylist

let lst3 = Cons (3, Nil)  (* 类似 [3] *)
let lst_hi = Cons ("hi", Nil)  (* 类似 ["hi"] *)
```
这里，`mylist` 是一个*类型构造器*，而不是一个类型：没有办法写一个类型为 `mylist` 的值。但我们可以写类型为 `int mylist` 的值（如 `lst3`）和类型为 `string mylist` 的值（如 `lst_hi`）。可以把类型构造器想象成函数，但它将类型映射到类型，而不是将值映射到值。

下面是作用在 `'a mylist` 上的一些函数：
```{code-cell} ocaml
let rec length : 'a mylist -> int = function
  | Nil -> 0
  | Cons (_, t) -> 1 + length t

let empty : 'a mylist -> bool = function
  | Nil -> true
  | Cons _ -> false
```
注意每个函数的主体与之前针对 `intlist` 的定义相比没有变化，我们改变的只是类型标注。这些标注甚至可以安全地省略：
```{code-cell} ocaml
let rec length = function
  | Nil -> 0
  | Cons (_, t) -> 1 + length t

let empty = function
  | Nil -> true
  | Cons _ -> false
```

我们刚刚编写的函数展示了一种称为**参数多态性**（parametric polymorphism）的语言特性。这些函数不关心 `'a mylist` 中的 `'a` 具体是什么，因此它们可以愉快地作用于 `int mylist`、`string mylist` 或任何其他 `(something) mylist`。"多态性"（polymorphism）一词源于希腊词根"poly"（许多）和"morph"（形式）。类型 `'a mylist` 的值可以根据实际类型 `'a` 的不同而呈现多种形式。

不过，当你对 `'a` 类型施加约束时，就会放弃一部分多态性。例如：
```{code-cell} ocaml
let rec sum = function
  | Nil -> 0
  | Cons (h, t) -> h + sum t
```
我们在列表头部使用了 `( + )` 运算符，这要求头部元素是 `int`，进而要求所有元素都是 `int`。这意味着 `sum` 必须接受 `int mylist`，而不能是任意类型的 `'a mylist`。

参数化类型也可以有多个类型参数，此时需要括号：
```{code-cell} ocaml
type ('a, 'b) pair = {first : 'a; second : 'b}
let x = {first = 2; second = "hello"}
```

## 多态变体

到目前为止，每当你想定义变体类型时，都必须给它一个名字，比如 `day`、`shape` 或 `'a mylist`：

```{code-cell} ocaml
type day = Sun | Mon | Tue | Wed | Thu | Fri | Sat

type shape =
  | Point of point
  | Circle of point * float
  | Rect of point * point

type 'a mylist = Nil | Cons of 'a * 'a mylist
```

但有时你可能只在一个函数的返回值中需要变体类型。例如，下面这个函数 `f` 可能返回一个 `int` 或 $\infty$；你被迫定义一个变体类型来表示这个结果：
```{code-cell} ocaml
type fin_or_inf = Finite of int | Infinity

let f = function
  | 0 -> Infinity
  | 1 -> Finite 1
  | n -> Finite (-n)
```
这种做法的缺点是你被迫定义了 `fin_or_inf` 类型，尽管它在程序的大部分地方都不会用到。

OCaml 提供了另一种变体形式来支持这种场景：*多态变体*（polymorphic variant）。多态变体与普通变体类似，但有三个区别：

1. 无需在使用前声明类型或其构造函数。

2. 多态变体类型没有名字。（所以这个特性的另一个叫法可能是"匿名变体"。）

3. 多态变体的构造函数以反引号字符开头。

使用多态变体，我们可以重写 `f`：
```{code-cell} ocaml
let f = function
  | 0 -> `Infinity
  | 1 -> `Finite 1
  | n -> `Finite (-n)
```

这个类型表示 `f` 要么返回 `` `Finite n``（其中 `n : int`），要么返回 `` `Infinity``。方括号并不表示列表，而是表示一组可能的构造函数。`>` 符号表示：针对该类型值进行模式匹配的代码，必须"至少"处理 `` `Finite`` 和 `` `Infinity`` 这两个构造函数，甚至还可以处理更多。例如，我们可以写：
```{code-cell} ocaml
match f 3 with
  | `NegInfinity -> "negative infinity"
  | `Finite n -> "finite"
  | `Infinity -> "infinite"
```
模式匹配包含 `` `Finite`` 和 `` `Infinity`` 之外的构造函数也是完全可以的，因为 `f` 保证永远不会返回这些之外的构造函数。

在课程稍后的部分，我们会看到多态变体还有其他更引人注目的用途，尤其是在库中。目前，我们通常会引导你避免广泛使用多态变体，因为它们的类型可能变得难以管理。

## 内置变体

OCaml 的内置列表数据类型实际上就是一种递归的参数化变体。它的定义如下：
```{code-cell} ocaml
:tags: ["remove-output"]
type 'a list = [] | ( :: ) of 'a * 'a list
```
所以 `list` 实际上只是一个类型构造器，带有（值）构造函数 `[]`（读作"nil"）和 `::`（读作"cons"）。

OCaml 的内置选项数据类型实际上也是一种参数化变体。它的定义如下：
```{code-cell} ocaml
:tags: ["remove-output"]
type 'a option = None | Some of 'a
```
所以 `option` 实际上只是一个类型构造器，带有（值）构造函数 `None` 和 `Some`。

你可以在 [OCaml 核心库][core] 中查看 `list` 和 `option` 的定义。

[core]: https://ocaml.org/manual/core.html
