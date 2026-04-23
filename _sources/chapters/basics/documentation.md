# 文档

OCaml 提供了一个名为 OCamldoc 的工具，其工作方式与 Java 的 Javadoc 工具非常相似：
它从源代码中提取特殊格式的注释并将其呈现为
HTML，使程序员可以轻松阅读文档。

## 如何记录

以下是 OCamldoc 注释的示例：
```ocaml
(** [sum lst] is the sum of the elements of [lst]. *)
let rec sum lst = ...
```

* 双星号会让注释被识别为 OCamldoc
注释。

* 注释部分周围的方括号意味着这些部分应该
在 HTML 中呈现为 `typewriter font` 而不是常规字体。

与 Javadoc 一样，OCamldoc 支持*文档标签*，例如 `@author`，
`@deprecated`、`@param`、`@return` 等

有关 OCamldoc 注释中可能的全部标记，请参阅
[OCamldoc 手册](https://ocaml.org/manual/ocamldoc.html)。
但我们在这里介绍的内容对于你将要阅读的大多数文档来说已经足够了
需要编写的内容来说已经足够了。

## 记录什么

我们在本书中喜欢的文档风格类似于 OCaml 的文档风格
标准库：简洁且声明式。作为一个例子，让我们回顾一下
`sum` 的文档：
```ocaml
(** [sum lst] is the sum of the elements of [lst]. *)
let rec sum lst = ...
```

该注释以 `sum lst` 开头，这是函数应用到参数的示例。
该注释接着使用 “is” 一词，从而以声明式方式描述应用的结果。
（也可以使用 “returns” 一词，但 “is” 强调了
函数的数学本质
函数。）该描述使用参数名称 `lst` 来解释
结果。

请注意，无需添加标签来冗余描述参数或
返回值，就像 Javadoc 经常做的那样。所有需要说的
已经说过了。我们强烈反对如下文档：
```ocaml
(** Sum a list.
    @param lst The list to be summed.
    @return The sum of the list. *)
let rec sum lst = ...
```
这份糟糕的文档需要三行不必要的难以阅读的行来说明
与清晰的单行版本相同。

有一种方法可以改进我们目前拥有的文档，那就是
明确说明空列表会发生什么：
```ocaml
(** [sum lst] is the sum of the elements of [lst].
    The sum of an empty list is 0. *)
let rec sum lst = ...
```

## 前提条件和后置条件

以下是一些以我们喜欢的风格撰写的注释示例。
```ocaml
(** [lowercase_ascii c] is the lowercase ASCII equivalent of
    character [c]. *)

(** [index s c] is the index of the first occurrence of
    character [c] in string [s].  Raises: [Not_found]
    if [c] does not occur in [s]. *)

(** [random_int bound] is a random integer between 0 (inclusive)
    and [bound] (exclusive).  Requires: [bound] is greater than 0
    and less than 2^30. *)
```

`index` 的文档指定该函数引发异常，如下所示
以及该异常是什么以及引发该异常的条件。 （我们
将在下一章中更详细地介绍异常。）
`random_int` 指定函数的参数必须满足条件。

在之前的课程中，你接触过*先决条件*和
*后置条件*。前提条件是在某些事情发生之前必须为真的事情
代码片段；后置条件则是在代码执行之后必须为真的性质。

`random_int` 文档中的上述“Requires”子句是一种
前提条件。它说 `random_int` 函数的客户端是
负责保证 `bound` 的值。同样，
同一文档的第一句话是一种后置条件。它
保证函数返回值的某些内容。

`index` 文档中的“Raises”子句是另一种
后置条件。它保证该函数引发异常。
请注意，该子句不是先决条件，即使它陈述了一个条件
输入项。

请注意，这些示例都没有一个“Requires”子句来说明什么
关于输入的类型。如果你来自动态类型语言，
就像 Python 一样，这可能会令人惊讶。 Python 程序员经常记录
关于函数输入类型的前提条件。 OCaml 程序员，
然而，不这样做。这是因为编译器本身会进行类型检查
确保永远不会将错误类型的值传递给函数。考虑
`lowercase_ascii` 再次：尽管英文注释有助于识别
`c` 的类型给读者，注释没有声明“Requires”子句，例如
这个：
```ocaml
(** [lowercase_ascii c] is the lowercase ASCII equivalent of [c].
    Requires: [c] is a character. *)
```
对于 OCaml 程序员来说，这样的注释读起来非常不惯用，他们会
阅读该注释并感到困惑，也许会想：“当然 `c` 是一个
字符；编译器会保证这一点。写这句话的人到底想表达什么？
他们遗漏了什么，还是我遗漏了什么？”
