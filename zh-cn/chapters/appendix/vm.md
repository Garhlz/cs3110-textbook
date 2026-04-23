# 虚拟机

“虚拟机”顾名思义：是在另一台机器内部虚拟运行的机器。
使用虚拟机时会涉及两个操作系统：*主机*操作系统 (OS) 和*来宾*操作系统。
主机是你自己的本机操作系统（也许是 Windows）；来宾是在主机内部运行的操作系统。

我们在这里提供的虚拟机 (VM) 在 Ubuntu 来宾操作系统中预装了 OCaml。
Ubuntu 是一个免费的 Linux 操作系统，其名称来自一个古老的非洲词语，意思是
“[humanity to others][ubuntu]”。我们用来创建 VM 的过程
[documented here][vmrepo]。

[ubuntu]: https://ubuntu.com/about
[vmrepo]: https://github.com/cs3110/vm

## 在 Windows 上开始安装

- 下载并安装[VMware Workstation Pro][vmware]。目前它可供个人免费使用，但你必须在 Broadcom 创建一个帐户。

- 下载我们的[AMD64-based VM][3110vms]。将“.ova”文件保存在你喜欢的位置。

- 启动 VMware Workstation，选择“文件”→“打开”，然后选择刚刚下载的 `.ova` 文件。单击“打开”。为 VM 选择你自己的名称（可能是 “CS 3110”），然后单击“导入”。单击“启动此虚拟机”。全部启动并显示 GUI 可能需要大约 2 分钟。

- 跳到下面的“完成安装”。

## 在 Mac 上开始安装

- 下载并安装[VMware Fusion Pro][vmware]。目前它可供个人免费使用，但你必须在 Broadcom 创建一个帐户。

- 如果你拥有 Apple Silicon（M1、M2 或 M3）Mac，请下载我们的 [ARM-based VM][3110vms]。如果你有 Intel Mac，请下载我们的 [AMD64-based VM][3110vms]。将“.ova”文件保存在你喜欢的位置。

- 启动 VMware Fusion，选择“文件”→“新建”，然后将刚刚下载的 `.ova` 文件拖到窗口中。单击“继续”。为虚拟机选择你自己的名称（可能是 “CS 3110”），然后单击“保存”。导入完成后，单击“自定义设置”→“系统设置”→“操作系统”→“Linux”→“Ubuntu 64-bit ARM”。关闭设置。单击黑色窗口中间的播放图标。全部启动并显示 GUI 可能需要大约 2 分钟。

- 继续下面的“完成安装”。

## 完成安装

虚拟机会自动登录。用户名是 `camel`，密码是 `camel`。终端、VS Code 和 Firefox Web 浏览器都有图标，位于左侧启动器栏中。

- 打开终端并更新 Ubuntu 和 OPAM：

  ```console
  $ sudo apt update
  $ sudo apt upgrade
  $ sudo opam update
  $ sudo opam upgrade
  ```

- 如果你是 CS 3110 的学生，请按照 [install instructions](../preface/install.md) 中的说明为当前学期创建 OPAM switch。否则，已有一个默认的 OPAM switch 可供使用。

- 启动 VS Code 并将其更新到最新版本。 OCaml 平台已为你安装。

或者，如果你想更改密码，请从终端运行 `passwd` 并按照提示操作。如果你希望拥有自己的用户名，欢迎你前往“设置”→“用户”创建一个新帐户。请注意，不会为该用户安装 OPAM 和 VS Code。你需要按照 [install instructions](../preface/install.md) 添加它们。

[vmware]: https://www.vmware.com/products/desktop-hypervisor/workstation-and-fusion
[3110vms]: https://cornell.box.com/v/cs3110-virtual-machines
