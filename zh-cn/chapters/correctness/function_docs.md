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

# 函数文档

*本节继续讨论
[documentation](../basics/documentation)，我们在第 2 章开始。*

{{ video_embed | replace("%%VID%%", "ggm5rjAyjhw")}}

规范是为人类阅读而编写的，而不是为机器阅读的。 “规格”可以采取
写好文章的时间，花得值。主要目标是清晰度。它是
简洁也很重要，因为客户端程序员并不总是采用
阅读长规范的努力。就像我们写的任何东西一样，我们需要意识到
编写规范时我们的受众。有些读者可能需要更多
比其他规范更详细。

一个写得很好的规范通常有几个部分来传达不同的信息
有关指定事物的各种信息。如果我们知道通常的情况
规范的组成部分是，我们不太可能忘记写下
一些重要的事情。现在让我们看一下编写规范的秘诀。

{{ video_embed | replace("%%VID%%", "p5OTwjNTQIs")}}

## 返回子句

我们如何指定 `sqr` 这个平方根函数？首先，我们需要描述一下
它的结果。我们将此描述称为“返回子句”，因为它是
描述函数调用结果的规范的一部分。它是
也称为*后置条件*：它描述了在
函数被调用。以下是 returns 子句的示例：

```ocaml
(** Returns: [sqr x] is the square root of [x]. *)
```

但我们通常会省略 `returns:`，只写返回值
子句作为评论的第一句：

```ocaml
(** [sqr x] is the square root of [x]. *)
```

对于数值编程，我们可能应该添加一些关于如何进行的信息
准确的是。

```ocaml
(** [sqr x] is the square root of [x]. Its relative accuracy is no worse than
    [1.0e-6]. *)
```

类似地，我们可以这样为 `find` 函数编写 returns 子句：

```ocaml
(** [find lst x] is the index of [x] in [lst], starting from zero. *)
```

一个好的规范是简洁但清晰的&mdash;它应该足以说明
读者了解该函数的作用，但无需额外的语言
并可能导致读者错过重点。有时有一个
在简洁性和清晰性之间取得平衡。

这两个规范使用了一个有用的技巧来使它们更加简洁：它们会说话
关于将指定函数应用于任意某个的结果
论据。我们隐含地理解，所陈述的后置条件适用于所有
任何未绑定变量（参数变量）的可能值。

## 前置条件子句

`sqr` 的规范并不完全有意义，因为正方形
对于 `real` 类型的某些 `x` ，根不存在。数学平方根
function 是一个“部分”函数，仅在其域的一部分上定义。一个
良好的函数规范对于可能的输入来说是完整的；它
让客户了解允许哪些输入以及哪些输入
结果将针对允许的输入。

我们有几种方法来处理部分函数。一个简单的方法
是限制域，以便明确该函数不能
在某些输入上合法使用。该规范排除了不良输入
*requires 子句*确定何时可以调用该函数。该条款是
也称为*前提条件*，因为它描述了必须满足的条件
在调用该函数之前。这是 `sqr` 的 require 子句：

```ocaml
(** [sqr x] is the square root of [x]. Its relative accuracy is no worse
    than [1.0e-6].  Requires: [x >= 0]. *)
```

该规范没有说明 `x < 0` 时会发生什么，也没有必要说明。
请记住，该规范是一份合同。这份合同恰好推动了
证明平方根存在的责任由客户承担。如果需要
不满足子句，则允许执行执行任何操作
喜欢：例如，进入无限循环或抛出异常。
这种方法的优点是实施者可以自由地设计
算法无需检查无效输入的约束
参数，这可能很乏味并且减慢程序速度。缺点是
如果函数调用不正确，调试可能会很困难，因为
该函数可能会出现错误，并且客户端不知道它会如何发生
行为不端。

## 抛出异常子句

处理偏函数的另一种方法是将它们转换为总函数
函数（在整个域上定义的函数）。这种方法是
对于客户端来说可以说更容易处理，因为该函数的行为是
总是被定义；它没有先决条件。然而，它把工作推到了
实施者，可能会导致实施速度变慢。

我们如何将`sqr`转换为total函数？一种（太）频繁的方法
接下来是定义在需要的情况下返回的一些值
条款将排除；例如：

```ocaml
(** [sqr x] is the square root of [x] if [x >= 0],
    with relative accuracy no worse than 1.0e-6.
    Otherwise, a negative number is returned. *)
```

不推荐这种做法，因为它往往会鼓励破碎，
难以阅读的客户端代码。几乎这个抽象的任何正确的客户端都会
如果不能证明前提条件成立，请编写如下代码：

```ocaml
if sqr(a) < 0.0 then ... else ...
```

该错误仍然必须在 `if` 表达式中处理，因此客户端的工作
这种抽象并不比使用 require 子句更容易：客户端
仍然需要在调用周围进行显式测试，以防可能出现的情况
失败。如果省略测试，编译器不会抱怨，并且负面的
数字结果将被默默地视为有效的平方根，可能
导致稍后程序执行过程中出现错误。这种编码风格一直是
Unix 操作系统中无数错误和安全问题的根源
及其后代（例如 Linux）。

