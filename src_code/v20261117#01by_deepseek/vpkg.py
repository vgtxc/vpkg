# lastEdit=>2026.11.17-22:00
# lastEdit=>2026.11.06-20:10
# lastEdit=>2026.04.16-22:38-2026.11.03-23:50
# creat:2026.04.16
# aut: vgtxc
# ver: src#20260428
# ver: 20261102
# ver: 20261106
"""
    bug->...待测试
"""

import os
import sys
import re
import shutil
import subprocess
from rich import print

# ================= 软件全局变量 =================
vpkg_root = str()                   # 01路径,软件二进制或脚本文件所在的文件夹
vpkg_root_system = str()            # 01路径,平台系统
vpkg_root_tool = str()              # 01路径,工具路径
vpkg_root_script = str()            # 01路径,脚本文件
vpkg_root_cache = str()             # 01路径,临时文件
vpkg_root_extra = str()             # 01路径,压缩包解压
vpkg_conf_path = str()              # 01路径,配置文件路径
vpkg_conf_symbol = list()           # 02配置文件中的关键词
vpkg_info = dict()                  # 03信息字典
vpkg_infoFmt = dict()               # 03信息字典,格式
vpkg_info_kwOrder = list()          # 03信息字典,自引用解包顺序
vpkg_tool = dict()                  # 03工具字典
vpkg_toolFmt = dict()               # 03工具字典,元素格式
vpkg_tool_kwOrder = list()          # 03工具字典,自引用解包顺序
vpkg_script = dict()                # 04脚本字典
vpkg_scriptFmt = dict()             # 04脚本字典,元素格式
vpkg_script_kwOrder = list()        # 04脚本字典,自引用解包顺序
vpkg_retvalu = "ugv_retvalu"        # 05默认无意义返回值
vpkg_cmd = list()                   # 05默认支持的命令
vpkg_zip_ext = dict()               # 05压缩包后缀名
vpkg_tool_basic = list()            # 05基础软件环境
vpkg_download_proxy = dict()        # 05下载代理, 采用xget代理: https://github.com/xixu-me/xget
vpkg_conf = str()                   # 05配置文件解析出的配置

