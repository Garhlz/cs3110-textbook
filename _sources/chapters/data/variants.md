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

# 变体

*变体*是一种数据类型，表示一个值是多个可能的值中的一个。最简单的说法是，变体就像 C 或 Java 中的枚举：

```{code-cell} ocaml
type day = Sun | Mon | Tue | Wed | Thu | Fri | Sat
let d = Tue
```

变体值的各个选项在 OCaml 中称为"构造函数"。在上面的例子中，构造函数包括 `Sun`、`Mon` 等。这里对"构造函数"一词的使用与 C++ 或 Java 中的含义有所不同。

对于 OCaml 中的每种数据类型，我们一直在讨论如何构建和
访问它。对于变体，构建很容易：只需写下变体的名称
构造函数。为了访问，我们使用模式匹配。例如：
```{code-cell} ocaml
let int_of_day d =
  match d with
  | Sun -> 1
  | Mon -> 2
  | Tue -> 3
  | Wed -> 4
  | Thu -> 5
  | Fri -> 6
  | Sat -> 7
```
没有任何类型的自动方法将构造函数名称映射到 `int`，
就像你对带有枚举的语言所期望的那样。

**语法。**

定义变体类型：
```ocaml
type t = C1 | ... | Cn
```

构造函数名称必须以大写字母开头。OCaml
使用它来区分构造函数和变量标识符。

编写构造函数值的语法就是它的名称，例如 `C`。

**动态语义。**

* 构造函数已经是一个值。  无需执行任何计算。

**静态语义。**

* 如果 `t` 是定义为 `type t = ... | C | ...` 的类型，则为 `C : t`。

## 作用域

假设有两个类型定义了重叠的构造函数名称，例如
例如，
```{code-cell} ocaml
type t1 = C | D
type t2 = D | E
let x = D
```
当 `D` 出现在这些定义之后时，它指的是哪种类型？也就是说，
上面的 `x` 是什么类型？答案是后面定义的类型获胜。
所以`x : t2`。这可能会让程序员感到惊讶，因此在任何给定的范围内
范围（例如，文件或模块，尽管我们还没有涵盖模块）
每当可能出现重叠的构造函数名称时，都会惯用它们作为前缀
一些显着的特征。例如，假设我们将类型定义为
代表 Pok&eacute;mon：
```{code-cell} ocaml
type ptype =
  TNormal | TFire | TWater

type peff =
  ENormal | ENotVery | ESuper
```
因为“Normal”自然是 a 类型的构造函数名称
Pok&eacute;mon 和 Pok&eacute;mon 攻击的有效性，我们额外添加一个
每个构造函数名称前面的字符指示它是类型还是
一个有效性。

## 模式匹配

每次我们引入一种新的数据类型时，我们都需要引入新的数据类型
与之相关的模式。对于变体来说，这很容易。我们添加以下内容
新模式形式添加到合法模式列表中：

* 构造函数名称 `C`

我们扩展了模式何时匹配一个值并产生一个的定义
绑定如下：

* 模式 `C` 与值 `C` 匹配并且不生成任何绑定。

```{note}
变体比我们在这里看到的要强大得多。我们会
很快就会再次回到他们身边。
```
