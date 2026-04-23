# 安装 OCaml

如果你只是需要一种运行本书代码示例的方式，实际上不需要安装 OCaml！如前言所述，每个页面上的代码都可以直接在浏览器中执行。

如果你想更进一步但还不准备花时间自己安装 OCaml，我们也提供了一个 [虚拟机](../appendix/vm)，其中已经在 Linux 操作系统里预装了 OCaml。

但如果你想在自己的机器上进行 OCaml 开发，就需要安装 OCaml。这没有放之四海而皆准的"正确"方法。下面的说明是为康奈尔大学 CS 3110 课程编写的，这门课除了 OCaml 还有其他课程目标和需求。不过，即使你不是这门课的学生，也可能会发现这些说明有用。

这是我们要安装的内容：

- Unix 开发环境
- OPAM，OCaml 包管理器
- 带有 OCaml 编译器和一些软件包的 OPAM *switch*
- Visual Studio Code 编辑器，支持 OCaml

安装过程会大量依赖*终端*，也就是计算机的文本界面。
如果你不太熟悉终端，可以先通过这个 [终端教程][terminal-tutorial] 复习一下。

[terminal-tutorial]: https://ubuntu.com/tutorials/command-line-for-beginners

```{tip}
如果这是你第一次安装开发软件，有一点值得先说明：“差不多能用”不算成功。
带着错误继续往下做，通常只会导致更严重的错误和更多痛苦。
这是因为我们正在搭建一座软件之塔，每一层都依赖上一层。
如果基础不牢，整座塔都可能倒塌。
好消息是，如果你真的遇到错误，很可能并不孤单。
快速 Google 搜索通常能找到其他人已经发现的解决办法。
当然，对互联网上陌生人给出的建议一定要保持批判性。
```

让我们开始吧！

## Unix 开发环境

```{important}
**首先，升级你的操作系统。** 如果你一直打算做一次大的操作系统升级，
现在就做。否则，等你以后真正升级时，可能不得不重复部分甚至全部安装过程。
最好先把这件事处理掉。
```

### Linux

如果你已经在运行 Linux，这一步就完成了。继续到下面的[安装 OPAM](install-opam)。

### Mac

macOS 在底层已经是一个基于 Unix 的操作系统。但你还需要一些开发工具和 Unix 包管理器。有两个选择：[Homebrew][homebrew] 和 [MacPorts][macports]。从本教材和 CS 3110 的角度看，选择哪一个都可以：

- 如果你已经习惯了其中一种，继续使用它。在继续下面的说明前，请先运行它的更新命令。

- 否则选择一个，按照其网站上的安装说明操作。Homebrew 的安装过程通常更简单快速，这可能会让你倾向于选择它。如果选择 MacPorts，请确保遵循其页面上的*所有*详细说明，包括 XCode 和 X11 服务器。**不要同时安装 Homebrew 和 MacPorts**，它们不打算共存。如果以后改变主意，请先卸载其中一个再安装另一个。

完成 Homebrew 或 MacPorts 的安装/更新后，继续到下面的 [安装 OPAM](install-opam)。

[homebrew]: https://brew.sh/
[macports]: https://www.macports.org/install.php

### Windows

Windows Subsystem for Linux（WSL）使 Windows 中的 Unix 开发成为可能。如果你有最新版本的 Windows（2020 年 11 月发布的内部版本 20262 或更新版本），WSL 易于安装。如果你的版本不够新，请尝试运行 Windows Update 来获取它。

```{tip}
如果你在安装 WSL 时收到有关“虚拟机”的错误，你可能需要在机器的 BIOS 中启用虚拟化。相关说明取决于机器制造商。尝试 Google 搜索“启用虚拟化 [制造商] [型号]”，替换为你机器的制造商和型号。这个 [Red Hat Linux][rh-virt] 页面也可能有帮助。
```

**使用最新版本的 Windows，**并假设你之前从未安装过 WSL，你需要做的就是：

- 以管理员身份打开 Windows PowerShell。点击"开始"，键入 PowerShell，它应该会是最佳匹配。右键点击"以管理员身份运行"，然后点击"是"以允许更改。

- 运行 `wsl --install`。（或者，如果你已经安装了 WSL 但没有安装 Ubuntu，则运行 `wsl --install -d Ubuntu`。）当 Ubuntu 下载完成后，系统可能会要求你重新启动。重新启动后，安装会自动继续。

