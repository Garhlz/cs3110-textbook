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

对于 OCaml 中的每种数据类型，我们一直在讨论如何构建和访问它。对于变体，构建非常简单：只需写下构造函数的名称。访问则通过模式匹配来完成。例如：
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
OCaml 不会像你在带有枚举的语言中所期待的那样，自动将构造函数名称映射为 `int`。

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

假设有两个类型定义了重叠的构造函数名称，例如：
```{code-cell} ocaml
type t1 = C | D
type t2 = D | E
let x = D
```
当 `D` 出现在这些定义之后时，它指的是哪种类型？也就是说，上面的 `x` 是什么类型？答案是：后定义的类型会胜出。因此 `x : t2`。这可能会让程序员感到意外，因此在同一作用域内（例如同一个文件或模块，不过我们还没有涉及模块），每当可能出现构造函数名冲突时，惯用的做法是给构造函数加上一个区分性的前缀。例如，假设我们定义代表宝可梦（Pok&eacute;mon）的类型：
```{code-cell} ocaml
type ptype =
  TNormal | TFire | TWater

type peff =
  ENormal | ENotVery | ESuper
```
因为"Normal"既可能是一种宝可梦类型，也可能是一种宝可梦招式的效果，所以我们在每个构造函数名前额外加一个字符，用来区分它是类型（T）还是效果（E）。

## 模式匹配

每次我们引入一种新的数据类型时，我们都需要引入新的数据类型
与之相关的模式。对于变体来说，这很容易。我们添加以下内容
新模式形式添加到合法模式列表中：

* 构造函数名称 `C`

我们扩展模式匹配值并产生绑定的定义如下：

* 模式 `C` 与值 `C` 匹配并且不生成任何绑定。

```{note}
变体比我们在这里看到的要强大得多。我们会
很快就会再次回到他们身边。
```
