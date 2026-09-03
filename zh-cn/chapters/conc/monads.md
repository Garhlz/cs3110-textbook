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

# 单子

*单子*（monad）与其说是一种数据结构，不如说是一种设计模式。许多数据结构只要换一个恰当的角度来看，都可以理解成单子。

“monad”一词来自数学中的范畴论，这个领域研究数学结构的抽象。若攻读编程语言理论方向的博士学位，你或许会深入接触这一概念；本书则略去大部分数学理论，把注意力放在代码上。

单子因 Haskell 而广为人知。Haskell 是一门比 OCaml 更纯粹的函数式语言，会更严格地避免副作用和命令式特性。然而，实用语言不可能彻底没有副作用——向屏幕打印本身就是副作用。因此，Haskell 使用单子模式来控制副作用。此后，单子也被其他函数式语言广泛采用，甚至开始出现在命令式语言中。

单子用于对*计算*建模。可以把计算看作一种函数：它把输入映射为输出，同时还做了“额外的事”。这些额外行为就是求值引发的*效果*，例如向屏幕打印。单子把效果抽象出来，并帮助我们确保它们以受控的顺序发生。

## Monad 签名

就我们的目的而言，单子是满足两个属性的结构。首先，
它必须与以下签名匹配：

```{code-cell} ocaml
:tags: ["hide-output"]
module type Monad = sig
  type 'a t
  val return : 'a -> 'a t
  val bind : 'a t -> ('a -> 'b t) -> 'b t
end
```

其次，单子必须遵守所谓的“单子定律”。等研究过 `return` 和 `bind` 之后，我们会在本章后面回到这些定律。

可以把单子想成装着某个值的盒子：值的类型是 `'a`，盒子的类型则是 `'a t`。此前讲 option 和 Promise 时，我们都用过类似的盒子比喻。这并非偶然，因为二者都是单子，下面会具体说明。

**返回。** `return` 可以形象地理解为把值放进盒子。从类型也能看出：输入类型为 `'a`，输出类型为 `'a t`。

从计算的角度看，`return` 应当只产生最简单的效果。例如，若某个单子表示带打印效果的计算，那么最简单的效果就是什么也不打印。

**绑定。** `bind` 操作隐喻地将其作为输入：

* 一个装箱值，其类型为 `'a t`，并且

* 本身采用 `'a` 类型的*未装箱*值作为输入的函数
返回 `'b t` 类型的 *boxed* 值作为输出。

`bind` 把第二个参数所表示的函数应用于第一个参数：从盒子里取出 `'a` 类型的值，将函数应用于它，再返回结果。

从计算的角度看，`bind` 用于安排效果的先后次序。仍以打印为例，它可以规定先打印一个字符串，再打印另一个，并确保顺序正确。

`bind` 通常写成中缀运算符 `>>=`，读作“bind”。因此，可以把单子签名改写为：

```{code-cell} ocaml
:tags: ["hide-output"]
module type Monad = sig
  type 'a t
  val return : 'a -> 'a t
  val ( >>= ) : 'a t -> ('a -> 'b t) -> 'b t
end
```

初读这些内容时，难免会觉得十分抽象。看几个具体例子会有所帮助；理解若干 `>>=` 和 `return` 的实际用法之后，单子这一设计模式自然会更加清晰。

接下来几节会从不同的代码中辨认单子。单子是一种设计模式，并不总是显而易见；有时需要仔细分析，才能看出单子操作究竟藏在哪里。

## Maybe Monad

正如之前所见，有些函数是偏函数：对某些输入没有合理的输出。例如，`max_list : int list -> int` 面对空列表时就没有合适的返回值。我们可以抛出异常，也可以把返回类型改成 `int option`，用 `None` 表示无法产生结果。换言之，函数“也许”返回结果，也许不能；这正是 Maybe 单子名称的由来。

