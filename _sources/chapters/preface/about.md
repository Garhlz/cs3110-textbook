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
thebe-kernel: ocaml-jupyter
---

# 关于本书

**报告错误。** 如果你发现错误，请报告给我们。或者如果你有改进本书某些部分的建议，也可以告诉我们。访问你想提出建议的页面，点击页面右上角附近的 GitHub 图标（看起来像一只猫），然后选择"Open issue"（提交 issue）或"Suggest edit"（建议编辑）。后者步骤更复杂，因为需要你在 GitHub 上 fork 教科书仓库。但即使是小的编辑建议，我们也非常感谢，这样能更快地改进教材。

**背景。** 这本书是康奈尔大学第三学期编程课程的教材。大多数学生已经完成了一学期的 Python 入门编程，随后一学期学过 Java 面向对象编程。因此，本书经常将这两种语言作为参考进行对比。有学过类似语言的读者应该不会有困难。本书不假设你具有函数式编程的任何先验知识，但假设你有某种主流命令式编程语言的编程经验。同时假设你了解离散数学（相当于第一学期标准计算机科学课程的水平）。

**视频。** 你会发现本书嵌入了 200 多个 YouTube 视频。这些视频通常先介绍主题，然后教科书会进一步深入。这些视频在疫情期间制作，当时使用本教科书的康奈尔大学 CS 3110 课程改为异步在线授课。学生们对这些视频的反应非常积极，所以现在作为教科书的一部分公开发布。但说实话，这些视频不是由专业视频制作团队制作的&mdash;只是作者在地下室一边自学一边录制的。

这些视频主要采用 2020 年秋季版本的 OCaml 及其相关工具。你现在使用的版本可能看起来有所不同，但不用担心&mdash;底层的思想是一样的。最明显的区别可能是 OCaml 的 VS Code 插件。2020 年秋季时还在使用老旧的"OCaml and Reason IDE"插件，现在已经被"OCaml Platform"插件取代。

教科书和视频有时会以不同的顺序讲解主题。视频被放在教科书中与其所涵盖主题最接近的位置。要按原始顺序观看所有视频，请从这个 [YouTube 播放列表][videos] 开始。

[videos]: https://www.youtube.com/playlist?list=PLre5AT9JnKShBOPeuiD9b-I4XROIJhkIU

**协作注释。** 在每页的右边距，你会发现由 [hypothes.is][hypothesis] 提供的注释功能。你可以用它来高亮文本、添加私人笔记来帮助学习。你还可以创建学习小组来分享注释，或将其公开分享。可以查看这些 [有效注释的建议][tips]。

[hypothesis]: https://web.hypothes.is/
[tips]: https://web.hypothes.is/annotation-tips-for-students/

**可执行代码。** 本书的许多页面都嵌入了 OCaml 代码。这些代码的执行结果已经在书中显示。这是一个例子：

```{code-cell} ocaml
print_endline "Hello world!"
```

你还可以自己编辑并重新运行代码来试验、检查理解。在页面右上角找到火箭图标，点击下拉菜单，你会看到两种与代码交互的方式：

- *Binder* 会打开 [mybinder.org](https://mybinder.org) 网站，这是一项免费的云端服务，提供"可复现、可交互、可共享的科学计算环境"。所有计算都在其云服务器上进行，用户界面通过浏览器提供。教科书页面在 Binder 中打开需要一段时间。打开后，你可以在 [*Jupyter notebook*][jupyter] 中编辑并运行代码。Jupyter notebook 是一种文档（通常以 `.ipynb` 扩展名结尾），可在浏览器中查看，用于混合编写说明文字和代码。它在数据科学社区（尤其是 Python、R 和 Julia）中因用于分享分析结果而广受欢迎，现在包括 OCaml 在内的许多语言都可以在其中运行。Jupyter notebook 中的代码和文字以*单元格*的形式组织，可通过"Cell"菜单运行；Shift-Enter 通常是运行当前单元格的快捷键。

- *Live Code* 的功能与 Binder 大致相同，区别在于它不会跳转到 Binder，而是直接将当前教科书页面上的代码单元格变为可编辑状态。建立连接需要一点时间，期间你会看到"Waiting for kernel"的提示。连接成功后，你可以编辑并重新运行页面上所有的代码单元格。如果连接失败，请先启动 Binder 站点——这可能需要较长时间。Binder 成功加载教科书页面后，可以关闭 Binder，刷新教科书页面，再次启动 Live Code，此时通常能快速连接成功。


现在试着与上面的单元格互动，让它打印你选择的字符串，比如：`"Camels are bae."`

```{tip}
当你编写"真正的" OCaml 代码时，不会用到这个界面。你会在 Visual Studio Code 或 Emacs 等编辑器中编写代码，然后在终端中编译。Binder 和 Live Code 只是为了更方便地与教科书中的代码互动。
```

**可下载页面。** 本书的每一页都可以以多种格式下载。下载图标位于每个页面的右上角。你会找到页面的原始源代码，通常是 [Markdown][md]&mdash;更准确地说是 [MyST Markdown][myst]，它是技术写作用的 Markdown 扩展。每一页也可以单独下载为 PDF 格式，只需从浏览器打印即可。如果要获取整本书的 PDF 格式，请查看下面的 PDF 部分。

嵌入了 OCaml 代码单元的页面也可以下载为 Jupyter notebook。如果想在自己的计算机上本地运行这些文件（而不是在 Binder 云端），需要安装 Jupyter。最简单的方法通常是安装 [Anaconda][anaconda]。然后需要安装 [OCaml Jupyter][ocaml-jupyter]，这需要你已经安装了 OCaml。需要说明的是，完全不需要安装 Jupyter 或使用 notebook。这只是除了阅读教科书外的另一种互动方式。

[md]: https://en.wikipedia.org/wiki/Markdown
[myst]: https://myst-parser.readthedocs.io/en/latest/
[jupyter]: https://jupyter.org/
[anaconda]: https://www.anaconda.com/
[ocaml-jupyter]: https://github.com/akabe/ocaml-jupyter

**练习和解决方案。** 除第一章外，每一章的末尾都有习题部分。练习题带有难度标注：

* 一颗星 [&starf;]：简单练习，只需一两分钟。

* 两颗星 [&starf;&starf;]：直接的练习，应该需要几分钟。

* 三颗星 [&starf;&starf;&starf;]：可能需要五到二十分钟左右的练习。

* 四颗星 [&starf;&starf;&starf;&starf;] 或更多：具有挑战性或耗时的练习，适合想要深入研究材料的学生。

我们有时可能会误判习题的难度。如果你认为标注有误，请让我们知道。

请不要在任何地方发布你的习题答案，特别是能被搜索引擎找到的公开仓库。{{ solutions }}

**PDF.** 本书提供了完整的 PDF 版本。它不包含嵌入的视频、注释功能或 HTML 版本的其他特性。可能也会存在排版错误。目前还没有平板电脑版本（如 ePub）可用，但大多数平板电脑都能导入 PDF。
