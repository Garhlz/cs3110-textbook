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

# 等式规范

接下来让我们应对更大的挑战：证明数据的正确性
结构，例如堆栈、队列或集合。

正确性证明总是需要规范。在证明正确性时
迭代阶乘，我们使用递归阶乘作为规范。以此类推，
我们可以提供数据结构的两种实现——一种简单，另一种
复杂且高效——并证明两者等价。那会
要求我们引入在两种实现之间进行转换的方法。对于
例如，我们可以证明用有效方法实现的映射的正确性
平衡二叉搜索树相对于低效的实现
关联列表，通过定义函数将树转换为列表。这样一个
方法当然是有效的，但它并没有带来关于验证的新想法
供我们学习。

相反，我们将寻求基于*等式的不同方法
规范*，又名*代数规范*。这些的想法是

- 定义数据结构操作的类型，以及

- 编写一组方程来定义操作如何与一个交互
另一个。

“代数”这个词出现在这里的原因（部分）是
基于类型和方程的方法是我们在高中代数中学到的东西。
例如，以下是一些运算符的规范：

```ocaml
0 : int
1 : int
- : int -> int
+ : int -> int -> int
* : int -> int -> int

(a + b) + c = a + (b + c)
a + b = b + a
a + 0 = a
a + (-a) = 0
(a * b) * c = a * (b * c)
a * b = b * a
a * 1 = a
a * 0 = 0
a * (b + c) = a * b + a * c
```

这些运算符的类型以及相关方程都是已知的事实
学习代数时。

我们现在的目标是为数据结构编写类似的规范，并使用
他们对实现的正确性进行推理。

## 示例：堆栈

{{ video_embed | replace("%%VID%%", "Pyz2xEzD2cY")}}

以下是一些熟悉的堆栈操作及其类型。

```{code-cell} ocaml
:tags: ["hide-output"]
module type Stack = sig
  type 'a t
  val empty : 'a t
  val is_empty : 'a t -> bool
  val peek : 'a t -> 'a
  val push : 'a -> 'a t -> 'a t
  val pop : 'a t -> 'a t
end

```
像往常一样，需要对 `peek` 等进行设计选择，了解要做什么
与空堆栈。这里我们没有使用`option`，这表明`peek`
将在空堆栈上引发异常。所以我们谨慎地放松我们的
禁止例外。

过去我们用英语给出了这些操作规范，例如，

```ocaml
  (** [push x s] is the stack [s] with [x] pushed on the top. *)
  val push : 'a -> 'a stack -> 'a stack
```

但现在，我们将编写一些方程来描述操作的工作原理：

```text
1. is_empty empty = true
2. is_empty (push x s) = false
3. peek (push x s) = x
4. pop (push x s) = s
```

（稍后我们将回到*如何*设计此类方程的问题。）
这些方程中出现的变量都被隐式普遍量化。
以下是如何阅读每个方程：

1. `is_empty empty = true`。  空栈是空的。

2. `is_empty (push x s) = false`。  刚刚压入的堆栈是
非空。

3. `peek (push x s) = x`。  推动然后立即查看会产生任何结果
价值被推了。

4. `pop (push x s) = s`。  推入然后立即弹出产生原始的
堆栈。

仅凭这些方程，我们就可以推断出很多关于如何
堆栈操作的顺序必须有效。例如，

```text
  peek (pop (push 1 (push 2 empty)))
=   { equation 4 }
  peek (push 2 empty)
=   { equation 3 }
  2
```

根据方程， `peek empty` 不等于任何值，因为有
不存在 `peek empty = ...` 形式的方程。一切都是真实的，无论
选择的堆栈实现：任何正确的实现都必须导致
要保持的方程。

假设我们将堆栈实现为列表，如下所示：

```{code-cell} ocaml
:tags: ["hide-output"]
module ListStack = struct
  type 'a t = 'a list
  let empty = []
  let is_empty = function [] -> true | _ -> false
  let peek = List.hd
  let push = List.cons
  let pop = List.tl
end
```

接下来我们可以*证明*每个方程都适用于实现。所有这些
现在证明很容易，并且完全通过评估进行。例如，
这是方程 3 的证明：

```text
  peek (push x s)
=   { evaluation }
  peek (x :: s)
=   { evaluation }
  x
```

## 示例：队列

{{ video_embed | replace("%%VID%%", "lAJz6ZnsbNI")}}

堆栈很容易。  排队怎么样？  这是规格：

```{code-cell} ocaml
:tags: ["hide-output"]
module type Queue = sig
  type 'a t
  val empty : 'a t
  val is_empty : 'a t -> bool
  val front : 'a t -> 'a
  val enq : 'a -> 'a t -> 'a t
  val deq : 'a t -> 'a t
end
```