使函数完整的一个更好的方法是让它们在以下情况下引发异常：
不满足预期的输入条件。例外避免了必要性
分散客户端代码中的错误处理逻辑。如果函数是
总而言之，规范必须说明引发什么异常以及何时引发。对于
例如，我们可以将平方根函数总计如下：

```ocaml
(** [sqr x] is the square root of [x], with relative accuracy no worse
    than 1.0e-6. Raises: [Negative] if [x < 0]. *)
```

注意，这个`sqr`函数的实现必须检查是否`x >= 0`，
即使在代码的生产版本中，因为某些客户端可能依赖
关于要抛出的异常。

## 示例子句

提供说明性示例作为规范的一部分可能很有用。
无论规范写得多么清晰和好，通常都会有一个例子
对客户有用。

```ocaml
(** [find lst x] is the index of [x] in [lst], starting from zero.
    Example: [find ["b","a","c"] "a" = 1]. *)
```

## 规格说明游戏

在评估规格时，想象一个游戏正在被开发是很有用的。
在两个人之间进行：一个*说明符*和一个*狡猾的程序员。*

假设说明符编写了以下说明：

```ocaml
(** Returns a list. *)
val reverse : 'a list -> 'a list
```

该规范显然是不完整的。  例如，一个狡猾的程序员可能会遇到
具有给出以下输出的实现的规范：

```ocaml
# reverse [1; 2; 3];;
- : int list = []
```

规范制定者意识到这一点后，将规范细化如下：

```ocaml
(** [reverse lst] returns a list that is the same length as [lst]. *)
val reverse : 'a list -> 'a list
```

但狡猾的程序员发现规范仍然允许损坏
实施：

```ocaml
# reverse [1; 2; 3];;
- : int list = [0; 0; 0]
```

最后，规范制定者确定了第三个规范：

```ocaml
(** [reverse lst] returns a list [m] satisfying the following conditions:
    - [length lst = length m],
    - for all [i], [nth m i = nth lst (n - i - 1)],
      where [n] is the length of [lst].
    For example, [reverse [1; 2; 3]] is [[3; 2; 1]], and [reverse []] is [[]]. *)
val reverse : 'a list -> 'a list
```

有了这个规范，狡猾的程序员就被迫提供一个可用的
实现以满足规范，因此规范者已成功编写她
规格

玩这个游戏的目的是提高你的写作能力
规格。显然我们并不提倡你刻意尝试
违反规范的意图并侥幸逃脱惩罚。当读某人的时候
其他人的规范，请尽可能广泛地阅读。但要无情
提高自己的规格。

## 注释

除了指定函数之外，程序员还需要在
函数体。事实上，程序员通常写的注释不够多
在他们的代码中。 （有关经典示例，请查看
Quake 3 Arena 游戏引擎的 [actual comment on line 561][quake3-wtf]。）

[quake3-wtf]: https://archive.softwareheritage.org/swh:1:cnt:bb0faf6919fc60636b2696f32ec9b3c2adb247fe;origin=https://github.com/id-Software/Quake-III-Arena;visit=swh:1:snp:4ab9bcef131aaf449a7c01370aff8c91dcecbf5f;anchor=swh:1:rev:dbe4ddb10315479fc00086f08e25d968b4b43c49;path=/code/game/q_math.c;lines=558-564

但这并不意味着添加更多评论总是更好。错误的
注释只会进一步模糊代码。将尽可能多的评论放入
尽可能多的代码通常会使代码变得更糟！代码和注释都是
精确的通信工具（与计算机和其他程序员）
应该小心使用。

阅读包含许多散布的代码时特别烦人
评论（通常价值值得怀疑），例如：

```ocaml
let y = x + 1 (* make y one greater than x *)
```

对于复杂的算法，可能需要一些注释来解释代码如何
实现该算法有效。程序员经常会被诱惑去写
关于算法的注释散布在代码中。但有人在读
代码经常会发现这些注释令人困惑，因为它们没有
算法的高级视图。通常最好写一个
函数开头的段落式注释解释其如何
实施工作。代码中需要关联的显式点
然后可以用非常简短的注释来标记该段落，例如 `(* case 1 *)`。

另一个常见但善意的错误是给变量很长，
描述性名称，如以下详细代码所示：

```{code-cell} ocaml
let number_of_zeros the_list =
  List.fold_left (fun (accumulator : int) (list_element : int) ->
    accumulator + (if list_element = 0 then 1 else 0)) 0 the_list
```

使用如此长的名称的代码非常冗长且难以阅读。而不是尝试
在变量名称中嵌入变量的完整描述，使用短和
建议性名称（例如 `zeros`），如有必要，请在其位置添加注释
解释变量用途的声明。

```{code-cell} ocaml
let zeros lst =
  let is0 = function 0 -> 1 | _ -> 0 in
  List.fold_left (fun zs x -> zs + is0 x) 0 lst
```

一个类似的不好的做法是在变量的名称中编码变量的类型，
例如，命名变量 `i_count` 以表明它是一个整数。类型系统
将为你保证，你的编辑器可以将鼠标悬停在
显示类型。如果你确实想在代码中强调类型，请添加一个类型
在变量进入作用域的地方进行注释。
