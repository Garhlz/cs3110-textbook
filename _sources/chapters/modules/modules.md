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

# 模块

{{ video_embed | replace("%%VID%%", "hIUSrPxCdHc")}}

在深入讨论之前，我们首先从 OCaml 模块系统的几个示例开始
进入细节。

*结构*只是定义的集合，例如：

```ocaml
struct
  let inc x = x + 1
  type primary_color = Red | Green | Blue
  exception Oops
end
```

在某种程度上，结构就像一个记录：结构有一些不同的
具有名称的组件。但与记录不同的是，它可以定义新类型、异常、
等等。

上面的代码本身无法编译，因为结构不具有相同的
作为整数或函数等值的一流状态。你不能只是输入
utop 中的代码，或将该结构传递给函数等。你可以做的是
将结构绑定到名称：

```{code-cell} ocaml
module MyModule = struct
  let inc x = x + 1
  type primary_color = Red | Green | Blue
  exception Oops
end
```

OCaml 的输出具有以下形式：

```ocaml
module MyModule : sig ... end
```

这表明 `MyModule` 已被定义，并且已被推断
具有出现在冒号右侧的*模块类型*。那个模块
类型写为*signature*：

```ocaml
sig
  val inc : int -> int
  type primary_color = Red | Green | Blue
  exception Oops
end
```

签名本身是*规范*的集合。规格为
变体类型和异常只是它们的原始定义，所以
`primary_color` 和 `Oops` 与原始版本没有什么不同
结构。 `inc` 的规范是用 `val` 关键字编写的，
与我们在其中定义 `inc` 时顶层的响应完全相同。

```{note}
“规范”一词的这种使用可能会令人困惑，因为许多
程序员会用这个词来表示“指定行为的注释”
一个函数。”但如果我们稍微拓宽一下视野，我们就可以允许这种类型
函数的定义是其规范的一部分。所以这至少是一种相关的感觉
这个词。
```

{{ video_embed | replace("%%VID%%", "8Q-2b7iGvXE")}}

模块中的定义通常比模块中的定义更密切相关
`MyModule`。通常一个模块会实现一些数据结构。例如，这里
是一个以链表形式实现的堆栈模块：

```{code-cell} ocaml
module ListStack = struct
  (** [empty] is the empty stack. *)
  let empty = []

  (** [is_empty s] is whether [s] is empty. *)
  let is_empty = function [] -> true | _ -> false

  (** [push x s] pushes [x] onto the top of [s]. *)
  let push x s = x :: s

  (** [Empty] is raised when an operation cannot be applied
      to an empty stack. *)
  exception Empty

  (** [peek s] is the top element of [s].
      Raises [Empty] if [s] is empty. *)
  let peek = function
    | [] -> raise Empty
    | x :: _ -> x

  (** [pop s] is all but the top element of [s].
      Raises [Empty] if [s] is empty. *)
  let pop = function
    | [] -> raise Empty
    | _ :: s -> s
end
```

```{important}
`pop` 的规范可能会让你感到惊讶。请注意，它不会返回
顶部元素。这是 `peek` 的工作。相反，`pop` 返回除顶部之外的所有内容
元素。
```

然后我们可以使用该模块来操作堆栈：

```{code-cell} ocaml
ListStack.push 2 (ListStack.push 1 ListStack.empty)
```

```{warning}
对于那些来自以下国家的程序员来说，这里潜藏着一个常见的困惑：
面向对象的语言。人们很容易将 `ListStack` 视为
你调用其方法的对象。事实上 `ListStack.push` 隐约看起来像
我们在 `ListStack` 对象上调用 `push` 方法。但事实并非如此
正在发生。在面向对象语言中，你可以实例化许多堆栈对象。但在这里，
只有一个 `ListStack`。而且它在很大程度上不是一个物体
因为它没有 `this` 或 `self` 关键字的概念来表示接收
方法调用的对象。
```

无可否认，这是相当冗长的代码。很快我们就会看到几个解决方案
问题，但现在有一个：

```{code-cell} ocaml
ListStack.(push 2 (push 1 empty))
```

通过写入 `ListStack.(e)`，`ListStack` 中的所有名称都可以在 `e` 中使用
无需每次都写入前缀 `ListStack.` 。另一个改进
可以使用管道运算符：

```{code-cell} ocaml
ListStack.(empty |> push 1 |> push 2)
```

