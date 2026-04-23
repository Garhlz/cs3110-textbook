# 类型检查

{{ video_embed | replace("%%VID%%", "_whuqDIWiO0")}}

早些时候，我们跳过了类型检查阶段。现在让我们回到这一点。
在词法分析和解析之后，编译的下一阶段是语义分析，
语义分析的首要任务是类型检查。

*类型系统*是如何确定一个类型是否是一个数学描述
表达式是*类型错误*或*类型正确*，在后一种情况下，类型是什么
的表达式是. *类型检查器*是一个实现类型的程序
系统，即实现语言的静态语义的系统。

通常，类型系统被表述为三元关系
$\mathit{HasType}(\Gamma, e, t)$，这意味着表达式 $e$ 的类型为 $t$
在静态环境 $\Gamma$ 中。*静态环境*，又名*类型上下文*，是
从标识符到类型的映射。静态环境是用来记录什么的
变量在范围内，以及它们的类型是什么。希腊字母的使用
静态环境的 $\Gamma$ 是传统的。

三元关系 $\mathit{HasType}$ 通常用中缀编写
不过，符号为 $\Gamma \vdash e : t$。你可以阅读十字转门符号
$\vdash$ 作为“证明”或“显示”，即静态环境 $\Gamma$ 显示
$e$ 的类型为 $t$。

让我们通过消除希腊语和
数学排版。我们只需写 `env |- e : t` 来表示静态
环境 `env` 显示 `e` 具有类型 `t`。我们之前使用 `env` 来表示
大步关系 `==>` 中的动态环境。既然总是有可能
查看我们是否使用 `==>` 或 `|-` 关系， `env` 的含义为
动态或静态环境总是可辨别的。

让我们为空静态环境写 `{}` ，并写 `x:t` 表示 `x` 是
绑定到 `t`。所以， `{foo:int, bar:bool}` 将是静态环境
`foo` 的类型为 `int`，而 `bar` 的类型为 `bool`。静态环境可以绑定
标识符最多一次。我们将写 `env[x -> t]` 来表示静态环境
它包含 `env` 的所有绑定，并将 `x` 绑定到 `t`。如果 `x` 是
已经绑定在 `env` 中，那么旧的绑定将被新的绑定替换
`t` 在 `env[x -> t]` 中。与动态环境一样，如果我们想要更多
数学符号我们会写 $\mapsto$ 而不是 `->`
`env[x -> v]`，但我们的目标是在标准上轻松输入的符号
键盘。

有了所有这些机制，我们终于可以定义良好类型的含义了：
表达式 `e` 在静态环境 `env` 中是**类型正确的**（如果存在）
类型 `t` 对应 `env |- e : t`。因此，类型检查器的目标是找到
这样的类型 `t`，从一些初始静态环境开始。

假装初始静态环境是空的很方便。但在
实践中，很少有语言真正使用空静态环境来
确定程序是否类型正确。例如，在 OCaml 中，有很多
始终在范围内的内置标识符，例如
`Stdlib` 模块。

## SimPL 类型系统

{{ video_embed | replace("%%VID%%", "9Lxz8qS3uQ8")}}

回想一下 SimPL 的语法：

```text
e ::= x | i | b | e1 bop e2
    | if e1 then e2 else e3
    | let x = e1 in e2

bop ::= + | * | <=
```

让我们为 SimPL 定义一个类型系统 `env |- e : t` 。 SimPL 中唯一的类型是
整数和布尔值：

```text
t ::= int | bool
```

为了定义 `|-`，我们将发明一组*打字规则*来指定类型
表达式的类型基于其子表达式的类型。换句话说，
`|-` 是一个*归纳定义的关系*，可以通过离散关系来了解
数学课程。因此，它有一些基本情况和一些归纳情况。

对于基本情况，整数常量在任何静态环境中都具有类型 `int`
无论如何，布尔常量同样总是具有类型 `bool`，并且变量
具有静态环境规定的任何类型。以下是
表达这些想法的输入规则：

