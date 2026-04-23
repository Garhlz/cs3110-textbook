# 总结

本章是本书中最重要的章节之一。它没有介绍任何新的语言特性。
相反，我们学习了如何以可能新颖、令人惊讶或具有挑战性的方式
使用一些已有特性。高阶编程和抽象原则这两个思想
将帮助你成为更好的程序员，不仅限于 OCaml。当然，
不同语言支持这些思想的程度确实不同，有些语言对编写高阶代码的
帮助要少得多&mdash;这也是我们在这门课中使用 OCaml 的原因之一。

`map`、`filter`、`fold` 和其他函数已经被广泛认为是
构建计算的优秀方式。部分原因是它们把数据结构上的*迭代*
从对每个元素执行的*计算*中分离出来。Python、Ruby 和 Java 8 等语言现在支持
这种迭代。

## 术语和概念

* 抽象原则
* 累加器
* 应用
* 结合性
* 组合
* 提取因子
* `filter`
* 一阶函数
* `fold`
* 函数式的
* 广义折叠操作
* 高阶函数
* `map`
* 管道
* 流水线

## 进一步阅读

* *Objective Caml 简介*，第 3.1.3、5.3 章
* *从一开始的 OCaml*，第 6 章
* *更多 OCaml：算法、方法和转移*，第 1 章，作者：John
惠廷顿。本书是《OCaml from the Very Beginning》的续集。
* *真实世界 OCaml*，第 3 章（请注意，本书的 `Core` 库有一个
与标准库的 `List` 模块不同的 `List` 模块，
  `map` 和 `fold` 的类型与我们在这里看到的类型不同）
* “高阶函数”，*函数式编程：练习和第 6 章
理论*。 Bruce J. MacLennan，Addison-Wesley，1990。我们的讨论
  高阶函数和抽象原则归功于此
  章。
* “编程能否从冯·诺依曼风格中解放出来？函数式风格
及其程序代数。”约翰·巴克斯 1977 年图灵奖演讲
  详细形式为 [published article][backus-turing]。
* *斯坦福百科全书中的“[Second-order and Higher-order Logic][solhol]”
哲学*。

[solhol]:  http://plato.stanford.edu/entries/logic-higher-order/
[backus-turing]: https://dl.acm.org/doi/pdf/10.1145/359576.359579