现在我们可以从左到右阅读代码，而不必解析括号。
好的。

```{warning}
这里潜伏着另一个常见的面向对象混淆。很容易让人想到
`ListStack` 作为实例化对象的类。那不是
但情况是这样的。请注意上面没有使用 `new` 运算符来创建堆栈，
也没有任何构造函数（在该词的 OO 意义上）。
```

模块比类更加基础。模块只是一个集合
其自己的命名空间中的定义。在 `ListStack` 中，我们有一些定义
函数&mdash;`push`、`pop`等&mdash;和一个值`empty`。

因此，在 Java 中，我们可以使用如下代码创建几个堆栈：

```java
Stack s1 = new Stack();
s1.push(1);
s1.push(2);
Stack s2 = new Stack();
s2.push(3);
```

在 OCaml 中，可以按如下方式创建相同的堆栈：

```{code-cell} ocaml
let s1 = ListStack.(empty |> push 1 |> push 2)
let s2 = ListStack.(empty |> push 3)
```


## 模块定义

{{ video_embed | replace("%%VID%%", "EUJXBpra0oY")}}

`module` 定义关键字非常类似于 `let` 定义关键字
我们之前学过。 （假设 OCaml 设计者可以选择使用
`let_module` 而不是 `module` 以强调相似性。）区别在于
只是这样：

- `let` 将值绑定到名称，而
- `module` 将*模块值*绑定到名称。

**语法。**

模块定义最常见的语法很简单：

```ocaml
module ModuleName = struct
  module_items
end
```

其中结构内的 `module_items` 可以包含 `let` 定义、`type`
定义、`exception` 定义以及嵌套 `module`
定义。模块名称必须以大写字母开头，并且符合习惯用法
他们使用 `CamelCase` 而不是 `Snake_case`。

但更准确的语法版本是：

```ocaml
module ModuleName = module_expression
```

其中 `struct` 只是 `module_expression` 的一种。这是另一个：
已定义模块的名称。例如，你可以写 `module L = List`
如果你想要 `List` 模块的简短别名。我们会看到其他类型的
本节和本章后面的模块表达式。

结构内的定义可以选择以 `;;` 终止，如下所示
顶层：

```{code-cell} ocaml
module M = struct
  let x = 0;;
  type t = int;;
end
```
有时，如果你尝试诊断，临时添加可能会很有用
语法错误。  它将帮助 OCaml 理解你需要两个定义
在语法上是分开的。  修复了潜在的错误之后，
不过，你可以删除 `;;`。

`;;` 的一个用例是，如果你想将表达式作为
模块：

```{code-cell} ocaml
module M = struct
  let x = 0;;
  assert (x = 0);;
end
```

但可以在没有 `;;` 的情况下重写为：

```{code-cell} ocaml
module M = struct
  let x = 0
  let _ = assert (x = 0)
end
```

结构也可以写在一行上，之间有可选的 `;;`
可读性项目：

```{code-cell} ocaml
module N = struct let x = 0 let y = 1 end
module O = struct let x = 0;; let y = 1 end
```

允许使用空结构：

```{code-cell} ocaml
module E = struct end
```

**动态语义。**

我们已经知道表达式被计算为值。同样，一个模块
表达式被计算为*模块值*或简称为“模块”。唯一的
到目前为止，从求值的角度来看，我们唯一感兴趣的模块表达式
其实就是结构。结构求值很简单：只需
按其中出现的顺序评估其中的每个定义。正因为如此，
因此，较早的定义在较晚的定义的范围内，但不在较晚的定义范围内
反之亦然。所以这个模块很好：

```{code-cell} ocaml
module M = struct
  let x = 0
  let y = x
end
```

但这个模块不是，因为当时 `x` 的 `let` 定义是
正在评估，`y` 尚未绑定：

```{code-cell} ocaml
:tags: ["raises-exception"]
module M = struct
  let x = y
  let y = 0
end
```

当然，如果需要的话可以使用相互递归：

```{code-cell} ocaml
module M = struct
  (* Requires: input is non-negative. *)
  let rec even = function
    | 0 -> true
    | n -> odd (n - 1)
  and odd = function
    | 0 -> false
    | n -> even (n - 1)
end
```

**静态语义。**

如果结构中的所有定义都是其本身，则该结构是类型良好的
根据我们已经学过的所有打字规则，打字良好。

