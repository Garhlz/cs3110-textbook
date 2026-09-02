# 编译单元

{{ video_embed | replace("%%VID%%", "hjZ8FvMUw2k")}}

*编译单元*（compilation unit）是同一目录下的一对 OCaml 源文件。它们共享相同的基本名称（称其为 `x`），但扩展名不同：一个文件是 `x.ml`，另一个是 `x.mli`。`x.ml` 文件称为*实现*（implementation），而 `x.mli` 文件称为*接口*（interface）。

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

编译 `foo.ml` 的效果相当于定义下面的模块 `Foo`：

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

一般来说，编译器会把一个编译单元视为如下形式的模块及其签名：

```ocaml
module Foo
  : sig (* insert contents of foo.mli here *) end
= struct
  (* insert contents of foo.ml here *)
end
```

*单元名* `Foo` 来自基本名称 `foo`，只是把首字母改成了大写。注意，这里并没有定义具名的模块类型；`Foo` 的签名实际上是匿名的。

标准库使用编译单元实现了我们一直在用的大多数模块，例如 `List` 和 `String`。你可以在[标准库源代码][stdlibsrc]中查看它们。

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
  接口文件中的规范。

两个文件之间**不应**重复文档。尤其不要把接口文件中面向客户端的规范注释再抄到实现文件中。一方面，重复内容迟早会出现不一致；另一方面，OCamldoc 会自动把接口文件中的注释加入为实现文件生成的 HTML 文档。

在接口中，OCamldoc 注释既可以放在相应条目之前，也可以放在之后。例如，下面两种写法都合法：

```ocaml
(** The mathematical constant 3.14... *)
val pi : float
```

```ocaml
val pi : float
(** The mathematical constant 3.14... *)
```

```{tip}
标准库开发者显然更偏爱后置注释，OCamlFormat 对这种写法的支持似乎也更好。
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

这里使用名称 `mystack`，是因为标准库中已经有一个 `Stack` 模块；重用这个名称可能会让错误信息变得难以理解。

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

创建一个 Dune 文件：

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

如果编译单元缺少接口文件或实现文件，会发生什么？

**缺少接口文件。** 其实在此前的大部分内容中，我们一直都是这样工作的。例如，你可能写过名为 `lab1.ml` 的作业，却从未需要考虑 `lab1.mli`。并非每个 `.ml` 文件都必须配有对应的 `.mli` 文件；换句话说，编译单元不一定非要包含两个文件。

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
没有办法把已经在 `.mli` 文件中声明的模块类型自动"导入"到对应的
`.ml` 文件中。
