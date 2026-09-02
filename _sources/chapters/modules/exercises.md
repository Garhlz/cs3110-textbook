# 练习

{{ solutions }}

<!--------------------------------------------------------------------------->
{{ ex1 | replace("%%NAME%%", "complex synonym")}}

这是复数的模块类型，具有实数和虚数
组件：

```ocaml
module type ComplexSig = sig
  val zero : float * float
  val add : float * float -> float * float -> float * float
end
```

通过添加 `type t = float * float` 改进该代码。显示签名如何
由于类型同义词，可以写得更简洁。

<!--------------------------------------------------------------------------->
{{ ex2 | replace("%%NAME%%", "complex encapsulation")}}

这是上一个练习中的模块类型的模块：

```ocaml
module Complex : ComplexSig = struct
  type t = float * float
  let zero = (0., 0.)
  let add (r1, i1) (r2, i2) = r1 +. r2, i1 +. i2
end
```

调查如果你进行以下更改（每个更改
独立），并解释为什么会出现错误：

- 从结构中删除 `zero`
- 从签名中删除 `add`
- 将结构体中的 `zero` 更改为 `let zero = 0, 0`

<!--------------------------------------------------------------------------->
{{ ex2 | replace("%%NAME%%", "big list queue")}}

使用以下代码创建长度呈指数增长的 `ListQueue`：
10、100、1000 等。在出现之前你可以创建多大的队列
明显的延迟？延迟至少 10 秒之前有多大？ （注：
你可以使用 Ctrl-C 中止 utop 计算。）

```ocaml
(** Creates a ListQueue filled with [n] elements. *)
let fill_listqueue n =
  let rec loop n q =
    if n = 0 then q
    else loop (n - 1) (ListQueue.enqueue n q) in
  loop n ListQueue.empty
```

<!--------------------------------------------------------------------------->
{{ ex2 | replace("%%NAME%%", "big batched queue")}}

使用以下函数创建指数增长的 `BatchedQueue`
长度：

```ocaml
let fill_batchedqueue n =
  let rec loop n q =
    if n = 0 then q
    else loop (n - 1) (BatchedQueue.enqueue n q) in
  loop n BatchedQueue.empty
```

现在，在延迟至少 10 之前，你可以创建多大的队列
秒？

<!--------------------------------------------------------------------------->
{{ ex3 | replace("%%NAME%%", "queue efficiency")}}

比较 `ListQueue` 和 `BatchedQueue` 中 `enqueue` 的实现。
用你自己的话解释为什么 `ListQueue.enqueue` 的效率是线性的
队列长度中的时间。 *提示：考虑 `@` 运算符。*然后解释
为什么将 $n$ 元素添加到队列中所花费的时间是 $n$ 的二次方。

现在考虑`BatchedQueue.enqueue`。假设队列处于以下状态
它从未有任何元素出列。用你自己的话解释为什么
`BatchedQueue.enqueue` 是常数时间。然后解释一下为什么要添加$n$元素
到队列所需的时间与 $n$ 呈线性关系。

<!--------------------------------------------------------------------------->
{{ ex4 | replace("%%NAME%%", "binary search tree map")}}

使用二进制文件编写一个模块 `BstMap` 来实现 `Map` 模块类型
搜索树类型。 *二叉树*之前我们讨论时已经介绍过
代数数据类型。二叉搜索树（BST）是遵循以下规则的二叉树：
以下*BST 不变量*：

> 对于任何节点 *n*，*n* 左子树中的每个节点的值都小于
> *n* 的值，并且 *n* 右子树中的每个节点的值都大于
> 大于 *n* 的值。

你的节点应该存储键和值对。钥匙应按以下顺序订购
BST 不变量。基于这个不变量，你总是知道是否要查看
在树中向左或向右查找特定键。

<!--------------------------------------------------------------------------->
{{ ex3 | replace("%%NAME%%", "fraction")}}

编写一个实现以下 `Fraction` 模块类型的模块：

```ocaml
module type Fraction = sig
  (* A fraction is a rational number p/q, where q != 0. *)
  type t

  (** [make n d] represents n/d, a fraction with 
      numerator [n] and denominator [d].
      Requires d <> 0. *)
  val make : int -> int -> t

  val numerator : t -> int
  val denominator : t -> int
  val to_string : t -> string
  val to_float : t -> float

  val add : t -> t -> t
  val mul : t -> t -> t
end
```

<!--------------------------------------------------------------------------->
{{ ex3 | replace("%%NAME%%", "fraction reduced")}}

