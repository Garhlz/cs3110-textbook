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

# 函子

{{ video_embed | replace("%%VID%%", "CLi5RmgQ9Mg")}}

我们在上一节中遇到的问题是我们想要添加
代码到两个不同的模块，但是该代码需要在
所添加模块的详细信息。就是这样的
由称为 *functors* 的 OCaml 语言特性启用的参数化。

```{note}
**为什么命名为“函子”？** 在 [category theory][intellectualterrorism] 中，一个
*类别*包含*态射*，这是我们所描述的函数的泛化
了解它们，*函子*是类别之间的映射。同样，OCaml 模块
包含函数，并且 OCaml 函子从模块映射到模块。
```

[intellectualterrorism]: https://en.wikipedia.org/wiki/Category_theory

不幸的是，这个名字令人生畏，但**函子只是一个“函数”
从模块到模块。**“函数”一词在引号中
句子只是因为它是一种不可互换的函数
其余的函数我们已经见过了。 OCaml 的类型系统是
*分层*：模块值与其他值不同，因此函数来自
模块到模块的编写或使用方式不能与来自模块的函数相同
价值观对价值观。但从概念上讲，函子实际上只是函数。

这是函子的一个小例子：

```{code-cell} ocaml
module type X = sig
  val x : int
end

module IncX (M : X) = struct
  let x = M.x + 1
end
```

函子的名称是 `IncX`。它本质上是一个从模块到
模块。作为一个函数，它接受输入并产生输出。它的输入是
名为`M`，其输入类型为`X`。它的输出是这样的结构
出现在等号的右侧：`struct let x = M.x + 1 end`。

考虑 `IncX` 的另一种方式是它是一个*参数化结构*。
它采用的参数名为 `M` 且类型为 `X`。该结构本身有
其中有一个名为 `x` 的值。 `x` 的值取决于
参数`M`。

由于函子本质上是函数，因此我们“应用”它们。这是一个例子
应用`IncX`：
```{code-cell} ocaml
module A = struct let x = 0 end
```

```{code-cell} ocaml
A.x
```

```{code-cell} ocaml
module B = IncX (A)
```

```{code-cell} ocaml
B.x
```

```{code-cell} ocaml
module C = IncX (B)
```

```{code-cell} ocaml
C.x
```

每次，我们都会传递 `IncX` 一个模块。当我们传递它时，模块绑定到名称
`A`，`IncX` 的输入是 `struct let x = 0 end`。函子 `IncX` 认为
输入并产生输出 `struct let x = A.x + 1 end`。由于 `A.x` 是 `0`，
结果是`struct let x = 1 end`。因此 `B` 绑定到 `struct let x = 1 end`。
同样，`C` 最终被绑定到 `struct let x = 2 end`。

尽管函子 `IncX` 返回一个与其输入非常相似的模块
模块，情况不一定如此。事实上，函子可以返回任何模块
喜欢，也许与它的输入结构非常不同：

```{code-cell} ocaml
module AddX (M : X) = struct
  let add y = M.x + y
end
```

让我们将该函子应用于模块。  该模块甚至不必
受名称约束；我们可以写一个匿名结构：

```{code-cell} ocaml
module Add42 = AddX (struct let x = 42 end)
```

```{code-cell} ocaml
Add42.add 1
```

请注意，`AddX` 的输入模块包含一个名为 `x` 的值，但输出
`AddX` 中的模块不会：

```{code-cell} ocaml
:tags: ["raises-exception"]
Add42.x
```

```{warning}
人们很容易认为函子与 Java 中的 `extends` 相同，并且
因此，函子用新的定义扩展了输入模块，同时
也保留旧的定义。上面的例子表明，这不是
案例。函子本质上只是一个函数，并且该函数可以返回
无论程序员想要什么。事实上函子的输出可以是
与输入任意不同。
```

## 函子语法和语义

在我们一直使用的函子语法中：

```ocaml
module F (M : S) = ...
end
```

