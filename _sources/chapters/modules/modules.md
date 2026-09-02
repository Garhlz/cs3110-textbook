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

在深入细节之前，我们先来看几个 OCaml 模块系统的例子。

*结构*只是定义的集合，例如：

```ocaml
struct
  let inc x = x + 1
  type primary_color = Red | Green | Blue
  exception Oops
end
```

从某种角度看，结构很像记录：二者都包含若干各有名称的组成部分。不过，结构还能定义新的类型、异常等内容，这是记录做不到的。

上面这段代码本身无法编译，因为结构不像整数或函数那样属于一等值。你不能直接把它输入 utop，也不能把结构传给函数。不过，可以将结构绑定到一个名称：

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

这表示 `MyModule` 已经定义，编译器还推断出它具有冒号右侧所示的*模块类型*。这个模块类型写成一个*签名*（signature）：

```ocaml
sig
  val inc : int -> int
  type primary_color = Red | Green | Blue
  exception Oops
end
```

签名本身是一组*规范*。变体类型和异常的规范就是它们原本的定义，因此 `primary_color` 和 `Oops` 与结构中的写法完全相同。`inc` 的规范则使用 `val` 关键字书写，与我们在顶层定义 `inc` 后看到的输出一致。

```{note}
这里使用“规范”一词可能有些令人困惑，因为许多程序员会把它理解为“描述函数行为的注释”。不过，只要稍微放宽这个概念，把函数的类型也看作其规范的一部分，这里的用法就不难理解了。
```

{{ video_embed | replace("%%VID%%", "8Q-2b7iGvXE")}}

实际模块中的各项定义，通常会比 `MyModule` 这个例子联系得更加紧密。模块常用于实现某种数据结构。下面这个栈模块便以链表作为底层表示：

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
`pop` 的规范也许与你预想的不同：它并不返回栈顶元素，那是 `peek` 的职责。`pop` 返回的是移除栈顶元素之后的栈。
```

然后我们可以使用该模块来操作堆栈：

```{code-cell} ocaml
ListStack.push 2 (ListStack.push 1 ListStack.empty)
```

```{warning}
对于有面向对象语言背景的程序员来说，这里潜伏着一个常见的困惑。人们很容易将 `ListStack` 看作一个可以调用其方法的对象。事实上，`ListStack.push` 隐约看起来就像我们在 `ListStack` 对象上调用 `push` 方法。但实际上并非如此。在面向对象语言中，你可以实例化许多堆栈对象。但在这里，只有一个 `ListStack`。而且它在很大程度上不是一个对象，因为它没有 `this` 或 `self` 关键字的概念来代表接收方法调用的对象。
```

不得不说，这种写法相当冗长。稍后我们会看到几种解决办法，现在先看其中一种：

```{code-cell} ocaml
ListStack.(push 2 (push 1 empty))
```

写成 `ListStack.(e)` 后，`ListStack` 中的所有名称都可以直接在 `e` 中使用，不必反复加上 `ListStack.` 前缀。还可以进一步使用管道运算符：

```{code-cell} ocaml
ListStack.(empty |> push 1 |> push 2)
```

这样一来，代码可以从左到右顺着读，再也不必费力分辨层层括号。

```{warning}
这里还容易产生另一种常见的面向对象式误解：把 `ListStack` 当成用于实例化对象的类。事实并非如此。请注意，上面的代码没有使用 `new` 运算符创建栈，也不存在面向对象意义上的构造函数。
```

模块是比类更基础的概念：它只是在自己的命名空间中收集一组定义。在 `ListStack` 中，这组定义包括 `push`、`pop` 等函数，以及值 `empty`。

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

`module` 定义与我们之前学过的 `let` 定义非常相似。（OCaml 的设计者原本也可以选择使用
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

结构也可以写在一行内，各项之间可以加上 `;;` 以提高可读性：

```{code-cell} ocaml
module N = struct let x = 0 let y = 1 end
module O = struct let x = 0;; let y = 1 end
```

允许使用空结构：

```{code-cell} ocaml
module E = struct end
```

**动态语义。**

我们已经知道，表达式会求值为值。同样，模块表达式会求值为*模块值*，简称“模块”。目前需要从求值角度考察的模块表达式只有结构。结构的求值规则很简单：按照各项定义出现的顺序逐一求值。因此，后面的定义可以引用前面的定义，反过来却不行。所以下面的模块没有问题：

```{code-cell} ocaml
module M = struct
  let x = 0
  let y = x