- 系统会提示你创建 Unix 用户名和密码。你可以使用任何你想要的用户名和密码。它与你的 Windows 用户名和密码无关（尽管你可以重复使用）。用户名中不要包含空格。不要忘记你的密码，以后会需要它。

```{warning}
如果没有提示你创建 Unix 用户名和密码，请*不要继续*执行这些说明。出了什么问题——也许你的 Ubuntu 安装没有正确完成。请尝试通过 Windows 开始菜单卸载 Ubuntu 并重新安装。
```

现在跳到下面的“Ubuntu 设置”段落。

**如果没有最新版本的 Windows，**你将需要遵循 [Microsoft 的手动安装说明][wsl-manual]。OCaml 对 WSL2 的支持优于 WSL1（WSL2 提供性能和功能改进），所以如果可以的话请安装 WSL2。

[wsl-manual]: https://docs.microsoft.com/en-us/windows/wsl/install-manual
[rh-virt]: https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/6/html/virtualization_administration_guide/sect-virtualization-troubleshooting-enabling_intel_vt_and_amd_v_virtualization_hardware_extensions_in_bios

**Ubuntu 设置。**这些说明的其余部分假设你安装了 Ubuntu (22.04) 作为 Linux 发行版。这是 WSL 的默认发行版。原则上其他发行版应该可以工作，但从此时起可能需要不同的命令。

打开 Ubuntu 应用程序。（如果你刚刚安装完 WSL，它可能已经打开。）你将看到 *Bash 提示符*，它看起来像这样：

```console
user@machine:~$
```

