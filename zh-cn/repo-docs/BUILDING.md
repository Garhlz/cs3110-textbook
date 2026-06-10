# 如何创建 Conda 教材环境

- 安装 [Miniconda3 for Python 3.9](https://docs.conda.io/en/latest/miniconda.html)。
- 运行 `conda update -n base -c defaults conda`，把基础安装升级到最新版本。
- 运行 `conda env create -f environment.yml`，创建名为 `textbook` 的环境。
- 然后选择下面两种方式之一继续使用。

自动方式（更省心，推荐）：

- 安装 [conda-auto-env](https://github.com/introkun/conda-auto-env)。你只需要克隆该仓库并 `source` 它的脚本。
- 之后，只要你 `cd` 到教材仓库根目录，就会自动激活正确的环境；不过如果你继续 `cd` 到更深的子目录，就会失去这个自动激活效果。

手动方式：

- 每次要处理这个教材仓库时，都运行一次 `conda activate textbook`。

# 如何创建 uv 教材环境

如果你不想用 Conda，也可以直接用 `uv` 来管理 Python 构建依赖：

- 在仓库根目录运行 `uv venv .venv`
- 运行 `uv pip install --python .venv/bin/python -r requirements.txt`
- 后续把 `./.venv/bin/jupyter-book` 当作 `jupyter-book` 命令来使用

注意：这个仓库当前实际依赖 `jupyter-book==0.15.1`。如果安装更新的 Jupyter Book 版本，会切换到另一套构建链路，并可能额外要求 Node / npm。

# 如何创建 OCaml Jupyter 内核

- 为教材创建一个 OPAM switch，例如：`opam switch create textbook ocaml-base-compiler.5.3.0`。理想情况下，这个 switch 的编译器版本应与前言里面向学生的安装说明保持一致。
- 运行 `opam install jupyter`，安装 Ocaml-Jupyter。
- 安装教材所需的最小包集合：
  `opam install ounit2 qcheck menhir zarith`
- 如果你还想在该 switch 下方便地用 VS Code 编辑 OCaml 代码，也建议安装：
  `opam install ocaml-lsp-server ocamlformat`
- 运行 `ocaml-jupyter-opam-genspec`。记下输出中 kernelspec 的生成位置，然后编辑该文件，把 `display_name` 改成单纯的 `"OCaml"`。
  **这一步很重要。** 因为各章里的代码单元会把这个显示名写死，所以需要一个稳定且不随学期 switch 名称变化的名字。
- 如果你使用的是 Conda，请先确保上面的 Conda 环境已经创建并激活。
- 如果你使用的是 `uv`，请先确保 `.venv` 已创建，并且其中已经安装好 Python 侧的 Jupyter 相关包。
- 然后运行：
  `jupyter kernelspec install --user --name ocaml-jupyter "$(opam var share)/jupyter"`
- 如果你的 `~/.ocamlinit` 中包含 `#use "topfind";;`，可以考虑把它包在下面这几行之间：
  ```
  Sys.interactive := false;;
  #use "topfind";;
  Sys.interactive := true;;
  ```
  这样在构建教材时会减少一些额外输出。但如果你的 `~/.ocamlinit` 本来就没有 `#use "topfind"`，或者根本没有这个文件，那就不需要额外添加。

# 如何构建教材

- 运行 `make html` 或者直接运行 `make`，即可构建英文 HTML 版本。
- 如果你使用 `uv` 而不是 Conda，那么构建英文版可以运行：
  `OPAMSWITCH=textbook .venv/bin/jupyter-book build src`
- 如果你使用 `uv` 构建中文版，可以运行：
  `OPAMSWITCH=textbook .venv/bin/jupyter-book build zh-cn`
- 运行 `make view`（目前只在 Mac 上支持），可以方便地在浏览器中打开生成后的 HTML。它适合大多数校对工作，不过因为页面不是通过 Web 服务器提供的，所以并非所有功能都能正常工作。
- 运行 `make localserver` 可以启动一个本地 Python Web 服务器来提供教材页面；然后在另一个终端标签页中运行 `make viewlocalserver`（同样目前只在 Mac 上支持），即可在浏览器中查看本地服务的版本。
- 运行 `make deploy` 可以把教材部署到 GitHub Pages。在此之前，你需要先配置一个 git remote。例如：
  `git remote add public git@github.com:cs3110/textbook.git`
  这里的 remote 名称 `public` 也可以在 `Makefile` 顶部修改成你想要的其他名字。
