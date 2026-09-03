# 练习

{{ solutions }}

<!--------------------------------------------------------------------------->
{{ ex2 | replace("%%NAME%%", "promise and resolve")}}

使用我们完成的 `Promise` 模块执行以下操作：创建一个整数 Promise 及其解析器；为 Promise 绑定一个打印其内容的函数；最后解析 Promise。打印操作应当只在 Promise 解析后发生。

<!--------------------------------------------------------------------------->
{{ ex2 | replace("%%NAME%%", "promise and resolve lwt")}}

重复上一题，但使用 Lwt 而不是我们自己的 Promise 库。务必使用 Lwt 的 I/O 函数，例如 `Lwt_io.printf`。

<!--------------------------------------------------------------------------->
{{ ex1 | replace("%%NAME%%", "map via bind")}}

使用我们开发的 `Promise` 模块的完成版本来实现 `map` 运算符。查看文本以获取 `map p f` 行为的描述。你可以在 `map` 的实现中调用 `bind` 。提示：使用 `return`。

<!--------------------------------------------------------------------------->
{{ ex2 | replace("%%NAME%%", "map anew")}}

使用我们开发的 `Promise` 模块的完成版本来实现 `map` 运算符。查看文本以获取 `map p f` 行为的描述。你可以使用我们为 `bind` 开发的代码作为模板，但你不能在 `map` 的实现中调用 `bind` 。

<!--------------------------------------------------------------------------->
{{ ex2 | replace("%%NAME%%", "timing challenge 1")}}

下面的函数会产生延迟，可用来模拟耗时较长的 I/O 调用。

```ocaml
(** [delay s] is a promise that resolves after about [s] seconds. *)
let delay (sec : float) : unit Lwt.t =
  Lwt_unix.sleep sec
```

编写函数 `delay_then_print : unit -> unit Lwt.t`，延迟三秒后打印 `"done"`。

<!--------------------------------------------------------------------------->
{{ ex3 | replace("%%NAME%%", "timing challenge 2")}}

运行 `timing2 ()` 时会发生什么？整个过程需要多久？先作出预测，再运行代码验证。

```ocaml
let delay n = Lwt_unix.sleep n

let timing2 () =
  let%lwt () = delay 1. in
  let%lwt () = Lwt_io.printl "1" in
  let%lwt () = delay 10. in
  let%lwt () = Lwt_io.printl "2" in
  let%lwt () = delay 20. in
  let%lwt () = Lwt_io.printl "3" in
  Lwt_io.printl "all done"

let _ = timing2 ()
let _ = Lwt_main.run (delay 35.)
```

<!--------------------------------------------------------------------------->
{{ ex3 | replace("%%NAME%%", "timing challenge 3")}}

运行 `timing3 ()` 时会发生什么？运行需要多长时间？做一个
预测，然后运行代码来找出答案。

```ocaml
open Lwt.Infix

let delay n = Lwt_unix.sleep n

let timing3 () =
  let _t1 = let%lwt () = delay 1. in Lwt_io.printl "1" in
  let _t2 = let%lwt () = delay 10. in Lwt_io.printl "2" in
  let _t3 = let%lwt () = delay 20. in Lwt_io.printl "3" in
  Lwt_io.printl "all done"

let _ = timing3 ()
let _ = Lwt_main.run (delay 35.)
```

<!--------------------------------------------------------------------------->
{{ ex3 | replace("%%NAME%%", "timing challenge 4")}}

运行 `timing4 ()` 时会发生什么？运行需要多长时间？做一个
预测，然后运行代码来找出答案。

```ocaml
open Lwt.Infix

let delay n = Lwt_unix.sleep n

let timing4 () =
  let t1 = let%lwt () = delay 1. in Lwt_io.printl "1" in
  let t2 = let%lwt () = delay 10. in Lwt_io.printl "2" in
  let t3 = let%lwt () = delay 20. in Lwt_io.printl "3" in
  let%lwt () = Lwt.join [t1; t2; t3] in
  Lwt_io.printl "all done"

let _ = timing4 ()
let _ = Lwt_main.run (delay 35.)
```

