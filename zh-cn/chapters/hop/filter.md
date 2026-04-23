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

# Filter

{{ video_embed | replace("%%VID%%", "FaWtD-LRdpU")}}

假设我们只想保留列表中的偶数或奇数。
以下是一些可以做到这一点的函数：

```{code-cell} ocaml
(** [even n] is whether [n] is even. *)
let even n =
  n mod 2 = 0

(** [evens lst] is the sublist of [lst] containing only even numbers. *)
let rec evens = function
  | [] -> []
  | h :: t -> if even h then h :: evens t else evens t

let lst1 = evens [1; 2; 3; 4]
```

```{code-cell} ocaml
(** [odd n] is whether [n] is odd. *)
let odd n =
  n mod 2 <> 0

(** [odds lst] is the sublist of [lst] containing only odd numbers. *)
let rec odds = function
  | [] -> []
  | h :: t -> if odd h then h :: odds t else odds t

let lst2 = odds [1; 2; 3; 4]
```

函数 `evens` 和 `odds` 几乎是相同的代码：唯一重要的
区别在于它们应用于 head 元素的测试。正如我们对 `map` 所做的那样
在上一节中，我们将该测试分解为函数。让我们命名
函数 `p`，作为“谓词”的缩写。谓词只是一个
测试某件事是真还是假的函数：

```{code-cell} ocaml
let rec filter p = function
  | [] -> []
  | h :: t -> if p h then h :: filter p t else filter p t
```

现在我们可以重新实现原来的两个函数：

```{code-cell} ocaml
let evens = filter even
let odds = filter odd
```

多么简单！多么清楚！（至少对于熟悉
`filter`。）

## `filter` 和尾递归

正如我们对 `map` 所做的那样，我们可以创建 `filter` 的尾递归版本：

```{code-cell} ocaml
let rec filter_aux p acc = function
  | [] -> acc
  | h :: t -> if p h then filter_aux p (h :: acc) t else filter_aux p acc t

let filter p = filter_aux p []

let lst = filter even [1; 2; 3; 4]
```

我们再次发现输出顺序反了。在这里，标准库做出了
与 `map` 不同的选择。它内置了反转操作：
`List.filter`，其实现如下：

```{code-cell} ocaml
let rec filter_aux p acc = function
  | [] -> List.rev acc (* note the built-in reversal *)
  | h :: t -> if p h then filter_aux p (h :: acc) t else filter_aux p acc t

let filter p = filter_aux p []
```

为什么标准库在这一点上对 `map` 和 `filter` 的处理方式不同？
这是个好问题。也许是因为并不需要让
`filter` 函数在常数因子上更高效。也许
这只是历史的偶然。

## 其他语言中的 Filter

同样，`filter` 的概念存在于许多编程语言中。这是在
Python：
```python
>>> print(list(filter(lambda x: x % 2 == 0, [1, 2, 3, 4])))
[2, 4]
```
在 Java 中：
```java
jshell> Stream.of(1, 2, 3, 4).filter(x -> x % 2 == 0).collect(Collectors.toList())
$1 ==> [2, 4]
```