```text
1.  is_empty empty = true
2.  is_empty (enq x q) = false
3a. front (enq x q) = x            if is_empty q = true
3b. front (enq x q) = front q      if is_empty q = false
4a. deq (enq x q) = empty          if is_empty q = true
4b. deq (enq x q) = enq x (deq q)  if is_empty q = false
```

队列操作的类型实际上与类型相同
的堆栈操作。  在这里，将它们并排进行比较：
```ocaml
module type Stack = sig            module type Queue = sig
  type 'a t                          type 'a t
  val empty : 'a t                   val empty : 'a t
  val is_empty : 'a t -> bool        val is_empty : 'a t -> bool
  val peek : 'a t -> 'a              val front : 'a t -> 'a
  val push : 'a -> 'a t -> 'a t      val enq : 'a -> 'a t -> 'a t
  val pop : 'a t -> 'a t             val deq : 'a t -> 'a t
end                                end
```
查看每一行：虽然操作可能有不同的名称，但它的类型
是一样的。  显然，仅这些类型并不能告诉我们足够的信息
操作。  但方程式确实如此！  以下是如何阅读每个方程：

1. 空队列是空的。

2. 入队使队列非空。

3. 将 `x` 放入空队列会使 `x` 成为前面的元素。
但如果队列不为空，则排队不会更改前面的元素。

4. 在空队列上入队然后出队会使队列为空。
但如果队列不为空，则可以进行入队和出队操作
   被交换。

例如，

```text
  front (deq (enq 1 (enq 2 empty)))
=   { equations 4b and 2 }
  front (enq 1 (deq (enq 2 empty)))
=   { equations 4a and 1 }
  front (enq 1 empty)
=   { equations 3a and 1 }
  1
```

根据方程式，`front empty` 不等于任何值。

将队列实现为列表会导致易于实现的实现
仅通过评估进行验证。

```{code-cell} ocaml
module ListQueue : Queue = struct
  type 'a t = 'a list
  let empty = []
  let is_empty q = q = []
  let front = List.hd
  let enq x q = q @ [x]
  let deq = List.tl
end
```

例如4a可以这样验证：

```text
  deq (enq x empty)
=   { evaluation of empty and enq}
  deq ([] @ [x])
=   { evaluation of @ }
  deq [x]
=   { evaluation of deq }
  []
=   { evaluation of empty }
  empty
```

以及4b，如下：
```text
  deq (enq x q)
=  { evaluation of enq and deq }
  List.tl (q @ [x])
=  { lemma, below, and q <> [] }
  (List.tl q) @ [x]

  enq x (deq q)
=  { evaluation }
  (List.tl q) @ [x]
```

这是引理：

```text
Lemma: if xs <> [], then List.tl (xs @ ys) = (List.tl xs) @ ys.
Proof: if xs <> [], then xs = h :: t for some h and t.

  List.tl ((h :: t) @ ys)
=   { evaluation of @ }
  List.tl (h :: (t @ ys))
=   { evaluation of tl }
  t @ ys

  (List.tl (h :: t)) @ ys
=   { evaluation of tl }
  t @ ys

QED
```

请注意 3b 和 4b 中 `q` 不为空的前提条件如何确保我们
永远不必处理等式证明中提出的异常。

## 示例：批量队列

回想一下，批处理队列表示具有两个列表的队列：

```{code-cell} ocaml
:tags: ["hide-output"]
module BatchedQueue = struct
  (* AF: [(o, i)] represents the queue [o @ (List.rev i)].
     RI: if [o] is empty then [i] is empty. *)
  type 'a t = 'a list * 'a list

  let empty = ([], [])

  let is_empty (o, i) = if o = [] then true else false

  let enq x (o, i) = if o = [] then ([x], []) else (o, x :: i)

  let front (o, _) = List.hd o

  let deq (o, i) =
    match List.tl o with
    | [] -> (List.rev i, [])
    | t -> (t, i)
end
```

这个实现与之前的实现有表面上的不同
我们给出的，因为它使用对而不是记录，并且它引发了内置
异常 `Failure` 而不是自定义异常 `Empty`。

这个实现正确吗？  我们只需验证方程即可找到答案。

首先，一个引理：

```text
Lemma:  if is_empty q = true, then q = empty.
Proof:  Since is_empty q = true, it must be that q = (f, b) and f = [].
By the RI, it must also be that b = [].  Thus q = ([], []) = empty.
QED
```

验证方程 1：

```text
  is_empty empty
=   { eval empty }
  is_empty ([], [])
=   { eval is_empty }
  [] = []
=   { eval = }
  true
```

