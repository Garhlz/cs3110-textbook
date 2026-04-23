# 解析

你“可以”从头开始编写自己的词法分析器和解析器。但很多
语言包括自动生成词法分析器和解析器的工具
来自语言语法的正式描述。祖先
其中许多工具是 [lex][lex] 和 [yacc][yacc]，它们生成
分别是词法分析器和解析器； lex 和 yacc 是在
20 世纪 70 年代为 C 语言开发的。

作为标准发行版的一部分，OCaml 提供词法分析器和解析器
名为 [ocamllex and ocamlyacc][ocamllexyacc] 的生成器。还有一个更
名为 [menhir][menhir] 的现代解析器生成器可通过 opam 获得；
Menhir 与 ocamlyacc “90% 兼容”，并显著
改进了对调试生成的解析器的支持。

[lex]: https://en.wikipedia.org/wiki/Lex_(software)
[yacc]: https://en.wikipedia.org/wiki/Yacc
[ocamllexyacc]: https://ocaml.org/manual/lexyacc.html
[menhir]: http://gallium.inria.fr/~fpottier/menhir/

## 词法分析器

Lexer 生成器（例如 lex 和 ocamllex）基于以下理论构建：
确定性有限自动机，通常包含在离散数学或
计算理论课程。这种自动机接受*正则语言*，这些语言
可以用*正则表达式*来描述。因此，词法分析器生成器的输入
是描述语言标记的正则表达式的集合。
输出是用高级语言实现的自动机，例如 C（例如
lex）或 OCaml（对于 ocamllex）。

该自动机本身将文件（或字符串）作为输入，并且每个字符
该文件成为自动机的输入。最终，自动机要么
*识别*它收到的字符序列为语言中的有效标记，
在这种情况下，自动机会输出该标记，并且
将自身重置为识别下一个标记；要么“拒绝”该序列
字符作为无效标记。

## 解析器

诸如 yacc 和 menhir 之类的解析器生成器同样是基于以下理论构建的：
自动机。但他们使用*下推自动机*，这就像有限自动机
还维护一个堆栈，可以在其中压入和弹出符号。堆栈
使他们能够接受更大类别的语言，这些语言被称为
*上下文无关语言*（CFL）。 CFL 的重大改进之一
正则语言的一个优点是 CFL 可以表达分隔符必须平衡这一思想
&mdash;例如，每个左括号必须由一个匹配的
右括号。

正如正则语言可以用特殊符号来表达一样（正则
表达式），CFL 也可以。 *上下文无关语法*用于描述 CFL。一个
上下文无关语法是一组“产生规则”，描述一个符号如何
可以用其他符号代替。例如，平衡的语言
括号，其中包括 `(())` 和 `()()` 和 `(()())` 等字符串，但是
不是诸如 `)` 或 `(()` 之类的字符串，是由以下规则生成的：

* $S \rightarrow (S)$
* $S \rightarrow SS$
* $S \rightarrow \epsilon$

这些规则中出现的符号是 $S$、$($ 和 $)$。 $\epsilon$
表示空字符串。每个符号要么是*非终结符*，要么是
*终结符*，取决于它是否是所描述语言的标记。
上例中 $S$ 是非终结符， ( 和 ) 是终结符。

在下一节中，我们将研究*巴科斯-诺尔范式* (BNF)，这是一个标准
上下文无关语法的符号。解析器生成器的输入通常是
语言语法的 BNF 描述。解析器生成器的输出
是一个识别语言语法的程序。作为输入，该程序
期望词法分析器的输出。作为输出，程序产生一个值
表示已接受的字符串的 AST 类型。输出的程序
因此，解析器生成器和词法分析器生成器依赖于另一个生成器
根据 AST 类型。

## 巴科斯-诺尔范式

{{ video_embed | replace("%%VID%%", "NQacOvZbbX4")}}

描述语言语法的标准方法是使用数学
称为*巴科斯-诺尔形式* (BNF) 的表示法，以其发明者约翰·巴科斯 (John Backus) 命名
和彼得·瑙尔。 BNF 有多种变体。在这里，我们不会太挑剔
关于遵守一种或另一种变体。我们的目标只是有一个合理的
描述语言语法的好符号。

BNF 使用一组“推导规则”来描述语言的语法。让我们
从一个例子开始。这是一种小型语言的 BNF 描述
仅包含整数和加法的表达式：

