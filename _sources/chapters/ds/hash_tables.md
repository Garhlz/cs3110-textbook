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

# 哈希表

*哈希表*是一种广泛使用的数据结构，其性能依赖于可变性。
与到目前为止我们实现过的其他数据结构相比，哈希表的实现相当复杂。
我们会慢慢搭建它，以便理解每个部分的需求和用途。

## 映射

{{ video_embed | replace("%%VID%%", "hr8SmQK8ld8")}}

{{ video_embed | replace("%%VID%%", "I5E_BPkE_fE")}}

哈希表实现了 *map* 数据抽象。映射将*键*绑定到*值*。
这种抽象非常有用，以至于它有许多其他名称，其中
它们是*关联数组*、*字典*和*符号表*。我们会写映射
抽象地（即数学上；实际上不是 OCaml 语法）为 { $k_1 : v_1,
k_2: v_2, \ldots, k_n : v_n$ }。每个 $k : v$ 都是一个*绑定*，
把键 $k$ 绑定到值 $v$。这里有几个例子：

* 将课程编号与相关内容绑定的映射：{3110：“Fun”，2110：
“哦”}。

* 将大学名称与其成立年份绑定的映射：{“哈佛”：1636，
“普林斯顿大学”：1746，“宾夕法尼亚大学”：1740，“康奈尔大学”：1865}。

绑定的抽象书写顺序并不重要，因此
第一个示例也可以写为 {2110 : "OO", 3110 : "Fun"}。这就是为什么我们
使用大括号&mdash;它们暗示绑定形成一个集合，没有隐含顺序。

```{note}
正如该符号所示，映射和集合非常相似。数据结构
可以实现集合也可以实现映射，反之亦然：

* 给定一个映射数据结构，我们可以将键视为集合的元素，并且
只需忽略键绑定的值即可。这无疑浪费了
  空间很小，因为我们永远不需要这些值。

* 给定一个集合数据结构，我们可以将 key&ndash;value 对存储为
元素。搜索元素（因此插入和删除）可能会变得
  更昂贵，因为集合抽象不太可能支持搜索
  自己查找键。
```

这是映射的接口：

```{code-cell} ocaml
:tags: ["hide-output"]
module type Map = sig

  (** [('k, 'v) t] is the type of maps that bind keys of type
      ['k] to values of type ['v]. *)
  type ('k, 'v) t

  (** [insert k v m] is the same map as [m], but with an additional
      binding from [k] to [v].  If [k] was already bound in [m],
      that binding is replaced by the binding to [v] in the new map. *)
  val insert : 'k -> 'v -> ('k, 'v) t -> ('k, 'v) t

  (** [find k m] is [Some v] if [k] is bound to [v] in [m],
      and [None] if not. *)
  val find : 'k -> ('k, 'v) t -> 'v option

  (** [remove k m] is the same map as [m], but without any binding of [k].
      If [k] was not bound in [m], then the map is unchanged. *)
  val remove : 'k -> ('k, 'v) t -> ('k, 'v) t

  (** [empty] is the empty map. *)
  val empty : ('k, 'v) t

  (** [of_list lst] is a map containing the same bindings as
      association list [lst].
      Requires: [lst] does not contain any duplicate keys. *)
  val of_list : ('k * 'v) list -> ('k, 'v) t

  (** [bindings m] is an association list containing the same
      bindings as [m]. There are no duplicates in the list. *)
  val bindings : ('k, 'v) t -> ('k * 'v) list
end
```

接下来，我们将基于以下内容检查映射的三种实现

- 关联列表，

- 数组，以及

- 上述两者的组合，称为“链式哈希表”。

每个实现都需要稍微不同的接口，因为
由底层表示类型产生的约束。在每种情况下
我们将密切关注 AF、RI 和操作效率。

## 作为关联列表的映射

{{ video_embed | replace("%%VID%%", "6JUcwUgAHl8")}}

OCaml 中映射的最简单实现是作为关联列表。我们已经
到目前为止，已经看到该表示两次了 [[1]][assoc-list] [[2]][map-module]。这里
是使用它的 `Map` 的实现：