验证方程 2：

```text
  is_empty (enq x q) = false
=   { eval enq }
  is_empty (if f = [] then [x], [] else f, x :: b)

case analysis: f = []

  is_empty (if f = [] then [x], [] else f, x :: b)
=   { eval if, f = [] }
  is_empty ([x], [])
=   { eval is_empty }
  [x] = []
=   { eval = }
  false

case analysis: f = h :: t

  is_empty (if f = [] then [x], [] else f, x :: b)
=   { eval if, f = h :: t }
  is_empty (h :: t, x :: b)
=   { eval is_empty }
  h :: t = []
=   { eval = }
  false
```

验证方程 3a：

```text
  front (enq x q) = x
=   { emptiness lemma }
  front (enq x ([], []))
=   { eval enq }
  front ([x], [])
=   { eval front }
  x
```

验证方程 3b：

```text
  front (enq x q)
=   { rewrite q as (h :: t, b), because q is not empty }
  front (enq x (h :: t, b))
=   { eval enq }
  front (h :: t, x :: b)
=   { eval front }
  h

  front q
=   { rewrite q as (h :: t, b), because q is not empty }
  front (h :: t, b)
=   { eval front }
  h
```

验证方程 4a：

```text
  deq (enq x q)
=   { emptiness lemma }
  deq (enq x ([], []))
=   { eval enq }
  deq ([x], [])
=   { eval deq }
  List.rev [], []
=   { eval rev }
  [], []
=   { eval empty }
  empty
```

验证方程 4b：

```text
Show: deq (enq x q) = enq x (deq q)  assuming is_empty q = false.
Proof: Since is_empty q = false, q must be (h :: t, b).

Case analysis:  t = [], b = []

  deq (enq x q)
=   { rewriting q as ([h], []) }
  deq (enq x ([h], []))
=   { eval enq }
  deq ([h], [x])
=   { eval deq }
  List.rev [x], []
=   { eval rev }
  [x], []

  enq x (deq q)
=   { rewriting q as ([h], []) }
  enq x (deq ([h], []))
=   { eval deq }
  enq x (List.rev [], [])
=   { eval rev }
  enq x ([], [])
=   { eval enq }
  [x], []

Case analysis:  t = [], b = h' :: t'

  deq (enq x q)
=   { rewriting q as ([h], h' :: t') }
  deq (enq x ([h], h' :: t'))
=   { eval enq }
  deq ([h], x :: h' :: t')
=   { eval deq }
  (List.rev (x :: h' :: t'), [])

  enq x (deq q)
=   { rewriting q as ([h], h' :: t') }
  enq x (deq ([h], h' :: t'))
=   { eval deq }
  enq x (List.rev (h' :: t'), [])
=   { eval enq }
  (List.rev (h' :: t'), [x])

STUCK
```

等等，我们刚刚被困住了！ `(List.rev (x :: h' :: t'), [])` 和
`(List.rev (h' :: t'), [x])` 不同。但是，抽象地讲，他们确实
代表同一个队列：`(List.rev t') @ [h'; x]`。

为了解决这个问题，我们将采用以下方程来表示
类型：

```text
e = e'   if  AF(e) = AF(e')
```

该方程使我们得出结论，两个不同的表达式是
等于：

```text
  AF((List.rev (h' :: t'), [x]))
=   { apply AF }
  List.rev (h' :: t') @ List.rev [x]
=   { rev distributes over @, an exercise in the previous lecture }
  List.rev ([x] @ (h' :: t'))
=   { eval @ }
  List.rev (x :: h' :: t')

  AF((List.rev (x :: h' :: t'), []))
=   { apply AF }
  List.rev (x :: h' :: t') @ List.rev []
=   { eval rev }
  List.rev (x :: h' :: t') @ []
=   { eval @ }
  List.rev (x :: h' :: t')
```

现在我们摆脱困境了：

```text
  (List.rev (h' :: t'), [x])
=   { AF equation }
  (List.rev (x :: h' :: t'), [])
```

还剩下一个案例分析来完成证明：

```text
Case analysis:  t = h' :: t'

  deq (enq x q)
=   { rewriting q as (h :: h' :: t', b) }
  deq (enq x (h :: h' :: t', b))
=   { eval enq }
  deq (h :: h' :: t, x :: b)
=   { eval deq }
  h' :: t, x :: b

  enq x (deq q)
=   { rewriting q as (h :: h' :: t', b) }
  enq x (deq (h :: h' :: t', b))
=   { eval deq }
  enq x (h' :: t', b)
=   { eval enq }
  h' :: t', x :: b

QED
```

