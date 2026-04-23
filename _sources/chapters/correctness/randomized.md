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

# 使用 QCheck 进行随机测试

{{ video_embed | replace("%%VID%%", "62SYeSlSCNM")}}

*随机测试*又名*模糊测试*是生成随机数的过程
输入并将它们提供给程序或函数以查看程序是否
行为正确。当前的问题是如何确定什么是正确的
输出是针对给定输入的。如果*参考实现*是
available&mdash; 也就是说，一个被认为是正确的实现，但在
其他一些方式还不够（例如，它的性能太慢，或者它处于
不同的语言）&mdash;那么两个实现的输出可以是
比较。否则，也许可以检查输出的某些“属性”。对于
例如，

* “不崩溃”是用户界面中一个令人感兴趣的属性；

* 将 $n$ 元素添加到数据集合中，然后删除这些元素，以及
最终得到一个空集合，是数据中感兴趣的属性
  结构；和

* 在密钥下加密字符串，然后在该密钥下解密它并得到
返回原始字符串是加密方案中感兴趣的属性
  就像恩尼格玛一样。

随机测试是一种非常强大的技术。它经常被用在
测试程序是否存在安全漏洞。 [`qcheck` package][qcheck]
for OCaml 支持随机测试。讨论完之后我们接下来再看
随机数生成。

[qcheck]: https://github.com/c-cube/qcheck

## 随机数生成

为了理解随机测试，我们需要简短地讨论一下随机测试
数生成。

大多数语言都提供生成随机数的工具。事实上，这些
生成器通常不是真正随机的（从某种意义上说，它们完全是随机的）
不可预测）但实际上是 [*pseudorandom*][prng]：数字序列
他们生成通过良好的统计测试，以确保没有可辨别的
其中的模式，但序列本身是一个确定性函数
初始*种子*值。 （回想一下，前缀 *pseudo* 来自希腊语
*pseud&emacr;s* 表示“假”。） [Java][java-random] 和
[Python][python-random] 都提供伪随机数生成器 (PRNG)。所以
OCaml 在标准库的 [`Random` module][random] 中执行。

[prng]: https://en.wikipedia.org/wiki/Pseudorandom_number_generator
[java-random]: https://docs.oracle.com/javase/8/docs/api/java/util/Random.html
[python-random]: https://docs.python.org/3/library/random.html
[random]: https://ocaml.org/api/Random.html

**实验。** 启动 utop 的新会话并输入以下内容：

```ocaml
# Random.int 100;;
# Random.int 100;;
# Random.int 100;;
```

每个响应都是一个整数 $i$ ，使得 $0 \leq i < 100$ 。

现在退出 utop 并开始另一个新会话。再次输入相同的短语。你
将得到与上次相同的答复。事实上，除非你的 OCaml
安装与制作本书时使用的安装有些不同，你将
得到与下面相同的数字：

```{code-cell} ocaml
Random.int 100;;
Random.int 100;;
Random.int 100;;
```

并不完全不可预测，是吗？

**PRNG。** 尽管出于安全和加密的目的，PRNG 会导致
可怕的漏洞，用于其他目的&mdash;包括测试和
模拟&mdash;PRNG 就可以了。它们的可预测性甚至很有用：
给定相同的初始种子，PRNG 将始终产生相同的序列
伪随机数，从而能够重复特定的序列
测试或特定的模拟。

PRNG 的一般工作方式是初始化一个它所保留的“状态”
来自初始种子的内部。从那时起，每次PRNG生成一个
新值，它必须更新该状态。 `Random` 模块使得它
可以以有限的方式操纵该状态。例如，你可以

* 使用 `Random.get_state` 获取当前状态，

* 使用 `Random.State.copy` 复制当前状态，

* 请求从特定状态生成的随机 `int`
`Random.State.int`，以及

* 自己初始化状态。函数 `Random.self_init` 和
`Random.State.make_self_init` 将选择一个“随机”种子来初始化
  状态。他们通过从一个名为的特殊 Unix 文件中采样来做到这一点
  [`/dev/urandom`][urandom]，旨在提供尽可能接近真实的
  计算机可以具有随机性。

[urandom]: https://en.wikipedia.org/wiki//dev/random

**重复实验。** 启动一个新的 utop 会话。输入以下内容：

```ocaml
# Random.self_init ();;
# Random.int 100;;
# Random.int 100;;
# Random.int 100;;
```

现在再做一次（无论你是否退出 utop
或不在两者之间）。  你会发现你得到了不同的
值的序列。  很有可能你得到的会有所不同
比以下值：

```{code-cell} ocaml
Random.self_init ();;
Random.int 100;;
Random.int 100;;
Random.int 100;;
```

## QCheck 抽象

在使用 QCheck 进行测试之前，我们需要先了解三个抽象：
生成器、属性和任意值。  如果你想跟随
utop，使用此指令加载 QCheck：

