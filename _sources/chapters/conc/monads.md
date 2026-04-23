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

*monad* 与其说是一种数据结构，不如说是一种设计模式。也就是说，有
许多数据结构，如果你以正确的方式看待它们，就会发现它们是
单子。

“monad”这个名字来自数学领域“范畴论”，
研究数学结构的抽象。如果你曾经攻读博士学位
在编程语言理论课上，你可能会遇到这个想法
更多细节。不过，在这里，我们将省略大部分数学理论和
专注于代码。

Monad 通过在 Haskell（一个
比 OCaml&mdash; 更纯粹的函数式编程语言，即
Haskell 比 OCaml 更能避免副作用和命令式特性。但没有
实用的语言可以做到没有副作用。毕竟，打印到
屏幕是一个副作用。因此 Haskell 着手控制副作用的使用
通过 monad 设计模式。从那时起，单子被认为是
在其他函数式编程语言中很有用，甚至开始
出现在命令式语言中。

Monad 用于建模*计算*。将计算视为
函数，它将输入映射到输出，但也做“更多的事情”。
更重要的是该函数由于存在而产生的效果
计算出来的。例如，效果可能涉及打印到屏幕。单子
提供效果的抽象，并帮助确保效果发生在
受控命令。

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

其次，单子必须遵守所谓的“单子法则”。我们将回到
很久以后，在我们研究了 `return` 和 `bind` 操作之后。

将单子视为一个包含某些值的盒子。该值有
类型为 `'a`，并且包含它的盒子的类型为 `'a t`。我们之前有过
对 option 和 Promise 都使用了类似的盒子隐喻。这并非偶然：
option 和 Promise 都是 monad 的例子，我们将详细看到，
下面。

**返回。** `return` 操作隐喻地将一个值放入一个框中。你
在其类型中可以看到：输入的类型为`'a`，输出的类型为
`'a t`。

在计算方面， `return` 旨在具有某种微不足道的作用
效果。例如，如果 monad 表示其副作用为的计算
打印到屏幕上，最简单的效果就是不打印任何东西。

**绑定。** `bind` 操作隐喻地将其作为输入：

* 一个装箱值，其类型为 `'a t`，并且

* 本身采用 `'a` 类型的*未装箱*值作为输入的函数
返回 `'b t` 类型的 *boxed* 值作为输出。

`bind` 将其第二个参数应用于第一个参数。这需要采取
`'a` 值超出其范围，将函数应用于它，并返回
结果。

在计算方面， `bind` 旨在对效果进行排序
另一个。继续打印的运行示例，排序意味着首先
打印一个字符串，然后打印另一个字符串，并且 `bind` 将确保
打印按正确的顺序进行。

`bind` 的通常表示法是写成 `>>=` 的中缀运算符，并且仍然
发音为“绑定”。因此，让我们修改 monad 的签名：

```{code-cell} ocaml
:tags: ["hide-output"]
module type Monad = sig
  type 'a t
  val return : 'a -> 'a t
  val ( >>= ) : 'a t -> ('a -> 'b t) -> 'b t
end
```

第一次阅读时，以上所有内容可能会感觉非常抽象。它将
帮助查看 monad 的一些具体示例。一旦你理解了几个 `>>=`
和 `return` 操作，设计模式本身应该更有意义。

因此，接下来的几节将介绍几个不同的代码示例，其中
可以发现单子。因为单子是一种设计模式，但它们不是
总是显而易见的；可能需要一些研究才能弄清楚 monad 的操作位置
正在被使用。

## Maybe Monad

正如我们之前所见，有时函数是不完整的：没有好的输出
他们可以生产一些投入。例如，函数
`max_list : int list -> int` 不一定具有良好的输出值
返回空列表。一种可能性是提出例外。另一个
可能性是将返回类型更改为 `int option`，并使用 `None` 来
表示函数无法产生输出。换句话说，*也许*
该函数产生一个输出，或者*也许*它无法这样做，因此返回
`None`。

另一个例子，考虑内置的 OCaml 整数除法函数
`( / ) : int -> int -> int`。如果它的第二个参数为零，它会引发一个
例外。不过，另一种可能性是将其类型更改为
`( / ) : int -> int -> int option`，只要除数为 `None` 就返回 `None`
零。

这两个示例都涉及更改部分函数的输出类型
成为一个选项，从而使函数完整。这是一种很好的编程方式
直到你开始尝试将许多函数组合在一起。例如，因为
所有整数运算&mdash;加法、减法、除法、
乘法、求反等&mdash;期望一个 `int` （或两个）作为输入，你可以
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

