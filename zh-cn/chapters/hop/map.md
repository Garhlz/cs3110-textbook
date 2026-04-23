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

# Map

{{ video_embed | replace("%%VID%%", "qz7kn2pIl3M")}}

以下是我们可能想要编写的两个函数：
```{code-cell} ocaml
(** [add1 lst] adds 1 to each element of [lst]. *)
let rec add1 = function
  | [] -> []
  | h :: t -> (h + 1) :: add1 t

let lst1 = add1 [1; 2; 3]
```

```{code-cell} ocaml
(** [concat_bang lst] concatenates "!" to each element of [lst]. *)
let rec concat_bang = function
  | [] -> []
  | h :: t -> (h ^ "!") :: concat_bang t

let lst2 = concat_bang ["sweet"; "salty"]
```

这两个函数有很多相似之处：

- 它们都针对列表进行模式匹配。
- 对于空列表的基本情况，它们都返回相同的值。
- 在非空列表的情况下，它们都在尾部递归。

事实上，唯一的区别（除了他们的名字）是他们为
head 元素：添加与连接。让我们重写这两个函数
这种差异更加明显：

```{code-cell} ocaml
(** [add1 lst] adds 1 to each element of [lst]. *)
let rec add1 = function
  | [] -> []
  | h :: t ->
    let f = fun x -> x + 1 in
    f h :: add1 t

(** [concat_bang lst] concatenates "!" to each element of [lst]. *)
let rec concat_bang = function
  | [] -> []
  | h :: t ->
    let f = fun x -> x ^ "!" in
    f h :: concat_bang t
```

现在这两个函数之间的唯一区别（同样，除了它们的
名称）是辅助函数 `f` 的主体。为什么要重复所有这些代码呢？
函数差别这么小？我们不妨“抽象”一下
每个主函数中都有一个辅助函数，并将其作为一个参数：

```{code-cell} ocaml
let rec add1' f = function
  | [] -> []
  | h :: t -> f h :: add1' f t

(** [add1 lst] adds 1 to each element of [lst]. *)
let add1 = add1' (fun x -> x + 1)

let rec concat_bang' f = function
  | [] -> []
  | h :: t -> f h :: concat_bang' f t

(** [concat_bang lst] concatenates "!" to each element of [lst]. *)
let concat_bang = concat_bang' (fun x -> x ^ "!")
```

但现在 `add1'` 和 `concat_bang'` 之间确实没有任何区别
除了他们的名字。它们是完全重复的代码。甚至他们的类型都是
现在是一样的，因为它们没有提到整数或字符串。我们可能
也可以只保留其中一个，并为其想一个好听的新名字。一
可能性可能是 `transform`，因为它们通过应用
对列表中的每个元素执行函数：

```{code-cell} ocaml
let rec transform f = function
  | [] -> []
  | h :: t -> f h :: transform f t

(** [add1 lst] adds 1 to each element of [lst]. *)
let add1 = transform (fun x -> x + 1)

(** [concat_bang lst] concatenates "!" to each element of [lst]. *)
let concat_bang = transform (fun x -> x ^ "!")
```

````{note}
而不是
```ocaml
let add1 lst = transform (fun x -> x + 1) lst
```
上面我们写了
```ocaml
let add1 = transform (fun x -> x + 1)
```
这是另一种更高阶的方式，但这是我们已经学到的
关于部分应用的幌子。  后一种写法
该函数部分地将 `transform` 应用于其两个之一
参数，从而返回一个函数。  该函数绑定到
名称 `add1`。
````

事实上，C++ 库确实调用了等效函数 `transform`。但是OCaml
和许多其他语言（包括 Java 和 Python）使用较短的单词 *map*，
在数学意义上，函数如何将输入映射到输出。那么让我们
对该名称进行最后一项更改：