# 05软件内置默认配置
vpkg_conf_default = """
# lastEdit=>2026.11.16-20:54
# lastEdit=>2026.11.12-20:05
# creat:2026.02.01
# vpkg基本配置
info->vpkg
    platform: x64-win
    name: vpkg
    version: v.xxx
    website: https://github.com/vgtxc/vpkg
    autor: vgtxc
    publish: None
    description: A lightWight sftw manager!!!
    proxy: False
over->vpkg
# 基础软件: a7z
info->tool
    platform: x64-win
    name: a7z
    version: v26.04
    website: https://www.7-zip.org/
    local_path: {vpkg_tool}/<name>/<version>
    symbol_excu: <local_path>/7za.exe
    init->install
        <local_path>=https://github.com/ip7z/7zip/releases/download/26.04/7z2604-extra.7z
    over->install
    init->env_arg
        path=<local_path>
    over->env_arg
over->tool
# 基础软件: aria2
info->tool
    platform: x64-win
    name: aria2
    version: v1.37.0
    website: https://github.com/aria2/aria2
    local_path: {vpkg_tool}/<name>/<version>
    symbol_excu: <local_path>/aria2c.exe
    init->install
        <local_path>=https://github.com/aria2/aria2/releases/latest/download/aria2-1.37.0-win-64bit-build1.zip
    over->install
    init->env_arg
        aria2_home=<local_path>
        path=<local_path>
    over->env_arg
over->tool
# 下载软件: wget
info->tool
    platform: x64-win
    name: wget
    version: v1.25.0
    website: https://eternallybored.org/misc/wget/
    local_path: {vpkg_tool}/<name>/<version>
    symbol_excu: <local_path>/wget.exe
    init->install
        <local_path>=https://eternallybored.org/misc/wget/releases/wget-1.25.0-win64.zip
    over->install
    init->env_arg
        wget_home=<local_path>
        path=<local_path>
    over->env_arg
over->tool
# 截图软件: fastCapture
info->tool
    platform: x64-win
    name: fastCapture
    version: v11.3
    website: https://www.faststone.org/
    local_path: {vpkg_tool}/<name>/<version>
    symbol_excu: <local_path>/FSCapture.exe
    init->install
        <local_path>=https://www.faststonesoft.net/DN/FSCapture113.zip
    over->install
    init->env_arg
        path=<local_path>
    over->env_arg
over->tool
# 文本软件: sublime
info->tool
    platform: x64-win
    name: sublime
    version: v4215
    website: https://www.sublimetext.com/
    local_path: {vpkg_tool}/<name>/<version>
    symbol_excu: <local_path>/sublime.exe
    init->install
        <local_path>=https://www.sublimetext.com/download_thanks?target=win-x64-portable#direct-downloads
    over->install
    init->env_arg
        path=<local_path>
    over->env_arg
over->tool
# 工具软件: 图像高分辨修复
info->tool
    platform: x64-win
    name: ncnn_vulkan
    version: v20250915
    website: https://github.com/BtbN/FFmpeg-Builds
    local_path: {vpkg_tool}/<name>/<version>
    symbol_excu: <local_path>/waifu2x-ncnn-vulkan.exe
    init->install
        <local_path>=https://github.com/nihui/waifu2x-ncnn-vulkan/releases/download/20250915/waifu2x-ncnn-vulkan-20250915-windows.zip
    over->install
    init->env_arg
        path=<local_path>
    over->env_arg
over->tool
# 工具软件: 音频处理
info->tool
    platform: x64-win
    name: ffmpeg
    version: v.last
    website: https://github.com/BtbN/FFmpeg-Builds
    local_path: {vpkg_tool}/<name>/<version>
    symbol_excu: <local_path>/bin/ffmpeg.exe
    init->install
        <local_path>=https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip
    over->install
    init->env_arg
        path=<local_path>/bin
    over->env_arg
over->tool
# 工具软件: 代码管理
info->tool
    platform: x64-win
    name: git
    version: v2.55.0
    website: https://git-scm.com/
    local_path: {vpkg_tool}/<name>/<version>
    symbol_excu: <local_path>/bin/git.exe
    init->install
        <local_path>=https://github.com/git-for-windows/git/releases/download/v2.55.0.windows.5/PortableGit-2.55.0.5-64-bit.7z.exe
    over->install
    init->env_arg
        path=<local_path>
        path=<local_path>/bin
    over->env_arg
over->tool
# 工具软件: 包管理
info->tool
    platform: x64-win
    name: pixi
    version: v.last
    website: https://github.com/prefix-dev/pixi
    local_path: {vpkg_tool}/<name>/<version>
    symbol_excu: <local_path>/pixi.exe
    init->install
        <local_path>=https://github.com/prefix-dev/pixi/releases/latest/download/pixi-x86_64-pc-windows-msvc.zip
    over->install
    init->env_arg
        path=<local_path>
    over->env_arg
over->tool
# 工具软件: 编译
info->tool
    platform: x64-win
    name: cmake
    version: v4.5.0-rc1
    website: https://github.com/Kitware/CMake
    local_path: {vpkg_tool}/<name>/<version>
    symbol_excu: <local_path>/bin/cmake.exe
    init->install
        <local_path>=https://github.com/Kitware/CMake/releases/download/v4.5.0-rc1/cmake-4.5.0-rc1-windows-x86_64.zip
    over->install
    init->env_arg
        path=<local_path>/bin
    over->env_arg
over->tool
# 工具软件: 编译
info->tool
    platform: x64-win
    name: xmake
    version: v3.1.1
    website: https://github.com/xmake-io/xmake
    local_path: {vpkg_tool}/<name>/<version>
    symbol_excu: <local_path>/xmake.exe
    init->install
        <local_path>=https://github.com/xmake-io/xmake/releases/download/v3.1.1/xmake-v3.1.1.win64.zip
    over->install
    init->env_arg
        path=<local_path>
    over->env_arg
over->tool
# 工具软件: 包管理
info->tool
    platform: x64-win
    name: vcpkg
    version: v20261016
    website: https://github.com/microsoft/vcpkg
    local_path: {vpkg_tool}/<name>/<version>
    symbol_excu: <local_path>/vcpkg.exe
    init->install
        <local_path>=https://github.com/microsoft/vcpkg/archive/refs/tags/2026.10.16.zip
        <local_path>=https://github.com/microsoft/vcpkg-tool/releases/download/2026-09-26/vcpkg.exe
    over->install
    init->env_arg
        path=<local_path>
        vcpkg_root=<local_path>
        vcpkg_default_triplet=x64-mingw-static
        vcpkg_default_host_triplet=x64-mingw-static
        X_VCPKG_ASSET_SOURCES=x-azurl,https://mirrors.tuna.tsinghua.edu.cn/vcpkg/assets/
        VCPKG_BINARY_SOURCES=clear;x-https,https://mirrors.tuna.tsinghua.edu.cn/vcpkg-ce/cache/,readwrite
    over->env_arg
over->tool
# 工具软件: 编译器, nodejs
info->tool
    platform: x64-win
    name: nodejs
    version: v26.8.2
    website: https://nodejs.org
    local_path: {vpkg_tool}/<name>/<version>
    symbol_excu: <local_path>/node.exe
    init->install
        <local_path>=https://nodejs.org/dist/v26.8.2/node-v26.8.2-win-x64.zip
    over->install
    init->env_arg
        path=<local_path>
        path=<local_path>/node_modules
        path=<local_path>/node_pkg
        npm_config_prefix=<local_path>/npm_pkg
        npm_config_cache=<local_path>/npm_cache
    over->env_arg
over->tool
# 工具软件: 编译器, python
info->tool
    platform: x64-win
    name: python
    version: v3.15.2
    website: https://www.python.org
    local_path: {vpkg_tool}/<name>/<version>
    symbol_excu: <local_path>/python.exe
    init->install
        <local_path>=https://www.python.org/ftp/python/3.15.2/python-3.15.2-embed-amd64.zip
        <local_path>=https://bootstrap.pypa.io/get-pip.py
    over->install
    init->env_arg
        path=<local_path>
        path=<local_path>/Scripts
    over->env_arg
over->tool
# 工具软件: 编译器, rust
info->tool
    platform: x64-win
    name: rust
    version: v1.98.1
    website: https://rust-lang.org/
    local_path: {vpkg_tool}/<name>/<version>
    symbol_excu: <local_path>/rustup-init.exe
    init->install
        <local_path>=https://static.rust-lang.org/rustup/dist/x86_64-pc-windows-msvc/rustup-init.exe
    over->install
    init->env_arg
        rustup_home=<local_path>/rustup_home
        cargo_home=<local_path>/cargo_home
        path=<local_path>
        path=<local_path>/cargo_home/bin
        path=<local_path>/rustup_home
    over->env_arg
over->tool
# 工具软件: 编译器, java
info->tool
    platform: x64-win
    name: java
    version: v27
    website: https://www.java.com
    local_path: {vpkg_tool}/<name>/<version>
    symbol_excu: <local_path>/bin/java.exe
    init->install
        <local_path>=https://download.oracle.com/java/27/latest/jdk-27_windows-x64_bin.zip
    over->install
    init->env_arg
        path=<local_path>/bin
    over->env_arg
over->tool
# 工具软件: 编译器, golang
info->tool
    platform: x64-win
    name: golang
    version: v1.27.3
    website: https://golang.google.cn/
    local_path: {vpkg_tool}/<name>/<version>
    symbol_excu: <local_path>/bin/go.exe
    init->install
        <local_path>=https://go.dev/dl/go1.27.3.windows-amd64.zip
    over->install
    init->env_arg
        go_root=<local_path>
        path=<local_path>
    over->env_arg
over->tool
# 工具软件: 编译器, zig
info->tool
    platform: x64-win
    name: zig
    version: v0.17.1
    website: https://ziglang.org/
    local_path: {vpkg_tool}/<name>/<version>
    symbol_excu: <local_path>/zig.exe
    init->install
        <local_path>=https://ziglang.com.cn/download/0.17.1/zig-x86_64-windows-0.17.1.zip
    over->install
    init->env_arg
        path=<local_path>
    over->env_arg
over->tool
# 工具软件: 编译器, vlang
info->tool
    platform: x64-win
    name: vlang
    version: v0.5
    website: https://vlang.io/
    local_path: {vpkg_tool}/<name>/<version>
    symbol_excu: <local_path>/v.exe
    init->install
        <local_path>=https://github.com/vlang/v/releases/latest/download/v_windows.zip
    over->install
    init->env_arg
        path=<local_path>
    over->env_arg
over->tool
# 工具软件: 编译器, lua
info->tool
    platform: x64-win
    name: lua
    version: v5.5.0
    website: https://www.lua.org/
    local_path: {vpkg_tool}/<name>/<version>
    symbol_excu: <local_path>/lua55.exe
    init->install
        <local_path>=https://xget.xi-xu.me/sf/projects/luabinaries/files/5.5.0/Tools%20Executables/lua-5.5.0_Win64_bin.zip
        <local_path>=https://xget.xi-xu.me/sf/projects/luabinaries/files/5.5.0/Windows%20Libraries/Static/lua-5.5.0_Win64_mingw6_lib.zip
        <local_path>=https://luarocks.github.io/luarocks/releases/luarocks-3.13.0-windows-64.zip
    over->install
    init->env_arg
        luarocks_config=<local_path>/config.lua
        path=<local_path>
    over->env_arg
over->tool
# 工具软件: 编译器, lua_onePro
info->tool
    platform: x64-win
    name: lua_onePro
    version: v5.5.1.0
    website: https://github.com/OneLuaPro/OneLuaPro
    local_path: {vpkg_tool}/<name>/<version>
    symbol_excu: <local_path>/bin/lua.exe
    init->install
        <local_path>=https://github.com/OneLuaPro/OneLuaPro/releases/download/v5.5.1.0/OneLuaPro-5.5.1.0-x64.zip
        <local_path>/src_code=https://github.com/OneLuaPro/OneLuaPro/archive/refs/tags/v5.5.1.0.zip
    over->install
    init->env_arg
        path=<local_path>/bin
    over->env_arg
over->tool
# 工具软件: 编译器, mingw_w64
info->tool
    platform: x64-win
    name: mingw_w64
    version: v16.2.0
    website: https://github.com/niXman/mingw-builds-binaries
    local_path: {vpkg_tool}/<name>/<version>
    symbol_excu: <local_path>/bin/gcc.exe
    init->install
        <local_path>=https://github.com/niXman/mingw-builds-binaries/releases/download/16.2.0-rt_v14-rev1/x86_64-16.2.0-release-posix-seh-ucrt-rt_v14-rev1.7z
    over->install
    init->env_arg
        path=<local_path>/bin
    over->env_arg
over->tool
# 工具软件: 编译器, msvc_kit
info->tool
    platform: x64-win
    name: msvc_kit
    version: v.last
    website: https://github.com/loonghao/msvc-kit
    local_path: {vpkg_tool}/<name>/<version>
    symbol_excu: <local_path>/msvc-kit-x86_64-windows.exe
    init->install
        <local_path>=https://github.com/loonghao/msvc-kit/releases/latest/download/msvc-kit-x86_64-windows.exe
    over->install
    init->env_arg
        path=<local_path>
    over->env_arg
over->tool
# 工具软件: 编译器, msvc_delphier
info->tool
    platform: x64-win
    name: msvc_delphier
    version: v.last
    website: https://github.com/Delphier/MSVC
    local_path: {vpkg_tool}/<name>/<version>
    symbol_excu: <local_path>/setup_x64.bat
    init->install
        <local_path>=https://github.com/Delphier/MSVC/releases/download/v14.51.36231/MSVC-14.51.36231.7z
    over->install
    init->env_arg
        path=<local_path>
    over->env_arg
over->tool
# 工具软件: 编译器, msvc_chnlm
info->tool
    platform: x64-win
    name: msvc_chnlm
    version: v14.51.36260
    website: https://github.com/Delphier/MSVC
    local_path: {vpkg_tool}/<name>/<version>
    symbol_excu: <local_path>/setup_x64.bat
    init->install
        <local_path>=https://github.com/CHNLM/PortableMSVC-GUI/releases/download/msvc-14.51.36260/PortableMSVC-14.51.36231.7z
    over->install
    init->env_arg
        path=<local_path>
    over->env_arg
over->tool
# 工具软件: 编译器, w64devkit
info->tool
    platform: x64-win
    name: w64devkit
    version: v2.11.0
    website: https://github.com/skeeto/w64devkit
    local_path: {vpkg_tool}/<name>/<version>
    symbol_excu: <local_path>/bin/gcc.exe
    init->install
        <local_path>=https://github.com/skeeto/w64devkit/releases/download/v2.11.0/w64devkit-x64-2.11.0.7z.exe
    over->install
    init->env_arg
        path=<local_path>/bin
    over->env_arg
over->tool
# 工具软件: 编译器, mingw-lite
info->tool
    platform: x64-win
    name: mingw-lite
    version: v2.11.0
    website: https://github.com/redpanda-cpp/mingw-lite
    local_path: {vpkg_tool}/<name>/<version>
    symbol_excu: <local_path>/bin/gcc.exe
    init->install
        <local_path>=https://github.com/redpanda-cpp/mingw-lite/releases/download/next-17-20261101-r0/mingw64-ucrt-next-17-20261101-r0.7z
    over->install
    init->env_arg
        path=<local_path>/bin
    over->env_arg
over->tool
# 工具软件: 编译器, llvm_mingw
info->tool
    platform: x64-win
    name: llvm_mingw
    version: v20260908
    website: https://github.com/mstorsjo/llvm-mingw
    local_path: {vpkg_tool}/<name>/<version>
    symbol_excu: <local_path>/bin/gcc.exe
    init->install
        <local_path>=https://github.com/mstorsjo/llvm-mingw/releases/download/20260908/llvm-mingw-20260908-ucrt-x86_64.zip
    over->install
    init->env_arg
        path=<local_path>/bin
    over->env_arg
over->tool
# 工具软件: 编译器, llvm_msvc
info->tool
    platform: x64-win
    name: llvm_msvc
    version: v777.3.1
    website: https://github.com/aftermathlabs/llvm-msvc
    local_path: {vpkg_tool}/<name>/<version>
    symbol_excu: <local_path>/bin/clang-cl.exe
    init->install
        <local_path>=https://github.com/aftermathlabs/llvm-msvc/releases/download/llvm-msvc-v777.3.1/windows-wrapper-llvm-msvc-PDB.zip.001
        <local_path>=https://github.com/aftermathlabs/llvm-msvc/releases/download/llvm-msvc-v777.3.1/windows-wrapper-llvm-msvc-PDB.zip.002
    over->install
    init->env_arg
        path=<local_path>/bin
    over->env_arg
over->tool
# 工具软件: 编译器, llvm_winlibs
info->tool
    platform: x64-win
    name: llvm_winlibs
    version: v16.2.0
    website: https://github.com/brechtsanders/winlibs_mingw
    local_path: {vpkg_tool}/<name>/<version>
    symbol_excu: <local_path>/bin/gcc.exe
    init->install
        <local_path>=https://github.com/brechtsanders/winlibs_mingw/releases/download/16.2.0posix-23.1.3-14.0.0-ucrt-r3/winlibs-x86_64-posix-seh-gcc-16.2.0-llvm-23.1.3-mingw-w64ucrt-14.0.0-r3.7z
    over->install
    init->env_arg
        path=<local_path>/bin
    over->env_arg
over->tool
# 工具软件: 编译器, mingw_winlibs
info->tool
    platform: x64-win
    name: mingw_winlibs
    version: v16.2.0
    website: https://github.com/brechtsanders/winlibs_mingw
    local_path: {vpkg_tool}/<name>/<version>
    symbol_excu: <local_path>/bin/gcc.exe
    init->install
        <local_path>=https://github.com/brechtsanders/winlibs_mingw/releases/download/16.2.0posix-23.1.3-14.0.0-ucrt-r3/winlibs-x86_64-posix-seh-gcc-16.2.0-mingw-w64ucrt-14.0.0-r3.7z
    over->install
    init->env_arg
        path=<local_path>/bin
    over->env_arg
over->tool
# 工具软件: 编译器, llvm_qt
info->tool
    platform: x64-win
    name: llvm_qt
    version: v6.11.2
    website: https://github.com/yuanpeirong/buildQt
    local_path: {vpkg_tool}/<name>/<version>
    symbol_excu: <local_path>/bin/qmake.exe
    init->install
        <local_path>=https://github.com/yuanpeirong/buildQt/releases/download/Qt6.11.2_rev0/Qt_6.11.2-static-Release_llvm-mingw22.1.8_64_UCRT.7z
    over->install
    init->env_arg
        path=<local_path>/bin
    over->env_arg
over->tool
# 工具软件: 编译器, mingw_qt
info->tool
    platform: x64-win
    name: mingw_qt
    version: v6.11.2
    website: https://github.com/yuanpeirong/buildQt
    local_path: {vpkg_tool}/<name>/<version>
    symbol_excu: <local_path>/bin/qmake.exe
    init->install
        <local_path>=https://github.com/yuanpeirong/buildQt/releases/download/Qt6.11.2_rev0/Qt_6.11.2-static-Release_mingw1620_64_UCRT.7z
    over->install
    init->env_arg
        path=<local_path>/bin
    over->env_arg
over->tool
# 工具软件: 编译器, msvc_qt
info->tool
    platform: x64-win
    name: msvc_qt
    version: v6.11.2
    website: https://github.com/yuanpeirong/buildQt
    local_path: {vpkg_tool}/<name>/<version>
    symbol_excu: <local_path>/bin/qmake.exe
    init->install
        <local_path>=https://github.com/yuanpeirong/buildQt/releases/download/Qt6.11.2_rev0/Qt_6.11.2-static-Release_msvc2026_64.7z
    over->install
    init->env_arg
        path=<local_path>/bin
    over->env_arg
over->tool
# 工具软件: 下载软件, motrix
info->tool
    platform: x64-win
    name: motrix
    version: v2.2.1
    website: https://motrix.app/zh/
    local_path: {vpkg_tool}/<name>/<version>
    symbol_excu: <local_path>/Motrix.exe
    init->install
        <local_path>=https://dl.motrix.app/releases/Motrix-2.2.1-win.zip
    over->install
    init->env_arg
        path=<local_path>
    over->env_arg
over->tool
# 工具软件: 代理工具, FlClash
info->tool
    platform: x64-win
    name: FlClash
    version: v0.9.2
    website: https://github.com/chen08209/FlClash
    local_path: {vpkg_tool}/<name>/<version>
    symbol_excu: <local_path>/FlClash.exe
    init->install
        <local_path>=https://github.com/chen08209/FlClash/releases/download/v0.9.2/FlClash-0.9.2-windows-amd64.zip
    over->install
    init->env_arg
        path=<local_path>
    over->env_arg
over->tool
# 工具软件: 代理工具, v2rayN
info->tool
    platform: x64-win
    name: v2rayN
    version: v7.25.6
    website: https://github.com/2dust/v2rayN
    local_path: {vpkg_tool}/<name>/<version>
    symbol_excu: <local_path>/v2rayN.exe
    init->install
        <local_path>=https://github.com/2dust/v2rayN/releases/download/7.25.6/v2rayN-windows-64.zip
    over->install
    init->env_arg
        path=<local_path>
    over->env_arg
over->tool
# 脚本: 取消shell代理
info->script
    platform: x64-win
    name: unproxy
    version: 1.0
    website: void
    local_path: {vpkg_script}/unproxy.bat
    init->content
        @echo off
        set http_proxy=
        set https_proxy=
        echo info-}remove the proxy
    over->content
over->script
# 脚本: 设置代理
info->script
    platform: x64-win
    name: proxy_clash
    version: v1.0
    website: void
    local_path: {vpkg_script}/proxy_clash.bat
    init->content
        @echo off
        set http_proxy=127.0.0.1:7890
        set https_proxy=127.0.0.1:7890
        echo info-}set the proxy to http://127.0.0.1:7890
    over->content
over->script
# 脚本: 设置代理
info->script
    platform: x64-win
    name: proxy_v2ray
    version: v1.0
    website: void
    local_path: {vpkg_script}/proxy_v2ray.bat
    init->content
        @echo off
        set http_proxy=127.0.0.1:7880
        set https_proxy=127.0.0.1:7880
        echo info-}set the proxy to http://127.0.0.1:7880
    over->content
over->script
"""

