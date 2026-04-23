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

# 记忆化

在上一节中，我们看到 `Lazy` 模块会记住计算结果，
这样就不必浪费时间重新计算它们。记忆化是一种强大的技术：
它能在不改变算法工作方式的情况下，渐近地加速简单递归算法。

让我们看看如何应用抽象原则，发明一种记忆化*任意*函数的方法，
使该函数在任意给定输入上只计算一次。
我们最终将使用命令式数据结构（数组和哈希表）作为一部分
我们的解决方案。

## 斐波那契

让我们再次考虑计算第 n 个斐波那契数的问题。
简单的递归实现需要指数时间，因为
一遍又一遍地重新计算相同的斐波那契数：

```{code-cell} ocaml
let rec fib n = if n < 2 then 1 else fib (n - 1) + fib (n - 2)
```

```{note}
准确地说，它的运行时间是$O(\phi^n)$，其中$\phi$是
黄金比例，$\frac{1 + \sqrt{5}}{2}$。
```

如果我们在计算斐波那契数时记录它们，我们就可以避免这种冗余
工作。这个想法是，每当我们计算 `f n` 时，我们都会将其存储在索引表中
由 `n` 提供。在这种情况下，索引键是整数，所以我们可以实现这个
使用数组的表：

```{code-cell} ocaml
let fibm n =
  let memo : int option array = Array.make (n + 1) None in
  let rec f_mem n =
    match memo.(n) with
    | Some result -> (* computed already *) result
    | None ->
        let result =
          if n < 2 then 1 else f_mem (n - 1) + f_mem (n - 2)
        in
        (* record in table *)
        memo.(n) <- Some result;
        result
  in
  f_mem n
```

`fibm` 内部定义的函数 `f_mem` 包含原始递归
算法，除了在进行计算之前它首先检查结果是否
已经被计算并存储在表中；如果是，它就只是
返回结果。

我们如何分析这个函数的运行时间呢？单次花费的时间
如果我们排除任何递归调用所花费的时间，则对 `f_mem` 的调用是 $O(1)$
它碰巧进行的递归调用。现在我们寻找一种方法来限制总数
通过查找正在取得的进展的某种度量来进行递归调用。

进度衡量的一个很好的选择，不仅在这里而且对于许多用途
记忆化问题，是表中非空条目的数量（即，
包含 `Some n` 而不是 `None`）。每次 `f_mem` 使两者递归
调用它还会将非空条目的数量增加一（填充
表中以前的空条目填入新值）。由于表中只有
`n` 条目，因此总共只能有 $O(n)$ 次对 `f_mem` 的调用，对于
$O(n)$ 的总运行时间（因为我们上面确定每个调用需要
$O(1)$ 时间）。记忆带来的加速因此减少了运行时间
从指数时间降低到线性时间，这是巨大的变化。例如，对于 $n=4$，
记忆化带来的加速超过一百万倍！

能够应用记忆化的关键是存在常见的子问题
正在反复解决。因此我们可以使用一些额外的存储空间
节省重复计算。

尽管此代码使用命令式构造（具体来说，数组更新），
副作用在函数 `fibm` 之外不可见。所以从客户端的角度来看，`fibm` 是函数式的。
我们不需要提及内部使用的命令式实现（也就是良性副作用）。

## 使用高阶函数进行记忆化

现在我们已经看到了记忆一个函数的示例，让我们使用高阶函数
函数来记忆任何函数。首先，考虑记住一个的情况
非递归函数 `f`。在这种情况下，我们只需要创建一个哈希表
存储调用 `f` 的每个参数的相应值
（为了记住多参数函数，我们可以使用柯里化和非柯里化来
转换为单个参数函数）。

```{code-cell} ocaml
let memo f =
  let h = Hashtbl.create 11 in
  fun x ->
    try Hashtbl.find h x
    with Not_found ->
      let y = f x in
      Hashtbl.add h x y;
      y
```

然而，对于递归函数，递归调用结构需要是
已修改。这可以独立于正在执行的函数而被抽象出来
已记忆：

```{code-cell} ocaml
let memo_rec f =
  let h = Hashtbl.create 16 in
  let rec g x =
    try Hashtbl.find h x
    with Not_found ->
      let y = f g x in
      Hashtbl.add h x y;
      y
  in
  g
```

现在我们可以使用这个通用函数稍微重写上面的原始 `fib` 函数
记忆技术：

```{code-cell} ocaml
let fib_memo =
  let fib self n =
    if n < 2 then 1 else self (n - 1) + self (n - 2)
  in
  memo_rec fib
```

## 只是为了好玩：派对优化