```text
env |- i : int
env |- b : bool
{x : t, ...} |- x : t
```

其余的句法形式是归纳格。

**Let.** 正如我们从 OCaml 中所知，我们输入检查 let 的主体
使用通过新绑定扩展的范围的表达式。

```text
env |- let x = e1 in e2 : t2
  if env |- e1 : t1
  and env[x -> t1] |- e2 : t2
```

该规则表示 `let x = e1 in e2` 在静态环境 `env` 中具有类型 `t2`，
但前提是满足某些条件。第一个条件是 `e1` 具有类型
`t1` 在 `env` 中。第二个是 `e2` 在新的静态中具有类型 `t2`
环境，它被扩展为将 `x` 绑定到 `t1`。

**二元运算符。** 我们需要一些不同的二元运算符规则。

```text
env |- e1 bop e2 : int
  if bop is + or *
  and env |- e1 : int
  and env |- e2 : int

env |- e1 <= e2 : bool
  if env |- e1 : int
  and env |- e2 : int
```

**If.** 就像 OCaml 一样，if 表达式必须有一个布尔值守卫，并且它的两个
分支必须具有相同的类型。

```text
env |- if e1 then e2 else e3 : t
  if env |- e1 : bool
  and env |- e2 : t
  and env |- e3 : t
```

## SimPL 类型检查器

{{ video_embed | replace("%%VID%%", "BN_nIMgFZ_o")}}

让我们基于我们定义的类型系统为 SimPL 实现一个类型检查器
上一节。你可以下载完整的类型检查器作为
SimPL 解释器：{{ code_link | replace("%%NAME%%", "simpl.zip") }}

我们需要一个变体来表示类型：

```ocaml
type typ =
  | TInt
  | TBool
```

该变体的自然名称当然是“type”而不是“typ”，
但前者已经是 OCaml 中的关键字。我们必须为构造函数添加前缀
用“T”来消除它们与 `expr` 类型的构造函数的歧义，其中
包括 `Int` 和 `Bool`。

让我们介绍一个静态环境的小签名，基于
到目前为止我们已经介绍过的抽象：空的静态环境，查找
变量，并扩展静态环境。

```ocaml
module type StaticEnvironment = sig
  (** [t] is the type of a static environment. *)
  type t

  (** [empty] is the empty static environment. *)
  val empty : t

  (** [lookup env x] gets the binding of [x] in [env].
      Raises: [Failure] if [x] is not bound in [env]. *)
  val lookup : t -> string -> typ

  (** [extend env x ty] is [env] extended with a binding
      of [x] to [ty]. *)
  val extend : t -> string -> typ -> t
end
```

使用关联列表很容易实现该签名。

```ocaml
module StaticEnvironment : StaticEnvironment = struct
  type t = (string * typ) list

  let empty = []

  let lookup env x =
    try List.assoc x env
    with Not_found -> failwith "Unbound variable"

  let extend env x ty =
    (x, ty) :: env
end
```

现在我们可以实现类型关系 `|-`。我们将通过编写一个来做到这一点
函数 `typeof : StaticEnvironment.t -> expr -> typ`，这样
`typeof env e = t` 当且仅当 `env |- e : t` 时。请注意 `typeof`
函数产生类型作为输出，因此该函数实际上是在推断
键入！对于 SimPL 来说，这一推论很容易；这将是相当困难的
更大的语言。

{{ video_embed | replace("%%VID%%", "m3bt3BYB0vQ")}}

让我们从基本案例开始：

```ocaml
open StaticEnvironment

(** [typeof env e] is the type of [e] in static environment [env].
    Raises: [Failure] if [e] is not well-typed in [env]. *)
let rec typeof env = function
  | Int _ -> TInt
  | Bool _ -> TBool
  | Var x -> lookup env x
  ...
```

请注意到目前为止 `typeof` 的实现是如何基于我们的规则的
先前为 `|-` 定义。特别是：

