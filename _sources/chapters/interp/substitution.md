# 替换模型

在词法分析和解析之后，下一阶段是类型检查（以及其他语义
分析）。我们将暂时跳过该阶段，并在本节结束时返回该阶段
章。

相反，让我们把注意力转向求值。在编译器中，下一阶段
语义分析后会将 AST 重写为中间
表示（IR），准备将程序翻译成机器
代码。解释器也可能将 AST 重写为 IR，或者可能直接
开始评估 AST。重写 AST 的原因之一是简化它：
有时，某些语言特性可以根据其他语言特性来实现，并且
将语言缩减为一个小核心，以保持解释器实现较短，是有意义的。
语法糖就是这个想法的一个很好的例子。

消除语法糖称为*脱糖。*举个例子，我们知道
`let x = e1 in e2` 和 `(fun x -> e2) e1` 是等效的。所以，我们可以把
让表达式作为语法糖。

假设我们有一种语言，其 AST 对应于这个 BNF：

```text
e ::= x | fun x -> e | e1 e2
    | let x = e1 in e2
```

然后解释器可以将其脱糖为更简单的 AST&mdash;某种意义上也就是 IR&mdash;
方法是把所有出现的 `let x = e1 in e2` 转换为 `(fun x -> e2) e1`。
然后解释器
只需要评估这种较小的语言：

```text
e ::= x | fun x -> e | e1 e2
```

简化 AST 后，就该对其求值了。*求值*是
继续简化 AST 直到它只是一个值的过程。在其他方面
换句话说，求值是语言动态语义的实现。
回想一下，*值*是一个没有计算的表达式
尚待完成。通常，我们将值看作表达式的严格语法子集，
尽管稍后会看到一些例外。

**大步求值与小步求值。** 我们将用数学定义求值
关系，就像我们对类型检查所做的那样。实际上，我们要定义
三个求值关系：

* 第一个 `-->` 将表示程序如何执行单个步骤
执行。

* 第二个 `-->*` 是 `-->` 的自反传递闭包，它
表示程序如何执行多个步骤。

* 第三个，`==>`，抽象了单个步骤的所有细节，
表示程序如何直接减少到一个值。

我们用这些关系定义求值的风格被称为
*操作语义*，因为我们使用关系来指定如何
机器在求值程序时“运行”。还有另外两种主要风格，
称为*指称语义*和*公理语义*，但我们不会涵盖
那些在这里。

我们可以进一步将操作语义分为两个独立的子样式
定义求值：*小步*与*大步*语义。第一个关系，
`-->`，是小步风格，因为它代表执行
单个小步骤。第三个，`==>`，是大步风格，因为它
表示从表达式直接一步执行到值。第二个关系 `-->*` 将两者混合。
确实，我们的愿望就是这样
从以下意义上弥合差距：

**关联大步和小步：** 对于所有表达式 `e` 和值 `v`，它
认为 `e -->* v` 当且仅当 `e ==> v` 时。

换句话说，如果一个表达式采取许多小步骤并最终达到
值，例如 `e --> e1 --> .... --> en --> v`，那么情况应该是这样的
`e ==> v`。所以大步关系是小步的忠实抽象
关系：它只是忘记了所有中间步骤。

为什么有大、小两种不同风格？每种风格在某些情况下都更容易使用
在某些情况下，比另一个更重要，所以在我们的系统中同时拥有两者是有帮助的
工具包。小步语义往往更容易使用
来建模复杂的语言特征，但大步语义倾向于
更类似于解释器的实际实现方式。

**替换与环境模型。** 我们必须做出另一个选择，
它与小步与大步的选择正交。有两种不同的
考虑变量实现的方法：

* 我们可以急切地用变量的值“替换”它的名称，
一旦我们找到变量的绑定，就可以确定该名称的范围。

* 我们可以懒惰地将替换记录在字典中，通常是
用于此目的时称为*环境*，我们可以查找
  每当我们发现变量的名称在该环境中被提及时，变量的值
  范围。

这些想法导致了求值的“替换模型”和“环境模型”。
与小步和大步一样，替换模型
往往更适合数学处理，而环境模型
往往更类似于解释器的实现方式。

一些例子将有助于理解这一切。接下来让我们看看如何
定义 SimPL 的关系。

## 在替换模型中求值 SimPL

{{ video_embed | replace("%%VID%%", "J-DkHQ37kaM")}}

让我们首先为 SimPL 定义一个小步替换模型语义。
也就是说，我们将定义一个关系 `-->` 来表示如何
表达式一次执行一步，我们将使用以下方法实现变量
用值替换名称。

回想一下 SimPL 的语法：

```text
e ::= x | i | b | e1 bop e2
    | if e1 then e2 else e3
    | let x = e1 in e2

bop ::= + | * | <=
```

