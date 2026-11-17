# lastEdit=>2026.11.17-21:17
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
        # --------------安装脚本<需要使用python,暂时不使用该方案>
        # <local_path>=https://raw.githubusercontent.com/luarocks/hererocks/master/hererocks.py
        # --------------项目地址
        # "https://sourceforge.net/projects/luabinaries/files/5.5.0/Tools%20Executables/lua-5.5.0_Win64_bin.zip",
        # "https://sourceforge.net/projects/luabinaries/files/5.5.0/Windows%20Libraries/Static/lua-5.5.0_Win64_mingw6_lib.zip",
        # "https://sourceforge.net/projects/luabinaries/files/5.5.0/Windows%20Libraries/Static/lua-5.5.0_Win64_vc17_lib.zip",
        # "https://github.com/luarocks/luarocks/releases/download/v3.12.2/luarocks-3.12.2-windows-64.zip",
        # --------------代理下载
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
def init_program():
    global vpkg_root
    global vpkg_root_system
    global vpkg_root_tool
    global vpkg_root_script
    global vpkg_root_cache
    global vpkg_root_extra
    global vpkg_conf_path
    global vpkg_conf_symbol
    global vpkg_info
    global vpkg_infoFmt
    global vpkg_info_kwOrder
    global vpkg_tool
    global vpkg_toolFmt
    global vpkg_tool_kwOrder
    global vpkg_script
    global vpkg_scriptFmt
    global vpkg_script_kwOrder
    global vpkg_retvalu
    global vpkg_cmd
    global vpkg_zip_ext
    global vpkg_tool_basic
    global vpkg_download_proxy
    global vpkg_conf
    # 判断是否是 PyInstaller 打包后的环境
    if getattr(sys, 'frozen', False):   # 如果是打包后的 exe，获取 exe 所在的目录
        vpkg_root = os.path.dirname(sys.executable)
    else:   # 如果是直接运行 .py 源文件，获取当前脚本所在的目录
        script_path = os.path.abspath(__file__)
        vpkg_root = os.path.dirname(script_path)
    vpkg_root = vpkg_root.replace("\\","/")
    vpkg_conf_path = vpkg_root+"/vpkg_config.txt"
    vpkg_conf_symbol = (
        "info->vpkg",
        "info->tool",
        "info->script",
    )
    vpkg_info_kwOrder = (
        "platform",
        "name",
        "version",
        "website",
        "autor",
        "publish",
        "description",
        "proxy",
    )
    vpkg_infoFmt = {
        "platform": ("x64-win","x64-linux","x64-mac","x64-unix")[0],
        "name": "vpkg",
        "version": "v20261112",
        "website": "https://github.com/vgtxc/vpkg",
        "autor": "vgtxc",
        "publish": "20261112",
        "description": "A lightWight portable software package manager!!!",
        "proxy": False,
    }
    vpkg_toolFmt = {
        "platform": str(),
        "name": str(),
        "version": str(),
        "website": str(),
        "local_path": str(),
        "symbol_excu": str(),
        "install": str(),
        "env_arg": str(),
        "install_statu": bool(),    # 由软件判断赋值, 不通过配置文件获取
    }
    vpkg_scriptFmt = {
        "platform": str(),
        "name": str(),
        "version": str(),
        "website": str(),
        "local_path": str(),
        "content": str(),
        "install_statu": bool(),    # 由软件判断赋值, 不通过配置文件获取
    }
    vpkg_tool_kwOrder = (
        "platform",
        "name",
        "version",
        "website",
        "local_path",
        "symbol_excu",
        "install",
        "env_arg",
        "install_statu",
    )
    vpkg_script_kwOrder = (
        "platform",
        "name",
        "version",
        "website",
        "local_path",
        "content",
        "install_statu",
    )
    vpkg_tool_basic = (
        "a7z",
        "aria2",
        # "wget",
        # "fastCapture",
    )
    vpkg_cmd = (
        "help",
        "list",
        "install",
        "remove",
        "shell",
        "excu",
        "gen_conf",
    )
    vpkg_root_system = "{vpkg_root}/{platform}"
    vpkg_root_tool = "{vpkg_root_system}/tool"
    vpkg_root_script = "{vpkg_root_system}/script"
    vpkg_root_cache = "{vpkg_root_system}/cache"
    vpkg_root_extra =  "{vpkg_root_system}/cache/extra_dir"
    vpkg_zip_ext = {
        "single_file": (".7z",".zip",".rar",".7z.exe",),
        "multi_7z": (".7z.001",".7z.002",".7z.003",".7z.004",".7z.005",".7z.006",),
        "multi_zip": (".zip.001",".zip.002",".zip.003",".zip.004",".zip.005",".zip.006",),
        "multi_rar": (".part001.rar",".part002.rar",".part003.rar",".part004.rar",".part005.rar",".part006.rar",),
        "default": (
            ".7z",".zip",".rar",".7z.exe",
            ".7z.001",
            ".zip.001",
            ".part001.rar",
        ),
        "filter": (
            ".7z",".zip",".rar",".7z.exe",
            ".7z.001",".7z.002",".7z.003",".7z.004",".7z.005",".7z.006",
            ".zip.001",".zip.002",".zip.003",".zip.004",".zip.005",".zip.006",
            ".part001.rar",".part002.rar",".part003.rar",".part004.rar",".part005.rar",".part006.rar",
        ),
    }
    vpkg_download_proxy = {     # 采用xget代理: https://github.com/xixu-me/xget
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
def extra_config():
    # 条目匹配
    def _item_match():
        vpkg_sftw_pattern = (
            "info->vpkg\n",
            " "*4+"platform:(?P<platform>.*)\n",
            " "*4+"name:(?P<name>.*)\n",
            " "*4+"version:(?P<version>.*)\n",
            " "*4+"website:(?P<website>.*)\n",
            " "*4+"autor:(?P<autor>.*)\n",
            " "*4+"publish:(?P<publish>.*)\n",
            " "*4+"description:(?P<description>.*)\n",
            " "*4+"proxy:(?P<proxy>.*)\n",
            "over->vpkg",
        )
        vpkg_tool_pattern = (
            "info->tool\n",
            " "*4+"platform:(?P<platform>.*)\n",
            " "*4+"name:(?P<name>.*)\n",
            " "*4+"version:(?P<version>.*)\n",
            " "*4+"website:(?P<website>.*)\n",
            " "*4+"local_path:(?P<local_path>.*)\n",
            " "*4+"symbol_excu:(?P<symbol_excu>.*)\n",
            " "*4+"init->install(?P<install>.*)over->install\n",
            " "*4+"init->env_arg(?P<env_arg>.*)over->env_arg\n",
            "over->tool",
        )
        vpkg_script_pattern = (
            "info->script\n",
            " "*4+"platform:(?P<platform>.*)\n",
            " "*4+"name:(?P<name>.*)\n",
            " "*4+"version:(?P<version>.*)\n",
            " "*4+"website:(?P<website>.*)\n",
            " "*4+"local_path:(?P<local_path>.*)\n",
            " "*4+"init->content(?P<content>.*)over->content\n",
            "over->script",
        )
        with open(vpkg_conf_path,"r",encoding="utf8") as f:
            config_file_content = f.read()
        vpkg_conf = config_file_content + vpkg_conf_default
        vpkg_conf = re.sub(r"#.*$","",vpkg_conf,flags=re.MULTILINE)
        vpkg_conf = vpkg_conf.split("\n")
        vpkg_conf = [idx for idx in vpkg_conf if idx not in ["","\t"," "*4," "*8," "*12," "*16]]
        vpkg_conf_len = len(vpkg_conf)
        vpkg_conf_splitIdx = [idx for idx in range(vpkg_conf_len) if (vpkg_conf[idx] in vpkg_conf_symbol) or idx==vpkg_conf_len]
        vpkg_conf_splitIdx.append(vpkg_conf_len)
        vpkg_conf_splitIdx_len = len(vpkg_conf_splitIdx)
        for idx in range(vpkg_conf_splitIdx_len-1):
            tmp_split_part = vpkg_conf[vpkg_conf_splitIdx[idx]:vpkg_conf_splitIdx[idx+1]]
            tmp_split_part_string = "\n".join(tmp_split_part)
            if tmp_split_part[0] == "info->vpkg":
                tmp_match_pattern = vpkg_sftw_pattern
                tmp_match_result = re.match(r"".join(tmp_match_pattern),tmp_split_part_string)
                if tmp_match_result==None:
                    log_erro("erro->func:<extra_config>...config file “sftw” syntax panic!!!")
                    log_erro("...source config_file part as follow...")
                    log_warn(tmp_split_part_string)
                    log_erro("...source config_file part over...")
                    break
                tmp_vpkg_platform = tmp_match_result.group("platform").strip()
                tmp_vpkg_name = tmp_match_result.group("name").strip()
                tmp_vpkg_version = tmp_match_result.group("version").strip()
                tmp_vpkg_website = tmp_match_result.group("website").strip()
                tmp_vpkg_autor = tmp_match_result.group("autor").strip()
                tmp_vpkg_publish = tmp_match_result.group("publish").strip()
                tmp_vpkg_description = tmp_match_result.group("description").strip()
                tmp_vpkg_proxy = False
                if tmp_match_result.group("proxy").strip() == "True":
                    tmp_vpkg_proxy = True
                vpkg_info.update({
                    "platform": tmp_vpkg_platform,
                    "name": tmp_vpkg_name,
                    "version": tmp_vpkg_version,
                    "website": tmp_vpkg_website,
                    "autor": tmp_vpkg_autor,
                    "publish": tmp_vpkg_publish,
                    "description": tmp_vpkg_description,
                    "proxy": tmp_vpkg_proxy,
                })
                continue
            if tmp_split_part[0] == "info->tool":
                tmp_match_pattern = vpkg_tool_pattern
                tmp_match_result = re.match(r"".join(tmp_match_pattern),tmp_split_part_string,re.S)
                if tmp_match_result==None:
                    log_erro("erro->func:<extra_config>...config file “tool” syntax panic!!!")
                    log_erro("...source config_file part as follow...")
                    log_warn(tmp_split_part_string)
                    log_erro("...source config_file part over...")
                    continue
                tmp_tool_platform =  tmp_match_result.group("platform").strip()
                tmp_tool_name =  tmp_match_result.group("name").strip()
                tmp_tool_version =  tmp_match_result.group("version").strip()
                tmp_tool_website =  tmp_match_result.group("website").strip()
                tmp_tool_local_path = tmp_match_result.group("local_path").strip()
                tmp_tool_symbol_excu = tmp_match_result.group("symbol_excu").strip()
                tmp_tool_install =  tmp_match_result.group("install").split("\n")
                tmp_tool_env_arg =  tmp_match_result.group("env_arg").split("\n")
                if tmp_tool_platform!=vpkg_info["platform"]:
                    log_warn("warn->{tool_name}...{platformA}...not match system platform...{platformB}!!!".format(tool_name=tmp_tool_name,platformA=tmp_tool_platform,platformB=vpkg_info["platform"]))
                    continue
                tmp_tool_install_dict = dict()
                tmp_tool_env_arg_dict = dict()
                for idx1 in tmp_tool_install:
                    tmp_install_line = idx1.strip()
                    if not tmp_install_line:
                        continue
                    tmp_install_line = tmp_install_line.split("=")
                    tmp_install_path = tmp_install_line[0].strip()
                    tmp_install_url = tmp_install_line[1].strip()
                    if tmp_install_path not in tmp_tool_install_dict.keys():
                        tmp_tool_install_dict[tmp_install_path] = [tmp_install_url]
                        continue
                    tmp_tool_install_dict[tmp_install_path].append(tmp_install_url)
                for idx1 in tmp_tool_env_arg:
                    tmp_env_arg_line = idx1.strip()
                    if not tmp_env_arg_line:
                        continue
                    tmp_env_arg_line = tmp_env_arg_line.split("=")
                    tmp_env_arg_name = tmp_env_arg_line[0].strip()
                    tmp_env_arg_value = tmp_env_arg_line[1].strip()
                    if tmp_env_arg_name not in tmp_tool_env_arg_dict.keys():
                        tmp_tool_env_arg_dict[tmp_env_arg_name] = [tmp_env_arg_value]
                        continue
                    tmp_tool_env_arg_dict[tmp_env_arg_name].append(tmp_env_arg_value)
                vpkg_tool[tmp_tool_name] = {
                    "platform": tmp_tool_platform,
                    "name": tmp_tool_name,
                    "version": tmp_tool_version,
                    "website": tmp_tool_website,
                    "local_path": tmp_tool_local_path,
                    "symbol_excu": tmp_tool_symbol_excu,
                    "install": tmp_tool_install_dict,
                    "env_arg": tmp_tool_env_arg_dict,
                }
                continue
            if tmp_split_part[0] == "info->script":
                tmp_match_pattern = vpkg_script_pattern
                tmp_match_result = re.match(r"".join(tmp_match_pattern),tmp_split_part_string,re.S)
                if tmp_match_result==None:
                    log_erro("erro->func:<extra_config>...config file “tool” syntax panic!!!")
                    log_erro("...source config_file part as follow...")
                    log_warn(tmp_split_part_string)
                    log_erro("...source config_file part over...")
                    continue
                tmp_script_platform =  tmp_match_result.group("platform").strip()
                tmp_script_name = tmp_match_result.group("name").strip()
                tmp_script_version = tmp_match_result.group("version").strip()
                tmp_script_website = tmp_match_result.group("website").strip()
                tmp_script_local_path = tmp_match_result.group("local_path").strip()
                tmp_script_content = tmp_match_result.group("content").split("\n")
                if tmp_script_platform!=vpkg_info["platform"]:
                    log_warn("warn->{script_name}...{platformA}...not match system platform...{platformB}!!!".format(script_name=tmp_script_name,platformA=tmp_script_platform,platformB=vpkg_info["platform"]))
                    continue
                tmp_script_content_string = str()
                for idx1 in tmp_script_content:
                    if not idx1:
                        continue
                    tmp_script_content_string += idx1[8:]+"\n"
                vpkg_script[tmp_script_name] = {
                    "platform": tmp_script_platform,
                    "name": tmp_script_name,
                    "version": tmp_script_version,
                    "website": tmp_script_website,
                    "local_path": tmp_script_local_path,
                    "content": tmp_script_content_string,
                }
                continue
        return vpkg_retvalu
    # 条目关键词自引用解引用
    def _item_extra():
        for tool_name in vpkg_tool.keys():
            tmp_tool_platform = vpkg_tool[tool_name]["platform"]
            tmp_tool_name = vpkg_tool[tool_name]["name"]
            tmp_tool_version = vpkg_tool[tool_name]["version"]
            tmp_tool_website = vpkg_tool[tool_name]["website"]
            tmp_tool_local_path = vpkg_tool[tool_name]["local_path"]
            tmp_tool_symbol_excu = vpkg_tool[tool_name]["symbol_excu"]
            tmp_tool_install_dict = vpkg_tool[tool_name]["install"]
            tmp_tool_env_arg_dict = vpkg_tool[tool_name]["env_arg"]
            # local_path解引用
            tmp_tool_local_path = tmp_tool_local_path.replace("{vpkg_root}",vpkg_root)
            tmp_tool_local_path = tmp_tool_local_path.replace("{vpkg_system}",vpkg_root_system)
            tmp_tool_local_path = tmp_tool_local_path.replace("{vpkg_tool}",vpkg_root_tool)
            tmp_tool_local_path = tmp_tool_local_path.replace("{vpkg_script}",vpkg_root_script)
            tmp_tool_local_path = tmp_tool_local_path.replace("{vpkg_cache}",vpkg_root_cache)
            tmp_tool_local_path = tmp_tool_local_path.replace("<platform>",tmp_tool_platform)
            tmp_tool_local_path = tmp_tool_local_path.replace("<name>",tmp_tool_name)
            tmp_tool_local_path = tmp_tool_local_path.replace("<version>",tmp_tool_version)
            # symbol_excu解引用
            tmp_tool_symbol_excu = tmp_tool_symbol_excu.replace("{vpkg_root}",vpkg_root)
            tmp_tool_symbol_excu = tmp_tool_symbol_excu.replace("{vpkg_system}",vpkg_root_system)
            tmp_tool_symbol_excu = tmp_tool_symbol_excu.replace("{vpkg_tool}",vpkg_root_tool)
            tmp_tool_symbol_excu = tmp_tool_symbol_excu.replace("{vpkg_script}",vpkg_root_script)
            tmp_tool_symbol_excu = tmp_tool_symbol_excu.replace("{vpkg_cache}",vpkg_root_cache)
            tmp_tool_symbol_excu = tmp_tool_symbol_excu.replace("<platform>",tmp_tool_platform)
            tmp_tool_symbol_excu = tmp_tool_symbol_excu.replace("<name>",tmp_tool_name)
            tmp_tool_symbol_excu = tmp_tool_symbol_excu.replace("<version>",tmp_tool_version)
            tmp_tool_symbol_excu = tmp_tool_symbol_excu.replace("<local_path>",tmp_tool_local_path)
            vpkg_tool[tool_name]["local_path"] = tmp_tool_local_path
            vpkg_tool[tool_name]["symbol_excu"] = tmp_tool_symbol_excu
            # install解引用
            tmp_tool_install_dict_new = dict()
            for idx1 in tmp_tool_install_dict.keys():
                tmp_key = idx1
                tmp_val = tmp_tool_install_dict[idx1]
                tmp_key = tmp_key.replace("{vpkg_root}",vpkg_root)
                tmp_key = tmp_key.replace("{vpkg_system}",vpkg_root_system)
                tmp_key = tmp_key.replace("{vpkg_tool}",vpkg_root_tool)
                tmp_key = tmp_key.replace("{vpkg_script}",vpkg_root_script)
                tmp_key = tmp_key.replace("{vpkg_cache}",vpkg_root_cache)
                tmp_key = tmp_key.replace("<platform>",tmp_tool_platform)
                tmp_key = tmp_key.replace("<name>",tmp_tool_name)
                tmp_key = tmp_key.replace("<version>",tmp_tool_version)
                tmp_key = tmp_key.replace("<website>",tmp_tool_version)
                tmp_key = tmp_key.replace("<local_path>",tmp_tool_local_path)
                tmp_key = tmp_key.replace("<symbol_excu>",tmp_tool_local_path)
                tmp_new_key = tmp_key
                tmp_new_val = list()
                for idx2 in range(len(tmp_val)):
                    tmp_val_elem = tmp_val[idx2]
                    tmp_val_elem = tmp_val_elem.replace("{vpkg_root}",vpkg_root)
                    tmp_val_elem = tmp_val_elem.replace("{vpkg_system}",vpkg_root_system)
                    tmp_val_elem = tmp_val_elem.replace("{vpkg_tool}",vpkg_root_tool)
                    tmp_val_elem = tmp_val_elem.replace("{vpkg_script}",vpkg_root_script)
                    tmp_val_elem = tmp_val_elem.replace("{vpkg_cache}",vpkg_root_cache)
                    tmp_val_elem = tmp_val_elem.replace("<platform>",tmp_tool_platform)
                    tmp_val_elem = tmp_val_elem.replace("<name>",tmp_tool_name)
                    tmp_val_elem = tmp_val_elem.replace("<version>",tmp_tool_version)
                    tmp_val_elem = tmp_val_elem.replace("<website>",tmp_tool_version)
                    tmp_val_elem = tmp_val_elem.replace("<local_path>",tmp_tool_local_path)
                    tmp_val_elem = tmp_val_elem.replace("<symbol_excu>",tmp_tool_local_path)
                    tmp_new_val.append(tmp_val_elem)
                tmp_tool_install_dict_new[tmp_new_key] = tmp_new_val
            # env_arg解引用
            tmp_tool_env_arg_dict_new = dict()
            for idx1 in tmp_tool_env_arg_dict.keys():
                tmp_key = idx1
                tmp_val = tmp_tool_env_arg_dict[idx1]
                tmp_key = tmp_key.replace("{vpkg_root}",vpkg_root)
                tmp_key = tmp_key.replace("{vpkg_system}",vpkg_root_system)
                tmp_key = tmp_key.replace("{vpkg_tool}",vpkg_root_tool)
                tmp_key = tmp_key.replace("{vpkg_script}",vpkg_root_script)
                tmp_key = tmp_key.replace("{vpkg_cache}",vpkg_root_cache)
                tmp_key = tmp_key.replace("<platform>",tmp_tool_platform)
                tmp_key = tmp_key.replace("<name>",tmp_tool_name)
                tmp_key = tmp_key.replace("<version>",tmp_tool_version)
                tmp_key = tmp_key.replace("<website>",tmp_tool_version)
                tmp_key = tmp_key.replace("<local_path>",tmp_tool_local_path)
                tmp_key = tmp_key.replace("<symbol_excu>",tmp_tool_local_path)
                tmp_new_key = tmp_key
                tmp_new_val = list()
                for idx2 in range(len(tmp_val)):
                    tmp_val_elem = tmp_val[idx2]
                    tmp_val_elem = tmp_val_elem.replace("{vpkg_root}",vpkg_root)
                    tmp_val_elem = tmp_val_elem.replace("{vpkg_system}",vpkg_root_system)
                    tmp_val_elem = tmp_val_elem.replace("{vpkg_tool}",vpkg_root_tool)
                    tmp_val_elem = tmp_val_elem.replace("{vpkg_script}",vpkg_root_script)
                    tmp_val_elem = tmp_val_elem.replace("{vpkg_cache}",vpkg_root_cache)
                    tmp_val_elem = tmp_val_elem.replace("<platform>",tmp_tool_platform)
                    tmp_val_elem = tmp_val_elem.replace("<name>",tmp_tool_name)
                    tmp_val_elem = tmp_val_elem.replace("<version>",tmp_tool_version)
                    tmp_val_elem = tmp_val_elem.replace("<website>",tmp_tool_version)
                    tmp_val_elem = tmp_val_elem.replace("<local_path>",tmp_tool_local_path)
                    tmp_val_elem = tmp_val_elem.replace("<symbol_excu>",tmp_tool_local_path)
                    tmp_new_val.append(tmp_val_elem)
                tmp_tool_env_arg_dict_new[tmp_new_key] = tmp_new_val
            vpkg_tool[tool_name]["install"] = tmp_tool_install_dict_new
            vpkg_tool[tool_name]["env_arg"] = tmp_tool_env_arg_dict_new
        # script条目解引用
        for script_name in vpkg_script.keys():
            tmp_script_platform = vpkg_script[script_name]["platform"]
            tmp_script_name = vpkg_script[script_name]["name"]
            tmp_script_version = vpkg_script[script_name]["version"]
            tmp_script_website = vpkg_script[script_name]["website"]
            tmp_script_local_path = vpkg_script[script_name]["local_path"]
            tmp_script_content = vpkg_script[script_name]["content"]
            tmp_script_local_path = tmp_script_local_path.replace("{vpkg_root}",vpkg_root)
            tmp_script_local_path = tmp_script_local_path.replace("{vpkg_system}",vpkg_root_system)
            tmp_script_local_path = tmp_script_local_path.replace("{vpkg_tool}",vpkg_root_tool)
            tmp_script_local_path = tmp_script_local_path.replace("{vpkg_script}",vpkg_root_script)
            tmp_script_local_path = tmp_script_local_path.replace("{vpkg_cache}",vpkg_root_cache)
            tmp_script_local_path = tmp_script_local_path.replace("<platform>",tmp_script_platform)
            tmp_script_local_path = tmp_script_local_path.replace("<name>",tmp_script_platform)
            tmp_script_local_path = tmp_script_local_path.replace("<version>",tmp_script_platform)
            vpkg_script[script_name]["local_path"] = tmp_script_local_path
        return vpkg_retvalu
    # 检测软件安装状态
    def _item_check():
        vpkg_sftw_platform = vpkg_info["platform"]
        del_sftw_tool = list()
        del_sftw_script = list()
        # 删除不匹配平台的项目
        for idx in vpkg_tool.keys():
            sftw_platform = vpkg_tool[idx]["platform"]
            if sftw_platform!=vpkg_sftw_platform:
                del_sftw_tool.append(idx)
        for idx in vpkg_script.keys():
            sftw_platform = vpkg_script[idx]["platform"]
            if sftw_platform!=vpkg_sftw_platform:
                del_sftw_script.append(idx)
        for idx in del_sftw_tool:
            del vpkg_tool[idx]
        for idx in del_sftw_script:
            del vpkg_script[idx]
        # 检测必要的文件目录,不存在则创建
        for idx in (vpkg_root_cache,vpkg_root_tool,vpkg_root_script):
            if not os.path.exists(idx):
                os.mkdir(idx)
                log_warn("info->creat dir...>%s<"%(idx))
        # 检查软件安装状态
        for idx in vpkg_tool.keys():
            vpkg_tool[idx]["install_statu"] = os.path.exists(vpkg_tool[idx]["symbol_excu"])
        for idx in vpkg_script.keys():
            vpkg_script[idx]["install_statu"] = os.path.exists(vpkg_script[idx]["local_path"])
        # 特殊处理
        def _unique_handle():
            if vpkg_tool["pixi"]["install_statu"] == True:
                pixi_excu = vpkg_tool["pixi"]["symbol_excu"]
                pixi_home = vpkg_tool["pixi"]["local_path"]
                vpkg_script["prefix"] = {
                    "platform": "x64-win",
                    "name": "prefix",
                    "version": "1.0",
                    "website": "void",
                    "local_path": "{vpkg_script}/prefix.bat".format(vpkg_script=vpkg_root_script),
                    "content": "@echo off\ncall {pixi_excu} shell --manifest-path {pixi_config}".format(pixi_excu=vpkg_tool["pixi"]["symbol_excu"],pixi_config="%s/pixi.toml"%(vpkg_tool["pixi"]["local_path"])),
                    "install_statu": True,
                }
            return vpkg_retvalu
        _unique_handle()
        return vpkg_retvalu
    # 解引用路径全局变量
    def vpkg_root_extra():
        global vpkg_root_system
        global vpkg_root_tool
        global vpkg_root_script
        global vpkg_root_cache
        global vpkg_root_extra
        vpkg_platform = vpkg_info["platform"]
        vpkg_root_system = "%s/%s"%(vpkg_root,vpkg_platform)
        vpkg_root_tool = "%s/tool"%(vpkg_root_system)
        vpkg_root_script = "%s/script"%(vpkg_root_system)
        vpkg_root_cache = "%s/cache"%(vpkg_root_system)
        vpkg_root_extra = "%s/cache/extra"%(vpkg_root_system)
        return vpkg_retvalu
    # 安装脚本
    def _install_script():
        for idx in vpkg_script.keys():
            script_path = vpkg_script[idx]["local_path"]
            install_statu = vpkg_script[idx]["install_statu"]
            if install_statu == True:
                continue
            with open(script_path,"w") as f:
                f.write(vpkg_script[idx]["content"])
            log_info("info->func:extra_config._install_script, install script...>%s<"%(script_path))
    # 配置文件判断
    if os.path.exists(vpkg_conf_path) == False:
        log_warn("warn->config file miss...>%s<"%(vpkg_conf_path))
        vpkg_root_extra()
        _item_extra()
        _item_check()
        _install_script()
        return vpkg_retvalu
    _item_match()
    vpkg_root_extra()
    _item_extra()
    _item_check()
    _install_script()
    return vpkg_retvalu

# ================= 02.命令解析 =================
def extra_command():
    def _check_basic_sftw_statu():
        sftw_statu = False
        for idx in vpkg_tool_basic:
            install_statu = vpkg_tool[idx]["install_statu"]
            if install_statu == False:
                sftw_statu = False
                log_erro("erro->lack of basic sftw...>%s<"%(idx))
        return sftw_statu
    def _get_cli_arg():     # 获取命令行命令
        sys_argv = sys.argv
        if len(sys_argv)==1:
            return (vpkg_retvalu,list())
        return (sys_argv[1],sys_argv[2:])
    def _clean_dir(aim_path):     # 清除临时文件夹
        if os.path.exists(aim_path) == False:
            log_warn("warn->not exists the dir...>%s<"%(aim_path))
            return vpkg_retvalu
        shutil.rmtree(aim_path)
        os.mkdir(aim_path)
        log_warn("warn->clean the dir...>%s<"%(aim_path))
    def _system_run_cmd(cmd):
        result = subprocess.run(cmd)
        if result.returncode != 0:
            log_erro("erro->_system_run_cmd...%s"%(cmd))
        return result.returncode == 0
    def _file_download(file_url, out_dir):
        file_url_real = file_url
        out_dir_real = out_dir
        if vpkg_info["proxy"]==True:    # 开启代理, 进行url替换
            for idx in vpkg_download_proxy.keys():
                if idx in file_url_real:
                    file_url_real = file_url_real.replace(idx,vpkg_download_proxy[idx])
        aria2_statu = vpkg_tool["aria2"]["install_statu"]
        aria2_excu = vpkg_tool["aria2"]["symbol_excu"]
        wget_statu = vpkg_tool["wget"]["install_statu"]
        wget_excu = vpkg_tool["wget"]["symbol_excu"]
        cmd = [aria2_excu, file_url_real, "--dir=%s"%(out_dir_real), "--allow-overwrite=true", "--max-connection-per-server=16", "--min-split-size=1M"]
        if aria2_statu == False and wget_statu == True:     # 默认aria2下载, 其次wget
            cmd = [wget_excu, "-P",  out_dir_real, file_url_real]
        log_info("info->running command...\n\t%s" % " ".join(cmd))
        result = subprocess.run(cmd)
        if result.returncode != 0:
            log_erro("erro->download failed (code=%d): %s" % (result.returncode, file_url))
            return False
        return True
    def _file_unzip(file_path, out_dir):
        unzip_cmd_tool = vpkg_tool["a7z"]["symbol_excu"]
        cmd = [unzip_cmd_tool, "x", file_path, "-o" + out_dir, "-y"]
        log_info("info->running command...\n\t%s" % " ".join(cmd))
        result = subprocess.run(cmd)
        if result.returncode != 0:
            log_erro("erro->unzip failed (code=%d): %s" % (result.returncode, file_path))
        return result.returncode == 0
    def _cmd_help(cmd_valu):    # 命令_帮助
        log_warn("info->vpkg sftw info start!!!")
        for idx in vpkg_info.keys():
            log_info("\t%-12s->\t%s" % (idx, vpkg_info[idx]))
        log_warn("info->vpkg usage...>vpkg \\[command] \\[argument]<")
        for idx in vpkg_cmd:
            log_info("\tsupport command: {cmd}".format(cmd=idx))
        log_warn("info->vpkg sftw info end!!!")
        return vpkg_retvalu
    def _cmd_list(cmd_valu):    # 命令_列出软件
        log_warn("info->list software install status!!!")
        log_info("\t"+"-"*40)
        log_info("\t%-15s->%-15s->%-10s"%("tool_name","install_status","website"))
        log_info("\t"+"-"*40)
        for idx in vpkg_tool.keys():
            tmp_tool_name = vpkg_tool[idx]["name"]
            tmp_tool_install_statu = vpkg_tool[idx]["install_statu"]
            tmp_tool_website = vpkg_tool[idx]["website"]
            if tmp_tool_install_statu == True:
                log_info("\t%-15s->%-15s->%-10s"%(tmp_tool_name,tmp_tool_install_statu,tmp_tool_website))
                continue
            log_erro("\t%-15s->%-15s->%-10s"%(tmp_tool_name,tmp_tool_install_statu,tmp_tool_website))
        log_info("\n")
        log_info("\t"+"-"*40)
        log_info("\t%-15s->%-15s->%-10s"%("script_name","install_status","website"))
        log_info("\t"+"-"*40)
        for idx in vpkg_script.keys():
            tmp_script_name = vpkg_script[idx]["name"]
            tmp_script_install_statu = vpkg_script[idx]["install_statu"]
            tmp_script_website = vpkg_script[idx]["website"]
            if tmp_script_install_statu == True:
                log_info("\t%-15s->%-15s->%-10s"%(tmp_script_name,tmp_script_install_statu,tmp_script_website))
                continue
            log_erro("\t%-15s->%-15s->%-10s"%(tmp_script_name,tmp_script_install_statu,tmp_script_website))
        log_info("\t"+"-"*40)
    def _cmd_shell(cmd_valu):
        origin_var = os.environ.copy()
        shell_var = {}
        path_key = "PATH"
        for idx in origin_var.keys():
            shell_var[idx] = origin_var[idx].replace("\\", "/")   # 保留原名
            if idx.lower() == "path":
                path_key = idx
        # 后续合并 sftw env_arg 时用 path_key 而不是硬编码 "path"
        for idx in vpkg_tool.keys():
            if vpkg_tool[idx]["install_statu"] == False:
                continue
            for k, vlist in vpkg_tool[idx]["env_arg"].items():
                val = ";".join(vlist)
                # 找已有同名 key（大小写不敏感），不存在就用 k
                existing = next((ek for ek in shell_var if ek.lower() == k.lower()), None)
                if existing:
                    shell_var[existing] = "%s;%s" % (shell_var[existing], val)
                else:
                    shell_var[k] = val
        shell_var[path_key] = "%s;%s" % (shell_var[path_key], vpkg_root_script)
        if os.name == "nt":
            new_shell_arg = "title vpkg && prompt (vpkg) $P$G"
            subprocess.run(["cmd", "/k", new_shell_arg], env=shell_var)
            sys.exit(0)
        return vpkg_retvalu
    def _cmd_install(cmd_valu): # 命令_安装软件
        def _get_file_and_dir(aim_path):
            file_list = list()
            dir_list = list()
            for idx in os.scandir(aim_path):
                if idx.is_file():
                    file_list.append(idx.path)
                if idx.is_dir():
                    dir_list.append(idx.path)
            return (file_list,dir_list)
        def _get_differ_item(listA,listB):
            differ_list = list()
            for item in listB:
                if item not in listA:
                    differ_list.append(item)
            return differ_list
        def _get_stop_dir(aim_path):
            current = aim_path
            while True:
                entries = os.listdir(current)
                # 过滤掉隐藏文件（按需保留/删除这一行）
                entries = [e for e in entries if not e.startswith('.')]
                # 子目录列表
                subdirs = [e for e in entries if os.path.isdir(os.path.join(current, e))]
                # 停止条件：不是「只有一个子目录且没有其他内容」
                if len(entries) != 1 or len(subdirs) != 1:
                    return current
                # 继续向下
                current = os.path.join(current, subdirs[0])
        def _install_script(script_name):
            if script_name not in vpkg_script.keys():
                log_erro("erro->not exist script config...>%s<"%(script_name))
                return vpkg_retvalu
            script_file = vpkg_script[script_name]["name"]
            script_path = vpkg_script[script_name]["local_path"]
            script_content = vpkg_script[script_name]["content"]
            with open(script_path,"w") as f:
                f.write(script_content)
            return vpkg_retvalu
        def _install_sftw(tool_name):
            cache_dir = vpkg_root_cache        # 缓存目录
            extra_dir = cache_dir+"/extra_dir"              # 解压目录
            _clean_dir(cache_dir)                         # 清空缓存目录
            if os.path.exists(extra_dir)==False:
                os.makedirs(extra_dir,exist_ok=True)
            cache_init_file, cache_init_dir = _get_file_and_dir(cache_dir) # 扫描文件夹和文件夹
            # (01)逐项下载文件
            for install_item in vpkg_tool[tool_name]["install"].keys():
                install_dir = install_item
                download_url_list = vpkg_tool[tool_name]["install"][install_item]
                os.makedirs(install_dir,exist_ok=True) # 创建目录树
                _clean_dir(install_dir)         # 清空目标安装目录
                for url in download_url_list:   # 下载文件到缓存目录
                    down_result = _file_download(url,cache_dir)
                    if not down_result:
                        log_erro("erro->abort install %s, download failed" % tool_name)
                        return vpkg_retvalu
                cache_over_file, _ = _get_file_and_dir(cache_dir)
                download_file_list = _get_differ_item(cache_init_file,cache_over_file)
                pack_file = list()
                move_file = list()
                for idx in download_file_list:  # 判断文件类型并处理
                    file = os.path.split(idx)[1]
                    ispack_flag = False
                    for pack_ext in vpkg_zip_ext["default"]:
                        if file.endswith(pack_ext):     # 压缩包文件
                            pack_file.append(idx)
                            ispack_flag = True
                            break
                    if ispack_flag == False:
                        move_file.append(idx)
                for idx in pack_file:
                    _clean_dir(extra_dir)
                    _file_unzip(idx,extra_dir)
                    unpack_dir = _get_stop_dir(extra_dir)
                    shutil.copytree(unpack_dir,install_dir,dirs_exist_ok=True)
                for idx in move_file:
                    old_file = idx
                    file = os.path.split(idx)[1]
                    new_file = os.path.join(install_dir,file)
                    os.rename(old_file,new_file)
            return vpkg_retvalu
        def _unique_handle(tool_name):
            if tool_name == "pixi":
                log_info("info->install DLC(init home) for...>pixi<")
                pixi_excu = vpkg_tool[tool_name]["symbol_excu"]
                pixi_home = vpkg_tool[tool_name]["local_path"]
                _system_run_cmd("%s init %s"%(pixi_excu,pixi_home))
                vpkg_script["prefix"] = {
                    "platform": "x64-win",
                    "name": "prefix",
                    "version": "1.0",
                    "website": "void",
                    "local_path": "{vpkg_script}/prefix.bat".format(vpkg_script=vpkg_root_script),
                    "content": "@echo off\ncall {pixi_excu} shell --manifest-path {pixi_config}".format(pixi_excu=vpkg_tool["pixi"]["symbol_excu"],pixi_config="%s/pixi.toml"%(vpkg_tool["pixi"]["local_path"])),
                    "install_statu": bool(),
                }
                _install_script("prefix")
            if tool_name == "python":
                log_info("info->install DLC(pip) for...>python<")
                path_install = list(vpkg_tool[tool_name]["install"].keys())[0]
                print(path_install)
                file_net_contorl = str()
                file_get_pip = str()
                file_python_excu = str()
                for idx in os.scandir(path_install):
                    file_path = idx.path
                    if file_path.endswith("._pth"):
                        file_net_contorl = file_path
                    if file_path.endswith("get-pip.py"):
                        file_get_pip = file_path
                    if file_path.endswith("python.exe"):
                        file_python_excu = file_path
                if file_net_contorl:
                    with open(file_net_contorl,"r") as f:
                        new_content = f.read()
                        new_content.replace("#import site","import site")
                    with open(file_net_contorl,"w") as f:
                        f.write(new_content)
                if file_net_contorl and file_get_pip and file_python_excu:
                    _system_run_cmd("{python} {get_pip_script}".format(python=file_python_excu,get_pip_script=file_get_pip))
            if tool_name == "rust":
                log_info("info->install DLC for...>rust<")
                rust_env_arg = vpkg_tool[tool_name]["env_arg"]
                rustup_home = rust_env_arg["rustup_home"][0]
                cargo_home = rust_env_arg["cargo_home"][0]
                os.environ["rustup_home"] = rustup_home
                os.environ["cargo_home"] = cargo_home
                rustup_excu = vpkg_tool[tool_name]["symbol_excu"]
                _system_run_cmd(rustup_excu)            
            if tool_name == "lua":
                log_info("info->install DLC(luarocks config.lua) for...>lua<")
                # lua信息
                lua_ver = "5.5.0"
                lua_root = vpkg_tool["lua"]["local_path"]
                lua_include = "%s/include"%(lua_root)
                lua_excu = vpkg_tool["lua"]["symbol_excu"]
                for file in os.listdir(lua_root):
                    if file.startswith("luac") and file.endswith(".exe"):
                        lua_excu = "%s/%s"%(lua_root,file)
                lua_excu_copy = "%s/lua.exe"%(lua_root)
                shutil.copy2(lua_excu,lua_excu_copy)
                # 安装mingw-lite信息
                mingw_lite_root = vpkg_tool["mingw-lite"]["local_path"]
                mingw_lite_statu = vpkg_tool["mingw-lite"]["install_statu"]
                # 移动mingw-lite信息
                mingw_lite_root_toLua = "%s/%s"%(lua_root,"mingw-lite")
                # luarocks配置文件
                config_content = (
                    'lua_version = "<lua_ver>"\n',
                    'rocks_trees = {\n',
                        '\t{name = "user",root = "<lua_root>",},\n',
                    '}\n',
                    'variables = {\n',
                        '\t-- C 编译器完整路径\n',
                        '\tcc = "<mingw_lite_root>/bin/gcc.exe",\n',
                        '\t-- C++ 编译器完整路径\n',
                        '\tcxx = "<mingw_lite_root>/bin/g++.exe",\n',
                        '\t-- 链接器(通常与 CC 相同)\n',
                        '\tld = "<mingw_lite_root>/bin/gcc.exe",\n',
                        '\t-- 可选：静态库打包工具\n',
                        '\tar = "<mingw_lite_root>/bin/ar.exe",\n',
                        '\tranlib = "D:/tool/mingw_w64/v16.2.0/bin/ranlib.exe",\n',
                        '\tlinkflags = "-shared",\n',
                        '\tlua_version = "<lua_ver>",\n',
                        '\tlua = "<lua_excu>",\n',
                        '\tlua_bindir = "<lua_root>",\n',
                        '\tlua_incdir = "<lua_include>",\n',
                        '\tlua_libdir = "<lua_root>",\n',
                    '}',
                )
                vpkg_script["luarocks_config"] = {
                    "platform": "x64-win",
                    "name": "luarocks_config",
                    "version": "v1.0",
                    "website": "void",
                    "local_path": "%s/config.lua"%(lua_root),
                    "content": "".join(config_content).replace(
                            "<mingw_lite_root>",mingw_lite_root_toLua
                        ).replace(
                            "<lua_ver>",lua_ver
                        ).replace(
                            "<lua_root>",lua_root
                        ).replace(
                            "<lua_excu>",lua_excu_copy
                        ).replace(
                            "<lua_include>",lua_include
                        ),
                    "install_statu": bool(),
                }
                # 配置luarocks配置文件
                _install_script("luarocks_config")
                # 配置mingw工具                
                if mingw_lite_statu == False:
                    # 安装配套gcc mingw-lite工具套
                    _install_sftw("mingw-lite")
                    # 将mingw-lite移动到指定lua路径下
                    os.rename(mingw_lite_root,mingw_lite_root_toLua)
                if mingw_lite_statu == True:
                    shutil.copytree(mingw_lite_root,mingw_lite_root_toLua)
            if tool_name == "vcpkg":
                log_info("info->install DLC(vcpkg.exe) for...>vcpkg<")
                vcpkg_root = vpkg_tool[tool_name]["local_path"]
                vcpkg_cmd = "%s/%s"%(vcpkg_root,"bootstrap-vcpkg.bat")
                _system_run_cmd(vcpkg_cmd)
            if tool_name == "msvc_kit":
                log_info("info->install DLC(vcpkg.exe) for...>msvc_kit<")
                msvc_kit_root = vpkg_tool["msvc_kit"]["local_path"]
                msvc_kit_excu = vpkg_tool["msvc_kit"]["symbol_excu"]
                msvc_kit_excu_copy = "%s/%s"%(msvc_kit_root,"msvc_kit.exe")
                shutil.copy2(msvc_kit_excu,msvc_kit_excu_copy)
                msvc_install_cmd = [msvc_kit_excu_copy,"bundle","--accept-license","--arch","x64","--output",msvc_kit_root]
                _system_run_cmd(msvc_install_cmd)
            if tool_name == "msvc_delphier":
                log_info("info->install DLC(vcpkg.exe) for...>msvc_delphier<")
                msvc_delphier_root = vpkg_tool["msvc_delphier"]["local_path"]
                msvc_delphier_excu = vpkg_tool["msvc_delphier"]["symbol_excu"]
                msvc_delphier_excu_copy = "%s/%s"%(msvc_delphier_root,"msvc_env.bat")
                shutil.copy(msvc_delphier_excu,msvc_delphier_excu_copy)
            if tool_name == "msvc_chnlm":
                log_info("info->install DLC(vcpkg.exe) for...>msvc_chnlm<")
                msvc_chnlm_root = vpkg_tool["msvc_chnlm"]["local_path"]
                msvc_chnlm_excu = vpkg_tool["msvc_chnlm"]["symbol_excu"]
                msvc_chnlm_excu_copy = "%s/%s"%(msvc_chnlm_root,"msvc_env.bat")
            return vpkg_retvalu
        def _run(tool_name):
            log_info("info->cheak the repo for aim sftw...")
            if not tool_name:
                log_erro("erro->command “install” argu is empty...")
                return vpkg_retvalu
            if tool_name not in vpkg_tool.keys():   # 检测软件是否存在软件库中
                platform = vpkg_info["platform"]
                repo = vpkg_conf_path
                tool_name = tool_name
                log_erro("erro->platform...>%s<...the repo not contain...>%s<"%(platform,tool_name))
                return vpkg_retvalu
            log_info("info->check the basic sftw...")
            if _check_basic_sftw_statu == False:
                log_erro("erro->lack of basic sftw...>%s<"%(vpkg_tool_basic))
                return vpkg_retvalu
            tool_statu = vpkg_tool[tool_name]["install_statu"]
            if tool_statu == True:
                log_info("info->the sftw >%s< already install!!!"%(tool_name))
                return vpkg_retvalu
            # ==========================软件安装: 下载解压================================
            _install_sftw(tool_name)
            # ==========================软件安装: 特殊处理================================
            _unique_handle(tool_name)
            # ===========================================================================
            tool_statu = os.path.exists(vpkg_tool[tool_name]["symbol_excu"])
            if tool_statu == False:
                log_erro("erro->install faild...>%s<"%(tool_name))
                return vpkg_retvalu
            log_info("info->install success...>%s<"%(tool_name))
            return vpkg_retvalu
        tool_name = cmd_valu
        _run(tool_name)
    def _cmd_remove(cmd_valu):  # 命令_卸载软件
        def _unique_handle(tool_name):
            if tool_name == "pixi":
                prefix_shell = vpkg_script["prefix"]["local_path"]
                if os.path.exists(prefix_shell):
                    os.remove(prefix_shell)
            return vpkg_retvalu
        tool_name = cmd_valu
        if tool_name in vpkg_tool_basic:
            log_erro("erro->can not remove the basic sftw...>%s<"%(tool_name))
            return vpkg_retvalu
        if tool_name not in vpkg_tool.keys():   # 检测软件是否存在软件库中
            log_erro("erro->repo not exist...>%s<"%(tool_name))
            return vpkg_retvalu
        if vpkg_tool[tool_name]["install_statu"] == False:
            log_erro("erro->not install the sftw...>%s<"%(tool_name))
            return vpkg_retvalu
        install_path = vpkg_tool[tool_name]["local_path"]
        install_path_father = os.path.split(install_path)[0]
        shutil.rmtree(install_path)
        if len(os.listdir(install_path_father))==0:
            shutil.rmtree(install_path_father)
        _unique_handle(tool_name)
        log_warn("warn->success remove sftw...>%s<"%(tool_name))
    def _cmd_excu(cmd_valu):    # 命令_运行安装软件
        tool_name = cmd_valu[0]
        if tool_name in vpkg_tool.keys():
            tool_excu = vpkg_tool[tool_name]["symbol_excu"]
            cmd = [tool_excu,]
            if len(cmd_valu)>1:
                cmd += cmd_valu[1:]
            log_info("info->running command...\n\t%s" % " ".join(cmd))
            result = subprocess.run(cmd)
            if result.returncode != 0:
                log_erro("erro->running command...erro exit!!!")
            return result.returncode == 0
        if tool_name in vpkg_script.keys():
            tool_excu = vpkg_script[tool_name]["local_path"]
            cmd = ["cmd","/k",tool_excu,]
            if len(cmd_valu)>1:
                cmd += cmd_valu[1:]
            log_info("info->running command...\n\t%s" % " ".join(cmd))
            result = subprocess.run(cmd)
            if result.returncode != 0:
                log_erro("erro->running command...erro exit!!!")
            return result.returncode == 0
        log_erro("erro->platform...>%s<...repo not exist...>%s<"%(vpkg_info["platform"],tool_name))
        return vpkg_retvalu
    def _cmd_gen_conf(cmd_valu):    # 命令_生成配置文件
        out_file = "%s/%s"%(vpkg_root,"vpkg_tmp.txt")
        with open(out_file,"w",encoding="utf8") as f:
            f.write(vpkg_conf_default)
        log_warn("warn->export conf to...>%s<"%(out_file))
        return vpkg_retvalu
    cmd_type,cmd_valu = _get_cli_arg()
    log_warn("warn->func extra_command: %s...%s"%(cmd_type,cmd_valu))
    if cmd_type not in vpkg_cmd:
        log_erro("erro->vpkg not support command...>%s<"%(cmd_type))
        return vpkg_retvalu
    if cmd_type == "help":
        _cmd_help(cmd_valu)
    if cmd_type == "list":
        _cmd_list(cmd_valu)
    if cmd_type == "install":
        tool_name = vpkg_retvalu
        if len(cmd_valu)>0:
            tool_name = cmd_valu[0]
        _cmd_install(tool_name)
    if cmd_type == "remove":
        tool_name = vpkg_retvalu
        if len(cmd_valu)>0:
            tool_name = cmd_valu[0]
        _cmd_remove(tool_name)
    if cmd_type == "shell":
        _cmd_shell(cmd_valu)
    if cmd_type == "excu":
        _cmd_excu(cmd_valu)
    if cmd_type == "gen_conf":  # 生成配置文件
        _cmd_gen_conf(cmd_valu)
    return vpkg_retvalu
    
def main():
    init_program()
    log_info("info->vpkg local_path...>%s<"%(vpkg_root))
    log_info("info->vpkg config_file path...>%s<"%(vpkg_conf_path))
    log_info("info->vpkg config_file exist...>%s<"%(os.path.exists(vpkg_conf_path)))
    extra_config()
    # ---- 优化：逐行对齐打印 vpkg_info ----
    _info_width = max(len(k) for k in vpkg_info.keys())
    _info_rows = ["info->vpkg_info:"]
    for _k, _v in vpkg_info.items():
        _info_rows.append("    {key:<{width}} -> {val}".format(key=_k, width=_info_width, val=_v))
    log_info("\n".join(_info_rows))
    # ------------------------------------
    extra_command()

if __name__=="__main__":
    import os
    import sys
    import re
    import shutil
    from rich import print
    import subprocess

    main()