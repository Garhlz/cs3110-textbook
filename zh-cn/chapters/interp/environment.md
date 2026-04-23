# 环境模型

{{ video_embed | replace("%%VID%%", "cYnSVZIczJE")}}

到目前为止，我们一直在使用替换模型来求值程序。这是一个
很好的求值思维模型，常用于编程
语言理论。

但在实现方面，替换模型并不是最好的选择。
它太“急切”了：它会替换变量的每次出现，
即使这种情况永远不需要发生。例如，`let x = 42 in e`
将需要遍历整个 `e`，而 `e` 可能是一个非常大的表达式，
即使 `x` 从未出现在 `e` 中，或者即使 `x` 仅出现在 `e` 的分支内
永远不会被求值的 if 表达式。

为了提高效率，最好采用*惰性*方式：只有当解释器确实需要变量的值时，
才进行替换。这就是“环境模型”背后的关键思想。在这个模型中，
有一种数据结构称为“动态环境”，简称“环境”，
它是一个将变量名映射到值的字典。
每当需要变量的值时，就会在该字典中查找它。

为了纳入环境，求值关系需要改变。相对于
`e --> e'` 或 `e ==> v` 的，两者都是二元关系，我们现在需要一个
三元关系，即

* `<env, e> --> e'`，或

* `<env, e> ==> v`，

其中 `env` 表示环境，`<env, e>` 称为 *machine
配置*。该配置代表计算机的状态
求值程序：`env` 代表计算机内存的一部分（
变量与值的绑定），`e` 代表程序。

作为符号，让：

* `{}` 代表空环境，

* `{x1:v1, x2:v2, ...}` 表示将 `x1` 绑定到 `v1` 等的环境，

* `env[x -> v]` 表示环境 `env` 和变量 `x`
另外绑定到值 `v`，并且

* `env(x)` 表示 `x` 与 `env` 的绑定。

如果我们想要一个更数学的符号，我们会写 $\mapsto$ 而不是
`->` 在 `env[x -> v]` 中，但我们的目标是易于在
标准键盘。

我们将在本章的其余部分集中讨论
环境模型。当然也可以定义一个小步
版本也一样。

{{ video_embed | replace("%%VID%%", "93CN7gV_G2w")}}

{{ video_embed | replace("%%VID%%", "YZO-vQohBYA")}}

## 在环境模型中求值 Lambda 演算

{{ video_embed | replace("%%VID%%", "l0Db3KW5X_U")}}

回想一下 lambda 演算是函数式语言的片段
涉及函数及应用：

```text
e ::= x | e1 e2 | fun x -> e

v ::= fun x -> e
```

让我们探讨一下如何定义 lambda 的大步求值关系
环境模型中的演算。变量规则只是说要查找
环境中的变量名称：

```text
<env, x> ==> env(x)
```

这条函数规则表示匿名函数求值为它自身。毕竟，函数就是值：

```text
<env, fun x -> e> ==> fun x -> e
```

最后，这条应用规则表示：先把左侧 `e1` 求值为函数 `fun x -> e`，
再把右侧求值为 `v2`，然后在把函数参数 `x` 映射到 `v2` 的扩展环境中
求值函数体 `e`：

```text
<env, e1 e2> ==> v
  if <env, e1> ==> fun x -> e
  and <env, e2> ==> v2
  and <env[x -> v2], e> ==> v
```

看起来很合理，对吧？问题是，**这是错误的。** 至少，如果
你希望评估的行为与 OCaml 相同。或者，老实说，几乎任何
其他现代语言。

如果我们再添加两种语言，会更容易解释为什么它是错误的
特点：let 表达式和整型常量。整数常量将
对自己的评价：

```text
<env, i> ==> i
```

至于 let 表达式，请记住我们实际上并不“需要”它们，
因为`let x = e1 in e2`可以重写为`(fun x -> e2) e1`。
尽管如此，它们的语义是：

```text
<env, let x = e1 in e2> ==> v
  if <env, e1> ==> v1
  and <env[x -> v1], e2> ==> v
```

这条规则实际上只是从上面的其他规则中得出的，使用该规则
重写。

这个表达式的计算结果是什么？

