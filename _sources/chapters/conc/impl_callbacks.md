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

# 实现回调

当使用 `bind` 或其他语法之一通过 Promise 注册回调时，它是
添加到与 Promise 一起存储的回调列表中。最终，如果
Promise 被履行，Lwt 的*解析循环*会运行所有注册到该 Promise 上的回调。
这些回调的执行顺序没有保证。换句话说，执行顺序是
不确定的。如果顺序很重要，程序员需要使用
组合运算符（例如 `bind` 和 `join`）来强制执行排序。如果
Promise 永远不会被履行（或被拒绝），它的任何回调都不会运行。

```{note}
Lwt 还支持注册在 Promise 被拒绝后运行的函数。
`Lwt.catch` 和 `try%lwt` 用于此目的。他们是同行
对应于 `Lwt.bind` 和 `let%lwt`。
```

再次强调，跟踪并发的真正来源非常重要
来自：操作系统。可能有许多异步 I/O 操作发生在
操作系统级别。但在 OCaml 级别，解析循环是顺序的，这意味着
一次只能运行一个回调。

最后，解析循环永远不会尝试中断回调。所以如果一个
回调进入无限循环，任何其他回调都不会运行。
这使得 Lwt 成为一种协作并发机制，而不是抢占式并发机制。

为了更好地理解回调解析，我们自己实现一下。我们会
使用我们之前开发的 `Promise` 数据结构。首先，我们添加一个绑定
运算符到 `Promise` 签名。

```ocaml
module type PROMISE = sig
  ...

  (** [bind p c] registers callback [c] with promise [p].
      When the promise is fulfilled, the callback will be run
      on the promises's contents.  If the promise is never
      fulfilled, the callback will never run. *)
  val bind : 'a promise -> ('a -> 'b promise) -> 'b promise
end
```

接下来，我们重新开发整个 `Promise` 结构。  我们开始
像以前一样关闭：

```ocaml
module Promise : PROMISE = struct
  type 'a state = Pending | Fulfilled of 'a | Rejected of exn
  ...
```

但现在为了实现 Promise 的表示类型，我们使用一条带有可变字段的记录。
第一个字段是 Promise 的状态，对应于我们之前使用的 `ref`。
第二个字段更有趣，下面会讨论。

```ocaml
  (** RI: the input may not be [Pending]. *)
  type 'a handler = 'a state -> unit

  (** RI: if [state <> Pending] then [handlers = []]. *)
  type 'a promise = {
    mutable state : 'a state;
    mutable handlers : 'a handler list
  }
```

*处理程序*是一个新的抽象：一个接受状态的函数。
处理程序的主要用途是运行回调。
当 Promise 的状态准备好从待处理切换为已履行或已拒绝时，
处理程序就会被用来完成履行或拒绝。这就是为什么表示不变量要求
处理程序的输入状态不能是待处理。

我们要求只有待处理的 Promise 才可以在列表中保存等待运行的处理程序。
一旦状态变为非待处理，也就是已履行或已拒绝，与该 Promise 相关的处理程序
都会被处理并从列表中删除。所以，作为表示不变量，如果状态不是待处理，
处理程序列表就必须为空。

这个辅助函数会把一个处理程序加入 Promise 的处理程序列表，后面会用到：

```ocaml
  let enqueue
      (handler : 'a state -> unit)
      (promise : 'a promise) : unit
    =
    promise.handlers <- handler :: promise.handlers
```

我们继续在内部把解析器和 Promise 视为同一种表示：

```ocaml
  type 'a resolver = 'a promise
```

因为我们将表示类型从 `ref` 更改为记录，
我们必须以简单的方式更新一些函数：

```ocaml
  (** [write_once p s] changes the state of [p] to be [s].  If [p] and [s]
      are both pending, that has no effect.
      Raises: [Invalid_arg] if the state of [p] is not pending. *)
  let write_once p s =
    if p.state = Pending
    then p.state <- s
    else invalid_arg "cannot write twice"

  let make () =
    let p = {state = Pending; handlers = []} in
    (p, p)

  let return x =
    {state = Fulfilled x; handlers = []}

  let state p = p.state
```

现在我们来看看实现中比较棘手的部分。

拒绝 Promise（带有异常）和履行 Promise（带有值）所需的步骤非常相似，
因此我们实现一个辅助函数 `resolve`。
这个助手需要一个解析器和一个状态，它将关联的 Promise 的状态更改为
给定的状态。
我们要求我们要转移到的状态 `st` 不能是挂起状态。
我们将处理程序列表更改为空以确保 RI 成立，
但我们将处理程序保存在局部变量中。
然后我们在解析器上调用 `write_once` 来更改其状态。
最后，我们处理所有正在等待这个 Promise 的处理程序。
每个处理程序都需要一个输入状态，我们会把 Promise 刚刚设置的新状态传给它们。

```ocaml
  (** Requires: [st] may not be [Pending]. *)
  let resolve (r : 'a resolver) (st : 'a state) =
    assert (st <> Pending);
    let handlers = r.handlers in
    r.handlers <- [];
    write_once r st;
    List.iter (fun f -> f st) handlers

  let reject r e =
    resolve r (Rejected e)

  let fulfill r v =
    resolve r (Fulfilled v)
```

最后，`bind` 的实现是最棘手的部分。
回想一下，这个函数需要立即返回一个新的 Promise。
首先，考虑输入 Promise 已经用某个值 `x` 履行的情况。
我们需要*立即*
在 `x` 上运行回调：
我们无法在输入 Promise 上排队处理程序，因为表示不变式表明非挂起的 Promise（例如我们的输入 Promise）*必须*具有空的处理程序列表。
运行回调会产生一个新的 Promise，我们立即返回：

