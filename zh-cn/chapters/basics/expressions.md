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

# 表达式

OCaml 语法的主要组成部分是*表达式*。命令式语言中的程序主要由*命令*构成，而函数式语言中的程序则主要由表达式构建。表达式的例子包括 `2+2` 和 `increment 21`。

OCaml 手册有语言中所有[表达式][exprs]的完整定义。该页面开头相当晦涩，但如果你向下滚动，会看到一些英文解释。现在不必深入研究那个页面；只需知道它可以作为参考即可。

[exprs]:  https://ocaml.org/manual/expr.html

函数式语言中计算的主要任务是把表达式“求值”为*值*。值是一个不再有任何待计算步骤的表达式。所以，所有值都是表达式，但不是所有表达式都是值。值的示例包括 `2`、`true` 和 `"yay!"`。

OCaml 手册也有[所有值][values]的定义，同样，该页面主要用于参考，而不是学习。

[values]: https://ocaml.org/manual/values.html

有时表达式可能无法计算出某个值。这有两种可能的原因：

1. 表达式的求值引发了异常。
2. 表达式的求值永远不会终止（例如，它进入了“无限循环”）。

## 原始类型和值

*原始*类型是内置的最基本类型：整数、浮点数、字符、字符串和布尔值。这些类型与其他编程语言中的基本类型相似。

**类型 `int`：整数。** OCaml 整数照常编写：`1`、`2` 等。
常用运算符可用：`+`、`-`、`*`、`/` 和 `mod`。后者
两个是整数除法和模数：

```{code-cell} ocaml
65 / 60
```

```{code-cell} ocaml
65 mod 60
```

```{code-cell} ocaml
:tags: ["raises-exception"]
65 / 0
```

在现代平台上，OCaml 整数范围从 $-2^{62}$ 到 $2^{62}-1$。它们是
用 64 位机器 *words* 实现，这是寄存器的大小
64 位处理器。但其中一位被 OCaml 实现“窃取”，
导致 63 位表示。该位在运行时用于区分
来自指针的整数。对于需要真正 64 位整数的应用程序，有
是标准库中的 [`Int64` module][int64] 。对于应用程序
需要任意精度整数，有一个单独的 [`Zarith`][zarith]
库。但对于大多数用途，内置 `int` 类型就足够了，并提供
最佳表现。

[int64]: https://ocaml.org/api/Int64.html
[zarith]: https://github.com/ocaml/Zarith

**类型 `float`：浮点数。** OCaml 浮点数是 [IEEE 754
双精度浮点数][binary64]。从语法上来说，他们必须
始终包含一个点 &mdash; 例如，`3.14` 或 `3.0` 甚至 `3.`。  最后一个
是 `float`；如果你将其写为 `3`，则它是 `int`：

```{code-cell} ocaml
3.
```

```{code-cell} ocaml
3
```

OCaml 故意不支持运算符重载。算术运算
浮点数后面有一个点。例如，浮点
乘法写成 `*.` 而不是 `*`：

```{code-cell} ocaml
3.14 *. 2.
```

```{code-cell} ocaml
:tags: ["raises-exception"]
3.14 * 2.
```

OCaml 不会自动在 `int` 和 `float` 之间进行转换。如果你想
转换，有两个内置函数用于此目的： `int_of_float` 和
`float_of_int`。

```{code-cell} ocaml
3.14 *. (float_of_int 2)
```

与任何语言一样，浮点表示是近似的。那可以
导致舍入错误：

```{code-cell} ocaml
0.1 +. 0.2
```

在 Python 和 Java 中也可以观察到相同的行为。  如果你还没有
以前遇到过这种现象，这里有一个【浮点基础指南
表示][fp-guide]你可能会喜欢阅读。

[binary64]: https://en.wikipedia.org/wiki/Double-precision_floating-point_format
[fp-guide]: https://floating-point-gui.de/basic/

**类型 `bool`：布尔值。** 布尔值写作 `true` 和 `false`。
常见的短路合取 `&&` 和析取 `||` 运算符是
可用。