```{warning}
如果提示符看起来像 `root@...#`，说明出现了问题。你是否在上面的步骤中为 Ubuntu 创建了 Unix 用户名和密码？如果是的话，这里显示的用户名应该是你当时选择的，而不是 `root`。*如果提示符如上所示，请不要继续*执行这些说明。可以尝试卸载 Ubuntu 并重新安装。
```

在当前版本的 Windows 终端中，Ctrl+Shift+C 用于复制，Ctrl+Shift+V 用于粘贴。请注意，按键时必须包含 Shift。在旧版本的终端中，你可能需要在终端设置中找到启用这些快捷键的选项。

运行以下命令来更新*APT包管理器*，这就是帮助安装 Unix 软件包：

```console
sudo apt update
```

系统将提示你输入你选择的 Unix 密码。前缀 `sudo` 表示以管理员（也称为"超级用户"）身份运行命令，即以超级用户身份执行（do thus as a superuser），这正是"sudo"名称的由来。

```{warning}
使用 `sudo` 运行命令具有潜在风险，不应轻率行事。不要养成在命令前随意加 `sudo` 的习惯，不要无故使用它。
```

现在运行以下命令来升级所有APT软件包：

```console
sudo apt upgrade -y
```

然后安装我们需要的一些有用的包：

```console
sudo apt install -y zip unzip build-essential
```

**文件系统。** WSL 拥有独立于 Windows 的文件系统，但两者之间有多种方式可以互相访问。

- 当你启动 Ubuntu 并出现 $ 提示符时，你就处于 WSL 文件系统中。你的主目录名为 `~`，即 `/home/your_ubuntu_user_name` 的内置别名。运行 `explorer.exe .`（注意末尾的点）可以在 Windows 资源管理器中打开 Ubuntu 主目录。

- 在 Ubuntu 中，可以通过路径 `/mnt/c/Users/your_windows_user_name/` 访问 Windows 主目录。

- 在 Windows 资源管理器中，可以通过左侧列表中的 Linux 图标（靠近"此电脑"和"网络"），依次导航到 Ubuntu &rarr; `home` &rarr; `your_ubuntu_user_name` 来访问 Ubuntu 主目录。也可以直接在资源管理器路径栏中输入：`\\wsl$\Ubuntu\home\your_ubuntu_user_name`。

现在练习访问你的 Ubuntu 和 Windows 主目录，确保你能判断自己当前处于哪个位置。更多信息请参阅 Microsoft 的 [Windows 与 Linux 文件系统指南][wsl-fs]。

建议将 OCaml 开发工作存储在 Ubuntu 主目录中，而不是 Windows 主目录中。Microsoft 在上面链接的指南中也有同样的建议。

[wsl-fs]: https://docs.microsoft.com/en-us/windows/wsl/filesystems

(install-opam)=
## 安装 OPAM

**Mac。** 如果你使用的是 Homebrew，请运行以下命令：

```console
brew install opam
```

如果你使用的是 MacPorts，请运行以下命令：

```console
sudo port install opam
```

[opam-install]: https://opam.ocaml.org/doc/Install.html

**Windows。** 从 Ubuntu 运行此命令：

```console
sudo apt install opam
```

**Linux。** 遵循 [instructions for your distribution][opam-install]。

## 初始化 OPAM

```{warning}
不要将 `sudo` 放在任何 `opam` 命令前面。那会破坏你的 OCaml 安装。
```

**Linux、Mac 和 WSL2。** 运行：

```console
opam init --bare -a -y
```

如果你收到有关确保 `.profile` 在 `.bashrc` 中“来源良好”的注释，请不要担心。你不需要对此做任何事情。

如果你收到 OPAM 已过期的警告，请通过运行以下命令进行更新：

```console
opam update
```

**WSL1。** 希望你运行的是 WSL2，而不是 WSL1。但在 WSL1 上运行：

```console
opam init --bare -a -y --disable-sandboxing
```

由于[涉及 OPAM 和WSL1][bwrap]。

[bwrap]: https://github.com/ocaml/opam-repository/issues/12050

## 创建 OPAM switch

*switch* 是 OCaml 的一个具名安装，包含特定编译器版本和一套软件包。你可以拥有多个 switch 并在它们之间切换——这也是"switch"这个名称的由来。运行以下命令为本学期的 CS 3110 创建一个 switch：

```console
opam switch create cs3110-2026sp ocaml-base-compiler.5.3.0
```

```{tip}
如果该命令失败并提示无法找到 5.3.0 编译器，可能是你之前安装过 OPAM，需要先更新。请运行 `opam update`。
```

系统可能会提示你运行下一个命令。无论运行与否都没关系，因为我们接下来无论如何都会执行下一步（注销）。

```console
eval $(opam env)
```

现在我们需要确保你的 OCaml 环境配置正确。**从操作系统注销（或重启）**，然后重新打开终端并运行以下命令：

```console
opam switch list
```

你应该得到如下输出：

```
#  switch         compiler
→  cs3110-2026sp  ocaml-base-compiler.5.3.0,ocaml-options-vanilla.1
```

如果你之前做过 OCaml 开发，可能还有其他行。还有一个名为“description”的列，其内容此处未显示。仔细检查以下内容：

- 你**绝对不能**收到"环境与当前 switch 不同步，请运行 `eval $(opam env)`"的警告。如果出现了以下任一问题，需要先解决此问题。

- 当前学期的 switch 旁边的第一列中必须有一个向右箭头。

- 该 switch 必须具有正确的名称和正确的编译器版本。

```{warning}
如果你确实收到了关于 `opam env` 的警告，说明存在问题。你的 shell 可能没有运行 `opam init` 应安装的 OPAM 配置命令。可以尝试 `opam init --reinit` 来解决问题。另外，请确认你真的注销了操作系统（或重启了）。
```

继续安装我们需要的 OPAM 包：

```console
opam install -y utop odoc ounit2 qcheck bisect_ppx menhir ocaml-lsp-server ocamlformat
```

复制时请确保包含上面完整的一行。你会看到一些关于编辑器配置的输出。除非你打算用 Emacs 或 Vim 进行 OCaml 开发，否则可以安全地忽略这些输出。这些说明中我们将使用 VS Code 作为编辑器，所以暂时忽略它。

你现在应该能够启动 utop，即 OCaml 通用顶层（Universal Toplevel）。

```console
utop
```

```{tip}
你应该看到消息"Welcome to utop version ...（using OCaml version 5.3.0）！"如果 OCaml 版本不正确，可能存在环境问题。请参阅上面有关 `opam env` 命令的提示。
```

输入 3110，后跟两个分号，然后按回车。`#` 是 utop 提示符，无需自己输入。

```ocaml
# 3110;;
- : int = 3110
```

先欣赏一下 `3110` 的可爱之处，然后退出 utop。注意这次在 quit 指令前需要额外输入 `#`。

```ocaml
# #quit;;
```

更快的退出方法是按 Control+D。

## 仔细检查 OCaml

