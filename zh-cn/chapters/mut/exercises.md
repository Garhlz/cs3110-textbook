# 练习

{{ solutions }}

<!--------------------------------------------------------------------------->
{{ ex1 | replace("%%NAME%%", "mutable fields")}}

定义一个 OCaml 记录类型，表示学生的姓名和 GPA，其中 GPA 应当可以修改。编写表达式，创建姓名为 `"Alice"`、GPA 为 `3.7` 的学生，然后把 Alice 的 GPA 修改为 `4.0`。

<!--------------------------------------------------------------------------->
{{ ex1 | replace("%%NAME%%", "refs")}}

分别给出具有以下类型的 OCaml 表达式，并使用 utop 检查答案。

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

C 及许多受它影响的语言（如 Java）都有*加法赋值*运算符：`a += b` 等价于 `a = a + b`。请在 OCaml 中实现这样的运算符，其类型应为 `int ref -> int -> unit`。下面的代码可作为起点：

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

$n$ 维向量 $x = (x_1, \ldots, x_n)$ 的[欧几里得范数][norm]记作 $|x|$，定义为

$$\sqrt{x_1^2 + \cdots + x_n^2}.$$

[norm]: https://en.wikipedia.org/wiki/Norm_(mathematics)#Euclidean_norm

编写函数 `norm : vector -> float`，计算向量的欧几里得范数，其中 `vector` 定义如下：

```
(* AF: the float array [| x1; ...; xn |] represents the
 *     vector (x1, ..., xn)
 * RI: the array is non-empty *)
type vector = float array
```

函数不得修改输入数组。*提示：先别急着使用循环，试试 `Array.map` 配合 `Array.fold_left` 或 `Array.fold_right`。*

<!--------------------------------------------------------------------------->
{{ ex2 | replace("%%NAME%%", "normalize")}}

每个向量 $x$ 都可以通过将每个分量除以来*归一化*
$|x|$；这会产生一个范数为 1 的向量：

$$
\left(\frac{x_1}{|x|}, \ldots, \frac{x_n}{|x|}\right) .
$$

编写函数 `normalize : vector -> unit`，通过修改输入数组对向量进行*原地*归一化。用法示例如下：

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

`Array` 模块提供了两个创建数组的函数：`make` 和 `init`。`make` 用同一个默认值填充数组，`init` 则用给定函数计算每个元素。该模块还提供创建二维数组的 `make_matrix`，却没有对应的 `init_matrix`，不能用初始化函数生成矩阵。

编写函数 `init_matrix : int -> int -> (int -> int -> 'a) -> 'a array array`，使 `init_matrix n o f` 创建并返回一个 $n \times o$ 的矩阵 `m`，且对所有范围内的 `i`、`j`，均有 `m.(i).(j) = f i j`。

有关 [`make_matrix`](https://v2.ocaml.org/api/Array.html#VALmake_matrix) 的更多信息，请参阅文档
将矩阵表示为数组。