类型注释 `: S` 及其周围的括号 `(M : S)` 是必需的。
原因是 OCaml 需要提供有关 `S` 的类型信息
为了做好 `F` 本身的类型推断。

与函数非常相似，函子可以匿名编写。下面两个
函子的语法是等效的：

```ocaml
module F (M : S) = ...

module F = functor (M : S) -> ...
```

第二种形式使用 `functor` 关键字创建一个匿名函子，例如
`fun` 关键字如何创建匿名函数。

函子可以在多个结构上参数化：

```ocaml
module F (M1 : S1) ... (Mn : Sn) = ...
```

当然，这只是一个“高阶函子”的语法糖，它需要
一个结构体作为输入并返回一个匿名函子：

```ocaml
module F = functor (M1 : S1) -> ... -> functor (Mn : Sn) -> ...
```

如果你想指定函子的输出类型，语法又是
类似函数：

```ocaml
module F (M : Si) : So = ...
```

像往常一样，也可以在模块上编写输出类型注释
表达式：

```ocaml
module F (M : Si) = (... : So)
```

要评估应用程序 `module_expression1 (module_expression2)`，第一个
模块表达式被求值并且必须产生一个函子 `F`。第二模块
然后表达式被评估为模块 `M`。然后函子被应用到
模块。函子将生成一个新模块 `N` 作为其中的一部分
应用程序。该新模块一如既往地按照定义顺序进行评估
从上到下，可以使用 `M` 的定义。

## 函子类型语法和语义

函子类型最简单的语法实际上与函数相同：

```ocaml
module_type -> module_type
```

例如，下面的 `X -> Add` 是一个仿函数类型，它适用于 `AddX`
我们在本节前面定义的模块：

```{code-cell} ocaml
module type Add = sig val add : int -> int end
module CheckAddX : X -> Add = AddX
```

如果输出模块类型是，函子类型语法会变得更加复杂
取决于输入模块类型。例如，假设我们想创建一个
将一个模块中的值与另一个值配对的函子：

```{code-cell} ocaml
module type T = sig
  type t
  val x : t
end

module Pair1 (M : T) = struct
  let p = (M.x, 1)
end
```

`Pair1` 的类型结果是：

```ocaml
functor (M : T) -> sig val p : M.t * int end
```

所以我们也可以这样写：

```{code-cell} ocaml
module type P1 = functor (M : T) -> sig val p : M.t * int end

module Pair1 : P1 = functor (M : T) -> struct
  let p = (M.x, 1)
end
```

模块类型 `P1` 是采用名为 `M` 的输入模块的仿函数的类型
模块类型 `T`，并返回一个输出模块，其模块类型由下式给出
签名 `sig..end`。在签名内部，名称 `M` 在范围内。那是
为什么我们可以在里面写`M.t`，从而保证第一个的类型
对 `p` 的组件是来自传递的*特定*模块 `M` 的类型
进入 `Pair1`，而不是任何*其他*模块。例如，这里有两个不同的
实例化：

```{code-cell} ocaml
module P0 = Pair1 (struct type t = int let x = 0 end)
module PA = Pair1 (struct type t = char let x = 'a' end)
```

请注意生成的模块类型中 `int` 和 `char` 之间的差异。这是
重要的是 `Pair1` 的输出模块类型可以区分它们。并且
这就是为什么 `M` 必须在 `P1` 中箭头的右侧命名。

```{note}
functor 类型是一种高级编程语言特性的例子，称为
*依赖类型*，输出的 **类型** 由
输入的**值**。这与函数的正常情况不同，
其中输出**值**由输入值决定，并且
输出**类型**与输入值无关。

依赖类型使类型系统能够表达更多关于正确性的信息
程序的一部分，但依赖类型的类型检查和推理要复杂得多
具有挑战性。实用的依赖类型系统是一个活跃的研究领域。
也许有一天它们会在主流语言中流行起来。
```

函子的实际参数的模块类型不需要与
参数的正式声明模块类型；成为一个亚型就好了。对于
例如，可以将下面的 `F` 应用于 `X` 或 `Z`。中的额外项目
`Z` 不会造成任何困难。

