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

# 高级模式匹配

以下是一些有用的额外模式形式：

* `p1 | ... | pn`：“或”模式；如果匹配则匹配成功
成功对抗任何单个模式 `pi`，这些模式按顺序尝试
  从左到右。所有模式必须绑定相同的变量。

* `(p : t)`：具有显式类型注释的模式。

* `c`：这里，`c`表示任何常量，例如整数文字，字符串文字，
和布尔值。

* `'ch1'..'ch2'`：这里，`ch` 表示字符文字。例如，`'A'..'Z'`
匹配任何大写字母。

* `p when e`：匹配 `p`，但前提是 `e` 计算结果为 `true`。

你可以在手册中阅读[所有模式形式][patterns]。

[patterns]: https://ocaml.org/manual/patterns.html

## 使用 Let 进行模式匹配

事实上，到目前为止我们一直使用的 let 表达式的语法是一种特殊的
OCaml 允许的完整语法的情况。该语法是：
```ocaml
let p = e1 in e2
```
也就是说，装订的左侧实际上可能是一个图案，而不仅仅是一个
标识符。当然，变量标识符在我们的有效模式列表中，
这就是为什么我们到目前为止所研究的语法只是一个特例。

考虑到这种语法，我们重新审视 let 表达式的语义。

**动态语义。**

要对 `let p = e1 in e2` 求值：

1. 将 `e1` 计算为值 `v1`。

2. 将 `v1` 与模式 `p` 进行匹配。如果不匹配，则引发异常
`Match_failure`。否则，如果匹配，它会生成一组 $b$
   绑定。

3. 将这些绑定替换为 `e2` 中的 $b$，产生新的表达式 `e2'`。

4. 将 `e2'` 计算为值 `v2`。

5. let 表达式的求值结果是 `v2`。

**静态语义。**

* 如果以下所有条件成立，则 `(let p = e1 in e2) : t2`：

  - `e1 : t1`

  - `p` 中的模式变量是 `x1..xn`

  - `e2 : t2` 假设对于 `1..n` 中的所有 `i` 来说，它认为
`xi : ti`，

**让定义。**

和之前一样，let 定义可以理解为一个 let 表达式，其主体有
尚未给出。所以他们的语法可以概括为
```ocaml
let p = e
```
和以前一样，它们的语义遵循 let 表达式的语义。

## 使用函数进行模式匹配

到目前为止我们使用的函数语法也是
OCaml 允许的完整语法。该语法是：
```ocaml
let f p1 ... pn = e1 in e2   (* function as part of let expression *)
let f p1 ... pn = e          (* function definition at toplevel *)
fun p1 ... pn -> e           (* anonymous function *)
```

我们需要关心的真正原始的语法形式是`fun p -> e`。让我们
重新审视匿名函数的语义及其应用
形式；其他表格的变化如下：

**静态语义。**

* 令 `x1..xn` 为 `p` 中出现的模式变量。如果假设
`x1 : t1` 和 `x2 : t2` 以及 ... 和 `xn : tn`，我们可以得出结论 `p : t`
  和 ` e : u`，然后是 `fun p -> e : t -> u`。

* 应用程序的类型检查规则不变。

**动态语义。**

* 匿名函数的求值规则不变。

* 要对 `e0 e1` 求值：

  1. 将 `e0` 计算为匿名函数 `fun p -> e`，并且
将 `e1` 求值为值 `v1`。

  2. 将 `v1` 与模式 `p` 进行匹配。如果不匹配，则引发异常
`Match_failure`。否则，如果匹配，它会生成一组 $b$
     绑定。

  3. 将这些绑定替换为 `e` 中的 $b$，产生新的表达式 `e'`。

  4. 将 `e'` 计算为值 `v`，这是计算 `e0 e1` 的结果。

## 模式匹配示例

{{ video_embed | replace("%%VID%%", "3ExRHHqfWm4")}}

以下是获得 Pok&eacute;mon 生命值的几种方法：
```{code-cell} ocaml
(* Pokemon types *)
type ptype = TNormal | TFire | TWater

(* A record to represent Pokemon *)
type mon = { name : string; hp : int; ptype : ptype }

(* OK *)
let get_hp m = match m with { name = n; hp = h; ptype = t } -> h

(* better *)
let get_hp m = match m with { name = _; hp = h; ptype = _ } -> h

(* better *)
let get_hp m = match m with { name; hp; ptype } -> hp

(* better *)
let get_hp m = match m with { hp; _ } -> hp

(* best *)
let get_hp m = m.hp
```

以下是获取一对的第一个和第二个组件的方法：
```{code-cell} ocaml
let fst (x, _) = x

let snd (_, y) = y
```
`fst` 和 `snd` 实际上已经在标准中为你定义了
库。

最后，这里有几种获取三元组的第三个分量的方法：
```{code-cell} ocaml
(* OK *)
let thrd t = match t with x, y, z -> z

(* good *)
let thrd t =
  let x, y, z = t in
  z

(* better *)
let thrd t =
  let _, _, z = t in
  z

(* best *)
let thrd (_, _, z) = z
```
标准库没有定义任何三元组、四元组等函数。