[assoc-list]: ../data/assoc_list
[map-module]: ../modules/functional_data_structures

```{code-cell} ocaml
:tags: ["hide-output"]
module ListMap : Map = struct
  (** AF: [[(k1, v1); (k2, v2); ...; (kn, vn)]] is the map {k1 : v1, k2 : v2,
      ..., kn : vn}. If a key appears more than once in the list, then in the
      map it is bound to the left-most occurrence in the list. For example,
      [[(k, v1); (k, v2)]] represents {k : v1}. The empty list represents
      the empty map.
      RI: none. *)
  type ('k, 'v) t = ('k * 'v) list

  (** Efficiency: O(1). *)
  let insert k v m = (k, v) :: m

  (** Efficiency: O(n). *)
  let find = List.assoc_opt

  (** Efficiency: O(n). *)
  let remove k lst = List.filter (fun (k', _) -> k <> k') lst

  (** Efficiency: O(1). *)
  let empty = []

  (** Efficiency: O(1). *)
  let of_list lst = lst

  (** [keys m] is a list of the keys in [m], without
      any duplicates.
      Efficiency: O(n log n). *)
  let keys m = m |> List.map fst |> List.sort_uniq Stdlib.compare

  (** [binding m k] is [(k, v)], where [v] is the value that [k]
      binds in [m].
      Requires: [k] is a key in [m].
      Efficiency: O(n). *)
  let binding m k = (k, List.assoc k m)

  (** Efficiency: O(n log n) + O(n) * O(n), which is O(n^2). *)
  let bindings m = List.map (binding m) (keys m)
end
```

{{ video_embed | replace("%%VID%%", "yZkQhcIM0OA")}}

{{ video_embed | replace("%%VID%%", "5aZNbVTXmtE")}}

{{ video_embed | replace("%%VID%%", "bKFfD3oHKTE")}}

{{ video_embed | replace("%%VID%%", "ek2Obhfx064")}}

## 作为数组的映射

{{ video_embed | replace("%%VID%%", "cUEN8sFVkS4")}}

*可变映射*是其绑定可能发生变化的映射。接口为
因此，可变映射与不可变映射不同。插入和移除
因此，可变映射的操作返回 `unit`，因为它们不
生成一个新的映射，但会改变现有的映射。

数组可用于表示键为整数的可变映射。一个
从键到值的绑定是通过使用键作为索引来存储的
数组，并将绑定存储在该索引处。例如，我们可以使用数组
将办公室号码映射到其占用者：

|办公室|居住者|
|-|-|
|459|风扇|
|460|格里|
|461|克拉克森|
|462|米尔伯格|
|463|*不存在*|

这种映射称为“直接地址表”。由于数组有固定的
大小，实现者现在需要知道客户端对*容量*的需求
每当一个
创建空表。这会导致以下接口：

```{code-cell} ocaml
:tags: ["hide-output"]
module type DirectAddressMap = sig
  (** [t] is the type of maps that bind keys of type int to values of
      type ['v]. *)
  type 'v t

  (** [insert k v m] mutates map [m] to bind [k] to [v]. If [k] was
      already bound in [m], that binding is replaced by the binding to
      [v] in the new map. Requires: [k] is in bounds for [m]. *)
  val insert : int -> 'v -> 'v t -> unit

  (** [find k m] is [Some v] if [k] is bound to [v] in [m], and [None]
      if not. Requires: [k] is in bounds for [m]. *)
  val find : int -> 'v t -> 'v option

  (** [remove k m] mutates [m] to remove any binding of [k]. If [k] was
      not bound in [m], then the map is unchanged. Requires: [k] is in
      bounds for [m]. *)
  val remove : int -> 'v t -> unit

  (** [create c] creates a map with capacity [c]. Keys [0] through [c-1]
      are _in bounds_ for the map. *)
  val create : int -> 'v t

  (** [of_list c lst] is a map containing the same bindings as
      association list [lst] and with capacity [c]. Requires: [lst] does
      not contain any duplicate keys, and every key in [lst] is in
      bounds for capacity [c]. *)
  val of_list : int -> (int * 'v) list -> 'v t

  (** [bindings m] is an association list containing the same bindings
      as [m]. There are no duplicate keys in the list. *)
  val bindings : 'v t -> (int * 'v) list
end
```

