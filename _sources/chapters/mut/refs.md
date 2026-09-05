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

# 引用

{{ video_embed | replace("%%VID%%", "R0tGac0jaEQ")}}

引用（*ref*）类似于命令式语言中的指针或引用：它表示内存中的一个位置，其中保存的内容可以改变。引用也称为*引用单元*（reference cell），可以把它想成内存中一个内容可变的单元格。

下面的例子依次展示如何创建引用、读取其中的值、修改其内容，再观察修改后的结果：

```{code-cell} ocaml
let x = ref 0;;
```
```{code-cell} ocaml
!x;;
```
```{code-cell} ocaml
x := 1;;
```
```{code-cell} ocaml
!x;;
```

第一条语句 `let x = ref 0` 使用 `ref` 关键字创建一个引用。这是内存中的一个位置，其内容被初始化为 `0`。可以把位置本身想象成地址——例如 `0x3110bae0`——尽管在 OCaml 程序中无法写下这样的地址。`ref` 关键字就是用来分配并初始化内存位置的。

OCaml 响应中的第一部分 `val x : int ref` 表明 `x` 是一个类型为 `int ref` 的变量。这里出现了一个新的类型构造器 `ref`，它和 `list`、`option` 一样用于构造类型。对于任意类型 `t`，`t ref` 表示对某个内存位置的引用，并且该位置中保证存放类型为 `t` 的值。类型仍然从右向左读：`t ref` 就是“对 `t` 的引用”。响应的第二部分显示了该位置当前保存的内容，也就是初始化时写入的 `0`。

第二条语句 `!x` 对 `x` 解引用（dereference），返回内存位置的内容。注意，`!` 在 OCaml 中是一元解引用运算符，而不是布尔取反。

第三条语句 `x := 1` 是一个赋值。它将 `x` 的内容更改为 `1`。注意，`x` 本身仍然指向内存中的同一个位置（即地址）。内存是可变的；变量绑定则不是。改变的是内容。OCaml 的响应只是 `()`，这意味着赋值已经发生——就像打印函数返回 `()` 来表明打印已经完成一样。

第四条语句 `!x` 再次解引用 `x`，证明该内存位置的内容确实已经改变。

这里最重要的区别是“绑定”与“内容”：`x` 始终绑定到同一个内存位置，`x := 1` 并没有让 `x` 改为指向别处，只是替换了该位置中保存的值。后文的引用、可变字段和数组都可以用这个“位置—内容”模型理解。

## 别名

{{ video_embed | replace("%%VID%%", "pt06BxGhjDQ")}}

现在我们有了引用，也就出现了*别名*（aliasing）问题：两个引用可以指向同一个内存位置，因此通过一个引用进行的更新也会影响另一个。例如：

```{code-cell} ocaml
let x = ref 42;;
let y = ref 42;;
let z = x;;
x := 43;;
let w = !y + !z;;
```

执行这段代码的结果是 `w` 被绑定到 `85`，因为 `let z = x` 使得 `z` 和 `x` 成为别名，因此将 `x` 更新为 `43` 同样导致 `z` 变为 `43`。

严格地说，变化的不是 `z` 这个绑定，而是 `x` 与 `z` 共同指向的位置。也正因为存在别名，理解一次赋值的影响时，不能只看赋值语句本身，还要考虑程序中是否有其他名字指向同一位置。

## 语法和语义

{{ video_embed | replace("%%VID%%", "ByV1N3hDgSw")}}

ref 的语义基于内存中的*位置*（location）。位置是可以传递给函数并从函数返回的值。但与其他类型的值（如整数、变体）不同，位置无法直接在 OCaml 程序中写出。这与 C 等语言不同——在 C 中，程序员可以直接写出内存地址并对指针进行算术运算。C 程序员需要这种底层访问来与硬件交互、构建操作系统等。高级语言的程序员愿意放弃这种能力，以换取*内存安全*（memory safety）。这是一个不易精确定义的术语，但根据 [Hicks 2014][memory-safety-hicks] 的描述，直观上它意味着：

* 指针只能以安全的方式创建，并明确其可合法访问的内存区域；

* 只有当指针指向为它分配的内存区域时，才能对其解引用；

* 解引用时，该内存区域仍然有效。

[memory-safety-hicks]: http://www.pl-enthusiast.net/2014/07/21/memory-safety/