end
```

下面这个模块却不合法，因为对 `x` 的 `let` 定义求值时，`y` 尚未绑定：

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

只要结构中的每项定义按照我们已经学过的类型规则都是良类型的，整个结构就是良类型的。

正如顶层输出所示，结构的模块类型是签名。不过，模块类型还有更多内容。我们暂且把它放在一边，先来讨论作用域。

## 作用域和 Open

{{ video_embed | replace("%%VID%%", "GjlKfsY2nY8")}}

定义模块 `M` 后，可以用点运算符访问其中的名称。例如：

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
[String 模块][string]中的名称引入当前作用域，效果类似于
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
有一个会自动打开的[特殊模块 `Stdlib`][stdlib]
在每个 OCaml 程序中。它包含"内置"函数和运算符。你
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
已经定义的模块类型，例如 `module type LS = LIST_STACK`。
我们将在本节和本章的后面看到其他模块类型。

按照惯例，模块类型名与模块名一样，通常采用 `CamelCase`。那么上面为什么把 `LIST_STACK` 写成 `ALL_CAPS` 呢？这是为了避免一个容易引起混淆的情况。我们其实可以让模块和模块类型都叫作 `ListStack`：

```ocaml
module type ListStack = sig ... end
module ListStack : ListStack = struct ... end
```

OCaml 为模块和模块类型设置了不同的命名空间，因此二者同名完全合法。它们出现在不同的语法位置，编译器不会混淆；人类读者却很容易被这种看似一名多用的写法绕晕。

```{note}
过去常用 `ALL_CAPS` 命名模块类型，如今偶尔仍能见到。这是 Standard ML 留下的旧惯例。不过，全大写在社会语境中的含义后来发生了变化；对现代读者而言，`LIST_STACK` 仿佛是代码在冲人大喊大叫。这种含义在 20 世纪 80 年代逐渐形成。Pascal、COBOL、FORTRAN 等较早的语言常把关键字乃至语言名称本身写成全大写；现代语言则通常只用全大写表示常量，例如 Java 的 `Math.PI`，Python 的[风格指南][python-caps]也采用这一惯例。
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

模块类型就是类型，不参与求值，因此没有动态语义。

**静态语义。**

在本节前面，我们推迟讨论模块的静态语义
表达式。现在我们已经了解了模块类型，我们可以回到上面
讨论。  接下来，我们将在其自己的部分中这样做，因为讨论将
冗长。

## 模块类型语义

{{ video_embed | replace("%%VID%%", "VprvFk7KKWk")}}

如果 `M` 只是一个 `struct` 块，它的模块类型由编译器推断。不过，模块类型标注可以改变这一点。关键问题是：类型标注对模块究竟意味着什么？也就是说，在 `module M : T = ...` 中写下 `: T` 会产生什么效果？

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

那么，“子类型”究竟是什么？具体定义在很大程度上取决于语言，但我们可以借助 Barbara Liskov 提出的一条通用原则来理解。她因在面向对象语言设计等方面的贡献获得了 2008 年图灵奖。早在二十多年前，她便提出了如今所谓的*里氏替换原则*：如果 `S` 是 `T` 的子类型，那么用 `S` 类型的对象替换 `T` 类型的对象，不应改变程序的任何预期行为。上面的 Java 例子同时体现了语言允许做什么，以及程序员必须保证什么。

Java 采用的方式称为*名义子类型*，也就是根据名称和显式声明确定子类型关系。在上例中，`D` 之所以是 `C` 的子类型，是因为程序员如此声明，语言则直接接受这项声明。事实上，Java 中只有通过 `extends`、`implements` 等方式明确指定的子类型关系才算成立。

现在回到 OCaml。它的模块系统同样使用子类型，也遵循里氏替换原则背后的直觉，但采用的是另一种方式：*结构子类型*。顾名思义，子类型关系取决于模块的结构，而不是模块的名称。这里的“结构”就是模块所包含的各项定义。编译器依据这些定义，判断模块 `M` 能否接受模块类型 `T` 的标注 `(M : T)`。

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

请仔细阅读这条错误信息。先在小例子中学会理解这类信息，日后它们出现在大段代码中时便会很有帮助。OCaml 正在比较 `(M : Y)` 中冒号两侧的表达式所对应的两个签名。其中

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
与 `Xstring` 所需的类型不同。这就是"不包含在"的意思
在这里。那么为什么 OCaml 不说一些更直接的话，比如"是
不一样"？这是因为类型不必完全相同。如果
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

第二条规则中的“子”与“超”并没有写反。请看下面这些模块类型和模块：

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
`Stack`，因此在上面的规则中使用"超集"。但是模块的集合
实现 `StackHistory` 的值小于模块值集
实现 `Stack`，因此使用"子集"。

## 模块类型是静态的

模块类型标注是否有效，在编译时就会确定，而不是留到运行时判断。

```{important}
因此，模块类型注释给程序员带来了潜在的困惑
习惯于面向对象语言，其中子类型的工作方式有所不同。
```

例如，Python 程序员习惯了所谓的“鸭子类型”，可能会认为 `((M : X) : Z)` 应该有效，因为运行时的 `M` 确实含有 `z`。但在 OCaml 中，`(M : X)` 的编译时类型已经不可逆地隐藏了 `z`。

另一方面，Java 程序员可能以为模块类型标注会像类型转换一样工作，于是觉得先把 `M`“转换”为 `X`，再“转换”为 `Z` 应该可行。在 Java 中，这类转换会在需要时接受运行时检查；OCaml 的模块类型标注却是静态的。一旦标注为 `X`，编译器便无法再确认模块中可能还存在哪些成员；要恢复这些信息就得进行运行时检查，而 OCaml 不允许这样做。

在这两种情况下，你都可能觉得 OCaml 限制过严。也许确实如此，但作为回报，OCaml 保证**不会出现 Java 或 Python 中可能发生的这类运行时错误**，无论错误源于类型转换失败，还是缺少方法。

## 一等模块

在 OCaml 中，模块不像函数那样是一等值，不过可以把模块*打包*成一等值。简而言之：

- `(module M : T)` 将模块类型为 `T` 的模块 `M` 打包为一个值。
- `(val e : T)` 将 `e` 解包到类型为 `T` 的模块中。

我们不会进一步介绍这一点，但如果你好奇，可以看看
[手册][firstclassmodules]。

[firstclassmodules]: https://ocaml.org/manual/firstclassmodules.html
