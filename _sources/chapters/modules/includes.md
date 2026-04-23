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

# Include

{{ video_embed | replace("%%VID%%", "SmG3ChuOLpQ")}}

复制和粘贴代码几乎总是一个坏主意。重复代码会让错误也被重复并扩散。
那么我们为什么还是这么容易犯这个错误？也许是因为它看起来总是更轻松：
比起应用抽象原则、抽取通用代码，复制粘贴显得更快也更省事。

OCaml 模块系统提供了一个名为 *include* 的简洁特性。
它像是一种有原则的复制粘贴：快速、易用，但避免了真正的重复。
它可以解决一些在面向对象语言中通常由*继承*解决的问题。

让我们从一个例子开始。回想一下集合作为列表的实现：

```{code-cell} ocaml
:tags: ["hide-output"]
module type Set = sig
  type 'a t
  val empty : 'a t
  val mem : 'a -> 'a t -> bool
  val add : 'a -> 'a t -> 'a t
  val elements : 'a t -> 'a list
end

module ListSet : Set = struct
  type 'a t = 'a list
  let empty = []
  let mem = List.mem
  let add = List.cons
  let elements s = List.sort_uniq Stdlib.compare s
end
```

假设我们想添加一个函数 `of_list : 'a list -> 'a t` ，它可以
从列表中构造一个集合。如果我们能够访问两者的源代码
`ListSet` 和 `Set`，如果我们被允许修改它，这将不会是
很难。但是如果它们是我们没有的第三方库怎么办
源代码？

在 Java 中，我们可以使用继承来解决这个问题：

```java
interface Set<T> { ... }
class ListSet<T> implements Set<T> { ... }
class ListSetExtended<T> extends ListSet<T> {
  Set<T> ofList(List<T> lst) { ... }
}
```

这有助于我们重用代码，因为子类继承了所有的方法
它的超类。

OCaml 的 *include* 与此类似。它让一个模块能够包含另一个模块定义的所有项，
也让一个模块类型能够包含另一个模块类型给出的所有规格说明。

下面是我们如何使用 `include` 来解决添加 `of_list` 的问题
`ListSet`：

```{code-cell} ocaml
module ListSetExtended = struct
  include ListSet
  let of_list lst = List.fold_right add lst empty
end
```

这段代码表示 `ListSetExtended` 是一个包含所有
`ListSet` 模块的定义，以及 `of_list` 的定义。我们
不必知道实现 `ListSet` 的源代码即可实现此目的。

```{note}
你可能想知道为什么我们不能简单地实现 `of_list` 作为身份
函数。请参阅下面有关封装的部分以获得答案。
```

## Include 的语义

包含可以在结构和签名内部使用。当我们包含在里面时
一个签名，我们必须包含另一个签名。当我们包括在内
一个结构，我们必须包含另一个结构。

**包含一个结构**实际上只是编写一个语法糖
模块中定义的每个名称的本地定义。写入 `include ListSet`
例如，正如我们上面所做的那样，其效果类似于编写以下内容：

```{code-cell} ocaml
module ListSetExtended = struct
  (* BEGIN all the includes *)
  type 'a t = 'a ListSet.t
  let empty = ListSet.empty
  let mem = ListSet.mem
  let add = ListSet.add
  let elements = ListSet.elements
  (* END all the includes *)
  let of_list lst = List.fold_right add lst empty
end
```
这些实际上都不是复制 `ListSet` 的源代码。相反，
`include` 只是在 `ListSetExtended` 中创建一个同名的新定义
正如 `ListSet` 中的每个定义。但是如果里面定义的一组名称
`ListSet` 发生变化时， `include` 将反映该变化，而
复制粘贴工作不会。

**包括签名**大致相同。例如，我们可以写：

```{code-cell} ocaml
module type SetExtended = sig
  include Set
  val of_list : 'a list -> 'a t
end
```

这将产生类似于编写以下内容的效果：