我们需要知道表达式何时完成评估，即何时
它们被认为是价值观。对于 SimPL，我们将定义值如下：

```text
v ::= i | b
```

也就是说，值可以是整数常量，也可以是布尔常量。

对于 SimPL 表达式可能具有的每种语法形式，我们现在将
定义一些*评估规则*，它们构成了
`-->` 关系。每条规则的形式为 `e --> e'`，这意味着 `e` 采用
一步到达 `e'`。

虽然 BNF 中首先给出了变量，但我们现在先忽略它们，并且
在所有其他形式之后再回到它们。

**常量。** 整数和布尔常量已经是值，因此它们不能
迈出一步。乍一看这可能令人惊讶，但请记住，我们是
还打算定义一个允许零个或多个步骤的 `-->*` 关系；
而 `-->` 关系代表“恰好”一步。

从技术上讲，我们要做的就是不编写任何规则来实现这一点
对于某些 `e`，其形式为 `i --> e` 或 `b --> e`。所以我们已经完成了
实际上：我们还没有定义任何规则。

让我们介绍另一种写法 `e -/->` ，它的意思是
一个带有斜杠的箭头，表示“不存在这样的 `e'`
那个`e --> e'`”。使用它我们可以写：

* `i -/->`
* `b -/->`

虽然严格来说不是 `-->` 定义的一部分，但这些命题
帮助我们记住常数不会阶跃。事实上，我们可以更一般地
写，“对于所有 `v`，它认为 `v -/->`。”

**二元运算符。** 二元运算符应用程序 `e1 bop e2` 有两个
子表达式 `e1` 和 `e2`。这导致了一些关于如何评估的选择
表达式：

* 我们可以首先评估左侧 `e1`，然后评估右侧
`e2`，然后应用运算符。

* 或者我们可以先做右侧，然后做左侧。

* 或者我们可以交错评估，首先执行 `e1` 步骤，然后执行
`e2`，然后`e1`，然后`e2`，等等。

* 或者该运算符可能是“短路”运算符，在这种情况下，其中之一
子表达式可能永远不会被计算。

你还可以发明许多其他策略。

事实证明 OCaml 语言定义是这样说的（对于非短路
运算符）未指定首先评估哪一侧。目前的
实现恰好首先评估右侧，但事实并非如此
任何程序员都应该依赖的东西。

许多人会期望从左到右的评估，所以让我们定义 `-->`
的关系。我们首先说左边可以迈出一步：

```text
e1 bop e2 --> e1' bop e2
  if e1 --> e1'
```

与 SimPL 的类型系统类似，该规则表示两个表达式是
如果另外两个（更简单的）子表达式也在 `-->` 关系中
`-->` 关系。这就是它成为归纳定义的原因。

如果左侧完成评估，则右侧可以开始
步进：

```text
v1 bop e2 --> v1 bop e2'
  if e2 --> e2'
```

最后当两边都达到一个值时，二元运算符
可以应用：

```text
v1 bop v2 --> v
  if v is the result of primitive operation v1 bop v2
```

通过“原始操作”，我们的意思是存在一些基本概念：
`bop` 实际上意味着。例如，字符 `+` 只是一段语法，
但我们习惯于将其理解为算术加法
操作。原始操作通常是由
硬件（例如 `ADD` 操作码），或通过运行时库（例如 `pow`
函数）。

对于 SimPL，我们将所有原始操作委托给 OCaml。也就是说，SimPL
`+` 运算符将与 OCaml `+` 运算符相同，`*` 和 `<=` 也是如此。

这是使用二元运算符规则的示例：

```text
    (3*1000) + ((1*100) + ((1*10) + 0))
--> 3000 + ((1*100) + ((1*10) + 0))
--> 3000 + (100 + ((1*10) + 0))
--> 3000 + (100 + (10 + 0))
--> 3000 + (100 + 10)
--> 3000 + 110
--> 3110
```

**If 表达式。** 与二元运算符一样，有多种选择
计算 if 表达式的子表达式。尽管如此，大多数程序员
期望首先评估守卫，然后只评估其中一个分支
进行评估，因为这就是大多数语言的工作方式。那我们来写评价吧
该语义的规则。

首先，守卫被评估为一个值：

```text
if e1 then e2 else e3 --> if e1' then e2 else e3
  if e1 --> e1'
```

然后，在guard的基础上，简化了if表达式
仅到其中一个分支：

```text
if true then e2 else e3 --> e2

if false then e2 else e3 --> e3
```

**Let 表达式。** 让 SimPL Let 表达式以相同的方式求值
如 OCaml let 表达式：首先是绑定表达式，然后是主体。

绑定表达式的步进规则是：

```text
let x = e1 in e2 --> let x = e1' in e2
  if e1 --> e1'
```

接下来，如果绑定表达式达到了一个值，我们要替换它
主体表达式中变量名称的值：