```{code-cell} ocaml
let rec map f = function
  | [] -> []
  | h :: t -> f h :: map f t

(** [add1 lst] adds 1 to each element of [lst]. *)
let add1 = map (fun x -> x + 1)

(** [concat_bang lst] concatenates "!" to each element of [lst]. *)
let concat_bang = map (fun x -> x ^ "!")
```

我们现在已经成功应用了抽象原则：通用结构
已经被提取出来。剩下的代码至少对熟悉 `map` 的读者来说，
比原始版本更清楚地表达了计算。

{{ video_embed | replace("%%VID%%", "hynjCGMpcFk")}}

## 副作用

`map` 函数已经作为 `List.map` 存在于 OCaml 的标准库中，但是
与我们上面发现的实现有一点小小的不同。  首先，
让我们看看我们自己的实现有什么潜在的问题，然后我们看看
在标准库的实现中。

我们之前在 [exceptions](../data/exceptions) 的讨论中已经看到
OCaml 语言规范通常不指定计算顺序
子表达式，而当前的语言实现通常会
从右到左求值。因此，下面这段（相当刻意构造的）代码实际上
导致列表元素以看似相反的顺序打印：

```{code-cell} ocaml
let p x = print_int x; print_newline(); x + 1

let lst = map p [1; 2]
```

原因如下：

- 表达式 `map p [1; 2]` 的计算结果为 `p 1 :: map p [2]`。
- 然后对该表达式的右侧求值，得到
`p 1 :: (p 2 :: map p [])`。`p` 对 `1` 的应用尚未
  发生。
- 接下来再次求值 `::` 的右侧，产生
  `p 1 :: (p 2 :: [])`.
- 然后 `p` 应用于 `2`，最后应用于 `1`。

对于那些倾向于认为这一点的人来说，这可能会感到惊讶
求值会从左到右进行。解决方案是使用 `let`
表达式，确保函数应用的求值发生在
在递归调用之前：

```{code-cell} ocaml
let rec map f = function
  | [] -> []
  | h :: t -> let h' = f h in h' :: map f t

let lst2 = map p [1; 2]
```

这就是为什么它有效：

- 表达式 `map p [1; 2]` 的计算结果为 `let h' = p 1 in h' :: map p [2]`。
- 求值绑定表达式 `p 1`，导致打印 `1`
和 `h'` 绑定到 `2`。
- 然后对主体表达式 `h' :: map p [2]` 进行求值，其中
导致接下来打印 `2` 。

这就是标准库定义 `List.map` 的方式。我们应该用它来代替
从现在开始我们自己重新定义该函数。但很高兴我们有
可以说是“从头开始”发现了这个函数，如果需要的话我们可以
快速重新编码。

从这次讨论中得到的更大的教训是，当求值
顺序很重要，我们需要使用 `let` 来确保它。什么时候重要？仅当
有副作用。到目前为止，我们已经看到了打印和异常两种情况。
稍后我们将添加可变性。

## `map` 和尾递归

精明的读者会注意到 `map` 的实现不是 tail
递归的。这在某种程度上是不可避免的。下面是一种诱人但糟糕的
尾递归版本写法：

```{code-cell} ocaml
let rec map_tr_aux f acc = function
  | [] -> acc
  | h :: t -> map_tr_aux f (acc @ [f h]) t

let map_tr f = map_tr_aux f []

let lst = map_tr (fun x -> x + 1) [1; 2; 3]
```

在某种程度上是有效的：输出是正确的，并且 `map_tr_aux` 是尾部
递归的。微妙的问题在于子表达式 `acc @ [f h]`。回想一下
追加是单链表上的线性时间操作。也就是说，如果有
$n$ 列出元素然后追加需要时间 $O(n)$。所以在每次递归调用时我们
执行 $O(n)$ 操作。并且将会有 $n$ 递归调用，每个递归调用一个
列表的元素。总共需要 $n \cdot O(n)$ 工作，即 $O(n^2)$。
所以我们实现了尾递归，但代价很高：应该是
线性时间操作变成了二次时间。