另一个例子，考虑内置的 OCaml 整数除法函数
`( / ) : int -> int -> int`。如果它的第二个参数为零，它会引发一个
例外。不过，另一种可能性是将其类型更改为
`( / ) : int -> int -> int option`，只要除数为 `None` 就返回 `None`
零。

这两个示例都涉及更改部分函数的输出类型
成为一个选项，从而使函数完整。这是一种很好的编程方式
直到你开始尝试将许多函数组合在一起。例如，因为
所有整数运算——加法、减法、除法、乘法、取负等——都接收一个或两个 `int` 作为输入，因此可以
用它们组成大的表达式。但是一旦你改变了输出类型
除法成为一种选择，你就失去了*组合性*。

下面是一些使这个想法具体化的代码：

```{code-cell} ocaml
(* works fine *)
let x = 1 + (4 / 2)
```

```{code-cell} ocaml
:tags: ["raises-exception"]
let div (x:int) (y:int) : int option =
  if y = 0 then None else Some (x / y)

let ( / ) = div

(* won't type check *)
let x = 1 + (4 / 2)
```

问题是我们不能将 `int` 添加到 `int option` 中：
运算符期望其第二个输入的类型为 `int`，但新的除法
运算符返回 `int option` 类型的值。

一种可能性是将所有现有运算符重新编码为
接受 `int option` 作为输入。  例如，

```{code-cell} ocaml
:tags: ["hide-output"]
let plus_opt (x:int option) (y:int option) : int option =
  match x,y with
  | None, _ | _, None -> None
  | Some a, Some b -> Some (Stdlib.( + ) a b)

let ( + ) = plus_opt

let minus_opt (x:int option) (y:int option) : int option =
  match x,y with
  | None, _ | _, None -> None
  | Some a, Some b -> Some (Stdlib.( - ) a b)

let ( - ) = minus_opt

let mult_opt (x:int option) (y:int option) : int option =
  match x,y with
  | None, _ | _, None -> None
  | Some a, Some b -> Some (Stdlib.( * ) a b)

let ( * ) = mult_opt

let div_opt (x:int option) (y:int option) : int option =
  match x,y with
  | None, _ | _, None -> None
  | Some a, Some b ->
    if b=0 then None else Some (Stdlib.( / ) a b)

let ( / ) = div_opt
```

```{code-cell} ocaml
(* does type check *)
let x = Some 1 + (Some 4 / Some 2)
```

但这是大量的代码重复。我们应该应用
抽象原则和重复数据删除。四个运算符中的三个可以是
通过抽象一个只进行一些模式匹配的函数来处理
传播 `None`：

```{code-cell} ocaml
let propagate_none (op : int -> int -> int) (x : int option) (y : int option) =
  match x, y with
  | None, _ | _, None -> None
  | Some a, Some b -> Some (op a b)

let ( + ) = propagate_none Stdlib.( + )
let ( - ) = propagate_none Stdlib.( - )
let ( * ) = propagate_none Stdlib.( * )
```

不幸的是，除法更难消除重复。我们不能就这么过去
`Stdlib.( / )` 到 `propagate_none`，因为这些函数都不会
检查除数是否为零。如果我们能够通过我们的
函数 `div : int -> int -> int option` 到 `propagate_none`，但返回
`div` 的类型使得这是不可能的。

因此，让我们重写 `propagate_none` 以接受与以下类型相同的运算符
`div`，这使得很容易实现除法：

```{code-cell} ocaml
let propagate_none
  (op : int -> int -> int option) (x : int option) (y : int option)
=
  match x, y with
  | None, _ | _, None -> None
  | Some a, Some b -> op a b

let ( / ) = propagate_none div
```

实现其他三个操作需要更多的工作，因为
它们的返回类型是 `int` 而不是 `int option`。我们需要包装它们的返回值
与 `Some`:

