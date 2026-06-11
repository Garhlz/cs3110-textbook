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

## 用 Let 进行模式匹配

事实上，我们一直在使用的 let 表达式语法只是 OCaml 完整语法的一个特例。完整语法是：
```ocaml
let p = e1 in e2
```
也就是说，绑定的左侧实际上可以是一个模式，而不仅仅是一个标识符。当然，变量标识符本身就在我们的合法模式列表之中，这也是为什么我们之前学到的语法只是一个特例。

有了这个更一般的语法，我们来重新审视 let 表达式的语义。

**动态语义。**

对 `let p = e1 in e2` 求值：

1. 将 `e1` 求值为值 `v1`。

2. 将 `v1` 与模式 `p` 进行匹配。如果匹配失败，则引发 `Match_failure` 异常。如果匹配成功，则产生一组绑定 $b$。

3. 将绑定 $b$ 替换到 `e2` 中，产生新表达式 `e2'`。

4. 将 `e2'` 求值为值 `v2`。

5. 整个 let 表达式的求值结果为 `v2`。

**静态语义。**

* 如果以下条件全部成立，则 `(let p = e1 in e2) : t2`：

  - `e1 : t1`

  - `p` 中的模式变量为 `x1..xn`

  - 在假设对所有 `i` ∈ `1..n` 有 `xi : ti` 的前提下，可推出 `e2 : t2`

**let 定义。**

和之前一样，let 定义可以理解为一个主体尚未给出的 let 表达式。因此其语法可以推广为：
```ocaml
let p = e
```
其语义也同之前一样，遵循 let 表达式的语义。

## 用函数进行模式匹配

我们迄今为止使用的函数语法同样只是 OCaml 完整语法的一个特例。完整语法是：
```ocaml
let f p1 ... pn = e1 in e2   (* 作为 let 表达式一部分的函数 *)
let f p1 ... pn = e          (* 顶层的函数定义 *)
fun p1 ... pn -> e           (* 匿名函数 *)
```

我们真正需要关心的原始语法形式是 `fun p -> e`。让我们重新审视匿名函数的语义以及函数应用的语义；其他形式的变化由此可以推出：

**静态语义。**

* 令 `x1..xn` 为 `p` 中出现的模式变量。如果在假设 `x1 : t1`、`x2 : t2`、...、`xn : tn` 的前提下，可以推出 `p : t` 和 `e : u`，那么 `fun p -> e : t -> u`。

* 函数应用的类型检查规则不变。

**动态语义。**

* 匿名函数的求值规则不变。

* 对 `e0 e1` 求值：

  1. 将 `e0` 求值为匿名函数 `fun p -> e`，并将 `e1` 求值为值 `v1`。

  2. 将 `v1` 与模式 `p` 进行匹配。如果匹配失败，则引发 `Match_failure` 异常。如果匹配成功，则产生一组绑定 $b$。

  3. 将绑定 $b$ 替换到 `e` 中，产生新表达式 `e'`。

  4. 将 `e'` 求值为值 `v`，这就是 `e0 e1` 的求值结果。

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
