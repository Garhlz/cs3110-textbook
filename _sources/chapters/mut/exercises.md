# 练习

{{ solutions }}

<!--------------------------------------------------------------------------->
{{ ex1 | replace("%%NAME%%", "mutable fields")}}

定义 OCaml 记录类型来表示学生姓名和 GPA。应该是
可能会改变学生的 GPA 值。写一个表达式定义a
学生姓名为`"Alice"`，GPA为`3.7`。然后写一个表达式来变异
Alice 的 GPA 为 `4.0`。

<!--------------------------------------------------------------------------->
{{ ex1 | replace("%%NAME%%", "refs")}}

给出具有以下类型的 OCaml 表达式。  使用utop检查
你的答案。

* `bool ref`
* `int list ref`
* `int ref list`

<!--------------------------------------------------------------------------->
{{ ex1 | replace("%%NAME%%", "inc fun")}}

定义对函数的引用如下：

```ocaml
let inc = ref (fun x -> x + 1)
```

编写使用 `inc` 生成值 `3110` 的代码。

<!--------------------------------------------------------------------------->
{{ ex2 | replace("%%NAME%%", "addition assignment")}}

C 语言和许多由它派生的语言，例如 Java，都有一个
*加法赋值*运算符写为`a += b`，含义为`a = a + b`。
在 OCaml 中实现这样一个运算符；它的类型应该是
`int ref -> int -> unit`。下面是一些可以帮助你入门的代码：

```ocaml
let ( +:= ) x y = ...
```

这是一个示例用法：

```ocaml
# let x = ref 0;;
# x +:= 3110;;
# !x;;
- : int = 3110
```

<!--------------------------------------------------------------------------->
{{ ex2 | replace("%%NAME%%", "physical equality")}}

定义 `x`、`y` 和 `z` 如下：
```ocaml
let x = ref 0
let y = x
let z = ref 0
```

预测以下一系列表达式的值：
```ocaml
# x == y;;
# x == z;;
# x = y;;
# x = z;;
# x := 1;;
# x = y;;
# x = z;;
```

在 utop 中检查你的答案。

<!--------------------------------------------------------------------------->
{{ ex2 | replace("%%NAME%%", "norm")}}

$n$ 维向量的 [Euclidean norm][norm]
$x = (x_1, \ldots, x_n)$ 写为 $|x|$ 并定义为

$$\sqrt{x_1^2 + \cdots + x_n^2}.$$

[norm]: https://en.wikipedia.org/wiki/Norm_(mathematics)#Euclidean_norm

编写一个函数 `norm : vector -> float` 来计算
向量的欧几里得范数，其中 `vector` 定义如下：

```
(* AF: the float array [| x1; ...; xn |] represents the
 *     vector (x1, ..., xn)
 * RI: the array is non-empty *)
type vector = float array
```

你的函数不应改变输入数组。 *提示：虽然你是第一次
本能可能是去循环，而不是尝试使用 `Array.map` 和
`Array.fold_left` 或 `Array.fold_right`.*

<!--------------------------------------------------------------------------->
{{ ex2 | replace("%%NAME%%", "normalize")}}

每个向量 $x$ 都可以通过将每个分量除以来*归一化*
$|x|$；这会产生一个范数为 1 的向量：

$$
\left(\frac{x_1}{|x|}, \ldots, \frac{x_n}{|x|}\right) .
$$

编写一个函数 `normalize : vector -> unit` 来规范化向量“
通过改变输入数组来放置”。这是一个示例用法：

```ocaml
# let a = [|1.; 1.|];;
val a : float array = [|1.; 1.|]

# normalize a;;
- : unit = ()

# a;;
- : float array = [|0.7071...; 0.7071...|]
```

*提示：`Array.iteri`.*

<!--------------------------------------------------------------------------->
{{ ex2 | replace("%%NAME%%", "norm loop")}}

修改 `norm` 的实现以使用循环。这是伪代码
你应该这样做：

```text
initialize norm to 0.0
loop through array
  add to norm the square of the current array component
return sqrt of norm
```

<!--------------------------------------------------------------------------->
{{ ex2 | replace("%%NAME%%", "normalize loop")}}

修改 `normalize` 的实现以使用循环。

<!--------------------------------------------------------------------------->
{{ ex3 | replace("%%NAME%%", "init matrix")}}

`Array` 模块包含两个用于创建数组的函数： `make` 和
`init`。 `make` 创建一个数组并用默认值填充它，而 `init`
创建一个数组并使用提供的函数来填充它。该库还
包含一个用于创建二维数组的函数 `make_matrix` ，但它
不包含类似的 `init_matrix` 使用函数创建矩阵
用于初始化。

编写一个函数 `init_matrix : int -> int -> (int -> int -> 'a) -> 'a array
array` such that `init_matrix n o f` creates and returns an `n` by `o` 矩阵
`m` 和 `m.(i).(j) = f i j` 对于边界内的所有 `i` 和 `j` 。

有关 [`make_matrix`](https://v2.ocaml.org/api/Array.html#VALmake_matrix) 的更多信息，请参阅文档
将矩阵表示为数组。

