# 编译 OCaml 程序

使用 OCaml 作为一种交互式计算器可能很有趣，但我们无法以这种方式编写大型程序。我们需要将代码存储在文件中并编译它们。

## 将代码存储在文件中

打开终端，创建一个新目录，然后在该目录中打开 VS Code。
例如，你可以使用以下命令：

```console
$ mkdir hello-world
$ cd hello-world
```

```{warning}
不要使用 Unix 主目录的根目录作为存储文件的位置。
我们很快就要使用的构建系统，Dune，可能无法正常工作
你的主目录的根目录。相反，你需要使用你的子目录
主目录。
```

使用 VS Code 创建一个名为 `hello.ml` 的新文件。将以下代码输入到
文件：

```ocaml
let _ = print_endline "Hello world!"
```

```{note}
该行代码末尾没有双分号 `;;` 。双
分号用于顶层的交互式会话，以便
toplevel 知道你已完成输入一段代码。通常没有理由
将其写入 .ml 文件中。
```

上面的 `let _ =` 意味着我们不关心给出名称（因此是“空白”）
或下划线）在 `=` 的右侧进行编码。

保存文件并返回到命令行。  编译代码：

```console
$ ocamlc -o hello.byte hello.ml
```

编译器名为 `ocamlc`。 `-o hello.byte` 选项表示命名
输出可执行文件`hello.byte`。可执行文件包含已编译的 OCaml 字节码。
此外，还会生成另外两个文件：`hello.cmi` 和 `hello.cmo`。我们不
现在需要关心这些文件。运行可执行文件：

```console
$ ./hello.byte
```

它应该打印 `Hello world!` 并终止。

现在将打印的字符串更改为你选择的字符串。保存
文件、重新编译并重新运行。尝试让代码打印多行。

编辑器和命令行之间的编辑-编译-运行循环是很重要的
如果你习惯在 Eclipse 等 IDE 中工作，这可能会让你感到陌生。
不用担心;它很快就会成为第二天性。

现在让我们清理所有生成的文件：

```console
$ rm hello.byte hello.cmi hello.cmo
```

## Main 呢？

与 C 或 Java 不同，OCaml 程序不需要具有名为
`main` 被调用以启动程序。通常的习语是 just to have the
文件中的最后一个定义作为启动的主函数
无论要进行什么计算。

## Dune

在较大的项目中，我们不想运行编译器或手动清理。
相反，我们希望使用*构建系统*来自动查找并链接
库。 OCaml 有一个名为 ocamlbuild 的遗留构建系统，以及一个较新的构建系统
系统称为Dune。类似的系统包括`make`，它长期以来一直被用于
C 和其他语言的 Unix 世界；以及 Gradle、Maven 和 Ant，它们是
与 Java 一起使用。

Dune *项目* 是包含 OCaml 代码的目录（及其子目录）
你想要编译。项目的*root*是其最高目录
层次结构。项目可能依赖外部*包*提供额外的代码
已经编译好了。通常，软件包与 OPAM（OCaml）一起安装
包管理器。

项目中的每个目录都可以包含一个名为 `dune` 的文件。那个文件
向 Dune 描述你希望该目录（和子目录）中的代码如何
待编译。 Dune 文件使用源自以下版本的函数式编程语法：
LISP 称为*s-表达式*，其中括号用于显示嵌套数据
形成一棵树，就像 HTML 标签一样。 Dune 文件的语法已记录
在 [Dune 手册][dune-man] 中。

[dune-man]: https://dune.readthedocs.io/en/stable/reference/dune/index.html

### 手动创建 Dune 项目

这是一个如何使用 Dune 的小示例。在与 `hello.ml` 相同的目录中，
创建一个名为 `dune` 的文件并将以下内容放入其中：

```text
(executable
 (name hello))
```

声明一个*可执行文件*（可以执行的程序），其主文件
是 `hello.ml`。

另外创建一个名为 `dune-project` 的文件并在其中放入以下内容：

```text
(lang dune 3.21)
```

这告诉 Dune 该项目使用 Dune 版本 3.21，当前版本为
该版本教材的发布时间。这个*项目*文件是
在要编译的每个源代码树的根目录中都需要
Dune。一般来说，源代码的每个子目录中都会有一个 `dune` 文件
树，但根部只有一个 `dune-project` 文件。

然后从终端运行此命令：

```console
$ dune build hello.exe
```

请注意，Dune 在所有平台上都使用 `.exe` 扩展，而不仅仅是在
Windows。这会导致 Dune 构建*本机*可执行文件而不是字节码
可执行的。

Dune 将创建一个目录 `_build` 并在其中编译我们的程序。那是
与直接运行编译器相比，构建系统的一个好处是：而不是
用一堆生成的文件污染你的源目录，他们得到
在单独的目录中干净地创建。 `_build`里面有很多文件
由Dune创建的。我们的可执行文件被埋藏在下面几层：

```console
$ _build/default/hello.exe
Hello world!
```

但 Dune 提供了一条捷径，让你无需记住并输入所有这些内容。
要一步构建并执行程序，我们只需运行：

```console
$ dune exec ./hello.exe
Hello world!
```

最后，为了清理我们刚刚运行的所有编译代码：

```console
$ dune clean
```

这会删除 `_build` 目录，只留下源代码。

```{tip}
当 Dune 编译你的程序时，它会把源文件的副本缓存在
`_build/default` 中。如果你不小心犯错导致源文件丢失，
也许可以从 `_build` 里面恢复。当然，使用 git 这样的源代码管理工具也很明智。
```

```{warning}
不要编辑 `_build` 目录中的任何文件。如果你在尝试保存只读文件时遇到错误，则你可能正在尝试编辑 `_build` 目录中的文件。
```

### 自动创建 Dune 项目

在终端中，切换到你要存储工作的目录，例如"~/work"。为项目选择一个名称，例如"calculator"。然后运行：

```console
$ dune init project calculator
$ cd calculator
$ code .
```

你现在应该打开 VS Code 并查看 Dune 自动为你的项目生成的文件。

从 `calculator` 目录中的终端运行：

```console
$ dune exec bin/main.exe
```

它将打印 `Hello, World!`

```{tip}
如果你使用 ocamlformat 自动格式化源代码，请注意 Dune 不会自动将 `.ocamlformat` 文件添加到你的项目中。你可能想在项目的顶级目录（也称为 *root*）中添加一个。该目录中包含名为 `dune-project` 的文件。
```

### 持续运行 Dune

当你运行 `dune build` 时，它会编译你的项目一次。你可能希望每次在项目中保存文件时自动编译代码。为此，请运行以下命令：

```console
$ dune build --watch
```

Dune 将响应它正在等待文件系统更改。这意味着 Dune 现在会持续运行，并在你每次在 VS Code 中保存文件时重建你的项目。要停止 Dune，请按 Control+C。
