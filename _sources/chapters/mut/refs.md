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

# Ref

{{ video_embed | replace("%%VID%%", "R0tGac0jaEQ")}}

*ref* 就像命令式语言中的指针或引用。它是内存中的一个位置，其内容可以改变。ref 也被称为*引用单元*（reference cell），这个想法的含义是内存中有一个可变的单元格。

下面是一个创建 ref、从中获取值、修改内容、并观察内容变化的示例：

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

OCaml 响应中的第一部分 `val x : int ref` 表明 `x` 是一个类型为 `int ref` 的变量。我们在这里遇到了一个新的类型构造器。就像 `list` 和 `option` 是类型构造器一样，`ref` 也是。对于任意类型 `t`，`t ref` 是对某个保证包含类型 `t` 值的内存位置的引用。和往常一样，我们应该从右向左读类型：`t ref` 表示"对 `t` 的引用"。响应的第二部分向我们展示了该内存位置的内容。事实上，内容已被初始化为 `0`。

第二条语句 `!x` 对 `x` 解引用（dereference），返回内存位置的内容。注意，`!` 在 OCaml 中是一元解引用运算符，而不是布尔取反。

第三条语句 `x := 1` 是一个赋值。它将 `x` 的内容更改为 `1`。注意，`x` 本身仍然指向内存中的同一个位置（即地址）。内存是可变的；变量绑定则不是。改变的是内容。OCaml 的响应只是 `()`，这意味着赋值已经发生——就像打印函数返回 `()` 来表明打印已经完成一样。

第四条语句 `!x` 再次解引用 `x`，证明该内存位置的内容确实已经改变。

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

## 语法和语义

{{ video_embed | replace("%%VID%%", "ByV1N3hDgSw")}}

ref 的语义基于内存中的*位置*（location）。位置是可以传递给函数并从函数返回的值。但与其他类型的值（如整数、变体）不同，位置无法直接在 OCaml 程序中写出。这与 C 等语言不同——在 C 中，程序员可以直接写出内存地址并对指针进行算术运算。C 程序员需要这种底层访问来与硬件交互、构建操作系统等。高级语言的程序员愿意放弃这种能力，以换取*内存安全*（memory safety）。这是一个不易精确定义的术语，但根据 [Hicks 2014][memory-safety-hicks] 的描述，直观上它意味着：

* 指针只能以安全的、定义了其合法内存区域的方式创建，

* 指针只能在其指向的已分配内存区域内被解引用，

* 该区域（仍）是确定的。

[memory-safety-hicks]: http://www.pl-enthusiast.net/2014/07/21/memory-safety/

**语法。**

* 参考创建：`ref e`

* 参考分配：`e1 := e2`

* 取消引用：`!e`

**动态语义。**

* 要评估 `ref e`，

  - 将 `e` 计算为值 `v`

  - 在内存中分配一个新位置 `loc` 来保存 `v`

  - 将 `v` 存储在 `loc` 中

  - 返回`loc`

* 要评估 `e1 := e2`，

  - 将 `e2` 计算为值 `v`，将 `e1` 计算为位置 `loc`。

  - 将 `v` 存储在 `loc` 中。

  - 返回`()`，即单位。

* 要评估 `!e`，

  - 将 `e` 评估为位置 `loc`。

  - 返回 `loc` 的内容。

**静态语义。**

我们有一个新的类型构造函数 `ref`，这样 `t ref` 是任何类型的类型
`t`。请注意，`ref` 关键字有两种使用方式：作为类型构造函数，以及
作为构造 refs 的表达式。

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

我们可以通过几种方式改进我们的计数器。首先，有一个库
函数 `incr : int ref -> unit` 将 `int ref` 加 1。因此它是
就像 C 家族中许多语言所熟悉的 `++` 运算符一样。
使用它，我们可以写 `incr counter` 而不是 `counter := !counter + 1`。
（还有一个减 1 的 `decr` 函数。）

其次，目前的写法把变量 `counter` 暴露给了外部代码。我们更希望将它隐藏起来，防止 `next_val` 的客户端直接修改它。为此，可以把 `counter` 嵌套在 `next_val` 的作用域中：

```{code-cell} ocaml
let next_val =
  let counter = ref 0 in
  fun () ->
    incr counter;
    !counter
```

现在 `counter` 位于 `next_val` 内部，离开这个作用域便无法访问。

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

每次我们调用 `next_val_broken` 时，它都会返回 `1`：我们不再有
柜台。这里出了什么问题？