```{code-cell} ocaml
:tags: ["remove-cell"]
#use "topfind";;
```

```{code-cell} ocaml
:tags: ["remove-output"]
#require "qcheck";;
```

**生成器。** QCheck 提供的关键功能之一是
生成各种类型的伪随机值的能力。这是一些
执行此操作的模块的签名：

```ocaml
module QCheck : sig
  ...
  module Gen :
  sig
    type 'a t = Random.State.t -> 'a
    val int : int t
    val generate : ?rand:Random.State.t -> n:int -> 'a t -> 'a list
    val generate1 : ?rand:Random.State.t -> 'a t -> 'a
    ...
  end
  ...
end
```
`'a QCheck.Gen.t` 是一个函数，它接受 PRNG 状态并使用它来
产生类型为 `'a` 的伪随机值。所以 `QCheck.Gen.int` 产生
伪随机整数。函数 `generate1` 实际上生成
一个伪随机值。它采用一个可选参数，即 PRNG 状态；如果
未提供该参数，它使用默认的 PRNG 状态。函数
`generate` 生成 `n` 伪随机值的列表。

QCheck 实现了许多伪随机值的生成器。这里还有一些
他们：

```ocaml
module QCheck : sig
  ...
  module Gen :
  sig
    val int : int t
    val small_int : int t
    val int_range : int -> int -> int t
    val list : 'a t -> 'a list t
    val list_size : int t -> 'a t -> 'a list t
    val string : ?gen:char t -> string t
    val small_string : ?gen:char t -> string t
    ...
  end
  ...
end
```
你可以在 [文档][qcheckdoc] 中了解这一点以及许多其他内容。

[qcheckdoc]: https://c-cube.github.io/qcheck/0.17/qcheck-core/QCheck/Gen/index.html

**属性。** 人们很容易认为 QCheck 将使我们能够测试
函数通过生成许多伪随机输入到函数，运行
对它们运行，然后检查输出是否正确。但有
立即出现一个问题：QCheck 如何知道每个的正确输出是什么？
这些输入？由于它们是随机生成的，测试工程师无法
对正确的输出进行硬编码。

因此，QCheck 允许我们检查每个输出的“属性”是否成立。
属性是类型 `t -> bool` 的函数，对于某些类型 `t`，它告诉我们
`t` 类型的值是否表现出某些所需的特征。在这里，为了
例如，有两个属性；判断一个整数是否是
Even，另一个确定列表是否按非递减排序
根据内置 `<=` 运算符进行排序：

```{code-cell} ocaml
let is_even n = n mod 2 = 0

let rec is_sorted = function
  | [] -> true
  | [_] -> true
  | h1 :: (h2 :: t as t') -> h1 <= h2 && is_sorted t'
```

**任意。** 我们向 QCheck 呈现要检查的输出的方式是
类型为 `'a QCheck.arbitrary` 的值。该类型表示“任意”值
类型为 `'a`&mdash; 也就是说，它是伪随机选择的值
想要检查，更具体地说，检查它是否满足某个属性。

我们可以使用该函数从生成器中创建*任意*
`QCheck.make : 'a QCheck.Gen.t -> 'a QCheck.arbitrary`。 （其实这个函数
接受一些我们在这里省略的可选参数。）这实际上不是
创建任意值的正常方法，但这是一种可以帮助我们的简单方法
理解他们；过一会儿我们就会恢复正常。例如，
下面的表达式代表任意整数：

```{code-cell} ocaml
:tags: ["hide-output"]
QCheck.make QCheck.Gen.int
```

## 测试性质

为了构建 QCheck 测试，我们创建一个任意值和一个属性，并将它们传递给
到 `QCheck.Test.make` ，其类型可以简化为：

```ocaml
QCheck.Test.make : 'a QCheck.arbitrary -> ('a -> bool) -> QCheck.Test.t
```

实际上，该函数还采用几个我们省略的可选参数
在这里。该测试将生成一定数量的任意值并检查是否
他们每个人都有财产。例如，以下代码创建一个 QCheck
检查任意整数是否为偶数的测试：

```{code-cell} ocaml
let t = QCheck.Test.make (QCheck.make QCheck.Gen.int) is_even
```

如果我们想改变检查的任意数量，我们可以
将可选整数参数 `~count` 传递给 `QCheck.Test.make`。

我们可以使用 `QCheck_runner.run_tests : QCheck.Test.t list -> int` 运行该测试。
（该函数再次采用一些我们在此处省略的可选参数。）
如果列表中的所有测试都通过，则返回整数 0，否则返回 1。对于
上面的测试，运行它很大概率会输出1，因为它会
生成至少一个奇数。

```{code-cell} ocaml
QCheck_runner.run_tests [t]
```