```{code-cell} ocaml
module type SetExtended = sig
  (* BEGIN all the includes *)
  type 'a t
  val empty : 'a t
  val mem : 'a -> 'a t -> bool
  val add : 'a -> 'a t -> 'a t
  val elements  : 'a t -> 'a list
  (* END all the includes *)
  val of_list : 'a list -> 'a t
end
```

该模块类型适合 `ListSetExtended`：

```{code-cell} ocaml
module ListSetExtended : SetExtended = struct
  include ListSet
  let of_list lst = List.fold_right add lst empty
end
```

## 封装和 Include

我们上面提到过，你可能想知道为什么我们不写得更简单一些
`of_list` 的定义：

```{code-cell} ocaml
:tags: ["raises-exception"]
module ListSetExtended : SetExtended = struct
  include ListSet
  let of_list lst = lst
end
```

查看该错误消息。  看起来 `of_list` 没有权限
类型。  如果我们尝试添加一些类型注释怎么办？

```{code-cell} ocaml
:tags: ["raises-exception"]
module ListSetExtended : SetExtended = struct
  include ListSet
  let of_list (lst : 'a list) : 'a t = lst
end
```

啊，现在问题更清楚了：在`of_list`的主体中，`'a t`的相等性
并且 `'a list` 未知。在 `ListSetExtended` 中，我们确实知道
`'a t = 'a ListSet.t`，因为这就是 `include` 给我们的。但事实
当 `ListSet` 被密封在模块中时，`'a ListSet.t = 'a list` 被隐藏
输入 `Set`。因此，包含必须服从封装，就像其余的一样
模块系统。

一种解决方法是重写定义，如下所示：

```{code-cell} ocaml
module ListSetImpl = struct
  type 'a t = 'a list
  let empty = []
  let mem = List.mem
  let add = List.cons
  let elements s = List.sort_uniq Stdlib.compare s
end

module ListSet : Set = ListSetImpl

module type SetExtended = sig
  include Set
  val of_list : 'a list -> 'a t
end

module ListSetExtendedImpl = struct
  include ListSetImpl
  let of_list lst = lst
end

module ListSetExtended : SetExtended = ListSetExtendedImpl
```

重要的变化是 `ListSetImpl` 没有被密封，所以它的类型 `'a t` 是
不抽象。当我们将其包含在 `ListSetExtended` 中时，我们就可以利用
事实上它是 `'a list` 的同义词。

我们刚才所做的实际上与 Java 处理
可见性修饰符 `public`、`private` 等。类的“私有版本”
就像上面的 `Impl` 版本：任何可以看到该版本的人都可以看到
所有公开的项目（Java 中的字段、OCaml 中的类型），没有任何
封装。类的“公共版本”就像上面的密封版本：
任何可以看到该版本的人都被迫将这些项目视为抽象的，因此
封装的。

通过这种技术，如果我们想提供其中一个的新实现
我们也可以这样做：

```{code-cell} ocaml
module ListSetExtendedImpl = struct
  include ListSetImpl
  let of_list lst = List.fold_right add lst empty
  let rec elements = function
    | [] -> []
    | h :: t -> if mem h t then elements t else h :: elements t
end
```

但这是个坏主意。首先，它实际上是一个二次实现
`elements` 而不是线性。其次，它不会“取代”原来的
`elements` 的实现。记住模块的语义：所有定义
按从上到下的顺序进行评估。所以 `elements` 的新定义
以上要等到评估结束后才能使用。如果有更早的
函数碰巧使用 `elements` 作为辅助函数，它们会使用
原始的线性版本，而不是新的二次版本。

```{warning}
这不同于你在 Java 中可能期待的行为；Java 使用一种语言特性
调用 [dynamic dispatch][dd] 来确定要执行哪个方法实现
调用。动态调度可以说是面向对象的*定义*特征
语言。 OCaml 函数不是方法，并且它们不使用动态
派遣。
```

