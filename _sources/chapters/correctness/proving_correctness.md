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

# 证明正确性

{{ video_embed | replace("%%VID%%", "48GBq4koKPs")}}

测试提供正确性的证据，但不能完全保证。即使之后
广泛的黑盒和玻璃盒测试，也许还有一些测试用例
程序员未能发明，该测试用例将揭示程序中的错误
程序。

```{epigraph}
程序测试可用于显示错误的存在，但绝不能显示错误的不存在。

——埃兹格·W·迪杰斯特拉
```

重点不是测试没有用！它可能非常有效。但这是一个
一种*归纳推理*，其中证据（即通过测试）
积累支持结论（即程序的正确性）
并不能绝对保证该结论的有效性。 （请注意，
这里的“归纳”一词与证明的含义不同
称为归纳法的技术。）为了获得这种保证，我们转向*演绎
推理*，其中我们从逻辑的前提和规则出发，得出有效的结论
结论。换句话说，我们证明了程序的正确性。我们的目标，
接下来，是学习此类正确性证明的一些技术。这些技巧
由于使用了逻辑形式主义，因此被称为“形式方法”。

*正确性*在这里意味着程序产生正确的输出
根据*规范*。规格通常在
函数的文档（因此称为“规范注释”）：它们
描述程序的前提条件和后置条件。后置条件，正如我们
一直在写它们，其形式为“[f x] 是“...输出的描述
就输入 [x]..."` 而言。例如，阶乘的规范
函数可以是：

```ocaml
(** [fact n] is [n!]. Requires: [n >= 0]. *)
let rec fact n = ...
```

后置条件断言函数的输出之间相等
以及一些关于输入计算的英文描述。 *正式
verification* 是证明函数的实现的任务
满足其规格。

等式是我们思考正确性的基本方式之一
函数式程序。不存在可变状态使得推理成为可能
直接判断两个表达式是否相等。很难做到
在命令式语言中，因为这些表达可能有侧面
改变状态的效果。

## 相等

{{ video_embed | replace("%%VID%%", "zjDUrMdVC5U")}}

什么时候两个表达式相等？  两个可能的答案是：

- 当它们在语法上相同时。

- 当它们在语义上等效时：它们产生相同的值。

例如，`42` 和 `41+1` 是否相等？语法答案会说它们是
不是，因为它们涉及不同的标记。语义答案会说它们
是：它们都产生值 `42`。

那么函数呢：`fun x -> x` 和 `fun y -> y` 相等吗？从句法上来说
他们是不同的。但从语义上讲，它们都产生一个值，即
恒等函数：当它们应用于输入时，它们都会产生
相同的输出。即 `(fun x -> x) z = z` 和 `(fun y -> y) z = z`。如果是的话
对于所有输入，两个函数产生相同输出的情况，我们将
考虑函数相等：

```text
if (forall x, f x = g x), then f = g.
```

函数相等的定义被称为 *Axiom of
数学某些分支的外延性*；今后我们会参考它
简单地说就是“外延性”。

这里我们将采用语义方法。如果 `e1` 和 `e2` 计算结果相同
值 `v`，然后我们写 `e1 = e2`。我们在数学中使用 `=`
平等感，不像 OCaml 多态相等运算符。例如，
我们允许 `(fun x -> x) = (fun y -> y)`，即使 OCaml 的运算符会引发
异常并拒绝比较函数。

我们还将限制自己使用类型良好、纯粹的表达式
（意味着它们没有副作用）和总体（意味着它们没有
异常或无限循环）。

## 等式推理

{{ video_embed | replace("%%VID%%", "MjpZJA1jIqU")}}

考虑这些函数：

```{code-cell} ocaml
let twice f x = f (f x)
let compose f g x = f (g x)
```

从 OCaml 评估规则中我们知道 `twice h x = h (h x)`，并且
同样，`compose h h x = h (h x)`。因此我们有：

```ocaml
twice h x = h (h x) = compose h h x
```

