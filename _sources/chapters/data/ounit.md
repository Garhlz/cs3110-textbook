# 使用 OUnit 进行单元测试

```{note}
本节与我们对数据类型的研究略有偏离，但这是一个很合适的
插入点：我们现在已经知道足够多的内容，可以理解如何在 OCaml 中
进行单元测试，没有必要再推迟学习它。
```

使用顶层来测试函数仅适用于非常小的程序。
较大的程序需要包含许多“单元测试”的“测试套件”，并且可以
每次我们更新代码库时都会重新运行。单元测试是对一个小的测试
程序中的一部分函数，例如单个函数。

我们现在已经了解了足够多的 OCaml 特性，可以学习如何使用
名为 OUnit 的库。它是一个单元测试框架，类似于 Java 中的 JUnit、
Haskell 中的 HUnit 等。使用 OUnit 的基本工作流程如下：

* 在文件 `f.ml` 中编写一个函数。里面可能还有很多其他的函数
文件也。

* 在单独的文件 `test.ml` 中编写该函数的单元测试。这个具体
文件名其实并不重要。

* 构建并运行 `test` 以执行单元测试。

[OUnit 文档][ounitdoc] 可在 GitHub 上找到。

[ounitdoc]: https://gildor478.github.io/ounit/ounit2/index.html

## OUnit 的示例

以下示例展示如何创建 OUnit 测试套件。
示例中的某些内容乍看可能有些神秘；这些内容
会在下一节中讨论。

创建一个新目录。在该目录中，创建一个名为 `sum.ml` 的文件，并将
将以下代码写入其中：
```ocaml
let rec sum = function
  | [] -> 0
  | x :: xs -> x + sum xs
```

现在创建第二个名为 `test.ml` 的文件，并将以下代码放入其中：
```ocaml
open OUnit2
open Sum

let tests = "test suite for sum" >::: [
  "empty" >:: (fun _ -> assert_equal 0 (sum []));
  "singleton" >:: (fun _ -> assert_equal 1 (sum [1]));
  "two_elements" >:: (fun _ -> assert_equal 3 (sum [1; 2]));
]

let _ = run_test_tt_main tests
```

根据你的编辑器及其配置，你现在可能会看到一些
关于 OUnit2 和 Sum 的“未绑定模块”错误。不用担心；代码实际上是
正确的。我们只需要设置 Dune，并告诉它链接 OUnit。创建一个 `dune`
文件并将其放入其中：

```text
(executable
 (name test)
 (libraries ounit2))
```

并像往常一样创建一个 `dune-project` 文件：

```text
(lang dune 3.4)
```

现在构建测试套件：

```console
$ dune build test.exe
```

返回到你的编辑器并执行任何会导致其重新访问 `test.ml` 的操作。
你可以关闭并重新打开窗口，或者对文件进行一些简单的更改
（例如，添加然后删除空格）。现在错误应该全部消失。

最后，你可以运行测试套件：

```console
$ dune exec ./test.exe
```

你将得到如下响应：

```text
...
Ran: 3 tests in: 0.12 seconds.
OK
```

现在假设我们修改 `sum.ml` 通过更改代码来引入错误
其中包含以下内容：
```ocaml
let rec sum = function
  | [] -> 1 (* bug *)
  | x :: xs -> x + sum xs
```

如果重建并重新执行测试套件，所有测试用例现在都会失败。输出
会告诉我们失败测试用例的名称。下面是输出的开头，
其中一些取决于你本地计算机的字符串已经被替换为 `...`：
```
FFF
==============================================================================
Error: test suite for sum:2:two_elements.

File ".../_build/oUnit-test suite for sum-...#01.log", line 9, characters 1-1:
Error: test suite for sum:2:two_elements (in the log).

Raised at OUnitAssert.assert_failure in file "src/lib/ounit2/advanced/oUnitAssert.ml", line 45, characters 2-27
Called from OUnitRunner.run_one_test.(fun) in file "src/lib/ounit2/advanced/oUnitRunner.ml", line 83, characters 13-26

not equal
------------------------------------------------------------------------------
```

该输出的第一行
```
FFF
```
告诉我们 OUnit 运行了三个测试用例，并且所有三个 <u>f</u>ailed。

下一个有趣的行
```
Error: test suite for sum:2:two_elements.
```
告诉我们，在名为 `test suite for sum` 的测试套件中，测试用例位于
名为 `two_elements` 的索引 2 失败。该测试用例的其余输出
不是特别有趣；我们暂时忽略它。

## OUnit 示例的说明

让我们更仔细地研究一下我们在上一节中所做的事情。在测试中
文件中，`open OUnit2` 会把 OUnit2 中的许多定义引入作用域，
OUnit2 是 OUnit 框架的版本 2。`open Sum` 则会引入
来自 `sum.ml` 的定义。我们将了解有关作用域和 `open` 关键字的更多信息
稍后在后面的章节中。