**语法。**

* 创建引用：`ref e`

* 为引用赋值：`e1 := e2`

* 解引用：`!e`

**动态语义。**

* 对 `ref e` 求值时：

  - 将 `e` 计算为值 `v`

  - 在内存中分配一个新位置 `loc` 来保存 `v`

  - 将 `v` 存储在 `loc` 中

  - 返回 `loc`

* 对 `e1 := e2` 求值时：

  - 将 `e2` 计算为值 `v`，将 `e1` 计算为位置 `loc`。

  - 将 `v` 存储在 `loc` 中。

  - 返回 `()`，即 `unit` 值。

* 对 `!e` 求值时：

  - 将 `e` 求值为位置 `loc`。

  - 返回 `loc` 的内容。

**静态语义。**

这里引入了新的类型构造器 `ref`：对于任意类型 `t`，`t ref` 都是一个类型。注意，`ref` 有两种用途：它既可以作为类型构造器出现在类型中，也可以作为创建引用的表达式出现在程序中。

* `ref e : t ref` 如果 `e : t`。

* `e1 := e2 : unit` 如果 `e1 : t ref` 和 `e2 : t`。

* `!e : t` 如果 `e : t ref`。

## 副作用排序

{{ video_embed | replace("%%VID%%", "aj0bpOyv7Gs")}}

分号运算符用于对副作用（如修改引用）进行排序。我们之前在打印时已经见过分号。现在学习了可变性，是时候正式地对待它了。

* **语法：** `e1; e2`

* **动态语义：** 对 `e1; e2` 求值：

  - 首先将 `e1` 求值为值 `v1`。

  - 然后将 `e2` 求值为值 `v2`。

  - 返回 `v2`。（`v1` 完全不被使用。）

  - 如果序列中有多个表达式，如 `e1; e2; ...; en`，则按从左到右的顺序逐个求值，仅返回 `vn`。

* **静态语义：** `e1; e2 : t`，如果 `e1 : unit` 且 `e2 : t`。类似地，`e1; e2; ...; en : t`，如果除了 `en` 具有类型 `t` 之外，`e1`、`e2`……都具有类型 `unit`。

分号的类型规则旨在防止程序员犯错。例如，程序员写出 `2+3; 7` 可能并非本意：没有理由去求值 `2+3`，然后丢弃结果再返回 `7`。如果你违反这条类型规则，编译器会向你发出警告。

想要消除该警告（且你确定这就是你需要做的），标准库中有一个函数 `ignore : 'a -> unit`。使用它，`ignore(2+3); 7` 将在没有警告的情况下编译。当然，你也可以自己写 `ignore`：`let ignore _ = ()`。

## 示例：可变计数器

{{ video_embed | replace("%%VID%%", "o5wFQvCRJsc")}}

这是实现*计数器*的代码。每次调用 `next_val` 时，它返回的值比上次多 1。

```{code-cell} ocaml
let counter = ref 0

let next_val =
  fun () ->
    counter := !counter + 1;
    !counter
```

```{code-cell} ocaml
next_val ()
```

```{code-cell} ocaml
next_val ()
```

```{code-cell} ocaml
next_val ()
```

`next_val` 的实现由分号连接的两个表达式组成。第一个表达式 `counter := !counter + 1` 执行赋值，将计数器加一；第二个表达式 `!counter` 返回更新后的内容。

`next_val` 很不寻常，因为每次调用都可能返回不同的值。此前我们实现的函数都是*确定性的*：输入相同，输出就相同。有些函数则具有*非确定性*，即使接收相同输入，不同调用也可能产生不同输出。标准库中 `Random` 模块的函数如此，读取用户输入的 `Stdlib.read_line` 也是如此。它们恰好都依赖可变性，这并非巧合。

这个计数器还可以从两个方面改进。首先，标准库函数 `incr : int ref -> unit` 可以把 `int ref` 中的值加 1，作用类似于许多 C 系语言中的 `++` 运算符。因此，可以用 `incr counter` 代替 `counter := !counter + 1`。（相应地，`decr` 会将值减 1。）

其次，目前的写法把变量 `counter` 暴露给了外部代码。我们更希望将它隐藏起来，防止 `next_val` 的客户端直接修改它。为此，可以把 `counter` 嵌套在 `next_val` 的作用域中：