```{code-cell} ocaml
module F (M : sig val x : int end) = struct let y = M.x end
module X = struct let x = 0 end
module Z = struct let x = 0;; let z = 0 end
module FX = F (X)
module FZ = F (Z)
```

## `Map` 模块

{{ video_embed | replace("%%VID%%", "sCbUwQvNYJA")}}

标准库的 Map 模块实现了一个映射（从键到键的绑定）
值）使用平衡二叉树。它以一种重要的方式使用函子。在
本节我们研究如何使用它。你可以看到
[implementation of that module on GitHub][mapimplsrc] 及其
[interface][mapintsrc]。

[mapintsrc]: https://github.com/ocaml/ocaml/blob/trunk/stdlib/map.mli
[mapimplsrc]: https://github.com/ocaml/ocaml/blob/trunk/stdlib/map.ml

Map 模块定义了一个函子 `Make` ，它创建一个实现
映射特定类型的键。该类型是 `Make` 的输入结构。
该输入结构的类型是 `Map.OrderedType`，这些类型
支持 `compare` 操作：

```{code-cell} ocaml
module type OrderedType = sig
  type t
  val compare : t -> t -> int
end
```

Map 模块需要排序，因为平衡二叉树需要能够
比较键以确定一个是否大于另一个。 `compare`
函数的规范与比较参数的规范相同
`List.sort_uniq`，我们之前讨论过：

- 如果两个键相等，则比较应返回 `0`。
- 如果第一个键是，则比较应返回严格的负数
小于第二个。
- 如果第一个键是，则比较应返回严格正数
大于第二个。

````{note}
这个规格看起来是不是有点奇怪？是不是看起来很难记住
何时返回负数和正数？为什么不定义一个变体呢？
```ocaml
type order = LT | EQ | GT
val compare : t -> t -> order
```
唉，历史上许多语言都使用过类似的比较函数
规范，例如 C 标准库的 [`strcmp` function][strcmp]。

[strcmp]: http://www.gnu.org/software/libc/manual/html_node/String_002fArray-Comparison.html
````

`Map.Make` 的输出支持我们期望的所有常用操作
一本字典：

```ocaml
module type S = sig
  type key
  type 'a t
  val empty: 'a t
  val mem: key -> 'a t -> bool
  val add: key -> 'a -> 'a t -> 'a t
  val find: key -> 'a t -> 'a
  ...
end
```

类型变量 `'a` 是映射中值的类型。  所以任何特定的
由 `Map.Make` 创建的映射模块只能处理一种类型的键，但不是
仅限于任何特定类型的值。

### 映射示例

以下是使用 `Map.Make` 函子的示例：

```{code-cell} ocaml
:tags: ["hide-output"]
module IntMap = Map.Make(Int)
```

如果显示该输出，你将看到长模块类型 `IntMap`。 `Int`
模块是标准库的一部分。方便的是，它已经定义了两个
`OrderedType` 所需的项目，即 `t` 和 `compare`，以及适当的
行为。标准库还已经定义了其他模块
原始类型（`String` 等），可以方便地使用任何原始类型作为键。

现在让我们通过将 `int` 映射到 `string` 来尝试该映射：

```{code-cell} ocaml
open IntMap;;
let m1 = add 1 "one" empty
```
```{code-cell} ocaml
find 1 m1
```
```{code-cell} ocaml
mem 42 m1
```
```{code-cell} ocaml
:tags: ["raises-exception"]
find 42 m1
```
```{code-cell} ocaml
bindings m1
```

相同的 `IntMap` 模块允许我们将 `int` 映射到 `float`：

```{code-cell} ocaml
let m2 = add 1 1. empty
```
```{code-cell} ocaml
bindings m2
```

但键必须是 `int`，而不是任何其他类型：

```{code-cell} ocaml
:tags: ["raises-exception"]
let m3 = add true "one" empty
```

