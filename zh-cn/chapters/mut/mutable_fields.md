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

记录的字段可以声明为可变的（mutable），这意味着它们的内容可以被更新而无需构建新记录。例如，下面是一个二维彩色点的记录类型，其颜色字段 `c` 是可变的：

```{code-cell} ocaml
type point = {x : int; y : int; mutable c : string}
```

注意，`mutable` 修饰的是字段，而不是字段的类型。因此应写作 `mutable field : type`，而不是 `field : mutable type`。

更新可变字段使用 `<-` 运算符，它形似一个向左的箭头。

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

* **动态语义：** 对 `e1.f <- e2` 求值时，先将 `e2` 求值为 `v2`，再将 `e1` 求值为 `v1`；`v1` 必须包含名为 `f` 的字段。随后把 `v1.f` 更新为 `v2`，并返回 `()`。

* **静态语义：** 若 `e1 : t1`、`t1 = {...; mutable f : t2; ...}` 且 `e2 : t2`，则 `e1.f <- e2 : unit`。

## 引用就是可变字段

事实上，引用就是用可变字段实现的。[`Stdlib`][stdlib] 中有如下声明：

```ocaml
type 'a ref = { mutable contents : 'a }
```

这解释了为什么顶层输出的引用看起来像记录：它*的确就是*一个包含可变字段 `contents` 的记录。

因此，引用和可变记录并不是两套互不相干的机制：引用可以看作只有一个可变字段的记录。读取 `!r` 就是读取该字段，执行 `r := v` 就是更新该字段。

```{code-cell} ocaml
let r = ref 42
```

引用的其他语法实际上等价于几个简单的 OCaml 函数：

```{code-cell} ocaml
let ref x = {contents = x}
```

```{code-cell} ocaml
let ( ! ) r = r.contents
```

```{code-cell} ocaml
let ( := ) r x = r.contents <- x
```

之所以说“等价”，是因为这些函数实际上并非由 OCaml 源码实现，而是位于主要以 C 编写的 OCaml 运行时中。不过，它们的行为确实与上面的 OCaml 代码相同。

[stdlib]: https://ocaml.org/api/Stdlib.html

## 示例：可变单链表

{{ video_embed | replace("%%VID%%", "dLi6Vo_Yp34")}}

借助可变字段，可以实现一个与引用版本几乎相同的单链表，而且节点和列表的类型更加简洁：

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

各项操作的算法没有本质变化，但因为不再需要引用操作，代码略为简化：

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

我们已经知道，列表和栈的实现方式十分相似。下面运用可变链表中的知识实现可变栈。先给出接口：

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

下面用可变链表实现可变栈。

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
