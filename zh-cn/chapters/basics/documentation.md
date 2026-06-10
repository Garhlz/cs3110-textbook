# 文档

OCaml 提供了一个名为 OCamldoc 的工具，它的工作方式很像 Java 的 Javadoc：从源代码中提取特定格式的注释，并将其渲染成 HTML，方便程序员阅读文档。

## 如何写文档

下面是一个 OCamldoc 注释的例子：

```ocaml
(** [sum lst] is the sum of the elements of [lst]. *)
let rec sum lst = ...
```

* 双星号会让这条注释被识别为 OCamldoc 注释。

* 注释中带方括号的部分，在 HTML 中会以 `typewriter font` 而不是普通字体显示。

和 Javadoc 一样，OCamldoc 也支持*文档标签*（documentation tags），例如 `@author`、`@deprecated`、`@param`、`@return` 等。

关于 OCamldoc 注释中可用的完整标记语法，可以参考 [OCamldoc 手册](https://ocaml.org/manual/ocamldoc.html)。不过，这里介绍的内容已经足够覆盖你大多数时候需要编写的文档了。

## 写什么文档

本书所偏好的文档风格，和 OCaml 标准库很接近：简洁、声明式。还是以 `sum` 为例：

```ocaml
(** [sum lst] is the sum of the elements of [lst]. *)
let rec sum lst = ...
```

这条注释以 `sum lst` 开头，这是一个把函数应用到参数上的示例。接着用 `is` 来声明式地说明这个应用的结果。（当然也可以用 `returns`，但 `is` 更能体现函数的数学意味。）在这段描述里，参数名 `lst` 被直接拿来解释结果。

注意，这里完全不需要像 Javadoc 那样，再额外加标签去重复描述参数和返回值。需要说的信息其实已经都说完了。我们非常不推荐下面这种写法：

```ocaml
(** Sum a list.
    @param lst The list to be summed.
    @return The sum of the list. *)
let rec sum lst = ...
```

这份糟糕的文档用了三行、而且并不好读，只是表达了那条清晰的一行版本已经表达过的同样内容。

如果想进一步改进已有的文档，一个办法是把空列表的情况也明确写出来：

```ocaml
(** [sum lst] is the sum of the elements of [lst].
    The sum of an empty list is 0. *)
let rec sum lst = ...
```

## 前置条件与后置条件

下面再看几个符合我们偏好风格的注释示例：

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

`index` 的文档说明了这个函数会抛出异常，也说明了异常是什么，以及在什么条件下会抛出。（我们会在下一章更详细地讨论异常。）`random_int` 的文档则说明了该函数参数必须满足某个条件。

在之前的课程里，你应该已经接触过*前置条件*（precondition）和*后置条件*（postcondition）的概念。前置条件是某段代码执行之前必须为真的条件；后置条件则是代码执行之后必须为真的条件。

`random_int` 文档中的 `Requires` 子句就是一种前置条件。它表示：`random_int` 的调用者有责任保证 `bound` 的值满足这个条件。相应地，同一条文档中的第一句话则是一种后置条件，它保证了函数返回值具有什么性质。

`index` 文档中的 `Raises` 子句则是另一种后置条件。它保证了该函数会抛出某个异常。注意，尽管这个子句用输入条件来表述，但它并不是前置条件。

还要注意，这几个例子里都没有写“某个输入必须是什么类型”这样的 `Requires` 子句。如果你来自 Python 这类动态类型语言，这可能会让你有点意外。Python 程序员经常会把“函数参数必须是什么类型”写成前置条件；但 OCaml 程序员通常不会这么做。原因在于：编译器自己就会完成类型检查，保证你不会把错误类型的值传给函数。

再看 `lowercase_ascii`。虽然英文注释本身已经有助于读者看出 `c` 的类型，但它并不会再额外写出像下面这样的 `Requires` 子句：

```ocaml
(** [lowercase_ascii c] is the lowercase ASCII equivalent of [c].
    Requires: [c] is a character. *)
```

对于 OCaml 程序员来说，这种注释显得非常不符合习惯。他们读到时很可能会疑惑：“`c` 当然是字符啊，编译器本来就会保证这一点。写这句话的人到底真正想表达什么？是他漏了什么，还是我漏了什么？”