正如我们在顶级输出中看到的，结构的模块类型是签名。
不过，模块类型还有更多内容。让我们暂时搁置一下吧
先说说范围。

## 作用域和 Open

{{ video_embed | replace("%%VID%%", "GjlKfsY2nY8")}}

定义模块 `M` 后，你可以使用以下命令访问其中的名称
点运算符。例如：

```{code-cell} ocaml
module M = struct let x = 42 end
```

```{code-cell} ocaml
M.x
```

当然，从模块外部来看，名称 `x` 本身没有意义：

```{code-cell} ocaml
:tags: ["raises-exception"]
x
```

但是你可以将模块的所有定义带入当前作用域
使用 `open`：

```{code-cell} ocaml
open M
```

```{code-cell} ocaml
x
```

打开模块就像为模块中定义的每个名称编写本地定义
模块。例如， `open String` 带来了来自
[String module][string] 进入范围，并具有类似于以下的效果
在本地命名空间上：
```ocaml
let length = String.length
let get = String.get
let lowercase_ascii = String.lowercase_ascii
...
```

[string]: https://ocaml.org/api/String.html

如果模块中定义了类型、异常或模块，那么它们也是
使用 `open` 纳入作用域。

**始终打开的模块。**
有一个自动打开的[special module called `Stdlib`][stdlib]
在每个 OCaml 程序中。它包含“内置”函数和运算符。你
因此永远不需要在它定义的任何名称前添加 `Stdlib.` 前缀，
不过，如果你需要明确地识别来自以下位置的名称，则可以这样做
它。早些时候，这个模块被命名为 `Pervasives`，你可能仍然会看到
某些代码库中的名称。

[stdlib]: https://ocaml.org/api/Stdlib.html

**作为模块项打开。**
`open` 是另一种 `module_item`。这样我们就可以打开里面的一个模块了
另一个：

```{code-cell} ocaml
module M = struct
  open List

  (** [uppercase_all lst] upper-cases all the elements of [lst]. *)
  let uppercase_all = map String.uppercase_ascii
end
```

由于 `List` 已打开，因此它的名称 `map` 在作用域内。但如果我们也想
去掉 `String.` 呢？

```{code-cell} ocaml
:tags: ["raises-exception"]
module M = struct
  open List
  open String

  (** [uppercase_all lst] upper-cases all the elements of [lst]. *)
  let uppercase_all = map uppercase_ascii
end
```

现在我们有一个问题，因为 `String` 也定义了名称 `map`，但是带有一个
与 `List` 不同的类型。像往常一样，后面的定义会掩盖前面的定义，
因此，按照我们的预期，选择了 `String.map` 而不是 `List.map` 。

如果你在代码中使用许多模块，那么你可能至少有
像这样的一次碰撞。通常它会带有标准的高阶函数
就像在许多库模块中定义的 `map` 一样。

```{tip}
因此，通常最好的做法是 **不要** 在 `.ml` 文件或结构的顶部 `open`
你将要使用的所有模块。这也许不同于
与你习惯使用 Java 等语言的方式不同，你可能会
`import` 许多带有 `*` 的包。相反，最好将作用域限制在
你打开的模块。
```

**限制打开作用域。**
我们已经看到了一种限制打开作用域的方法：`M.(e)`。在 `e` 内部，
模块 `M` 中的所有名称都在作用域内。这对于在短表达式中短暂使用 `M` 很有用：

```{code-cell} ocaml
(* remove surrounding whitespace from [s] and convert it to lower case *)
let s = "BigRed "
let s' = s |> String.trim |> String.lowercase_ascii (* long way *)
let s'' = String.(s |> trim |> lowercase_ascii) (* short way *)
```

但是，如果你想将模块纳入整个函数的范围，或者
其他一些大代码块？ （诚然很奇怪）的语法是
`let open M in e`。它使 `M` 中的所有名称都在 `e` 的范围内。对于
示例：

```{code-cell} ocaml
(** [lower_trim s] is [s] in lower case with whitespace removed. *)
let lower_trim s =
  let open String in
  s |> trim |> lowercase_ascii
```

回到我们的 `uppercase_all` 示例，最好避免任何类型的
打开并简单地明确我们在哪里使用哪个模块：

```{code-cell} ocaml
module M = struct
  (** [uppercase_all lst] upper-cases all the elements of [lst]. *)
  let uppercase_all = List.map String.uppercase_ascii
end
```

## 模块类型定义