```{code-cell} ocaml
let next_val =
  let counter = ref 0 in
  fun () ->
    incr counter;
    !counter
```

现在 `counter` 位于 `next_val` 内部，离开这个作用域便无法访问。

这是一种常见而重要的设计方式：把可变状态限制在尽可能小的作用域中，只通过函数暴露必要的操作。调用者可以使用计数器，却不能绕过 `next_val` 任意修改其内部状态。

此前介绍 let 表达式的动态语义时，我们使用了替换模型。可以据此按如下方式理解 `next_val` 的定义：

* 首先求值 `ref 0`，得到位置 `loc`，也就是内存中的一个地址；该地址的内容初始化为 `0`。

* 接着，把 let 表达式主体中每个 `counter` 都替换成这个位置，于是得到：
  ```
  fun () -> incr loc; !loc
  ```

* 第三，该匿名函数绑定到 `next_val`。

因此，每次调用 `next_val`，都会递增并返回内存位置 `loc` 中的内容。

再看看下面这段有问题的代码：

```{code-cell} ocaml
let next_val_broken = fun () ->
  let counter = ref 0 in
  incr counter;
  !counter
```

它看似只有一处细微区别：`counter` 的绑定位于 `fun () ->` 之后，而不是之前。但这一点会造成截然不同的结果：

```{code-cell} ocaml
next_val_broken ();;
next_val_broken ();;
next_val_broken ();;
```

每次调用 `next_val_broken`，它都返回 `1`——这个函数已经起不到计数器的作用了。问题出在哪里？

每次调用 `next_val_broken` 时，函数都会先对 `ref 0` 求值，分配一个新的引用单元并将其初始化为 `0`；随后把其中的值递增到 `1`，再返回 `1`。也就是说，`next_val_broken` 的*每次调用*都会分配新的引用单元，而 `next_val` 从始至终只分配并使用*同一个*引用单元。

## 示例：指针

在 C 这类语言中，指针兼具两个特性：它可以为空，所指向位置中的内容也可以改变。（Java 的对象引用与此相似，但在当前 OCaml 语境中，“引用”已经专指引用单元，容易混淆，因此本节统一使用“指针”。）下面用 OCaml 的引用单元模拟指针。

```{code-cell} ocaml
type 'a pointer = 'a ref option
```

这个类型仍然从右向左读。其中的 `option` 表示指针可能为空，我们用 `None` 表示空指针。

```{code-cell} ocaml
let null : 'a pointer = None
```

类型中的 `ref` 表示指针所指位置的内容可以改变。下面定义一个辅助函数，用于分配并初始化一个新指针：

```{code-cell} ocaml
let malloc (x : 'a) : 'a pointer = Some (ref x)
```

现在就可以创建指向任意值的指针：

```{code-cell} ocaml
let p = malloc 42
```

在 C 中，前缀运算符 `*` 用于对指针*解引用*。解引用会返回指针所指位置中的内容；如果指针为空，则抛出异常：

```{code-cell} ocaml
exception Segfault

let deref (ptr : 'a pointer) : 'a =
  match ptr with None -> raise Segfault | Some r -> !r
```

```{code-cell} ocaml
deref p
```

```{code-cell} ocaml
:tags: ["raises-exception"]
deref null
```

我们甚至可以自定义一个 OCaml 解引用运算符。不过，需要在符号前加上 `~`，解析器才会把它识别为前缀运算符。

```{code-cell} ocaml
let ( ~* ) = deref;;
~*p
```

在 C 中，通过指针赋值写作 `*p = x`。它把 `p` 所指内存位置的内容改为 `x`。可以在 OCaml 中这样实现该操作：

```{code-cell} ocaml
let assign (ptr : 'a pointer) (x : 'a) : unit =
  match ptr with None -> raise Segfault | Some r -> r := x
```

```{code-cell} ocaml
assign p 2;
deref p
```

```{code-cell} ocaml
:tags: ["raises-exception"]
assign null 0
```

同样，我们也可以为它自定义 OCaml 运算符。不过，很难找到一个同时包含 `*` 和 `=`、又不会让人误以为与乘法有关的符号：

```{code-cell} ocaml
let ( =* ) = assign;;
p =* 3;;
~*p
```