* `typeof` 是一个递归函数，就像 `|-` 是一个归纳关系一样。
* `typeof` 递归的基本情况与基本情况相同
对于 `|-`。

另请注意 `typeof` 的实现与
`|-` 的定义：错误处理。类型系统没有说明要做什么
错误；相反，它只是定义了类型良好的含义。类型
另一方面，checker 需要采取行动并报告错误类型的程序。
我们的 `typeof` 函数通过引发异常来实现这一点。 `lookup` 函数，在
特别是，如果我们尝试查找一个变量，则会引发异常
没有被束缚在静态环境中。

{{ video_embed | replace("%%VID%%", "TiKPU5rYeF8")}}

让我们继续讨论递归情况：

```ocaml
  ...
  | Let (x, e1, e2) -> typeof_let env x e1 e2
  | Binop (bop, e1, e2) -> typeof_bop env bop e1 e2
  | If (e1, e2, e3) -> typeof_if env e1 e2 e3
```

为了保留，我们为每个分支分解了一个辅助函数
模式匹配可读。每个助手直接编码的想法
`|-` 规则，添加了错误处理。

```ocaml
and typeof_let env x e1 e2 =
  let t1 = typeof env e1 in
  let env' = extend env x t1 in
  typeof env' e2

and typeof_bop env bop e1 e2 =
  let t1, t2 = typeof env e1, typeof env e2 in
  match bop, t1, t2 with
  | Add, TInt, TInt
  | Mult, TInt, TInt -> TInt
  | Leq, TInt, TInt -> TBool
  | _ -> failwith "Operator and operand type mismatch"

and typeof_if env e1 e2 e3 =
  if typeof env e1 = TBool
  then begin
    let t2 = typeof env e2 in
    if t2 = typeof env e3 then t2
    else failwith "Branches of if must have same type"
  end
  else failwith "Guard of if must have type bool"
```

请注意 `typeof` 实现中的递归调用如何准确地发生在
`|-` 的定义是归纳式的。

最后，我们可以实现一个函数来检查表达式是否为
类型良好：

```ocaml
(** [typecheck e] checks whether [e] is well-typed in
    the empty static environment. Raises: [Failure] if not. *)
let typecheck e =
  ignore (typeof empty e)
```

## 类型安全

{{ video_embed | replace("%%VID%%", "MrmEIbDOfnk")}}

类型系统的目的是什么？可能有很多，但其中之一
主要目的是确保不会发生某些运行时错误。现在那
我们知道如何用 `|-` 关系形式化类型系统并用
通过 `-->` 关系，我们可以使这个想法变得精确。

语言设计者的目标通常包括确保这两个
在 `|-` 和 `-->` 之间建立关系的属性都包含：

* **进展：** 如果一个表达式类型正确，那么它要么已经是一个
值，或者至少可以采取一步。我们可以将其形式化为“对于所有
  `e`，如果存在 `t` 使得 `{} |- e : t` 存在，则 `e` 是一个值，或者
  存在 `e'` 这样 `e --> e'`。”

* **保留：** 如果一个表达式类型正确，那么如果该表达式
步骤，新表达式与旧表达式具有相同的类型。正式地，
  “对于所有 `e` 和 `t` 这样的 `{} |- e : t`，如果存在这样的 `e'`
  `e --> e'`，然后`{} |- e' : t`。”

总而言之，进步加上保存意味着对一个事物的评估
类型良好的表达式永远不会“卡住”，这意味着它达到一个非值
无法迈出一步。此属性称为“类型安全”。

例如，使用 SimPL 求值关系 `5 + true` 会陷入困境，
因为原始 `+` 操作不能接受布尔值作为操作数。但是
SimPL 类型系统不会接受该程序，从而使我们免于陷入困境
达到那种境地。

回顾我们写的SimPL，到处都是`step`的实现
我们提出例外的地方是评估会陷入困境的地方。但是
类型系统保证这些异常永远不会发生。