```text
let x = v1 in e2 --> e2 with v1 substituted for x
```

例如，`let x = 42 in x + 1` 应步进到 `42 + 1`，因为替换
`42` 对于 `x + 1` 中的 `x` 会产生 `42 + 1`。

当然，该规则的右侧并不是真正的表达式。这是
只是给出我们真正想要的表达的直觉。我们需要
正式定义“替代”的含义。事实证明这相当棘手。所以，
让我们假设一个新的表示法，而不是现在就被它转移注意力：
`e'{e/x}`，这意味着“表达式 `e'` 用 `e` 替换了 `x`。”
我们将在下一节中回到该符号并仔细研究它
定义。

现在，我们可以添加这条规则：

```text
let x = v1 in e2 --> e2{v1/x}
```

{{ video_embed | replace("%%VID%%", "c_11LeMoPtk")}}

**变量。** 注意 let 表达式规则如何从
出现在主体表达式中：变量的名称被值替换
该变量应该有。所以，我们永远不应该达到尝试的地步
步骤一个变量名&mdash;假设程序类型正确。

考虑 OCaml：如果我们尝试使用未绑定变量计算表达式，
会发生什么？让我们检查一下utop：

```text
# x;;
Error: Unbound value x

# let y = x in y;;
Error: Unbound value x
```

对于要包含的表达式，这是一个错误 &mdash;a 类型检查错误 &mdash;
一个未绑定的变量。因此，任何类型正确的表达式 `e` 将永远不会到达
尝试单步执行变量名称的点。

与常量一样，因此我们不需要为变量添加任何规则。但是，
为了清楚起见，我们可以声明 `x -/->`。

## 实现单步关系

很容易将 `-->` 的上述定义转换为 OCaml 函数：
与 AST 节点进行模式匹配。在下面的代码中，请记住我们没有
尚未完成定义替换（即 `subst`）；我们将回到这一点
下一节。

```ocaml
(** [is_value e] is whether [e] is a value. *)
let is_value : expr -> bool = function
  | Int _ | Bool _ -> true
  | Var _ | Let _ | Binop _ | If _ -> false

(** [subst e v x] is [e{v/x}]. *)
let subst _ _ _ =
  failwith "See next section"

(** [step] is the [-->] relation, that is, a single step of
    evaluation. *)
let rec step : expr -> expr = function
  | Int _ | Bool _ -> failwith "Does not step"
  | Var _ -> failwith "Unbound variable"
  | Binop (bop, e1, e2) when is_value e1 && is_value e2 ->
    step_bop bop e1 e2
  | Binop (bop, e1, e2) when is_value e1 ->
    Binop (bop, e1, step e2)
  | Binop (bop, e1, e2) -> Binop (bop, step e1, e2)
  | Let (x, e1, e2) when is_value e1 -> subst e2 e1 x
  | Let (x, e1, e2) -> Let (x, step e1, e2)
  | If (Bool true, e2, _) -> e2
  | If (Bool false, _, e3) -> e3
  | If (Int _, _, _) -> failwith "Guard of if must have type bool"
  | If (e1, e2, e3) -> If (step e1, e2, e3)

(** [step_bop bop v1 v2] implements the primitive operation
    [v1 bop v2].  Requires: [v1] and [v2] are both values. *)
and step_bop bop e1 e2 = match bop, e1, e2 with
  | Add, Int a, Int b -> Int (a + b)
  | Mult, Int a, Int b -> Int (a * b)
  | Leq, Int a, Int b -> Bool (a <= b)
  | _ -> failwith "Operator and operand type mismatch"
```

在该实现中我们必须处理的唯一新问题是两个地方
发现运行时类型错误的地方，即在评估
`If (Int _, _, _)` 在最后一行，我们发现一个二进制文件
运算符应用于错误类型的参数。类型检查将
保证这里永远不会引发异常，但 OCaml 的详尽性
尽管如此，模式匹配的分析还是迫使我们编写一个分支。而且，
如果事实证明我们的类型检查器中有一个错误导致
要评估类型错误的二元运算符应用程序，此异常将
帮助我们发现出了什么问题。

## 多步关系

现在我们已经定义了 `-->`，实际上没有什么需要做的来定义
`-->*`。这只是 `-->` 的自反传递闭包。换句话说，它
可以用这两个规则来定义：

```text
e -->* e

e -->* e''
  if e --> e' and e' -->* e''
```

当然，在实现解释器时，我们真正想要的是
尽可能多的步骤，直到表达式达到一个值。也就是说，我们是
对子关系 `e -->* v` 感兴趣，其中右侧是一个 not
只是一个表达式，而是一个值。这很容易实现：

```ocaml
(** [eval_small e] is the [e -->* v] relation.  That is,
    keep applying [step] until a value is produced.  *)
let rec eval_small (e : expr) : expr =
  if is_value e then e
  else e |> step |> eval_small
```

