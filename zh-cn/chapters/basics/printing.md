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

# 打印

OCaml 具有针对一些内置原语的内置打印函数
类型：`print_char`、`print_string`、`print_int` 和 `print_float`。有
还有一个 `print_endline` 函数，类似于 `print_string`，但也输出
换行符。

```{code-cell} ocaml
print_endline "Camels are bae"
```

## Unit

让我们看一下其中几个函数的类型：
```{code-cell} ocaml
print_endline
```

```{code-cell} ocaml
print_string
```

它们都接受一个字符串作为输入并返回一个 `unit` 类型的值，我们
以前没见过。该类型只有一个值，写为 `()`
也读作“unit”。所以 `unit` 类似于 `bool`，只不过
`unit` 类型的值比 `bool` 类型的值少。

当你需要接受参数或返回值，但没有
有意义的值要传递或返回时，就会使用 `unit`。它相当于 Java 中的 `void`，
也类似于 Python 中的 `None`。编写或使用有副作用的代码时，
经常会用到 `unit`。打印就是副作用的一个例子：它会改变
外部世界，而且这种改变无法撤销。

## 分号

如果你想打印一件又一件，你可以按顺序打印一些东西
使用嵌套 `let` 表达式的函数：

```{code-cell} ocaml
let _ = print_endline "Camels" in
let _ = print_endline "are" in
print_endline "bae"
```

上面的 `let _ = e` 语法是一种求值 `e` 但不把
结果绑定到任何名字的方式。事实上，我们知道每个 `print_endline`
函数都会返回什么：它始终返回 `()`，也就是 unit 值。
所以没有充分理由把它绑定到变量名。我们也可以写 `let () = e`，
表明我们知道这只是一个不关心的 unit 值：

```{code-cell} ocaml
let () = print_endline "Camels" in
let () = print_endline "are" in
print_endline "bae"
```

但无论哪种写法，所有这些 `let..in` 样板都很烦人。
所以 OCaml 提供了一种特殊语法，用来串联多个返回 `unit` 的函数。
表达式 `e1; e2` 会先求值 `e1`，它应该求值为 `()`，
然后丢弃该值，并求值 `e2`。所以我们可以将上面的代码改写为：

```{code-cell} ocaml
print_endline "Camels";
print_endline "are";
print_endline "bae"
```

这是更惯用的 OCaml 代码，而且对于命令式来说它看起来也更自然
程序员。

```{warning}
在该示例中，最后一个 `print_endline` 之后没有分号。一个常见的
错误是在每个打印语句*之后*放置一个分号。相反，
分号严格位于*语句之间*。也就是说，分号是一个语句
*分隔符*不是语句*终止符*。如果你要在
最后，根据周围的代码，你可能会收到语法错误。
```

## Ignore

如果 `e1` 没有类型 `unit`，那么 `e1; e2` 将给出警告，因为
你正在丢弃一个潜在有用的值。如果这确实是你的意图，那么你
可以调用内置函数 `ignore : 'a -> unit` 将任意值转换为
`()`：

```{code-cell} ocaml
(ignore 3); 5
```

实际上 `ignore` 很容易自己实现：

```{code-cell} ocaml
let ignore x = ()
```

或者你甚至可以写下划线来表示该函数接受一个值，
但不把该值绑定到名称。这意味着该函数体内永远不能使用这个值。
但这没关系：我们本来就想忽略它。

```{code-cell} ocaml
let ignore _ = ()
```

## Printf

对于复杂的文本输出，使用原始类型的内置函数
打印很快就会变得乏味。例如，假设你想写一个
打印统计数据的函数：

```{code-cell} ocaml
(** [print_stat name num] prints [name: num]. *)
let print_stat name num =
  print_string name;
  print_string ": ";
  print_float num;
  print_newline ()
```

```{code-cell} ocaml
print_stat "mean" 84.39
```

我们如何缩短`print_stat`？在 Java 中，你可以使用重载的 `+`
运算符将所有对象转换为字符串：

```java
void print_stat(String name, double num) {
   System.out.println(name + ": " + num);
}
```

但 OCaml 值不是对象，并且它们没有 `toString()` 方法
它们继承自某个根 `Object` 类。OCaml 也不允许重载
运算符。

不过很久以前，FORTRAN 发明了一种与其他语言不同的解决方案
C 和 Java 甚至 Python 支持。这个想法是使用*格式说明符*来
&mdash;顾名思义&mdash;指定如何格式化输出。
这个想法最出名的名字可能是“printf”，它来自 C 语言中
实现它的库函数。许多其他语言和库仍然
使用该名称，包括 OCaml 的 `Printf` 模块。

以下是我们如何使用 `printf` 重新实现 `print_stat`：

```{code-cell} ocaml
let print_stat name num =
  Printf.printf "%s: %F\n%!" name num
```

```{code-cell} ocaml
print_stat "mean" 84.39
```

函数 `Printf.printf` 的第一个参数是格式说明符。它
*看起来*像一个字符串，但它的含义远不止于此。其实是
OCaml 编译器非常深入地理解了这一点。里面的格式
说明符有：

- 普通字符，以及

- 转换说明符，以 `%` 开头。

有大约两打可用的转换说明符，你可以阅读
大约在 [documentation of `Printf`][printf-doc] 中。让我们来拆解一下
以上面的格式说明符为例。

[printf-doc]: https://ocaml.org/api/Printf.html

- 它以 `"%s"` 开头，这是字符串的转换说明符。  这意味着
`printf` 的下一个参数必须是 `string`，并且该字符串的内容
  将被输出。

- 它以 `": "` 继续，这些只是普通字符。它们会被插入
到输出中。

- 然后它有另一个转换说明符 `%F`。这意味着下一个参数
`printf` 必须具有类型 `float`，并且将以与
  OCaml 用于打印浮点数。

- 之后的换行符 `"\n"` 是另一个纯字符序列。

- 最后，转换说明符 `"%!"` 表示*刷新输出缓冲区*。
正如你在早期的编程课程中可能已经学到的那样，输出通常是
  *缓冲*，这意味着它不会同步或立即发生。刷新
  缓冲区可以确保仍在缓冲区中的任何内容都会被输出
  立即。这个说明符的特殊之处在于它实际上不需要
  `printf` 的另一个参数。

如果参数的类型相对于转换说明符不正确，
OCaml 会检测到这一点。  让我们添加一个类型注释来强制 `num` 成为一个
`int`，看看浮点转换说明符 `%F` 会发生什么：

```{code-cell} ocaml
:tags: ["raises-exception"]
let print_stat name (num : int) =
  Printf.printf "%s: %F\n%!" name num
```

为了解决这个问题，我们可以更改为 `int` 的转换说明符，即 `%i`：

```{code-cell} ocaml
let print_stat name num =
  Printf.printf "%s: %i\n%!" name num
```

`printf` 的另一个非常有用的变体是 `sprintf`，它收集输出
在字符串中而不是打印它：

```{code-cell} ocaml
let string_of_stat name num =
  Printf.sprintf "%s: %F" name num
```

```{code-cell} ocaml
string_of_stat "mean" 84.39
```