# ================= 颜色与日志打印封装 =================
def log_info(msg):
    print(f'[green]{msg}[/green]')
def log_warn(msg):
    print(f'[blue]{msg}[/blue]')
def log_erro(msg):
    print(f'[red]{msg}[/red]')

# ================= 核心功能函数 =================
# ================= 00.初始化 =================
def init_program() -> str:
    global vpkg_root, vpkg_root_system, vpkg_root_tool, vpkg_root_script
    global vpkg_root_cache, vpkg_root_extra, vpkg_conf_path, vpkg_conf_symbol
    global vpkg_info, vpkg_infoFmt, vpkg_info_kwOrder
    global vpkg_tool, vpkg_toolFmt, vpkg_tool_kwOrder
    global vpkg_script, vpkg_scriptFmt, vpkg_script_kwOrder
    global vpkg_retvalu, vpkg_cmd, vpkg_zip_ext, vpkg_tool_basic
    global vpkg_download_proxy, vpkg_conf
    # 判断是否是 PyInstaller 打包后的环境
    if getattr(sys, "frozen", False):
        vpkg_root = os.path.dirname(sys.executable)
    else:
        vpkg_root = os.path.dirname(os.path.abspath(__file__))
    vpkg_root = vpkg_root.replace("\\", "/")
    vpkg_conf_path = f"{vpkg_root}/vpkg_config.txt"
    vpkg_conf_symbol = ["info->vpkg", "info->tool", "info->script"]
    # 路径模板（由 extra_config 内的闭包最终解析）
    vpkg_root_system = "{vpkg_root}/{platform}"
    vpkg_root_tool = "{vpkg_root_system}/tool"
    vpkg_root_script = "{vpkg_root_system}/script"
    vpkg_root_cache = "{vpkg_root_system}/cache"
    vpkg_root_extra = "{vpkg_root_system}/cache/extra_dir"
    # vpkg_info
    vpkg_info_kwOrder = ["platform", "name", "version", "website", "autor", "publish", "description", "proxy"]
    vpkg_infoFmt = {
        "platform": "x64-win",
        "name": "vpkg",
        "version": "v20261112",
        "website": "https://github.com/vgtxc/vpkg",
        "autor": "vgtxc",
        "publish": "20261112",
        "description": "A lightWight portable software package manager!!!",
        "proxy": False,
    }
    vpkg_info = dict(vpkg_infoFmt)   # ★ 关键：用默认值填充，避免配置文件缺失时 KeyError
    # vpkg_tool
    vpkg_tool_kwOrder = ["platform", "name", "version", "website", "local_path", "symbol_excu", "install", "env_arg", "install_statu"]
    vpkg_toolFmt = {k: str() for k in vpkg_tool_kwOrder}
    vpkg_tool = {}
    # vpkg_script
    vpkg_script_kwOrder = ["platform", "name", "version", "website", "local_path", "content", "install_statu"]
    vpkg_scriptFmt = {k: str() for k in vpkg_script_kwOrder}
    vpkg_script = {}
    # 环境 & 命令
    vpkg_tool_basic = ["a7z", "aria2"]
    vpkg_retvalu = "ugv_retvalu"
    vpkg_cmd = ["help", "list", "install", "remove", "shell", "excu", "gen_conf"]
    # 压缩包后缀
    vpkg_zip_ext = {
        "single_file": (".7z", ".zip", ".rar", ".7z.exe"),
        "multi_7z":   tuple(f".7z.{i:03d}" for i in range(1, 7)),
        "multi_zip":  tuple(f".zip.{i:03d}" for i in range(1, 7)),
        "multi_rar":  tuple(f".part{i:03d}.rar" for i in range(1, 7)),
        "default": (".7z", ".zip", ".rar", ".7z.exe", ".7z.001", ".zip.001", ".part001.rar"),
        "filter": (
            ".7z", ".zip", ".rar", ".7z.exe",
            *[f".7z.{i:03d}" for i in range(1, 7)],
            *[f".zip.{i:03d}" for i in range(1, 7)],
            *[f".part{i:03d}.rar" for i in range(1, 7)],
        ),
    }
    # 下载代理
    vpkg_download_proxy = {
        "https://github.com/": "https://xget.xi-xu.me/gh/",
        "https://gist.github.com/": "https://xget.xi-xu.me/gist/",
        "https://gitlab.com/": "https://xget.xi-xu.me/gl/",
        "https://gitea.com/": "https://xget.xi-xu.me/gitea/",
        "https://codeberg.org/": "https://xget.xi-xu.me/codeberg/",
        "https://sourceforge.net/": "https://xget.xi-xu.me/sf/",
        "https://android.googlesource.com/": "https://xget.xi-xu.me/aosp/",
        "https://huggingface.co/": "https://xget.xi-xu.me/hf/",
        "https://civitai.com/": "https://xget.xi-xu.me/civitai/",
        "https://registry.npmjs.org/": "https://xget.xi-xu.me/npm/",
        "https://pypi.org/": "https://xget.xi-xu.me/pypi/",
        "https://repo.anaconda.com/": "https://xget.xi-xu.me/conda/",
        "https://conda.anaconda.org/": "https://xget.xi-xu.me/conda/community/",
        "https://repo1.maven.org/": "https://xget.xi-xu.me/maven/",
        "https://downloads.apache.org/": "https://xget.xi-xu.me/apache/",
        "https://plugins.gradle.org/": "https://xget.xi-xu.me/gradle/",
        "https://github.com/Homebrew/": "https://xget.xi-xu.me/homebrew/",
        "https://rubygems.org/": "https://xget.xi-xu.me/rubygems/",
        "https://cran.r-project.org/": "https://xget.xi-xu.me/cran/",
        "https://www.cpan.org/": "https://xget.xi-xu.me/cpan/",
        "https://tug.ctan.org/": "https://xget.xi-xu.me/ctan/",
        "https://proxy.golang.org/": "https://xget.xi-xu.me/golang/",
        "https://api.nuget.org/": "https://xget.xi-xu.me/nuget/",
        "https://crates.io/": "https://xget.xi-xu.me/crates/",
        "https://repo.packagist.org/": "https://xget.xi-xu.me/packagist/",
        "https://dl.flathub.org/": "https://xget.xi-xu.me/flathub/",
        "https://deb.debian.org/": "https://xget.xi-xu.me/debian/",
        "https://archive.ubuntu.com/": "https://xget.xi-xu.me/ubuntu/",
        "https://mirrors.kernel.org/fedora/": "https://xget.xi-xu.me/fedora/",
        "https://download.rockylinux.org/": "https://xget.xi-xu.me/rocky/",
        "https://download.opensuse.org/": "https://xget.xi-xu.me/opensuse/",
        "https://geo.mirror.pkgbuild.com/": "https://xget.xi-xu.me/arch/",
        "https://arxiv.org/": "https://xget.xi-xu.me/arxiv/",
        "https://f-droid.org/": "https://xget.xi-xu.me/fdroid/",
        "https://updates.jenkins.io/": "https://xget.xi-xu.me/jenkins/",
    }
    return vpkg_retvalu