## 定义大步关系

{{ video_embed | replace("%%VID%%", "P456qGgeoYs")}}

回想一下，我们定义大步关系 `==>` 的目标是确保它
同意多步关系 `-->*`。

常量很容易，因为它们向自己迈出了一大步：

```text
i ==> i

b ==> b
```

二元运算符只是将它们的两个子表达式向前迈了一大步，
然后应用原始运算符：

```text
e1 bop e2 ==> v
  if e1 ==> v1
  and e2 ==> v2
  and v is the result of primitive operation v1 bop v2
```

如果表情大步守卫，那么大步第一步
分支机构：

```text
if e1 then e2 else e3 ==> v2
  if e1 ==> true
  and e2 ==> v2

if e1 then e2 else e3 ==> v3
  if e1 ==> false
  and e3 ==> v3
```

让表达式大步绑定表达式，进行替换，然后大步
替换的结果：

```text
let x = e1 in e2 ==> v2
  if e1 ==> v1
  and e2{v1/x} ==> v2
```

最后，变量不会大步，原因与小步相同
语义&mdash;一个类型良好的程序永远不会达到尝试的程度
评估变量名：

```text
x =/=>
```

## 实现大步关系

如果有的话，大步评估关系甚至比
小步关系。它只是在树上递归，评估
`==>` 定义所需的子表达式：

```ocaml
(** [eval_big e] is the [e ==> v] relation. *)
let rec eval_big (e : expr) : expr = match e with
  | Int _ | Bool _ -> e
  | Var _ -> failwith "Unbound variable"
  | Binop (bop, e1, e2) -> eval_bop bop e1 e2
  | Let (x, e1, e2) -> subst e2 (eval_big e1) x |> eval_big
  | If (e1, e2, e3) -> eval_if e1 e2 e3

(** [eval_bop bop e1 e2] is the [e] such that [e1 bop e2 ==> e]. *)
and eval_bop bop e1 e2 = match bop, eval_big e1, eval_big e2 with
  | Add, Int a, Int b -> Int (a + b)
  | Mult, Int a, Int b -> Int (a * b)
  | Leq, Int a, Int b -> Bool (a <= b)
  | _ -> failwith "Operator and operand type mismatch"

(** [eval_if e1 e2 e3] is the [e] such that [if e1 then e2 else e3 ==> e]. *)
and eval_if e1 e2 e3 = match eval_big e1 with
  | Bool true -> eval_big e2
  | Bool false -> eval_big e3
  | _ -> failwith "Guard of if must have type bool"
```

分解每个部分的函数是很好的工程实践
语法，就像我们上面所做的那样，除非实现只能在一行中完成
在 `eval_big` 内的主模式匹配中。

## SimPL 中的替换

在上一节中，我们提出了一个新的符号`e'{e/x}`，意思是
“表达式 `e'` 用 `e` 替换 `x`。”直觉是
`x` 出现在 `e'` 中的任何地方，我们都应该用 `e` 替换 `x` 。

让我们仔细定义 SimPL 的替代。大多数情况下，
这并不太难。

**常量** 中没有出现变量（例如， `x` 不能
语法上出现在 `42` 中），因此替换使它们保持不变：

```text
i{e/x} = i
b{e/x} = b
```

对于**二元运算符和 if 表达式**，所有替换都需要完成
是在子表达式内递归：

```text
(e1 bop e2){e/x} = e1{e/x} bop e2{e/x}
(if e1 then e2 else e3){e/x} = if e1{e/x} then e2{e/x} else e3{e/x}
```

**变量**开始变得有点棘手。有两种可能：
要么我们遇到变量 `x`，这意味着我们应该进行替换，
或者我们遇到一些具有不同名称的其他变量，例如 `y`，其中
在这种情况下我们不应该进行替换：

```text
x{e/x} = e
y{e/x} = y
```

其中第一个情况 `x{e/x} = e` 需要注意：它是
最终进行替换操作。例如，假设我们正在尝试
找出 `(x + 42){1/x}` 的结果。使用上面的定义，

```text
  (x + 42){1/x}
= x{1/x} + 42{1/x}   by the bop case
= 1 + 42{1/x}        by the first variable case
= 1 + 42             by the integer case
```

请注意，我们现在没有定义 `-->` 关系。也就是说，没有一个
这些等式代表了评估的一个步骤。为了具体化，假设
我们正在评估 `let x = 1 in x + 42`：

```text
    let x = 1 in x + 42
--> (x + 42){1/x}
  = 1 + 42
--> 43
```

这里有两个步骤，一个用于 `let`，另一个用于 `+`。但我们
考虑替换同时发生，作为 `let` 步骤的一部分
需要。这就是为什么我们写 `(x + 42){1/x} = 1 + 42`，而不是
`(x + 42){1/x} --> 1 + 42`。