**Monad 在哪里？** 我们刚刚所做的工作是对整数进行函数处理
并将它们转换为值的函数，这些值可能是整数，但也可能是
不是 &mdash;，即，值是 `Some i`，其中 `i` 是整数，
或者是 `None`。我们可以将这些“升级”的函数视为计算
*可能会产生什么也不产生的效果*。他们生产隐喻的盒子，并且
这些盒子可能装满了东西，也可能什么也没有。

我们刚才写的代码中有两个基本思想，分别对应
`return` 和 `bind` 的 monad 操作。

第一个（诚然看起来微不足道）是将值从 `int` 升级到
`int option` 通过用 `Some` 包装它。这就是 `wrap_output` 的主体
确实如此。我们可以通过定义以下内容来更清楚地揭示这个想法
函数：

```{code-cell} ocaml
let return (x : int) : int option = Some x
```
该函数具有将值放入隐喻的*微不足道的效果*
盒子。

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

**也许 Monad。** 我们刚刚发现的 monad 有几个名字：
*也许 monad* （如，“也许有一个值，也许没有”），*错误 monad* （如
在“要么有值，要么有错误”中，错误表示为
`None`&mdash;尽管有些作者希望错误单子能够
代表多种错误，而不是仅仅将它们全部折叠到
`None`) 和 *option monad* （这是显而易见的）。

这是 Maybe monad 的 monad 签名的实现：

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

这些与我们上面发明的 `return` 和 `>>=` 的实现相同，
但没有类型注释来强制它们仅适用于整数。确实，
我们从来不需要这些注释；他们只是帮助修改了上面的代码
更清晰。

实际上，这里的 `return` 函数非常微不足道，而且并不是真正的
必要的。但是 `>>=` 运算符可以用来替换很多样板文件
模式匹配，正如我们在算术的最终实现中看到的那样
上面的运算符。只有一个模式匹配，位于 `>>=` 内部。
与 `plus_opt` 等的原始实现相比，后者有很多
模式匹配。

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

请注意，在整数上调用可记录函数是多么不方便，因为
我们必须将整数与字符串配对。所以让我们再写一个函数
通过将整数与*空*日志配对来帮助解决这个问题：

```{code-cell} ocaml
let e x = (x, "")
```

现在我们可以写 `id' (e 5)` 而不是 `id' (5, "")`。

**Monad 在哪里？** 我们刚刚所做的工作是对整数进行函数处理
并将它们转换为与日志消息配对的整数函数。我们可以
将这些“升级”的函数视为记录的计算。他们生产
隐喻的盒子，这些盒子包含函数输出以及日志
消息。

我们刚才写的代码中有两个基本思想，分别对应
`return` 和 `bind` 的 monad 操作。

第一个是将值从 `int` 升级到 `int * string` 通过将其与
空字符串。这就是 `e` 的作用。我们可以将其重命名为 `return`：

```{code-cell} ocaml
let return (x : int) : int * string = (x, "")
```
该函数具有将值放入隐喻的*微不足道的效果*
框以及空日志消息。

第二个想法是分解代码来处理对的模式匹配
和字符串连接。这是用它自己的函数表达的想法：

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

** Writer Monad。** 我们刚刚发现的 monad 通常称为 *writer
monad* （如“另外写入日志或字符串”）。这是一个
其 monad 签名的实现：

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

正如我们在 Maybe monad 中看到的，这些是 `return` 的相同实现
和 `>>=` 正如我们上面发明的，但没有类型注释来强制它们
仅适用于整数。事实上，我们从来不需要这些注释；我们不需要这些注释。他们只是
帮助使上面的代码更清晰一些。

哪个版本的 `loggable` 更容易阅读是有争议的。当然你需要
适应一元编程风格，欣赏
使用 `>>=` 的版本。但如果你正在开发更大的代码
基（即，涉及配对字符串的函数不仅仅是 `loggable`），
使用 `>>=` 运算符可能是一个不错的选择：这意味着你的代码
write 可以集中于 `'a Writer.t` 类型中的 `'a` 而不是
字符串。换句话说，writer monad 会为你处理字符串，
只要你使用 `return` 和 `>>=` 即可。

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
数据结构。所以不可能写出 `return` 的规范
`>>=` 对于一般的单子：规范需要讨论
特定的 monad，例如 writer monad 或 Lwt monad。

另一方面，事实证明我们可以写下一些应该
持有任何单子。其原因可以追溯到我们的直觉之一
给出了有关单子的信息，即它们代表了具有影响的计算。
例如，考虑 Lwt。我们可以在 Promise X 上注册一个回调 C
`bind`。这会产生一个新的 Promise Y，我们可以在其上注册另一个
回调 D。我们期望这些回调按顺序排列：C 必须在 D 之前运行，
因为 Y 无法先于 X 被解析。