{{ video_embed | replace("%%VID%%", "eDd9i-imDYo")}}

这是该接口的实现：

```{code-cell} ocaml
:tags: ["hide-output"]
module ArrayMap : DirectAddressMap = struct
  (** AF: [[|Some v0; Some v1; ... |]] represents {0 : v0, 1 : v1, ...}.
      If element [i] of the array is instead [None], then [i] is not
      bound in the map.
      RI: None. *)
  type 'v t = 'v option array

  (** Efficiency: O(1). *)
  let insert k v a = a.(k) <- Some v

  (** Efficiency: O(1). *)
  let find k a = a.(k)

  (** Efficiency: O(1). *)
  let remove k a = a.(k) <- None

  (** Efficiency: O(c). *)
  let create c = Array.make c None

  (** Efficiency: O(c). *)
  let of_list c lst =
    (* O(c) *)
    let a = create c in
    (* O(c) * O(1) = O(c) *)
    List.iter (fun (k, v) -> insert k v a) lst;
    a

  (** Efficiency: O(c). *)
  let bindings a =
    let bs = ref [] in
    (* O(1) *)
    let add_binding k v =
      match v with None -> () | Some v -> bs := (k, v) :: !bs
    in
    (* O(c) *)
    Array.iteri add_binding a;
    !bs
end
```

它的效率是非常高的！ `insert`、`find` 和 `remove` 操作是
恒定时间。但这是以强制键为整数为代价的。
此外，它们需要是小整数（或者至少是小整数）
range），否则我们使用的数组将需要很大。

{{ video_embed | replace("%%VID%%", "mrpti_Guevs")}}

## 作为哈希表的映射

{{ video_embed | replace("%%VID%%", "NyZ07rpq7tk")}}

数组提供恒定的时间性能，但有严格的限制
键。关联列表不会对键施加这些限制，但它们也
不提供恒定时间性能。有没有一种方法可以两全其美
世界？是的（或多或少）！ *哈希表*是解决方案。

关键思想是我们假设存在一个*哈希函数* `hash : 'a ->
int` 可以将任何键转换为非负整数。然后我们可以使用它
函数来索引数组，就像我们对直接地址表所做的那样。
当然，我们希望哈希函数本身以恒定的时间运行，否则
使用它的操作效率不高。

{{ video_embed | replace("%%VID%%", "8IJpySZ5iLM")}}

这就导致了下面的接口，其中哈希表的客户端需要
创建表时传入哈希函数：

```{code-cell} ocaml
module type TableMap = sig
  (** [('k, 'v) t] is the type of mutable table-based maps that bind
      keys of type ['k] to values of type ['v]. *)
  type ('k, 'v) t

  (** [insert k v m] mutates map [m] to bind [k] to [v]. If [k] was
      already bound in [m], that binding is replaced by the binding to
      [v]. *)
  val insert : 'k -> 'v -> ('k, 'v) t -> unit

  (** [find k m] is [Some v] if [m] binds [k] to [v], and [None] if [m]
      does not bind [k]. *)
  val find : 'k -> ('k, 'v) t -> 'v option

  (** [remove k m] mutates [m] to remove any binding of [k]. If [k] was
      not bound in [m], the map is unchanged. *)
  val remove : 'k -> ('k, 'v) t -> unit

  (** [create hash c] creates a new table map with capacity [c] that
      will use [hash] as the function to convert keys to integers.
      Requires: The output of [hash] is always non-negative, and [hash]
      runs in constant time. *)
  val create : ('k -> int) -> int -> ('k, 'v) t

  (** [bindings m] is an association list containing the same bindings
      as [m]. *)
  val bindings : ('k, 'v) t -> ('k * 'v) list

  (** [of_list hash lst] creates a map with the same bindings as [lst],
      using [hash] as the hash function. Requires: [lst] does not
      contain any duplicate keys. *)
  val of_list : ('k -> int) -> ('k * 'v) list -> ('k, 'v) t
end
```