最后，**let 表达式**也有两种情况，具体取决于表达式的名称
绑定变量：

```text
(let x = e1 in e2){e/x}  =  let x = e1{e/x} in e2
(let y = e1 in e2){e/x}  =  let y = e1{e/x} in e2{e/x}
```

这两种情况都用 `e` 替换绑定表达式 `e1` 中的 `x`。
这是为了确保像 `let x = 42 in let y = x in y` 这样的表达式
正确评估：`x` 需要位于绑定 `y = x` 内的范围内，因此我们
无论绑定的名称如何，都必须在那里进行替换。

但第一种情况不会在 `e2` 内进行替换，而第二种情况
情况确实如此。因此，当我们遇到隐藏名称时，我们“停止”替换。
考虑`let x = 5 in let x = 6 in x`。我们知道它会评估为 `6`
OCaml 因为阴影。以下是它如何根据我们的定义进行评估
模拟PL：

```text
    let x = 5 in let x = 6 in x
--> (let x = 6 in x){5/x}
  = let x = 6{5/x} in x      ***
  = let x = 6 in x
--> x{6/x}
  = 6
```

在上面标记为 `***` 的行中，我们已停止在体内进行替换
表达式，因为我们到达了一个隐藏的变量名称。如果我们保留
进入体内，我们会得到不同的结果：

```text
    let x = 5 in let x = 6 in x
--> (let x = 6 in x){5/x}
  = let x = 6{5/x} in x{5/x}      ***WRONG***
  = let x = 6 in 5
--> 5{6/x}
  = 5
```

{{ video_embed | replace("%%VID%%", "4eywIvwhTfs")}}

**示例1：**

```text
let x = 2 in x + 1
--> (x + 1){2/x}
  = 2 + 1
--> 3
```

**示例2：**

```text
    let x = 0 in (let x = 1 in x)
--> (let x = 1 in x){0/x}
  = (let x = 1{0/x} in x)
  = (let x = 1 in x)
--> x{1/x}
  = 1
```

**示例3：**

```text
    let x = 0 in x + (let x = 1 in x)
--> (x + (let x = 1 in x)){0/x}
  = x{0/x} + (let x = 1 in x){0/x}
  = 0 + (let x = 1{0/x} in x)
  = 0 + (let x = 1 in x)
--> 0 + x{1/x}
  = 0 + 1
--> 1
```

{{ video_embed | replace("%%VID%%", "lBqdzVTSdCc")}}

## 实现替换

{{ video_embed | replace("%%VID%%", "gttjeAd5IS0")}}

上面的定义很容易转换成 OCaml 代码。请注意，虽然我们
在下面写 `v` ，该函数实际上可以替换任何表达式
一个变量，而不仅仅是一个值。解释器只会调用这个函数
不过，在一个值上。

```ocaml
(** [subst e v x] is [e] with [v] substituted for [x], that
    is, [e{v/x}]. *)
let rec subst e v x = match e with
  | Var y -> if x = y then v else e
  | Bool _ -> e
  | Int _ -> e
  | Binop (bop, e1, e2) -> Binop (bop, subst e1 v x, subst e2 v x)
  | Let (y, e1, e2) ->
    let e1' = subst e1 v x in
    if x = y
    then Let (y, e1', e2)
    else Let (y, e1', subst e2 v x)
  | If (e1, e2, e3) ->
    If (subst e1 v x, subst e2 v x, subst e3 v x)
```

## SimPL 解释器已完成！

我们已经完成了 SimPL 解释器的开发。回想一下完成的
解释器可以在这里下载：{{ code_link | replace("%%NAME%%",
"simpl.zip") }}。它包括一些基本的测试用例以及 makefile
你会发现有帮助的目标。

{{ video_embed | replace("%%VID%%", "348PIgywcss")}}

{{ video_embed | replace("%%VID%%", "Y2hiUqlfW8U")}}

## 避免捕获的替换

{{ video_embed | replace("%%VID%%", "WrHrKnbRc1w")}}

SimPL 替换的定义有点棘手，但也不是太难
复杂。但事实证明，一般来说，定义是
更复杂。

让我们考虑一下这个小语言：

```text
e ::= x | e1 e2 | fun x -> e
v ::= fun x -> e
x ::= <identifiers>
```

此语法也称为 *lambda 演算*。只有三种
其中的表达式：变量、函数应用和匿名函数。
唯一的值是匿名函数。语言甚至都没有打字。然而，一
它最显着的特性之一是它是*计算通用的：*
可以表达任何可计算的函数。 （要了解更多信息，请阅读
*丘奇-图灵假说*。）

有多种方法可以定义 lambda 的求值语义
微积分。也许最简单的方法——也最接近 OCaml——使用以下方法
规则：