**类型 `char`：字符。**字符用单引号书写，例如
`'a'`、`'b'` 和 `'c'`。它们被表示为字节&mdash;即8位
ISO 8859-1“Latin-1”编码中的整数&mdash;。上半场
该范围内的字符是标准 ASCII 字符。你可以转换
带有 `char_of_int` 和 `int_of_char` 的整数与字符之间的转换。

**类型 `string`：字符串。** 字符串是字符序列。它们是
用双引号书写，例如 `"abc"`。  字符串连接运算符
是 `^`：

```{code-cell} ocaml
"abc" ^ "def"
```

面向对象语言通常提供可重写的方法来转换
对象到字符串，例如 Java 中的 `toString()` 或 Python 中的 `__str__()` 。但是
大多数 OCaml 值不是对象，因此需要另一种方法来转换为
字符串。对于三种基本类型，有内置函数：
`string_of_int`、`string_of_float`、`string_of_bool`。  奇怪的是，
没有`string_of_char`，但是库函数`String.make`可以
用于实现相同的目标。

```{code-cell} ocaml
string_of_int 42
```

```{code-cell} ocaml
String.make 1 'z'
```

同样，对于相同的三种基本类型，也有内置函数可以
如果可能的话，从字符串转换：`int_of_string`、`float_of_string` 和
`bool_of_string`。

```{code-cell} ocaml
int_of_string "123"
```

```{code-cell} ocaml
:tags: ["raises-exception"]
int_of_string "not an int"
```

没有 `char_of_string`，但字符串的各个字符可以
通过基于 0 的索引访问。索引运算符由点和组成
方括号：

```{code-cell} ocaml
"abc".[0]
```

```{code-cell} ocaml
"abc".[1]
```

```{code-cell} ocaml
:tags: ["raises-exception"]
"abc".[3]
```

## 更多运算符

我们已经介绍了上面的大部分内置运算符，但还有一些
你可以在 [OCaml 手册][ops]中看到。

OCaml中有两个相等运算符，`=`和`==`，对应
不等式运算符 `<>` 和 `!=`。运算符 `=` 和 `<>` 检查*结构*
平等，而 `==` 和 `!=` 检查*物理*平等。直到我们研究完
OCaml 的命令式特性，它们之间的区别很难区分
解释一下。如果你现在好奇，请参阅 `Stdlib.(==)` 的 [documentation][stdlib] 。

```{important}
现在开始训练自己使用 `=` 而不是使用 `==`。这将是
如果你来自像 Java 这样的语言，其中 `==` 是常见的，那么这会很困难
相等运算符。
```

[ops]: https://ocaml.org/manual/expr.html#ss%3Aexpr-operators
[stdlib]: https://ocaml.org/api/Stdlib.html

## 断言

表达式 `assert e` 计算 `e`。如果结果是 `true`，仅此而已
发生时，整个表达式的计算结果为一个名为 *unit* 的特殊值。
单元值写作`()`，其类型为`unit`。但如果结果是
`false`，引发异常。

测试函数 `f` 的一种方法是编写一系列如下断言：

```ocaml
let () = assert (f input1 = output1)
let () = assert (f input2 = output2)
let () = assert (f input3 = output3)
```

这些断言 `f input1` 应该是 `output1`，等等。
其中 `let () = ...` 部分用于处理每个返回的单位值
断言。

## 如果表达式

{{ video_embed | replace("%%VID%%", "XJ6QPtlPD7s")}}

如果 `e1` 计算结果为 `if e1 then e2 else e3` ，则表达式 `if e1 then e2 else e3` 计算结果为 `e2`
`true`，否则为 `e3`。我们将 `e1` 称为 `if` 表达式的 *guard*。

```{code-cell}
if 3 + 5 > 2 then "yay!" else "boo!"
```

与你可能在命令式中使用的 `if-then-else` *语句*不同
语言，OCaml 中的 `if-then-else` *表达式* 就像任何其他语言一样
表达；它们可以放在表达式可以到达的任何地方。这使得他们
类似于你可能在其他中使用过的三元运算符 `? :`
语言。