这个想法的一个直接问题是：如果哈希输出不在数组范围内怎么办？
解决这个问题很容易：如果 `a` 是数组长度，那么计算 `(hash k) mod a`
就会返回一个在界限之内的索引。

另一个问题是：如果哈希函数不是*单射*怎么办？这意味着
它不是一对一的。那么多个键可能会发生*冲突*并且需要
存储在数组中的同一索引处。没关系！我们故意允许这种情况发生。
但这确实意味着我们需要一个策略来应对按键冲突时的操作。

有两种众所周知的处理冲突的策略。一是储存
每个数组索引处有多个绑定。数组元素称为*桶*。
通常，存储桶被实现为链表。该策略被称为
许多名称，包括*链式法*、*封闭寻址*和*开放散列*。我们会
使用 **chaining** 作为名称。要检查某个元素是否在哈希表中，
首先对键进行哈希处理以找到要查找的正确存储桶。然后，链接的
扫描列表以查看是否存在所需的元素。如果链表是
总之，这个扫描速度非常快。通过散列来添加或删除元素
找到正确的桶。然后，检查桶中的元素是否存在
在那里，最后将元素从存储桶中适当地添加或删除
以链表的通常方式。

另一种策略是将绑定存储在其正确位置以外的位置
根据哈希值确定的位置。将新绑定添加到哈希表时
会产生冲突，插入操作会找到一个空位置
在数组中放置绑定。这种策略（令人困惑地）被称为
*探测*、*开放寻址*和*封闭散列*。我们将使用**探测**作为
名字。查找空位置的一个简单方法是向前搜索
具有固定步长（通常为 1）的数组索引，寻找未使用的条目；这个
*线性探测*策略往往会产生大量元素聚类
表，导致性能不佳。更好的策略是使用第二个哈希
计算探测间隔的函数；这个策略称为*double
散列*。然而，无论如何实现探测，所需的时间
随着哈希表填满，搜索或添加元素所需的探测次数会迅速增长。

在软件实现中，链接通常比探测更受青睐，
因为用软件实现链表很容易。硬件
当表的大小固定时，实现经常使用探测
电路。但一些现代软件实现正在重新审视
探测的性能优势。

### 链式表示

{{ video_embed | replace("%%VID%%", "LOWAC3WOl6Q")}}

以下是使用链接的哈希表的表示类型：

```ocaml
type ('k, 'v) t = {
  hash : 'k -> int;
  mutable size : int;
  mutable buckets : ('k * 'v) list array
}
```

`buckets` 数组的元素是关联列表，其中存储
绑定。`hash` 函数用于确定键进入哪个桶。
`size` 用于跟踪当前的绑定数量
表，因为通过迭代 `buckets` 进行计算的成本很高。

以下是 AF 和 RI：
```
  (** AF:  If [buckets] is
        [| [(k11,v11); (k12,v12); ...];
           [(k21,v21); (k22,v22); ...];
           ... |]
      that represents the map
        {k11:v11, k12:v12, ...,
         k21:v21, k22:v22, ...,  ...}.
      RI: No key appears more than once in the array (so, no
        duplicate keys in association lists).  All keys are
        in the right buckets: if [k] is in [buckets] at index
        [b] then [hash(k) = b]. The output of [hash] must always
        be non-negative. [hash] must run in constant time. *)
```

对于这种表示，`insert`、`find` 和 `remove` 的效率是多少
类型？全部需要

- 对键进行哈希（常数时间），
- 索引到适当的存储桶（恒定时间），以及
- 找出键是否已经在关联列表中（线性关系）
该列表中的元素数量）。

所以哈希表的效率取决于每个元素的数量
桶。反过来，这取决于哈希函数的分布情况
所有存储桶中的键。

一个糟糕的哈希函数，例如常量函数 `fun k -> 42`，会导致
所有键都放入同一个桶中。那么每个操作都将是线性的
映射中的绑定的 $n$&mdash; 即 $O(n)$。我们绝对不想要
那个。