然后我们创建了一个测试用例列表：
```ocaml
[
  "empty"  >:: (fun _ -> assert_equal 0 (sum []));
  "one"    >:: (fun _ -> assert_equal 1 (sum [1]));
  "onetwo" >:: (fun _ -> assert_equal 3 (sum [1; 2]));
]
```
每行代码都是一个单独的测试用例。测试用例包含一个字符串，
作为描述性名称；还包含一个函数，作为测试用例运行。
名称和我们编写的函数之间的 `>::` 是 OUnit 框架定义的自定义运算符。
让我们看一下上面的第一个函数：
```
fun _ -> assert_equal 0 (sum [])
```
每个测试用例函数都会接收 OUnit 调用的 *test context* 作为输入。
在这里（以及我们编写的许多测试用例中）我们实际上不需要
担心上下文，所以我们使用下划线来表示
函数忽略其输入。然后该函数调用 `assert_equal`，这是一个
OUnit 提供的函数，用于检查其两个参数是否相等。
如果相等，则测试用例成功；否则测试用例失败。

然后我们创建了一个测试套件：
```ocaml
let tests = "test suite for sum" >::: [
  "empty" >:: (fun _ -> assert_equal 0 (sum []));
  "singleton" >:: (fun _ -> assert_equal 1 (sum [1]));
  "two_elements" >:: (fun _ -> assert_equal 3 (sum [1; 2]));
]
```

`>:::` 运算符是另一个自定义 OUnit 运算符。它位于名字之间
测试套件的名称以及该套件中的测试用例列表。

然后我们运行测试套件：
```ocaml
let _ = run_test_tt_main tests
```

函数 `run_test_tt_main` 由 OUnit 提供。它运行一个测试套件并
把哪些测试用例通过、哪些测试用例失败的结果打印到标准输出。
这里使用 `let _ = ` 表明我们不关心该值是什么
函数返回；它只是被丢弃。

## 改进 OUnit 输出

在我们的 `sum` 实现有缺陷的示例中，我们得到以下结果
输出：

```
==============================================================================
Error: test suite for sum:2:two_elements.
...
not equal
------------------------------------------------------------------------------
```

OUnit 输出中的 `not equal` 意味着 `assert_equal` 发现了这两个
在该测试用例中传递给它的值不相等。这不是那么有用：
我们想知道*为什么*它们不相等。我们特别想知道什么
`sum` 产生的实际输出是针对该测试用例的。为了找出答案，我们需要
将附加参数传递给 `assert_equal`。这个参数的标签是
`printer`，应该是一个可以将输出转换为字符串的函数。在
在这种情况下，输出是整数，因此来自 `Stdlib` 模块的 `string_of_int`
就足够了。我们将测试套件修改如下：

```ocaml
let tests = "test suite for sum" >::: [
  "empty" >:: (fun _ -> assert_equal 0 (sum []) ~printer:string_of_int);
  "singleton" >:: (fun _ -> assert_equal 1 (sum [1]) ~printer:string_of_int);
  "two_elements" >:: (fun _ -> assert_equal 3 (sum [1; 2]) ~printer:string_of_int);
]
```

现在我们得到更多信息输出：
```
==============================================================================
Error: test suite for sum:2:two_elements.
...
expected: 3 but got: 4
------------------------------------------------------------------------------
```

该输出意味着名为 `two_elements` 的测试断言以下内容相等
`3` 和 `4`。预期输出是 `3` 因为这是第一个输入
`assert_equal`，该函数的规范指出
`assert_equal x y`，你（作为测试人员）期望获得的输出应该
是 `x`，被测试的函数实际产生的输出应该是
`y`。

请注意我们的测试套件如何积累大量冗余代码。在
特别是，我们必须将 `printer` 参数添加到几行中。让我们改进一下
该代码通过分解出构建测试用例的函数来实现：

```ocaml
let make_sum_test name expected_output input =
  name >:: (fun _ -> assert_equal expected_output (sum input) ~printer:string_of_int)

let tests = "test suite for sum" >::: [
  make_sum_test "empty" 0 [];
  make_sum_test "singleton" 1 [1];
  make_sum_test "two_elements" 3 [1; 2];
]
```

对于比整数更复杂的输出类型，你最终会得到
需要编写自己的函数来传递给 `printer`。这类似于
用 Java 编写 `toString()` 方法：对于你自己发明的复杂类型，
该语言不知道如何将它们呈现为字符串。你必须提供
执行此操作的代码。

## 测试异常

在了解如何测试异常之前，我们还需要学习更多 OCaml 知识。
如果你现在就想知道，可以提前查看 [异常一节](exceptions)。

## 测试驱动开发