```text
e ::= i | e + e
i ::= <integers>
```

这些规则规定表达式 `e` 要么是一个整数 `i`，要么是两个
其间出现符号 `+` 的表达式。 “整数”的语法
这些规则未指定。

每个规则都有以下形式

```text
metavariable ::= symbols | ... | symbols
```

*元变量*是 BNF 规则中使用的变量，而不是
所描述语言中的变量。规则中出现的 `::=` 和 `|` 是
*元语法*：用于描述语言语法的 BNF 语法。*符号*是
可以包含元变量（例如 `i` 和 `e`）以及标记的序列
语言的名称（例如 `+`）。空格与这些规则无关。

有时我们可能想轻松引用个别事件
元变量。我们通过在
元变量。例如，我们可以将上面的第一条规则重写为

```text
e ::= i | e1 + e2
```

或作为

```text
e ::= i | e + e'
```

现在我们可以谈论 `e2` 或 `e'` 而不必说“
`+` 的右侧。

如果语言本身包含标记 `::=` 或 `|`&mdash; 并且
OCaml确实包含了后者&mdash;那么写BNF可以变得有点
令人困惑。一些 BNF 符号试图通过使用额外的方法来解决这个问题
用于区分语法和元语法的分隔符。我们会更加放松和
假设读者能够区分它们。

## 示例：SimPL

作为一个运行示例，我们将使用一种非常简单的编程语言，我们称之为
SimPL。以下是 BNF 格式的语法：

```text
e ::= x | i | b | e1 bop e2
    | if e1 then e2 else e3
    | let x = e1 in e2

bop ::= + | * | <=

x ::= <identifiers>

i ::= <integers>

b ::= true | false
```

显然，这种语言缺少很多东西，尤其是函数。但是
这足以让我们研究解释器中的重要概念
不会因大量语言特性而分心。稍后我们将
考虑 OCaml 的更大片段。

我们将为 SimPL 开发一个完整的解释器。你可以下载
此处完成解释：{{ code_link | replace("%%NAME%%", "simpl.zip") }}。
或者，只要跟着我们构建它的每个部分即可。

### AST

{{ video_embed | replace("%%VID%%", "duTIBuK_fdw")}}

由于 AST 是解释器中最重要的数据结构，让我们
先设计一下。我们将此代码放入名为 `ast.ml` 的文件中：

```ocaml
type bop =
  | Add
  | Mult
  | Leq

type expr =
  | Var of string
  | Int of int
  | Bool of bool
  | Binop of bop * expr * expr
  | Let of string * expr * expr
  | If of expr * expr * expr
```

对于表达式中的每种语法形式都有一个构造函数
巴纳夫。对于标识符、整数的底层基本语法类，
和布尔值，我们使用 OCaml 自己的 `string`、`int` 和 `bool` 类型。

我们可以不定义 `bop` 类型和单个 `Binop` 构造函数
为三个二元运算符定义了三个单独的构造函数：

```ocaml
type expr =
  ...
  | Add of expr * expr
  | Mult of expr * expr
  | Leq of expr * expr
  ...
```

但是通过分解 `bop` 类型，我们将能够避免大量代码
稍后在我们的实现中会出现重复。

### Menhir 解析器

{{ video_embed | replace("%%VID%%", "-BBbgVhj66s")}}

让我们从解析开始，然后再回到词法分析。我们会把所有的纪念碑
我们将下面的代码写入名为 `parser.mly` 的文件中。 `.mly` 扩展名表示
该文件旨在作为 Menhir 的输入。 （“y”暗指 yacc。）这
文件包含我们要解析的语言的*语法定义*。
下面通过示例描述语法定义的语法。请注意，这是
也许有点奇怪，但那是因为它基于工具（如 yacc）
是很久以前开发的。 Menhir 将处理该文件并生成一个
名为 `parser.ml` 的文件作为输出；它包含一个 OCaml 程序来解析
语言。 （这里的名字 `parser` 没有什么特别的；它只是
描述性的。）

语法定义有四个部分：标题、声明、规则和
拖车。

**标头。** *标头* 出现在 `%{` 和 `%}` 之间。这是代码
按字面意思复制到生成的 `parser.ml` 中。这里我们只是用它来打开
`Ast` 模块，以便稍后在语法定义中，我们可以编写
类似 `Int i` 而不是 `Ast.Int i` 的表达式。如果我们愿意的话，我们也可以
在标头中定义一些 OCaml 函数。