```text
e1 e2 ==> v
  if e1 ==> fun x -> e
  and e2 ==> v2
  and e{v2/x} ==> v
```

该规则是我们需要的*唯一*规则：不需要其他规则。这条规则是
也称为“按值调用”语义，因为它要求参数
在应用函数之前减少到*值*。如果这看起来很明显，
这是因为你已经习惯了 OCaml。

然而，其他语义当然是可能的。例如，Haskell 使用
称为*call by name*的变体，具有单一规则：

```text
e1 e2 ==> v
  if e1 ==> fun x -> e
  and e{e2/x} ==> v
```

通过名称调用，`e2` 不必减少为一个值；这可能导致
如果永远不需要 `e2` 的值，则效率更高。

现在我们需要定义 lambda 演算的替换运算。我们会
就像适用于按名称调用或按值调用的定义一样。受到启发
根据我们对 SimPL 的定义，定义的开头如下：

```text
x{e/x} = e
y{e/x} = y
(e1 e2){e/x} = e1{e/x} e2{e/x}
```

前两行正是我们在 SimPL 中定义变量替换的方式。
下一行类似于我们定义二元运算符替换的方式；我们只是
递归到子表达式中。

函数中的替换怎么样？在 SimPL 中，当我们
到达同名的绑定变量；否则，我们继续。在
lambda 演算，这个想法可以表述如下：

```text
(fun x -> e'){e/x} = fun x -> e'
(fun y -> e'){e/x} = fun y -> e'{e/x}
```

也许令人惊讶的是，这个定义被证明是错误的。原因如下：它
违反了名称无关性原则。假设我们正在尝试这个
替换：

```text
(fun z -> x){z/x}
```

结果将是：

```text
  fun z -> x{z/x}
= fun z -> z
```

并且，突然间，一个“不是”恒等函数的函数变成了
恒等函数。然而，如果我们尝试这种替换：

```text
(fun y -> x){z/x}
```

结果将是：

```text
  fun y -> x{z/x}
= fun y -> z
```

这不是恒等函数。所以我们里面的替换定义
匿名函数是不正确的，因为它“捕获”变量。一个变量
在匿名函数中替换名称可能会意外发生
由函数的参数名称“捕获”。

请注意，我们在 SimPL 中从未遇到过此问题，部分原因是 SimPL 是类型化的。
函数 `fun y -> z` 如果应用于任何参数只会返回 `z`，
这是一个未绑定的变量。但 lambda 演算是无类型的，所以我们不能
在这里依靠打字来排除这种可能性。

所以问题就变成了：我们如何定义替换，才能得到正确结果而不捕获变量？
答案称为*避免捕获的替换*，数学家们一直没有找到它的正确定义
几个世纪。

正确的定义如下：

```text
(fun x -> e'){e/x} = fun x -> e'
(fun y -> e'){e/x} = fun y -> e'{e/x}  if y is not in FV(e)
```

其中 `FV(e)` 表示 `e` 的“自由变量”，即变量
不受其约束，定义如下：

```text
FV(x) = {x}
FV(e1 e2) = FV(e1) + FV(e2)
FV(fun x -> e) = FV(e) - {x}
```

`+` 表示集合并，`-` 表示集合差。

该定义防止替换 `(fun z -> x){z/x}` 发生，
因为 `z` 在 `FV(z)` 中。

不幸的是，由于附带条件 `y is not in FV(e)`，
替换操作现在是*部分*：有时，就像我们的例子一样
刚刚给出，无法应用的地方。

这个问题可以通过改变变量的名称来解决：如果我们检测到
遇到了偏向性，我们可以更改函数的名称
论点。例如，当遇到 `(fun z -> x){z/x}` 时，函数的
参数可以替换为新名称 `w` ，该名称不会出现在其他地方，
产生`(fun w -> x){z/x}`。 （如果 `z` 发生在身体的任何地方，它
也会被 `w` 替换。）这是*替换*，而不是替换：
绝对在任何我们看到 `z` 的地方，我们都会将其替换为 `w`。然后替换
可以继续并正确生成 `fun w -> z`。

其中棘手的部分是如何选择一个在任何地方都没有出现过的新名称
否则，就是如何挑选一个“新鲜”的名字。以下是三种策略：

1. 选择一个新的变量名，检查是否新鲜，如果不是，请尝试
再次，直到成功。例如，如果尝试替换 `z`，你可能
   首先尝试 `z'`，然后尝试 `z''`，依此类推。

1. 增强评估关系以维持一个流（即无限列表）
未使用的变量名。每次你需要一个新的时，就拿起它的头
   流。但任何时候你都必须小心使用流的尾部
   之后。为了保证它们不被使用，保留一些变量名
   供解释器单独使用，并使它们作为变量名非法
   由程序员选择。例如，你可能决定程序员
   变量名永远不能以字符 `$` 开头，然后有一个流
   `<$x1, $x2, $x3, ...>` 新名字。