{{ video_embed | replace("%%VID%%", "4Uew8GEegyg")}}

我们已经看到 OCaml 会将签名推断为模块的类型。
现在让我们看看如何自己编写这些模块类型。举个例子，这里是
基于列表的堆栈的模块类型：

```{code-cell} ocaml
module type LIST_STACK = sig
  exception Empty
  val empty : 'a list
  val is_empty : 'a list -> bool
  val push : 'a -> 'a list -> 'a list
  val peek : 'a list -> 'a
  val pop : 'a list -> 'a list
end
```

现在我们已经有了基于列表的堆栈的模块和模块类型，我们
应该将规范注释从结构移到签名中。
这些注释是中名称规范的正确组成部分
签名。它们指定行为，从而增强类型的规范
由 `val` 声明提供。

```{code-cell} ocaml
:tags: [hide-output]
module type LIST_STACK = sig
  (** [Empty] is raised when an operation cannot be applied
      to an empty stack. *)
  exception Empty

  (** [empty] is the empty stack. *)
  val empty : 'a list

  (** [is_empty s] is whether [s] is empty. *)
  val is_empty : 'a list -> bool

  (** [push x s] pushes [x] onto the top of [s]. *)
  val push : 'a -> 'a list -> 'a list

  (** [peek s] is the top element of [s].
      Raises [Empty] if [s] is empty. *)
  val peek : 'a list -> 'a

  (** [pop s] is all but the top element of [s].
      Raises [Empty] if [s] is empty. *)
  val pop : 'a list -> 'a list
end

module ListStack = struct
  let empty = []

  let is_empty = function [] -> true | _ -> false

  let push x s = x :: s

  exception Empty

  let peek = function
    | [] -> raise Empty
    | x :: _ -> x

  let pop = function
    | [] -> raise Empty
    | _ :: s -> s
end
```

然而，到目前为止，没有任何信息告诉 OCaml 之间存在关系
`LIST_STACK` 和 `ListStack`。如果我们希望 OCaml 确保 `ListStack` 确实
确实有 `LIST_STACK` 指定的模块类型，我们可以添加一个类型
`module` 定义第一行的注释：

```{code-cell} ocaml
module ListStack : LIST_STACK = struct
  let empty = []

  let is_empty = function [] -> true | _ -> false

  let push x s = x :: s

  exception Empty

  let peek = function
    | [] -> raise Empty
    | x :: _ -> x

  let pop = function
    | [] -> raise Empty
    | _ :: s -> s
end
```

编译器同意模块 `ListStack` 确实定义了所有项目
由 `LIST_STACK` 使用适当的类型指定。  如果我们不小心
省略某些项目，类型注释将被拒绝：

```{code-cell} ocaml
:tags: ["raises-exception"]
module ListStack : LIST_STACK = struct
  let empty = []

  let is_empty = function [] -> true | _ -> false

  let push x s = x :: s

  exception Empty

  let peek = function
    | [] -> raise Empty
    | x :: _ -> x

  (* [pop] is missing *)
end
```

**语法。**

模块类型最常见的语法很简单：

```ocaml
module type ModuleTypeName = sig
  specifications
end
```

其中签名内的 `specifications` 可以包含 `val` 声明，类型
定义、异常定义和嵌套 `module type` 定义。喜欢
结构，签名可以写在多行或一行上，并且
允许空签名 `sig end`。

但是，正如我们在模块定义中看到的，语法的更准确版本
将是：

```ocaml
module type ModuleTypeName = module_type
```

其中签名只是 `module_type` 的一种。另一个是名字
已定义的模块类型&mdash;例如，`module type LS = LIST_STACK`。
我们将在本节和本章的后面看到其他模块类型。

按照约定，模块类型名称通常是 `CamelCase`，就像模块名称一样。所以
为什么我们使用上面的 `ALL_CAPS` 作为 `LIST_STACK` ？是为了避免一个可能的情况
这个例子中的混淆点，我们现在对此进行说明。我们可以改为
使用 `ListStack` 作为模块和模块类型的名称：

```ocaml
module type ListStack = sig ... end
module ListStack : ListStack = struct ... end
```

在 OCaml 中，模块和模块类型的命名空间是不同的，所以它是
拥有名为 `ListStack` 的模块和名为 的模块类型是完全有效的
`ListStack`。编译器不会对你的意思感到困惑，因为
它们出现在不同的句法上下文中。但作为一个人你很可能会得到
被那些看似超载的名字搞糊涂了。

