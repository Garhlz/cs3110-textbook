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

# 封装

模块系统的主要关注点之一是提供*封装*：
将有关实现的信息隐藏在接口后面。 OCaml的模块
系统通过我们已经见过的功能使这成为可能：*不透明度*
模块类型注释创建。不透明度的一种特殊用途是声明
*抽象类型*。我们将在本节中研究这两个想法。

## 不透明度

实现模块时，你有时可能会使用辅助函数
不想暴露给模块的客户端。  例如，也许你是
实现提供尾递归阶乘函数的数学模块：

```{code-cell} ocaml
module Math = struct
  (** [fact_aux n acc] is [n! * acc]. *)
  let rec fact_aux n acc =
    if n = 0 then acc else fact_aux (n - 1) (n * acc)

  (** [fact n] is [n!]. *)
  let fact n = fact_aux n 1
end
```

你想让 `fact` 可供 `Math` 的客户使用，但你还希望
保持 `fact_aux` 隐藏。但在上面的代码中，你可以看到 `fact_aux` 是
在为 `Math` 推断的签名中可见。隐藏它的一种方法就是简单地
巢`fact_aux`：

```{code-cell} ocaml
module Math = struct
  (** [fact n] is [n!]. *)
  let fact n =
    (** [fact_aux n acc] is [n! * acc]. *)
    let rec fact_aux n acc =
      if n = 0 then acc else fact_aux (n - 1) (n * acc)
    in
    fact_aux n 1
end
```

查看签名，注意 `fact_aux` 是如何消失的。但是，那个筑巢
使得 `fact` 有点难以阅读。这也意味着 `fact_aux` 不是
可供任何其他函数*内部* `Math` 使用。在这种情况下就是
可能很好&mdash;`Math`中可能没有任何其他函数
需要 `fact_aux`。但如果有的话，我们就无法嵌套`fact_aux`。

因此，还有另一种方法可以对 `Math` 的客户隐藏 `fact_aux` ，同时仍然保留它
对于 `Math` 的实现者可用，是使用仅公开的模块类型
客户应该看到的那些名称：

```{code-cell} ocaml
module type MATH = sig
  (** [fact n] is [n!]. *)
  val fact : int -> int
end

module Math : MATH = struct
  (** [fact_aux n acc] is [n! * acc]. *)
  let rec fact_aux n acc =
    if n = 0 then acc else fact_aux (n - 1) (n * acc)

  let fact n = fact_aux n 1
end
```

现在由于 `MATH` 没有提到 `fact_aux`，模块类型注释
`Math : MATH` 导致 `fact_aux` 被隐藏：

```{code-cell} ocaml
:tags: ["raises-exception"]
Math.fact_aux
```

从这个意义上说，模块类型注释是*不透明的*：它们可以防止可见性
模块项目。我们说模块类型“密封”了模块，使得任何
模块类型中未命名的组件将无法访问。

```{important}
请记住，模块类型注释因此不仅仅*用于检查
查看模块是否定义了某些项目。注释还隐藏项目。
```

如果你只想检查定义而不隐藏任何内容怎么办？
然后在模块定义时不要提供注释：

```{code-cell} ocaml
module type MATH = sig
  (** [fact n] is [n!]. *)
  val fact : int -> int
end

module Math = struct
  (** [fact_aux n acc] is [n! * acc]. *)
  let rec fact_aux n acc =
    if n = 0 then acc else fact_aux (n - 1) (n * acc)

  let fact n = fact_aux n 1
end

module MathCheck : MATH = Math
```

现在 `Math.fact_aux` 可见，但 `MathCheck.fact_aux` 不可见：

```{code-cell} ocaml
Math.fact_aux
```

```{code-cell} ocaml
:tags: ["raises-exception"]
MathCheck.fact_aux
```

你甚至不必为“检查”模块命名，因为你可能
从未打算访问它；你可以将其保留为匿名：

```{code-cell} ocaml
module _ : MATH = Math
```

**与可见性修饰符的比较。** OCaml 中密封的使用因此是
类似于使用可见性修饰符，例如 `private` 和 `public`
Java。事实上，思考 Java 类定义的一种方法是它们
同时定义多个签名。

例如，考虑这个 Java 类：
```java
class C {
  private int x;
  public int y;
}
```

OCaml 中的类比是以下模块和类型：