```text
%{
open Ast
%}
```

**声明。** *声明*部分首先说明词汇是什么
该语言的*标记*是。以下是 SimPL 的令牌声明：

```text
%token <int> INT
%token <string> ID
%token TRUE
%token FALSE
%token LEQ
%token TIMES
%token PLUS
%token LPAREN
%token RPAREN
%token LET
%token EQUALS
%token IN
%token IF
%token THEN
%token ELSE
%token EOF
```

其中每一个都只是令牌的描述性名称。到目前为止还没有任何说法
例如，`LPAREN` 实际上对应于 `(`。当我们
定义词法分析器。

`EOF` 标记是一个特殊的*文件结束*标记，当
它到达字符流的末尾。到那时我们就知道完整的
程序已被读取。

带有 `<type>` 注释的标记声明：
他们将携带一些额外的数据。在 `INT` 的情况下，
这是一个 OCaml `int`。对于 `ID` 来说，这是一个 OCaml `string`。

声明令牌后，我们必须提供一些附加信息
*优先级*和*关联性*。以下声明表示 `PLUS` 是
左关联，`IN` 不关联，并且 `PLUS` 的优先级高于
`IN` （因为 `PLUS` 出现在 `IN` 之后的一行上）。

```text
%nonassoc IN
%nonassoc ELSE
%left LEQ
%left PLUS
%left TIMES
```

因为 `PLUS` 是左关联的，所以 `1 + 2 + 3` 将解析为 `(1 + 2) + 3` 并且
不像`1 + (2 + 3)`。由于 `PLUS` 的优先级高于 `IN`，因此
表达式 `let x = 1 in x + 2` 将解析为 `let x = 1 in (x + 2)` 而不是
`(let x = 1 in x) + 2`。其他声明也有类似的效果。

正确的优先级和关联性声明是其中之一
开发语法定义中比较棘手的部分。它有助于发展
增量语法定义，仅添加几个标记（及其
相关规则，下面讨论）一次到语言。门希尔会让
你知道当你添加了一个令人困惑的令牌（和规则）时
你想要的优先级和关联性应该是什么。然后你可以添加
声明并进行测试以确保你的声明正确。

声明关联性和优先级后，我们需要声明什么
起点是解析语言。以下声明表示
从名为 `prog` 的规则（定义如下）开始。声明还表示
解析 `prog` 将返回类型为 `Ast.expr` 的 OCaml 值。

```text
%start <Ast.expr> prog
```

最后，`%%` 结束声明部分。

```text
%%
```

**规则。** *rules* 部分包含类似于 BNF 的产生式规则，
尽管在 BNF 中我们会写“::=”，但这些规则只是写“:”。
规则的格式是

```text
name:
  | production1 { action1 }
  | production2 { action2 }
  | ...
  ;
```

*产生式*是规则匹配的*符号*序列。一个符号是
令牌或另一个规则的名称。 *action* 是 OCaml 值
如果发生*匹配*则返回。每个产生式都可以*绑定*由a所携带的值
符号并在其操作中使用该值。这也许是最好的理解
例如，让我们深入探讨一下。

第一条规则名为 `prog`，只有一个产生式。它说一个
`prog` 是 `expr` 后跟 `EOF`。第一部分的制作，
`e=expr`，表示匹配 `expr` 并将结果值绑定到 `e`。
操作只是说返回该值 `e`。

```text
prog:
  | e = expr; EOF { e }
  ;
```


第二个也是最后一个规则，名为 `expr`，具有所有表达式的产生式
在 SimPL 中。

```text
expr:
  | i = INT { Int i }
  | x = ID { Var x }
  | TRUE { Bool true }
  | FALSE { Bool false }
  | e1 = expr; LEQ; e2 = expr { Binop (Leq, e1, e2) }
  | e1 = expr; TIMES; e2 = expr { Binop (Mult, e1, e2) }
  | e1 = expr; PLUS; e2 = expr { Binop (Add, e1, e2) }
  | LET; x = ID; EQUALS; e1 = expr; IN; e2 = expr { Let (x, e1, e2) }
  | IF; e1 = expr; THEN; e2 = expr; ELSE; e3 = expr { If (e1, e2, e3) }
  | LPAREN; e=expr; RPAREN {e}
  ;
```