相反，我们需要散列函数或多或少随机地把键分配到各个桶中。
那么每个桶的预期长度大约是
一样。如果我们可以安排，平均而言，桶长度是一个常数
$L$，然后 `insert`、`find` 和 `remove` 都会按预期运行
$O(L)$。

### 调整大小

{{ video_embed | replace("%%VID%%", "mn2pDfusFyY")}}

我们怎样才能将桶安排为具有预期的恒定长度？来回答
那么，让我们考虑一下表中绑定和存储桶的数量。定义
表的*负载系数*为

$$
\frac{\mbox{number of bindings}}{\mbox{number of buckets}}
$$

因此，具有 20 个绑定和 10 个桶的表的负载因子为 2，
而具有 10 个绑定和 20 个桶的表的负载因子为 0.5。
负载因子就是每个桶中的平均绑定数。所以如果我们能够保持
负载因子恒定，我们可以保持 $L$ 恒定，从而保持
（预期）恒定时间的性能。

为此，请注意绑定的数量不受
哈希表实现者&mdash;但桶的数量是。所以通过改变
桶的数量，实现者可以改变负载因子。一个常见的
策略是将负载因子保持在大约 1/2 到 2 之间。然后每个
桶仅包含几个绑定，因此预期的常数时间性能
是有保证的。

但是，实现者无法提前知道到底需要多少桶。
因此，每当负载因子变得太高时，实现者就必须“调整”桶数组的大小。
通常，新分配的桶数组大小会让负载因子恢复到大约 1。

将这两个想法放在一起，如果负载因子达到 2，则有
绑定数量是表中存储桶的两倍。因此，通过将大小加倍
数组，我们可以将负载因子恢复为1。同样，如果负载因子
达到 1/2，那么桶的数量是绑定的两倍，并且减半
数组的大小会将负载因子恢复为 1。

{{ video_embed | replace("%%VID%%", "BzusuFH1tNw")}}

调整桶数组的大小使其变大是哈希的一项基本技术
表。不过，调整其大小以使其变小并不是必需的。只要
负载因子受上面的常数限制，我们可以实现预期的
恒定的桶长度。所以并不是所有的实现都会减少
数组。虽然这样做可以恢复一些空间，但可能不值得
努力。如果哈希表的大小随时间循环，则尤其如此：
尽管有时它会变小，但最终它会再次变大。

不幸的是，调整大小似乎会破坏我们预期的恒定时间
虽然性能。插入绑定可能会导致负载因子下降
超过 2，从而导致调整大小。当调整大小时，所有现有的绑定
必须重新散列并添加到新的存储桶数组中。于是，插入就变成了
最坏情况线性时间运算！删除也是如此，如果我们调整大小
当负载因子太低时，数组会变得更小。

### 实现

下面的哈希表的实现将我们所有的部分组合在一起
上面讨论过。