<!--------------------------------------------------------------------------->
{{ ex4 | replace("%%NAME%%", "file monitor")}}

编写一个 Lwt 程序来监视名为“log”的文件的内容。
具体来说，你的程序应该打开该文件，不断地读取一行
文件，当每一行可用时，将该行打印到标准输出。当你
到达文件末尾（EOF），你的程序应该干净地终止，而不需要
任何异常。

这是起始代码：

```ocaml
open Lwt_io
open Lwt_unix

(** [log ()] is a promise for an [input_channel] that reads from
    the file named "log". *)
let log () : input_channel Lwt.t =
  let%lwt fd = openfile "log" [O_RDONLY] 0 in
  Lwt.return (of_fd ~mode:input fd)

(** [loop ic] reads one line from [ic], prints it to stdout,
    then calls itself recursively. It is an infinite loop. *)
let rec loop (ic : input_channel) =
  failwith "TODO"
  (* hint: use [Lwt_io.read_line] and [Lwt_io.printlf] *)

(** [monitor ()] monitors the file named "log". *)
let monitor () : unit Lwt.t =
  Lwt.bind (log ()) loop

(** [handler] is a helper function for [main]. If its input is
    [End_of_file], it handles cleanly exiting the program by
    returning the unit promise. Any other input is re-raised
    with [Lwt.fail]. *)
let handler : exn -> unit Lwt.t =
  failwith "TODO"

let main () : unit Lwt.t =
  Lwt.catch monitor handler

let _ = Lwt_main.run (main ())
```

完成 `loop` 和 `handler`。[Lwt 手册](https://ocsigen.org/lwt/)可能会有所帮助。

要编译代码，请将其保存为 `monitor.ml`，并创建一个 Dune 文件
对于它：
```text
(executable
 (name monitor)
 (libraries lwt.unix))
```

并像往常一样运行它：

```console
$ dune exec ./monitor.exe
```

要模拟一个不断追加新行的文件，请打开新的终端窗口并输入：

```console
$ mkfifo log
$ cat >log
```

现在，你在终端窗口中输入的任何内容（按回车键后）都将
添加到名为 `log` 的文件中。这将使你能够交互式地测试你的
程序。

<!--------------------------------------------------------------------------->
{{ ex2 | replace("%%NAME%%", "add opt")}}

下面是 Maybe 单子的定义：

```ocaml
module type Monad = sig
  type 'a t
  val return : 'a -> 'a t
  val ( >>= ) : 'a t -> ('a -> 'b t) -> 'b t
end

module Maybe : Monad =
struct
  type 'a t = 'a option

  let return x = Some x

  let ( >>= ) m f =
    match m with
    | Some x -> f x
    | None -> None

end
```

实现 `add : int Maybe.t -> int Maybe.t -> int Maybe.t`。如果其中任何一个
输入是 `None`，那么输出应该是 `None`。否则，如果输入是
`Some a` 和 `Some b` 那么输出应该是 `Some (a+b)`。定义
`add` 必须位于 `Maybe` 之外，如上所示，这意味着你的
解决方案不得在其代码中使用构造函数 `None` 或 `Some` 。

<!--------------------------------------------------------------------------->
{{ ex2 | replace("%%NAME%%", "fmap and join")}}

下面扩展单子签名，加入两个新操作：

```ocaml
module type ExtMonad = sig
  type 'a t
  val return : 'a -> 'a t
  val ( >>= ) : 'a t -> ('a -> 'b t) -> 'b t
  val ( >>| ) : 'a t -> ('a -> 'b) -> 'b t
  val join : 'a t t -> 'a t
end
```
正如中缀运算符 `>>=` 被称为 `bind` 一样，中缀运算符 `>>|` 是
称为 `fmap`。这两个运算符仅在返回类型上有所不同
函数参数。

使用盒子比喻，`>>|` 接受一个装箱的值，以及一个仅
知道如何处理未装箱的值，从框中提取值，运行
函数，并将该输出装箱作为其自己的返回值。

同样使用盒子比喻，`join` 接受一个包含在两个盒子中的值
并移除其中一个盒子。

可以通过模式匹配直接实现 `>>|` 和 `join` （如
我们已经实现了 `>>=`)。也可以在不使用的情况下实现它们
模式匹配。