```{code-cell} ocaml
let wrap_output (op : int -> int -> int) (x : int) (y : int) : int option =
  Some (op x y)

let ( + ) = propagate_none (wrap_output Stdlib.( + ))
let ( - ) = propagate_none (wrap_output Stdlib.( - ))
let ( * ) = propagate_none (wrap_output Stdlib.( * ))
```

最后，我们可以重新实现 `div` 以使用 `wrap_output`：

```{code-cell} ocaml
let div (x : int) (y : int) : int option =
  if y = 0 then None else wrap_output Stdlib.( / ) x y

let ( / ) = propagate_none div
```

**单子在哪里？** 我们刚才把作用于整数并返回整数的函数，提升成了可能返回整数、也可能没有结果的函数：返回值要么是 `Some i`，其中 `i` 为整数；要么是 `None`。可以把这些提升后的函数看成具有“可能不产生结果”这一效果的计算。它们返回一个比喻意义上的盒子，盒子里可能有值，也可能是空的。

刚才的代码包含两个基本思想，分别对应单子的 `return` 和 `bind` 操作。

第一个思想看似简单：用 `Some` 包装一个 `int`，把它提升为 `int option`。`wrap_output` 的函数体做的正是这件事。单独定义下面的函数，可以把这个思想表达得更清楚：

```{code-cell} ocaml
let return (x : int) : int option = Some x
```
这个函数只产生一种最简单的效果：把值放入比喻中的盒子。

第二个想法是分解代码来处理所有模式匹配
反对`None`。我们必须将输入类型为 `int` 的函数升级为
相反，接受 `int option` 类型的输入。这是这个想法表达为
自己的函数：

```{code-cell} ocaml
let bind (x : int option) (op : int -> int option) : int option =
  match x with
  | None -> None
  | Some a -> op a

let ( >>= ) = bind
```

`bind`函数可以理解为做升级`op`的核心工作
从接受 `int` 作为输入的函数到接受
`int option` 作为输入。事实上，我们甚至可以编写一个函数来做到这一点
使用 `bind` 为我们升级：

```{code-cell} ocaml
let upgrade : (int -> int option) -> (int option -> int option) =
  fun (op : int -> int option) (x : int option) -> (x >>= op)
```

所有这些类型注释都是为了帮助读者理解
的函数。  当然，还可以更简单地写成：

```{code-cell} ocaml
let upgrade op x = x >>= op
```

仅使用 `return` 和 `>>=` 函数，我们可以重新实现
上面的算术运算：

```{code-cell} ocaml
let ( + ) (x : int option) (y : int option) : int option =
  x >>= fun a ->
  y >>= fun b ->
  return (Stdlib.( + ) a b)

let ( - ) (x : int option) (y : int option) : int option =
  x >>= fun a ->
  y >>= fun b ->
  return (Stdlib.( - ) a b)

let ( * ) (x : int option) (y : int option) : int option =
  x >>= fun a ->
  y >>= fun b ->
  return (Stdlib.( * ) a b)

let ( / ) (x : int option) (y : int option) : int option =
  x >>= fun a ->
  y >>= fun b ->
  if b = 0 then None else return (Stdlib.( / ) a b)
```

回想一下，根据我们对 Lwt 中绑定运算符的讨论，上面的语法
应该被你的眼睛解析为

* 获取 `x` 并从中提取值 `a`，
* 然后取出 `y` 并从中提取 `b`，
* 然后使用 `a` 和 `b` 构造返回值。

当然，那里仍然存在相当多的重复。我们可以
使用与我们之前相同的技术来消除重复：

```{code-cell} ocaml
let upgrade_binary op x y =
  x >>= fun a ->
  y >>= fun b ->
  op a b

let return_binary op x y = return (op x y)

let ( + ) = upgrade_binary (return_binary Stdlib.( + ))
let ( - ) = upgrade_binary (return_binary Stdlib.( - ))
let ( * ) = upgrade_binary (return_binary Stdlib.( * ))
let ( / ) = upgrade_binary div
```