```{code-cell} ocaml
module type C_PUBLIC = sig
  val y : int
end

module CPrivate = struct
  let x = 0
  let y = 0
end

module C : C_PUBLIC = CPrivate
```

通过这些定义，任何使用 `C` 的代码都只能访问
`C_PUBLIC` 模块类型中公开的名称。

这个类比可以扩展到其他可见性修饰符 `protected` 和
默认的，也是如此。这意味着 Java 类有效地定义了四个
相关类型，并且编译器确保每个都使用正确的类型
代码库中的位置 `C` 被命名。难怪它很难掌握
首先是面向对象语言的可见性。

## 抽象类型

{{ video_embed | replace("%%VID%%", "vuKBUhMpr-c")}}

在前面的部分中，我们将堆栈实现为具有以下列表的列表
模块和类型：

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

module ListStack : LIST_STACK = struct
  exception Empty
  let empty = []
  let is_empty = function [] -> true | _ -> false
  let push x s = x :: s
  let peek = function [] -> raise Empty | x :: _ -> x
  let pop = function [] -> raise Empty | _ :: s -> s
end
```

如果我们想修改该数据结构以添加操作怎么办
堆栈的大小？  最简单的方法是使用
`List.length`：

```ocaml
module type LIST_STACK = sig
  ...
  (** [size s] is the number of elements on the stack. *)
  val size : 'a list -> int
end

module ListStack : LIST_STACK = struct
  ...
  let size = List.length
end
```

这导致 `size` 的线性时间实现。如果我们想要一个
更快、常数时间的实现？以一点空间为代价，我们可以
缓存堆栈的大小。现在让我们将堆栈表示为一对，其中
该对的第一个组件与之前的列表相同，第二个组件
该对的大小是堆栈的大小：

```{code-cell} ocaml
:tags: ["hide-output"]
module ListStackCachedSize = struct
  exception Empty
  let empty = ([], 0)
  let is_empty = function ([], _) -> true | _ -> false
  let push x (stack, size) = (x :: stack, size + 1)
  let peek = function ([], _) -> raise Empty | (x :: _, _) -> x
  let pop = function
    | ([], _) -> raise Empty
    | (_ :: stack, size) -> (stack, size - 1)
end
```

我们有一个大问题。  `ListStackCachedSize` 没有实现
`LIST_STACK` 模块类型，因为该模块类型指定 `'a list`
整个它代表堆栈&mdash;而不是`'a list * int`。

```{code-cell} ocaml
:tags: ["raises-exception"]
module CheckListStackCachedSize : LIST_STACK = ListStackCachedSize
```

此外，我们之前使用 `ListStack` 编写的任何代码现在都必须修改
处理这对，这可能意味着修改模式匹配，函数
类型等。

毫无疑问，正如你在早期的编程课程中了解到的那样，我们面临的问题是
这里遇到的是缺乏封装。我们应该保留这样的类型
对客户端隐藏 `ListStack` 。例如，在 Java 中，我们可能有
写：

```java
class ListStack<T> {
  private List<T> stack;
  private int size;
  ...
}
```

这样 `ListStack` 的客户端就不会知道 `stack` 或 `size`。  事实上，
他们根本无法命名这些字段。  相反，他们会
只需使用 `ListStack` 作为堆栈的类型：

```java
ListStack<Integer> s = new ListStack<>();
s.push(1);
```

那么在 OCaml 中，我们如何才能隐藏堆栈的“表示类型”呢？什么
到目前为止，我们了解了不透明和密封还不够。问题是
类型 `'a list * int` 确实出现在签名中
`ListStackCachedSize`，例如，在 `push` 中：

```{code-cell} ocaml
ListStackCachedSize.push
```

模块类型注释可以隐藏中定义的值之一
`ListStackCachedSize`，例如 `push` 本身，但这并不能解决问题：
我们需要**隐藏类型** `'a list * int` 同时**公开操作**
`push`。因此 OCaml 有一个功能可以做到这一点：*抽象类型*。
让我们看一下此功能的示例。

我们首先修改 `LIST_STACK`，用新类型替换 `'a list`
`'a stack` 无处不在。这里不再重复规范注释，以便
使示例简短一些。当我们这样做时，让我们添加 `size` 操作。