[dd]: https://en.wikipedia.org/wiki/Dynamic_dispatch


## Include 与 Open

{{ video_embed | replace("%%VID%%", "P1-gLiagAK4")}}

`include` 和 `open` 语句非常相似，但它们有
对结构的影响略有不同。  考虑这段代码：

```{code-cell} ocaml
module M = struct
  let x = 0
end

module N = struct
  include M
  let y = x + 1
end

module O = struct
  open M
  let y = x + 1
end
```

仔细查看每个结构中包含的值。 `N` 具有 `x` 和
`y`，而 `O` 只有一个 `y`。原因是 `include M` 导致所有
`M` 的定义也包含在 `N` 中，因此 `x` 的定义来自 `M`
存在于 `N` 中。但 `open M` 仅使这些定义在
`O` 的*范围*；它实际上并没有使它们成为*结构*的一部分。所以`O`
不包含 `x` 的定义，即使 `x` 在
`O` 对 `y` 的定义的评估。

理解这种差异的隐喻可能是： `open M` 导入
`M` 中的定义并使其可供本地使用，但它们
不出口到外界。而 `include M` 导入定义
来自 `M`，使它们可供当地消费，并另外出口
他们对外面的世界。

## 在多个模块中包含代码

回想一下，我们还有一个集合的实现，它确保每个元素
底层列表是唯一的：

```{code-cell} ocaml
module UniqListSet : Set = struct
  (** All values in the list must be unique. *)
  type 'a t = 'a list
  let empty = []
  let mem = List.mem
  let add x s = if mem x s then s else x :: s
  let elements = Fun.id
end
```

假设我们也想将 `of_list` 添加到该模块。一种可能性是
将该函数从 `ListSet` 复制并粘贴到 `UniqListSet` 中。但这是很糟糕的
软件工程。因此，让我们立即把它排除为非解决方案。

相反，假设我们尝试在任一模块之外定义该函数：

```{code-cell} ocaml
:tags: ["raises-exception"]
let of_list lst = List.fold_right add lst empty
```

问题是我们要么需要选择哪个模块的 `add` 和 `empty` 我们
想要。但一旦我们这样做了，这个函数就只对那个函数有用了
模块：

```{code-cell} ocaml
let of_list lst = List.fold_right ListSet.add lst ListSet.empty
```

我们可以将 `add` 和 `empty` 作为参数：

```{code-cell} ocaml
let of_list' add empty lst = List.fold_right add lst empty

let of_list lst = of_list' ListSet.add ListSet.empty lst
let of_list_uniq lst = of_list' UniqListSet.add UniqListSet.empty lst
```

但这在几个方面都很烦人。首先我们要记住是哪一个
要调用的函数名称，而属于这些函数一部分的所有其他操作
模块具有相同的名称，无论它们位于哪个模块中。
`of_list` 函数位于任一模块之外，因此打开其中一个模块的客户端
模块不会自动获得命名这些函数的能力。

我们尝试使用include来解决这个问题。首先，我们编写一个模块
包含参数化实现：

```{code-cell} ocaml
module SetOfList = struct
  let of_list' add empty lst = List.fold_right add lst empty
end
```

然后我们包含该模块来获取辅助函数：

```{code-cell} ocaml
module UniqListSetExtended : SetExtended = struct
  include UniqListSet
  include SetOfList
  let of_list lst = of_list' add empty lst
end

module ListSetExtended : SetExtended = struct
  include ListSet
  include SetOfList
  let of_list lst = of_list' add empty lst
end
```

这可行，但我们只部分成功地实现了代码重用：

- 从积极的一面来看，实现 `of_list'` 的代码已被考虑在内
放入一个位置并在两个结构中重复使用。

- 但不利的一面是，我们仍然必须编写 `of_list` 的实现
在两个模块中。更糟糕的是，这些实现是相同的。所以有
  仍然发生代码重复。

我们可以做得更好吗？是的。接下来我们就到了函子。