**Maybe 单子。** 刚才得到的单子有几个名字：*Maybe 单子*，因为它也许有值、也许没有；*错误单子*，因为 `None` 表示发生了错误（不过有些作者认为错误单子应当保留不同错误的信息，而不是全都归结为 `None`）；以及含义最直白的 *option 单子*。

下面是 Maybe 单子对单子签名的实现：

```{code-cell} ocaml
module Maybe : Monad = struct
  type 'a t = 'a option

  let return x = Some x

  let (>>=) m f =
    match m with
    | None -> None
    | Some x -> f x
end
```

这里的 `return` 和 `>>=` 与上面得到的实现相同，只是去掉了将它们限制为整数的类型标注。那些标注本来就不是必需的，只是让此前的推导更清晰。

这里的 `return` 非常简单，甚至并非真正必需；`>>=` 却能消除大量重复的模式匹配。最终的算术运算实现只在 `>>=` 内部匹配一次，而最初的 `plus_opt` 等函数处处都要重复匹配。

结果是我们得到的代码（一旦你了解如何读取绑定
运算符）更易于阅读且易于维护。

现在我们已经完成了整数运算符的操作，我们应该恢复
该文件其余部分的原始含义：

```{code-cell} ocaml
let ( + ) = Stdlib.( + )
let ( - ) = Stdlib.( - )
let ( * ) = Stdlib.( * )
let ( / ) = Stdlib.( / )
```

## 示例：Writer Monad

当尝试诊断系统中的故障时，通常会出现以下情况：*log*
调用了哪些函数，以及它们的输入和输出是什么，
会有帮助的。

想象一下，我们有两个想要调试的函数，它们的类型都是 `int -> int`。
例如：

```{code-cell} ocaml
let inc x = x + 1
let dec x = x - 1
```

（好吧，这些都是非常简单的函数；我们可能不需要任何帮助
调试它们。但想象一下他们计算的东西要复杂得多，比如
整数的加密或解密。）

保留函数调用日志的一种方法是将每个函数扩充为
返回一对：函数通常返回的整数值，以及
包含日志消息的字符串。例如：

```{code-cell} ocaml
let inc_log x = (x + 1, Printf.sprintf "Called inc on %i; " x)
let dec_log x = (x - 1, Printf.sprintf "Called dec on %i; " x)
```

但这改变了两个函数的返回类型，这使得很难
*组合*函数。以前，我们可以编写如下代码

```{code-cell} ocaml
let id x = dec (inc x)
```

甚至更好

```{code-cell} ocaml
let id x = x |> inc |> dec
```

或者更好的是，使用*组合运算符* `>>`，

```{code-cell} ocaml
let ( >> ) f g x = x |> f |> g
let id = inc >> dec
```

这样就可以了。但尝试用做同样的事情
函数的可记录版本会产生类型检查错误：

```{code-cell} ocaml
:tags: ["raises-exception"]
let id = inc_log >> dec_log
```

这是因为 `inc_log x` 是一对，但 `dec_log` 只期望一个
整数作为输入。

我们可以编写 `dec_log` 的升级版本，它能够将一对作为
输入：

```{code-cell} ocaml
let dec_log_upgraded (x, s) =
  (x - 1, Printf.sprintf "%s; Called dec on %i; " s x)

let id x = x |> inc_log |> dec_log_upgraded
```

这工作得很好，但我们还需要编写一个类似的升级版本
`f_log` 如果我们想以相反的顺序调用它们，例如，
`let id = dec_log >> inc_log`。所以我们必须写：

```{code-cell} ocaml
let inc_log_upgraded (x, s) =
  (x + 1, Printf.sprintf "%s; Called inc on %i; " s x)

let id = dec_log >> inc_log_upgraded
```

此时我们已经重复了太多代码。实现
`inc` 和 `dec` 在 `inc_log` 和 `dec_log` 中重复，并且
里面有两个升级版本的函数。而且这两个升级都是重复的
用于将日志消息连接在一起的代码。我们想要的函数越多
使可记录，这种重复会变得更糟糕！