```text
let x = 1 in
let f = fun y -> x in
let x = 2 in
f 0
```

根据我们迄今为止的语义，它将评估如下：

* `let x = 1` 将产生环境 `{x:1}`。
* `let f = fun y -> x` 将产生环境 `{x:1, f:(fun y -> x)}`。
* `let x = 2` 将产生环境 `{x:2, f:(fun y -> x)}`。注意如何
`x` 到 `1` 的绑定被新绑定隐藏。
* 现在我们将评估 `<{x:2, f:(fun y -> x)}, f 0>`：
  ```
  <{x:2, f:(fun y -> x)}, f 0> ==> 2
	because <{x:2, f:(fun y -> x)}, f> ==> fun y -> x
	and <{x:2, f:(fun y -> x)}, 0> ==> 0
	and <{x:2, f:(fun y -> x)}[y -> 0], x> ==> 2
	  because <{x:2, f:(fun y -> x), y:0}, x> ==> 2
  ```
* 因此结果是 `2`。

但根据 utop（以及替换模型），它的求值如下：

```ocaml
# let x = 1 in
  let f = fun y -> x in
  let x = 2 in
  f 0;;
- : int = 1
```

因此结果是 `1`。显然，`1` 和 `2` 是不同的答案！

出了什么问题？  这与范围有关。

## 词法作用域与动态作用域

{{ video_embed | replace("%%VID%%", "s9kiXx0cSb4")}}

有两种不同的方式来理解变量的范围： 变量
可以是*动态*作用域或*词法*作用域。这一切都归结为
求值函数体时使用的环境：

* 根据**动态作用域规则**，函数体在
应用函数时的当前动态环境，而不是旧的
  定义函数时存在的动态环境。

* 根据**词法作用域规则**，函数体在
定义函数时存在的旧动态环境，而不是
  应用该函数时的当前环境。

动态作用域的规则就是我们上面的语义所实现的。让我们看看
回到函数应用的语义：

```text
<env, e1 e2> ==> v
  if <env, e1> ==> fun x -> e
  and <env, e2> ==> v2
  and <env[x -> v2], e> ==> v
```

请注意主体 `e` 是如何在同一环境 `env` 中进行求值的
就像应用该函数时一样。  在示例程序中

```text
let x = 1 in
let f = fun y -> x in
let x = 2 in
f 0
```

这意味着 `f` 在 `x` 绑定到 `2` 的环境中进行求值，
因为这是 `x` 的最新绑定。

但 OCaml 实现了词法作用域规则，这与
替换模型。根据该规则，`x` 在 `f` 主体中绑定到 `1`
定义了 `f` ，并且稍后将 `x` 绑定到 `2` 不会改变这一事实。

经过数十年编程语言设计经验的共识是
词法范围是正确的选择。也许主要原因是
词法范围支持名称无关原则。回想一下，这个原则
表示变量的名称与程序的含义无关，因为
只要该名称的使用一致。

尽管如此，动态作用域在某些情况下还是有用的。有些语言使用它
作为规范（例如，Emacs LISP、LaTeX），并且某些语言有特殊的方法
去做（例如 Perl、Racket）。但如今，大多数语言都没有它。

现代语言*确实*具有一种类似于
动态范围，那就是例外。异常处理类似于动态
范围，因为引发异常会将控制权转移到“最近的”
异常处理程序，就像动态作用域如何使用“最新”绑定一样
变量。

## 在环境模型中求值 Lambda 演算的第二次尝试

{{ video_embed | replace("%%VID%%", "Y0V_92x5J-Q")}}

那么问题就变成了，我们如何实现词法作用域？看来
需要时间旅行，因为函数体需要在旧的动态中进行评估
早已消失的环境。

答案是语言实现必须安排保持旧的
周围的环境。这确实是 OCaml 和其他语言必须做的事情。
为此，他们使用了一种称为“闭包”的数据结构。

闭包有两个部分：

* 一个 *code* 部分，其中包含函数 `fun x -> e`，以及

* 一个 *environment* 部分，其中包含当时的环境 `env`
函数被定义。

你可以把闭包想象成一对，只不过没有办法
直接在OCaml源代码中写一个闭包，并且没有办法解构
将其配对到 OCaml 源代码中的组件中。这对完全隐藏
通过语言实现从你那里得到。