```{code-cell} ocaml
:tags: ["hide-output"]
module HashMap : TableMap = struct

  (** AF and RI: above. *)
  type ('k, 'v) t = {
    hash : 'k -> int;
    mutable size : int;
    mutable buckets : ('k * 'v) list array
  }

  (** [capacity tab] is the number of buckets in [tab].
      Efficiency: O(1). *)
  let capacity {buckets} =
    Array.length buckets

  (** [load_factor tab] is the load factor of [tab], i.e., the number of
      bindings divided by the number of buckets. *)
  let load_factor tab =
    float_of_int tab.size /. float_of_int (capacity tab)

  (** Efficiency: O(n). *)
  let create hash n =
    {hash; size = 0; buckets = Array.make n []}

  (** [index k tab] is the index at which key [k] should be stored in the
      buckets of [tab].
      Efficiency: O(1). *)
  let index k tab =
    (tab.hash k) mod (capacity tab)

  (** [insert_no_resize k v tab] inserts a binding from [k] to [v] in [tab]
      and does not resize the table, regardless of what happens to the
      load factor.
      Efficiency: expected O(L). *)
  let insert_no_resize k v tab =
    let b = index k tab in (* O(1) *)
    let old_bucket = tab.buckets.(b) in
    tab.buckets.(b) <- (k,v) :: List.remove_assoc k old_bucket; (* O(L) *)
    if not (List.mem_assoc k old_bucket) then
      tab.size <- tab.size + 1;
    ()

  (** [rehash tab new_capacity] replaces the buckets array of [tab] with a new
      array of size [new_capacity], and re-inserts all the bindings of [tab]
      into the new array.  The keys are re-hashed, so the bindings will
      likely land in different buckets.
      Efficiency: O(n), where n is the number of bindings. *)
  let rehash tab new_capacity =
    (* insert [(k, v)] into [tab] *)
    let rehash_binding (k, v) =
      insert_no_resize k v tab
    in
    (* insert all bindings of bucket into [tab] *)
    let rehash_bucket bucket =
      List.iter rehash_binding bucket
    in
    let old_buckets = tab.buckets in
    tab.buckets <- Array.make new_capacity []; (* O(n) *)
    tab.size <- 0;
    (* [rehash_binding] is called by [rehash_bucket] once for every binding *)
    Array.iter rehash_bucket old_buckets (* expected O(n) *)

  (* [resize_if_needed tab] resizes and rehashes [tab] if the load factor
     is too big or too small.  Load factors are allowed to range from
     1/2 to 2. *)
  let resize_if_needed tab =
    let lf = load_factor tab in
    if lf > 2.0 then
      rehash tab (capacity tab * 2)
    else if lf < 0.5 then
      rehash tab (capacity tab / 2)
    else ()

  (** Efficiency: O(n). *)
  let insert k v tab =
    insert_no_resize k v tab; (* O(L) *)
    resize_if_needed tab (* O(n) *)

  (** Efficiency: expected O(L). *)
  let find k tab =
    List.assoc_opt k tab.buckets.(index k tab)

  (** [remove_no_resize k tab] removes [k] from [tab] and does not trigger
      a resize, regardless of what happens to the load factor.
      Efficiency: expected O(L). *)
  let remove_no_resize k tab =
    let b = index k tab in
    let old_bucket = tab.buckets.(b) in
    tab.buckets.(b) <- List.remove_assoc k tab.buckets.(b);
    if List.mem_assoc k old_bucket then
      tab.size <- tab.size - 1;
    ()

  (** Efficiency: O(n). *)
  let remove k tab =
    remove_no_resize k tab; (* O(L) *)
    resize_if_needed tab (* O(n) *)

  (** Efficiency: O(n). *)
  let bindings tab =
    Array.fold_left
      (fun acc bucket ->
         List.fold_left
           (* 1 cons for every binding, which is O(n) *)
           (fun acc (k,v) -> (k,v) :: acc)
           acc bucket)
      [] tab.buckets

  (** Efficiency: O(n^2). *)
  let of_list hash lst =
    let m = create hash (List.length lst) in  (* O(n) *)
    List.iter (fun (k, v) -> insert k v m) lst; (* n * O(n) is O(n^2) *)
    m
end
```

{{ video_embed | replace("%%VID%%", "FN-YyNaSkz8")}}

{{ video_embed | replace("%%VID%%", "Du4SxDJzS6g")}}

{{ video_embed | replace("%%VID%%", "GKtcy5AfPgc")}}

{{ video_embed | replace("%%VID%%", "YQUHqv-RXI8")}}

可以对 `rehash` 进行优化。当它调用 `insert_no_resize` 时
重新插入绑定，正在完成额外的工作：没有必要
插入调用 `remove_assoc` 或 `mem_assoc`，因为我们保证
绑定不包含重复的键。我们可以省略这项工作。如果哈希
函数很好，只是节省了我们不断的工作量。但如果
哈希函数很糟糕并且不能均匀地分配键，这可能是
重要的优化。

## 哈希函数

{{ video_embed | replace("%%VID%%", "tGktnJWmCy0")}}

哈希表是有史以来发明的最有用的数据结构之一。
不幸的是，它们也是最被滥用的之一。使用哈希构建的代码
表通常远远达不到可实现的性能。有两个原因
为此：