修改 `Fraction` 的实现以确保这些不变量适用
从 `make`、`add` 和 `mul` 返回的每个 `t` 类型的值 `v`：

1. `v` 位于 *[reduced form][irreducible]* 中

2. `v` 的分母为正

对于第一个不变量，你可能会发现欧几里得的这个实现
算法有帮助：

```ocaml
(** [gcd x y] is the greatest common divisor of [x] and [y].
    Requires: [x] and [y] are positive. *)
let rec gcd x y =
  if x = 0 then y
  else if (x < y) then gcd (y - x) x
  else gcd y (x - y)
```

[irreducible]: https://en.wikipedia.org/wiki/Irreducible_fraction

<!--------------------------------------------------------------------------->
{{ ex1 | replace("%%NAME%%", "make char map")}}

要创建标准库中的映射，首先要使用函子 `Map.Make`，生成一个专门处理所需键类型的模块。在 utop 中输入：

```ocaml
# module CharMap = Map.Make(Char);;
```

输出表明名为 `CharMap` 的新模块已经定义，并给出了它的签名。在签名中找到 `empty`、`add` 和 `remove`，用自己的话解释它们的类型。

<!--------------------------------------------------------------------------->
{{ ex1 | replace("%%NAME%%", "char ordered")}}

函子 `Map.Make` 要求输入模块匹配 `Map.OrderedType` 签名。阅读[该签名][ord]和 [`Char` 模块的签名][char]，用自己的话解释为什么可以把 `Char` 作为参数传给 `Map.Make`。

[ord]: https://ocaml.org/api/Map.OrderedType.html
[char]: https://ocaml.org/api/Char.html

<!--------------------------------------------------------------------------->
{{ ex2 | replace("%%NAME%%", "use char map")}}

使用刚创建的 `CharMap`，构造一个包含以下绑定的映射：

* `'A'` 映射到 `"Alpha"`
* `'E'` 映射到 `"Echo"`
* `'S'` 映射到 `"Sierra"`
* `'V'` 映射到 `"Victor"`

使用 `CharMap.find` 查找 `'E'` 的绑定。

现在删除 `'A'` 的绑定。使用 `CharMap.mem` 来查找 `'A'` 是否为
仍然受到束缚。

使用函数 `CharMap.bindings` 将你的映射转换为关联
列表。

<!--------------------------------------------------------------------------->
{{ ex2 | replace("%%NAME%%", "bindings")}}

查阅 [`Map.S` 签名的文档][map.s]，找到
`bindings` 的规范。以下哪个表达式将返回相同的结果
协会名单？

1. `CharMap.(empty |> add 'x' 0 |> add 'y' 1 |> bindings)`

2. `CharMap.(empty |> add 'y' 1 |> add 'x' 0 |> bindings)`

3. `CharMap.(empty |> add 'x' 2 |> add 'y' 1 |> remove 'x' |> add 'x' 0 |> bindings)`

在 utop 中检查你的答案。

[map.s]: https://ocaml.org/api/Map.S.html


<!--------------------------------------------------------------------------->
{{ ex2 | replace("%%NAME%%", "date order")}}

这是日期类型：

```ocaml
type date = {month : int; day : int}
```

例如，3 月 31 日表示为 `{month = 3; day = 31}`。接下来几个练习的目标，是实现一个以 `date` 为键类型的映射。

显然，`date` 类型也能表示无效日期。例如，`{ month=6; day=50 }` 表示 6 月 50 日，而这一天[并不存在][parksandrec]。对于无效日期，下面练习中的代码行为不作规定。

[parksandrec]: http://nbcparksandrec.tumblr.com/post/46760908046/march-31st-is-a-day

要创建日期映射，需要向 `Map.Make` 传入一个匹配 `Map.OrderedType` 签名的模块。请创建这样的模块。下面的代码可以作为起点：

```ocaml
module Date = struct
  type t = date
  let compare ...
end
```

编写 `Date.compare` 时，请回顾 `Map.OrderedType` 中 [`compare` 的规范][ord]。

<!--------------------------------------------------------------------------->
{{ ex2 | replace("%%NAME%%", "calendar")}}

将 `Map.Make` 函子与 `Date` 模块一起使用来创建 `DateMap` 模块。
然后定义一个 `calendar` 类型，如下所示：

```ocaml
type calendar = string DateMap.t
```

`calendar` 的含义是把一个 `date` 映射到当天发生的事件名称。