```{note}
对模块类型使用 `ALL_CAPS` 一度很常见，你可能
仍然看到它。这是标准机器学习的旧约定。但社会
从那时起，所有大写字母的约定都发生了变化。对于现代读者来说，一个名字
像 `LIST_STACK` 可能会觉得你的代码在无礼地对你大喊大叫。那
是 [evolved in the 1980s][all-caps] 的内涵。较旧的编程
语言（例如 Pascal、COBOL、FORTRAN）通常对关键字使用全部大写
甚至他们自己的名字。现代语言仍然习惯性地使用全部大写
常量 &mdash; 例如 Java 的 `Math.PI`，或者 Python 的
[风格指南][python-caps]。
```

[all-caps]: https://newrepublic.com/article/117390/netiquette-capitalization-how-caps-became-code-yelling

[python-caps]: https://www.python.org/dev/peps/pep-0008/#constants

**更多语法。**

我们现在还应该为模块类型注释添加语法。  模块
定义可以包括可选的类型注释：
```ocaml
module ModuleName : module_type = module_expression
```
并且模块表达式可能包含手动类型注释：
```ocaml
(module_expression : module_type)
```
该语法类似于我们如何编写 `(e : t)` 来手动指定
表达式 `e` 的类型 `t`。

以下是一些示例，展示了如何使用该语法：

```{code-cell} ocaml
:tags: ["hide-output"]
module ListStackAlias : LIST_STACK = ListStack
(* equivalently *)
module ListStackAlias = (ListStack : LIST_STACK)

module M : sig val x : int end = struct let x = 42 end
(* equivalently *)
module M = (struct let x = 42 end : sig val x : int end)
```

并且，模块类型可以包含嵌套模块规范：

```{code-cell} ocaml
:tags: ["hide-output"]
module type X = sig
  val x : int
end

module type T = sig
  module Inner : X
end

module M : T = struct
  module Inner : X = struct
    let x = 42
  end
end
```

在上面的示例中，`T` 指定必须有一个名为
`Inner`，其模块类型为 `X`。这里，类型注释是强制性的，
因为否则我们将无法得知 `Inner` 的情况。在实现 `T` 时，
因此，模块 `M` 必须提供一个具有该名称的模块 (i)，它还 (ii)
符合模块类型`X` 的规格。

**动态语义。**

由于模块类型实际上是类型，因此不会对它们进行评估。他们没有
动态语义。

**静态语义。**

在本节前面，我们推迟讨论模块的静态语义
表达式。现在我们已经了解了模块类型，我们可以回到上面
讨论。  接下来，我们将在其自己的部分中这样做，因为讨论将
冗长。

## 模块类型语义

{{ video_embed | replace("%%VID%%", "VprvFk7KKWk")}}

如果 `M` 只是一个 `struct` 块，则其模块类型是
编译器对其进行推断。但这可以通过模块类型注释来改变。
我们必须回答的关键问题是：类型注释对于模块意味着什么？
也就是说，当我们在`module M : T = ...`中写入`: T`时，意味着什么？

编译器保证两个属性：

  1. *签名匹配：* `T` 中声明的每个名称均在 `M` 中定义
相同或更通用的类型。

  2. *封装*又名*不透明度：* `M` 中定义的任何未出现在 `T` 中的名称都不是
对 `M` 之外的代码可见。

但更完整的答案涉及*子类型化*，这是一个概念
你以前可能见过面向对象语言。我们要采取
现在简要介绍一下该领域，然后回到 OCaml 和模块。

在 Java 中，`extends` 关键字创建类之间的子类型关系：

```java
class C { }
class D extends C { }

D d = new D();
C c = d;
```

子类型允许将 `d` 分配给最后一行的 `c`
示例。因为 `D` 扩展了 `C`，Java 认为 `D` 是 `C` 的子类型，并且
因此允许从 `D` 实例化的对象可以在任何地方使用
预期从 `C` 实例化对象。由 `D` 的程序员决定
当然，确保这不会导致任何运行时错误。 `D` 的方法
例如，必须确保 `C` 的类不变量成立。所以通过写
`D extends C`，程序员承担了一些责任，反过来
通过编写此类赋值语句获得一些灵活性。

