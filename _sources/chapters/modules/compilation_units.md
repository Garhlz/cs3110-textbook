# 编译单元

{{ video_embed | replace("%%VID%%", "hjZ8FvMUw2k")}}

*编译单元*是同一目录下的一对 OCaml 源文件
目录。它们共享相同的基本名称，称之为 `x`，但是它们的
扩展名不同：一个文件是 `x.ml`，另一个是 `x.mli`。该文件
`x.ml` 称为*实现*，而 `x.mli` 称为
*接口*。

例如，假设 `foo.mli` 恰好包含以下内容：

```ocaml
val x : int
val f : int -> int
```

和 `foo.ml` 在同一目录中，包含以下内容：

```ocaml
let x = 0
let y = 12
let f x = x + y
```

然后编译`foo.ml`将与定义模块具有相同的效果
`Foo` 如下：

```ocaml
module Foo : sig
  val x : int
  val f : int -> int
end = struct
  let x = 0
  let y = 12
  let f x = x + y
end
```

一般来说，当编译器遇到一个编译单元时，它会将其视为
定义一个模块和一个签名，如下所示：

```ocaml
module Foo
  : sig (* insert contents of foo.mli here *) end
= struct
  (* insert contents of foo.ml here *)
end
```

*单元名称* `Foo` 是从基本名称 `foo` 派生而来的，只需大写
第一个字母。请注意，没有定义命名模块类型；的
`Foo` 的签名实际上是匿名的。

标准库使用编译单元来实现我们的大部分模块
到目前为止一直在使用，例如 `List` 和 `String`。你可以在
[standard library source code][stdlibsrc]。

[stdlibsrc]: https://github.com/ocaml/ocaml/tree/trunk/stdlib

## 文档注释

一些文档注释应写在接口文件中，另一些则应写在实现文件中：

- 抽象的客户端应当阅读接口文件，更准确地说，是阅读由接口文件生成的
  HTML 文档。因此，接口文件中的注释应该面向这个受众来写。这些注释
  应描述如何使用抽象、调用函数的前置条件、函数可能引发哪些异常，
  也可以简要说明操作使用了什么算法。标准库的 `List` 模块包含许多
  这类注释的示例。

- 不应期待客户端阅读实现文件。这些文件主要供实现的作者和维护者阅读。
  实现文件中的文档应解释抽象的内部细节，例如表示类型如何使用、
  代码如何工作、维护了哪些重要的内部不变式，等等。维护者还应该阅读
  接口文件中的规格说明。

文件之间**不**应该重复。特别是，
接口文件中面向客户的规范注释不应
在实现文件中重复。原因之一是重复不可避免地会导致错误。
另一个原因是 OCamldoc 能够自动把接口文件中的注释注入到
为实现文件生成的 HTML 中。

OCamldoc 注释可以放置在元素之前或之后
接口。例如，这两种放置方式都是可能的：

```ocaml
(** The mathematical constant 3.14... *)
val pi : float
```

```ocaml
val pi : float
(** The mathematical constant 3.14... *)
```

```{tip}
标准库开发人员显然更喜欢后置
注释，并且 OCamlFormat 似乎也更适合这种写法。
```

## 堆栈示例

将此代码放入 `mystack.mli` 中，注意其周围没有 `sig..end` 或
任何 `module type`：

```ocaml
type 'a t
exception Empty
val empty : 'a t
val is_empty : 'a t -> bool
val push : 'a -> 'a t -> 'a t
val peek : 'a t -> 'a
val pop : 'a t -> 'a t
```

我们使用名称“mystack”，因为标准库已经有一个
`Stack` 模块。重新使用该名称可能会导致错误消息
有点难以理解。

同样将这段代码放入`mystack.ml`中，注意没有`struct..end`
它周围或任何 `module`：

```ocaml
type 'a t = 'a list
exception Empty
let empty = []
let is_empty = function [] -> true | _ -> false
let push = List.cons
let peek = function [] -> raise Empty | x :: _ -> x
let pop = function [] -> raise Empty | _ :: s -> s
```

创建Dune文件：

```text
(library
 (name mystack))
```

编译代码并启动 utop：

```console
$ dune utop
```

你的编译单元已可供使用：

```ocaml
# Mystack.empty;;
- : 'a Mystack.t = <abstr>
```

## 不完整的编译单元

如果编译时缺少接口或实现文件怎么办
单位？

