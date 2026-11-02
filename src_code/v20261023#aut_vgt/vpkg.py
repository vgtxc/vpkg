# lastEdit=>2026.10.23-23:37
# lastEdit=>2026.10.13-23:24
# lastEdit=>2026.09.26-22:10
# lastEdit=>2026.09.17-22:00
# lastEdit=>2026.04.28-14:00
# lastEdit=>2026.04.28-13:00
# lastEdit=>2026.04.28-12:00
# lastEdit=>2026.04.28-11:05
# lastEdit=>2026.04.18-23:00
# lastEdit=>2026.04.16-22:38
# creat:2026.04.16
# aut: vgtxc
# ver: src#20260428
# ver: 20261023
"""
    bug-> lua安装：luarocks的配置
    bug-> 在shell环境下无法安装软件
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
    global vpkg_config_file
    global vpkg_root_tree
    global vpkg_config_symbol
    global vpkg_info
    global vpkg_info_kwOrder
    global vpkg_sftw
    global vpkg_sftw_toolFmt
    global vpkg_sftw_scriptFmt
    global vpkg_sftw_tool_kwOrder
    global vpkg_sftw_script_kwOrder
    global vpkg_sftw_tool_basic
    global vpkg_placeHolder
    global vpkg_cmd
    global vpkg_zip_ext
    # 判断是否是 PyInstaller 打包后的环境
    if getattr(sys, 'frozen', False):   # 如果是打包后的 exe，获取 exe 所在的目录
        vpkg_root = os.path.dirname(sys.executable)
    else:   # 如果是直接运行 .py 源文件，获取当前脚本所在的目录
        script_path = os.path.abspath(__file__)
        vpkg_root = os.path.dirname(script_path)
    vpkg_root = vpkg_root.replace("\\","/")
    vpkg_config_file = vpkg_root+"/vpkg_config.txt"
    vpkg_config_symbol = (
        "info->sftw", "info=>sftw",
        "info->tool", "info=>tool",
        "info->script", "info=>script",
    )
    vpkg_info = {
        "platform": str(),
        "name": str(),
        "version": str(),
        "website": str(),
        "autor": str(),
        "publish": str(),
        "description": str(),
    }
    vpkg_info_kwOrder = (
        "platform",
        "name",
        "version",
        "website",
        "autor",
        "publish",
        "description",
    )
    vpkg_sftw = {
        "tool": dict(),
        "script": dict(),
    }
    vpkg_sftw_toolFmt = {
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
    vpkg_sftw_scriptFmt = {
        "platform": str(),
        "name": str(),
        "version": str(),
        "website": str(),
        "local_path": str(),
        "content": str(),
        "install_statu": bool(),    # 由软件判断赋值, 不通过配置文件获取
    }
    vpkg_sftw_tool_kwOrder = (
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
    vpkg_sftw_script_kwOrder = (
        "platform",
        "name",
        "version",
        "website",
        "local_path",
        "content",
        "install_statu",
    )
    vpkg_sftw_tool_basic = (    # 必须是单压缩包文件
        "a7z",
        "aria2",
    )
    vpkg_placeHolder = "ugv"
    vpkg_cmd = (
        "help",
        "list",
        "install",
        "remove",
        "shell",
    )
    vpkg_root_tree = {
        "root_vpkg": "{vpkg_root}",
        "root_system": "{vpkg_root}/{platform}",
        "root_tool": "{vpkg_root}/{platform}/tool",
        "root_script": "{vpkg_root}/{platform}/script",
        "root_cache" : "{vpkg_root}/{platform}/cache",
    }
    vpkg_zip_ext = {
        "single_file": (".7z",".zip",".rar",),
        "multi_7z": (".7z.001",".7z.002",".7z.003",".7z.004",".7z.005",".7z.006",),
        "multi_zip": (".zip.001",".zip.002",".zip.003",".zip.004",".zip.005",".zip.006",),
        "multi_rar": (".part001.rar",".part002.rar",".part003.rar",".part004.rar",".part005.rar",".part006.rar",),
        "default": (
            ".7z",".zip",".rar",
            ".7z.001",
            ".zip.001",
            ".part001.rar",
        ),
        "filter": (
            ".7z",".zip",".rar",
            ".7z.001",".7z.002",".7z.003",".7z.004",".7z.005",".7z.006",
            ".zip.001",".zip.002",".zip.003",".zip.004",".zip.005",".zip.006",
            ".part001.rar",".part002.rar",".part003.rar",".part004.rar",".part005.rar",".part006.rar",
        ),
    }
    # 默认配置
    def _item_default():
        # --------------------------------------------
        vpkg_info = {
            "platform": "x64-win",
            "name": "vpkg",
            "version": "v20261021",
            "website": "https://github.com/vgtxc/vpkg.git",
            "autor": "vgtxc",
            "publish": "None",
            "description": "A lightWight sftw manager!!!",
        }
        for idx in vpkg_root_tree.keys():
            vpkg_root_tree[idx] = vpkg_root_tree[idx].replace("{vpkg_root}",vpkg_root)
            vpkg_root_tree[idx] = vpkg_root_tree[idx].replace("{platform}",vpkg_info["platform"])
        # --------------------------------------------
        vpkg_sftw["tool"]["a7z"] = {
            "platform": "x64-win",
            "name": "a7z",
            "version": "v26.04",
            "website": "https://www.7-zip.org/",
            "local_path": "{vpkg_tool}/<name>/<version>",
            "symbol_excu": "<local_path>/7za.exe",
            "install": {
                "<local_path>":["https://github.com/ip7z/7zip/releases/download/26.04/7z2604-extra.7z",],
            },
            "env_arg": {
                "path":["<local_path>"],
            },
            "install_statu": bool(),
        }
        vpkg_sftw["tool"]["aria2"] = {
            "platform": "x64-win",
            "name": "aria2",
            "version": "v1.37.0",
            "website": "https://github.com/aria2/aria2",
            "local_path": "{vpkg_tool}/<name>/<version>",
            "symbol_excu": "<local_path>/aria2c.exe",
            "install": {
                "<local_path>": ["https://github.com/aria2/aria2/releases/latest/download/aria2-1.37.0-win-64bit-build1.zip",],
            },
            "env_arg": {
                "aria2_home": ["<local_path>"],
                "path": ["<local_path>"],
            },
            "install_statu": bool(),
        }
        vpkg_sftw["tool"]["ffmpeg"] = {
            "platform": "x64-win",
            "name": "ffmpeg",
            "version": "v.latest",
            "website": "https://github.com/BtbN/FFmpeg-Builds",
            "local_path": "{vpkg_tool}/<name>/<version>",
            "symbol_excu": "<local_path>/bin/ffmpeg.exe",
            "install": {
                "<local_path>": ["https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip",],
            },
            "env_arg": {
                "path": ["<local_path>/bin",],
            },
            "install_statu": bool(),
        }
        vpkg_sftw["tool"]["git"] = {
            "platform": "x64-win",
            "name": "git",
            "version": "v2.55.0",
            "website": "https://git-scm.com/",
            "local_path": "{vpkg_tool}/<name>/<version>",
            "symbol_excu": "<local_path>/bin/git.exe",
            "install": {
                "<local_path>":["https://github.com/git-for-windows/git/releases/download/v2.55.0.windows.5/PortableGit-2.55.0.5-64-bit.7z.exe",],
            },
            "env_arg": {
                "path": ["<local_path>",],
            },
            "install_statu": bool(),
        }
        vpkg_sftw["tool"]["pixi"] = {
            "platform": "x64-win",
            "name": "pixi",
            "version": "v0.80.0",
            "website": "https://github.com/prefix-dev/pixi",
            "local_path": "{vpkg_tool}/<name>/<version>",
            "symbol_excu": "<local_path>/pixi.exe",
            "install": {
                "<local_path>":["https://github.com/prefix-dev/pixi/releases/download/v0.80.0/pixi-x86_64-pc-windows-msvc.zip",],
            },
            "env_arg": {
                "path":["<local_path>",],
            },
            "install_statu": bool(),
        }
        vpkg_sftw["tool"]["uv"] = {
            "platform": "x64-win",
            "name": "uv",
            "version": "v0.12.13",
            "website": "https://github.com/astral-sh/uv",
            "local_path": "{vpkg_tool}/<name>/<version>",
            "symbol_excu": "<local_path>/uv.exe",
            "install": {
                "<local_path>":["https://releases.astral.sh/github/uv/releases/download/0.12.13/uv-x86_64-pc-windows-msvc.zip",],
            },
            "env_arg": {
                "path": ["<local_path>",],
            },
            "install_statu": bool(),
        }
        vpkg_sftw["tool"]["cmake"] = {
            "platform": "x64-win",
            "name": "cmake",
            "version": "v4.5.0-rc1",
            "website": "https://github.com/Kitware/CMake",
            "local_path": "{vpkg_tool}/<name>/<version>",
            "symbol_excu": "<local_path>/bin/cmake.exe",
            "install": {
                "<local_path>": ["https://github.com/Kitware/CMake/releases/download/v4.5.0-rc1/cmake-4.5.0-rc1-windows-x86_64.zip",],
            },
            "env_arg": {
                "path": ["<local_path>",],
            },
            "install_statu": bool(),
        }
        vpkg_sftw["tool"]["xmake"] = {
            "platform": "x64-win",
            "name": "xmake",
            "version": "v3.1.1",
            "website": "https://github.com/xmake-io/xmake",
            "local_path": "{vpkg_tool}/<name>/<version>",
            "symbol_excu": "<local_path>/xmake.exe",
            "install": {
                "<local_path>": ["https://github.com/xmake-io/xmake/releases/download/v3.1.1/xmake-v3.1.1.win64.zip",],
            },
            "env_arg": {
                "path": ["<local_path>",],
            },
            "install_statu": bool(),
        }
        vpkg_sftw["tool"]["vcpkg"] = {
            "platform": "x64-win",
            "name": "vcpkg",
            "version": "v20260926",
            "website": "https://github.com/microsoft/vcpkg-tool",
            "local_path": "{vpkg_tool}/<name>/<version>",
            "symbol_excu": "<local_path>/vcpkg.exe",
            "install": {
                "<local_path>": ["https://github.com/microsoft/vcpkg-tool/releases/download/2026-09-26/vcpkg.exe",],
            },
            "env_arg": {
                "path": ["<local_path>",],
            },
            "install_statu": bool(),
        }
        vpkg_sftw["tool"]["nodejs"] = {
            "platform": "x64-win",
            "name": "nodejs",
            "version": "v26.8.2",
            "website": "https://nodejs.org",
            "local_path": "{vpkg_tool}/<name>/<version>",
            "symbol_excu": "<local_path>/node.exe",
            "install": {
                "<local_path>": ["https://nodejs.org/dist/v26.8.2/node-v26.8.2-win-x64.zip",],
            },
            "env_arg": {
                "path": ["<local_path>",],
            },
            "install_statu": bool(),
        }
        vpkg_sftw["tool"]["python"] = {
            "platform": "x64-win",
            "name": "python",
            "version": "v3.14.7",
            "website": "https://www.python.org",
            "local_path": "{vpkg_tool}/<name>/<version>",
            "symbol_excu": "<local_path>/python.exe",
            "install": {
                "<local_path>": [
                    "https://www.python.org/ftp/python/3.14.7/python-3.14.7-embed-amd64.zip",
                    "https://bootstrap.pypa.io/get-pip.py",
                ],
            },
            "env_arg": {
                "path": ["<local_path>",],
            },
            "install_statu": bool(),
        }
        vpkg_sftw["tool"]["rust"] = {
            "platform": "x64-win",
            "name": "rust",
            "version": "v1.98.1",
            "website": "https://rust-lang.org/",
            "local_path": "{vpkg_tool}/<name>/<version>",
            "symbol_excu": "<local_path>/rustup-init.exe",
            "install": {
                "<local_path>": ["https://static.rust-lang.org/rustup/dist/x86_64-pc-windows-msvc/rustup-init.exe",],
            },
            "env_arg": {
                "rustup_home": ["<local_path>/rustup_home",],
                "cargo_home": ["<local_path>/cargo_home",],
                "path": ["<local_path>","<local_path>/cargo_home/bin","<local_path>/rustup_home",],
            },
            "install_statu": bool(),
        }
        vpkg_sftw["tool"]["java"] = {
            "platform": "x64-win",
            "name": "java",
            "version": "v26",
            "website": "https://www.java.com",
            "local_path": "{vpkg_tool}/<name>/<version>",
            "symbol_excu": "<local_path>/java.exe",
            "install": {
                "<local_path>": ["https://download.oracle.com/java/26/latest/jdk-26_windows-x64_bin.zip",],
            },
            "env_arg": {
                "path": ["<local_path>",],
            },
            "install_statu": bool(),
        }
        vpkg_sftw["tool"]["golang"] = {
            "platform": "x64-win",
            "name": "golang",
            "version": "v1.27.1",
            "website": "https://golang.google.cn/",
            "local_path": "{vpkg_tool}/<name>/<version>",
            "symbol_excu": "<local_path>/go.exe",
            "install": {
                "<local_path>": ["https://golang.google.cn/dl/go1.27.1.windows-amd64.zip",],
            },
            "env_arg": {
                "go_root": ["<local_path>",],
                "path": ["<local_path>",],
            },
            "install_statu": bool(),
        }
        vpkg_sftw["tool"]["zig"] = {
            "platform": "x64-win",
            "name": "zig",
            "version": "v0.17.0",
            "website": "https://ziglang.org/",
            "local_path": "{vpkg_tool}/<name>/<version>",
            "symbol_excu": "<local_path>/zig.exe",
            "install": {
                "<local_path>": ["https://ziglang.org/builds/zig-x86_64-windows-0.17.0-dev.2125+0d600e488.zip",],
            },
            "env_arg": {
                "path": ["<local_path>",],
            },
            "install_statu": bool(),
        }
        vpkg_sftw["tool"]["vlang"] = {
            "platform": "x64-win",
            "name": "vlang",
            "version": "v0.5",
            "website": "https://vlang.io/",
            "local_path": "{vpkg_tool}/<name>/<version>",
            "symbol_excu": "<local_path>/v.exe",
            "install": {
                "<local_path>": ["https://github.com/vlang/v/releases/latest/download/v_windows.zip",],
            },
            "env_arg": {
                "path": ["<local_path>",],
            },
            "install_statu": bool(),
        }
        vpkg_sftw["tool"]["lua"] = {
            "platform": "x64-win",
            "name": "lua",
            "version": "v5.5.0",
            "website": "https://www.lua.org/",
            "local_path": "{vpkg_tool}/<name>/<version>",
            "symbol_excu": "<local_path>/bin/lua55.exe",
            "install": {
                "<local_path>/bin": ["https://zenlayer.dl.sourceforge.net/project/luabinaries/5.5.0/Tools%20Executables/lua-5.5.0_Win64_bin.zip",],
                "<local_path>/lib": ["https://twds.dl.sourceforge.net/project/luabinaries/5.5.0/Windows%20Libraries/Static/lua-5.5.0_Win64_mingw6_lib.zip",],
                "<local_path>/pkg": ["https://luarocks.github.io/luarocks/releases/luarocks-3.13.0-windows-64.zip",],
            },
            "env_arg": {
                # "lua": ["<local_path>/bin/lua55.exe",],
                # "lua_root": ["<local_path>",],
                # "lua_excu": ["<local_path>/bin/lua55.exe",],
                # "lua_bindir": ["<local_path>/bin",],
                # "lua_libdir": ["<local_path>/lib",],
                # "lua_incdir": ["<local_path>/lib/include",],
                # "luarocks_root": ["<local_path>/pkg",],
                "luarocks_config": ["<local_path>/pkg/config.lua",],
                "path": ["<local_path>/pkg","<local_path>/bin"],
            },
            "install_statu": bool(),
        }
        vpkg_sftw["tool"]["mingw_w64"] = {
            "platform": "x64-win",
            "name": "mingw_w64",
            "version": "v16.2.0",
            "website": "https://github.com/niXman/mingw-builds-binaries",
            "local_path": "{vpkg_tool}/<name>/<version>",
            "symbol_excu": "<local_path>/bin/gcc.exe",
            "install": {
                "<local_path>": ["https://github.com/niXman/mingw-builds-binaries/releases/download/16.2.0-rt_v14-rev1/x86_64-16.2.0-release-posix-seh-ucrt-rt_v14-rev1.7z",],
            },
            "env_arg": {
                "path": ["<local_path>/bin",],
            },
            "install_statu": bool(),
        }
        vpkg_sftw["tool"]["llvm_mingw"] = {
            "platform": "x64-win",
            "name": "llvm_mingw",
            "version": "v20260908",
            "website": "https://github.com/mstorsjo/llvm-mingw",
            "local_path": "{vpkg_tool}/<name>/<version>",
            "symbol_excu": "<local_path>/bin/gcc.exe",
            "install": {
                "<local_path>": ["https://github.com/mstorsjo/llvm-mingw/releases/download/20260908/llvm-mingw-20260908-ucrt-x86_64.zip",],
            },
            "env_arg": {
                "path": ["<local_path>/bin",],
            },
            "install_statu": bool(),
        }
        vpkg_sftw["tool"]["llvm_msvc"] = {
            "platform": "x64-win",
            "name": "llvm_msvc",
            "version": "v777.3.1",
            "website": "https://github.com/aftermathlabs/llvm-msvc",
            "local_path": "{vpkg_tool}/<name>/<version>",
            "symbol_excu": "<local_path>/bin/clang-cl.exe",
            "install": {
                "<local_path>": [
                    "https://github.com/aftermathlabs/llvm-msvc/releases/download/llvm-msvc-v777.3.1/windows-wrapper-llvm-msvc-PDB.zip.001",
                    "https://github.com/aftermathlabs/llvm-msvc/releases/download/llvm-msvc-v777.3.1/windows-wrapper-llvm-msvc-PDB.zip.002",
                ],
            },
            "env_arg": {
                "path": ["<local_path>/bin",],
            },
            "install_statu": bool(),
        }
        vpkg_sftw["tool"]["llvm_winlibs"] = {
            "platform": "x64-win",
            "name": "llvm_winlibs",
            "version": "v16.2.0",
            "website": "https://github.com/brechtsanders/winlibs_mingw",
            "local_path": "{vpkg_tool}/<name>/<version>",
            "symbol_excu": "<local_path>/bin/gcc.exe",
            "install": {
                "<local_path>": [
                    "https://github.com/brechtsanders/winlibs_mingw/releases/download/16.2.0posix-23.1.3-14.0.0-ucrt-r3/winlibs-x86_64-posix-seh-gcc-16.2.0-llvm-23.1.3-mingw-w64ucrt-14.0.0-r3.7z",
                ],
            },
            "env_arg": {
                "path": ["<local_path>/bin",],
            },
            "install_statu": bool(),
        }
        vpkg_sftw["tool"]["mingw_winlibs"] = {
            "platform": "x64-win",
            "name": "mingw_winlibs",
            "version": "v16.2.0",
            "website": "https://github.com/brechtsanders/winlibs_mingw",
            "local_path": "{vpkg_tool}/<name>/<version>",
            "symbol_excu": "<local_path>/bin/gcc.exe",
            "install": {
                "<local_path>": [
                    "https://github.com/brechtsanders/winlibs_mingw/releases/download/16.2.0posix-23.1.3-14.0.0-ucrt-r3/winlibs-x86_64-posix-seh-gcc-16.2.0-mingw-w64ucrt-14.0.0-r3.7z",
                ],
            },
            "env_arg": {
                "path": ["<local_path>/bin",],
            },
            "install_statu": bool(),
        }
        vpkg_sftw["tool"]["llvm_qt"] = {
            "platform": "x64-win",
            "name": "llvm_qt",
            "version": "v6.11.2",
            "website": "https://github.com/yuanpeirong/buildQt",
            "local_path": "{vpkg_tool}/<name>/<version>",
            "symbol_excu": "<local_path>/bin/qmake.exe",
            "install": {
                "<local_path>": [
                    "https://github.com/yuanpeirong/buildQt/releases/download/Qt6.11.2_rev0/Qt_6.11.2-static-Release_llvm-mingw22.1.8_64_UCRT.7z",
                ],
            },
            "env_arg": {
                "path": ["<local_path>/bin",],
            },
            "install_statu": bool(),
        }
        vpkg_sftw["tool"]["mingw_qt"] = {
            "platform": "x64-win",
            "name": "mingw_qt",
            "version": "v6.11.2",
            "website": "https://github.com/yuanpeirong/buildQt",
            "local_path": "{vpkg_tool}/<name>/<version>",
            "symbol_excu": "<local_path>/bin/qmake.exe",
            "install": {
                "<local_path>": [
                    "https://github.com/yuanpeirong/buildQt/releases/download/Qt6.11.2_rev0/Qt_6.11.2-static-Release_mingw1620_64_UCRT.7z",
                ],
            },
            "env_arg": {
                "path": ["<local_path>/bin",],
            },
            "install_statu": bool(),
        }
        vpkg_sftw["tool"]["msvc_qt"] = {
            "platform": "x64-win",
            "name": "msvc_qt",
            "version": "v6.11.2",
            "website": "https://github.com/yuanpeirong/buildQt",
            "local_path": "{vpkg_tool}/<name>/<version>",
            "symbol_excu": "<local_path>/bin/qmake.exe",
            "install": {
                "<local_path>": [
                    "https://github.com/yuanpeirong/buildQt/releases/download/Qt6.11.2_rev0/Qt_6.11.2-static-Release_msvc2026_64.7z",
                ],
            },
            "env_arg": {
                "path": ["<local_path>/bin",],
            },
            "install_statu": bool(),
        }
        # --------------------------------------------
        vpkg_sftw["script"]["unproxy"] = {
            "platform": "x64-win",
            "name": "unproxy.bat",
            "version": "1.0",
            "website": "void",
            "local_path": "{vpkg_script}",
            "content": "@echo off\nset http_proxy=\nset https_proxy=\necho info-}remove the proxy\n\n",
            "install_statu": bool(),
        }
        vpkg_sftw["script"]["proxy_clash"] = {
            "platform": "x64-win",
            "name": "proxy_clash.bat",
            "version": "v1.0",
            "website": "void",
            "local_path": "{vpkg_script}",
            "content": "@echo off\nset http_proxy=127.0.0.1:7890\nset https_proxy=127.0.0.1:7890\necho info-}set the proxy to http://127.0.0.1:7890\n\n",
            "install_statu": bool(),
        }
        vpkg_sftw["script"]["proxy_v2ray"] = {
            "platform": "x64-win",
            "name": "proxy_v2ray.bat",
            "version": "v1.0",
            "website": "void",
            "local_path": "{vpkg_script}",
            "content": "@echo off\nset http_proxy=127.0.0.1:7880\nset https_proxy=127.0.0.1:7880\necho info-}set the proxy to http://127.0.0.1:7880\n\n",
            "install_statu": bool(),
        }
        # --------------------------------------------
        return vpkg_placeHolder
    _item_default()
    return vpkg_placeHolder

# ================= 01.配置解析 =================
def extra_config():
    # 条目匹配
    def _item_match():
        with open(vpkg_config_file,"r",encoding="utf8") as f:
            config_file_content = f.read()
        config_file_content = re.sub(r"#.*$","",config_file_content,flags=re.MULTILINE)
        # config_file_content = config_file_content.replace(r"{vpkg_root}",vpkg_root)
        config_file_content = config_file_content.split("\n")
        config_file_content = [idx for idx in config_file_content if idx not in ["","\t"," "*4," "*8," "*12," "*16]]
        config_file_splitIdx = [idx for idx in range(len(config_file_content)) if (config_file_content[idx] in vpkg_config_symbol) or idx==len(config_file_content)]
        config_file_splitIdx.append(len(config_file_content))
        for idx in range(len(config_file_splitIdx)-1):
            tmp_split_part = config_file_content[config_file_splitIdx[idx]:config_file_splitIdx[idx+1]]
            tmp_split_part_string = "\n".join(tmp_split_part)
            if tmp_split_part[0] in ["info->sftw","info=>sftw"]:
                tmp_match_pattern = (
                    "info->sftw\n",
                    " "*4+"platform:(?P<platform>.*)\n",
                    " "*4+"name:(?P<name>.*)\n",
                    " "*4+"version:(?P<version>.*)\n",
                    " "*4+"website:(?P<website>.*)\n",
                    " "*4+"autor:(?P<autor>.*)\n",
                    " "*4+"publish:(?P<publish>.*)\n",
                    " "*4+"description:(?P<description>.*)",
                )
                tmp_match_result = re.match(r"".join(tmp_match_pattern),tmp_split_part_string)
                if tmp_match_result==None:
                    tmp_match_result = re.match(r"".join(tmp_match_pattern).replace("info->sftw","info=>sftw"),tmp_split_part_string)
                if tmp_match_result==None:
                    log_erro("erro->func:<extra_config>...config file “sftw” syntax panic!!!")
                    log_erro("...source config_file part as follow...")
                    log_warn(tmp_split_part_string)
                    log_erro("...source config_file part over...")
                    break
                for idx1 in vpkg_info_kwOrder:
                    vpkg_info[idx1] = tmp_match_result.group(idx1).strip()
                continue
            if tmp_split_part[0] in ["info->tool","info=>tool"]:
                tmp_match_pattern = (
                    "info->tool\n",
                    " "*4+"platform:(?P<platform>.*)\n",
                    " "*4+"name:(?P<name>.*)\n",
                    " "*4+"version:(?P<version>.*)\n",
                    " "*4+"website:(?P<website>.*)\n",
                    " "*4+"local_path:(?P<local_path>.*)\n",
                    " "*4+"symbol_excu:(?P<symbol_excu>.*)\n",
                    " "*4+"init->install(?P<install>.*)over->install\n",
                    " "*4+"init->env_arg(?P<env_arg>.*)over->env_arg",
                )
                tmp_match_result = re.match(r"".join(tmp_match_pattern),tmp_split_part_string,re.S)
                if tmp_match_result==None:
                    tmp_match_result = re.match(r"".join(tmp_match_pattern).replace("info->tool","info=>tool"),tmp_split_part_string)
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
                    log_info("info->“{tool_name}”...“{platformA}”...not match system platform...“{platformB}”!!!".format(tool_name=tmp_tool_name,platformA=tmp_tool_platform,platformB=vpkg_info["platform"]))
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
                vpkg_sftw["tool"][tmp_tool_name] = {
                    "platform": tmp_tool_platform,
                    "name": tmp_tool_name,
                    "version": tmp_tool_version,
                    "website": tmp_tool_website,
                    "local_path": tmp_tool_local_path,
                    "symbol_excu": tmp_tool_symbol_excu,
                    "install": tmp_tool_install_dict,
                    "env_arg": tmp_tool_env_arg_dict,
                }
            if tmp_split_part[0] in ["info->script","info=>script"]:
                tmp_match_pattern = (
                    "info->script\n",
                    " "*4+"platform:(?P<platform>.*)\n",
                    " "*4+"name:(?P<name>.*)\n",
                    " "*4+"version:(?P<version>.*)\n",
                    " "*4+"website:(?P<website>.*)\n",
                    " "*4+"local_path:(?P<local_path>.*)\n",
                    " "*4+"init->content(?P<content>.*)over->content",
                )
                tmp_match_result = re.match(r"".join(tmp_match_pattern),tmp_split_part_string,re.S)
                if tmp_match_result==None:
                    tmp_match_result = re.match(r"".join(tmp_match_pattern).replace("info->script","info=>script"),tmp_split_part_string)
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
                    log_info("info->“{script_name}”...“{platformA}”...not match system platform...“{platformB}”!!!".format(script_name=tmp_script_name,platformA=tmp_script_platform,platformB=vpkg_info["platform"]))
                    continue
                tmp_script_content_string = str()
                for idx1 in tmp_script_content:
                    if not idx1:
                        continue
                    tmp_script_content_string += idx1[8:]+"\n"
                vpkg_sftw["script"][tmp_script_name] = {
                    "platform": tmp_script_platform,
                    "name": tmp_script_name,
                    "version": tmp_script_version,
                    "website": tmp_script_website,
                    "local_path": tmp_script_local_path,
                    "content": tmp_script_content_string,
                }
                continue
        return vpkg_placeHolder
    # 条目关键词自引用解引用
    def _item_extra():
        for tool_name in vpkg_sftw["tool"].keys():
            tmp_tool_platform = vpkg_sftw["tool"][tool_name]["platform"]
            tmp_tool_name = vpkg_sftw["tool"][tool_name]["name"]
            tmp_tool_version = vpkg_sftw["tool"][tool_name]["version"]
            tmp_tool_website = vpkg_sftw["tool"][tool_name]["website"]
            tmp_tool_local_path = vpkg_sftw["tool"][tool_name]["local_path"]
            tmp_tool_symbol_excu = vpkg_sftw["tool"][tool_name]["symbol_excu"]
            tmp_tool_install_dict = vpkg_sftw["tool"][tool_name]["install"]
            tmp_tool_env_arg_dict = vpkg_sftw["tool"][tool_name]["env_arg"]
            # local_path解引用
            tmp_tool_local_path = tmp_tool_local_path.replace("{vpkg_root}",vpkg_root_tree["root_vpkg"])
            tmp_tool_local_path = tmp_tool_local_path.replace("{vpkg_system}",vpkg_root_tree["root_system"])
            tmp_tool_local_path = tmp_tool_local_path.replace("{vpkg_tool}",vpkg_root_tree["root_tool"])
            tmp_tool_local_path = tmp_tool_local_path.replace("{vpkg_script}",vpkg_root_tree["root_script"])
            tmp_tool_local_path = tmp_tool_local_path.replace("{vpkg_cache}",vpkg_root_tree["root_cache"])
            tmp_tool_local_path = tmp_tool_local_path.replace("<platform>",tmp_tool_platform)
            tmp_tool_local_path = tmp_tool_local_path.replace("<name>",tmp_tool_name)
            tmp_tool_local_path = tmp_tool_local_path.replace("<version>",tmp_tool_version)
            # symbol_excu解引用
            tmp_tool_symbol_excu = tmp_tool_symbol_excu.replace("{vpkg_root}",vpkg_root_tree["root_vpkg"])
            tmp_tool_symbol_excu = tmp_tool_symbol_excu.replace("{vpkg_system}",vpkg_root_tree["root_system"])
            tmp_tool_symbol_excu = tmp_tool_symbol_excu.replace("{vpkg_tool}",vpkg_root_tree["root_tool"])
            tmp_tool_symbol_excu = tmp_tool_symbol_excu.replace("{vpkg_script}",vpkg_root_tree["root_script"])
            tmp_tool_symbol_excu = tmp_tool_symbol_excu.replace("{vpkg_cache}",vpkg_root_tree["root_cache"])
            tmp_tool_symbol_excu = tmp_tool_symbol_excu.replace("<platform>",tmp_tool_platform)
            tmp_tool_symbol_excu = tmp_tool_symbol_excu.replace("<name>",tmp_tool_name)
            tmp_tool_symbol_excu = tmp_tool_symbol_excu.replace("<version>",tmp_tool_version)
            tmp_tool_symbol_excu = tmp_tool_symbol_excu.replace("<local_path>",tmp_tool_local_path)
            vpkg_sftw["tool"][tool_name]["local_path"] = tmp_tool_local_path
            vpkg_sftw["tool"][tool_name]["symbol_excu"] = tmp_tool_symbol_excu
            # install解引用
            tmp_tool_install_dict_new = dict()
            for idx1 in tmp_tool_install_dict.keys():
                tmp_key = idx1
                tmp_val = tmp_tool_install_dict[idx1]
                tmp_key = tmp_key.replace("{vpkg_root}",vpkg_root_tree["root_vpkg"])
                tmp_key = tmp_key.replace("{vpkg_system}",vpkg_root_tree["root_system"])
                tmp_key = tmp_key.replace("{vpkg_tool}",vpkg_root_tree["root_tool"])
                tmp_key = tmp_key.replace("{vpkg_script}",vpkg_root_tree["root_script"])
                tmp_key = tmp_key.replace("{vpkg_cache}",vpkg_root_tree["root_cache"])
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
                    tmp_val_elem = tmp_val_elem.replace("{vpkg_root}",vpkg_root_tree["root_vpkg"])
                    tmp_val_elem = tmp_val_elem.replace("{vpkg_system}",vpkg_root_tree["root_system"])
                    tmp_val_elem = tmp_val_elem.replace("{vpkg_tool}",vpkg_root_tree["root_tool"])
                    tmp_val_elem = tmp_val_elem.replace("{vpkg_script}",vpkg_root_tree["root_script"])
                    tmp_val_elem = tmp_val_elem.replace("{vpkg_cache}",vpkg_root_tree["root_cache"])
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
                tmp_key = tmp_key.replace("{vpkg_root}",vpkg_root_tree["root_vpkg"])
                tmp_key = tmp_key.replace("{vpkg_system}",vpkg_root_tree["root_system"])
                tmp_key = tmp_key.replace("{vpkg_tool}",vpkg_root_tree["root_tool"])
                tmp_key = tmp_key.replace("{vpkg_script}",vpkg_root_tree["root_script"])
                tmp_key = tmp_key.replace("{vpkg_cache}",vpkg_root_tree["root_cache"])
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
                    tmp_val_elem = tmp_val_elem.replace("{vpkg_root}",vpkg_root_tree["root_vpkg"])
                    tmp_val_elem = tmp_val_elem.replace("{vpkg_system}",vpkg_root_tree["root_system"])
                    tmp_val_elem = tmp_val_elem.replace("{vpkg_tool}",vpkg_root_tree["root_tool"])
                    tmp_val_elem = tmp_val_elem.replace("{vpkg_script}",vpkg_root_tree["root_script"])
                    tmp_val_elem = tmp_val_elem.replace("{vpkg_cache}",vpkg_root_tree["root_cache"])
                    tmp_val_elem = tmp_val_elem.replace("<platform>",tmp_tool_platform)
                    tmp_val_elem = tmp_val_elem.replace("<name>",tmp_tool_name)
                    tmp_val_elem = tmp_val_elem.replace("<version>",tmp_tool_version)
                    tmp_val_elem = tmp_val_elem.replace("<website>",tmp_tool_version)
                    tmp_val_elem = tmp_val_elem.replace("<local_path>",tmp_tool_local_path)
                    tmp_val_elem = tmp_val_elem.replace("<symbol_excu>",tmp_tool_local_path)
                    tmp_new_val.append(tmp_val_elem)
                tmp_tool_env_arg_dict_new[tmp_new_key] = tmp_new_val
            vpkg_sftw["tool"][tool_name]["install"] = tmp_tool_install_dict_new
            vpkg_sftw["tool"][tool_name]["env_arg"] = tmp_tool_env_arg_dict_new
        # script条目解引用
        for script_name in vpkg_sftw["script"].keys():
            tmp_script_platform = vpkg_sftw["script"][script_name]["platform"]
            tmp_script_name = vpkg_sftw["script"][script_name]["name"]
            tmp_script_version = vpkg_sftw["script"][script_name]["version"]
            tmp_script_website = vpkg_sftw["script"][script_name]["website"]
            tmp_script_local_path = vpkg_sftw["script"][script_name]["local_path"]
            tmp_script_content = vpkg_sftw["script"][script_name]["content"]
            tmp_script_local_path = tmp_script_local_path.replace("{vpkg_root}",vpkg_root_tree["root_vpkg"])
            tmp_script_local_path = tmp_script_local_path.replace("{vpkg_system}",vpkg_root_tree["root_system"])
            tmp_script_local_path = tmp_script_local_path.replace("{vpkg_tool}",vpkg_root_tree["root_tool"])
            tmp_script_local_path = tmp_script_local_path.replace("{vpkg_script}",vpkg_root_tree["root_script"])
            tmp_script_local_path = tmp_script_local_path.replace("{vpkg_cache}",vpkg_root_tree["root_cache"])
            tmp_script_local_path = tmp_script_local_path.replace("<platform>",tmp_script_platform)
            tmp_script_local_path = tmp_script_local_path.replace("<name>",tmp_script_platform)
            tmp_script_local_path = tmp_script_local_path.replace("<version>",tmp_script_platform)
            vpkg_sftw["script"][script_name]["local_path"] = tmp_script_local_path
        # 检测必要的文件目录,不存在则创建
        for idx in vpkg_root_tree.keys():
            necessary_dir = vpkg_root_tree[idx].format(vpkg_root=vpkg_root,platform=vpkg_info["platform"])
            vpkg_root_tree[idx] = necessary_dir
            if not os.path.exists(necessary_dir):
                os.mkdir(necessary_dir)
                log_warn("info->creat dir...>%s<"%(necessary_dir))
        # 检测软件安装状态
        for idx in vpkg_sftw["tool"].keys():
            vpkg_sftw["tool"][idx]["install_statu"] = os.path.exists(vpkg_sftw["tool"][idx]["symbol_excu"])
        return vpkg_placeHolder
    # 检测软件安装状态
    def _item_check():
        for idx in vpkg_sftw["tool"].keys():
            vpkg_sftw["tool"][idx]["install_statu"] = os.path.exists(vpkg_sftw["tool"][idx]["symbol_excu"])
        for idx in vpkg_sftw["script"].keys():
            vpkg_sftw["script"][idx]["install_statu"] = os.path.exists("%s/%s"%(vpkg_sftw["script"][idx]["local_path"],vpkg_sftw["script"][idx]["name"]))
    # 安装脚本
    def _install_script():
        for idx in vpkg_sftw["script"].keys():
            script_path = "%s/%s"%(vpkg_sftw["script"][idx]["local_path"],vpkg_sftw["script"][idx]["name"])
            install_statu = vpkg_sftw["script"][idx]["install_statu"]
            if install_statu == True:
                continue
            with open(script_path,"w") as f:
                f.write(vpkg_sftw["script"][idx]["content"])
            log_info("info->func:extra_config._install_script, install script...>%s<"%(script_path))
    # 配置文件判断
    if os.path.exists(vpkg_config_file) == False:
        log_warn("warn->config file miss...>%s<"%(vpkg_config_file))
        _item_extra()
        _item_check()
        _install_script()
        return vpkg_placeHolder
    _item_match()
    _item_extra()
    _item_check()
    _install_script()
    return vpkg_placeHolder

# ================= 02.命令解析 =================
def extra_command():
    def _check_basic_sftw_statu():
        sftw_statu = False
        for idx in vpkg_sftw_tool_basic:
            install_statu = vpkg_sftw["tool"][idx]["install_statu"]
            if install_statu == False:
                sftw_statu = False
                log_erro("erro->lack of basic sftw...>%s<"%(idx))
        return sftw_statu
    def _get_cli_arg():     # 获取命令行命令
        sys_argv = sys.argv
        if len(sys_argv)==1:
            return (vpkg_placeHolder,list())
        return (sys_argv[1],sys_argv[2:])
    def _clean_dir(aim_path):     # 清除临时文件夹
        shutil.rmtree(aim_path)
        os.mkdir(aim_path)
        log_warn("info->clean the dir...>%s<"%(aim_path))
    def _install_script(script_name):   # 安装脚本, 只在软件内部调用
        if script_name not in vpkg_sftw["script"].keys():
            log_erro("erro->func: extra_command._install_script, not exists item...>%s<"%(script_name))
            return vpkg_placeHolder
        script_path = "%s/%s"%(vpkg_sftw["script"][script_name]["local_path"],vpkg_sftw["script"][script_name]["name"])
        with open(script_path,"w") as f:
            f.write(vpkg_sftw["script"][script_name]["content"])
    def _cmd_help(cmd_valu):    # 命令_帮助
        log_warn("info->vpkg sftw info start!!!")
        for idx in vpkg_info.keys():
            log_info("\t%-12s->\t%s" % (idx, vpkg_info[idx]))
        log_warn("info->vpkg usage...>vpkg \\[command] \\[argument]<")
        for idx in vpkg_cmd:
            log_info("\tsupport command: {cmd}".format(cmd=idx))
        log_warn("info->vpkg sftw info end!!!")
        return vpkg_placeHolder
    def _cmd_list(cmd_valu):    # 命令_列出软件
        log_warn("info->list software install status!!!")
        log_info("\t%-15s->%-10s"%("name","install_status"))
        for idx in vpkg_sftw["tool"].keys():
            tmp_tool_name = idx
            tmp_tool_install_statu = vpkg_sftw["tool"][idx]["install_statu"]
            if tmp_tool_install_statu == True:
                log_info("\t%-15s->%-10s"%(tmp_tool_name,tmp_tool_install_statu))
                continue
            log_erro("\t%-15s->%-10s"%(tmp_tool_name,tmp_tool_install_statu))
    def _cmd_shell(cmd_valu):   # 创建临时运行环境
        # 环境变量合并
        origin_var = os.environ.copy()
        shell_var = dict()
        for idx in origin_var.keys():
            key = idx.lower()
            valu = origin_var[idx].replace("\\","/")
            shell_var[key] = valu
        for idx in vpkg_sftw["tool"].keys():
            sftw_var = vpkg_sftw["tool"][idx]["env_arg"]
            sftw_statu = vpkg_sftw["tool"][idx]["install_statu"]
            if sftw_statu == False:
                continue
            for idx2 in sftw_var.keys():
                sftw_var_key = idx2
                sftw_var_valu = str()
                for idx3 in sftw_var[idx2]:
                    sftw_var_valu += idx3+";"
                sftw_var_valu = sftw_var_valu[:-1]
                if sftw_var_key in shell_var.keys():
                    shell_var[sftw_var_key] = ("%s;%s"%(shell_var[sftw_var_key],sftw_var_valu))
                    continue
                shell_var[sftw_var_key] = sftw_var_valu.replace(";;",";")
        log_info("info->reg the env arg...")
        # 将root_script添加到path环境变量
        shell_var["path"] = "%s;%s"%(shell_var["path"],vpkg_root_tree["root_script"])
        # 开启新的shell并注册环境变量
        if os.name == 'nt':
            new_shell_arg = "title vpkg && prompt (vpkg) $P$G"
            new_shell_cmd = ["cmd","/k",new_shell_arg]
            subprocess.run(new_shell_cmd,env=shell_var)
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
        def _install_sftw(tool_name):
            cache_dir = vpkg_root_tree["root_cache"]        # 缓存目录
            extra_dir = cache_dir+"/extra_dir"              # 解压目录
            unzip_cmd_tool = vpkg_sftw["tool"]["a7z"]["symbol_excu"]    # 二进制解压工具路径
            unzip_cmd_fmt = unzip_cmd_tool+" x {archive_file} -o%s -y"%(extra_dir)    # 解压命令
            down_cmd_tool = vpkg_sftw["tool"]["aria2"]["symbol_excu"]      # 二进制下载工具路径
            down_cmd_fmt = down_cmd_tool+" {url_link} -d {down_dir} --allow-overwrite=true "
            _clean_dir(cache_dir)                         # 清空缓存目录
            cache_init_file, cache_init_dir = _get_file_and_dir(cache_dir) # 扫描文件夹和文件夹
            # (01)逐项下载文件
            for install_item in vpkg_sftw["tool"][tool_name]["install"].keys():
                install_dir = install_item
                download_url_list = vpkg_sftw["tool"][tool_name]["install"][install_item]
                os.makedirs(install_dir,exist_ok=True) # 创建目录树
                _clean_dir(install_dir)         # 清空目标安装目录
                for url in download_url_list:   # 下载文件到缓存目录
                    down_cmd = down_cmd_fmt.format(down_dir=cache_dir,url_link=url)
                    log_info("info->running command...\n\t%s"%(down_cmd))
                    os.system(down_cmd)
                cache_over_file, _ = _get_file_and_dir(cache_dir)
                download_file_list = _get_differ_item(cache_init_file,cache_over_file)
                pack_file = str()
                move_file = list()
                for idx in download_file_list:  # 判断文件类型并处理
                    file = os.path.split(idx)[1]
                    file_name, file_ext = os.path.splitext(file)
                    if file_ext in vpkg_zip_ext["default"]:     # 压缩包文件
                        pack_file = idx
                    if file_ext in vpkg_zip_ext["filter"]:
                        continue
                    move_file.append(idx)
                if pack_file:
                    file = os.path.split(idx)[1]
                    file_name, file_ext = os.path.splitext(file)
                    unzip_cmd = unzip_cmd_fmt.format(archive_file=idx,out_dir=cache_dir)
                    log_info("info->running command...\n\t%s"%(unzip_cmd))
                    os.system(unzip_cmd)
                    extra_dir = _get_stop_dir(extra_dir)
                    if os.path.exists(install_dir):
                        shutil.rmtree(install_dir)
                    os.rename(extra_dir,install_dir)
                for idx in move_file:
                    old_file = idx
                    file = os.path.split(idx)[1]
                    new_file = os.path.join(install_dir,file)
                    os.rename(old_file,new_file)
            log_info("info->sucess install...>%s<"%(tool_name))
        def _run(tool_name):
            log_info("info->cheak the repo for aim sftw...")
            if not tool_name:
                log_erro("erro->command “install” argu is empty...")
                return vpkg_placeHolder
            if tool_name not in vpkg_sftw["tool"].keys():   # 检测软件是否存在软件库中
                platform = vpkg_info["platform"]
                repo = vpkg_config_file
                tool_name = tool_name
                log_erro("erro->platform...>{0}<...\n\tthe repo...>{1}<...\n\tnot contain...>{2}<".format(platform,repo,tool_name))
                return vpkg_placeHolder
            log_info("info->check the basic sftw...")
            if _check_basic_sftw_statu == False:
                log_erro("erro->lack of basic sftw...>%s<"%(vpkg_sftw_tool_basic))
                return vpkg_placeHolder
            tool_statu = vpkg_sftw["tool"][tool_name]["install_statu"]
            if tool_statu == True:
                log_info("info->the sftw >%s< already install!!!"%(tool_name))
                return vpkg_placeHolder
            _install_sftw(tool_name)
            tool_statu = os.path.exists(vpkg_sftw["tool"][tool_name]["symbol_excu"])
            if tool_statu == False:
                log_erro("erro->install faild...>%s<"%(tool_name))
                return vpkg_placeHolder
            # ==========================软件安装: 特殊处理================================
            if tool_name == "pixi":
                log_info("info->install DLC(init home) for...>pixi<")
                pixi_excu = vpkg_sftw["tool"][tool_name]["symbol_excu"]
                pixi_home = vpkg_sftw["tool"][tool_name]["local_path"]
                os.system("%s init %s"%(pixi_excu,pixi_home))
                vpkg_sftw["script"]["prefix"] = {
                    "platform": "x64-win",
                    "name": "prefix.bat",
                    "version": "1.0",
                    "website": "void",
                    "local_path": "{vpkg_script}".format(vpkg_script=vpkg_root_tree["root_script"]),
                    "content": "@echo off\ncall {pixi_excu} shell --manifest-path {pixi_config}".format(pixi_excu=vpkg_sftw["tool"]["pixi"]["symbol_excu"],pixi_config="%s/pixi.toml"%(vpkg_sftw["tool"]["pixi"]["local_path"])),
                    "install_statu": bool(),
                }
                _install_script("prefix")
            if tool_name == "python":
                log_info("info->install DLC(pip) for...>python<")
                path_install = list(vpkg_sftw["tool"][tool_name]["install"].keys())[0]
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
                    os.system("{python} {get_pip_script}".format(python=file_python_excu,get_pip_script=file_get_pip))
            if tool_name == "rust":
                log_info("info->install DLC for...>rust<")
                rust_env_arg = vpkg_sftw["tool"][tool_name]["env_arg"]
                rustup_home = rust_env_arg["rustup_home"][0]
                cargo_home = rust_env_arg["cargo_home"][0]
                os.environ["rustup_home"] = rustup_home
                os.environ["cargo_home"] = cargo_home
                rustup_excu = vpkg_sftw["tool"][tool_name]["symbol_excu"]
                os.system(rustup_excu)            
            if tool_name == "lua":
                log_info("info->install DLC(luarocks config.lua) for...>lua<")
                lua_excu = vpkg_sftw["tool"]["lua"]["symbol_excu"]
                lua_bin, file = os.path.split(lua_excu)
                lua_excu_copy = "%s/lua.exe"%(lua_bin)
                lua_root = os.path.split(lua_bin)[0]
                lua_lib = "%s/lib"%(lua_root)
                lua_include = "%s/include"%(lua_root)
                lua_pkg = "%s/pkg"%(lua_root)
                shutil.copy2(lua_excu,lua_excu_copy)
                config_content = (
                    'rocks_trees = {\n',
                        '\t{\n',
                                '\t\tname = "vgt",\n',
                                '\t\troot = "<lua_bin>",\n',
                        '\t},\n',
                    '}\n',
                    'variables = {\n',
                        '\t-- 指定编译器命令\n',
                        '\t-- CC = "gcc",\n',
                        '\t-- CXX = "g++",\n',
                        '\t-- 指定链接器标志 (告诉链接器使用 MinGW 风格)\n',
                        '\tLINKFLAGS = "-shared",\n',
                        '\t-- 指定lua路径\n',
                        '\tLUA = "<lua_excu>",             -- 指定exe的具体路径而非文件夹\n',
                        '\t-- luarocks安装配置\n',
                        '\tLUA_BINDIR = "<lua_excu_root>",	-- 指定二进制工具文件夹路径\n',
                        '\tLUA_INCDIR = "<lua_include>",   -- 指定lua的头文件路径\n',
                        '\tLUA_LIBDIR = "<lua_lib>",	    -- 指定lua动态库路径\n',
                    '}',
                )
                vpkg_sftw["script"]["luarocks_config"] = {
                    "platform": "x64-win",
                    "name": "config.lua",
                    "version": "v1.0",
                    "website": "void",
                    "local_path": lua_pkg,
                    "content": "".join(config_content).replace(
                            "<lua_bin>",lua_bin
                        ).replace(
                            "<lua_root>",lua_root
                        ).replace(
                            "<lua_excu>",lua_excu_copy
                        ).replace(
                            "<lua_excu_root>",lua_bin
                        ).replace(
                            "<lua_include>",lua_include
                        ).replace(
                            "<lua_lib>",lua_lib
                        ),
                    "install_statu": bool(),
                }
                _install_script("luarocks_config")
            # ==========================软件安装: 特殊处理================================
            return vpkg_placeHolder
        tool_name = cmd_valu
        _run(tool_name)   
    def _cmd_remove(cmd_valu):  # 命令_卸载软件
        tool_name = cmd_valu
        if tool_name in vpkg_sftw_tool_basic:
            log_erro("erro->can not remove the basic sftw...>%s<"%(tool_name))
            return vpkg_placeHolder
        if tool_name not in vpkg_sftw["tool"].keys():   # 检测软件是否存在软件库中
            log_erro("erro->repo not exist...>%s<"%(tool_name))
            return vpkg_placeHolder
        if vpkg_sftw["tool"][tool_name]["install_statu"] == False:
            log_erro("erro->not install the sftw...>%s<"%(tool_name))
            return vpkg_placeHolder
        install_path = vpkg_sftw["tool"][tool_name]["local_path"]
        install_path_father = os.path.split(install_path)[0]
        shutil.rmtree(install_path)
        if len(os.listdir(install_path_father))==0:
            shutil.rmtree(install_path_father)
        log_warn("warn->success remove sftw...>%s<"%(tool_name))
    cmd_type,cmd_valu = _get_cli_arg()
    cmd_type = cmd_type
    if len(cmd_valu)>0:
        cmd_valu = cmd_valu[0]
    log_warn("warn->func extra_command: %s...%s"%(cmd_type,cmd_valu))
    if cmd_type not in vpkg_cmd:
        log_erro("erro->vpkg not support command...>%s<"%(cmd_type))
        return vpkg_placeHolder
    if cmd_type == "help":
        _cmd_help(cmd_valu)
    if cmd_type == "list":
        _cmd_list(cmd_valu)
    if cmd_type == "install":
        _cmd_install(cmd_valu)
    if cmd_type == "remove":
        _cmd_remove(cmd_valu)
    if cmd_type == "shell":
        _cmd_shell(cmd_valu)
    return vpkg_placeHolder
    
def main():
    init_program()
    log_info("info->vpkg local_path...>%s<"%(vpkg_root))
    # log_info("info->vpkg config_file...>%s<"%(vpkg_config_file))
    extra_config()
    extra_command()
    # print(vpkg_sftw["tool"])
    # print(vpkg_sftw["script"]["luarocks_config"])

if __name__=="__main__":
    import os
    import sys
    import re
    import shutil
    from rich import print
    import subprocess

    main()