因此，我们可以得出结论：`twice h x = compose h h x`。并由
外延性我们可以简化这个等式：因为 `twice h x = compose h h x`
对于所有 `x` 都成立，我们可以得出 `twice h = compose h h` 的结论。

另一个例子，假设我们为函数定义一个中缀运算符
组成：

```ocaml
let ( << ) = compose
```

然后我们可以使用等式推理来证明组合是关联的：

```text
Theorem: (f << g) << h  =  f << (g << h)

Proof: By extensionality, we need to show
  ((f << g) << h) x  =  (f << (g << h)) x
for an arbitrary x.

  ((f << g) << h) x
= (f << g) (h x)
= f (g (h x))

and

  (f << (g << h)) x
= f ((g << h) x)
= f (g (h x))

So ((f << g) << h) x = f (g (h x)) = (f << (g << h)) x.

QED
```

上述等式证明中的所有步骤均来自评估。
另一种书写证明的格式将提供关于原因的提示
每个步骤都是有效的：

```text
  ((f << g) << h) x
=   { evaluation of << }
  (f << g) (h x)
=   { evaluation of << }
  f (g (h x))

and

  (f << (g << h)) x
=   { evaluation of << }
  f ((g << h) x)
=   { evaluation of << }
  f (g (h x))
```

## 自然数归纳法

{{ video_embed | replace("%%VID%%", "By4VSmpzuHw")}}

以下函数对 `n` 之前的非负整数求和：

```{code-cell} ocaml
let rec sumto n =
  if n = 0 then 0 else n + sumto (n - 1)
```

你可能还记得，相同的求和可以用封闭形式表示：
`n * (n + 1) / 2`。为了证明`forall n >= 0, sumto n = n * (n + 1) / 2`，我们
将需要*数学归纳法*。

回想一下自然数（即非负整数）的归纳法
公式如下：

```text
forall properties P,
  if P(0),
  and if forall k, P(k) implies P(k + 1),
  then forall n, P(n)
```

这就是自然数的“归纳原理”。 *基本情况*是
证明 `P(0)`，而*归纳案例*是证明 `P(k + 1)` 成立
在*归纳假设* `P(k)` 的假设下。

{{ video_embed | replace("%%VID%%", "JRNxlQYOLyw")}}

我们用归纳法来证明`sumto`的正确性。

```text
Claim: sumto n = n * (n + 1) / 2

Proof: by induction on n.
P(n) = sumto n = n * (n + 1) / 2

Base case: n = 0
Show: sumto 0 = 0 * (0 + 1) / 2

  sumto 0
=   { evaluation }
  0
=   { algebra }
  0 * (0 + 1) / 2

Inductive case: n = k + 1
Show: sumto (k + 1) = (k + 1) * ((k + 1) + 1) / 2
IH: sumto k = k * (k + 1) / 2

  sumto (k + 1)
=   { evaluation }
  k + 1 + sumto k
=   { IH }
  k + 1 + k * (k + 1) / 2
=   { algebra }
  (k + 1) * (k + 2) / 2

QED
```

请注意，我们在每种情况下都非常小心地写出我们需要的内容
显示，并写下归纳假设。展示很重要
所有这些工作。

假设我们现在定义：

```{code-cell} ocaml
let sumto_closed n = n * (n + 1) / 2
```

那么作为我们之前的主张的推论，通过外延性我们可以得出结论

```text
sumto_closed = sumto
```

从技术上讲，等式仅包含自然数输入。但自从
今后我们所有的例子都将针对自然数，而不是整数本身，我们将
删除说明有关自然数的任何先决条件或限制。

## 程序作为规范

我们刚刚证明了有效实现的正确性
实施效率低下。低效的实现 `sumto` 服务
作为高效实现的规范，`sumto_closed`。

这种技术在验证函数式程序时很常见：编写一个明显的
缺少某些所需属性的正确实现，例如
效率，然后证明更好的实现与原始实现相同。

让我们再举一个此类验证的例子。这次，好好利用
阶乘函数。

