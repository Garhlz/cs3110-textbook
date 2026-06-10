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

OCaml 为少数几种内置原始类型提供了内建的打印函数：`print_char`、`print_string`、`print_int` 和 `print_float`。此外还有一个 `print_endline` 函数，它和 `print_string` 类似，但会额外输出一个换行符。

```{code-cell} ocaml
print_endline "Camels are bae"
```

## Unit

我们来看看其中几个函数的类型：

```{code-cell} ocaml
print_endline
```

```{code-cell} ocaml
print_string
```

它们都接受一个字符串作为输入，并返回一个 `unit` 类型的值。这个类型我们之前还没有见过。`unit` 类型只有一个值，写作 `()`，读作 “unit”。所以你可以把 `unit` 想成有点像 `bool`，只不过 `unit` 比 `bool` 少一个值。

当你需要接收参数或者返回值，但又没有任何“有意义的值”可传可返时，就会用到 `unit`。它相当于 Java 中的 `void`，也和 Python 里的 `None` 有些相似。`unit` 往往出现在有副作用的代码中。打印就是副作用的一个例子：它改变了外部世界，而且这种改变无法撤销。

## 分号

如果你想依次打印多样东西，可以用嵌套的 `let` 表达式来串联几个打印函数：

```{code-cell} ocaml
let _ = print_endline "Camels" in
let _ = print_endline "are" in
print_endline "bae"
```

上面的 `let _ = e` 语法表示“对 `e` 求值，但不把结果绑定到任何名字上”。其实我们已经知道，这些 `print_endline` 函数返回的永远都是 `()`，也就是那个 `unit` 值，所以完全没有必要把它绑定到某个变量名上。我们也可以写成 `let () = e`，明确表示我们知道它只是一个我们不关心的 `unit` 值：

```{code-cell} ocaml
let () = print_endline "Camels" in
let () = print_endline "are" in
print_endline "bae"
```

但无论哪种写法，这些 `let .. in` 模板代码都显得有点烦。于是 OCaml 提供了一种专门的语法，用于把多个返回 `unit` 的函数串起来。表达式 `e1; e2` 会先对 `e1` 求值，`e1` 应当求值为 `()`；然后这个值会被丢弃，再继续对 `e2` 求值。所以，上面的代码可以改写为：

```{code-cell} ocaml
print_endline "Camels";
print_endline "are";
print_endline "bae"
```

这就是更符合 OCaml 习惯的写法，而且对熟悉命令式语言的程序员来说，看上去也更自然。

```{warning}
在这个例子里，最后一个 `print_endline` 后面没有分号。一个常见错误是：在每条打印语句*后面*都加上分号。其实分号只出现在*语句之间*。也就是说，分号是语句的*分隔符*，不是语句的*终止符*。如果你在末尾再加一个分号，根据周围代码的不同，可能会引发语法错误。
```

## Ignore

如果 `e1` 的类型不是 `unit`，那么写 `e1; e2` 会收到警告，因为你丢弃了一个也许有用的值。如果你确实就是想这么做，可以调用内置函数 `ignore : 'a -> unit`，把任意值转换成 `()`：

```{code-cell} ocaml
(ignore 3); 5
```

其实 `ignore` 很容易自己实现：

```{code-cell} ocaml
let ignore x = ()
```

你甚至可以直接把参数写成下划线，表示这个函数接受一个值，但不会把它绑定到任何名字上。这也意味着函数体根本无法使用这个值。不过这正好符合我们的目的：我们就是要忽略它。

```{code-cell} ocaml
let ignore _ = ()
```

## Printf

如果要输出比较复杂的文本，仅靠原始类型对应的那些内建打印函数，很快就会变得繁琐。比如，假设你想写一个函数来打印某项统计量：

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

怎样把 `print_stat` 写得更简洁一些？在 Java 里，你可能会用重载的 `+` 运算符，把所有对象拼接成字符串：

```java
void print_stat(String name, double num) {
   System.out.println(name + ": " + num);
}
```

但 OCaml 的值不是对象，也没有从某个根类 `Object` 继承来的 `toString()` 方法。OCaml 也不允许运算符重载。

不过很久以前，FORTRAN 发明了另一种后来被 C、Java 甚至 Python 等语言采用的方案：使用*格式说明符*（format specifier）来指定输出该如何格式化。这个思路最广为人知的名字大概就是 “printf”，也就是 C 标准库中那个实现这一思路的函数名。许多语言和库今天仍沿用这个名字，包括 OCaml 的 `Printf` 模块。

下面是如何用 `printf` 重写 `print_stat`：

```{code-cell} ocaml
let print_stat name num =
  Printf.printf "%s: %F\n%!" name num
```

```{code-cell} ocaml
print_stat "mean" 84.39
```

函数 `Printf.printf` 的第一个参数是格式说明符。它*看起来*像一个字符串，但其实不只是普通字符串那么简单。OCaml 编译器会以相当深入的方式理解它。在这个格式说明符里面，有两类内容：

- 普通字符；

- 转换说明符（conversion specifier），也就是以 `%` 开头的片段。

可用的转换说明符有二十多种，详见 [`Printf` 的文档][printf-doc]。我们就以上面的格式说明符为例来拆解一下。

[printf-doc]: https://ocaml.org/api/Printf.html

- 开头的 `"%s"` 是字符串的转换说明符。这意味着 `printf` 的下一个参数必须是一个 `string`，并且该字符串的内容会被输出。

- 接着的 `": "` 只是普通字符，会原样插入到输出里。

- 然后是另一个转换说明符 `%F`。这意味着 `printf` 的下一个参数必须是 `float` 类型，并且会按 OCaml 打印浮点数时所使用的格式输出。

- 之后的 `"\n"` 是另一段普通字符序列，也就是换行。

- 最后的转换说明符 `"%!"` 表示*刷新输出缓冲区*（flush the output buffer）。你可能在之前的编程课里学过，输出通常是*带缓冲*的，也就是说它不会立刻、一次性全部显示出来。刷新缓冲区可以确保缓冲区里尚未输出的内容立刻被真正输出。这个说明符比较特殊，因为它并不需要 `printf` 再接收一个额外参数。

如果某个参数的类型和转换说明符要求不匹配，OCaml 会检测出来。比如，我们给 `num` 人为加上类型注解，强制它是 `int`，然后看看使用浮点转换说明符 `%F` 会发生什么：

```{code-cell} ocaml
:tags: ["raises-exception"]
let print_stat name (num : int) =
  Printf.printf "%s: %F\n%!" name num
```

要修正这个问题，可以把转换说明符改成 `int` 对应的 `%i`：

```{code-cell} ocaml
let print_stat name num =
  Printf.printf "%s: %i\n%!" name num
```

`printf` 还有一个非常有用的变体叫做 `sprintf`，它不会直接打印，而是把输出收集成一个字符串：

```{code-cell} ocaml
let string_of_stat name num =
  Printf.sprintf "%s: %F" name num
```

```{code-cell} ocaml
string_of_stat "mean" 84.39
```