问题是每次调用 `next_val_broken` 时，它首先要做的就是
所做的是将 `ref 0` 评估为初始化为 `0` 的新位置。那
然后位置递增到 `1`，并返回 `1`。 *每次*致电
`next_val_broken` 因此分配一个新的引用单元，而 `next_val`
仅分配*一个*新的参考单元。

## 示例：指针

在 C 这类语言中，指针结合了两个特性：它们可以为空，并且可以改变。（Java 中有一个类似的对象引用构造，但是"引用"这个术语在当前的 OCaml 上下文中容易造成困惑，因为我们现在用"引用"表示引用单元。所以这里我们使用"指针"一词。）让我们用 OCaml 的引用单元来编写指针。

```{code-cell} ocaml
type 'a pointer = 'a ref option
```

像往常一样，从右到左阅读该类型。它的 `option` 部分编码了事实
指针可能为空。我们使用 `None` 来表示这种可能性。

```{code-cell} ocaml
let null : 'a pointer = None
```

类型的 `ref` 部分编码了内容是可变的这一事实。我们
可以创建一个辅助函数来分配和初始化新的内容
指针：

```{code-cell} ocaml
let malloc (x : 'a) : 'a pointer = Some (ref x)
```

现在我们可以创建一个指向我们喜欢的任何值的指针：

```{code-cell} ocaml
let p = malloc 42
```

*解引用*指针是 C 中的 `*` 前缀运算符。它返回
指针的内容，如果指针为 null，则引发异常：

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

我们甚至可以引入我们自己的 OCaml 运算符来取消引用。我们必须把
不过，在其前面添加 `~` 使其解析为前缀运算符。

```{code-cell} ocaml
let ( ~* ) = deref;;
~*p
```

在 C 中，通过指针进行的赋值被写为 `*p = x`。  这改变了
`p` 指向的内存，使其包含 `x`。  我们可以编码
该运算符如下：

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

同样，我们可以为此引入我们自己的 OCaml 运算符，尽管这很难
选择一个涉及 `*` 和 `=` 的好符号，这样不会被误解为
涉及乘法：

```{code-cell} ocaml
let ( =* ) = assign;;
p =* 3;;
~*p
```

我们不能做的一件事就是将指针视为整数。 C 允许，
包括获取变量的地址，从而启用*指针算术*。
这对于提高效率很有好处，但也很糟糕，因为它会导致各种问题
程序错误和安全漏洞。

````{admonition} Evil Secret
好吧，我们刚才所说的实际上并不正确，但这很危险
你根本不应该依赖的知识。有一个未文档化的
函数 `Obj.magic` 我们可以用来获取引用的内存地址：

```ocaml
let address (ptr : 'a pointer) : int =
  match ptr with None -> 0 | Some r -> Obj.magic r

let ( ~& ) = address
```

但你必须保证自己永远不会使用该函数，因为它
完全规避了 OCaml 类型系统的安全性。如果出现以下情况，则一切皆废
你做的。
````

这些指针编码都不属于 OCaml 标准库的一部分，因为你
不需要它。你可以根据需要自行使用 refs 和 options。
我们上面所做的编码并不是特别惯用。我们这样做的原因
是为了说明 OCaml refs 和 C 指针之间的关系
（相当于 Java 参考）。

## 示例：不带 Rec 的递归

引用还能实现一个巧妙的技巧：不用关键字 `rec` 也能构造递归函数。假设要定义递归阶乘函数 `fact`，通常会这样写：

```{code-cell} ocaml
let rec fact_rec n = if n = 0 then 1 else n * fact_rec (n - 1)
```

我们希望在不使用 `rec` 的情况下定义该函数。  我们可以从
定义对函数的明显不正确版本的引用：

```{code-cell} ocaml
let fact0 = ref (fun x -> x + 0)
```

`fact0` 不正确的方式实际上是无关紧要的。我们只需要它
有正确的类型。我们也可以使用 `fun x -> x` 代替
`fun x -> x + 0`。

此时，`fact0` 显然不计算阶乘函数。
例如，$5!$ 应该是 120，但这不是 `fact0` 计算的：

```{code-cell} ocaml
!fact0 5
```

接下来照常编写 `fact`，但省略 `rec`；需要递归调用时，改为调用 `fact0` 中存储的函数：

```{code-cell} ocaml
let fact n = if n = 0 then 1 else n * !fact0 (n - 1)
```

