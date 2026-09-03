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

下面是我们自行设计的 Lwt 风格 Promise 接口。为了让接口更清楚，其中的名称经过了调整。

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

要实现这个接口，可以让 `'a promise` 的表示类型成为对状态的引用：

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

因此，这两种类型在模块内部完全相同；模块外的客户端却能区分它们。换言之，我们利用类型系统来控制哪些函数可以作用于相应的值：例如用 `state` 读取 Promise，或用 `fulfill` 解析 Promise。

为了实现其余函数，先编写辅助函数 `write_once : 'a promise -> 'a state -> unit` 来更新引用。它把 Promise 从待处理状态改为已履行或已拒绝，此后不允许再次改变，从而强制维持“只写一次”的不变式。

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

Lwt 使用的类型名和函数名比上面的版本晦涩一些。它借用了线程领域的术语，但 Lwt 实际上并不实现线程，所以这种类比未必有帮助。（这并非有意贬低 Lwt；这个库一直在演进，术语也随时间变化。）

Lwt 接口包含以下声明。代码中的注释把这些声明与我们刚实现的接口对应起来：

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