因此，让我们重新开始，并分解出几个辅助函数。第一个帮手
调用函数并生成日志消息：

```{code-cell} ocaml
let log (name : string) (f : int -> int) : int -> int * string =
  fun x -> (f x, Printf.sprintf "Called %s on %i; " name x)
```
第二个助手生成类型的日志记录函数
`'a * string -> 'b * string` 位于不可记录的函数之外：

```{code-cell} ocaml
let loggable (name : string) (f : int -> int) : int * string -> int * string =
  fun (x, s1) ->
    let (y, s2) = log name f x in
    (y, s1 ^ s2)
```

使用这些助手，我们可以实现函数的日志记录版本
没有任何涉及配对、模式匹配或字符串的重复代码
连接：

```{code-cell} ocaml
let inc' : int * string -> int * string =
  loggable "inc" inc

let dec' : int * string -> int * string =
  loggable "dec" dec

let id' : int * string -> int * string =
  inc' >> dec'
```

这是一个用法示例：

```{code-cell} ocaml
id' (5, "")
```

直接对整数调用带日志的函数很不方便，因为每次都必须手工把整数与字符串配对。下面增加一个辅助函数，将整数与*空*日志配对：

```{code-cell} ocaml
let e x = (x, "")
```

现在我们可以写 `id' (e 5)` 而不是 `id' (5, "")`。

**单子在哪里？** 我们把作用于整数的函数提升成了返回“整数与日志消息”二元组的函数。可以把这些提升后的函数看成会记录日志的计算：它们产生比喻意义上的盒子，其中同时装着函数输出和日志消息。

刚才的代码包含两个基本思想，分别对应单子的 `return` 和 `bind` 操作。

第一个思想是把 `int` 与空字符串配对，将它提升为 `int * string`。这正是 `e` 的作用，因此可以把它改名为 `return`：

```{code-cell} ocaml
let return (x : int) : int * string = (x, "")
```
这个函数产生的效果最为简单：把值与一条空日志一起放入比喻中的盒子。

第二个思想是把配对模式匹配和字符串拼接抽取出来，形成一个独立函数：

```{code-cell} ocaml
let ( >>= ) (m : int * string) (f : int -> int * string) : int * string =
  let (x, s1) = m in
  let (y, s2) = f x in
  (y, s1 ^ s2)
```

使用 `>>=`，我们可以重新实现 `loggable`，这样就不会出现配对
或模式匹配曾经在其主体中使用过：

```{code-cell} ocaml
let loggable (name : string) (f : int -> int) : int * string -> int * string =
  fun m ->
    m >>= fun x ->
    log name f x
```

**Writer 单子。** 刚才得到的单子通常称为 *Writer 单子*，因为它会额外写出日志或字符串。下面是它对单子签名的实现：

```{code-cell} ocaml
module Writer : Monad = struct
  type 'a t = 'a * string

  let return x = (x, "")

  let ( >>= ) m f =
    let (x, s1) = m in
    let (y, s2) = f x in
    (y, s1 ^ s2)
end
```

与 Maybe 单子一样，这里的 `return` 和 `>>=` 就是上面推导出的实现，只是去掉了将它们限制为整数的类型标注。那些标注仅用于帮助说明，并非实现所必需。

哪个版本的 `loggable` 更易读，见仁见智；要欣赏使用 `>>=` 的版本，确实需要先适应单子式编程。不过在较大的代码库中，如果许多函数都要处理成对的字符串，`>>=` 会是不错的选择：业务代码可以专注于 `'a Writer.t` 中的 `'a`，不必亲自管理字符串。只要使用 `return` 和 `>>=`，Writer 单子就会替你处理日志。

## 示例：Lwt Monad