```{code-cell} ocaml
:tags: [hide-output]
module type LIST_STACK = sig
  type 'a stack
  exception Empty
  val empty : 'a stack
  val is_empty : 'a stack -> bool
  val push : 'a -> 'a stack -> 'a stack
  val peek : 'a stack -> 'a
  val pop : 'a stack -> 'a stack
  val size : 'a stack -> int
end
```

请注意 `'a stack` 实际上并未在该签名中定义。我们还没说过
任何关于它是什么的事情。它可能是 `'a list`、或 `'a list * int`、或
`{stack : 'a list; size : int}`，或其他任何东西。这就是它成为
*抽象*类型：我们已经声明了它的名称，但没有指定它的定义。

现在 `ListStackCachedSize` 可以通过添加来实现该模块类型
仅一行代码：结构的第一行，定义
`'a stack`：

```{code-cell} ocaml
module ListStackCachedSize : LIST_STACK = struct
  type 'a stack = 'a list * int
  exception Empty
  let empty = ([], 0)
  let is_empty = function ([], _) -> true | _ -> false
  let push x (stack, size) = (x :: stack, size + 1)
  let peek = function ([], _) -> raise Empty | (x :: _, _) -> x
  let pop = function
    | ([], _) -> raise Empty
    | (_ :: stack, size) -> (stack, size - 1)
  let size = snd
end
```

仔细查看输出：其中没有 `'a list` 出现。在
事实上，只有 `LIST_STACK` 可以。并且 `LIST_STACK` 仅提及 `'a stack`。所以不
人们会知道内部使用了一个列表。 （好吧，他们会知道：
顾名思义。但关键是他们无法利用这一点
因为类型是抽象的。）

同样，我们最初的线性时间 `size` 实现满足
模块类型。  我们只需添加一行来定义 `'a stack`：

```{code-cell} ocaml
module ListStack : LIST_STACK = struct
  type 'a stack = 'a list
  exception Empty
  let empty = []
  let is_empty = function [] -> true | _ -> false
  let push x s = x :: s
  let peek = function [] -> raise Empty | x :: _ -> x
  let pop = function [] -> raise Empty | _ :: s -> s
  let size = List.length
end
```

请注意，省略添加的行会导致错误，就像
我们未能定义 `push` 或任何其他操作
模块类型：

```{code-cell} ocaml
:tags: ["raises-exception"]
module ListStack : LIST_STACK = struct
  (* type 'a stack = 'a list *)
  exception Empty
  let empty = []
  let is_empty = function [] -> true | _ -> false
  let push x s = x :: s
  let peek = function [] -> raise Empty | x :: _ -> x
  let pop = function [] -> raise Empty | _ :: s -> s
  let size = List.length
end
```

这是 `LIST_STACK` 的第三个自定义实现。这个是故意的
过于复杂，部分是为了说明抽象类型如何隐藏
最好不要向客户端透露实现细节：

```{code-cell} ocaml
module CustomStack : LIST_STACK = struct
  type 'a entry = {top : 'a; rest : 'a stack; size : int}
  and 'a stack = S of 'a entry option
  exception Empty
  let empty = S None
  let is_empty = function S None -> true | _ -> false
  let size = function S None -> 0 | S (Some {size}) -> size
  let push x s = S (Some {top = x; rest = s; size = size s + 1})
  let peek = function S None -> raise Empty | S (Some {top}) -> top
  let pop = function S None -> raise Empty | S (Some {rest}) -> rest
end
```

这真的是一个“列表”堆栈吗？它满足模块类型 `LIST_STACK`。但是
经过反思，该模块类型实际上与列表没有任何关系
一旦我们将类型 `'a stack` 抽象化。确实没有必要调用它
`LIST_STACK`。我们最好只使用 `STACK`，因为它可以实现
有或没有 `list` 。那时，我们可以选择 `Stack` 作为它的
name，因为没有名为 `Stack` 的模块，我们已经编写了该模块
对此感到困惑。这避免了代码全大写的样子对我们大喊大叫。

```{code-cell} ocaml
:tags: [hide-output]
module type Stack = sig
  type 'a stack
  exception Empty
  val empty : 'a stack
  val is_empty : 'a stack -> bool
  val push : 'a -> 'a stack -> 'a stack
  val peek : 'a stack -> 'a
  val pop : 'a stack -> 'a stack
  val size : 'a stack -> int
end

module ListStack : Stack = struct
  type 'a stack = 'a list
  exception Empty
  let empty = []
  let is_empty = function [] -> true | _ -> false
  let push x s = x :: s
  let peek = function [] -> raise Empty | x :: _ -> x
  let pop = function [] -> raise Empty | _ :: s -> s
  let size = List.length
end
```