- 第一个产生式 `i = INT` 表示要匹配 `INT` 令牌，绑定
将结果 OCaml `int` 值设置为 `i`，并返回 AST 节点 `Int i`。

- 第二个产生式 `x = ID` 表示要匹配 `ID` 令牌，绑定
将结果 OCaml `string` 值设置为 `x`，并返回 AST 节点 `Var x`。

- 第三和第四个产生式匹配 `TRUE` 或 `FALSE` 令牌并返回
对应的 AST 节点。

- 第五、第六和第七产生式处理二元运算符。对于
例如， `e1 = expr; PLUS; e2 = expr` 表示匹配 `expr` 后跟
  `PLUS` 令牌后跟另一个 `expr`。第一个 `expr` 绑定到 `e1` 并且
  第二个到`e2`。返回的 AST 节点是 `Binop (Add, e1, e2)`。

- 第八个作品，`LET; x = ID; EQUALS; e1 = expr; IN; e2 = expr`，说
匹配 `LET` 令牌，后跟 `ID` 令牌，后跟 `EQUALS` 令牌
  后跟 `expr` ，后跟 `IN` 令牌，后跟另一个 `expr` 。
  `ID` 携带的字符串与 `x` 绑定，两个表达式为
  绑定到 `e1` 和 `e2`。返回的 AST 节点是 `Let (x, e1, e2)`。

- 最后一个作品，`LPAREN; e = expr; RPAREN` 表示要匹配 `LPAREN`
令牌后跟 `expr` 后跟 `RPAREN`。表达式已绑定
  到 `e` 并返回。

最终的结果可能会令人惊讶，因为它没有包含在 BNF 中
我们为 SimPL 编写。 BNF 旨在描述“抽象语法”
语言，因此它不包括表达式如何实现的具体细节
用括号分组。但我们一直在写的语法定义确实
必须描述*具体语法*，包括括号等细节。

规则后面还可以有一个 *trailer* 部分，就像标题一样
直接复制到输出 `parser.ml` 文件中的 OCaml 代码。

### OCamllex 词法分析器

现在让我们看看如何使用词法分析器生成器。很多都会有似曾相识的感觉
来自我们对解析器生成器的讨论。我们将把所有的 ocamllex 代码
在名为 `lexer.mll` 的文件中写入以下内容。 `.mll` 扩展名表明
该文件旨在作为 ocamllex 的输入。 （“l”暗示词法分析。）
文件包含我们想要 lex 的语言的 *lexer 定义*。门希尔
将处理该文件并生成一个名为 `lexer.ml` 的文件作为输出；它
包含一个对该语言进行词法分析的 OCaml 程序。 （没有什么特别的
关于名字 `lexer` 在这里；这只是描述性的。）

词法分析器定义由四个部分组成：标头、标识符、规则和
拖车。

**标头。** *标头* 出现在 `{` 和 `}` 之间。这是代码
只需按字面复制到生成的 `lexer.ml` 中即可。

```text
{
open Parser
}
```

在这里，我们打开了 `Parser` 模块，这是 `parser.ml` 中的代码
由 Menhir 根据 `parser.mly` 制作。我们打开它的原因是为了让我们
可以使用其中声明的令牌名称，例如 `TRUE`、`LET` 和 `INT`。
我们的词法分析器定义。否则，我们必须写 `Parser.TRUE` 等。

**标识符。** 词法分析器定义的下一部分包含
*标识符*，称为正则表达式。这些将用于
规则部分，接下来。

以下是我们将在 SimPL 中使用的标识符：

```text
let white = [' ' '\t']+
let digit = ['0'-'9']
let int = '-'? digit+
let letter = ['a'-'z' 'A'-'Z']
let id = letter+
```

上面的正则表达式适用于空白（空格和制表符）、数字（0
到 9），整数（非空数字序列，前面可以选择
减号）、字母（a 到 z 以及 A 到 Z）和 SimPL 变量名称
（非空字母序列）又名 ids 或“标识符”&mdash;尽管我们
现在这个词有两种不同的含义。

仅供参考，这些与整数和 OCaml 的定义并不完全相同
标识符。

标识符部分实际上不是必需的；而不是在中写入 `white`
规则我们直接写正则表达式就可以了。但是
标识符有助于使词法分析器定义更加自文档化。

**规则。** 词法分析器定义的规则部分以以下符号编写：
也类似于 BNF。规则的形式为