1. 使用命令式计数器来模拟先前策略中的流。
例如，以下函数保证返回一个新变量
   每次调用时的名称：
   ```ocaml
   let gensym =
     let counter = ref 0 in
     fun () -> incr counter; "$x" ^ string_of_int !counter
   ```
名称 `gensym` 是此类函数的传统名称。它来自
   LISP，并出现在整个编译器实现中。这意味着
   <u>gen</u>erate a fresh <u>sym</u>bol.

有一个完整的 lambda 演算解释器实现，
包括避免捕获的替换，你可以下载：{{ code_link |
replace("%%NAME%%", "lambda-subst.zip") }}。它使用 `gensym` 策略
上面生成新名称。有一个名为 `strategy` 的定义
`main.ml` 可用于在按值调用和按名称调用之间切换。

## Core OCaml

现在让我们从 SimPL 和 lambda 演算升级到更大的语言
我们称之为*Core OCaml*。以下是 BNF 格式的语法：

```text
e ::= x | e1 e2 | fun x -> e
    | i | b | e1 bop e2
    | (e1, e2) | fst e | snd e
    | Left e | Right e
    | match e with Left x1 -> e1 | Right x2 -> e2
    | if e1 then e2 else e3
    | let x = e1 in e2

bop ::= + | - | * | <=

x ::= <identifiers>

i ::= <integers>

b ::= true | false

v ::= fun x -> e | i | b | (v1, v2) | Left v | Right v
```

我们在 `bop` 中指定的二元运算符是具有代表性的，
并不详尽。我们可以添加 `<`、`=` 等。

为了使这个核心模型中的元组保持简单，我们只用两个来表示它们
组件（即它们是成对的）。更长的元组可以用嵌套编码
对。例如，OCaml 中的 `(1, 2, 3)` 在此核心中可能是 `(1, (2, 3))`
语言。

此外，为了在这个核心模型中保持变体类型简单，我们用
只有两个构造函数，我们将其命名为 `Left` 和 `Right`。具有更多功能的变体
构造函数可以用这两个的嵌套应用程序进行编码
构造函数。由于我们只有两个构造函数，因此匹配表达式只需要
两个分支。阅读上面的 BNF 时要注意一点：`|` 出现在
`Right` 构造函数之前的匹配表达式表示语法，而不是
元语法。

该核心语言省略了一些重要的 OCaml 结构，
包括递归函数、异常、可变性和模块。类型有
也失踪了； Core OCaml 没有任何类型检查。尽管如此，还是有
这种核心语言足以让我们开心。

## 在替换模型中求值 Core OCaml

{{ video_embed | replace("%%VID%%", "ozocssmPMFY")}}

让我们定义 Core OCaml 的小步和大步关系。老实说，
在这一点上不会有太多令人惊讶的事情；我们已经看到了
SimPL 和 lambda 演算中已有的一切。

**小步关系。** 这是我们已经知道的 Core OCaml 的片段
模拟PL：

```text
e1 bop e2 --> e1' bop e2
	if e1 --> e1'

v1 bop e2 --> v1 bop e2'
	if e2 --> e2'

v1 bop v2 --> v3
	where v3 is the result of applying primitive operation bop
	to v1 and v2

if e1 then e2 else e3 --> if e1' then e2 else e3
	if e1 --> e1'

if true then e2 else e3 --> e2

if false then e2 else e3 --> e3

let x = e1 in e2 --> let x = e1' in e2
	if e1 --> e1'

let x = v in e2 --> e2{v/x}
```

这是与 lambda 演算相对应的 Core OCaml 片段：

```text
e1 e2 --> e1' e2
	if e1 --> e1'

v1 e2 --> v1 e2'
	if e2 --> e2'

(fun x -> e) v2 --> e{v2/x}
```

以下是 Core OCaml 的新部分。首先，**两人**评估他们的第一个
组件，然后是第二个组件：

```text
(e1, e2) --> (e1', e2)
	if e1 --> e1'

(v1, e2) --> (v1, e2')
	if e2 --> e2'

fst e --> fst e'
  if e --> e'

snd e --> snd e'
  if e --> e'

fst (v1, v2) --> v1

snd (v1, v2) --> v2
```

**构造函数**评估它们携带的表达式：

```text
Left e --> Left e'
	if e --> e'

Right e --> Right e'
	if e --> e'
```

**模式匹配** 评估正在匹配的表达式，然后减少到 1
分支机构：

```text
match e with Left x1 -> e1 | Right x2 -> e2
--> match e' with Left x1 -> e1 | Right x2 -> e2
	if e --> e'

match Left v with Left x1 -> e1 | Right x2 -> e2
--> e1{v/x1}

match Right v with Left x1 -> e1 | Right x2 -> e2
--> e2{v/x2}
```

