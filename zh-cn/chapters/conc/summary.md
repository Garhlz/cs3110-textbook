# 总结

并发编程具有挑战性，这也许可以解释为什么有这么多不同的库和语言特性支持它。
Promise 在函数式和命令式编程中都优雅且有用。
但它们并不是终点：
OCaml 5 最近添加了基于*域*和线程的并行性和并发性的新机制。
你可能会发现阅读 OCaml 手册中有关这些内容的更多信息很有趣。

## 术语和概念

* 异步
* 绑定
* 阻塞
* 回调
* 通道
* 计算
* 并发
* 并行组合
* 协作式
* 确定性
* 效果
* 交错
* 延迟隐藏
* 左单位元
* Lwt Monad
* Maybe Monad
* 单子
* Monad 定律
* 非阻塞
* 非确定性
* 并行性
* 待处理
* 抢占式
* Promise
* 竞争条件
* 被拒绝
* 解析循环
* 已解决
* 解析器
* 右单位元
* 顺序的
* 顺序组合
* 标准输入
* 标准输出
* 同步的
* 线程
* Writer Monad

## 进一步阅读

* *现实世界 OCaml*，第 16 章

* [Lwt 手册](https://ocsigen.org/lwt/latest/manual/manual)

* [OCaml 5 Manual, "Parallel Programming"](https://ocaml.org/manual/latest/parallelism.html)