```text
rule name =
  parse
  | regexp1 { action1 }
  | regexp2 { action2 }
  | ...
```
这里，`rule` 和 `parse` 是关键字。生成的词法分析器将尝试
按照正则表达式的列出顺序进行匹配。当一个
正则表达式匹配，词法分析器生成由其指定的标记
`action`。

这是 SimPL 词法分析器的（唯一）规则：

```text
rule read =
  parse
  | white { read lexbuf }
  | "true" { TRUE }
  | "false" { FALSE }
  | "<=" { LEQ }
  | "*" { TIMES }
  | "+" { PLUS }
  | "(" { LPAREN }
  | ")" { RPAREN }
  | "let" { LET }
  | "=" { EQUALS }
  | "in" { IN }
  | "if" { IF }
  | "then" { THEN }
  | "else" { ELSE }
  | id { ID (Lexing.lexeme lexbuf) }
  | int { INT (int_of_string (Lexing.lexeme lexbuf)) }
  | eof { EOF }
```

大多数正则表达式和操作都是不言自明的，但有几个
不是：

* 第一个 `white { read lexbuf }` 意味着如果空格匹配，
词法分析器应该再次调用 `read` 规则，而不是返回令牌
  并返回任何标记结果。换句话说，空白将被跳过。

* id 和 int 的两个使用表达式 `Lexing.lexeme lexbuf`。这调用
`Lexing` 模块中定义的函数 `lexeme`，并返回字符串
  与正则表达式匹配。例如，在 `id` 规则中，它将
  返回构成变量的大小写字母序列
  名字。

* `eof` 正则表达式是一种特殊的正则表达式，它匹配文件末尾
（或字符串）被词法分析。

请注意，重要的是 `id` 正则表达式几乎出现在
名单。否则，像 `true` 和 `if` 这样的关键字将被词法为变量
名称而不是 `TRUE` 和 `IF` 标记。

### 生成解析器和词法分析器

现在我们已经完成了 `parser.mly` 中的解析器和词法分析器定义，并且
`lexer.mll`，我们可以运行 Menhir 和 ocamllex 来生成解析器和词法分析器
来自他们。让我们这样组织我们的代码：
```text
- <some root folder>
  - dune-project
  - src
    - ast.ml
    - dune
    - lexer.mll
    - parser.mly
```

在 `src/dune` 中写入以下内容：
```text
(library
 (name interp))

(menhir
 (modules parser))

(ocamllex lexer)
```

这会将整个 `src` 文件夹组织到一个名为 `Interp` 的*库*中。
解析器和词法分析器将是模块 `Interp.Parser` 和 `Interp.Lexer`
库。

运行 `dune build` 编译代码，从而生成解析器和词法分析器。如果
你想查看生成的代码，请在 `_build/default/src/` 中查找
`parser.ml` 和 `lexer.ml`。

### 驱动程序

最后，我们可以将词法分析器和解析器结合在一起，将字符串转换为字符串
AST。将此代码放入名为 `src/main.ml` 的文件中：

```ocaml
open Ast

let parse (s : string) : expr =
  let lexbuf = Lexing.from_string s in
  let ast = Parser.prog Lexer.read lexbuf in
  ast
```

该函数采用字符串 `s` 并使用标准库的 `Lexing` 模块
从中创建一个*词法分析器缓冲区*。将该缓冲区视为令牌流。
然后，该函数使用 `Lexer.read` 将字符串词法分析并解析为 AST
和`Parser.prog`。函数 `Lexer.read` 对应于名为
`read` 在我们的词法分析器定义中，函数 `Parser.prog` 对应于名为
`prog` 在我们的解析器定义中。

请注意此代码如何在字符串上运行词法分析器；有对应的函数
`from_channel` 从文件中读取。

我们现在可以交互地使用 `parse` 来解析一些字符串。  启动乌托普
并使用以下命令加载 `src` 中声明的库：

```console
$ dune utop src
```

现在 `Interp.Main.parse` 可供使用：

```ocaml
# Interp.Main.parse "let x = 3110 in x + x";;
- : Interp.Ast.expr =
Interp.Ast.Let ("x", Interp.Ast.Int 3110,
 Interp.Ast.Binop (Interp.Ast.Add, Interp.Ast.Var "x", Interp.Ast.Var "x"))
```

这就完成了 SimPL 的词法分析和解析。