{{ video_embed | replace("%%VID%%", "htMNllWnLzg")}}

阶乘的简单且明显正确的实现是：

```{code-cell} ocaml
let rec fact n =
  if n = 0 then 1 else n * fact (n - 1)
```

尾递归实现对于堆栈空间会更有效：

```{code-cell} ocaml
let rec facti acc n =
  if n = 0 then acc else facti (acc * n) (n - 1)

let fact_tr n = facti 1 n
```

名称 `facti` 中的 `i` 代表*迭代*。我们称之为迭代
实现，因为它非常类似于相同的计算方式
在命令式中使用循环（即迭代构造）来表达
语言。例如，在 Java 中我们可以这样写：

```java
int facti (int n) {
  int acc = 1;
  while (n != 0) {
    acc *= n;
    n--;
  }
  return acc;
}
```

`facti` 的 OCaml 和 Java 实现共享以下功能：

- 他们从 `1` 开始 `acc`
- 他们检查 `n` 是否为 `0`
- 他们将 `acc` 乘以 `n`
- 他们递减 `n`
- 他们返回累加器 `acc`

让我们尝试证明 `fact_tr` 正确实现了与
`fact`。

```text
Claim: forall n, fact n = fact_tr n

Since fact_tr n = facti 1 n, it suffices to show fact n = facti 1 n.

Proof: by induction on n.
P(n) = fact n = facti 1 n

Base case: n = 0
Show: fact 0 = facti 1 0

  fact 0
=   { evaluation }
  1
=   { evaluation }
  facti 1 0

Inductive case: n = k + 1
Show: fact (k + 1) = facti 1 (k + 1)
IH: fact k = facti 1 k

  fact (k + 1)
=   { evaluation }
  (k + 1) * fact k
=   { IH }
  (k + 1) * facti 1 k

  facti 1 (k + 1)
=   { evaluation }
  facti (1 * (k + 1)) k
=   { evaluation }
  facti (k + 1) k

Unfortunately, we're stuck.  Neither side of what we want to show
can be manipulated any further.

ABORT
```

我们知道 `facti (k + 1) k` 和 `(k + 1) * facti 1 k` 应该产生相同的结果
值。但 IH 只允许我们使用 `1` 作为 `facti` 的第二个参数，
而不是像 `k + 1` 这样的更大的参数。所以我们的证明在那一刻就误入歧途了
我们用的是IH。我们需要一个更强的归纳假设！

因此，让我们加强我们的主张。而不是表明
`fact n = facti 1 n`，我们将尝试显示`forall p, p * fact n = facti p n`。那
将 `k + 1` 概括为任意数量 `p`。

```text
Claim: forall n, forall p . p * fact n = facti p n

Proof: by induction on n.
P(n) = forall p, p * fact n = facti p n

Base case:  n = 0
Show: forall p,  p * fact 0 = facti p 0

  p * fact 0
=   { evaluation and algebra }
  p
=   { evaluation }
  facti p 0

Inductive case: n = k + 1
Show: forall p,  p * fact (k + 1) = facti p (k + 1)
IH: forall p,  p * fact k = facti p k

  p * fact (k + 1)
=   { evaluation }
  p * (k + 1) * fact k
=   { IH, instantiating its p as p * (k + 1) }
  facti (p * (k + 1)) k

  facti p (k + 1)
=   { evaluation }
  facti (p * (k + 1)) k

QED

Claim: forall n, fact n = fact_tr n

Proof:

  fact n
=   { algebra }
  1 * fact n
=   { previous claim }
  facti 1 n
=   { evaluation }
  fact_tr n

QED
```

这就完成了我们的证明，即高效的尾递归函数 `fact_tr` 是
相当于简单的递归函数 `fact`。本质上我们已经证明了
使用 `fact` 作为其规范的 `fact_tr` 的正确性。

## 递归与迭代

我们添加了一个累加器作为额外参数，以使阶乘函数为
尾递归。这是我们以前见过的伎俩。让我们抽象一下，看看如何
一般情况下做。

