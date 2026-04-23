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

# 实现 Promise

这是我们自己的 Lwt 风格的 Promise 的接口。名字已更改
使接口更加清晰。

```{code-cell} ocaml
(** A signature for Lwt-style promises, with better names. *)
module type PROMISE = sig
  type 'a state =
    | Pending
    | Fulfilled of 'a
    | Rejected of exn

  type 'a promise

  type 'a resolver

  (** [make ()] is a new promise and resolver. The promise is pending. *)
  val make : unit -> 'a promise * 'a resolver

  (** [return x] is a new promise that is already fulfilled with value
      [x]. *)
  val return : 'a -> 'a promise

  (** [state p] is the state of the promise. *)
  val state : 'a promise -> 'a state

  (** [fulfill r x] fulfills the promise [p] associated with [r] with
      value [x], meaning that [state p] will become [Fulfilled x].
      Requires: [p] is pending. *)
  val fulfill : 'a resolver -> 'a -> unit

  (** [reject r x] rejects the promise [p] associated with [r] with
      exception [x], meaning that [state p] will become [Rejected x].
      Requires: [p] is pending. *)
  val reject : 'a resolver -> exn -> unit
end
```

为了实现该接口，我们可以将表示类型设置为
`'a promise` 是对状态的引用：

```{code-cell} ocaml
type 'a state = Pending | Fulfilled of 'a | Rejected of exn
type 'a promise = 'a state ref
```

这样就可以改变 Promise 的内容。

对于解析器的表示类型，我们会做一些巧妙的事情。
它和 Promise 使用同一种表示。

```{code-cell} ocaml
type 'a resolver = 'a promise
```

所以在内部，这两种类型是完全相同的。但在外部，没有客户端
`Promise` 模块将能够区分它们。换句话说，我们是
使用类型系统来控制是否可以应用某些
函数（例如 `state` 与 `fulfill`）来读取或解析 Promise。

为了帮助实现其余的函数，让我们从编写一个助手开始
函数 `write_once : 'a promise -> 'a state -> unit` 来更新引用。这个
函数会把 Promise 的状态从待处理更改为
已履行或已拒绝，一旦状态改变，就不允许
又变了。也就是说，它强制执行“一次写入”不变式。

```{code-cell} ocaml
(** [write_once p s] changes the state of [p] to be [s].  If [p] and [s]
    are both pending, that has no effect.
    Raises: [Invalid_arg] if the state of [p] is not pending. *)
let write_once p s =
  if !p = Pending
  then p := s
  else invalid_arg "cannot write twice"
```

使用该助手，我们可以实现 `make` 函数：

```{code-cell} ocaml
let make () =
  let p = ref Pending in
  (p, p)
```

接口中的其余函数实现起来很简单。
将其全部放在一个模块中，我们有：

```{code-cell} ocaml
module Promise : PROMISE = struct
  type 'a state =
    | Pending
    | Fulfilled of 'a
    | Rejected of exn

  type 'a promise = 'a state ref

  type 'a resolver = 'a promise

  (** [write_once p s] changes the state of [p] to be [s]. If [p] and
      [s] are both pending, that has no effect. Raises: [Invalid_arg] if
      the state of [p] is not pending. *)
  let write_once p s =
    if !p = Pending then p := s else invalid_arg "cannot write twice"

  let make () =
    let p = ref Pending in
    (p, p)

  let return x = ref (Fulfilled x)

  let state p = !p

  let fulfill r x = write_once r (Fulfilled x)

  let reject r x = write_once r (Rejected x)
end
```

## Lwt Promise

Lwt 中使用的类型和名称比我们上面使用的要晦涩一些。
Lwt 使用来自线程&mdash;的类比术语，但是由于 Lwt 确实
没有实际实现线程，该术语不一定有帮助。 （我们
没有贬低Lwt的意思！这是一个一直在发展和变化的库
随着时间的推移。）

Lwt接口包括以下声明，我们已对其进行了注释
用注释将它们与我们上面实现的接口进行比较：

```{code-cell} ocaml
module type Lwt = sig
  (* [Sleep] means pending. [Return] means fulfilled.
     [Fail] means rejected. *)
  type 'a state = Sleep | Return of 'a | Fail of exn

  (* a [t] is a promise *)
  type 'a t

  (* a [u] is a resolver *)
  type 'a u

  val state : 'a t -> 'a state

  (* [wakeup_later] means [fulfill] *)
  val wakeup_later : 'a u -> 'a -> unit

  (* [wakeup_later_exn] means [reject] *)
  val wakeup_later_exn : 'a u -> exn -> unit

  (* [wait] means [make] *)
  val wait : unit -> 'a t * 'a u

  val return : 'a -> 'a t
end
```

Lwt 对该接口的实现比我们自己的要复杂得多
上面的实现，因为 Lwt 实际上支持更多的操作
Promise。尽管如此，我们上面提出的核心思想提供了合理的依据
对 Lwt 实现的直觉。

以下是一些 Lwt 代码示例，你可以在 utop 中尝试：

```{code-cell} ocaml
:tags: ["remove-cell"]
#use "topfind";;
```

```{code-cell} ocaml
:tags: ["remove-output"]
#require "lwt";;
```

```{code-cell} ocaml
let p, r = Lwt.wait();;
```

为了避免这些弱类型变量，我们可以向 OCaml 提供进一步的提示：
我们最终希望将什么类型放入 Promise 中。例如，如果我们想要
得到一个最终包含 `int` 的 Promise，我们可以这样写
代码：
```{code-cell} ocaml
let (p : int Lwt.t), r = Lwt.wait ()
```

现在我们可以解析这个 Promise：

```{code-cell} ocaml
Lwt.state p
```
```{code-cell} ocaml
Lwt.wakeup_later r 42
```
```{code-cell} ocaml
Lwt.state p;;
```
```{code-cell} ocaml
:tags: ["raises-exception"]
Lwt.wakeup_later r 42
```

引发最后一个异常是因为我们试图第二次解析同一个 Promise，这是不允许的。

要拒绝 Promise，我们可以编写类似的代码：

```{code-cell} ocaml
let (p : int Lwt.t), r = Lwt.wait ();;
Lwt.wakeup_later_exn r (Failure "nope");;
Lwt.state p;;
```

请注意，到目前为止，我们实现的任何内容都没有同时执行任何操作。
Promise 抽象本身并不是本质上并发的。  这是
只是一个最多可写入一次的数据结构，并且提供
一种控制谁可以写入的方法（通过解析器）。