我们还可以进一步改进命名。注意类型
`ListStack.empty` （现在不用担心 `abstr` 部分；我们会来
回到它）：

```{code-cell} ocaml
ListStack.empty
```

这种类型 `'a ListStack.stack` 相当笨重，因为它传达了这个词
“stack”两次：一次在模块名称中，另一次在模块名称中
该模块内的表示类型。在这样的地方，OCaml 程序员
习惯上使用标准名称 `t` 代替较长的表示类型
姓名：

```{code-cell} ocaml
:tags: [hide-output]
module type Stack = sig
  type 'a t
  exception Empty
  val empty : 'a t
  val is_empty : 'a t -> bool
  val push : 'a -> 'a t -> 'a t
  val peek : 'a t -> 'a
  val pop : 'a t -> 'a t
  val size : 'a t -> int
end

module ListStack : Stack = struct
  type 'a t = 'a list
  exception Empty
  let empty = []
  let is_empty = function [] -> true | _ -> false
  let push x s = x :: s
  let peek = function [] -> raise Empty | x :: _ -> x
  let pop = function [] -> raise Empty | _ :: s -> s
  let size = List.length
end

module CustomStack : Stack = struct
  type 'a entry = {top : 'a; rest : 'a t; size : int}
  and 'a t = S of 'a entry option
  exception Empty
  let empty = S None
  let is_empty = function S None -> true | _ -> false
  let size = function S None -> 0 | S (Some {size}) -> size
  let push x s = S (Some {top = x; rest = s; size = size s + 1})
  let peek = function S None -> raise Empty | S (Some {top}) -> top
  let pop = function S None -> raise Empty | S (Some {rest}) -> rest
end
```

现在堆栈的类型更简单：

```{code-cell} ocaml
ListStack.empty;;
CustomStack.empty;;
```

当存在单一表示类型时，这种习惯用法相当常见
数据结构的接口。你会看到它在整个标准中使用
库。

在非正式对话中，我们通常会在发音时不带“点”
t”部分。例如，我们可能会说“alpha ListStack”，只是忽略
`t`&mdash;尽管从技术上讲它必须存在才能成为合法的 OCaml 代码。

最后，抽象类型实际上只是不透明的一种特殊情况。你其实
如果你愿意，可以在签名中公开类型的定义：

```{code-cell} ocaml
module type T = sig
  type t = int
  val x : t
end

module M : T = struct
  type t = int
  let x = 42
end

let a : int = M.x
```

请注意我们如何将 `M.x` 用作 `int`。  这有效是因为
类型 `t` 和 `int` 的相等性已在模块类型中公开。
但如果我们保持 `t` 抽象，相同的用法将会失败：

```{code-cell} ocaml
:tags: ["raises-exception"]
module type T = sig
  type t (* = int *)
  val x : t
end

module M : T = struct
  type t = int
  let x = 42
end

let a : int = M.x
```

我们不允许在 `M` 之外的 `int` 类型上使用 `M.x`，因为它的类型
`M.t` 是抽象的。这是工作中的封装，保留该实现
细节隐藏。

## 美观打印

在上面的一些输出中，我们观察到一些奇怪的事情：顶层打印
`<abstr>` 代替抽象类型值的实际内容：

```{code-cell} ocaml
ListStack.empty;;
ListStack.(empty |> push 1 |> push 2);;
```

回想一下，顶层使用这个尖括号约定来指示
不可打印的价值。我们之前在函数和 `<fun>` 中遇到过这种情况：

```{code-cell} ocaml
fun x -> x
```

一方面，高层的这种行为也是合理的。一次
类型是抽象的，它的实现并不意味着向客户透露。所以
实际上打印出列表 `[]` 或 `[2; 1]` 作为对上述输入的响应
所揭示的内容将超出预期。

另一方面，实现者为客户端提供
查看抽象类型值的友好方式。 Java 程序员，对于
例如，经常会编写 `toString()` 方法，以便可以打印对象
作为终端或 JShell 中的输出。  为了支持这一点，OCaml 顶层
有一个指令 `#install_printer`，它注册一个函数来打印值。
这是它的工作原理。