我们对批量队列的验证到此结束。请注意，我们必须添加
涉及抽象函数的额外方程以获得证明
通过：

```text
e = e'   if  AF(e) = AF(e')
```

我们在证明过程中使用了 RI。 AF 和 RI 确实是
重要！

## 设计等式规范

{{ video_embed | replace("%%VID%%", "8uJmKmsiF2I")}}

对于堆栈和队列，我们提供了一些方程作为规范。
设计这些方程在某种程度上是认真思考数据的问题
结构。但还有更多的事情要做。

数据结构的每个值都是通过一些操作构造的。对于一个
堆栈，这些操作是 `empty` 和 `push`。可能有一些 `pop`
涉及的操作，但这些操作是可以消除的。例如，`pop (push 1
（推 2 空））` is really the same stack as `推 2 空`。后者是
该堆栈的*规范形式*：还有许多其他方法来构造它，但是
这是最简单的。事实上，每个可能的堆栈值都可以构造为
与 `empty` 和 `push`。类似地，每个可能的队列值都可以是
仅使用 `empty` 和 `enq` 构造：如果涉及 `deq` 操作，
这些是可以消除的。

我们将数据结构的操作分类如下：

- **生成器**是涉及创建规范形式的那些操作。
它们返回数据结构类型的值。例如，`empty`、`push`、
  `enq`。

- **操纵器**是创建数据结构值的操作
类型，但不需要创建规范形式。例如，`pop`、`deq`。

- **查询**不返回数据结构类型的值。例如，
`is_empty`、`peek`、`front`。

给定这样的分类，我们可以设计一个方程的规范
通过将非生成器应用于生成器来构建数据结构。例如：什么是
`is_empty` 返回 `empty`？在 `push` 上？ `front` 在 `enq` 上返回什么？什么
`deq` 是否在 `enq` 上返回？等等

因此，如果数据结构有 `n` 生成器和 `m` 非生成器，我们
首先尝试创建 `n*m` 方程，每对一个
发电机和非发电机。每个方程都将展示如何简化
表达。在某些情况下，我们可能需要几个方程，具体取决于
一些比较的结果。例如，在队列规范中，我们有
以下方程：

1. `is_empty empty = true`：这是一个非生成器 `is_empty` 应用于
生成器 `empty`。它只是减少为布尔值，这不涉及
   数据结构类型（队列）。

2. `is_empty (enq x q) = false`：非生成器 `is_empty` 应用于
生成器 `enq`。它再次简单地简化为布尔值。

3. 有两个子情况。

   - `front (enq x q) = x`，如果 `is_empty q = true`。非生成器 `front`
应用于生成器 `enq`。它减少到 `x`，这是一个更小的
     表达式比原来的`front (enq x q)`。

   - `front (enq x q) = front q`，`if is_empty q = false`。这同样
简化为更小的表达式。

4. 同样，有两个子情况。

   - `deq (enq x q) = empty`，如果 `is_empty q = true`。这简化了
原始表达式，将其减少为 `empty`。

   - `deq (enq x q) = enq x (deq q)`，如果 `is_empty q = false`。这简化了
原始表达式，通过将其简化为应用于更小的生成器
     参数，`deq q` 而不是 `deq (enq x q)`。

我们通常不会设计涉及非生成元对的方程。有时
不过，需要成对的生成器，正如我们将在下一个示例中看到的那样。

**示例：集合。** 这是集合的一个小界面：

```{code-cell} ocaml
:tags: ["hide-output"]
module type Set = sig
  type 'a t
  val empty : 'a t
  val is_empty : 'a t -> bool
  val add : 'a -> 'a t -> 'a t
  val mem : 'a -> 'a t -> bool
  val remove : 'a -> 'a t -> 'a t
end
```

生成器是 `empty` 和 `add`。唯一的操纵器是 `remove`。最后，
`is_empty` 和 `mem` 是查询。所以我们应该期望至少 2 * 3 = 6
方程，每对生成器和非生成器一个。这是一个
等式规范：

```text
1.  is_empty empty = true
2.  is_empty (add x s) = false
3.  mem x empty = false
4a. mem y (add x s) = true                    if x = y
4b. mem y (add x s) = mem y s                 if x <> y
5.  remove x empty = empty
6a. remove y (add x s) = remove y s           if x = y
6b. remove y (add x s) = add x (remove y s)   if x <> y
```

不过，请考虑这两组：

- `add 0 (add 1 empty)`
- `add 1 (add 0 empty)`

它们都直观地表示集合 {0,1}。然而，我们无法证明那些
使用上述规范，两组是相等的。我们缺少一个方程
涉及两台发电机：

```
7.  add x (add y s) = add y (add x s)
```