- 客户端选择较差的哈希函数，这些函数不会随机分配键
桶。

- 哈希表抽象没有充分指定哈希的要求
函数，或者使得很难提供好的哈希函数。

显然，一个糟糕的哈希函数可能会破坏我们持续运行的尝试
时间。许多明显的哈希函数选择都是不好的。例如，如果我们是
将姓名映射到电话号码，然后将每个姓名散列到其长度将是
非常糟糕的函数，就像只使用名字的哈希函数一样，或者
只有姓氏。我们希望我们的哈希函数使用中的所有信息
键。这是一门艺术。虽然哈希表在以下情况下非常有效
如果使用得当，那么糟糕的哈希函数常常会被使用，从而破坏性能。

当哈希函数看起来随机时，哈希表可以很好地工作。如果是为了看的话
随机的，这意味着对键的任何更改，即使是很小的更改，也应该改变
桶索引以明显随机的方式。如果我们想象写桶索引
作为二进制数，对键的微小更改应该会随机翻转其中的位
桶索引。这称为信息*扩散*。例如，一位
对键的更改应导致索引中的每一位以 1/2
概率。

**客户端与实现者。** 正如我们所描述的，哈希函数是一个单一的
从键类型映射到桶索引的函数。在实践中，哈希
函数是*两个*函数的组合：一个由客户端提供，另一个由
实现者提供。这是因为实现者不了解
元素类型，客户端不知道有多少个桶，而且
实现者可能不相信客户端能够实现扩散。

客户端函数 `hash_c` 首先将键转换为整数哈希码，
实现函数 `hash_i` 将哈希码转换为桶
索引。实际的哈希函数是这两个函数的组合。作为
哈希表设计者，需要弄清楚客户端哈希函数和
实现端哈希函数将如何提供扩散。如果客户端
足够精明，将扩散推到他们身上是有意义的，留下
哈希表的实现尽可能简单、快速。简单的方法
实现这一点的方法是将桶索引的计算分成三部分
步骤。

1.  序列化：将键转换为包含原始键中所有信息的字节流。
两个相等的键必须产生相同的结果
    字节流。仅当键实际上是时，两个字节流才应该相等
    相等。如何执行此操作取决于键的形式。如果键是
    字符串，那么字节流就只是
    字符串。

2.  扩散：将字节流映射为一个大整数*x*，其方式为
导致流中的每个更改显然都会影响 *x* 的位
    随机的。性能与随机性之间存在权衡（并且
    安全）在这里。

3.  压缩：将大整数缩小到范围内
桶。例如，将哈希桶索引计算为 *x* mod *m*。这个
    如果 *m* 是 2 的幂，则特别便宜。

不幸的是，哈希表的实现很少透露它们的含义。
假设客户端哈希函数。因此，作为客户端，可能很难知道如何
从表中获得良好的性能。实现能够向客户端提供的关于桶中键分布的信息越多越好。

## 标准库 `Hashtbl`

虽然知道如何实现哈希表并了解如何实现是很棒的
这样做使用了可变性，也不需要实现一个
在你自己的项目中自行构建数据。幸运的是 OCaml 标准
库确实提供了一个实现哈希表的模块 `Hashtbl`。你
可以将此模块视为函数式 `Map` 的命令式对应物
模块。

**哈希函数。** 函数 `Hashtbl.hash : 'a -> int` 负责
用于序列化和扩散。它能够对任何类型的值进行哈希处理。
这不仅包括整数，还包括字符串、列表、树等等。那么如何
如果树的长度或树的大小可以是，它是否以恒定的时间运行
任意大？它只查看预定数量的*有意义的节点*
它是散列的结构。默认情况下，该数字为 10。一个有意义的节点
是整数、浮点数、字符串、字符、布尔值或常量
构造函数。  当我们散列这些列表时，你可以看到：