# ================= 01.配置解析 =================
def extra_config() -> str:
    def _resolve(text: str, platform: str, name: str, version: str, local_path: str) -> str:
        for placeholder, value in (
            ("{vpkg_root}", vpkg_root),
            ("{vpkg_system}", vpkg_root_system),
            ("{vpkg_tool}", vpkg_root_tool),
            ("{vpkg_script}", vpkg_root_script),
            ("{vpkg_cache}", vpkg_root_cache),
            ("<platform>", platform),
            ("<name>", name),
            ("<version>", version),
            ("<website>", version),           # 保留历史行为
            ("<local_path>", local_path),
            ("<symbol_excu>", local_path),    # 保留历史行为
        ):
            text = text.replace(placeholder, value)
        return text

    def _item_match() -> str:
        user_content = ""
        if os.path.exists(vpkg_conf_path):
            with open(vpkg_conf_path, "r", encoding="utf8") as f:
                user_content = f.read()
        # ★ 默认在前，用户在后（用户覆盖默认）
        merged = vpkg_conf_default + "\n" + user_content
        merged = re.sub(r"#.*$", "", merged, flags=re.MULTILINE)
        lines = [ln for ln in merged.split("\n") if ln.strip()]
        splits = [i for i, ln in enumerate(lines) if ln in vpkg_conf_symbol]
        splits.append(len(lines))
        for b in range(len(splits) - 1):
            block = lines[splits[b]:splits[b + 1]]
            if not block:
                continue
            head, tail = block[0], block[-1]
            # ---------- info->vpkg ----------
            if head == "info->vpkg" and tail == "over->vpkg":
                kv = {}
                for ln in block[1:-1]:
                    if not ln.startswith("    ") or ":" not in ln:
                        log_erro("erro->func:<extra_config>...config file “sftw” syntax panic!!!")
                        log_warn("\n".join(block))
                        return vpkg_retvalu
                    k, _, v = ln[4:].partition(":")
                    kv[k.strip()] = v.strip()
                for key in vpkg_info_kwOrder:
                    if key not in kv:
                        continue
                    if key == "proxy":
                        vpkg_info[key] = kv[key] == "True"
                    else:
                        vpkg_info[key] = kv[key]
                continue
            # ---------- info->tool ----------
            if head == "info->tool" and tail == "over->tool":
                head_keys = ["platform", "name", "version", "website", "local_path", "symbol_excu"]
                if len(block) < 1 + len(head_keys) + 1:
                    log_erro("erro->func:<extra_config>...config file “tool” syntax panic!!!")
                    log_warn("\n".join(block))
                    continue
                kv = {}
                ok = True
                for j, k in enumerate(head_keys):
                    line = block[1 + j]
                    if not line.startswith(f"    {k}:"):
                        ok = False
                        break
                    kv[k] = line[4 + len(k) + 1:].strip()
                if not ok:
                    log_erro("erro->func:<extra_config>...config file “tool” syntax panic!!!")
                    log_warn("\n".join(block))
                    continue
                if kv["platform"] != vpkg_info["platform"]:
                    log_warn(f"warn->{kv['name']}...{kv['platform']}...not match system platform...{vpkg_info['platform']}!!!")
                    continue
                install = {}
                env_arg = {}
                state = None
                for line in block[1 + len(head_keys):-1]:
                    stripped = line.strip()
                    if stripped == "init->install":
                        state = "install"
                        continue
                    if stripped == "over->install":
                        state = None
                        continue
                    if stripped == "init->env_arg":
                        state = "env_arg"
                        continue
                    if stripped == "over->env_arg":
                        state = None
                        continue
                    if state and stripped and "=" in stripped:
                        k, _, v = stripped.partition("=")
                        k, v = k.strip(), v.strip()
                        target = install if state == "install" else env_arg
                        target.setdefault(k, []).append(v)
                vpkg_tool[kv["name"]] = {
                    "platform": kv["platform"],
                    "name": kv["name"],
                    "version": kv["version"],
                    "website": kv["website"],
                    "local_path": kv["local_path"],
                    "symbol_excu": kv["symbol_excu"],
                    "install": install,
                    "env_arg": env_arg,
                }
                continue
            # ---------- info->script ----------
            if head == "info->script" and tail == "over->script":
                head_keys = ["platform", "name", "version", "website", "local_path"]
                if len(block) < 1 + len(head_keys) + 1:
                    log_erro("erro->func:<extra_config>...config file “script” syntax panic!!!")
                    log_warn("\n".join(block))
                    continue
                kv = {}
                ok = True
                for j, k in enumerate(head_keys):
                    line = block[1 + j]
                    if not line.startswith(f"    {k}:"):
                        ok = False
                        break
                    kv[k] = line[4 + len(k) + 1:].strip()
                if not ok:
                    log_erro("erro->func:<extra_config>...config file “script” syntax panic!!!")
                    log_warn("\n".join(block))
                    continue
                if kv["platform"] != vpkg_info["platform"]:
                    log_warn(f"warn->{kv['name']}...{kv['platform']}...not match system platform...{vpkg_info['platform']}!!!")
                    continue
                content_lines = []
                in_content = False
                for line in block[1 + len(head_keys):-1]:
                    stripped = line.strip()
                    if stripped == "init->content":
                        in_content = True
                        continue
                    if stripped == "over->content":
                        in_content = False
                        continue
                    if in_content:
                        content_lines.append(line[8:] if len(line) >= 8 else line)
                content = "".join(ln + "\n" for ln in content_lines if ln)
                vpkg_script[kv["name"]] = {
                    "platform": kv["platform"],
                    "name": kv["name"],
                    "version": kv["version"],
                    "website": kv["website"],
                    "local_path": kv["local_path"],
                    "content": content,
                }
                continue
        return vpkg_retvalu

    def _item_extra() -> str:
        for tool in vpkg_tool.values():
            platform, name, version = tool["platform"], tool["name"], tool["version"]
            new_lp = _resolve(tool["local_path"], platform, name, version, tool["local_path"])
            new_sym = _resolve(tool["symbol_excu"], platform, name, version, new_lp)
            tool["local_path"] = new_lp
            tool["symbol_excu"] = new_sym
            tool["install"] = {
                _resolve(k, platform, name, version, new_lp):
                    [_resolve(v, platform, name, version, new_lp) for v in vs]
                for k, vs in tool["install"].items()
            }
            tool["env_arg"] = {
                _resolve(k, platform, name, version, new_lp):
                    [_resolve(v, platform, name, version, new_lp) for v in vs]
                for k, vs in tool["env_arg"].items()
            }
        # script 解引用（保留原历史行为：<name>/<version> 用 platform 替换）
        for script in vpkg_script.values():
            lp = script["local_path"]
            platform = script["platform"]
            for k, v in (
                ("{vpkg_root}", vpkg_root),
                ("{vpkg_system}", vpkg_root_system),
                ("{vpkg_tool}", vpkg_root_tool),
                ("{vpkg_script}", vpkg_root_script),
                ("{vpkg_cache}", vpkg_root_cache),
                ("<platform>", platform),
                ("<name>", platform),
                ("<version>", platform),
            ):
                lp = lp.replace(k, v)
            script["local_path"] = lp
        return vpkg_retvalu

    def _item_check() -> str:
        platform = vpkg_info["platform"]
        for kind in (vpkg_tool, vpkg_script):
            for name in list(kind.keys()):
                if kind[name]["platform"] != platform:
                    del kind[name]
        # 创建必要的文件目录
        for d in (vpkg_root_cache, vpkg_root_tool, vpkg_root_script):
            if not os.path.exists(d):
                os.mkdir(d)
                log_warn(f"info->creat dir...>{d}<")
        # 检查安装状态
        for tool in vpkg_tool.values():
            tool["install_statu"] = os.path.exists(tool["symbol_excu"])
        for script in vpkg_script.values():
            script["install_statu"] = os.path.exists(script["local_path"])
        # pixi 特殊处理
        if "pixi" in vpkg_tool and vpkg_tool["pixi"]["install_statu"]:
            pixi_excu = vpkg_tool["pixi"]["symbol_excu"]
            pixi_home = vpkg_tool["pixi"]["local_path"]
            vpkg_script["prefix"] = {
                "platform": "x64-win",
                "name": "prefix",
                "version": "1.0",
                "website": "void",
                "local_path": f"{vpkg_root_script}/prefix.bat",
                "content": f"@echo off\ncall {pixi_excu} shell --manifest-path {pixi_home}/pixi.toml",
                "install_statu": True,
            }
        return vpkg_retvalu

    def vpkg_root_extra() -> str:
        global vpkg_root_system, vpkg_root_tool, vpkg_root_script
        global vpkg_root_cache, vpkg_root_extra
        platform = vpkg_info["platform"]
        vpkg_root_system = f"{vpkg_root}/{platform}"
        vpkg_root_tool = f"{vpkg_root_system}/tool"
        vpkg_root_script = f"{vpkg_root_system}/script"
        vpkg_root_cache = f"{vpkg_root_system}/cache"
        vpkg_root_extra = f"{vpkg_root_system}/cache/extra_dir"
        return vpkg_retvalu

    def _install_script() -> str:
        for script in vpkg_script.values():
            if script["install_statu"]:
                continue
            with open(script["local_path"], "w") as f:
                f.write(script["content"])
            log_info(f"info->func:extra_config._install_script, install script...>{script['local_path']}<")
        return vpkg_retvalu

    if not os.path.exists(vpkg_conf_path):
        log_warn(f"warn->config file miss...>{vpkg_conf_path}<")
    _item_match()     # 内部已处理文件缺失 + 默认配置填充
    vpkg_root_extra() # 用最新 platform 计算 5 个 root
    _item_extra()
    _item_check()
    _install_script()
    return vpkg_retvalu