这是因为 `IntMap` 模块是专门为整数键创建的，并会相应地排序。
再次强调，顺序至关重要，因为底层数据结构是二叉搜索树，
需要通过键比较来确定键在树中的存储位置。你甚至可以看到
在 [standard library source code (v4.12)][mapv412] 中，其中
以下是经过轻微编辑的摘录：

[mapv412]: https://github.com/ocaml/ocaml/blob/4.12/stdlib/map.ml

```ocaml
module Make (Ord : OrderedType) = struct
  type key = Ord.t

  type 'a t =
    | Empty
    | Node of {l : 'a t; v : key; d : 'a; r : 'a t; h : int}
      (** Left subtree, key, value/data, right subtree, height of node. *)

  let empty = Empty

  let rec mem x = function
    | Empty -> false
    | Node {l, v, r} ->
        let c = Ord.compare x v in
        c = 0 || mem x (if c < 0 then l else r)
  ...
end
```

`key` 类型被定义为 `Ord` 内类型 `t` 的同义词，因此
`key` 值可使用 `Ord.compare` 进行比较。  `mem` 函数使用
比较键并决定是在左子树还是右子树上递归
子树。

注意 `Map` 的实现者如何解决一个棘手的问题：平衡二叉
搜索树需要一种比较键的方法，但实现者不可能提前知道
数据结构的客户端想要使用哪些不同类型的键。而且每种键类型
都可能需要自己的比较函数。
尽管 `Stdlib.compare` *可以*用于比较任意两个相同的值
类型的值，它返回的结果不一定是客户端想要的。对于
例如，不能保证按照我们上面想要的方式对名称进行排序。

因此 `Map` 的实现者使用函子来解决他们的问题。他们
在将键类型与函数捆绑在一起的模块上进行参数化
可以用来比较它们。客户端负责实现
那个模块。

Java Collections Framework 在 `TreeMap` 类中解决了类似的问题，
其中有一个 [constructor that takes a Comparator][treemapcomparator]。在那里，
客户端负责实现一个用于比较的类，而不是一个结构。
虽然语言特性不同，但思想是一样的。

[treemapcomparator]: https://docs.oracle.com/javase/8/docs/api/java/util/TreeMap.html#TreeMap-java.util.Comparator-

### 具有自定义键类型的映射

当键的类型变得复杂时，我们可能想编写自己的键
自定义比较函数。例如，假设我们想要一个映射，其中键是
代表姓名的记录，其中姓名按最后一个的字母顺序排序
然后按名字命名。在下面的代码中，我们提供了一个模块 `Name` ，可以
这样比较记录：

```{code-cell} ocaml
type name = {first : string; last : string}

module Name = struct
  type t = name
  let compare { first = first1; last = last1 } { first = first2; last = last2 }
      =
    match String.compare last1 last2 with
    | 0 -> String.compare first1 first2
    | c -> c
end
```

`Name` 模块可以用作 `Map.Make` 的输入，因为它满足
`Map.OrderedType` 签名：

```{code-cell} ocaml
:tags: ["hide-output"]
module NameMap = Map.Make (Name)
```

现在我们可以使用该映射将姓名与出生年份关联起来：

```{code-cell} ocaml
let k1 = {last = "Kardashian"; first = "Kourtney"}
let k2 = {last = "Kardashian"; first = "Kimberly"}
let k3 = {last = "Kardashian"; first = "Khloe"}

let nm =
  NameMap.(empty |> add k1 1979 |> add k2 1980 |> add k3 1984)

let lst = NameMap.bindings nm
```

请注意该列表中键的顺序与我们的顺序不同
他们补充道。该列表根据我们的 `Name.compare` 函数排序
写道。 `Map.S` 签名中的其他几个函数也将处理
按排序顺序映射绑定&mdash;，例如`map`、`fold` 和`iter`。

### `Map` 如何使用模块类型约束

在标准库的 `map.mli` 接口中，规范为
`Map.Make` 是：

```ocaml
module Make (Ord : OrderedType) : S with type key = Ord.t
```