“顺序”的概念是单子法则规定的一部分。我们
将在下面说明这些法律。但首先，让我们停下来考虑一下顺序
在命令式语言中。

**顺序。* 在 Java 和 C 等语言中，有一个分号表示
对语句施加顺序，例如：

```java
System.out.println(x);
x++;
System.out.println(x);
```

首先打印 `x` ，然后递增，然后再次打印。所带来的影响
这些语句必须按顺序出现。

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

换句话说，你可以删除任何出现的 `skip`，因为它没有
影响。从数学上来说，我们说 `skip` 是一个*左恒等式*（第一定律）
和分号的*正确身份*（第二定律）。

命令式语言通常还有一种将语句分组在一起的方法
成块。在 Java 和 C 中，这通常是通过花括号完成的。这是一个
块和分号的法则：

* `{s1; s2;} s3;` 的行为应与 `s1; {s2; s3;}` 相同。

换句话说，顺序始终是 `s1` 然后 `s2` 然后 `s3`，无论
无论将前两个语句分组到一个块中，还是将后两个语句分组到一个块中
块。所以你甚至可以去掉大括号，只写 `s1; s2; s3;`，
无论如何，这就是我们通常所做的。从数学上来说，我们说分号是
*联想。*

**单子定律的顺序。** 上述三个定律正好体现了
与我们现在要阐述的单子定律相同的直觉。单子定律
只是更抽象一些，因此一开始更难理解。

假设我们有任何 monad，它像往常一样必须具有以下内容
签名：

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

这里，“行为相同”意味着两个表达式的计算结果都为
相同的值，或者它们都将进入无限循环，或者它们都将
引发相同的异常。

这些定律在数学上与 `skip` 的定律有相同的含义，
分号和我们上面看到的大括号：`return` 是左右标识
`>>=` 的，并且 `>>=` 是结合的。让我们更详细地了解每条法律。

*定律 1* 表示对值产生微不足道的影响，然后绑定函数
就其而言，与仅对值调用函数相同。考虑 Maybe
Monad：`return x` 将是 `Some x`，而 `>>= f` 将提取 `x` 并应用 `f`
到它。或者考虑 Lwt monad：`return x` 将是一个已经存在的 Promise
用 `x` 解析，并且 `>>= f` 会将 `f` 注册为回调以在 `x` 上运行。

*定律 2* 规定，对琐碎效果的约束与不具有相同
的效果。考虑可能的单子： `m >>= return` 将取决于是否
`m` 是 `Some x` 或 `None`。在前一种情况下，绑定将提取 `x`，并且
`return` 只会用 `Some` 重新包装它。在后一种情况下，绑定将
只需返回 `None` 即可。同样，对于 Lwt，绑定 `m` 将注册 `return`
作为解析后在 `m` 的内容上运行的回调，以及
`return` 只会将这些内容放回到已经存在的文件中
解析的 Promise。

*定律 3* 表明绑定序列效果正确，但在中很难看到它
这条法律比上面的版本中带有分号和大括号。法则 3 将
如果我们可以将其重写为

>`(m >>= f) >>= g` 的行为与 `m >>= (f >>= g)` 相同。

但问题是没有类型检查： `f >>= g` 没有正确的
键入位于 `>>=` 的右侧。所以我们必须插入一个额外的
匿名函数 `fun x -> ...` 使类型正确。

## 组合与 Monad 定律

还有另一个名为 `compose` 的 monad 运算符可用于组合
一元函数。例如，假设你有一个类型为 `'a t` 的 monad，并且
两个函数：

* `f : 'a -> 'b t`
* `g : 'b -> 'c t`

这些函数的组成将是

* `compose f g : 'a -> 'c t`

也就是说，组合将采用 `'a` 类型的值，对其应用 `f` ，提取
将 `'b` 从结果中删除，对其应用 `g` 并返回该值。

我们可以使用 `>>=` 来编写 `compose` ；我们不需要了解更多
monad 的内部工作原理：

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

单子组合运算符将使我们能够将这两个组合成
一个恒等函数，无需编写任何额外的代码：

```{code-cell} ocaml
let ( >=> ) f g x =
  f x >>= fun y ->
  g y

let id : int -> int option = inc >=> dec
```

使用 compose 运算符，可以得到更清晰的 monad 表述
法律：

* **法则 1：** `return >=> f` 的行为与 `f` 相同。

* **法则 2：** `f >=> return` 的行为与 `f` 相同。

* **法则 3：** `(f >=> g) >=> h` 的行为与 `f >=> (g >=> h)` 相同。

在该表述中，很明显 `return` 是左和右
正确的身份，并且该组合是关联的。