# ================= 02.命令解析 =================
def extra_command() -> str:
    def _check_basic_sftw_statu() -> bool:
        ok = True   # ★ 修复：初始值应为 True
        for name in vpkg_tool_basic:
            if not vpkg_tool.get(name, {}).get("install_statu", False):
                ok = False
                log_erro(f"erro->lack of basic sftw...>{name}<")
        return ok

    def _get_cli_arg() -> tuple:
        if len(sys.argv) == 1:
            return (vpkg_retvalu, [])
        return (sys.argv[1], sys.argv[2:])

    def _clean_dir(aim_path: str) -> str:
        if not os.path.exists(aim_path):
            log_warn(f"warn->not exists the dir...>{aim_path}<")
            return vpkg_retvalu
        shutil.rmtree(aim_path)
        os.mkdir(aim_path)
        log_warn(f"warn->clean the dir...>{aim_path}<")
        return vpkg_retvalu

    def _system_run_cmd(cmd) -> bool:
        result = subprocess.run(cmd)
        if result.returncode != 0:
            log_erro(f"erro->_system_run_cmd...{cmd}")
        return result.returncode == 0

    def _file_download(file_url: str, out_dir: str) -> bool:
        real_url = file_url
        if vpkg_info["proxy"]:
            for prefix, xget in vpkg_download_proxy.items():
                if prefix in real_url:
                    real_url = real_url.replace(prefix, xget)
        aria2_statu = vpkg_tool["aria2"]["install_statu"]
        aria2_excu = vpkg_tool["aria2"]["symbol_excu"]
        wget_statu = vpkg_tool["wget"]["install_statu"]
        wget_excu = vpkg_tool["wget"]["symbol_excu"]
        if aria2_statu:
            cmd = [aria2_excu, real_url, f"--dir={out_dir}", "--allow-overwrite=true",
                   "--max-connection-per-server=16", "--min-split-size=1M"]
        elif wget_statu:
            cmd = [wget_excu, "-P", out_dir, real_url]
        else:
            log_erro("erro->no download tool (aria2 or wget)...")
            return False
        log_info(f"info->running command...\n\t{' '.join(cmd)}")
        result = subprocess.run(cmd)
        if result.returncode != 0:
            log_erro(f"erro->download failed (code={result.returncode}): {file_url}")
        return result.returncode == 0

    def _file_unzip(file_path: str, out_dir: str) -> bool:
        exe = vpkg_tool["a7z"]["symbol_excu"]
        cmd = [exe, "x", file_path, "-o" + out_dir, "-y"]
        log_info(f"info->running command...\n\t{' '.join(cmd)}")
        result = subprocess.run(cmd)
        if result.returncode != 0:
            log_erro(f"erro->unzip failed (code={result.returncode}): {file_path}")
        return result.returncode == 0

    def _cmd_help(cmd_valu: list) -> str:
        log_warn("info->vpkg sftw info start!!!")
        for k, v in vpkg_info.items():
            log_info(f"\t{k:<12}->\t{v}")
        log_warn("info->vpkg usage...>vpkg \\[command] \\[argument]<")
        for c in vpkg_cmd:
            log_info(f"\tsupport command: {c}")
        log_warn("info->vpkg sftw info end!!!")
        return vpkg_retvalu

    def _cmd_list(cmd_valu: list) -> str:
        log_warn("info->list software install status!!!")
        log_info("\t" + "-" * 40)
        log_info("\t%-15s->%-15s->%-10s" % ("tool_name", "install_status", "website"))
        log_info("\t" + "-" * 40)
        for tool in vpkg_tool.values():
            if tool["install_statu"]:
                log_info("\t%-15s->%-15s->%-10s" % (tool["name"], True, tool["website"]))
            else:
                log_erro("\t%-15s->%-15s->%-10s" % (tool["name"], False, tool["website"]))
        log_info("\n")
        log_info("\t" + "-" * 40)
        log_info("\t%-15s->%-15s->%-10s" % ("script_name", "install_status", "website"))
        log_info("\t" + "-" * 40)
        for script in vpkg_script.values():
            if script["install_statu"]:
                log_info("\t%-15s->%-15s->%-10s" % (script["name"], True, script["website"]))
            else:
                log_erro("\t%-15s->%-15s->%-10s" % (script["name"], False, script["website"]))
        log_info("\t" + "-" * 40)
        return vpkg_retvalu

    def _cmd_shell(cmd_valu: list) -> str:
        origin_var = os.environ.copy()
        shell_var = {}
        path_key = "PATH"
        for k in origin_var.keys():
            shell_var[k] = origin_var[k].replace("\\", "/")
            if k.lower() == "path":
                path_key = k
        for tool in vpkg_tool.values():
            if not tool["install_statu"]:
                continue
            for k, vlist in tool["env_arg"].items():
                val = ";".join(vlist)
                existing = next((ek for ek in shell_var if ek.lower() == k.lower()), None)
                if existing:
                    shell_var[existing] = f"{shell_var[existing]};{val}"
                else:
                    shell_var[k] = val
        shell_var[path_key] = f"{shell_var[path_key]};{vpkg_root_script}"
        if os.name == "nt":
            new_shell_arg = "title vpkg && prompt (vpkg) $P$G"
            subprocess.run(["cmd", "/k", new_shell_arg], env=shell_var)
            sys.exit(0)
        return vpkg_retvalu

    def _cmd_install(cmd_valu: str) -> str:
        def _get_file_and_dir(aim_path: str) -> tuple:
            file_list, dir_list = [], []
            for idx in os.scandir(aim_path):
                if idx.is_file():
                    file_list.append(idx.path)
                if idx.is_dir():
                    dir_list.append(idx.path)
            return (file_list, dir_list)

        def _get_differ_item(listA: list, listB: list) -> list:
            return [item for item in listB if item not in listA]

        def _get_stop_dir(aim_path: str) -> str:
            current = aim_path
            while True:
                entries = [e for e in os.listdir(current) if not e.startswith('.')]
                subdirs = [e for e in entries if os.path.isdir(os.path.join(current, e))]
                if len(entries) != 1 or len(subdirs) != 1:
                    return current
                current = os.path.join(current, subdirs[0])

        def _install_script(script_name: str) -> str:
            if script_name not in vpkg_script:
                log_erro(f"erro->not exist script config...>{script_name}<")
                return vpkg_retvalu
            script = vpkg_script[script_name]
            with open(script["local_path"], "w") as f:
                f.write(script["content"])
            return vpkg_retvalu

        def _install_sftw(tool_name: str) -> str:
            cache_dir = vpkg_root_cache
            extra_dir = f"{cache_dir}/extra_dir"
            _clean_dir(cache_dir)
            os.makedirs(extra_dir, exist_ok=True)
            cache_init_file, _ = _get_file_and_dir(cache_dir)
            for install_dir, url_list in vpkg_tool[tool_name]["install"].items():
                os.makedirs(install_dir, exist_ok=True)
                _clean_dir(install_dir)
                for url in url_list:
                    if not _file_download(url, cache_dir):
                        log_erro(f"erro->abort install {tool_name}, download failed")
                        return vpkg_retvalu
                cache_over_file, _ = _get_file_and_dir(cache_dir)
                download_file_list = _get_differ_item(cache_init_file, cache_over_file)
                pack_file, move_file = [], []
                for idx in download_file_list:
                    file = os.path.split(idx)[1]
                    ispack = any(file.endswith(ext) for ext in vpkg_zip_ext["default"])
                    (pack_file if ispack else move_file).append(idx)
                for idx in pack_file:
                    _clean_dir(extra_dir)
                    _file_unzip(idx, extra_dir)
                    unpack_dir = _get_stop_dir(extra_dir)
                    shutil.copytree(unpack_dir, install_dir, dirs_exist_ok=True)
                for idx in move_file:
                    file = os.path.split(idx)[1]
                    new_file = os.path.join(install_dir, file)
                    os.rename(idx, new_file)
            return vpkg_retvalu

        def _unique_handle(tool_name: str) -> str:
            if tool_name == "pixi":
                log_info("info->install DLC(init home) for...>pixi<")
                pixi_excu = vpkg_tool["pixi"]["symbol_excu"]
                pixi_home = vpkg_tool["pixi"]["local_path"]
                _system_run_cmd([pixi_excu, "init", pixi_home])
                _install_script("prefix")
            if tool_name == "python":
                log_info("info->install DLC(pip) for...>python<")
                path_install = list(vpkg_tool[tool_name]["install"].keys())[0]
                file_pth, file_pip, file_py = "", "", ""
                for idx in os.scandir(path_install):
                    fp = idx.path
                    if fp.endswith("._pth"):
                        file_pth = fp
                    if fp.endswith("get-pip.py"):
                        file_pip = fp
                    if fp.endswith("python.exe"):
                        file_py = fp
                if file_pth:
                    with open(file_pth, "r") as f:
                        new_content = f.read().replace("#import site", "import site")
                    with open(file_pth, "w") as f:
                        f.write(new_content)
                if file_pth and file_pip and file_py:
                    _system_run_cmd([file_py, file_pip])
            if tool_name == "rust":
                log_info("info->install DLC for...>rust<")
                rust_env = vpkg_tool["rust"]["env_arg"]
                os.environ["rustup_home"] = rust_env["rustup_home"][0]
                os.environ["cargo_home"] = rust_env["cargo_home"][0]
                _system_run_cmd([vpkg_tool["rust"]["symbol_excu"]])
            if tool_name == "lua":
                log_info("info->install DLC(luarocks config.lua) for...>lua<")
                lua_ver = "5.5.0"
                lua_root = vpkg_tool["lua"]["local_path"]
                lua_include = f"{lua_root}/include"
                lua_excu = vpkg_tool["lua"]["symbol_excu"]
                # 修复：不要被 luac* 覆盖（lua55.exe 才是解释器）
                lua_excu_copy = f"{lua_root}/lua.exe"
                if not os.path.exists(lua_excu_copy):
                    shutil.copy2(lua_excu, lua_excu_copy)
                # mingw-lite 存在性检查
                if "mingw-lite" not in vpkg_tool:
                    log_erro("erro->mingw-lite not found in repo, cannot configure luarocks!!!")
                    return vpkg_retvalu
                mingw_root = vpkg_tool["mingw-lite"]["local_path"]
                mingw_statu = vpkg_tool["mingw-lite"]["install_statu"]
                mingw_root_to_lua = f"{lua_root}/mingw-lite"
                config_content = (
                    f'lua_version = "{lua_ver}"\n'
                    'rocks_trees = {\n'
                    f'\t{{name = "user",root = "{lua_root}",}},\n'
                    '}\n'
                    'variables = {\n'
                    f'\tCC = "{mingw_root_to_lua}/bin/gcc.exe",\n'
                    f'\tCXX = "{mingw_root_to_lua}/bin/g++.exe",\n'
                    f'\tLD = "{mingw_root_to_lua}/bin/gcc.exe",\n'
                    f'\tAR = "{mingw_root_to_lua}/bin/ar.exe",\n'
                    f'\tLUA = "{lua_excu_copy}",\n'
                    f'\tLUA_BINDIR = "{lua_root}",\n'
                    f'\tLUA_INCDIR = "{lua_include}",\n'
                    f'\tLUA_LIBDIR = "{lua_root}",\n'
                    f'\tLUA_VERSION = "{lua_ver}",\n'
                    '\tLINKFLAGS = "-shared",\n'
                    '}'
                )
                vpkg_script["luarocks_config"] = {
                    "platform": "x64-win",
                    "name": "luarocks_config",
                    "version": "v1.0",
                    "website": "void",
                    "local_path": f"{lua_root}/config.lua",
                    "content": config_content,
                    "install_statu": False,
                }
                _install_script("luarocks_config")
                if not mingw_statu:
                    _install_sftw("mingw-lite")
                    if os.path.exists(mingw_root) and not os.path.exists(mingw_root_to_lua):
                        os.rename(mingw_root, mingw_root_to_lua)
                elif os.path.exists(mingw_root) and not os.path.exists(mingw_root_to_lua):
                    shutil.copytree(mingw_root, mingw_root_to_lua)
            if tool_name == "vcpkg":
                log_info("info->install DLC(vcpkg.exe) for...>vcpkg<")
                vcpkg_root = vpkg_tool["vcpkg"]["local_path"]
                _system_run_cmd([f"{vcpkg_root}/bootstrap-vcpkg.bat"])
            if tool_name == "msvc_kit":
                log_info("info->install DLC(msvc_kit) for...>msvc_kit<")
                msvc_kit_root = vpkg_tool["msvc_kit"]["local_path"]
                msvc_kit_excu = vpkg_tool["msvc_kit"]["symbol_excu"]
                msvc_kit_excu_copy = f"{msvc_kit_root}/msvc_kit.exe"
                if not os.path.exists(msvc_kit_excu_copy):
                    shutil.copy2(msvc_kit_excu, msvc_kit_excu_copy)
                _system_run_cmd([msvc_kit_excu_copy, "bundle", "--accept-license",
                                 "--arch", "x64", "--output", msvc_kit_root])
            if tool_name == "msvc_delphier":
                log_info("info->install DLC(msvc_kit) for...>msvc_delphier<")
                msvc_root = vpkg_tool["msvc_delphier"]["local_path"]
                msvc_bat = vpkg_tool["msvc_delphier"]["symbol_excu"]
                msvc_bat_copy  = "%s/%s"%(msvc_root,"msvc_env.bat")
                if not os.path.exists(msvc_bat_copy):
                    shutil.copy2(msvc_bat,msvc_bat_copy)
            if tool_name == "msvc_chnlm":
                log_info("info->install DLC(msvc_kit) for...>msvc_chnlm<")
                msvc_root = vpkg_tool["msvc_chnlm"]["local_path"]
                msvc_bat = vpkg_tool["msvc_chnlm"]["symbol_excu"]
                msvc_bat_copy  = "%s/%s"%(msvc_root,"msvc_env.bat")
                if not os.path.exists(msvc_bat_copy):
                    shutil.copy2(msvc_bat,msvc_bat_copy)
            return vpkg_retvalu

        def _run(tool_name: str) -> str:
            log_info("info->cheak the repo for aim sftw...")
            if not tool_name or tool_name == vpkg_retvalu:
                log_erro("erro->command “install” argu is empty...")
                return vpkg_retvalu
            if tool_name not in vpkg_tool:
                log_erro(f"erro->platform...>{vpkg_info['platform']}<...the repo not contain...>{tool_name}<")
                return vpkg_retvalu
            log_info("info->check the basic sftw...")
            if not _check_basic_sftw_statu():    # ★ 修复：去掉函数对象 == False 的错误比较
                log_erro(f"erro->lack of basic sftw...>{vpkg_tool_basic}<")
                return vpkg_retvalu
            if vpkg_tool[tool_name]["install_statu"]:
                log_info(f"info->the sftw >{tool_name}< already install!!!")
                return vpkg_retvalu
            _install_sftw(tool_name)
            _unique_handle(tool_name)
            if not os.path.exists(vpkg_tool[tool_name]["symbol_excu"]):
                log_erro(f"erro->install faild...>{tool_name}<")
                return vpkg_retvalu
            log_info(f"info->install success...>{tool_name}<")
            return vpkg_retvalu

        _run(cmd_valu)
        return vpkg_retvalu

    def _cmd_remove(cmd_valu: str) -> str:
        tool_name = cmd_valu
        if tool_name in vpkg_tool_basic:
            log_erro(f"erro->can not remove the basic sftw...>{tool_name}<")
            return vpkg_retvalu
        if tool_name not in vpkg_tool:
            log_erro(f"erro->repo not exist...>{tool_name}<")
            return vpkg_retvalu
        if not vpkg_tool[tool_name]["install_statu"]:
            log_erro(f"erro->not install the sftw...>{tool_name}<")
            return vpkg_retvalu
        install_path = vpkg_tool[tool_name]["local_path"]
        install_path_father = os.path.split(install_path)[0]
        shutil.rmtree(install_path)
        if os.path.exists(install_path_father) and len(os.listdir(install_path_father)) == 0:
            shutil.rmtree(install_path_father)
        if tool_name == "pixi" and "prefix" in vpkg_script:
            prefix_path = vpkg_script["prefix"]["local_path"]
            if os.path.exists(prefix_path):
                os.remove(prefix_path)
        log_warn(f"warn->success remove sftw...>{tool_name}<")
        return vpkg_retvalu

    def _cmd_excu(cmd_valu: list) -> bool:
        if not cmd_valu:
            log_erro("erro->command “excu” argument is empty...")
            return False
        tool_name = cmd_valu[0]
        if tool_name in vpkg_tool:
            cmd = [vpkg_tool[tool_name]["symbol_excu"], *cmd_valu[1:]]
        elif tool_name in vpkg_script:
            cmd = ["cmd", "/k", vpkg_script[tool_name]["local_path"], *cmd_valu[1:]]
        else:
            log_erro(f"erro->platform...>{vpkg_info['platform']}<...repo not exist...>{tool_name}<")
            return False
        log_info(f"info->running command...\n\t{' '.join(cmd)}")
        result = subprocess.run(cmd)
        if result.returncode != 0:
            log_erro("erro->running command...erro exit!!!")
        return result.returncode == 0

    def _cmd_gen_conf(cmd_valu: list) -> str:
        out_file = f"{vpkg_root}/vpkg_tmp.txt"
        with open(out_file, "w", encoding="utf8") as f:
            f.write(vpkg_conf_default)
        log_warn(f"warn->export conf to...>{out_file}<")
        return vpkg_retvalu

    cmd_type, cmd_valu = _get_cli_arg()
    log_warn(f"warn->func extra_command: {cmd_type}...{cmd_valu}")
    if cmd_type not in vpkg_cmd:
        log_erro(f"erro->vpkg not support command...>{cmd_type}<")
        return vpkg_retvalu
    if cmd_type == "help":
        _cmd_help(cmd_valu)
    if cmd_type == "list":
        _cmd_list(cmd_valu)
    if cmd_type == "install":
        _cmd_install(cmd_valu[0] if cmd_valu else vpkg_retvalu)
    if cmd_type == "remove":
        _cmd_remove(cmd_valu[0] if cmd_valu else vpkg_retvalu)
    if cmd_type == "shell":
        _cmd_shell(cmd_valu)
    if cmd_type == "excu":
        _cmd_excu(cmd_valu)
    if cmd_type == "gen_conf":
        _cmd_gen_conf(cmd_valu)
    return vpkg_retvalu

def main() -> str:
    init_program()
    log_info(f"info->vpkg local_path...>{vpkg_root}<")
    log_info(f"info->vpkg config_file path...>{vpkg_conf_path}<")
    log_info(f"info->vpkg config_file exist...>{os.path.exists(vpkg_conf_path)}<")
    extra_config()
    _info_width = max(len(k) for k in vpkg_info.keys())
    _info_rows = ["info->vpkg_info:"]
    for _k, _v in vpkg_info.items():
        _info_rows.append("    {key:<{width}} -> {val}".format(key=_k, width=_info_width, val=_v))
    log_info("\n".join(_info_rows))
    extra_command()
    return vpkg_retvalu

if __name__ == "__main__":
    main()