```ocaml
  let bind
      (input_promise : 'a promise)
      (callback : 'a -> 'b promise) : 'b promise
    =
    match input_promise.state with
    | Fulfilled x -> callback x
```

但是，这段代码有一个问题。
回想一下，回调本身可能会引发异常。
如果发生这种情况，我们必须构造一个简单的新 Promise：
它已经因同一个异常被拒绝。我们使用辅助函数 `fail` 来构造这种已拒绝的 Promise。
第一种情况的正确代码是：

```ocaml
  let fail exc = {state = Rejected exc; handlers = []}

  let bind
      (input_promise : 'a promise)
      (callback : 'a -> 'b promise) : 'b promise
    =
    match input_promise.state with
    | Fulfilled x -> (try callback x with exc -> fail exc)
```

其次，如果 Promise 已经被某个异常拒绝，我们同样构造一个简单的新 Promise，
并让它因同一个异常被拒绝。然后立即把这个新 Promise 返回给用户：
```ocaml
    | Rejected exc -> fail exc
```

第三，如果输入 Promise 仍然待处理，我们需要做更多工作。
任务很微妙：我们需要立即向用户返回一个新的 Promise
（称为输出 Promise），同时还要确保当（更准确地说，如果）输入 Promise
在未来某个时刻被履行，并且回调完成运行后，输出 Promise 也会得到履行。
它的内容将来自回调本身返回的 Promise。

因此，我们创建新的 Promise 和解析器，
称为 `output_promise` 和 `output_resolver`。这个 Promise 就是 `bind`
返回。在返回它之前，我们使用辅助函数 `handler_of_callback`
（如下所述）将回调转换为处理程序，并将其排队
到输入 Promise 的处理程序列表中。这确保了输入 Promise
稍后被解析时，该处理程序会运行：

```ocaml
    | Pending ->
      let output_promise, output_resolver = make () in
      enqueue (handler_of_callback callback output_resolver) input_promise;
      output_promise
```

剩下的就是实现该辅助函数来创建处理程序
回调。回想一下，处理程序的类型本身就是*函数类型*，
`'a state -> unit`。这就是为什么我们的辅助函数的输出实际上是
匿名函数。该匿名函数将状态作为其输入：

```ocaml
  let handler_of_callback
      (callback : 'a -> 'b promise)
      (resolver : 'b resolver) : 'a handler =
      fun (state : 'a state) ->
```

我们继续以该输入状态为例。
下面的前两种情况很简单。用待处理状态调用处理程序会违反 RI。
如果状态是已拒绝，那么处理程序应该把这个拒绝传播给解析器，
从而让 `bind` 返回的 Promise 也被拒绝。

```ocaml
  let handler_of_callback
      (callback : 'a -> 'b promise)
      (resolver : 'b resolver) : 'a handler =
      fun (state : 'a state) ->
      match state with
      | Pending -> failwith "handler RI violated"
      | Rejected exc -> reject resolver exc
```

但如果状态是已履行，那么注册到 Promise 上的回调终于可以在已履行的内容上运行。
如果回调成功执行，它会产生一个新的 Promise；但请记住，回调本身也可能引发异常。

首先考虑乐观情况：回调成功执行并产生一个 Promise。这个 Promise 可能已经被拒绝或履行；
在这种情况下，我们继续传播该状态。

```ocaml
      | Fulfilled x ->
        let promise = callback x in
        match promise.state with
        | Fulfilled y -> resolve resolver y
        | Rejected exc -> reject resolver exc
```

但这个 Promise 也可能仍然待处理。在这种情况下，我们需要排队一个新的处理程序，
目的就是在结果可用后继续传播：

```ocaml
        | Pending -> enqueue (copying_handler resolver) promise
```

其中 `copying_handler` 是一个新的辅助函数，它创建一个非常简单的处理程序
进行传播：

```ocaml
  let copying_handler (resolver : 'a resolver) : 'a handler
    = function
      | Pending -> failwith "handler RI violated"
      | Rejected exc -> reject resolver exc
      | Fulfilled x -> resolve resolver x
```

其次，考虑回调函数本身引发异常 `exc` 的情况。在这种情况下，
我们需要让输出 Promise 因该异常被拒绝。做法是把回调的执行包在 `try` 块中：

```ocaml
      | Fulfilled x ->
        try
          let promise = callback x in
          match promise.state with
          | Fulfilled y -> resolve resolver y
          | Rejected exc -> reject resolver exc
          | Pending -> enqueue (copying_handler resolver) promise
        with exc -> reject resolver exc
```

`bind` 的 Lwt 实现基本上遵循与我们相同的算法
刚刚实现的算法。请注意，`bind` 本身没有并发：正如我们上面所说，
它是提供并发性的操作系统。

```{warning}
当输入 Promise 已经履行且回调引发异常时，Lwt 会做出与我们这里不同的选择。在这种情况下，Lwt 的 `bind` 会直接引发异常，而不是返回包含该异常的被拒绝 Promise。这是一个 [known][lwt-bind-bug] 的 `bind` 规范违例，但由于向后兼容性原因不会修复。
```

[lwt-bind-bug]: https://discuss.ocaml.org/t/lwt-3-2-0-released-we-plan-to-change-lwt-bind/1337/13