**替换。** 我们还需要定义 Core 的替换操作
OCaml。以下是我们从 SimPL 和 lambda 演算中已知的信息：

```text
i{v/x} = i

b{v/x} = b

(e1 bop e2) {v/x} = e1{v/x} bop e2{v/x}

(if e1 then e2 else e3){v/x}
 = if e1{v/x} then e2{v/x} else e3{v/x}

(let x = e1 in e2){v/x} = let x = e1{v/x} in e2

(let y = e1 in e2){v/x} = let y = e1{v/x} in e2{v/x}
  if y not in FV(v)

x{v/x} = v

y{v/x} = y

(e1 e2){v/x} = e1{v/x} e2{v/x}

(fun x -> e'){v/x} = (fun x -> e')

(fun y -> e'){v/x} = (fun y -> e'{v/x})
  if y not in FV(v)
```

请注意，我们现在添加了避免捕获替换的要求
`let` 和 `fun` 的定义：它们都要求 `y` 不存在于 free 中
`v` 的变量。因此，我们需要定义一个自由变量
表达式：

```text
FV(x) = {x}
FV(e1 e2) = FV(e1) + FV(e2)
FV(fun x -> e) = FV(e) - {x}
FV(i) = {}
FV(b) = {}
FV(e1 bop e2) = FV(e1) + FV(e2)
FV((e1,e2)) = FV(e1) + FV(e2)
FV(fst e1) = FV(e1)
FV(snd e2) = FV(e2)
FV(Left e) = FV(e)
FV(Right e) = FV(e)
FV(match e with Left x1 -> e1 | Right x2 -> e2)
 = FV(e) + (FV(e1) - {x1}) + (FV(e2) - {x2})
FV(if e1 then e2 else e3) = FV(e1) + FV(e2) + FV(e3)
FV(let x = e1 in e2) = FV(e1) + (FV(e2) - {x})
```

最后，我们定义了 Core OCaml 中新语法形式的替换。
不绑定变量的表达式很容易处理：

```text
(e1,e2){v/x} = (e1{v/x}, e2{v/x})

(fst e){v/x} = fst (e{v/x})

(snd e){v/x} = snd (e{v/x})

(Left e){v/x} = Left (e{v/x})

(Right e){v/x} = Right (e{v/x})
```

匹配表达式需要更多的工作，就像 let 表达式和
匿名函数，以确保我们正确避免捕获：

```text
(match e with Left x1 -> e1 | Right x2 -> e2){v/x}
 = match e{v/x} with Left x1 -> e1{v/x} | Right x2 -> e2{v/x}
     if ({x1,x2} intersect FV(v)) = {}

(match e with Left x -> e1 | Right x2 -> e2){v/x}
 = match e{v/x} with Left x -> e1 | Right x2 -> e2{v/x}
     if ({x2} intersect FV(v)) = {}

(match e with Left x1 -> e1 | Right x -> e2){v/x}
 = match e{v/x} with Left x1 -> e1{v/x} | Right x -> e2
      if ({x1} intersect FV(v)) = {}

(match e with Left x -> e1 | Right x -> e2){v/x}
 = match e{v/x} with Left x -> e1 | Right x -> e2
```

对于编程语言的典型实现，我们不必担心
关于避免捕获替换，因为我们只评估类型良好的
表达式，没有自由变量。但对于更奇特的编程
语言中，可能需要评估开放表达式。在这些情况下，
我们需要上面给出的关于自由变量的所有额外条件。

## 大步关系

此时没有任何新概念需要介绍。
我们可以给出规则：
```
e1 e2 ==> v
  if e1 ==> fun x -> e
  and e2 ==> v2
  and e{v2/x} ==> v

fun x -> e ==> fun x -> e

i ==> i

b ==> b

e1 bop e2 ==> v
  if e1 ==> v1
  and e2 ==> v2
  and v is the result of primitive operation v1 bop v2

(e1, e2) ==> (v1, v2)
  if e1 ==> v1
  and e2 ==> v2

fst e ==> v1
  if e ==> (v1, v2)

snd e ==> v2
  if e ==> (v1, v2)

Left e ==> Left v
  if e ==> v

Right e ==> Right v
  if e ==> v

match e with Left x1 -> e1 | Right x2 -> e2 ==> v
  if e ==> Left v1
  and e1{v1/x1} ==> v

match e with Left x1 -> e1 | Right x2 -> e2 ==> v
  if e ==> Right v2
  and e2{v2/x2} ==> v

if e1 then e2 else e3 ==> v
  if e1 ==> true
  and e2 ==> v

if e1 then e2 else e3 ==> v
  if e1 ==> false
  and e3 ==> v

let x = e1 in e2 ==> v
  if e1 ==> v1
  and e2{v1/x} ==> v
```