假设我们想为一家组织结构图为二叉树的公司举办一场聚会。
每个员工都有一个相关的“有趣的价值”，我们想要一组受邀的员工
员工拥有最大的总乐趣价值。然而，如果他的员工
上级是被邀请的，所以我们从不邀请两个有联系的员工
组织结构图。 （这个问题不太有趣的名字是最大权重独立
设置在树中。）对于具有 $n$ 员工的组织结构图，可能有 $2^{n}$ 
邀请列表，所以比较每个有效的乐趣的幼稚算法 
邀请列表需要指数时间。

我们可以使用记忆将其转化为线性时间算法。我们从
定义一个变体类型来代表员工。每个节点的 `int` 是
乐趣。

```ocaml
type tree = Empty | Node of int * tree * tree
```

现在，我们如何递归地解决这个问题？一个重要的观察结果是，在任何
树中，不包含根节点的最优邀请列表为
左子树和右子树的最佳邀请列表的并集。还有
包含根节点的最优邀请列表将是
左右孩子的最佳邀请列表不包括
它们各自的根节点。所以拥有优化函数似乎很有用
需要邀请根节点的情况的邀请列表，以及
对于排除根节点的情况。我们将调用这两个函数
`party_in` 和 `party_out`。那么party的结果就是最大的
这两个函数：

```{code-cell} ocaml
module Unmemoized = struct
  type tree =
    | Empty
    | Node of int * tree * tree

  (* Returns optimum fun for t. *)
  let rec party t = max (party_in t) (party_out t)

  (* Returns optimum fun for t assuming the root node of t
   * is included. *)
  and party_in t =
    match t with
    | Empty -> 0
    | Node (v, left, right) -> v + party_out left + party_out right

  (* Returns optimum fun for t assuming the root node of t
   * is excluded. *)
  and party_out t =
    match t with
    | Empty -> 0
    | Node (v, left, right) -> party left + party right
end
```

该代码的运行时间呈指数级增长。但请注意，只有 $n$
可能有不同的派对召唤。如果我们更改代码来记住结果
在这些调用中，性能在 $n$ 中呈线性。这是一个版本
记住聚会的结果并计算实际的邀请列表。
请注意，此代码直接在树中记忆结果。

```{code-cell} ocaml
module Memoized = struct
  (* This version memoizes the optimal fun value for each tree node. It
     also remembers the best invite list. Each tree node has the name of
     the employee as a string. *)
  type tree =
    | Empty
    | Node of
        int * string * tree * tree * (int * string list) option ref

  let rec party t : int * string list =
    match t with
    | Empty -> (0, [])
    | Node (_, name, left, right, memo) -> (
        match !memo with
        | Some result -> result
        | None ->
            let infun, innames = party_in t in
            let outfun, outnames = party_out t in
            let result =
              if infun > outfun then (infun, innames)
              else (outfun, outnames)
            in
            memo := Some result;
            result)

  and party_in t =
    match t with
    | Empty -> (0, [])
    | Node (v, name, l, r, _) ->
        let lfun, lnames = party_out l and rfun, rnames = party_out r in
        (v + lfun + rfun, name :: lnames @ rnames)

  and party_out t =
    match t with
    | Empty -> (0, [])
    | Node (_, _, l, r, _) ->
        let lfun, lnames = party l and rfun, rnames = party r in
        (lfun + rfun, lnames @ rnames)
end
```

为什么记忆化对解决这个问题如此有效？和斐波那契算法一样，
这里也有重叠子问题这一性质：朴素递归实现会多次用相同参数调用同一个函数。
记忆化函数可以保存所有这些调用的结果。进一步说，派对优化问题还具有最优子结构：
问题的最优答案可以由子问题的最优答案计算得到。并不是所有优化问题都有这种性质。
使用记忆化有效解决优化问题的关键，是弄清楚如何编写一个递归函数，
既实现该算法，又具有这两个性质。有时这需要仔细思考。

<!--
*****
MRC 7/22/21：下面的部分需要更多解释。还有价值
`big` 在原始注释中未定义，因此代码无法编译。
我添加了 `target + 1` 的定义，但不知道这是否“足够大”。
*****

## 最优换行

这是一个更复杂的例子。假设我们有一些想要的文本
格式为特定列宽内的段落。例如，我们可能有
如果我们正在编写一个网络浏览器来执行此操作。为简单起见，我们假设
所有字符都具有相同的宽度。文本的格式包括
选择某些单词对在其之间放置换行符。例如，当
应用于本段中的单词列表，宽度为 60，我们想要输出
像下面这样：

```ocaml
let it =
  ["Here is a more involved example of memoization. Suppose that",
   "we have some text that we want to format as a paragraph",
   ...
   "applied to the list of words in this paragraph, with width",
   "60, we want output like the following:"] : string list
```

