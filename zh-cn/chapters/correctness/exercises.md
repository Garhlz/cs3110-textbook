# 练习

{{ solutions }}

<!--------------------------------------------------------------------------->
{{ ex3 | replace("%%NAME%%", "spec game")}}

与另一位程序员配对并与他们一起玩规范游戏。采取
变成了指定者和狡猾的程序员。这里有一些建议
你可以使用的函数：

 - `num_vowels : string -> int`
 - `is_sorted : 'a list -> bool`
 - `sort : 'a list -> 'a list`
 - `max : 'a list -> 'a`
 - `is_prime : int -> bool`
 - `is_palindrome : string -> bool`
 - `second_largest : int list -> int`
 - `depth : 'a tree -> int`

<!--------------------------------------------------------------------------->
{{ ex3 | replace("%%NAME%%", "poly spec")}}

让我们为单变量整数多项式创建一个数据抽象
形式

$$
c_n x^n + \dotsb + c_1 x + c_0 .
$$

让我们假设多项式是*稠密的*，这意味着它们包含非常多的
少数系数为零。这是一个不完整的多项式接口：

```ocaml
(** [Poly] represents immutable polynomials with integer coefficients. *)
module type Poly = sig
  (** [t] is the type of polynomials. *)
  type t

  (** [eval x p] is [p] evaluated at [x]. Example: if [p] represents
      $3x^3 + x^2 + x$, then [eval 10 p] is [3110]. *)
  val eval : int -> t -> int
end
```

通过向接口添加更多操作来完成 `Poly` 的设计。考虑
哪些操作对抽象的客户端有用：

* 他们将如何创建多项式？
* 他们如何组合多项式来得到新的多项式？
* 他们如何查询多项式来找出什么
它代表？

为你发明的操作编写规范注释。请记住
当你编写规范游戏时：狡猾的程序员是否会颠覆你的
意图？

<!--------------------------------------------------------------------------->
{{ ex3 | replace("%%NAME%%", "poly impl")}}

实施你的 `Poly` 规范。作为实施的一部分，你将
需要选择表示类型 `t`。 *提示：回想一下我们的多项式
密集可能会指导你选择一种表示类型
更容易实施。*

<!--------------------------------------------------------------------------->
{{ ex4 | replace("%%NAME%%", "interval arithmetic")}}

指定并实现 [interval arithmetic][int-arith] 的数据抽象。
确保包含抽象函数、表示不变式和
`rep_ok`。还实现一个 `to_string` 函数和一个 `format` ，可以
使用 `#install_printer` 安装在顶层。

[int-arith]: http://web.mit.edu/hyperbook/Patrikalakis-Maekawa-Cho/node45.html

<!--------------------------------------------------------------------------->
{{ ex4 | replace("%%NAME%%", "function maps")}}

实现具有抽象类型 `('k, 'v) t` 的映射（又名字典）数据结构。
使用 `'k -> 'v` 作为表示类型。也就是说，映射被表示为
OCaml 函数从键到值。记录 AF。你不需要 RI。你的
解决方案将大量使用高阶函数。至少提供这些
值和操作：`empty`、`mem`、`find`、`add`、`remove`。

<!--------------------------------------------------------------------------->
{{ ex3 | replace("%%NAME%%", "set black box")}}

回到上一章中带有列表的集合的实现。
根据`Set`的规范注释，编写OUnit测试套件
对于 `ListSet` ，对其所有操作进行黑盒测试。

<!--------------------------------------------------------------------------->
{{ ex3 | replace("%%NAME%%", "set glass box")}}

使用 Bisect 尽可能实现接近 100% 的代码覆盖率 `ListSet`
和 `UniqListSet`。

<!--------------------------------------------------------------------------->
{{ ex3 | replace("%%NAME%%", "random lists")}}

使用`QCheck.Gen.generate1`生成一个长度在5到10之间的列表，
其元素是 0 到 100 之间的整数。然后使用
`QCheck.Gen.generate` 生成一个3元素列表，其中每个元素都是一个
你刚刚使用 `generate1` 创建的类型列表。