那么什么是“亚型”呢？这个概念在很多方面取决于语言。
对于独立于语言的概念，我们求助于芭芭拉·利斯科夫（Barbara Liskov）。她赢得了图灵奖
2008 年获奖的部分原因是她在面向对象语言设计方面的工作。二十
几年前，她发明了现在所谓的*利斯科夫替代法
解释子类型的原理*。它说如果 `S` 是 `T` 的子类型，那么
用 `S` 类型的对象替换 `T` 类型的对象不应改变
程序的任何期望的行为。你可以看到它在 Java 中工作
上面的例子，无论是语言允许的内容还是程序员的内容
必须保证。

Java 中子类型的特殊风格称为*名义子类型*，它
也就是说，它是基于名称的。在我们的示例中，`D` 是 `C` 的子类型
因为名字的宣布方式。程序员决定了该子类型
关系，语言毫无疑问地接受了法令。确实，
*仅*存在的子类型关系是那些已按名称规定的关系
通过这样使用 `extends` 和 `implements`。

现在是时候返回 OCaml 了。它的模块系统也使用子类型，
关于里氏替换原理的基本直觉相同。但是OCaml
使用一种不同的风格，称为“结构子类型”。也就是说，它是基于
模块的结构而不是它们的名称。这里的“结构”只是指
模块中包含的定义。这些定义用于确定
`(M : T)` 是否可以接受作为类型注释，其中 `M` 是一个模块并且
`T` 是一种模块类型。

让我们通过几个例子来探讨这个结构的想法，从
该模块：

```{code-cell} ocaml
module M = struct
  let x = 0
  let z = 2
end
```

模块 `M` 包含两个定义。你可以在签名中看到这些内容
OCaml 输出的模块：它包含 `x : int` 和 `z : int`。  因为
对于前者，接受以下模块类型注释：

```{code-cell} ocaml
module type X = sig
  val x : int
end

module MX = (M : X)
```

模块类型 `X` 需要名为 `x` 且类型为 `int` 的模块项。  模块`M`
确实包含这样的项目。  所以 `(M : X)` 是有效的。  同样的效果
对于 `z`：

```{code-cell} ocaml
module type Z = sig
  val z : int
end

module MZ = (M : Z)
```

或者对于 `x` 和 `z`：

```{code-cell} ocaml
module type XZ = sig
  val x : int
  val z : int
end

module MXZ = (M : XZ)
```

但不适用于 `y`，因为 `M` 不包含此类项目：

```{code-cell} ocaml
:tags: ["raises-exception"]
module type Y = sig
  val y : int
end

module MY = (M : Y)
```

仔细查看该错误消息。学习在小内容上阅读此类错误
当示例出现在大量代码中时，它们会对你有所帮助。 OCaml是
比较两个签名，对应于两边的两个表达式
`(M : Y)` 中的冒号。线路

```ocaml
sig val x : int val z : int end
```

是 OCaml 用于 `M` 的签名。由于 `M` 是一个模块，因此
签名只是 `M` 中定义的名称和类型。OCaml
将该签名与 `Y` 进行比较，发现不匹配：

```text
The value `y' is required but not provided
```

这是因为 `Y` 需要 `y` 但 `M` 没有提供这样的定义。

这是另一个用于练习阅读的错误消息：

```{code-cell} ocaml
:tags: ["raises-exception"]
module type Xstring = sig
  val x : string
end

module MXstring = (M : Xstring)
```

这次的错误是

```text
Values do not match: val x : int is not included in val x : string
```

错误发生了变化，因为 `M` 确实提供了 `x` 的定义，但是在
与 `Xstring` 所需的类型不同。这就是“不包含在”的意思
在这里。那么为什么 OCaml 不说一些更直接的话，比如“是
不一样”？这是因为类型不必完全相同。如果
提供的值的类型是多态的，它足以满足所需值的
类型是该多态类型的实例化。

例如，如果签名需要类型 `int -> int`，则它足以满足
提供 `'a -> 'a` 类型值的结构：

```{code-cell} ocaml
:tags: ["raises-exception"]
module type IntFun = sig
  val f : int -> int
end

module IdFun = struct
  let f x = x
end

module Iid = (IdFun : IntFun)
```

到目前为止，所有这些例子只是比较定义的问题
结构提供的定义的签名所需要的。但这里是
一个可能令人惊讶的例子：

```{code-cell} ocaml
:tags: ["raises-exception"]
module MXZ' = ((M : X) : Z)
```

为什么 OCaml 抱怨 `z` 是必需的但未提供？我们从
`M` 的定义表明它确实有一个值 `z : int`。  然而
错误消息可能奇怪地声称：

```text
The value `z' is required but not provided.
```

