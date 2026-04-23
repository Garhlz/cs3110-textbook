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

# 可变字段

{{ video_embed | replace("%%VID%%", "9RNeX5t4_xA")}}

记录的字段可以声明为可变的，这意味着它们的内容可以
更新而不构建新记录。例如，这是一个记录类型
对于色域 `c` 可变的二维彩色点：

```{code-cell} ocaml
type point = {x : int; y : int; mutable c : string}
```

请注意，`mutable` 是字段的属性，而不是字段的类型
场。特别是，我们写 `mutable field : type`，而不是
`field : mutable type`。

更新可变字段的运算符是 `<-` ，它看起来像
向左箭头。

```{code-cell} ocaml
let p = {x = 0; y = 0; c = "red"}
```

```{code-cell} ocaml
p.c <- "white"
```

```{code-cell} ocaml
p
```

非可变字段不能以这种方式更新：

```{code-cell} ocaml
:tags: ["raises-exception"]
p.x <- 3;;
```

* **语法：** `e1.f <- e2`

* **动态语义：** 要评估 `e1.f <- e2`，请将 `e2` 评估为一个值
`v2` 和 `e1` 为值 `v1`，该值必须有一个名为 `f` 的字段。更新
  `v1.f` 至 `v2`。返回`()`。

* **静态语义：** `e1.f <- e2 : unit` if `e1 : t1` 和
`t1 = {...; mutable f : t2; ...}` 和 `e2 : t2`。

## Refs 是可变字段

事实证明，refs 实际上是作为可变字段实现的。在
[`Stdlib`][stdlib] 我们找到以下声明：

```ocaml
type 'a ref = { mutable contents : 'a }
```

这就是为什么当顶层输出一个 ref 时，它看起来像一条记录：它*是*一个
记录有一个名为 `contents` 的可变字段！

```{code-cell} ocaml
let r = ref 42
```

我们看到的 refs 的其他语法实际上相当于简单的 OCaml
函数：

```{code-cell} ocaml
let ref x = {contents = x}
```

```{code-cell} ocaml
let ( ! ) r = r.contents
```

```{code-cell} ocaml
let ( := ) r x = r.contents <- x
```

我们之所以说“等效”是因为这些函数实际上都实现了
不是在 OCaml 本身中，而是在 OCaml 运行时中，后者主要用 C 实现。
尽管如此，这些函数的行为确实与上面给出的 OCaml 源代码相同。

[stdlib]: https://ocaml.org/api/Stdlib.html

## 示例：可变单链表

{{ video_embed | replace("%%VID%%", "dLi6Vo_Yp34")}}

使用可变字段，我们可以实现与我们几乎相同的单链表
做了参考文献。节点和列表的类型已简化：

```{code-cell} ocaml
(** An ['a node] is a node of a mutable singly-linked list. It contains a value
    of type ['a] and optionally has a pointer to the next node. *)
type 'a node = {
  mutable next : 'a node option;
  value : 'a
}

(** An ['a mlist] is a mutable singly-linked list with elements of type ['a].
    RI: The list does not contain any cycles. *)
type 'a mlist = {
  mutable first : 'a node option;
}
```

{{ video_embed | replace("%%VID%%", "EEXa3bY4ZwI")}}

并且实现的算法没有本质区别
操作，但代码稍微简化了，因为我们不
必须使用参考操作：

```{code-cell} ocaml
(** [insert_first lst n] mutates mlist [lst] by inserting value [v] as the
    first value in the list. *)
let insert_first (lst : 'a mlist) (v : 'a) =
  lst.first <- Some {value = v; next = lst.first}

(** [empty ()] is an empty singly-linked list. *)
let empty () : 'a mlist = {
  first = None
}

(** [to_list lst] is an OCaml list containing the same values as [lst]
    in the same order. Not tail recursive. *)
let to_list (lst : 'a mlist) : 'a list =
  let rec helper = function
    | None -> []
    | Some {next; value} -> value :: helper next
  in
  helper lst.first
```

## 示例：可变堆栈

我们已经知道列表和堆栈可以以非常相似的方式实现
方式。让我们使用从可变链表中学到的知识来
实现可变堆栈。这是一个接口：

```{code-cell} ocaml
module type MutableStack = sig
  (** ['a t] is the type of mutable stacks whose elements have type ['a].
      The stack is mutable not in the sense that its elements can
      be changed, but in the sense that it is not persistent:
      the operations [push] and [pop] destructively modify the stack. *)
  type 'a t

  (** Raised if [peek] or [pop] encounter the empty stack. *)
  exception Empty

  (** [empty ()] is the empty stack. *)
  val empty : unit -> 'a t

  (** [push x s] modifies [s] to make [x] its top element.
      The rest of the elements are unchanged. *)
  val push : 'a -> 'a t -> unit

  (** [peek s] is the top element of [s].
      Raises: [Empty] if [s] is empty. *)
  val peek : 'a t -> 'a

  (** [pop s] removes the top element of [s].
      Raises: [Empty] if [s] is empty. *)
  val pop : 'a t -> unit
end
```

现在让我们用可变链表来实现可变堆栈。

```{code-cell} ocaml
module MutableRecordStack : MutableStack = struct
  (** An ['a node] is a node of a mutable linked list.  It has
     a field [value] that contains the node's value, and
     a mutable field [next] that is [None] if the node has
     no successor, or [Some n] if the successor is [n]. *)
  type 'a node = {value : 'a; mutable next : 'a node option}

 (** AF: An ['a t] is a stack represented by a mutable linked list.
     The mutable field [top] is the first node of the list,
     which is the top of the stack. The empty stack is represented
     by {top = None}.  The node {top = Some n} represents the
     stack whose top is [n], and whose remaining elements are
     the successors of [n]. *)
  type 'a t = {mutable top : 'a node option}

  exception Empty

  let empty () = {top = None}

  let push x s = s.top <- Some {value = x; next = s.top}

  let peek s =
    match s.top with
    | None -> raise Empty
    | Some {value} -> value

  let pop s =
    match s.top with
    | None -> raise Empty
    | Some {next} -> s.top <- next
end
```
