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

考虑整数上的这些函数 `double` 和 `square`：

```{code-cell} ocaml
let double x = 2 * x
let square x = x * x
```

让我们使用这些函数来编写另外两个函数：一个把数乘以 4，
另一个计算数的四次方：

```{code-cell} ocaml
let quad x = double (double x)
let fourth x = square (square x)
```

这两个函数有一个明显的相似之处：它们的作用是
将给定函数应用于一个值两次。通过将函数传递给另一个函数
函数 `twice` 作为参数，我们可以抽象这个函数：

```{code-cell} ocaml
let twice f x = f (f x)
```

函数 `twice` 是高阶的：它的输入 `f` 是一个函数。
并且 &mdash; 回想一下所有 OCaml 函数实际上只接收一个
参数 &mdash; 从技术上讲，它的输出是 `fun x -> f (f x)`；
因此 `twice` 返回函数，所以它也是高阶的。

使用`twice`，我们可以以统一的方式实现`quad`和`fourth`：

```{code-cell} ocaml
let quad x = twice double x
let fourth x = twice square x
```

## 抽象原则

上面，我们利用了 `quad` 和 `fourth` 之间的结构相似性
以节省工作量。诚然，在这个玩具示例中，这似乎并不需要太多工作。
但想象一下 `twice` 实际上是一些更复杂的函数。
然后，如果有人想出一个更有效的版本，每个函数
用它编写的函数（如 `quad` 和 `fourth`）都可以从效率提升中受益，
而无需重新编码。

成为一名优秀程序员的一部分就是认识到这些相似之处和
通过创建实现它们的函数（或其他代码单元）来*抽象*这些相似性。
Bruce MacLennan 在他的教科书中将此称为“抽象原则”
*函数式编程：理论与实践*（1990）。抽象原则
意思是避免多次陈述同一件事；相反，要把重复出现的模式
*提取出来*。高阶函数可以实现这样的重构，
因为它们允许我们分解函数，并用其他函数对函数进行参数化。

除了`twice`之外，这里还有一些比较简单的例子，也感谢
Mac伦南：

**应用。** 我们可以编写一个函数，将其第一个输入应用到第二个输入
输入：
```{code-cell} ocaml
let apply f x = f x
```
当然，编写 `apply f` 比直接编写 `f` 更费事。

**Pipeline.** 我们之前见过的 pipeline 操作符是一个
高阶函数：
```{code-cell} ocaml
let pipeline x f = f x
let (|>) = pipeline
let x = 5 |> double
```

**Compose.** 我们可以编写一个组合另外两个函数的函数：
```{code-cell} ocaml
let compose f g x = f (g x)
```
这个函数可以让我们创建一个可以应用的新函数
多次，例如：
```{code-cell} ocaml
let square_then_double = compose double square
let x = square_then_double 1
let y = square_then_double 2
```

**Both.** 我们可以编写一个函数，将两个函数应用于同一个
参数并返回一对结果：
```{code-cell} ocaml
let both f g x = (f x, g x)
let ds = both double square
let p = ds 3
```

**条件** 我们可以编写一个函数，有条件地选择两个中的哪一个
基于谓词应用的函数：
```{code-cell} ocaml
let cond p f g x =
  if p x then f x else g x
```

## “高阶”的含义

尽管“高阶”一词在整个逻辑和计算机科学中都有使用
不一定在所有情况下都具有精确或一致的含义。

在逻辑中，“一阶量化”主要指的是普遍的和
存在（$\forall$ 和 $\exists$）量词。这些可以让你量化
一些感兴趣的“领域”，例如自然数。但对于任意给定的
量化，比如 $\forall x$，被量化的变量代表一个
该域的单个元素，例如自然数 42。

*二阶量化*让你可以做一些更强大的事情，
也就是对论域中的“属性”进行量化。属性是关于单个元素的断言，
例如某个自然数是偶数，或者它是素数。在某些逻辑中，我们可以将属性等同于个体的集合，
例如所有偶数自然数的集合。所以二阶量化是
通常被认为是对“集合”的量化。你还可以考虑属性
作为接受元素并返回布尔值的函数，指示
元素是否满足属性；这就是所谓的属性的*特征函数*。

*三阶*逻辑将允许对属性的属性进行量化，
以及属性的属性的属性的*四阶*，等等。
*高阶逻辑*是指所有这些比逻辑更强大的逻辑
一阶逻辑；尽管这一领域的一个有趣的结果是所有
高阶逻辑可以用二阶逻辑来表达。

在编程语言中，“一阶函数”类似地指作用于普通数据元素
（例如字符串、整数、记录、变体等）的函数。
而*高阶函数*可以操作函数，很像高阶逻辑可以量化属性
（而属性就像函数）。

## 著名的高阶函数

在接下来的几节中，我们将深入探讨三个最著名的高阶
函数：`map`、`filter` 和 `fold`。这些是可以定义的函数
许多数据结构，包括列表和树。每个的基本思想是：

* *map* 变换元素，
* *filter* 消除元素，以及
* *fold* 组合元素。