然后使用 `QCheck.make` 创建一个任意的表示一个列表，其
长度在5到10之间，元素是0到100之间的整数。
你的任意类型应该是 `int list QCheck.arbitrary`。

最后，创建并运行 QCheck 测试，检查是否至少有一个元素
任意列表（5 到 10 个元素，每个元素在 0 到 100 之间）的偶数。
你需要“升级” `is_even` 属性才能处理整数列表
而不是单个整数。

每次运行测试时，请记住它将生成 100 个列表并检查
他们的财产。如果你多次运行测试，你可能会看到一些
成功和一些失败。

<!--------------------------------------------------------------------------->
{{ ex3 | replace("%%NAME%%", "qcheck odd divisor")}}

这是一个有缺陷的函数：

```ocaml
(** [odd_divisor x] is an odd divisor of [x].
    Requires: [x >= 0]. *)
let odd_divisor x =
  if x < 3 then 1 else
    let rec search y =
      if y >= x then y  (* exceeded upper bound *)
      else if x mod y = 0 then y  (* found a divisor! *)
      else search (y + 2) (* skip evens *)
    in search 3
```

编写一个 QCheck 测试来确定该函数的输出（在
正整数，根据其前提条件； *提示：有一个任意的
生成正整数*) 既是奇数又是输入的除数。你
会发现函数有bug。最小的整数是多少
会触发该错误吗？

<!--------------------------------------------------------------------------->
{{ ex4 | replace("%%NAME%%", "qcheck avg")}}

这是一个有缺陷的函数：

```ocaml
(** [avg [x1; ...; xn]] is [(x1 + ... + xn) / n].
     Requires: the input list is not empty. *)
let avg lst =
  let rec loop (s, n) = function
    | [] -> (s, n)
    | [ h ] -> (s + h, n + 1)
    | h1 :: h2 :: t -> if h1 = h2 then loop (s + h1, n + 1) t
      else loop (s + h1 + h2, n + 2) t
  in
  let (s, n) = loop (0, 0) lst
  in float_of_int s /. float_of_int n
```
编写一个 QCheck 测试来检测错误。对于你检查的财产，
构建你自己的average&mdash;的*参考实现*，也就是说，
`avg` 的优化程度较低的版本显然是正确的。

<!--------------------------------------------------------------------------->
{{ ex2 | replace("%%NAME%%", "exp")}}

证明 `exp x (m + n) = exp x m * exp x n`，其中

```ocaml
let rec exp x n =
  if n = 0 then 1 else x * exp x (n - 1)
```

继续在 `m` 上进行归纳。

<!--------------------------------------------------------------------------->
{{ ex3 | replace("%%NAME%%", "fibi")}}

证明 `forall n >= 1, fib n = fibi n (0, 1)`，其中

```ocaml
let rec fib n =
  if n = 1 then 1
  else if n = 2 then 1
  else fib (n - 2) + fib (n - 1)

let rec fibi n (prev, curr) =
  if n = 1 then curr
  else fibi (n - 1) (curr, prev + curr)
```

对 `n` 进行归纳，而不是尝试应用有关的定理
将递归转换为迭代。

<!--------------------------------------------------------------------------->
{{ ex3 | replace("%%NAME%%", "expsq")}}

证明 `expsq x n = exp x n`，其中

```ocaml
let rec expsq x n =
  if n = 0 then 1
  else if n = 1 then x
  else (if n mod 2 = 0 then 1 else x) * expsq (x * x) (n / 2)
```

从 `n` 上的 *[strong induction][strong-ind]* 继续。函数 `expsq` 实现
*通过重复平方求幂*，从而提高效率
计算比 `exp` 。

[strong-ind]: https://en.wikipedia.org/wiki/Mathematical_induction#Complete_(strong)_induction

<!--------------------------------------------------------------------------->
{{ ex3 | replace("%%NAME%%", "expsq simplified")}}

重做前面的练习，但使用该函数的简化版本。
简化版本需要更少的代码，但需要额外的递归
打电话。

```ocaml
let rec expsq' x n =
  if n = 0 then 1
  else (if n mod 2 = 0 then 1 else x) * expsq' (x * x) (n / 2)
```

