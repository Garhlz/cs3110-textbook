# 编译 OCaml 程序

把 OCaml 当成交互式计算器来用确实很有意思，但这样没法走得太远，更别说编写大型程序了。我们需要把代码保存到文件里，再对它们进行编译。

## 将代码保存到文件中

打开终端，创建一个新目录，然后在那个目录中打开 VS Code。比如，可以执行下面的命令：

```console
$ mkdir hello-world
$ cd hello-world
```

```{warning}
不要把 Unix 家目录的根目录当作存放这些文件的地方。我们很快就要使用的构建系统 Dune，在家目录根目录下可能无法正常工作。请使用家目录中的某个子目录。
```

用 VS Code 新建一个名为 `hello.ml` 的文件，并输入以下代码：

```ocaml
let _ = print_endline "Hello world!"
```

```{note}
这一行末尾没有双分号 `;;`。双分号是给顶层里的交互式会话用的，好让顶层知道你已经输入完一段代码。在 `.ml` 文件里通常没有理由写它。
```

上面的 `let _ =` 表示：我们不打算给 `=` 右边那段代码起名字，所以用了一个“空白名”或下划线 `_`。

保存文件并回到命令行。然后编译代码：

```console
$ ocamlc -o hello.byte hello.ml
```

编译器名叫 `ocamlc`。选项 `-o hello.byte` 表示把输出的可执行文件命名为 `hello.byte`。这个可执行文件里包含的是编译后的 OCaml 字节码。此外还会生成另外两个文件：`hello.cmi` 和 `hello.cmo`。现在先不用关心它们。接着运行可执行文件：

```console
$ ./hello.byte
```

它应该会打印 `Hello world!`，然后结束运行。

现在把输出的字符串改成你自己想要的内容。保存文件，重新编译，再重新运行。也可以试试让它打印多行内容。

在编辑器和命令行之间来回进行“编辑 - 编译 - 运行”的循环，如果你以前习惯一直在 Eclipse 这类 IDE 里工作，可能一开始会觉得不太熟悉。不过不用担心，很快这就会变成一种自然的工作方式。

现在把刚才生成的文件清理掉：

```console
$ rm hello.byte hello.cmi hello.cmo
```

## 那么 `main` 呢？

和 C 或 Java 不同，OCaml 程序不需要一个名为 `main` 的特殊函数来作为入口。通常的习惯写法是：让文件中的最后一个定义承担“主函数”的角色，启动所需的计算。

## Dune

在更大的项目里，我们不想手动调用编译器，也不想手动清理文件。相反，我们希望借助*构建系统*自动查找并链接库。OCaml 以前有一个较老的构建系统 `ocamlbuild`，现在更常用的是较新的构建系统 Dune。类似的系统还有 Unix 世界里长期用于 C 等语言的 `make`，以及 Java 生态中的 Gradle、Maven 和 Ant。

Dune *项目*是一个目录（及其子目录），里面包含你想要编译的 OCaml 代码。项目的*根目录*是这棵目录树里层级最高的那个目录。一个项目还可能依赖外部*包*提供的额外代码，这些代码通常已经预先编译好。一般来说，这些包通过 OCaml 的包管理器 OPAM 安装。

项目中的每个目录都可以包含一个名为 `dune` 的文件。这个文件告诉 Dune：该目录及其子目录中的代码应当如何编译。Dune 文件使用一种源自 LISP 的函数式语法，叫做 *s-expression*（S 表达式）。它用括号来表示嵌套的数据结构，从而形成树状结构，有点像 HTML 标签的组织方式。Dune 文件的语法可见 [Dune 手册][dune-man]。

[dune-man]: https://dune.readthedocs.io/en/stable/reference/dune/index.html

### 手动创建 Dune 项目

下面用一个小例子说明 Dune 的用法。在与 `hello.ml` 相同的目录中，新建一个名为 `dune` 的文件，并写入：

```text
(executable
 (name hello))
```

这表示声明了一个*可执行文件*（也就是可运行的程序），它的主文件是 `hello.ml`。

再创建一个名为 `dune-project` 的文件，并写入：

```text
(lang dune 3.21)
```

这告诉 Dune：该项目使用 Dune 3.21 版本。这个版本是本教材发布时的当前版本。这个*项目*文件是必须放在项目源代码树根目录中的。一般来说，源代码树的每个子目录里都可能有一个 `dune` 文件，但 `dune-project` 在根目录里通常只有一个。

然后在终端运行：

```console
$ dune build hello.exe
```

注意，Dune 在所有平台上都使用 `.exe` 后缀，不只是 Windows。这个命令会让 Dune 构建一个*本机*可执行文件，而不是字节码可执行文件。

Dune 会创建一个 `_build` 目录，并在里面编译程序。这也是构建系统相较于直接调用编译器的一个优势：不会把一堆生成文件散落到源代码目录里，而是统一放到单独的目录中。Dune 会在 `_build` 里生成很多文件。我们的可执行文件在比较深的路径中：

```console
$ _build/default/hello.exe
Hello world!
```

不过，Dune 提供了一个快捷方式，你不必记住并手动输入这一长串路径。若想一步完成构建和执行，只需运行：

```console
$ dune exec ./hello.exe
Hello world!
```

最后，要清理所有编译产物，只需要运行：

```console
$ dune clean
```

这会删除 `_build` 目录，只保留你的源代码。

```{tip}
Dune 编译程序时，会把源文件缓存一份到 `_build/default` 里。如果你哪天不小心误操作，导致源文件丢失，有时可以尝试从 `_build` 里恢复。当然，更推荐直接使用 git 之类的版本控制工具。
```

```{warning}
不要编辑 `_build` 目录中的任何文件。如果你在保存文件时看到“只读”错误，很可能是因为你正在编辑 `_build` 目录里的文件。
```

### 自动创建 Dune 项目

在终端中切换到你想保存项目的目录，比如 `"~/work"`。给项目起一个名字，例如 `"calculator"`。然后运行：

```console
$ dune init project calculator
$ cd calculator
$ code .
```

这时 VS Code 应该已经打开，你也会看到 Dune 为这个项目自动生成的文件。

在 `calculator` 目录中打开终端，运行：

```console
$ dune exec bin/main.exe
```

它会打印 `Hello, World!`

```{tip}
如果你使用 `ocamlformat` 自动格式化源代码，请注意 Dune 不会自动为项目添加 `.ocamlformat` 文件。你可能会想在项目的顶层目录，也就是项目的*根目录*，手动添加一个。这个目录里应当包含 `dune-project` 文件。
```

### 持续运行 Dune

运行 `dune build` 时，Dune 只会编译一次项目。你可能希望每次在项目中保存文件时都自动重新编译。要做到这一点，可以运行：

```console
$ dune build --watch
```

Dune 会提示它正在等待文件系统变化。这表示 Dune 会持续运行，并在你每次于 VS Code 中保存文件时重新构建项目。若要停止 Dune，按 `Control+C` 即可。