```{code-cell}
4 + (if 'a' = 'b' then 1 else 2)
```

`If` 表达式可以以一种愉快的方式嵌套：

```ocaml
if e1 then e2
else if e3 then e4
else if e5 then e6
...
else en
```

你应该将最后的 `else` 视为强制性的，无论你是否
编写单个 `if` 表达式或高度嵌套的 `if` 表达式。如果你
忽略它，你可能会收到一条目前难以理解的错误消息：

```{code-cell}
:tags: ["raises-exception"]
if 2 > 3 then 5
```

+++

**语法。** `if` 表达式的语法：

```ocaml
if e1 then e2 else e3
```

此处使用字母 `e` 来表示任何其他 OCaml 表达式；这是一个
*语法变量*又名*元变量*的示例，它实际上不是
OCaml 语言本身中的变量，而是某个特定的名称
句法结构。字母 `e` 后面的数字用于
区分它的三种不同出现。

**动态语义。** `if` 表达式的动态语义：

* 如果 `e1` 计算结果为 `true`，并且 `e2` 计算结果为值 `v`，则
`if e1 then e2 else e3` 计算结果为 `v`

* 如果 `e1` 计算结果为 `false`，并且 `e3` 计算结果为值 `v`，则
`if e1 then e2 else e3` 的计算结果为 `v`。

我们将这些称为“求值规则”：它们定义如何求值表达式。注意事项
如何使用两条规则来描述 `if` 表达式的求值，其中一条用于
当守卫为真时，一个为当守卫为假时。字母 `v` 是
此处用于表示任何 OCaml 值；这是元变量的另一个例子。
稍后我们将开发一种更数学的方式来表达动态语义，
但现在我们将坚持这种更非正式的解释方式。

**静态语义。** `if` 表达式的静态语义：

* 如果 `e1` 具有类型 `bool` 且 `e2` 具有类型 `t` 且 `e3` 具有类型 `t` 则
`if e1 then e2 else e3` 的类型为 `t`

我们称之为*打字规则*：它描述了如何对表达式进行类型检查。注意事项
如何只需要一条规则来描述 `if` 表达式的类型检查。
在编译时，当完成类型检查时，无论是否
守卫是真还是假；事实上，编译器无法知道什么
守卫在运行时将具有的值。这里的字母`t`用来表示
任何 OCaml 类型； OCaml 手册也有 [all types][types] 的定义
（奇怪的是，它没有命名语言的基本类型，如 `int` 和
`bool`)。

[types]: https://ocaml.org/manual/types.html

我们会经常写“has type”，所以让我们介绍一个更紧凑的
它的符号。每当我们写“`e` has type `t`”时，让我们写
`e : t`。冒号发音为“has type”。冒号的这种用法是一致的
顶层在计算你输入的表达式后如何响应：

```{code-cell}
let x = 42
```
在上面的示例中，变量 `x` 的类型为 `int`，这就是冒号的类型
表示。

## Let 表达式

{{ video_embed | replace("%%VID%%", "ug3L97FXC6A")}}

到目前为止，在我们使用 `let` 这个词时，我们一直在
顶层和 `.ml` 文件中。例如，
```{code-cell}
let x = 42;;
```
将 `x` 定义为 42，之后我们可以在以后的定义中使用 `x`
顶层。我们将 `let` 的这种使用称为 *let 定义*。

`let` 还有另一种用途，即作为表达式：
```{code-cell}
let x = 42 in x + 1
```
这里我们将一个值绑定到名称 `x` 然后在内部使用该绑定
另一个表达式，`x+1`。我们将 `let` 的这种使用称为 *let 表达式*。
由于它是一个表达式，因此它的计算结果是一个值。这不同于
定义，它们本身不会求值为任何值。你可以看到如果
你尝试将 let 定义放在需要表达式的位置：
```{code-cell}
:tags: ["raises-exception"]
(let x = 42) + 1
```
从语法上讲，`let` 定义不允许出现在
`+` 运算符，因为那里需要一个值，并且定义不会计算
到价值观。另一方面， `let` 表达式可以正常工作：
```{code-cell}
(let x = 42 in x) + 1
```

