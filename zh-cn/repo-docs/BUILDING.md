# 如何创建 Conda 教科书环境

- 安装
[Miniconda3 for Python 3.9](https://docs.conda.io/en/latest/miniconda.html)。
- 运行 `conda update -n base -c defaults conda` 将基本安装升级到
最新版本。
- 运行 `conda env create -f environment.yml` 以创建 `textbook`
环境。
- 继续执行接下来的两个选项之一。

自动选项（为了便利性推荐）：

- 安装 [conda-auto-env](https://github.com/introkun/conda-auto-env)。所有的你
所要做的就是克隆存储库并获取脚本。
- 现在，只要您 `cd` 进入教科书存储库的根目录，您就拥有权利
环境活跃。不过，如果你在环境下面进行 cd 操作，你就会失去环境。

手动选项：

- **每次**运行 `conda activate textbook` 来激活环境
想要研究教科书。

# 如何创建 OCaml Jupyter 内核

- 为教科书创建一个 OPAM switch，例如 `opam switch create textbook ocaml-base-compiler.5.3.0`。理想情况下，交换机的编译器版本应与前言面向学生的安装说明中指定的编译器版本相同。
- 使用 `opam install jupyter` 安装 Ocaml-Jupyter。
- 安装教科书所需的最小软件包集：
`opam install ounit2 qcheck menhir zarith`。
- 为了方便在教科书切换时在 VS Code 中编辑 OCaml 代码，还
安装这些软件包：
  `opam install ocaml-lsp-server ocamlformat`。
- 运行`ocaml-jupyter-opam-genspec`。请注意输出中生成的位置
内核规范。编辑该文件并将 `display_name` 更改为“OCaml”。
  **这很重要。** 显示名称将在每章中进行硬编码
  不幸的是，它使用代码单元，所以我们需要一个一致的名称
  并且与当前学期的切换名称无关。
- 确保您已经完成上述 Conda 环境安装并拥有
那个环境活跃。
- 运行`jupyter kernelspec install --user --name ocaml-jupyter "$(opam var share)/jupyter"`
- 如果您的 `~/.ocamlinit` 包含 `#use "topfind";;`，则考虑
用这些赋值语句包围它：
  ```
  Sys.interactive := false;;
  #use "topfind";;
  Sys.interactive := true;;
  ```
赋值语句将减少您看到的输出量
  构建教科书。但如果你的 `~/.ocamlinit` 还没有
  `#use "topfind"`，或者如果您没有这样的文件，则无需添加它或语句。

# 如何编写教科书

- 运行 `make html` 或仅运行 `make` 来构建 HTML 版本。
- 运行`make view`（目前仅Mac支持）即可方便地打开
在浏览器中生成 HTML。不过，这适用于大多数校对
  并非所有功能都能正常工作，因为该书未提供服务
  通过网络服务器。
- 运行 `make localserver` 启动本地 Python Web 服务器来服务
本地教科书，并在单独的终端选项卡中运行 `make viewlocalserver`
  打开浏览器（同样仅限 Mac）来查看提供的教科书。
- 运行 `make deploy` 将教科书部署到 GitHub Pages。在这样做之前，
你需要设置一个 git 远程。你可以这样做
  `git remote add public git@github.com:cs3110/textbook.git`。名称
  远程，该示例命令中的 `public` 可以在
  `Makefile` 如果您想使用不同的名称。