到目前为止，很明显我们讨论的 Lwt Promise 库是
也是一个单子。 Promise 的类型 `'a Lwt.t` 有 `return` 和 `bind`
正确类型的操作成为 monad：

```ocaml
val return : 'a -> 'a t
val bind : 'a t -> ('a -> 'b t) -> 'b t
```

并且 `Lwt.Infix.( >>= )` 是 `Lwt.bind` 的同义词，因此该库确实提供
中缀绑定运算符。

现在我们开始看到 monad 设计模式的一些强大能力。
我们之前看到的 `'a t` 和 `return` 的实现涉及创建
引用，但这些引用完全隐藏在 monad 接口背后。此外，我们知道 `bind`
涉及注册回调，但这一机制（正如你可能想象的那样，涉及维护一组回调）
被完全封装了。

打个比方，正如我们之前讨论的，这里涉及的盒子是一个开始的盒子
为空，但最终将被填充为 `'a` 类型的值。
这些计算中的“更多内容”是正在产生值
异步，而不是立即。

## Monad 定律

每个数据结构不仅有一个签名，还有一些预期的行为。对于
例如，堆栈有入栈和出栈操作，我们期望这些操作
以特定的方式行事。例如，如果我们将一个元素压入堆栈，那么
查看堆栈顶部的元素，我们希望看到该元素
我们刚刚推动。

然而，单子不仅仅是一个单一的数据结构。这是一个设计模式
数据结构。因此，我们无法为任意单子写出 `return` 和 `>>=` 的具体行为规范；规范必须针对特定单子，例如 Writer 单子或 Lwt 单子。

另一方面，任何单子都应当满足一些共同规律。这源自我们对单子的一个基本直觉：单子表示带有效果的计算。以 Lwt 为例，可以用 `bind` 在 Promise X 上注册回调 C，由此产生 Promise Y，再在 Y 上注册回调 D。我们期望回调依次运行：C 必须先于 D，因为 Y 不可能先于 X 得到解析。

单子定律规定的内容之一正是这种“顺序”。正式给出定律之前，先回顾命令式语言如何表达顺序。

**顺序。** Java、C 等语言使用分号规定语句的先后顺序，例如：

```java
System.out.println(x);
x++;
System.out.println(x);
```

程序先打印 `x`，再将它递增，最后再次打印；各条语句的效果必须依次发生。

让我们想象一个不会产生任何影响的假设陈述。对于
例如，`assert true` 在 Java 中不会发生任何事情。 （有些编译器会
完全忽略它，甚至不为其生成字节码。）在大多数汇编中
语言中，同样有一个“no op”指令，其助记符通常是
`NOP` 也会导致什么也不会发生。 （从技术上讲，某些时钟周期会
过去。但寄存器或内存不会有任何变化。）理论上
在编程语言中，这样的语句通常称为 `skip`，如：
“跳过我吧，因为我不做任何有趣的事情。”

以下是 `skip` 和分号的两条法则：

* `skip; s;` 的行为应与 `s;` 相同。

* `s; skip;` 的行为应与 `s;` 相同。

换句话说，`skip` 不产生任何效果，可以从任意位置删除。用数学语言说，`skip` 既是分号的*左单位元*（第一条定律），也是*右单位元*（第二条定律）。

命令式语言通常还有一种将语句分组在一起的方法
成块。在 Java 和 C 中，这通常是通过花括号完成的。这是一个
块和分号的法则：

* `{s1; s2;} s3;` 的行为应与 `s1; {s2; s3;}` 相同。

无论把前两条还是后两条语句放进同一个块，执行顺序始终是 `s1`、`s2`、`s3`。因此完全可以去掉花括号，直接写成 `s1; s2; s3;`，通常我们也正是这样做的。用数学语言说，分号满足*结合律*。

**单子定律的顺序。** 上述三个定律正好体现了
与我们现在要阐述的单子定律相同的直觉。单子定律
只是更抽象一些，因此一开始更难理解。