出现此错误的原因是我们已经提供了类型注释
模块表达式 `(M : X)` 中的 `X`。  这会导致模块表达式
仅在模块类型 `X` 处可见。  换句话说，我们忘记了
该注释之后不可撤销地存在 `z` 。  所有这一切都是
已知该模块具有 `X` 所需的项目。

在所有这些示例之后，以下是模块类型的静态语义
注释：

- 如果 `M` 的模块类型是 a，则模块类型注释 `(M : T)` 有效
`T` 的子类型。 `(M : T)` 的模块类型在任何其他类型中都是 `T`
  检查。

- 如果 `S` 中的定义集是一个，则模块类型 `S` 是 `T` 的子类型
`T` 中的超集。  允许实例化 `T` 中的定义
  类型来自 `S` 的变量。

第二条规则中的“sub”与“super”不是拼写错误。考虑这些模块
类型和模块：

```{code-cell} ocaml
module type T = sig
  val a : int
end

module type S = sig
  val a : int
  val b : bool
end

module A = struct
  let a = 0
end

module AB = struct
  let a = 0
  let b = true
end

module AC = struct
  let a = 0
  let c = 'c'
end
```

模块类型 `S` 提供了 `T` 中定义的*超*集，因为它添加了
`b` 的定义。那么为什么 `S` 被称为 `T` 的*子*类型呢？想想
设置所有模块值 `M` 的 $\mathit{Type}(T)$，使得 `M : T`。那一套
包含 `A`、`AB`、`AC` 等。再考虑集合
所有模块值 `M` 的 $\mathit{Type}(S)$ 使得 `M : S`。该集合包含
`AB` 但不是 `A` 也不是 `AC`。所以$\mathit{Type}(S) \subset \mathit{Type}(T)$，
因为有一些模块值在 $\mathit{Type}(T)$ 中但不在
$\mathit{Type}(S)$。

作为另一个例子，堆栈的模块类型 `StackHistory` 可能会自定义我们的
通常的 `Stack` 签名通过添加操作 `history : 'a t -> int` 来返回
历史上曾有多少项被推入堆栈。那个`history`
操作使 `StackHistory` 中的定义集大于
`Stack`，因此在上面的规则中使用“超集”。但是模块的集合
实现 `StackHistory` 的值小于模块值集
实现 `Stack`，因此使用“子集”。

## 模块类型是静态的

关于模块类型注释有效性的决定是在编译时做出的
而不是运行时。

```{important}
因此，模块类型注释给程序员带来了潜在的困惑
习惯于面向对象语言，其中子类型的工作方式有所不同。
```

例如，Python 程序员就习惯于所谓的“鸭子打字”。他们
可能期望 `((M : X) : Z)` 有效，因为 `z` 在运行时确实存在
`M`。但在 OCaml 中，`(M : X)` 的编译时类型在视图中隐藏了 `z`
不可撤销地。

另一方面，Java 程序员可能期望模块类型注释
像类型转换一样工作。因此，首先将 `M` “转换”为 `X` 然后再“转换”似乎是有效的
`Z`。在 Java 中，此类类型转换会根据需要在运行时进行检查。但是OCaml
模块类型注释是静态的。一旦做了 `X` 的注释，就有
无法在编译时检查文件中可能存在哪些其他项目
module&mdash; 需要运行时检查，而 OCaml 不允许这样做。

在这两种情况下，你可能会感觉 OCaml 限制过于严格。或许。但是
作为这种限制的回报，OCaml 保证**不存在
Java 或 Python 中可能发生的运行时错误**，无论是
由于强制转换导致的运行时错误，或者由于缺失而导致的运行时错误
方法。

## 一等模块

在 OCaml 中，模块不像函数那样一流。但有可能
*打包*模块作为一流的价值。简而言之：

- `(module M : T)` 将模块类型为 `T` 的模块 `M` 打包为一个值。
- `(val e : T)` 将 `e` 解包到类型为 `T` 的模块中。

我们不会进一步介绍这一点，但如果你好奇，可以看看
[手册][firstclassmodules]。

[firstclassmodules]: https://ocaml.org/manual/firstclassmodules.html