```{code-cell} ocaml
Hashtbl.hash [1; 2; 3; 4; 5; 6; 7; 8; 9];;
Hashtbl.hash [1; 2; 3; 4; 5; 6; 7; 8; 9; 10];;
Hashtbl.hash [1; 2; 3; 4; 5; 6; 7; 8; 9; 10; 11];;
Hashtbl.hash [1; 2; 3; 4; 5; 6; 7; 8; 9; 10; 11; 12];;
```

当列表超过 10 个元素后，哈希值停止变化。这会
影响我们如何使用这个内置哈希函数：它不一定
为大型数据结构提供良好的扩散，这意味着性能可以
随着冲突变得普遍而退化。为了支持想要散列此类
结构的客户端，`Hashtbl` 提供了另一个函数 `hash_param`，可以
配置为检查更多节点。

**哈希表。** 这是哈希表接口的摘要：

```ocaml
module type Hashtbl = sig
  type ('a, 'b) t
  val create : int -> ('a, 'b) t
  val add : ('a, 'b) t -> 'a -> 'b -> unit
  val find : ('a, 'b) t -> 'a -> 'b
  val remove : ('a, 'b) t -> 'a -> unit
  ...
end
```

表示类型 `('a, 'b) Hashtbl.t` 将类型 `'a` 的键映射到
值类型为 `'b`。`create` 函数会用给定容量初始化哈希表，
正如我们上面的实现所做的那样。但它不要求客户端提供哈希函数，
而是使用 `Hashtbl.hash`。

当负载因子超过 2 时，就会发生大小调整。让我们看看会发生什么。首先，
我们将创建一个表并填充它：

```{code-cell} ocaml
open Hashtbl;;
let t = create 16;;
for i = 1 to 16 do
  add t i (string_of_int i)
done;;
```

我们可以使用 `Hashtbl.stats` 查询哈希表，了解绑定在桶中如何分布：

```{code-cell} ocaml
stats t
```

绑定数和桶数相等，因此负载因子为1。
桶直方图是一个数组`a`，其中`a.(i)`是大小为`i`的桶的数量。

让我们将负载因子提高到 2：

```{code-cell} ocaml
for i = 17 to 32 do
  add t i (string_of_int i)
done;;
stats t;;
```

现在再添加一个绑定将触发调整大小，这会使桶的数量加倍：

```{code-cell} ocaml
add t 33 "33";;
stats t;;
```

但是 `Hashtbl` 不会在删除时实现调整大小：

```{code-cell} ocaml
for i = 1 to 33 do
  remove t i
done;;
stats t;;
```

尽管所有绑定已被删除，但桶的数量仍然是 32。

```{note}
Java 的 `HashMap` 有一个默认构造函数 `HashMap()` ，它创建一个空的
容量为 16 的哈希表，当负载因子超过 0.75 时会调整大小
而不是 2。因此 Java 哈希表往往具有较短的存储桶长度
比 OCaml 哈希表短，但也往往会占用更多空间，因为
空桶。
```

**客户端提供的哈希函数。** 如果 `Hashtbl` 的客户端发现
默认哈希函数会导致冲突，因此性能不佳，该怎么办？
这时改用不同的哈希函数是有意义的。为了支持这一点，
`Hashtbl` 提供类似于 `Map` 的函子接口。函子
是 `Hashtbl.Make`，它需要以下模块类型的输入：

```ocaml
module type HashedType = sig
  type t
  val equal : t -> t -> bool
  val hash : t -> int
end
```

类型 `t` 是表的键类型，两个函数 `equal` 和 `hash`
说明如何比较键的相等性以及如何对它们进行散列。如果两个键相等
根据 `equal` 相等，那么根据 `hash`，它们必须具有相同的哈希值。如果
违反了该要求，哈希表将不再运行
正确。例如，假设 `equal k1 k2` 成立，但是
`hash k1 <> hash k2`。那么 `k1` 和 `k2` 将被存储在不同的桶中。
因此，如果客户端将 `k1` 的绑定添加到 `v`，然后查找 `k2`，他们会
无法取回 `v`。

```{note}
最后一个要求对于 Java 来说可能听起来很熟悉。在那里，如果你覆盖
`Object.equals()` 和 `Object.hashCode()`，你必须确保二者彼此一致。
```