理解顶层的 let 定义的另一种方法是它们就像
let 表达式，我们还没有提供主体表达式。
隐含地，该身​​体表情就是我们将来键入的任何其他内容。对于
例如，
```ocaml
# let a = "big";;
# let b = "red";;
# let c = a ^ b;;
# ...
```
OCaml 的理解方式与
```ocaml
let a = "big" in
let b = "red" in
let c = a ^ b in
...
```
后一系列 `let` 绑定是惯用的几个变量
可以绑定在给定的代码块内。

**语法。**

```ocaml
let x = e1 in e2
```

像往常一样，`x` 是一个标识符。这些标识符必须以小写字母开头，
不是上层，并且通常用 `snake_case` 而不是 `camelCase` 来编写。我们
将 `e1` 称为*绑定表达式*，因为它是绑定到 `x` 的内容；和
我们将 `e2` 称为*主体表达式*，因为这是代码主体，其中
绑定将在范围内。

**动态语义。**

要对 `let x = e1 in e2` 求值：

* 将 `e1` 计算为值 `v1`。

* 将 `e2` 中的 `x` 替换为 `v1`，生成新表达式 `e2'`。

* 将 `e2'` 计算为值 `v2`。

* let 表达式的求值结果是 `v2`。

这是一个例子：
```text
    let x = 1 + 4 in x * 3
-->   (evaluate e1 to a value v1)
    let x = 5 in x * 3
-->   (substitute v1 for x in e2, yielding e2')
    5 * 3
-->   (evaluate e2' to v2)
    15
      (result of evaluation is v2)
```

**静态语义。**

* 如果 `e1 : t1` 且假设 `x : t1` 则成立
`e2 : t2`，然后`(let x = e1 in e2) : t2`。

我们使用上面的括号只是为了清楚起见。像往常一样，编译器的类型
推理器确定变量的类型是什么，或者程序员可以
使用以下语法显式注释它：
```ocaml
let x : t = e1 in e2
```

## 作用域

{{ video_embed | replace("%%VID%%", "_TpTC6eo34M")}}

`Let` 绑定仅在它们出现的代码块中有效。这个
这正是你在几乎所有现代编程语言中所习惯的。对于
示例：
```ocaml
let x = 42 in
  (* y is not meaningful here *)
  x + (let y = "3110" in
         (* y is meaningful here *)
         int_of_string y)
```
变量的*范围*是其名称有意义的地方。变量 `y` 位于
作用域仅在上面绑定它的 `let` 表达式内部。

可能存在同名的重叠绑定。例如：
```ocaml
let x = 5 in
  ((let x = 6 in x) + x)
```
但这实在令人困惑，因此强烈建议不要这样做
风格。
尽管如此，让我们考虑一下该代码的含义。

该代码计算出什么值？答案归结为 `x` 是怎样的
每次发生时都会替换为一个值。以下是这种情况的几种可能性
*替代*：
```ocaml
(* possibility 1 *)
let x = 5 in
  ((let x = 6 in 6) + 5)

(* possibility 2 *)
let x = 5 in
  ((let x = 6 in 5) + 5)

(* possibility 3 *)
let x = 5 in
  ((let x = 6 in 6) + 6)
```
第一个是几乎任何合理的语言都会做的事情。而且最有可能的是
这就是你猜到的但是，**为什么？**

答案是我们称之为“名称无关原则”的东西：名称
变量的值本质上不重要。你在数学上已经习惯了这一点。对于
例如，以下两个函数是相同的：

\开始{对齐*}
f(x) &= x^2 \\
f(y) &= y^2
\结束{对齐*}

我们是否调用函数的参数本质上并不重要
$x$ 或 $y$；不管怎样，它仍然是平方函数。
因此，在程序中，这两个函数应该是相同的：
```ocaml
let f x = x * x
let f y = y * y
```
这一原则通常被称为“alpha 等价”：两个函数
相当于变量重命名，也称为 *alpha
由于历史原因而进行的转换*在这里并不重要。

