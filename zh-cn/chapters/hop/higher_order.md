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

# 高阶函数

考虑以下两个作用在整数上的函数 `double` 和 `square`：

```{code-cell} ocaml
let double x = 2 * x
let square x = x * x
```

让我们用它们来编写另外两个函数：一个把数乘以 4，另一个计算数的四次方：

```{code-cell} ocaml
let quad x = double (double x)
let fourth x = square (square x)
```

这两个函数有一个明显的相似之处：它们都是把某个函数对同一个值应用两次。我们可以把这个模式抽象出来：把函数也作为参数传给另一个函数 `twice`：

```{code-cell} ocaml
let twice f x = f (f x)
```

函数 `twice` 是高阶的：它的输入 `f` 是一个函数。而且——回想一下所有 OCaml 函数实际上只接收一个参数——从技术上讲，它的输出是 `fun x -> f (f x)`；因此 `twice` 也返回函数，所以它同样是高阶的。

用 `twice`，我们可以以统一的方式实现 `quad` 和 `fourth`：

```{code-cell} ocaml
let quad x = twice double x
let fourth x = twice square x
```

## 抽象原则

上面我们利用了 `quad` 和 `fourth` 之间的结构相似性来节省工作量。诚然，在这个玩具示例中这似乎并不省多少事。但想象一下，如果 `twice` 实际上是某个更复杂的函数。那么，一旦有人写出了更高效的版本，每个用它定义的函数（如 `quad` 和 `fourth`）就都能从中受益，无需重新编写。

成为优秀程序员的一个标志，就是能识别这些相似性，并通过创建体现这些相似性的函数（或其他代码单元）来*抽象*它们。Bruce MacLennan 在其教材 *Functional Programming: Theory and Practice*（1990）中将此称为"抽象原则"。抽象原则说的是：避免多次陈述同一件事；相反，要把重复出现的模式*提取出来*。高阶函数使得这种重构成为可能，因为它们允许我们将函数参数化，用不同的函数来替换函数中的变化部分。

除了 `twice` 之外，这里还有一些较简单的例子，同样出自 MacLennan：

**应用（Apply）。** 我们可以编写一个函数，将第一个输入应用到第二个输入：
```{code-cell} ocaml
let apply f x = f x
```
当然，写 `apply f` 比直接写 `f` 更啰嗦。

**管道（Pipeline）。** 我们之前见过的管道运算符就是一个高阶函数：
```{code-cell} ocaml
let pipeline x f = f x
let (|>) = pipeline
let x = 5 |> double
```

**组合（Compose）。** 我们可以编写一个将两个函数组合起来的函数：
```{code-cell} ocaml
let compose f g x = f (g x)
```
这个函数可以让我们创建一个能多次应用的新函数，例如：
```{code-cell} ocaml
let square_then_double = compose double square
let x = square_then_double 1
let y = square_then_double 2
```

**两者（Both）。** 我们可以编写一个函数，将两个函数应用于同一个参数，返回一对结果：
```{code-cell} ocaml
let both f g x = (f x, g x)
let ds = both double square
let p = ds 3
```

**条件（Cond）。** 我们可以编写一个函数，根据谓词的结果选择应用两个函数中的哪一个：
```{code-cell} ocaml
let cond p f g x =
  if p x then f x else g x
```

## "高阶"的含义

"高阶"这个词在逻辑学和计算机科学中都有使用，但在不同语境下不一定有精确一致的含义。

在逻辑学中，"一阶量化"主要指的是全称量词和存在量词（$\forall$ 和 $\exists$）。它们允许你对某个感兴趣的"论域"进行量化，比如自然数。对于任意给定的量化，比如 $\forall x$，被量化的变量代表该论域中的单个元素，例如自然数 42。

*二阶量化*则更进一步，允许你对论域中的"属性"进行量化。属性是关于单个元素的断言，比如某个自然数是偶数，或者它是素数。在某些逻辑中，我们可以将属性等同于个体的集合，例如所有偶数自然数的集合。因此二阶量化通常被认为是对"集合"的量化。你还可以将属性视为接受元素并返回布尔值的函数，指示元素是否满足该属性；这就是所谓的属性的*特征函数*。

*三阶*逻辑允许对属性的属性进行量化，*四阶*则允许对属性的属性的属性进行量化，依此类推。*高阶逻辑*是指所有比一阶逻辑更强大的逻辑；不过这一领域有一个有趣的结果：所有高阶逻辑都可以用二阶逻辑来表达。

在编程语言中，*一阶函数*类似地指作用于普通数据元素（如字符串、整数、记录、变体等）的函数。而*高阶函数*则可以操作函数本身，就像高阶逻辑可以对属性进行量化一样（而属性就如同函数）。

## 著名的高阶函数

在接下来的几节中，我们将深入探讨三个最著名的高阶
函数：`map`、`filter` 和 `fold`。这些是可以定义的函数
许多数据结构，包括列表和树。每个的基本思想是：

* *map* 变换元素，
* *filter* 消除元素，以及
* *fold* 组合元素。