现在 `fact` 实际上得到了 `0` 的正确答案，但没有得到 `5` 的正确答案：

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

抽象一点，这就是我们所做的。我们从一个函数开始
递归：

```ocaml
let rec f x = ... f y ...
```

我们将其重写如下：

```ocaml
let f0 = ref (fun x -> x)

let f x = ... !f0 y ...

f0 := f
```

现在 `f` 将计算与我们定义的版本中相同的结果
与 `rec` 一起使用。

这里发生的事情有时被称为"打递归结"（tying the recursive knot）：我们更新 `f0` 的引用使其指向 `f`，这样当 `f` 解引用 `f0` 时，它得到的是自身。我们让 `f0` 指向的初始函数（这里是恒等函数）并不重要；它只是作为占位符，直到我们把递归结打好。

## 弱类型变量

也许你已经尝试过使用恒等函数来定义 `fact0`，
正如我们上面提到的。  如果是这样，你就会遇到这个相当令人困惑的问题
输出：

```{code-cell} ocaml
let fact0 = ref (fun x -> x)
```

恒等函数 `'_weak1 -> '_weak1` 这个奇怪的类型是什么？为什么
这不是通常的`'a -> 'a`吗？

答案涉及多态性与可变性之间格外微妙的相互作用。后面的解释器章节会介绍类型推断，届时我们便能详细解释这个问题。简而言之，如果允许该引用具有 `'a -> 'a` 类型，就可能让程序因类型错误在运行时崩溃。

现在，这样考虑：虽然存储在引用单元格中的*值*是
允许更改，但该值的*类型*则不允许。如果 OCaml 给出
`ref (fun x -> x)` 类型 `('a -> 'a) ref`，那么该单元可以首先存储
`fun x -> x + 1 : int -> int` 但稍后存储
`fun x -> s ^ "!" : string -> string`。这就是类型上的改变
这是不允许的。

因此 OCaml 使用*弱类型变量*来代表未知但非多态
类型。这些变量始终以 `_weak` 开头。本质上，类型推断
因为这些还没有完成。一旦你给 OCaml 足够的信息，它
将完成类型推断并将弱类型变量替换为实际类型变量
类型：

```{code-cell} ocaml
!fact0
```

```{code-cell} ocaml
!fact0 1
```

```{code-cell} ocaml
!fact0
```

将 `!fact0` 应用到 `1` 后，OCaml 现在知道该函数
意味着类型为 `int -> int`。所以从那时起，那就是唯一的类型
可以使用它。例如，它不能应用于字符串。

```{code-cell} ocaml
:tags: ["raises-exception"]
!fact0 "camel"
```

如果想进一步了解弱类型变量，请阅读 Jacques Garrigue 的 [*Relaxing the value restriction*][relaxing] 第 2 节，或 OCaml 手册的[相关章节][weak]。

[relaxing]: https://caml.inria.fr/pub/papers/garrigue-value_restriction-fiwflp04.pdf
[weak]: https://ocaml.org/manual/polymorphism.html

## 物理相等

OCaml 有两个相等运算符：物理相等和结构相等。
[`Stdlib.(==)` 的文档][stdlib]这样解释物理相等：

> `e1 == e2` 测试 `e1` 和 `e2` 的物理相等性。关于可变类型，例如
> 作为引用、数组、字节序列、具有可变字段和对象的记录
> 对于可变实例变量，`e1 == e2` 是 `true` 当且仅当物理
> `e1` 的修改也会影响 `e2`。在非可变类型上，行为
> `( == )` 取决于实现；但是，可以保证
> `e1 == e2` 意味着 `compare e1 e2 = 0`。

[stdlib]: https://ocaml.org/api/Stdlib.html

一种理解是，`==` 应当仅用于比较引用（及其他可变数据类型），以判断它们是否指向内存中的同一个位置。否则，不要使用 `==`。

`Stdlib.(=)` 的文档中也解释了结构相等性：

> `e1 = e2` 测试 `e1` 和 `e2` 的结构相等性。可变结构
> （例如引用和数组）当且仅当它们的当前内容相等
> 即使两个可变对象不相同，结构上也是相等的
> 物理对象。函数值之间的相等引发 `Invalid_argument`。
> 循环数据结构之间的相等可能不会终止。

结构平等通常是你想要测试的。对于参考，它检查
内存位置的内容是否相等，无论是否
它们是同一个位置。