测试不一定只能在编写代码之后进行。在*测试驱动开发*
(TDD) 中，测试先行。它强调*增量式*开发代码：
总会有一些东西可以测试。测试不是实现完成之后才发生的事情；
相反，*持续测试*用于及早发现错误。因此，一旦写出代码，
就立即编写单元测试非常重要。自动化测试套件也至关重要，
这样持续测试几乎不需要额外工作。

下面是一个 TDD 示例。为了让流程清楚，我们故意选择一个
极其简单的函数来实现。假设我们正在处理一个表示星期几的数据类型：

```ocaml
type day = Sunday | Monday | Tuesday | Wednesday | Thursday | Friday | Saturday
```
我们想要编写函数 `next_weekday : day -> day`，
返回指定日期之后的下一个工作日。我们从能写出的最简单、
但尚未实现的版本开始：
```ocaml
let next_weekday d = failwith "Unimplemented"
```

```{note}
内置函数 `failwith` 会引发异常，并把错误消息传给该异常。
```

然后我们编写我们能想象到的最简单的单元测试。例如，我们知道
星期一之后的下一个工作日是星期二。所以我们添加一个测试：

```ocaml
let tests = "test suite for next_weekday" >::: [
  "tue_after_mon"  >:: (fun _ -> assert_equal Tuesday (next_weekday Monday));
]
```

然后我们运行 OUnit 测试套件。正如预期的那样，它失败了。那挺好的！现在我们
有一个具体的目标，让单元测试通过。我们将 `next_weekday` 修改为
实现这一点：

```ocaml
let next_weekday d =
  match d with
  | Monday -> Tuesday
  | _ -> failwith "Unimplemented"
```

我们编译并运行测试；它通过了。现在该添加更多测试了。
剩下的最简单的可能性是仅涉及工作日的测试，而不是
周末。因此，让我们添加工作日的测试。
```ocaml
let tests = "test suite for next_weekday" >::: [
  "tue_after_mon"  >:: (fun _ -> assert_equal Tuesday (next_weekday Monday));
  "wed_after_tue"  >:: (fun _ -> assert_equal Wednesday (next_weekday Tuesday));
  "thu_after_wed"  >:: (fun _ -> assert_equal Thursday(next_weekday Wednesday));
  "fri_after_thu"  >:: (fun _ -> assert_equal Friday (next_weekday Thursday));
]
```

我们编译并运行测试；其中许多失败了。这很好。我们添加新的
情况：

```ocaml
  let next_weekday d =
    match d with
    | Monday -> Tuesday
    | Tuesday -> Wednesday
    | Wednesday -> Thursday
    | Thursday -> Friday
    | _ -> failwith "Unimplemented"
```

我们编译并运行测试；它们通过了。此时我们可以继续
处理周末，但应该先注意到我们已经写好的测试：
它们包含大量重复代码。事实上，我们可能就是通过复制粘贴第一个测试，
再修改接下来的三个测试来写出它们的。
这表明我们应该“重构”代码。 （正如我们之前所做的那样
我们正在测试 `sum` 函数。）

让我们抽象一个为 `next_weekday` 创建测试用例的函数：
```ocaml
let make_next_weekday_test name expected_output input =
  name >:: (fun _ -> assert_equal expected_output (next_weekday input))

let tests = "test suite for next_weekday" >::: [
  make_next_weekday_test "tue_after_mon" Tuesday Monday;
  make_next_weekday_test "wed_after_tue" Wednesday Tuesday;
  make_next_weekday_test "thu_after_wed" Thursday Wednesday;
  make_next_weekday_test "fri_after_thu" Friday Thursday;
]
```

现在我们通过处理周末来完成测试和实现。首先我们添加
一些测试用例：
```ocaml
  ...
  make_next_weekday_test "mon_after_fri" Monday Friday;
  make_next_weekday_test "mon_after_sat" Monday Saturday;
  make_next_weekday_test "mon_after_sun" Monday Sunday;
  ...
```

然后我们完成这个函数：

```ocaml
let next_weekday d =
  match d with
  | Monday -> Tuesday
  | Tuesday -> Wednesday
  | Wednesday -> Thursday
  | Thursday -> Friday
  | Friday -> Monday
  | Saturday -> Monday
  | Sunday -> Monday
```

当然，即使不使用 TDD，大多数人也能毫无错误地写出这个函数。
但我们很少只实现这么简单的函数。

**流程。** 我们回顾一下 TDD 的流程：

- 编写失败的单元测试用例。运行测试套件以证明测试用例
失败。

- 实现足够的功能，使测试用例通过。运行测试
套件来证明测试用例通过。

- 根据需要改进代码。在上面的示例中，我们重构了测试套件，但是
通常我们需要重构正在实现的函数。

- 重复上述过程，直到测试套件提供的证据足以让你相信
实现是正确的。