良好的格式会占用每一列的大部分内容，并且也使每一行都相似
宽度。贪婪的方法是尽可能填充每一行，
但这可能会导致线条长度差异很大。例如，如果我们
将字符串“这可能是一个困难的例子”格式化为 13 个字符的宽度，
我们得到了可以改进的格式：

```text
this may be a
difficult
example
```

请注意，最佳分割是：
```text
this may be
a difficult
example
```

TeX 格式化程序可以很好地保持线宽相似
找到使剩余空间的立方总和最小化的格式
每行（最后一行除外）。然而，对于 $n$ 字，有
$\Omega(2^n)$ 可能的格式，因此算法不可能检查它们
全部用于大文本输入。值得注意的是，我们可以使用记忆法来找到
高效地优化格式化。事实上，记忆化对许多优化问题都很有用。
优化问题。

我们首先编写一个简单的递归算法来遍历列表并尝试
在每个单词后插入换行符，或不插入换行符：

```{code-cell} ocaml
(** Result of formatting a string. A result [(lst, n)] means a string
    was formatted into the lines in [lst], with a total sum-of-cubes
    cost of [n]. Invariant: the list is never empty. *)
type break_result = string list * int

(** Result: format the words in [words] into a list of lines optimally,
    minimizing the sum of the cubes of differences between the line
    lengths and [target]. Performance: worst-case time is exponential in
    the number of words. *)
let linebreak1 (words : string list) (target : int) : string list =
  let rec lb (clen : int) (words : string list) : break_result =
    match words with
    | [] -> ([ "" ], 0) (* no charge for last line *)
    | word :: rest ->
        (* Try two ways of doing it: (1) insert a linebreak right after
           current word, or (2) continue the current line. Pick the
           better one. *)
        let wlen = String.length word in
        let contlen = if clen = 0 then wlen else clen + 1 + wlen in
        let l1, c1' = lb 0 rest in
        let cube x = x * x * x in
        let c1 = c1' + cube (target - contlen) in
        if contlen <= target then
          match lb contlen rest with
          | [], _ -> failwith "invariant violated"
          | h2 :: t2, c2 ->
              if c1 < c2 then (word :: l1, c1)
              else
                ((if h2 = "" then word else word ^ " " ^ h2) :: t2, c2)
        else
          let big = target + 1 in
          (word :: l1, big)
  in
  let result, cost = lb 0 words in
  result
```

该算法是指数算法，因为它计算所有可能的格式。它
因此速度太慢而不实用。

关键的观察结果是，在文本段落的最佳格式中，
超过任何给定点的文本格式是最佳格式
只是该文本，因为它的第一个字符从列位置开始
先前格式化文本结束的位置。因此，格式化问题具有最优
以这种方式铸造时的下部结构。

因此，如果我们计算特定换行位置之后的最佳格式，
该格式对于所有可能的文本格式之前的格式是最好的
打破。

我们可以通过记住最佳格式来使 `linebreak` 花费线性时间
调用在 `clen = 0` 处。 （我们可以记住所有调用，但这不会
大大提高速度。）这只需要引入一个函数 `lb_mem` 即可
查找并记录记忆的格式化结果：

```ocaml
(** Result of formatting a string. A result [(lst, n)] means a string
    was formatted into the lines in [lst], with a total sum-of-cubes
    cost of [n]. Invariant: the list is never empty. *)
type break_result = string list * int

(* Same spec as linebreak1. Performance: worst-case time is linear in
   the number of words. *)
let linebreak2 (words : string list) (target : int) : string list =
  let memo : break_result option array =
    Array.make (List.length words + 1) None
  in
  let rec lb_mem (words : string list) : break_result =
    let n = List.length words in
    match Array.get memo n with
    | Some br -> br
    | None ->
        let br = lb 0 words in
        Array.set memo n (Some br);
        br
  and lb (clen : int) (words : string list) : break_result =
    match words with
    | [] -> ([ "" ], 0) (* no charge for last line *)
    | word :: rest -> (
        let wlen = String.length word in
        let contlen = if clen = 0 then wlen else clen + 1 + wlen in
        let l1, c1' = lb_mem rest in
        let c1 = c1' + cube (target - contlen) in
        if contlen > target then
          let big = target + 1 in
          (word :: l1, big)
        else
          match lb contlen rest with
          | [], _ -> failwith "invariant violated"
          | h2 :: t2, c2 ->
              if c1 < c2 then (word :: l1, c1)
              else
                ((if h2 = "" then word else word ^ " " ^ h2) :: t2, c2))
  in
  let result, cost = lb 0 words in
  result
```
-->
