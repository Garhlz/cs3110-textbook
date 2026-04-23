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

# 流水线

假设我们想要计算从 0 到 $n$ 的数字的平方和。
我们可以怎样做呢？当然（数学是优化的最佳形式），
最有效的方法是封闭式公式：

$$
\frac{n (n+1) (2n+1)}{6}
$$

但假设你忘记了该公式。用命令式语言，你
可能会使用 `for` 循环：

```python
# Python
def sum_sq(n):
	sum = 0
	for i in range(0, n+1):
		sum += i * i
	return sum
```

OCaml 中的等效（尾）递归代码为：
```{code-cell} ocaml
let sum_sq n =
  let rec loop i sum =
    if i > n then sum
    else loop (i + 1) (sum + i * i)
  in loop 0 0
```

在 OCaml 中产生相同结果的另一种更清晰的方法是使用高阶
函数和管道运算符：
```{code-cell} ocaml
let rec ( -- ) i j = if i > j then [] else i :: i + 1 -- j
let square x = x * x
let sum = List.fold_left ( + ) 0

let sum_sq n =
  0 -- n              (* [0;1;2;...;n]   *)
  |> List.map square  (* [0;1;4;...;n*n] *)
  |> sum              (*  0+1+4+...+n*n  *)
```
函数 `sum_sq` 首先构造一个包含所有数字 `0..n` 的列表。
然后它使用管道运算符 `|>` 传递该列表
`List.map square`，对每个元素进行平方。那么结果列表就是
通过 `sum` 进行管道传输，将所有元素添加在一起。

你可能会考虑的其他替代方案有些丑陋：
```{code-cell} ocaml
(* Maybe worse: a lot of extra [let..in] syntax and unnecessary names
   for intermediate values we don't care about. *)
let sum_sq n =
  let l = 0 -- n in
  let sq_l = List.map square l in
  sum sq_l

(* Maybe worse: have to read the function applications from right to left
   rather than top to bottom, and extra parentheses. *)
let sum_sq n =
  sum (List.map square (0--n))
```

与原始尾递归版本相比，所有这些的缺点是
他们浪费空间&mdash;线性而不是常数&mdash;并采取
一个常数因子更多的时间。正如编程中经常出现的情况一样，
代码清晰度和效率之间的权衡。

请注意，低效率*不是*来自管道操作符本身，而是来自
必须构建所有那些不必要的中间列表。所以不要得到
认为管道本质上是不好的。事实上，它非常有用。当
我们进入了关于模块的章节，我们将经常使用它来处理一些数据
我们在那里研究的结构。