为了解决这个问题，我们可以使用常量时间 cons 操作
线性时间追加操作：

```{code-cell} ocaml
let rec map_tr_aux f acc = function
  | [] -> acc
  | h :: t -> map_tr_aux f (f h :: acc) t

let map_tr f = map_tr_aux f []

let lst = map_tr (fun x -> x + 1) [1; 2; 3]
```

在某种程度上，这是有效的：它是尾递归和线性时间。
这次更明显的问题是输出顺序反了。每次我们取出输入列表前面的元素，
都会把它放到输出列表的前面，于是元素顺序被颠倒了。

```{note}
要理解为什么会发生逆转，可能有助于思考输入和
输出列表为排队的人：

- 输入：爱丽丝、鲍勃。
- 输出：空。

然后我们从输入中删除 Alice 并将她添加到输出中：

- 输入：鲍勃.
- 输出：爱丽丝。

然后我们从输入中删除 Bob 并将他添加到输出中：

- 输入：空。
- 输出：鲍勃，爱丽丝。

重点是，对于单链表，我们只能对表头进行操作
列表仍然是常数时间。我们不能将 Bob 移到输出的后面
不要让他走过爱丽丝&mdash;和任何其他可能站着的人
在输出中。
```

因此，标准库将此函数称为 `List.rev_map`，即
是一个（尾递归）映射函数，以相反的顺序返回其输出。

```{code-cell} ocaml
let rec rev_map_aux f acc = function
  | [] -> acc
  | h :: t -> rev_map_aux f (f h :: acc) t

let rev_map f = rev_map_aux f []

let lst = rev_map (fun x -> x + 1) [1; 2; 3]
```

如果你希望以“正确”的顺序输出，那很简单：只需应用 `List.rev`
对它：

```{code-cell} ocaml
let lst = List.rev (List.rev_map (fun x -> x + 1) [1; 2; 3])
```

由于 `List.rev` 既是线性时间又是尾递归，因此会产生完整的
解决方案。我们得到了线性时间和尾递归的映射计算。费用
是它需要两次遍历列表：一次进行转换，另一次进行转换
反向。我们不会比单链接的效率做得更好
列表。当然，还有其他实现列表的数据结构，我们将
最终还是会谈到这些。同时，请记住，我们通常不必
担心尾递归（也就是说，堆栈空间），直到列表有
10,000 个或更多元素。

为什么标准库不提供这个一体化的函数呢？也许会
有一天，如果有足够的理由。但你可能会发现自己
编程没有太多需要。在很多情况下，我们可以这样做
没有尾递归，或者满足于反向列表。

从这次讨论中得到的更大的教训是，可以有一个
递归函数的时间和空间效率之间的权衡。由
试图使函数更加节省空间（即尾递归），我们
可能会意外地使其渐近地降低时间效率（即二次
而不是线性的），或者如果我们聪明的话可以保持渐近时间效率
相同（即线性），但代价是恒定因子（即处理两次）。

## 其他语言中的 Map

上面我们提到，map 的概念存在于很多编程语言中。
下面是一个来自 Python 的示例：
```python
>>> print(list(map(lambda x: x + 1, [1, 2, 3])))
[2, 3, 4]
```
我们必须使用 `list` 函数将 `map` 的结果转换回
列表，因为 Python 为了提高效率而生成 `map` 的每个元素
根据需要输出。这里我们再次看到“什么时候评估？”的主题。
返回。

在 Java 中，map 是 Java 8 中添加的 `Stream` 抽象的一部分。
没有用于列表或流的内置 Java 语法，它有点多
冗长地举个例子。这里我们使用一个工厂方法`Stream.of`来创建一个
流：
```java
jshell> Stream.of(1, 2, 3).map(x -> x + 1).collect(Collectors.toList())
$1 ==> [2, 3, 4]
```
就像在 Python 示例中一样，我们必须使用一些东西将流转换回来
到一个列表中。在本例中，它是 `collect` 方法。