假设有任意一个单子，它照例满足以下签名：

```{code-cell} ocaml
module type Monad = sig
  type 'a t
  val return : 'a -> 'a t
  val ( >>= ) : 'a t -> ('a -> 'b t) -> 'b t
end
```

三个单子定律如下：

* **法则 1：** `return x >>= f` 的行为与 `f x` 相同。

* **法则 2：** `m >>= return` 的行为与 `m` 相同。

* **法则 3：** `(m >>= f) >>= g` 的行为与 `m >>= (fun x -> f x >>= g)` 相同。

这里的“行为相同”是指：两个表达式要么求值得到相同的值，要么都陷入无限循环，要么都引发相同的异常。

这些定律在数学结构上与前面关于 `skip`、分号和花括号的定律相同：`return` 是 `>>=` 的左、右单位元，而 `>>=` 满足结合律。下面逐条细看。

*定律 1* 表明，先对值施加最简单的效果，再绑定函数，等同于直接把函数应用于这个值。对 Maybe 单子而言，`return x` 得到 `Some x`，`>>= f` 随后取出 `x` 并应用 `f`。对 Lwt 单子而言，`return x` 创建一个已经以 `x` 解析的 Promise，`>>= f` 再把 `f` 注册为作用于 `x` 的回调。

*定律 2* 表明，把计算绑定到只产生最简单效果的 `return`，等同于什么也不做。对 Maybe 单子而言，若 `m` 是 `Some x`，绑定会取出 `x`，而 `return` 只会再次用 `Some` 包装它；若 `m` 是 `None`，绑定仍返回 `None`。对 Lwt 而言，把 `m` 绑定到 `return`，只是注册一个回调，将解析出的内容重新放入一个已解析的 Promise。

*定律 3* 表明 `bind` 能正确安排效果的顺序，不过它不像前面带分号和花括号的版本那样一目了然。如果能写成下面这样，结合律会更加清楚：

>`(m >>= f) >>= g` 的行为与 `m >>= (f >>= g)` 相同。

问题在于这段表达式无法通过类型检查：`f >>= g` 的类型不适合放在 `>>=` 右侧。因此必须插入匿名函数 `fun x -> ...`，使类型吻合。

## 组合与 Monad 定律

另一个名为 `compose` 的单子运算符可以组合一元函数。假设有类型构造器 `'a t` 和两个函数：

* `f : 'a -> 'b t`
* `g : 'b -> 'c t`

这些函数的组成将是

* `compose f g : 'a -> 'c t`

也就是说，组合函数接收 `'a` 类型的值，先应用 `f`，从结果中取出 `'b`，再应用 `g` 并返回最终结果。

可以只用 `>>=` 实现 `compose`，无须了解单子的内部机制：

```{code-cell} ocaml
let compose f g x =
  f x >>= fun y ->
  g y

let ( >=> ) = compose
```

正如最后一行所示， `compose` 可以表示为中缀运算符
`>=>`。

回到我们带有安全除法运算符的 Maybe monad 的例子，
假设我们有递增和递减函数：

```{code-cell} ocaml
let inc (x : int) : int option = Some (x + 1)
let dec (x : int) : int option = Some (x - 1)
let ( >>= ) x op =
  match x with
  | None -> None
  | Some a -> op a
```

借助单子组合运算符，无须额外代码就能把二者组合成恒等函数：

```{code-cell} ocaml
let ( >=> ) f g x =
  f x >>= fun y ->
  g y

let id : int -> int option = inc >=> dec
```

使用 compose 运算符，可以把单子定律表述得更加清楚：

* **法则 1：** `return >=> f` 的行为与 `f` 相同。

* **法则 2：** `f >=> return` 的行为与 `f` 相同。

* **法则 3：** `(f >=> g) >=> h` 的行为与 `f >=> (g >=> h)` 相同。

在这种表述中，`return` 显然是左、右单位元，而组合运算满足结合律。