不幸的是，该输出的信息量并不大。它没有告诉我们什么
特定值未能满足属性！我们将解决这个问题
一会儿。

如果你想制作一个运行 QCheck 测试并打印的 OCaml 程序
结果，有一个函数 `QCheck_runner.run_tests_main` 的工作原理很像
`OUnit2.run_test_tt_main`：只需将其作为测试中的最终表达式调用
文件。例如：

```ocaml
let tests = (* code that constructs a [QCheck.Test.t list] *)
let _ = QCheck_runner.run_tests_main tests
```

要编译 QCheck 代码，只需将 `qcheck` 库添加到 `dune` 文件中：

```console
(executable
 ...
 (libraries ... qcheck))
```

QCheck 测试可以转换为 OUnit 测试并包含在通常的测试中
我们一直在编写 OUnit 测试套件。执行此操作的函数是：

```{code-cell} ocaml
QCheck_runner.to_ounit2_test
```

## QCheck 的信息输出

我们在上面注意到，到目前为止 QCheck 的输出只告诉我们“是否”有一些
任意者满足了一个属性，但没有满足任意者未能满足的“哪个”属性
它。让我们解决这个问题。

问题在于我们如何直接从生成器构造任意值。
任意的不仅仅是一个生成器。 QCheck 库需要
知道如何打印生成器的值，以及其他一些东西。你
可以看到`'a QCheck.arbitrary`的定义中：

```{code-cell} ocaml
#show QCheck.arbitrary;;
```

除了生成器字段 `gen` 之外，还有一个包含
从生成器打印值的可选函数，以及其他一些可选函数
领域也是如此。幸运的是，我们通常不需要找到一种方法来完成这些
我们自己田野； `QCheck` 模块提供了许多对应的任意值
到 `QCheck.Gen` 中找到的生成器：

```ocaml
module QCheck :
  sig
    ...
  val int : int arbitrary
  val small_int : int arbitrary
  val int_range : int -> int -> int arbitrary
  val list : 'a arbitrary -> 'a list arbitrary
  val list_of_size : int Gen.t -> 'a arbitrary -> 'a list arbitrary
  val string : string arbitrary
  val small_string : string arbitrary
    ...
  end
```

使用这些任意值，我们可以获得改进的错误消息：

```{code-cell} ocaml
let t = QCheck.Test.make ~name:"my_test" QCheck.int is_even;;
QCheck_runner.run_tests [t];;
```

输出告诉我们 `my_test` 失败，并向我们显示输入
导致了失败。

## 使用 QCheck 测试函数

QCheck 难题的最后一部分是使用随机生成的输入
测试函数的输出是否满足某些属性。例如，这里有一个
QCheck测试`double`的输出是否正确：

```{code-cell} ocaml
let double x = 2 * x;;
let double_check x = double x = x + x;;
let t = QCheck.Test.make ~count:1000 QCheck.int double_check;;
QCheck_runner.run_tests [t];;
```

上面，`double` 是我们正在测试的函数。我们正在测试的属性
`double_check`，就是 `double x` 始终是 `x + x`。我们通过以下方式做到这一点
QCheck 创建 1000 个任意整数并测试每个整数的属性是否成立
其中。

这里还有几个例子，取自 QCheck 自己的文档。
首先检查 `List.rev` 是否是*对合*，这意味着应用它
两次将带你回到原始列表。  这是一个属性，应该
保持列表反转的正确实施。

```{code-cell} ocaml
let rev_involutive lst = List.(lst |> rev |> rev = lst);;
let t = QCheck.(Test.make ~count:1000 (list int) rev_involutive);;
QCheck_runner.run_tests [t];;
```

事实上，运行 1000 次随机测试表明，没有一个失败。 `int`
上面使用的生成器在 OCaml 的整个范围内统一生成整数
整数。 `list` 生成器创建其元素是单独的列表
由 `int` 生成。根据`list`的文档，每个的长度
列表是由另一个生成器 `nat` 随机生成的，它生成“小
自然数。”这意味着什么？没有指定。但如果我们读到
[current source code][src-nat]，我们看到这些是从0到10,000的整数，
并偏向于该范围内较小的数字。

[src-nat]: https://github.com/c-cube/qcheck/blob/18247cf40af4272f7a2f93e273724b962db61b01/src/core/QCheck2.ml#L276


第二个示例检查所有列表是否已排序。  当然，并不是所有的名单
*已*排序！  所以我们应该预料到这个测试会失败。

```{code-cell} ocaml
let is_sorted lst = lst = List.sort Stdlib.compare lst;;
let t = QCheck.(Test.make ~count:1000 (list small_nat) is_sorted);;
QCheck_runner.run_tests [t];;
```

输出显示了未排序的列表示例，因此违反了
财产。生成器 `small_nat` 类似于 `nat` 但范围从 0 到 100。