<!--------------------------------------------------------------------------->
{{ ex2 | replace("%%NAME%%", "mult")}}

通过 `n` 归纳证明 `forall n, mult n Z = Z`，其中：

```ocaml
let rec mult a b =
  match a with
  | Z -> Z
  | S k -> plus b (mult k b)
```

<!--------------------------------------------------------------------------->
{{ ex2 | replace("%%NAME%%", "append nil")}}

通过 `lst` 归纳证明 `forall lst, lst @ [] = lst`。

<!--------------------------------------------------------------------------->
{{ ex3 | replace("%%NAME%%", "rev dist append")}}

证明反向分布优于追加，即
`forall lst1 lst2, rev (lst1 @ lst2) = rev lst2 @ rev lst1`，其中：

```ocaml
let rec rev = function
  | [] -> []
  | h :: t -> rev t @ [h]
```

（当然，这是 `rev` 的低效实现。）你需要
选择要归纳的列表。你将需要之前的练习作为
引理，以及`append`的结合性，这在注释中得到了证明
上面。

<!--------------------------------------------------------------------------->
{{ ex3 | replace("%%NAME%%", "rev involutive")}}

证明逆向是对合，即
`forall lst, rev (rev lst) = lst`。继续在 `lst` 上进行感应。你将需要
前面的练习作为引理。

<!--------------------------------------------------------------------------->
{{ ex3 | replace("%%NAME%%", "reflect size")}}

通过 `t` 归纳证明 `forall t, size (reflect t) = size t`，其中：

```ocaml
let rec size = function
  | Leaf -> 0
  | Node (l, v, r) -> 1 + size l + size r

let rec reflect = function
  | Leaf -> Leaf
  | Node (l, v, r) -> Node (reflect r, v, reflect l)
```

<!--------------------------------------------------------------------------->
{{ ex4 | replace("%%NAME%%", "fold theorem 2")}}

我们证明了 `fold_left` 和 `fold_right` 会产生相同的结果，如果它们
函数参数具有结合性和交换性。但这并不能解释为什么
`concat` 的这两个实现产生相同的结果，因为 `( ^ )` 是
不可交换：

```ocaml
let concat_l lst = List.fold_left ( ^ ) "" lst
let concat_r lst = List.fold_right ( ^ ) lst ""
```

制定并证明关于 `fold_left` 和 `fold_right` 何时产生的新定理
相同的结果，在宽松的假设下，他们的函数参数是
结合但不一定可交换。 *提示：做出新的假设
累加器的初始值。*

<!--------------------------------------------------------------------------->
{{ ex4 | replace("%%NAME%%", "propositions")}}

在命题逻辑中，我们有原子命题、否定、合取、
析取和蕴涵。例如，`raining /\ snowing /\ cold` 是
命题指出同时下雨、下雪和寒冷（a
天气状况称为*Ithacaating*）。

定义 OCaml 类型来表示命题。然后说出归纳法
该类型的原则。

<!--------------------------------------------------------------------------->
{{ ex3 | replace("%%NAME%%", "list spec")}}

为具有 `nil`、`cons`、`append` 和 `append` 的列表设计一个 OCaml 接口
`length` 操作。设计等式规范。提示：方程
看起来与 `@` 和 `List.length` 的 OCaml 实现非常相似。

<!--------------------------------------------------------------------------->
{{ ex4 | replace("%%NAME%%", "bag spec")}}

*bag* 或 *multiset* 就像列表和集合的混合：像集合一样，顺序
没关系；与列表一样，元素可能会出现多次。数量
一个元素出现的次数就是它的*重数*。不存在于的元素
该包的多重性为 0。这是包的 OCaml 签名：

```ocaml
module type Bag = sig
  type 'a t
  val empty : 'a t
  val is_empty : 'a t -> bool
  val insert : 'a -> 'a t -> 'a t
  val mult : 'a -> 'a t -> int
  val remove : 'a -> 'a t -> 'a t
end
```

将 `Bag` 接口中的操作分类为生成器、操纵器或
查询。然后设计袋子的等式规格。对于 `remove`
操作，你的规范应该最多导致一个元素出现一次
被删除。也就是说，该值的重数应减少
大多数。