唯一无法用上述编码实现的，是把指针当作整数处理。C 允许取得变量地址并把地址用于*指针算术*。这有助于编写高效的底层代码，却也容易引发各种程序错误和安全漏洞。

````{admonition} 危险的秘密
严格来说，刚才的话并不完全正确。不过，下面的做法极其危险，不应在实际代码中使用：借助未公开文档的函数 `Obj.magic`，可以取得引用的内存地址：

```ocaml
let address (ptr : 'a pointer) : int =
  match ptr with None -> 0 | Some r -> Obj.magic r

let ( ~& ) = address
```

但请务必不要使用这个函数：它会彻底绕过 OCaml 类型系统提供的安全保障，一旦使用，程序行为便不再有任何保证。
````

OCaml 标准库没有提供上述指针编码，因为实际编程中并不需要它；需要时直接组合引用与 `option` 即可。前面的写法也不是地道的 OCaml 风格，其目的只是说明 OCaml 引用与 C 指针（以及 Java 对象引用）之间的关系。

## 示例：不使用 `rec` 的递归

引用还能实现一个巧妙的技巧：不用关键字 `rec` 也能构造递归函数。假设要定义递归阶乘函数 `fact`，通常会这样写：

```{code-cell} ocaml
let rec fact_rec n = if n = 0 then 1 else n * fact_rec (n - 1)
```

现在尝试在不使用 `rec` 的情况下定义它。第一步是创建一个引用，让它暂时保存一个显然不正确的函数：

```{code-cell} ocaml
let fact0 = ref (fun x -> x + 0)
```

这个初始函数究竟“错”在哪里并不重要，只要类型正确即可。因此，也可以用 `fun x -> x` 代替 `fun x -> x + 0`。

此时 `fact0` 中保存的显然还不是阶乘函数。例如，$5!$ 应为 120，而 `fact0` 并不会算出这个结果：

```{code-cell} ocaml
!fact0 5
```

接下来照常编写 `fact`，但省略 `rec`；需要递归调用时，改为调用 `fact0` 中存储的函数：

```{code-cell} ocaml
let fact n = if n = 0 then 1 else n * !fact0 (n - 1)
```

现在 `fact` 能正确计算 `0`，却仍然无法正确计算 `5`：

```{code-cell} ocaml
fact 0;;
fact 5;;
```

`5` 的结果不对，是因为递归调用找错了函数：我们希望它调用 `fact`，而不是原先的 `fact0`。**技巧就在这里：**把 `fact0` 修改为指向 `fact`：

```{code-cell} ocaml
fact0 := fact
```

现在 `fact` 递归调用并解引用 `fact0` 时，得到的正是自身，计算结果也就正确了：

```{code-cell} ocaml
fact 5
```

抽象地说，我们从下面这个递归函数开始：

```ocaml
let rec f x = ... f y ...
```

我们将其重写如下：

```ocaml
let f0 = ref (fun x -> x)

let f x = ... !f0 y ...

f0 := f
```

此时，`f` 的计算结果就与使用 `rec` 定义时相同。

这种技巧有时称为“打递归结”（tying the recursive knot）：把 `f0` 更新为指向 `f`，于是 `f` 解引用 `f0` 时取回的就是自身。`f0` 最初保存什么函数并不重要；这里的恒等函数只是一个占位符，等着我们把这个递归结连接起来。

## 弱类型变量

也许你已经按照前面的提示，尝试用恒等函数定义 `fact0`。这样做会得到一段颇令人费解的输出：

```{code-cell} ocaml
let fact0 = ref (fun x -> x)
```

恒等函数为什么会具有 `'_weak1 -> '_weak1` 这个奇怪的类型，而不是通常的 `'a -> 'a`？

答案涉及多态性与可变性之间格外微妙的相互作用。后面的解释器章节会介绍类型推断，届时我们便能详细解释这个问题。简而言之，如果允许该引用具有 `'a -> 'a` 类型，就可能让程序因类型错误在运行时崩溃。

目前可以这样理解：引用单元中保存的*值*可以改变，但值的*类型*不能改变。假如 OCaml 把 `ref (fun x -> x)` 赋予类型 `('a -> 'a) ref`，同一单元就可能先存入 `fun x -> x + 1 : int -> int`，之后又存入 `fun x -> x ^ "!" : string -> string`。这相当于改变引用单元所存值的类型，是类型系统所不允许的。