对于本练习，执行前者：实现 `>>|` 和 `join` 作为
`Maybe` monad，并且不要在 `>>|` 或 `join` 的主体中使用 `>>=` 或 `return`。

<!--------------------------------------------------------------------------->
{{ ex2 | replace("%%NAME%%", "fmap and join again")}}

再次解决之前的练习。  这次，你必须使用 `>>=` 和 `return`
实现 `>>|` 和 `join`，并且你不能在正文中使用 `Some` 或 `None`
`>>|` 和 `join`。

<!--------------------------------------------------------------------------->
{{ ex3 | replace("%%NAME%%", "bind from fmap+join")}}

前面的练习表明可以实现 `>>|` 和 `join`
完全按照 `>>=` （和 `return`），不需要知道任何事情
关于 monad 的表示类型 `'a t` 。

其实也可以往另一个方向走。也就是说，`>>=` 可以是
仅使用 `>>|` 和 `join` 实现，无需了解任何内容
表示类型 `'a t`。

通过完成以下代码来证明这一点：

```ocaml
module type FmapJoinMonad = sig
  type 'a t
  val ( >>| ) : 'a t -> ('a -> 'b) -> 'b t
  val join : 'a t t -> 'a t
  val return : 'a -> 'a t
end

module type BindMonad = sig
  type 'a t
  val return : 'a -> 'a t
  val ( >>= ) : 'a t -> ('a -> 'b t) -> 'b t
end

module MakeMonad (M : FmapJoinMonad) : BindMonad = struct
  (* TODO *)
end
```

*提示：让类型作为你的指南。*

<!--------------------------------------------------------------------------->
{{ ex3 | replace("%%NAME%%", "list monad")}}

我们已经看过三种单子，下面考察第四种：*列表单子*。它所做的“额外工作”，是把函数提升为可以处理整个列表，而不只是单个值。（这里并不涉及并发；列表单子不会同时对各个元素运行函数，不过 Lwt 单子的确提供了相应的并发操作。）

例如，假设你有以下函数：

```ocaml
let inc x = x + 1
let pm x = [x; -x]
```

列表单子可以把这些函数应用于列表中的每个元素，并以列表形式返回结果。例如：

* `[1; 2; 3] >>| inc` 是 `[2; 3; 4]`。
* `[1; 2; 3] >>= pm` 是 `[1; -1; 2; -2; 3; -3]`。
* `[1; 2; 3] >>= pm >>| inc` 是 `[2; 0; 3; -1; 4; -2]`。

可以这样理解：列表单子运算符接收一列输入，对每个输入运行函数，再把所有输出合并成一个列表。

请完成列表单子的以下定义：

```ocaml
module type ExtMonad = sig
  type 'a t
  val return : 'a -> 'a t
  val ( >>= ) : 'a t -> ('a -> 'b t) -> 'b t
  val ( >>| ) : 'a t -> ('a -> 'b) -> 'b t
  val join : 'a t t -> 'a t
end

module ListMonad : ExtMonad = struct
  type 'a t = 'a list

  (* TODO *)
end
```

*提示：* 将 `>>=` 留到最后。  让类型成为你的指南。  有
两个非常有用的列表库函数可以帮助你。

<!--------------------------------------------------------------------------->
{{ ex3 | replace("%%NAME%%", "trivial monad laws")}}

这是世界上最琐碎的单子。它所做的就是将一个值包装在一个
构造函数。

```ocaml
module Trivial : Monad = struct
  type 'a t = Wrap of 'a
  let return x = Wrap x
  let ( >>= ) (Wrap x) f = f x
end
```

证明使用 `>>=` 和 `return` 制定的三个单子定律成立
对于琐碎的单子。