**缺少接口文件。**实际上这正是我们通常的情况
一直工作到这一点。例如，你可能已经做了一些作业
文件名为 `lab1.ml` 但永远不需要担心 `lab1.mli`。没有
要求每个 `.ml` 文件都有一个对应的 `.mli` 文件，或者在其他文件中
换句话说，每个编译单元都是完整的。

如果 `.mli` 文件丢失，仍然会创建一个模块，正如我们所看到的
当我们了解 `#load` 和模块时。它只是没有
自动强加签名。比如上面 `lab1` 的情况
将导致在编译期间创建以下模块：

```ocaml
module Lab1 = struct
  (* insert contents of lab1.ml here *)
end
```

**缺少实现文件。** 这种情况比较罕见，而且你不是这样的情况
日常开发中可能会遇到。但请注意，有一个
Java 或 C++ 程序员有时会意外陷入**误用**情况。
假设你有一个接口，该接口有几个实现。
回想一下本章前面的堆栈，也许你有一个模块类型
`Stack` 和两个实现它的模块，`ListStack` 和 `CustomStack`：

```ocaml
module type Stack = sig
  type 'a t
  val empty : 'a t
  val push : 'a -> 'a t -> 'a t
  (* etc. *)
end

module ListStack : Stack = struct
  type 'a t = 'a list
  let empty = []
  let push = List.cons
  (* etc. *)
end

module CustomStack : Stack = struct
  (* omitted *)
end
```

人们很容易将该代码划分为文件，如下所示：

```ocaml
(********************************)
(* stack.mli *)
type 'a t
val empty : 'a t
val push : 'a -> 'a t -> 'a t
(* etc. *)

(********************************)
(* listStack.ml *)
type 'a t = 'a list
let empty = []
let push = List.cons
(* etc. *)

(********************************)
(* customStack.ml *)
(* omitted *)
```

这种划分很有诱惑力，因为在 Java 中你可能会把 `Stack` 接口
放入 `Stack.java` 文件，把 `ListStack` 类放入 `ListStack.java` 文件，以及
等等。在 C++ 中，可以使用 `.hpp` 和 `.cpp` 文件完成类似的操作。

但上面这种 OCaml 文件组织是行不通的。要形成一个编译单元，
`listStack.ml` 的接口**必须**位于 `listStack.mli` 中，不能放在任何其他名称的文件里。
所以这种代码划分无法表达 `ListStack : Stack`。

相反，代码可以这样划分：

```ocaml
(********************************)
(* stack.ml *)
module type S = sig
  type 'a t
  val empty : 'a t
  val push : 'a -> 'a t -> 'a t
  (* etc. *)
end

(********************************)
(* listStack.ml *)
module M : Stack.S = struct
  type 'a t = 'a list
  let empty = []
  let push = List.cons
  (* etc. *)
end

(********************************)
(* customStack.ml *)
module M : Stack.S = struct
  (* omitted *)
end
```

请注意有关该划分的以下几点：

- 模块类型位于 `.ml` 文件中，而不是 `.mli` 文件中，因为我们不是
在尝试为它创建一个编译单元。

- 我们为文件中的模块和模块类型提供短名称，因为它们
根据文件名已经位于模块内。例如，如果把 `S` 命名为更长的 `Stack`，
  写起来会相当冗长；那样一来，我们就必须在模块类型注解中写
  `Stack.Stack` 而不是
  `Stack.S`。

代码划分的另一种可能性是将所有代码放在一个单独的代码中
文件 `stack.ml`。如果所有代码都是同一个库的一部分，那么这是可行的，但不是
如果（例如）`ListStack` 和 `CustomStack` 是由不同的组织开发的。
如果它在单个文件中，那么我们可以将它变成一个编译单元：

```ocaml
(********************************)
(* stack.mli *)
module type S = sig
  type 'a t
  val empty : 'a t
  val push : 'a -> 'a t -> 'a t
  (* etc. *)
end

module ListStack : S

module CustomStack : S

(********************************)
(* stack.ml *)
module type S = sig
  type 'a t
  val empty : 'a t
  val push : 'a -> 'a t -> 'a t
  (* etc. *)
end

module ListStack : S = struct
  type 'a t = 'a list
  let empty = []
  let push = List.cons
  (* etc. *)
end

module CustomStack : S = struct
  (* omitted *)
end
```

不幸的是，这确实意味着我们在接口文件和实现文件中都重复了 `Stack.S`。
没有办法把已经在 `.mli` 文件中声明的模块类型自动“导入”到对应的
`.ml` 文件中。