- 你编写了一个*漂亮的打印*类型的函数
`Format.formatter -> t -> unit`，无论你喜欢什么类型 `t`。我们假设
  例如，你将该函数命名为 `pp`。

- 你在顶层调用 `#install_printer pp` 。

- 从现在开始，只要顶层想要打印它使用的 `t` 类型的值
你的函数 `pp` 可以这样做。

漂亮的打印函数需要接受以下值可能是有意义的
输入 `t` （因为这就是它需要打印的内容）并返回 `unit` （与其他
打印函数即可）。但为什么它需要 `Format.formatter` 参数呢？
这是因为 OCaml 试图提供一个相当强大的函数
此处提供：在非常中间自动换行和缩进
产量大。

考虑此表达式的输出，它创建嵌套列表：

```{code-cell} ocaml
List.init 15 (fun n -> List.init n (Fun.const n))
```

每个内部列表包含数字 `n` 的 `n` 副本。注意如何缩进
和换行有点复杂。所有内部列表均缩进
距左侧边距的空间。已插入换行符以避免
将内部列表拆分为多行。

`Format` 模块提供了此函数，并且 `Format.formatter`
是其中的一个抽象类型。你可以将格式化程序视为一个地方
发送输出（如文件），并在过程中自动格式化。
格式化程序的典型用途是作为函数的参数，例如
`Format.fprintf`，与 `Printf` 一样使用格式说明符。

例如，假设你想要更改字符串的打印方式
toplevel 并将“kupo”添加到每个字符串的末尾。这是可以做的代码
它：

```{code-cell} ocaml
let kupo_pp fmt s = Format.fprintf fmt "%s kupo" s;;
#install_printer kupo_pp;;
```

现在你可以看到顶层在打印时向每个字符串添加了“kupo”，
即使它实际上不是原始字符串的一部分：

```{code-cell} ocaml
let h = "Hello"
let s = String.length h
```

为了避免我们在接下来的内容中对字符串感到困惑
部分，让我们在继续之前卸载那台漂亮的打印机：

```{code-cell} ocaml
#remove_printer kupo_pp;;
```

作为一个更大的例子，让我们为 `ListStack` 添加漂亮的打印：

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
  val pp :
    (Format.formatter -> 'a -> unit) -> Format.formatter -> 'a t -> unit
end
```

首先，请注意，我们必须将 `pp` 公开为模块类型的一部分。
否则它会被封装，因此我们将无法安装它。
其次，请注意 `pp` 的类型现在需要一个额外的第一个参数
类型为 `Format.formatter -> 'a -> unit`。  这本身就是一台漂亮的打印机
对于类型 `'a`，其中 `t` 被参数化。  我们需要这个论证
能够漂亮地打印 `'a` 类型的值。

```{code-cell} ocaml
:tags: ["hide-output"]
module ListStack : Stack = struct
  type 'a t = 'a list
  exception Empty
  let empty = []
  let is_empty = function [] -> true | _ -> false
  let push x s = x :: s
  let peek = function [] -> raise Empty | x :: _ -> x
  let pop = function [] -> raise Empty | _ :: s -> s
  let size = List.length
  let pp pp_val fmt s =
    let open Format in
    let pp_break fmt () = fprintf fmt "@," in
    fprintf fmt "@[<v 0>top of stack";
    if s <> [] then fprintf fmt "@,";
    pp_print_list ~pp_sep:pp_break pp_val fmt s;
    fprintf fmt "@,bottom of stack@]"
end
```

在`ListStack.pp`中，我们使用了`Format`模块的一些高级函数。
函数 `Format.pp_print_list` 负责打印所有元素
堆栈的。代码的其余部分处理缩进和换行符。
结果如下：

```{code-cell} ocaml
#install_printer ListStack.pp
```

```{code-cell} ocaml
ListStack.empty
```

```{code-cell} ocaml
ListStack.(empty |> push 1 |> push 2)
```

有关详细信息，请参阅 [toplevel 手册][toplevel]（搜索
`#install_printer`)，[Format module][format]，还有这个
[OCaml GitHub issue][poly-printer]。后者似乎是唯一的地方
记录了额外参数的使用，如上面的 `pp_val` 中，以打印值
多态类型。

[toplevel]: https://ocaml.org/manual/toplevel.html
[format]: https://ocaml.org/api/Format.html
[poly-printer]: https://github.com/ocaml/ocaml/issues/5958