因此，OCaml 用*弱类型变量*表示尚未确定、但并非多态的类型。这类变量总以 `_weak` 开头，意味着类型推断尚未完成。一旦获得足够的信息，OCaml 就会完成推断，并用实际类型取代弱类型变量：

```{code-cell} ocaml
!fact0
```

```{code-cell} ocaml
!fact0 1
```

```{code-cell} ocaml
!fact0
```

把 `!fact0` 应用于 `1` 之后，OCaml 便确定该函数的类型是 `int -> int`。从此它只能以这个类型使用，例如不能再应用于字符串。

```{code-cell} ocaml
:tags: ["raises-exception"]
!fact0 "camel"
```

如果想进一步了解弱类型变量，请阅读 Jacques Garrigue 的 [*Relaxing the value restriction*][relaxing] 第 2 节，或 OCaml 手册的[相关章节][weak]。

[relaxing]: https://caml.inria.fr/pub/papers/garrigue-value_restriction-fiwflp04.pdf
[weak]: https://ocaml.org/manual/polymorphism.html

## 物理相等

OCaml 提供两类相等性判断：物理相等与结构相等。[`Stdlib.(==)` 的文档][stdlib]这样解释物理相等：

> `e1 == e2` 检验 `e1` 与 `e2` 是否物理相等。对于引用、数组、字节序列、含可变字段的记录以及含可变实例变量的对象等可变类型，当且仅当对 `e1` 的物理修改也会影响 `e2` 时，`e1 == e2` 才为 `true`。对于不可变类型，`( == )` 的行为取决于具体实现；但可以保证，若 `e1 == e2`，则 `compare e1 e2 = 0`。

[stdlib]: https://ocaml.org/api/Stdlib.html

一种理解是，`==` 应当仅用于比较引用（及其他可变数据类型），以判断它们是否指向内存中的同一个位置。否则，不要使用 `==`。

`Stdlib.(=)` 的文档中也解释了结构相等性：

> `e1 = e2` 检验 `e1` 与 `e2` 是否结构相等。对于引用和数组等可变结构，只要它们当前的内容在结构上相等，结果就为真，即使两者并不是同一个物理对象。比较函数值会抛出 `Invalid_argument`；比较循环数据结构则可能无法终止。

大多数情况下，我们需要的是结构相等。对于引用，它比较两个内存位置中保存的内容，而不关心二者是否为同一个位置。

物理相等的否定写作 `!=`，结构相等的否定写作 `<>`。这两个符号不太容易记混。

下面通过几个引用的例子，说明结构相等（`=`）与物理相等（`==`）的区别：

```{code-cell} ocaml
let r1 = ref 42
let r2 = ref 42
```

一个引用与自身物理相等，却不会与指向另一个内存位置的引用物理相等：

```{code-cell} ocaml
r1 == r1
```
```{code-cell} ocaml
r1 == r2
```
```{code-cell} ocaml
r1 != r2
```

两个引用即使位于不同的内存位置，只要其中保存的值结构相等，这两个引用本身也结构相等：

```{code-cell} ocaml
r1 = r1
```
```{code-cell} ocaml
r1 = r2
```
```{code-cell} ocaml
r1 <> r2
```

如果两个引用保存的值结构不相等，那么引用本身也结构不相等：

```{code-cell} ocaml
ref 42 <> ref 43
```

## 示例：单链表

OCaml 的内置单链表是函数式数据结构，而不是命令式数据结构。当然，我们也可以借助引用实现命令式单链表。（也可以使用前面模拟的指针，不过那只会让代码更加复杂。）

首先定义链表节点类型 `'a node`，其中保存类型为 `'a` 的值。节点的 `next` 字段本身也是一条链表。

```{code-cell} ocaml
(** An ['a node] is a node of a mutable singly-linked list. It contains a value
    of type ['a] and a link to the [next] node. *)
type 'a node = { next : 'a mlist; value : 'a }

(** An ['a mlist] is a mutable singly-linked list with elements of type ['a].
    The [option] represents the possibility that the list is empty.
    RI: The list does not contain any cycles. *)
and 'a mlist = 'a node option ref
```

要创建一个空列表，我们只需返回 `None` 的引用：

```{code-cell} ocaml
(** [empty ()] is an empty singly-linked list. *)
let empty () : 'a mlist = ref None
```