如果你在安装时遇到任何问题，请按照以下步骤仔细检查。其中一些与上面提供的提示重复，但我们将它们集中在一处，以帮助诊断问题。

首先，**重启计算机**。我们需要一个干净的状态来重新检查。

其次，运行 utop，确认其正常工作。如果不能运行，以下是一些常见问题：

- **你是否处于正确的 Unix 提示符下？** 在 Mac 上，请确保你处于终端默认的 Unix shell 中：不要手动运行 bash 或 zsh 或其他 shell 来切换。在 Windows 上，请确保使用的是 Ubuntu 应用，而不是 PowerShell 或 Cmd。

- **是否设置了 OPAM 环境？** 如果 utop 不是可识别的命令，请运行 `eval $(opam env)` 然后再次尝试运行 utop。如果 utop 现在可以使用，说明你的登录 shell 不知何故没有运行正确的命令来自动激活 OPAM 环境；你不应该需要手动用 `eval` 命令激活环境。这可能是之前运行 `opam init` 时出了问题。要修复此问题，请按照下面的"重做"说明操作。

- **你的 switch 是否已列出？** 运行 `opam switch list`，确保名为 `cs3110-2026sp` 的 switch 已列出，且具有 5.3.0 编译器，且它是活动的 switch（旁边用箭头标识）。如果该 switch 存在但未激活，运行 `opam switch cs3110-2026sp` 然后看 utop 是否正常。如果该 switch 不存在，请按照下面的"重做"说明操作。

**重做说明：** 运行 `rm -r ~/.opam` 删除 OPAM 目录。然后回到上面的 OPAM 初始化步骤，按照说明重新执行。使用上面给出的确切 OPAM 命令时要格外仔细；有时省略部分内容就会出错。最后，再次仔细检查：重启后验证 utop 是否仍然有效。

```{important}
你想要达到的目标是：重启后 utop 立即可用，无需键入任何额外命令。
```

## Visual Studio Code

Visual Studio Code 是 OCaml 代码编辑器的绝佳选择。（当然，如果你已经是 Emacs 或 Vim 的高级用户，它们也很好。）

首先，按照 Microsoft 针对你的操作系统的说明下载并安装 Visual Studio Code（以下简称 VS Code）：[Mac 说明][vscode-mac]、[Windows 说明][vscode-win]、[Linux 说明][vscode-nix]。

```{warning}
在 Mac 上，你必须按照 Microsoft 的说明将 VS Code 安装在 Applications 文件夹中。跳过这些说明会导致一些问题，直到后来才会显现。请确保现在就正确安装。
```

启动 VS Code。通过 View &rarr; Extensions 或点击左侧图标栏中的扩展图标（看起来像四个小方块，右上角那个与其他三个分离）来打开扩展窗格。

在以下说明的不同位置，你会被要求"打开命令面板"。为此，请转到 View → Command Palette。这个菜单中 "Command Palette" 右侧也会显示对应操作系统的键盘快捷键。

其次，如果你使用的是 Windows 或 Mac，请执行以下操作之一：

- **仅限 Windows：** 安装"WSL"扩展。

- **仅限 Mac：** 打开命令面板，输入"shell command"以找到"Shell Command: Install 'code' command in PATH"命令，然后运行它。

第三，无论使用哪种操作系统，请关闭所有打开的终端，或者直接注销或重启，以让新的路径设置生效，这样之后才能从终端启动 VS Code。

第四，**仅限 Windows**，打开命令面板并运行"WSL: Connect to WSL"命令。（Mac 用户请跳到下一步。）第一次执行时，它会安装一些额外的软件。完成后，你将在 VS Code 窗口左下角看到"WSL: Ubuntu"指示器。**请确保在继续下一步之前看到该指示器。** 如果你只看到一个形如 <sub>&gt;</sub><sup>&lt;</sup> 的图标，点击它，然后从打开的命令面板中选择"Connect to WSL"。

第五，再次打开 VS Code 扩展窗格，搜索并安装来自 OCaml Labs 的 **"OCaml Platform"** 扩展。安装时请确保名称*完全*正确。

```{warning}
名为"OCaml"或"OCaml and Reason IDE"的扩展不是正确的选择。它们都很旧，不再由开发人员维护。
```
[vscode]: https://code.visualstudio.com/
[vscode-mac]: https://code.visualstudio.com/docs/setup/mac
[vscode-win]: https://code.visualstudio.com/docs/setup/windows
[vscode-nix]: https://code.visualstudio.com/docs/setup/linux