使用 `DateMap` 模块中的函数，创建一个包含若干事件的日历，例如生日或纪念日。

<!--------------------------------------------------------------------------->
{{ ex2 | replace("%%NAME%%", "print calendar")}}

编写函数 `print_calendar : calendar -> unit`，以类似上一题示例的格式打印日历中的每个条目。
*提示：使用 [`Map.S` 签名][map.s]中记录的 `DateMap.iter`。*

<!--------------------------------------------------------------------------->
{{ ex3 | replace("%%NAME%%", "is for")}}

编写一个函数 `is_for : string CharMap.t -> string CharMap.t` ，给出一个
具有从 $k_1$ 到 $v_1$、...、$k_n$ 到 $v_n$ 的绑定的输入映射，会生成一个
具有相同键的输出映射，但每个键 $k_i$ 现在绑定到
字符串"$k_i$ 用于 $v_i$"。例如，如果 `m` 将 `'a'` 映射到 `"apple"`，则
`is_for m` 会将 `'a'` 映射到 `"a is for apple"`。 *提示：有一行
使用 `Map.S` 签名中的函数的解决方案。转换字符
对于字符串，你可以使用 `String.make`。一个更奇特的方法是使用
`Printf.sprintf`.*

<!--------------------------------------------------------------------------->
{{ ex3 | replace("%%NAME%%", "first after")}}

编写一个函数 `first_after : calendar -> Date.t -> string` 返回
严格在给定日期之后发生的第一个事件的名称。如果有
没有这样的事件，函数应该引发 `Not_found`，这是一个例外
已经在标准库中定义了。 *提示：你可以使用 `Map.S` 签名中的一两个函数在一行中完成此操作。*

<!--------------------------------------------------------------------------->
{{ ex3 | replace("%%NAME%%", "sets")}}

标准库 `Set` 模块与 `Map` 模块非常相似。使用它
创建一个表示*不区分大小写的字符串*集的模块。弦乐
仅在大小写不同的情况下，应将其视为相等。对于
例如，集合 {"grr", "argh"} 和 {"aRgh", "GRR"} 应被视为
相同，并且将"gRr"添加到任一组中不应更改该组。

<!--------------------------------------------------------------------------->
{{ ex2 | replace("%%NAME%%", "ToString")}}

编写一个模块类型 `ToString` ，指定具有抽象类型的签名
`t` 和函数 `to_string : t -> string`。

<!--------------------------------------------------------------------------->
{{ ex2 | replace("%%NAME%%", "Print")}}

编写一个函子 `Print` ，它将名为 `M` 类型的模块作为输入
`ToString`。你的函子返回的模块应该只有一个值
它是 `print`，它是一个函数，它采用 `M.t` 类型的值并打印
该值的字符串表示形式。

<!--------------------------------------------------------------------------->
{{ ex2 | replace("%%NAME%%", "Print Int")}}

创建一个名为 `PrintInt` 的模块，这是应用函子的结果
`Print` 到新模块 `Int`。你需要自己编写 `Int` 。类型
`Int.t` 应为 `int`。 *提示：不要密封 `Int`。*

在 utop 中尝试 `PrintInt`。用它来打印整数的值。

<!--------------------------------------------------------------------------->
{{ ex2 | replace("%%NAME%%", "Print String")}}

创建一个名为 `PrintString` 的模块，这是应用函子的结果
`Print` 到新模块 `MyString`。你需要自己编写 `MyString` 。
*提示：不要密封 `MyString`。*

在 utop 中尝试 `PrintString`。用它来打印字符串的值。

<!--------------------------------------------------------------------------->
{{ ex1 | replace("%%NAME%%", "Print Reuse")}}

用你自己的话解释 `Print` 是如何实现代码重用的，尽管这是一个非常
少量。

<!--------------------------------------------------------------------------->
{{ ex2 | replace("%%NAME%%", "Print String reuse revisited")}}

你上面创建的 `PrintString` 模块仅支持一种操作：`print`。
如果有一个支持所有 `String` 模块的模块那就太好了
除了 `print` 操作之外，还有其他函数，如果能够
无需复制任何代码即可派生此类模块。

定义一个模块 `StringWithPrint`。它应该具有内置的所有值
`String` 模块。它还应该具有 `print` 操作，该操作应该是
从 `Print` 函子派生而不是复制代码。 *提示：使用两个
`include` 语句。*

<!--------------------------------------------------------------------------->
{{ ex1 | replace("%%NAME%%", "implementation without interface")}}

创建一个名为 `date.ml` 的文件。  在其中放入以下代码：