物理平等的否定是`!=`，结构平等的否定
平等是 `<>`。这可能很难记住。

下面是一些涉及 equals 和 refs 的例子来说明区别
结构平等 (`=`) 和物理平等 (`==`) 之间：

```{code-cell} ocaml
let r1 = ref 42
let r2 = ref 42
```

一个 ref 在物理上等于它自己，但不等于另一个不同的 ref
在内存中的位置：

```{code-cell} ocaml
r1 == r1
```
```{code-cell} ocaml
r1 == r2
```
```{code-cell} ocaml
r1 != r2
```

位于内存中不同位置但存储结构不同的两个引用
相同的值本身在结构上是相同的：

```{code-cell} ocaml
r1 = r1
```
```{code-cell} ocaml
r1 = r2
```
```{code-cell} ocaml
r1 <> r2
```

存储结构上不相等值的两个引用本身在结构上
不平等：

```{code-cell} ocaml
ref 42 <> ref 43
```

## 示例：单链表

OCaml 的内置单链表是函数式的，而不是命令式的。但我们当然可以使用 ref 来编写命令式单链表。（也可以使用我们上面发明的指针，但那只会让代码更复杂。）

我们首先为包含值的列表的节点定义类型 `'a node`
类型为 `'a`。  节点的 `next` 字段本身就是另一个列表。

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

请注意 `empty` 的类型：它现在不再是一个值，而是一个函数。这个
是创建可变数据结构的典型函数。在这最后
部分，我们将回到为什么 `empty` *必须* 是一个函数。

插入新的第一个元素只需要创建一个新节点，从
它到原始列表，并改变列表：

```{code-cell} ocaml
(** [insert_first lst v] mutates mlist [lst] by inserting value [v] as the
    first value in the list. *)
let insert_first (lst : 'a mlist) (v : 'a) : unit =
  lst := Some { next = ref !lst; value = v }
```

再次注意 `insert_first` 的类型。它不是返回 `'a mlist`，而是返回
返回 `unit`。这也是修改可变数据的典型函数
结构。

在 `empty` 和 `insert_first` 中，使用 `unit` 使函数更加丰富
就像命令式语言中的等价物一样。空的构造函数
例如，Java 中的 list 可能不带任何参数（相当于
采取 `unit`)。 Java 链表的 `insert_first` 操作可能
返回`void`，相当于返回`unit`。

最后，这是一个从我们新的可变列表到
OCaml 的内置列表：

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

对 `lst0` 的更改会改变 `lst1`，因为它们是别名。

**`empty`的类型。**回到`empty`，为什么它一定是函数呢？它
看起来我们可以更简单地定义它，如下所示：

```{code-cell} ocaml
let empty = ref None
```

但现在只有一个*一个* 引用被创建，因此只有一个
曾经存在过的列表：

```{code-cell} ocaml
let lst2 = empty;;
let lst3 = empty;;
insert_first lst2 2;;
insert_first lst3 3;;
to_list lst2;;
to_list lst3;;
```

请注意突变如何影响两个列表，因为它们都是别名
对于同一个参考。

通过正确地使 `empty` 成为一个函数，我们保证新的引用是
每次创建空列表时都会返回。

```{code-cell} ocaml
let empty () = ref None
```

该函数采用什么参数实际上并不重要，因为它会
永远不要使用它。  原则上我们可以将其定义为以下任何一个：

```{code-cell} ocaml
let empty _ = ref None
let empty (b : bool) = ref None
let empty (n : int) = ref None
(* etc. *)
```

但我们更喜欢 `unit` 作为参数类型的原因是为了向
客户端将不会使用参数值。毕竟有
该函数对单位值没有什么有趣的作用。另一种方式
想想看，输入类型为 `unit` 的函数就像
不带参数的命令式语言中的函数或方法。对于
例如，在 Java 中，链表类可以有一个不带任何参数的构造函数
参数并创建一个空列表：

```java
class LinkedList {
  /** Returns an empty list. */
  LinkedList() { ... }
}
```

**可变值。** 在 `mlist` 中，列表的节点是可变的，但是
价值观不是。  如果我们希望这些值也是可变的，我们可以使
他们也参考了：

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

现在，如果我们想更改值，则不必创建新节点，
我们可以直接改变节点中的值：

```{code-cell} ocaml
let lst = empty ();;
insert_first lst 42;;
insert_first lst 41;;
to_list lst;;
set lst 1 43;;
to_list lst;;
```