注意 `empty` 的类型：它不是一个值，而是一个函数。用于创建可变数据结构的操作通常都采用这种形式。本节末尾会再解释为什么 `empty` *必须*是函数。

要在表头插入新元素，只需创建一个新节点，把它链接到原链表，再修改链表的头部：

```{code-cell} ocaml
(** [insert_first lst v] mutates mlist [lst] by inserting value [v] as the
    first value in the list. *)
let insert_first (lst : 'a mlist) (v : 'a) : unit =
  lst := Some { next = ref !lst; value = v }
```

再看 `insert_first` 的类型：它不返回 `'a mlist`，而是返回 `unit`。修改可变数据结构的函数通常也是如此。

`empty` 和 `insert_first` 对 `unit` 的使用，使它们更接近命令式语言中的对应操作。例如，Java 中空链表的构造函数可能不接收参数，这相当于接收 `unit`；Java 链表的 `insert_first` 操作可能返回 `void`，这相当于返回 `unit`。

最后，定义一个转换函数，把新实现的可变链表转换为 OCaml 内置链表：

```{code-cell} ocaml
(** [to_list lst] is an OCaml list containing the same values as [lst]
    in the same order. Not tail recursive. *)
let rec to_list (lst : 'a mlist) : 'a list =
  match !lst with None -> [] | Some { next; value } -> value :: to_list next
```

现在我们可以看到实际的可变性：

```{code-cell} ocaml
let lst0 = empty ();;
let lst1 = lst0;;
insert_first lst0 1;;
to_list lst1;;
```

由于 `lst0` 与 `lst1` 互为别名，通过 `lst0` 所做的修改也会反映在 `lst1` 上。

**`empty` 的类型。** 回到刚才的问题：为什么 `empty` 必须是函数？看起来似乎可以把它更简单地定义成一个值：

```{code-cell} ocaml
let empty = ref None
```

但这样只会创建*一个*引用，因此程序中实际上也只会存在一条链表：

```{code-cell} ocaml
let lst2 = empty;;
let lst3 = empty;;
insert_first lst2 2;;
insert_first lst3 3;;
to_list lst2;;
to_list lst3;;
```

注意，修改会同时影响两个链表，因为它们都是同一个引用的别名。

正确地把 `empty` 定义成函数，才能保证每次创建空链表时都返回一个新的引用。

```{code-cell} ocaml
let empty () = ref None
```

这个函数并不会使用参数，因此参数取什么值其实并不重要。原则上，下面这些定义都可以：

```{code-cell} ocaml
let empty _ = ref None
let empty (b : bool) = ref None
let empty (n : int) = ref None
(* etc. *)
```

不过，我们更愿意把参数类型写成 `unit`，以便明确告诉调用者：参数值不会被使用，毕竟函数也无法从唯一的 `unit` 值中获得什么有用信息。换个角度看，输入类型为 `unit` 的函数，就相当于命令式语言中不接收参数的函数或方法。例如，Java 链表类可以用一个无参数构造函数创建空链表：

```java
class LinkedList {
  /** Returns an empty list. */
  LinkedList() { ... }
}
```

**可变值。** 在当前的 `mlist` 中，链表结构可以改变，但节点中保存的值本身不能原地修改。如果希望这些值也可变，可以让它们同样存放在引用中：

```{code-cell} ocaml
:tags: ["hide-output"]
type 'a node = { next : 'a mlist; value : 'a ref }
and 'a mlist = 'a node option ref

let empty () : 'a mlist = ref None

let insert_first (lst : 'a mlist) (v : 'a) : unit =
  lst := Some { next = ref !lst; value = ref v }

let rec set (lst : 'a mlist) (n : int) (v : 'a) : unit =
  match (!lst, n) with
  | None, _ -> invalid_arg "out of bounds"
  | Some { value }, 0 -> value := v
  | Some { next }, _ -> set next (n - 1) v

let rec to_list (lst : 'a mlist) : 'a list =
  match !lst with None -> [] | Some { next; value } -> !value :: to_list next
```

这样一来，修改值时就不必创建新节点，而可以直接更新节点中的引用：

```{code-cell} ocaml
let lst = empty ();;
insert_first lst 42;;
insert_first lst 41;;
to_list lst;;
set lst 1 43;;
to_list lst;;
```