`with` 约束至关重要。回想一下，类型约束是专门化的
模块类型。这里， `S with type key = Ord.t` 专门 `S` 来暴露
`S.key` 和 `Ord.t` 相等。换句话说，键的类型是有序的
类型。

你可以通过查看模块类型来了解该共享约束的效果
我们之前的 `IntMap` 示例。共享约束是造成这种情况的原因
`= Int.t` 出席：

```ocaml
module IntMap : sig
  type key = Int.t
  ...
end
```

并且 `Int` 模块包含这一行：

```ocaml
type t = int
```

所以 `IntMap.key = Int.t = int`，这正是我们被允许通过的原因
`int` 到 `IntMap` 的 `add` 和 `mem` 函数。

如果没有类型约束，类型 `key` 将保持抽象。我们可以
通过添加 `Map.S` 的模块类型注释来模拟，从而
重新密封该类型的模块而不暴露等式：

```{code-cell} ocaml
module UnusableMap = (IntMap : Map.S);;
```

现在不可能向映射添加绑定：

```{code-cell} ocaml
:tags: ["raises-exception"]
let m = UnusableMap.(empty |> add 0 "zero")
```

这种用例就是为什么模块类型约束在
使用 OCaml 模块系统进行有效编程。很多时候需要
专门化函子的输出类型以显示类型之间的关系
它和函子输入之一的类型。仔细思考到底是什么
约束是必要的，但可能具有挑战性！

## 使用函子

通过 `Map`，我们看到了函子的一个用例：生成一个数据结构
根据客户提供的订单进行参数化。这里还有两个用例。

### 测试套件

下面是堆栈的两种实现：

```{code-cell} ocaml
:tags: ["hide-output"]
exception Empty

module type Stack = sig
  type 'a t
  val empty : 'a t
  val push : 'a -> 'a t -> 'a t
  val peek : 'a t -> 'a
  val pop : 'a t -> 'a t
end

module ListStack = struct
  type 'a t = 'a list
  let empty = []
  let push = List.cons
  let peek = function [] -> raise Empty | x :: _ -> x
  let pop = function [] -> raise Empty | _ :: s -> s
end

module VariantStack = struct
  type 'a t = E | S of 'a * 'a t
  let empty = E
  let push x s = S (x, s)
  let peek = function E -> raise Empty | S (x, _) -> x
  let pop = function E -> raise Empty | S (_, s) -> s
end
```

假设我们想为 `ListStack` 编写一个 OUnit 测试：

```{code-cell} ocaml
:tags: ["remove-cell"]
#use "topfind";;
#require "ounit2";;
open OUnit2;;
```

```{code-cell} ocaml
:tags: ["remove-output"]
let test = "peek (push x empty) = x" >:: fun _ ->
  assert_equal 1 ListStack.(empty |> push 1 |> peek)
```

不幸的是，要测试 `VariantStack`，我们必须复制该代码：

```{code-cell} ocaml
:tags: ["remove-output"]
let test' = "peek (push x empty) = x" >:: fun _ ->
  assert_equal 1 VariantStack.(empty |> push 1 |> peek)
```

如果我们有其他堆栈实现，我们必须重复测试
他们也是。如果这只是一个测试用例，那么考虑起来并没有那么可怕
几个实现，但如果是数百次测试，即使是几个
实现，重复太多，无法成为好的软件
工程。

函子提供了更好的解决方案。我们可以编写一个参数化的函子
在堆栈实现上，并生成该实现的测试：

```{code-cell} ocaml
:tags: ["remove-output"]
module StackTester (S : Stack) = struct
  let tests = [
    "peek (push x empty) = x" >:: fun _ ->
      assert_equal 1 S.(empty |> push 1 |> peek)
  ]
end

module ListStackTester = StackTester (ListStack)
module VariantStackTester = StackTester (VariantStack)

let all_tests = List.flatten [
  ListStackTester.tests;
  VariantStackTester.tests
]
```

现在，每当我们发明一个新测试时，我们都会将其添加到 `StackTester` 中，并且它
自动在两个堆栈实现上运行。好的！