```ocaml
type date = {month : int; day : int}
let make_date month day = {month; day}
let get_month d = d.month
let get_day d = d.day
let to_string d = (string_of_int d.month) ^ "/" ^ (string_of_int d.day)
```

再创建一个 Dune 文件：

```text
(library
 (name date))
```

将库加载到 utop 中：

```console
$ dune utop
```

在 utop 中，打开 `Date`，创建一个日期，访问其日期，并将其转换为字符串。

<!--------------------------------------------------------------------------->
{{ ex1 | replace("%%NAME%%", "implementation with interface")}}

完成前面的练习后，还创建一个名为 `date.mli` 的文件。在其中
输入以下代码：

```ocaml
type date = {month : int; day : int}
val make_date : int -> int -> date
val get_month : date -> int
val get_day : date -> int
val to_string : date -> string
```

然后在 utop 中重复刚才的操作。

<!--------------------------------------------------------------------------->
{{ ex1 | replace("%%NAME%%", "implementation with abstracted interface")}}

完成前两个练习后，编辑 `date.mli` 并更改第一个
其中声明如下：

```ocaml
type date
```

类型 `date` 现在是抽象的。再次在 utop 中重新做同样的工作。一些
反应将会改变。用你自己的话解释这些变化。

<!--------------------------------------------------------------------------->
{{ ex3 | replace("%%NAME%%", "printer for date")}}

向 `date.mli` 添加声明：

```ocaml
val format : Format.formatter -> date -> unit
```

并将 `format` 的定义添加到 `date.ml` 中。 *提示：使用 `Format.fprintf` 和
`Date.to_string`.*

现在重新编译，加载 utop，加载 `date.cmo` 后安装打印机
发出指令

```ocaml
#install_printer Date.format;;
```

正如你在上面的练习中所做的那样，将其他短语重新发出到 utop。
对一个短语的反应将会以一种有益的方式改变。解释一下为什么。

<!--------------------------------------------------------------------------->
{{ ex4 | replace("%%NAME%%", "refactor arith")}}

下载此文件：{{ code_link | replace("%%NAME%%", "algebra.ml")}}。它
包含这些签名和结构：

* `Ring` 是描述*[环（ring）][ring]*这一代数结构的签名，
这是加法和乘法运算符的抽象。

* `Field` 是描述*[域（field）][field]*这一代数结构的签名。域与环相似，但还抽象了除法运算。

* `IntRing` 和 `FloatRing` 分别以 `int` 和 `float` 实现环。

* `IntField` 和 `FloatField` 分别以 `int` 和 `float` 实现域。

* `IntRational` 和 `FloatRational` 用比值（也就是分数）实现域；前者以一对 `int` 表示分数，后者以一对 `float` 表示。

```{note}
致抽象代数爱好者：受机器算术所限，这些表示当然未必满足环与域的全部公理。此外，`IntField` 的除法运算在除数为零时没有良好定义。这里暂且不必深究。
```

[ring]: https://en.wikipedia.org/wiki/Ring_(mathematics)
[field]: https://en.wikipedia.org/wiki/Field_(mathematics)

重构代码以提高代码重用程度。请使用 `include` 和函子，并按需引入额外的结构与签名。本题不一定只有一种正确答案，下面给出一些建议：

* 任何名称都不应在多个签名中“直接声明”。例如，`Field` 不应再次直接声明 `( + )`，而应重用此前签名中的声明。“直接声明”指 `val name : ...` 形式的声明；由 `include` 带入的声明属于间接声明。

* 对代数运算与数值（加、减、乘、除、零和一），只需三组“直接定义”：分别用于 `int`、`float` 和比值。例如，不应把 `IntField.( + )` 直接定义为 `Stdlib.( + )`，而应从别处重用。“直接定义”指 `let name = ...` 形式的定义；由 `include` 或函子应用带入的定义属于间接定义。

* 有理结构都可以由单个函子产生，即
对 `IntRing` 应用一次，对 `FloatRing` 应用一次。

* 可以消除 `of_int` 的所有重复，这样它就是
直接定义一次，并且所有结构都重用该定义；和
  这样它就只能在一个签名中直接声明。这将需要
  函子的使用。它还需要发明一种可以转换的算法
  一个整数到任意 `Ring` 表示形式，无论什么
  `Ring` 的表示类型是。

完成后，所有模块的类型应保持不变。你可以
通过运行 `ocamlc -i algebra.ml` 可以轻松查看这些类型。