假设我们有一个整数的递归函数：

```ocaml
let rec f_r n =
  if n = 0 then i else op n (f_r (n - 1))
```

这里，`f_r`中的`r`意味着`f_r`是一个递归函数。
`i` 和 `op` 是函数的一部分，应该被替换为
一些具体值 `i` 和运算符 `op`。例如，阶乘
函数，我们有：

```ocaml
f_r = fact
i = 1
op = ( * )
```

这样的函数可以通过如下重写来使其成为尾递归：

```ocaml
let rec f_i acc n =
  if n = 0 then acc
  else f_i (op acc n) (n - 1)

let f_tr = f_i i
```

这里，`f_i`中的`i`意味着`f_i`是一个迭代函数，
`i` 和 `op` 与函数的递归版本中的相同。对于
例如，对于阶乘我们有：

```ocaml
f_i = fact_i
i = 1
op = ( * )
f_tr = fact_tr
```

我们可以证明 `f_r` 和 `f_tr` 计算相同的函数。证明过程中，
接下来，我们将发现 `i` 和 `op` 必须满足的某些条件才能使
尾递归的转换是正确的。

```text
Theorem: f_r = f_tr

Proof:  By extensionality, it suffices to show that forall n, f_r n = f_tr n.

As in the previous proof for fact, we will need a strengthened induction
hypothesis. So we first prove this lemma, which quantifies over all accumulators
that could be input to f_i, rather than only i:

  Lemma: forall n, forall acc, op acc (f_r n) = f_i acc n

  Proof of Lemma: by induction on n.
  P(n) = forall acc, op acc (f_r n) = f_i acc n

  Base: n = 0
  Show: forall acc, op acc (f_r 0) = f_i acc 0

    op acc (f_r 0)
  =   { evaluation }
    op acc i
  =   { if we assume forall x, op x i = x }
    acc

    f_i acc 0
  =   { evaluation }
    acc

  Inductive case: n = k + 1
  Show: forall acc, op acc (f_r (k + 1)) = f_i acc (k + 1)
  IH: forall acc, op acc (f_r k) = f_i acc k

    op acc (f_r (k + 1))
  =   { evaluation }
    op acc (op (k + 1) (f_r k))
  =   { if we assume forall x y z, op x (op y z) = op (op x y) z }
    op (op acc (k + 1)) (f_r k)

    f_i acc (k + 1)
  =   { evaluation }
    f_i (op acc (k + 1)) k
  =   { IH, instantiating acc as op acc (k + 1)}
    op (op acc (k + 1)) (f_r k)

  QED

The proof then follows almost immediately from the lemma:

  f_r n
=   { if we assume forall x, op i x = x }
  op i (f_r n)
=   { lemma, instantiating acc as i }
  f_i i n
=   { evaluation }
  f_tr n

QED
```

在此过程中，我们对 i 和 op 做出了三个假设：

1. `forall x, op x i = x`
2. `op x (op y z) = op (op x y) z`
3. `forall x, op i x = x`

第一个和第三个表示 `i` 是 `op` 的*身份*：在左侧使用它
或者右侧保留另一个参数 `x` 不变。第二个说 `op`
是*关联*。这两个假设都适用于我们在
阶乘函数：

- `op` 是乘法，具有结合律。
- `i` 是 `1`，它是乘法的恒等式：乘以 1 个叶子
另一个参数不变。

因此，我们从递归函数到尾递归函数的转换是有效的：
只要递归调用中应用的运算符是结合的，并且值
基本情况中返回的是该操作员的身份。

回到`sumto`函数，我们可以应用刚刚证明的定理
立即得到尾递归版本：

```{code-cell} ocaml
let rec sumto_r n =
  if n = 0 then 0 else n + sumto_r (n - 1)
```

这里，运算符是加法，具有结合性；且基本情况为零，
这是加法的恒等式。因此我们的定理适用，我们可以使用
它甚至无需考虑即可生成尾递归版本：