我们将闭包标记为 `(| fun x -> e, env |)`。分隔符 `(| ... |)`
旨在唤起 OCaml 对，但当然它们不是合法的 OCaml 语法。

使用该符号，我们可以重新定义求值关系，如下所示：

函数规则现在规定匿名函数的求值结果是闭包：

```text
<env, fun x -> e> ==> (| fun x -> e, env |)
```

该规则将定义环境保存为闭包的一部分，以便它可以
在将来的某个时刻使用。

应用程序规则要求使用该闭包：

```text
<env, e1 e2> ==> v
  if <env, e1> ==> (| fun x -> e, defenv |)
  and <env, e2> ==> v2
  and <defenv[x -> v2], e> ==> v
```

该规则使用闭包的环境 `defenv` （其名称旨在
建议“定义环境”）来评估函数体 `e`。

let 表达式的派生规则保持不变：

```text
<env, let x = e1 in e2> ==> v
  if <env, e1> ==> v1
  and <env[x -> v1], e2> ==> v
```

这是因为主体 `e2` 的定义环境与
评估 let 表达式时的当前环境 `env` 。

## 环境模型中 Lambda 演算的实现

你可以下载上述两个 lambda 演算语义的完整实现：
{{ code_link | replace("%%NAME%%", "lambda-env.zip") }}。在`main.ml`中，有一个
名为 `scope` 的定义，可用于在词法和动态之间切换
范围。

## 在环境模型中求值 Core OCaml

{{ video_embed | replace("%%VID%%", "z2ktAgYTCRw")}}

Core 的（一大步）环境模型语义中没有任何新内容
OCaml，现在我们已经了解了闭包，但为了完整起见，让我们声明一下
无论如何。

**语法。**

```text
e ::= x | e1 e2 | fun x -> e
    | i | b | e1 bop e2
    | (e1,e2) | fst e1 | snd e2
    | Left e | Right e
    | match e with Left x1 -> e1 | Right x2 -> e2
    | if e1 then e2 else e3
    | let x = e1 in e2
```

**语义。**

我们已经了解了 Core OCaml 的 lambda 演算片段的语义：

```text
<env, x> ==> v
  if env(x) = v

<env, e1 e2> ==> v
  if  <env, e1> ==> (| fun x -> e, defenv |)
  and <env, e2> ==> v2
  and <defenv[x -> v2], e> ==> v

<env, fun x -> e> ==> (|fun x -> e, env|)
```

常量的计算忽略了环境：

```text
<env, i> ==> i

<env, b> ==> b
```

大多数其他语言特性的评估只是使用环境而不是
改变它：

```text
<env, e1 bop e2> ==> v
  if  <env, e1> ==> v1
  and <env, e2> ==> v2
  and v is the result of applying the primitive operation bop to v1 and v2

<env, (e1, e2)> ==> (v1, v2)
  if  <env, e1> ==> v1
  and <env, e2> ==> v2

<env, fst e> ==> v1
  if <env, e> ==> (v1, v2)

<env, snd e> ==> v2
  if <env, e> ==> (v1, v2)

<env, Left e> ==> Left v
  if <env, e> ==> v

<env, Right e> ==> Right v
  if <env, e> ==> v

<env, if e1 then e2 else e3> ==> v2
  if <env, e1> ==> true
  and <env, e2> ==> v2

<env, if e1 then e2 else e3> ==> v3
  if <env, e1> ==> false
  and <env, e3> ==> v3
```

最后，评估结合结构（即匹配
并让表达式）使用新的绑定扩展环境：

```text
<env, match e with Left x1 -> e1 | Right x2 -> e2> ==> v1
  if  <env, e> ==> Left v
  and <env[x1 -> v], e1> ==> v1

<env, match e with Left x1 -> e1 | Right x2 -> e2> ==> v2
  if  <env, e> ==> Right v
  and <env[x2 -> v], e2> ==> v2

<env, let x = e1 in e2> ==> v2
  if  <env, e1> ==> v1
  and <env[x -> v1], e2> ==> v2
```

{{ video_embed | replace("%%VID%%", "VZTrEYb6PPk")}}