根据名称无关原则，这两个表达式应该是
相同：
```ocaml
let x = 6 in x
let y = 6 in y
```
因此，有下面两个表达式，它们都有上面的表达式
嵌入其中，也应该是相同的：
```ocaml
let x = 5 in (let x = 6 in x) + x
let x = 5 in (let y = 6 in y) + x
```
但为了使它们相同，我们**必须**选择三个中的第一个
上面的可能性。它是唯一一个使变量的名称成为
无关紧要。

有一个常用术语来描述这种现象：变量的新绑定
*隐藏*变量名称的任何旧绑定。打个比方来说，就好像
新绑定暂时在旧绑定上投射阴影。但最终
当阴影消退时，旧的装订可能会重新出现。

{{ video_embed | replace("%%VID%%", "4SqMkUwakEA")}}

阴影不是可变分配。例如，以下两者
表达式的值为 11：
```ocaml
let x = 5 in ((let x = 6 in x) + x)
let x = 5 in (x + (let x = 6 in x))
```
同样，以下 utop 转录本不是可变赋值，尽管在
首先看起来可能是这样的：
```ocaml
# let x = 42;;
val x : int = 42
# let x = 22;;
val x : int = 22
```

回想一下，顶层中的每个 `let` 定义实际上都是一个嵌套的 `let`
表达。所以上面的内容实际上如下：
```ocaml
let x = 42 in
  let x = 22 in
    ... (* whatever else is typed in the toplevel *)
```
思考这个问题的正确方法是第二个 `let` 绑定一个全新的
恰好与第一个 `let` 同名的变量。

这是另一个非常值得研究的 utop 成绩单：
```ocaml
# let x = 42;;
val x : int = 42
# let f y = x + y;;
val f : int -> int = <fun>
# f 0;;
: int = 42
# let x = 22;;
val x : int = 22
# f 0;;
- : int = 42  (* x did not mutate! *)
```

总而言之，每个 let 定义都绑定一个全新的变量。如果那个新的
变量恰好与旧变量同名，新变量
暂时掩盖旧的。但旧的变量仍然存在，并且它
价值是不可变的：它永远不会改变。所以即使 `let` 表达式
表面上可能看起来像命令式语言中的赋值语句，
它们实际上是完全不同的。

## 类型注解

OCaml 自动推断每个表达式的类型，无需
程序员手动编写。尽管如此，有时它还是有用的
手动指定所需的表达式类型。 *类型注释*可以
那：

```{code-cell} ocaml
(5 : int)
```

不正确的注释将产生编译时错误：

```{code-cell} ocaml
:tags: ["raises-exception"]
(5 : float)
```

该示例说明了为什么你可以在期间使用手动类型注释
调试。  也许你忘记了 `5` 不能被视为 `float`，
你尝试写：

```ocaml
5 +. 1.1
```

你可以尝试手动指定 `5` 应该是 `float`：

```{code-cell} ocaml
:tags: ["raises-exception"]
(5 : float) +. 1.1
```

很明显，类型注释失败了。虽然这可能看起来很愚蠢
对于这个小程序，你可能会发现这种技术作为程序很有效
变大。

```{important}
类型注释不是** *类型转换*，例如 C 或 Java 中可能存在的类型注释。
它们并不表示从一种类型到另一种类型的转换。相反，他们表明
检查表达式是否确实具有给定类型。
```

**语法。** 类型注释的语法：

```ocaml
(e : t)
```

请注意，括号是必需的。

**动态语义。** 类型注释没有运行时含义。
它在编译期间消失，因为它指示编译时检查。
没有运行时转换。
因此，如果 `(e : t)` 编译成功，那么在运行时它只是 `e`，
它的计算结果与 `e` 相同。

**静态语义。** 如果 `e` 具有类型 `t`，则 `(e : t)` 具有类型 `t`。