不过，仍然存在一些令人反感的代码重复，因为我们
每个实现必须编写两行代码。  我们可以消除
通过使用一流模块进行重复：

```{code-cell} ocaml
:tags: ["remove-output"]
let stacks = [ (module ListStack : Stack); (module VariantStack) ]

let all_tests =
  let tests m =
    let module S = (val m : Stack) in
    let module T = StackTester (S) in
    T.tests
  in
  let open List in
  stacks |> map tests |> flatten
```

现在只需将最新的堆栈实现添加到 `stacks` 即可
列表。更好了！

### 扩展多个模块

之前，我们尝试向 `ListSet` 和 `ListSet` 添加函数 `of_list`
`UniqListSet` 没有任何重复的代码，但我们并没有完全成功。
现在让我们真正做对吧。

我们之前遇到的问题是我们需要参数化实现
`add` 函数上的 `of_list` 和 set 模块中的 `empty` 值。我们可以
使用函子完成参数化：

```{code-cell} ocaml
:tags: ["remove-output"]
module type Set = sig
  type 'a t
  val empty : 'a t
  val mem : 'a -> 'a t -> bool
  val add : 'a -> 'a t -> 'a t
  val elements : 'a t -> 'a list
end

module SetOfList (S : Set) = struct
  let of_list lst = List.fold_right S.add lst S.empty
end
```

请注意函子在其主体中如何使用 `S.add`。还需要落实
来自 `S` 的 `add` 并使用它来实现 `of_list` （对于 `empty` 也是如此），
从而解决了我们之前尝试使用包含时遇到的确切问题。

当我们将 `SetOfList` 应用到我们的集合实现时，我们得到模块
每个实现都包含一个 `of_list` 函数：

```{code-cell} ocaml
:tags: ["remove-output"]
module ListSet : Set = struct
  type 'a t = 'a list
  let empty = []
  let mem = List.mem
  let add = List.cons
  let elements s = List.sort_uniq Stdlib.compare s
end

module UniqListSet : Set = struct
  (** All values in the list must be unique. *)
  type 'a t = 'a list
  let empty = []
  let mem = List.mem
  let add x s = if mem x s then s else x :: s
  let elements = Fun.id
end
```

```{code-cell} ocaml
module OfList = SetOfList (ListSet)
module UniqOfList = SetOfList (UniqListSet)
```

函子实现了我们以前无法实现的代码重用：我们现在可以
实现一个 `of_list` 函数，并从中派生出两个函数的实现
不同的集合。

但这是这两个模块包含的**唯一**函数。确实是我们想要的
是一个完整的实现，还包含 `of_list` 函数。我们可以
通过将包含与函子结合起来得到：

```{code-cell} ocaml
module SetWithOfList (S : Set) = struct
  include S
  let of_list lst = List.fold_right S.add lst S.empty
end
```

该函子接受一个集合作为输入，并生成一个包含以下内容的模块：
该集合中的所有内容（因为 `include`）以及一个新函数
`of_list`。

当我们应用函子时，我们得到一个非常好的集合模块：

```{code-cell} ocaml
module SetL = SetWithOfList (ListSet)
module UniqSetL = SetWithOfList (UniqListSet)
```

注意输出结构如何记录其类型 `t` 相同的事实
type 作为其输入结构中的类型 `t` 。他们分享它是因为
`include`。

退后一步，我们刚刚所做的不仅仅是与课堂的短暂相似
Java 中的扩展。我们创建了一个基本模块并扩展了其功能
新代码，同时保留其旧功能。但是类扩展
要求新扩展的类是旧类的子类型，并且它
仍然具有所有旧功能，OCaml 函子在以下方面更加细粒度
他们能完成什么。我们可以选择是否包含旧的
功能。并且不一定涉及子类型关系。
此外，我们编写的函子可以用来扩展**任何**集合实现
与 `of_list` ，而类扩展仅适用于**单个**基类。
在面向对象语言中，有一些方法可以实现类似的目标：
*mixins*，使一个类能够重用其他类的功能
无需多重继承的复杂性。