```{code-cell} ocaml
let rec sumto_i acc n =
  if n = 0 then acc else sumto_i (acc + n) (n - 1)

let sumto_tr = sumto_i 0
```

由于我们的定理，我们已经知道 `sumto_tr` 是正确的。

## 终止

{{ video_embed | replace("%%VID%%", "Xy7GTfEfIK4")}}

有时程序的正确性进一步分为：

- **部分正确**：意味着*如果*一个程序终止，那么它的
输出正确；和

- **完全正确**：意味着程序*确实*终止，*并且*其
输出正确。

因此，完全正确性是部分正确性和
终止。到目前为止，我们已经证明了部分正确性。

证明程序终止是很困难的。确实，这是不可能的
算法这样做的一般原则是：计算机无法精确地决定是否
程序将终止。 （有关更多详细信息，请参阅“停机问题”。）但是，
聪明的人有时能做到这一点。

有一个简单的启发式可以用来证明递归函数
终止：

- 所有递归调用都在“较小”的输入上，并且
- 所有基本情况都将终止。

例如，考虑阶乘函数：

```{code-cell} ocaml
let rec fact n =
  if n = 0 then 1
  else n * fact (n - 1)
```

基本情况 `1` 显然已终止。递归调用在`n - 1`上，
这是比原始 `n` 更小的输入。所以 `fact` 总是终止（如
只要其输入是自然数）。

同样的推理也适用于我们上面讨论的所有其他函数。

为了使这一点更加精确，我们需要了解“变小”意味着什么。
假设我们在输入上有一个二元关系 `<` 。尽管有符号，这
关系不必是整数上的小于关系——尽管这会
为 `fact` 工作。还假设永远不可能创建无限
使用此关系的元素的序列 `x0 > x1 > x2 > x3 ...` 。 （哪里的
当然`a > b`当且仅当`b < a`。）也就是说，不存在无限
元素的降序链：一旦选择起始元素 `x0`，就可以
根据你面前的 `<` 关系，只有有限数量的“血统”
触底并触及基本情况。 `<` 的这一属性使其成为*有充分根据的
关系*。

因此，如果所有递归调用都针对元素，则递归函数将终止
根据 `<` 较小。为什么？因为只能有有限的
达到基本情况之前的调用次数，并且基本情况必须终止。

通常的 `<` 关系在自然数上是有充分根据的，因为
最终任何链都必须达到 0 的基本情况。但这并不是有充分根据的
在整数上，它可能会变得越来越小：`-1 > -2 > -3 > ...`。

这是一个有趣的函数，通常的 `<` 关系不足以满足要求
证明终止：

```{code-cell} ocaml
let rec ack = function
  | (0, n) -> n + 1
  | (m, 0) -> ack (m - 1, 1)
  | (m, n) -> ack (m - 1, ack (m, n - 1))
```

这称为*阿克曼函数*。它的增长速度比任何指数都快
函数。尝试运行 `ack (1, 1)`、`ack (2, 1)`、`ack (3, 1)`，然后运行 `ack (4,
1)` 来了解一下。这也是一个著名的函数示例，可以
使用 `while` 循环实现，但不能使用 `for` 循环实现。尽管如此，它确实
终止。

为了证明这一点，基本情况很简单：当输入为 `(0, _)` 时，函数
终止。但在其他情况下，它会进行递归调用，我们需要定义
适当的 `<` 关系。事实证明，“字典顺序”是对的
作品。如果满足以下条件，则定义 `(a, b) < (c, d)`：

- `a < c`，或
- `a = c` 和 `b < d`。

这两种情况下的 `<` 顺序是自然数上常见的 `<` 顺序。

在第一个递归调用中，`(m - 1, 1) < (m, 0)` 由第一种情况
`<` 的定义，因为 `m - 1 < m`。在嵌套递归调用中
`ack (m - 1, ack (m, n - 1))`，两种情况都需要：

- `(m, n - 1) < (m, n)` 因为 `m = m` 和 `n - 1 < n`
- `(m - 1, _) < (m, n)` 因为 `m - 1 < m`。