## 仔细检查 VS Code

让我们确保 VS Code 的 OCaml 支持正常工作。

- 再次重启计算机。（是的，这其实没有必要。但它能发现许多潜在的问题，因此值得这样做。）

- 打开一个全新的 Unix shell。**Windows**：记住是 Ubuntu，而不是 PowerShell 或 Cmd。**Mac**：记住不要手动输入 `zsh` 或 `bash` 来切换 shell。

- 导航到你选择的目录，最好是主目录的子目录。例如，你可以在主目录中为 3110 工作创建一个目录：

  ```console
  mkdir ~/3110
  cd ~/3110
  ```

  在该目录中运行以下命令打开 VS Code：

  ```console
  code .
  ```

  转到 File &rarr; New File，以 `test.ml` 为文件名保存。VS Code 应该给它一个橙色骆驼图标。

- 输入以下 OCaml 代码，然后按 Return/Enter：

  ```ocaml
  let x : int = 3110
  ```

  键入时，VS Code 应该进行语法高亮、提示部分补全，并在代码行上方添加小注释。尝试将 `int` 改为 `string`，`3110` 下方应出现一条波浪线。将鼠标悬停可查看错误信息，也可转到 View &rarr; Problems 查看。加上双引号将整数改为字符串，问题就会消失。

**如果没有观察到上述行为，** 说明安装存在问题。以下是排查思路：

- 确保在启动 VS Code 的同一 Unix 提示符下，能够顺利完成 OPAM switch 的双重检查：utop 能正常运行吗？正确的 switch 是否处于激活状态？如果没有，需要先解决这个问题，再处理 VS Code 的问题，届时可能已经自动修复了。

- 确保你使用的是最新版本的 VS Code。在命令面板中运行"Code: Check for Updates"。如果你在 Mac 上无法更新 VS Code，请确保按照 Microsoft 的说明将 VS Code 安装在 Applications 文件夹中。

- 如果你使用的是 WSL，VS Code 添加了语法高亮但没有波浪线，或者收到"沙盒初始化失败"的错误，请仔细检查 VS Code 窗口左下角是否显示"WSL"指示符。如果有，请确保安装了"OCaml Platform"扩展。如果没有，请确保按照上述步骤安装了"WSL"扩展，并从 Ubuntu 而不是 PowerShell 或 Windows GUI 启动 VS Code。

**如果仍然遇到问题，** 可以尝试卸载 VS Code、重启计算机，然后从头重新执行所有安装说明，注意任何警告或错误。

```{warning}
在对任何 VS Code 问题进行排查时，**不要在 VS Code 设置文件中对任何路径进行硬编码**，尽管网上可能有这样的建议。那是治标不治本的做法，真正的根源很可能是 OCaml 环境问题，可以使用上面的 OCaml 仔细检查说明来排查。
```

## VS Code 设置

我们建议调整一些编辑器设置。通过以下方式打开用户设置 JSON 文件：(i) 转到 View → Command Palette，(ii) 输入"user settings json"，(iii) 选择 Open User Settings (JSON)。你将看到一个 JSON 文件，其中可能已经包含一些设置，类似这样：

```
{
  (your pre-existing settings here)
}
```

将这些新设置添加到最外面的大括号中：

```
{
  "[ocaml][ocaml.interface]": {
    "editor.tabSize": 2,
    "editor.rulers": [ 80 ],
    "editor.formatOnSave": true
  },
  (your pre-existing settings here)
}
```

保存文件并关闭选项卡。

## 协作使用 VS Code

VS Code 的 Live Share 扩展让与他人协作编写代码变得轻松有趣。你们可以像在 Google Docs 中协作一样共同编辑代码，它甚至支持共享语音频道，无需另开一个 Zoom 通话。要安装和使用 Live Share，请参阅 [Microsoft 教程][liveshare]。

如果你是康奈尔大学的学生，请使用 Microsoft 账号登录，而不是 GitHub 账号。输入你的康奈尔 NetID 邮箱，例如 `your_netid@cornell.edu`，然后在康奈尔大学的登录页面使用与 NetID 关联的密码。

[liveshare]: https://learn.microsoft.com/en-us/visualstudio/liveshare/
