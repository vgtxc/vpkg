# lastEdit=>2026.11.06-24:13
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

# ================= 颜色与日志打印封装 =================

def _enable_ansi() -> bool:
    if os.name != "nt":
        return True
    try:
        import ctypes
        handle = ctypes.windll.kernel32.GetStdHandle(-11)
        mode = ctypes.c_uint32()
        if not ctypes.windll.kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            return False
        return bool(ctypes.windll.kernel32.SetConsoleMode(handle, mode.value | 0x0004))
    except Exception:
        return False

_ansi_enabled = _enable_ansi()

def log_info(msg: str) -> str:
    if _ansi_enabled:
        print(f"\033[32m{msg}\033[0m")
    else:
        print(msg)
    return vpkg_placeHolder

def log_warn(msg: str) -> str:
    if _ansi_enabled:
        print(f"\033[34m{msg}\033[0m")
    else:
        print(msg)
    return vpkg_placeHolder

def log_erro(msg: str) -> str:
    if _ansi_enabled:
        print(f"\033[31m{msg}\033[0m")
    else:
        print(msg)
    return vpkg_placeHolder

# ================= 核心功能函数 =================
def init_program() -> str:  # 程序初始化
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
    global vpkg_download_proxy
    if getattr(sys, 'frozen', False):
        vpkg_root = os.path.dirname(sys.executable)
    else:
        script_path = os.path.abspath(__file__)
        vpkg_root = os.path.dirname(script_path)
    vpkg_root = vpkg_root.replace("\\", "/")
    vpkg_config_file = vpkg_root + "/vpkg_config.txt"
    vpkg_config_symbol = (
        "info->sftw", "info=>sftw",
        "info->tool", "info=>tool",
        "info->script", "info=>script",
    )
    vpkg_info = {
        "platform": str(), "name": str(), "version": str(), "website": str(),
        "autor": str(), "publish": str(), "description": str(), "proxy": bool(),
    }
    vpkg_info_kwOrder = (
        "platform", "name", "version", "website",
        "autor", "publish", "description", "proxy",
    )
    vpkg_sftw = {"tool": dict(), "script": dict()}
    vpkg_sftw_toolFmt = {
        "platform": str(), "name": str(), "version": str(), "website": str(),
        "local_path": str(), "symbol_excu": str(), "install": str(), "env_arg": str(),
        "install_statu": bool(),
    }
    vpkg_sftw_scriptFmt = {
        "platform": str(), "name": str(), "version": str(), "website": str(),
        "local_path": str(), "content": str(), "install_statu": bool(),
    }
    vpkg_sftw_tool_kwOrder = (
        "platform", "name", "version", "website", "local_path",
        "symbol_excu", "install", "env_arg", "install_statu",
    )
    vpkg_sftw_script_kwOrder = (
        "platform", "name", "version", "website",
        "local_path", "content", "install_statu",
    )
    vpkg_sftw_tool_basic = ("a7z", "aria2")
    vpkg_placeHolder = "ugv"
    vpkg_cmd = ("help", "list", "install", "remove", "shell", "excu")
    vpkg_root_tree = {
        "root_vpkg":   "{vpkg_root}",
        "root_system": "{vpkg_root}/{platform}",
        "root_tool":   "{vpkg_root}/{platform}/tool",
        "root_script": "{vpkg_root}/{platform}/script",
        "root_cache":  "{vpkg_root}/{platform}/cache",
        "root_extra":   "{vpkg_root}/{platform}/cache/extra_dir",
    }
    vpkg_zip_ext = {
        "single_file": (".7z", ".zip", ".rar", ".7z.exe"),
        "multi_7z":   (".7z.001", ".7z.002", ".7z.003", ".7z.004", ".7z.005", ".7z.006"),
        "multi_zip":  (".zip.001", ".zip.002", ".zip.003", ".zip.004", ".zip.005", ".zip.006"),
        "multi_rar":  (".part001.rar", ".part002.rar", ".part003.rar", ".part004.rar", ".part005.rar", ".part006.rar"),
        "default": (
            ".7z", ".zip", ".rar", ".7z.exe",
            ".7z.001", ".zip.001", ".part001.rar",
        ),
        "filter": (
            ".7z", ".zip", ".rar", ".7z.exe",
            ".7z.001", ".7z.002", ".7z.003", ".7z.004", ".7z.005", ".7z.006",
            ".zip.001", ".zip.002", ".zip.003", ".zip.004", ".zip.005", ".zip.006",
            ".part001.rar", ".part002.rar", ".part003.rar", ".part004.rar", ".part005.rar", ".part006.rar",
        ),
    }
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

    def _item_default() -> str:
        # --------------------------------------------
        vpkg_info.update({
            "platform": "x64-win",
            "name": "vpkg",
            "version": "v20261106",
            "website": "https://github.com/vgtxc/vpkg",
            "autor": "vgtxc",
            "publish": "None",
            "description": "A lightWight sftw manager!!!",
            "proxy": False,
        })
        for idx in vpkg_root_tree.keys():
            vpkg_root_tree[idx] = vpkg_root_tree[idx].replace("{vpkg_root}", vpkg_root)
            vpkg_root_tree[idx] = vpkg_root_tree[idx].replace("{platform}", vpkg_info["platform"])
        # --------------------------------------------
        vpkg_sftw["tool"]["a7z"] = {
            "platform": "x64-win",
            "name": "a7z",
            "version": "v26.04",
            "website": "https://www.7-zip.org/",
            "local_path": "{vpkg_tool}/<name>/<version>",
            "symbol_excu": "<local_path>/7za.exe",
            "install": {
                "<local_path>": ["https://github.com/ip7z/7zip/releases/download/26.04/7z2604-extra.7z", ],
            },
            "env_arg": {
                "path": ["<local_path>"],
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
                "<local_path>": ["https://github.com/aria2/aria2/releases/latest/download/aria2-1.37.0-win-64bit-build1.zip", ],
            },
            "env_arg": {
                "aria2_home": ["<local_path>"],
                "path": ["<local_path>"],
            },
            "install_statu": bool(),
        }
        vpkg_sftw["tool"]["wget"] = {
            "platform": "x64-win",
            "name": "wget",
            "version": "v1.25.0",
            "website": "https://eternallybored.org/misc/wget/",
            "local_path": "{vpkg_tool}/<name>/<version>",
            "symbol_excu": "<local_path>/wget.exe",
            "install": {
                "<local_path>": ["https://eternallybored.org/misc/wget/releases/wget-1.25.0-win64.zip", ],
            },
            "env_arg": {
                "wget_home": ["<local_path>", ],
                "path": ["<local_path>", ],
            },
            "install_statu": bool(),
        }
        vpkg_sftw["tool"]["fastCapture"] = {   # 截图软件
            "platform": "x64-win",
            "name": "fastCapture",
            "version": "v11.3",
            "website": "https://www.faststone.org/",
            "local_path": "{vpkg_tool}/<name>/<version>",
            "symbol_excu": "<local_path>/FSCapture.exe",
            "install": {
                "<local_path>": [
                    "https://www.faststonesoft.net/DN/FSCapture113.zip",
                ],
            },
            "env_arg": {
                "path": ["<local_path>", ],
            },
            "install_statu": bool(),
        }
        vpkg_sftw["tool"]["sublime"] = {   # 文本软件
            "platform": "x64-win",
            "name": "sublime",
            "version": "v4215",
            "website": "https://www.sublimetext.com/",
            "local_path": "{vpkg_tool}/<name>/<version>",
            "symbol_excu": "<local_path>/sublime.exe",
            "install": {
                "<local_path>": [
                    "https://www.sublimetext.com/download_thanks?target=win-x64-portable#direct-downloads",
                ],
            },
            "env_arg": {
                "path": ["<local_path>", ],
            },
            "install_statu": bool(),
        }
        vpkg_sftw["tool"]["ncnn_vulkan"] = {
            "platform": "x64-win",
            "name": "ncnn_vulkan",
            "version": "v20250915",
            "website": "https://github.com/BtbN/FFmpeg-Builds",
            "local_path": "{vpkg_tool}/<name>/<version>",
            "symbol_excu": "<local_path>/waifu2x-ncnn-vulkan.exe",
            "install": {
                "<local_path>": ["https://github.com/nihui/waifu2x-ncnn-vulkan/releases/download/20250915/waifu2x-ncnn-vulkan-20250915-windows.zip", ],
            },
            "env_arg": {
                "path": ["<local_path>", ],
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
                "<local_path>": ["https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip", ],
            },
            "env_arg": {
                "path": ["<local_path>/bin", ],
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
                "<local_path>": ["https://github.com/git-for-windows/git/releases/download/v2.55.0.windows.5/PortableGit-2.55.0.5-64-bit.7z.exe", ],
            },
            "env_arg": {
                "path": ["<local_path>", "<local_path>/bin"],
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
                "<local_path>": ["https://github.com/prefix-dev/pixi/releases/download/v0.80.0/pixi-x86_64-pc-windows-msvc.zip", ],
            },
            "env_arg": {
                "path": ["<local_path>", ],
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
                "<local_path>": ["https://github.com/Kitware/CMake/releases/download/v4.5.0-rc1/cmake-4.5.0-rc1-windows-x86_64.zip", ],
            },
            "env_arg": {
                "path": ["<local_path>/bin", ],
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
                "<local_path>": ["https://github.com/xmake-io/xmake/releases/download/v3.1.1/xmake-v3.1.1.win64.zip", ],
            },
            "env_arg": {
                "path": ["<local_path>", ],
            },
            "install_statu": bool(),
        }
        vpkg_sftw["tool"]["vcpkg"] = {
            "platform": "x64-win",
            "name": "vcpkg",
            "version": "v20261016",
            "website": "https://github.com/microsoft/vcpkg",
            "local_path": "{vpkg_tool}/<name>/<version>",
            "symbol_excu": "<local_path>/vcpkg.exe",
            "install": {
                "<local_path>": [
                    "https://github.com/microsoft/vcpkg/archive/refs/tags/2026.10.16.zip",
                    "https://github.com/microsoft/vcpkg-tool/releases/download/2026-09-26/vcpkg.exe",
                ],
            },
            "env_arg": {
                "path": ["<local_path>", ],
                "vcpkg_root": ["<local_path>", ],
                "vcpkg_default_triplet": ["x64-mingw-static", ],
                "vcpkg_default_host_triplet": ["x64-mingw-static", ],
                "X_VCPKG_ASSET_SOURCES": ["x-azurl,https://mirrors.tuna.tsinghua.edu.cn/vcpkg/assets/",],
                "VCPKG_BINARY_SOURCES": ["clear;x-https,https://mirrors.tuna.tsinghua.edu.cn/vcpkg-ce/cache/,readwrite",],
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
                "<local_path>": ["https://nodejs.org/dist/v26.8.2/node-v26.8.2-win-x64.zip", ],
            },
            "env_arg": {
                "path": ["<local_path>", "<local_path>/node_modules", "<local_path>/node_pkg", ],
                "npm_config_prefix": ["<local_path>/npm_pkg", ],
                "npm_config_cache": ["<local_path>/npm_cache", ],
            },
            "install_statu": bool(),
        }
        vpkg_sftw["tool"]["python"] = {
            "platform": "x64-win",
            "name": "python",
            "version": "v3.15.2",
            "website": "https://www.python.org",
            "local_path": "{vpkg_tool}/<name>/<version>",
            "symbol_excu": "<local_path>/python.exe",
            "install": {
                "<local_path>": [
                    "https://www.python.org/ftp/python/3.15.2/python-3.15.2-embed-amd64.zip",
                    "https://bootstrap.pypa.io/get-pip.py",
                ],
            },
            "env_arg": {
                "path": ["<local_path>", "<local_path>/Scripts"],
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
                "<local_path>": ["https://static.rust-lang.org/rustup/dist/x86_64-pc-windows-msvc/rustup-init.exe", ],
            },
            "env_arg": {
                "rustup_home": ["<local_path>/rustup_home", ],
                "cargo_home": ["<local_path>/cargo_home", ],
                "path": ["<local_path>", "<local_path>/cargo_home/bin", "<local_path>/rustup_home", ],
            },
            "install_statu": bool(),
        }
        vpkg_sftw["tool"]["java"] = {
            "platform": "x64-win",
            "name": "java",
            "version": "v27",
            "website": "https://www.java.com",
            "local_path": "{vpkg_tool}/<name>/<version>",
            "symbol_excu": "<local_path>/bin/java.exe",
            "install": {
                "<local_path>": ["https://download.oracle.com/java/27/latest/jdk-27_windows-x64_bin.zip", ],
            },
            "env_arg": {
                "path": ["<local_path>/bin", ],
            },
            "install_statu": bool(),
        }
        vpkg_sftw["tool"]["golang"] = {
            "platform": "x64-win",
            "name": "golang",
            "version": "v1.27.3",
            "website": "https://golang.google.cn/",
            "local_path": "{vpkg_tool}/<name>/<version>",
            "symbol_excu": "<local_path>/bin/go.exe",
            "install": {
                "<local_path>": ["https://go.dev/dl/go1.27.3.windows-amd64.zip", ],
            },
            "env_arg": {
                "go_root": ["<local_path>", ],
                "path": ["<local_path>", ],
            },
            "install_statu": bool(),
        }
        vpkg_sftw["tool"]["zig"] = {
            "platform": "x64-win",
            "name": "zig",
            "version": "v0.17.1",
            "website": "https://ziglang.org/",
            "local_path": "{vpkg_tool}/<name>/<version>",
            "symbol_excu": "<local_path>/zig.exe",
            "install": {
                "<local_path>": [
                    "https://ziglang.com.cn/download/0.17.1/zig-x86_64-windows-0.17.1.zip",
                ],
            },
            "env_arg": {
                "path": ["<local_path>", ],
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
                "<local_path>": ["https://github.com/vlang/v/releases/latest/download/v_windows.zip", ],
            },
            "env_arg": {
                "path": ["<local_path>", ],
            },
            "install_statu": bool(),
        }
        vpkg_sftw["tool"]["lua"] = {
            "platform": "x64-win",
            "name": "lua",
            "version": "v5.5.0",
            "website": "https://www.lua.org/",
            "local_path": "{vpkg_tool}/<name>/<version>",
            "symbol_excu": "<local_path>/lua55.exe",
            "install": {
                "<local_path>": [
                    "https://xget.xi-xu.me/sf/projects/luabinaries/files/5.5.0/Tools%20Executables/lua-5.5.0_Win64_bin.zip",
                    "https://xget.xi-xu.me/sf/projects/luabinaries/files/5.5.0/Windows%20Libraries/Static/lua-5.5.0_Win64_mingw6_lib.zip",
                    "https://github.com/luarocks/luarocks/releases/download/v3.12.2/luarocks-3.12.2-windows-64.zip",
                ]
            },
            "env_arg": {
                "luarocks_config": ["<local_path>/config.lua", ],
                "path": ["<local_path>", ],
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
                "<local_path>": ["https://github.com/niXman/mingw-builds-binaries/releases/download/16.2.0-rt_v14-rev1/x86_64-16.2.0-release-posix-seh-ucrt-rt_v14-rev1.7z", ],
            },
            "env_arg": {
                "path": ["<local_path>/bin", ],
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
                "<local_path>": ["https://github.com/mstorsjo/llvm-mingw/releases/download/20260908/llvm-mingw-20260908-ucrt-x86_64.zip", ],
            },
            "env_arg": {
                "path": ["<local_path>/bin", ],
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
                "path": ["<local_path>/bin", ],
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
                "path": ["<local_path>/bin", ],
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
                "path": ["<local_path>/bin", ],
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
                "path": ["<local_path>/bin", ],
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
                "path": ["<local_path>/bin", ],
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
                "path": ["<local_path>/bin", ],
            },
            "install_statu": bool(),
        }
        vpkg_sftw["tool"]["motrix"] = {   # 下载软件
            "platform": "x64-win",
            "name": "motrix",
            "version": "v2.2.1",
            "website": "https://motrix.app/zh/",
            "local_path": "{vpkg_tool}/<name>/<version>",
            "symbol_excu": "<local_path>/Motrix.exe",
            "install": {
                "<local_path>": [
                    "https://dl.motrix.app/releases/Motrix-2.2.1-win.zip",
                ],
            },
            "env_arg": {
                "path": ["<local_path>", ],
            },
            "install_statu": bool(),
        }
        vpkg_sftw["tool"]["ScreenCapture"] = {   # 截图软件
            "platform": "x64-win",
            "name": "ScreenCapture",
            "version": "v2.5.15",
            "website": "https://github.com/xland/ScreenCapture",
            "local_path": "{vpkg_tool}/<name>/<version>",
            "symbol_excu": "<local_path>/ScreenCapture.exe",
            "install": {
                "<local_path>": [
                    "https://github.com/xland/ScreenCapture/releases/download/2.5.15/ScreenCapture.exe",
                ],
            },
            "env_arg": {
                "path": ["<local_path>", ],
            },
            "install_statu": bool(),
        }
        vpkg_sftw["tool"]["sharex"] = {   # 截图软件
            "platform": "x64-win",
            "name": "sharex",
            "version": "v22.1.0",
            "website": "https://github.com/ShareX/ShareX",
            "local_path": "{vpkg_tool}/<name>/<version>",
            "symbol_excu": "<local_path>/ShareX.exe",
            "install": {
                "<local_path>": [
                    "https://github.com/ShareX/ShareX/releases/download/v22.1.0/ShareX-22.1.0-portable-x64.zip",
                ],
            },
            "env_arg": {
                "path": ["<local_path>", ],
            },
            "install_statu": bool(),
        }
        # --------------------------------------------
        vpkg_sftw["tool"]["FlClash"] = {   # 代理软件
            "platform": "x64-win",
            "name": "FlClash",
            "version": "v0.9.2",
            "website": "https://github.com/chen08209/FlClash",
            "local_path": "{vpkg_tool}/<name>/<version>",
            "symbol_excu": "<local_path>/FlClash.exe",
            "install": {
                "<local_path>": [
                    "https://github.com/chen08209/FlClash/releases/download/v0.9.2/FlClash-0.9.2-windows-amd64.zip",
                ],
            },
            "env_arg": {
                "path": ["<local_path>", ],
            },
            "install_statu": bool(),
        }
        vpkg_sftw["tool"]["v2rayN"] = {   # 代理软件
            "platform": "x64-win",
            "name": "v2rayN",
            "version": "v7.25.6",
            "website": "https://github.com/2dust/v2rayN",
            "local_path": "{vpkg_tool}/<name>/<version>",
            "symbol_excu": "<local_path>/v2rayN.exe",
            "install": {
                "<local_path>": [
                    "https://github.com/2dust/v2rayN/releases/download/7.25.6/v2rayN-windows-64.zip",
                ],
            },
            "env_arg": {
                "path": ["<local_path>", ],
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

def extra_config() -> str:  # 配置文件解析
    def _resolve_placeholders(text, platform: str, name: str, version: str, local_path: str) -> str:
        if not isinstance(text, str):
            return text
        for key, value in (
            ("{vpkg_root}", vpkg_root_tree["root_vpkg"]),
            ("{vpkg_system}", vpkg_root_tree["root_system"]),
            ("{vpkg_tool}", vpkg_root_tree["root_tool"]),
            ("{vpkg_script}", vpkg_root_tree["root_script"]),
            ("{vpkg_cache}", vpkg_root_tree["root_cache"]),
            ("<platform>", platform),
            ("<name>", name),
            ("<version>", version),
            ("<website>", version),
            ("<local_path>", local_path),
            ("<symbol_excu>", local_path),
        ):
            text = text.replace(key, value)
        return text
    def _syntax_panic(head: str, block: list) -> str:
        log_erro("erro->func:<extra_config>...config file “%s” syntax panic!!!" % (head.split("->")[-1],))
        log_erro("...source config_file part as follow...")
        log_warn("\n".join(block))
        log_erro("...source config_file part over...")
        return vpkg_placeHolder
    def _parse_sftw_block(block: list) -> str:
        expected = ("platform", "name", "version", "website", "autor", "publish", "description", "proxy")
        if len(block) < len(expected) + 1:
            return _syntax_panic(block[0], block)
        kv = {}
        for i, key in enumerate(expected):
            prefix = "    " + key + ":"
            line = block[i + 1]
            if not line.startswith(prefix):
                return _syntax_panic(block[0], block)
            kv[key] = line[len(prefix):].strip()
        for key in vpkg_info_kwOrder:
            value = kv.get(key, "")
            if key == "proxy":
                vpkg_info[key] = value in ("True", "true", "T", "t", "1")
                continue
            vpkg_info[key] = value
        return vpkg_placeHolder
    def _parse_tool_block(block: list) -> str:
        pre_keys = ("platform", "name", "version", "website", "local_path", "symbol_excu")
        if len(block) < 9:
            return _syntax_panic(block[0], block)
        common = {}
        for i, key in enumerate(pre_keys):
            prefix = "    " + key + ":"
            line = block[i + 1]
            if not line.startswith(prefix):
                return _syntax_panic(block[0], block)
            common[key] = line[len(prefix):].strip()
        install = {}
        env_arg = {}
        state = None
        for line in block[7:]:
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
            if not stripped:
                continue
            if state in ("install", "env_arg"):
                if "=" not in stripped:
                    return _syntax_panic(block[0], block)
                key, _, value = stripped.partition("=")
                key = key.strip()
                value = value.strip()
                (install if state == "install" else env_arg).setdefault(key, []).append(value)
        platform = common["platform"]
        tool_name = common["name"]
        if platform != vpkg_info["platform"]:
            log_info("info->“{tool_name}”...“{platformA}”...not match system platform...“{platformB}”!!!".format(
                tool_name=tool_name, platformA=platform, platformB=vpkg_info["platform"]))
            return vpkg_placeHolder
        vpkg_sftw["tool"][tool_name] = {
            "platform": platform,
            "name": tool_name,
            "version": common["version"],
            "website": common["website"],
            "local_path": common["local_path"],
            "symbol_excu": common["symbol_excu"],
            "install": install,
            "env_arg": env_arg,
            "install_statu": False,
        }
        return vpkg_placeHolder
    def _parse_script_block(block: list) -> str:
        pre_keys = ("platform", "name", "version", "website", "local_path")
        if len(block) < 7:
            return _syntax_panic(block[0], block)
        common = {}
        for i, key in enumerate(pre_keys):
            prefix = "    " + key + ":"
            line = block[i + 1]
            if not line.startswith(prefix):
                return _syntax_panic(block[0], block)
            common[key] = line[len(prefix):].strip()
        content_lines = []
        in_content = False
        for line in block[6:]:
            stripped = line.strip()
            if stripped == "init->content":
                in_content = True
                continue
            if stripped == "over->content":
                in_content = False
                continue
            if in_content:
                content_lines.append(line[8:] if len(line) >= 8 else line)
        platform = common["platform"]
        script_name = common["name"]
        if platform != vpkg_info["platform"]:
            log_info("info->“{script_name}”...“{platformA}”...not match system platform...“{platformB}”!!!".format(
                script_name=script_name, platformA=platform, platformB=vpkg_info["platform"]))
            return vpkg_placeHolder
        content_string = ""
        for ln in content_lines:
            if not ln:
                continue
            content_string += ln + "\n"
        vpkg_sftw["script"][script_name] = {
            "platform": platform,
            "name": script_name,
            "version": common["version"],
            "website": common["website"],
            "local_path": common["local_path"],
            "content": content_string,
            "install_statu": False,
        }
        return vpkg_placeHolder
    def _item_match() -> str:
        with open(vpkg_config_file, "r", encoding="utf8") as f:
            config_file_content = f.read()
        config_file_content = re.sub(r"#.*$", "", config_file_content, flags=re.MULTILINE)
        lines = [ln for ln in config_file_content.split("\n") if ln.strip() != ""]
        split_idx = [i for i in range(len(lines)) if lines[i] in vpkg_config_symbol]
        split_idx.append(len(lines))
        for b in range(len(split_idx) - 1):
            block = lines[split_idx[b]:split_idx[b + 1]]
            if not block:
                continue
            head = block[0]
            if head in ("info->sftw", "info=>sftw"):
                _parse_sftw_block(block)
            elif head in ("info->tool", "info=>tool"):
                _parse_tool_block(block)
            elif head in ("info->script", "info=>script"):
                _parse_script_block(block)
        return vpkg_placeHolder
    def _item_extra() -> str:
        for tool_name in list(vpkg_sftw["tool"].keys()):
            tool = vpkg_sftw["tool"][tool_name]
            platform = tool["platform"]
            name = tool["name"]
            version = tool["version"]
            new_local_path = _resolve_placeholders(tool["local_path"], platform, name, version, tool["local_path"])
            new_symbol_excu = _resolve_placeholders(tool["symbol_excu"], platform, name, version, new_local_path)
            new_install = {
                _resolve_placeholders(k, platform, name, version, new_local_path):
                    [_resolve_placeholders(v, platform, name, version, new_local_path) for v in vals]
                for k, vals in tool["install"].items()
            }
            new_env_arg = {
                _resolve_placeholders(k, platform, name, version, new_local_path):
                    [_resolve_placeholders(v, platform, name, version, new_local_path) for v in vals]
                for k, vals in tool["env_arg"].items()
            }
            tool["local_path"] = new_local_path
            tool["symbol_excu"] = new_symbol_excu
            tool["install"] = new_install
            tool["env_arg"] = new_env_arg
        for script_name in list(vpkg_sftw["script"].keys()):
            script = vpkg_sftw["script"][script_name]
            new_local = script["local_path"]
            new_local = new_local.replace("{vpkg_root}", vpkg_root_tree["root_vpkg"])
            new_local = new_local.replace("{vpkg_system}", vpkg_root_tree["root_system"])
            new_local = new_local.replace("{vpkg_tool}", vpkg_root_tree["root_tool"])
            new_local = new_local.replace("{vpkg_script}", vpkg_root_tree["root_script"])
            new_local = new_local.replace("{vpkg_cache}", vpkg_root_tree["root_cache"])
            new_local = new_local.replace("<platform>", script["platform"])
            new_local = new_local.replace("<name>", script["platform"])
            new_local = new_local.replace("<version>", script["platform"])
            script["local_path"] = new_local
        for idx in vpkg_root_tree.keys():
            necessary_dir = vpkg_root_tree[idx].format(vpkg_root=vpkg_root, platform=vpkg_info["platform"])
            vpkg_root_tree[idx] = necessary_dir
            if not os.path.exists(necessary_dir):
                os.mkdir(necessary_dir)
                log_warn("info->creat dir...>%s<" % (necessary_dir,))
        for idx in vpkg_sftw["tool"].keys():
            vpkg_sftw["tool"][idx]["install_statu"] = os.path.exists(vpkg_sftw["tool"][idx]["symbol_excu"])
        return vpkg_placeHolder
    def _item_check() -> str:
        platform = vpkg_info["platform"]
        for kind in ("tool", "script"):
            for idx in list(vpkg_sftw[kind].keys()):
                if vpkg_sftw[kind][idx]["platform"] != platform:
                    del vpkg_sftw[kind][idx]
        for idx in vpkg_sftw["tool"].keys():    # 检查配置文件中的软件
            vpkg_sftw["tool"][idx]["install_statu"] = os.path.exists(vpkg_sftw["tool"][idx]["symbol_excu"])
        for idx in vpkg_sftw["script"].keys():  # 检查配置文件中的脚本
            path = "%s/%s" % (vpkg_sftw["script"][idx]["local_path"], vpkg_sftw["script"][idx]["name"])
            vpkg_sftw["script"][idx]["install_statu"] = os.path.exists(path)
        exist_script = tuple(vpkg_sftw["script"].keys())
        for _,_,files in os.walk(vpkg_root_tree["root_script"]):    # 检查目录下存在但排除在外的脚本
            for file in files:
                file_name, file_ext = os.path.splitext(file)
                if file not in exist_script:
                    with open("%s/%s"%(vpkg_root_tree["root_script"],file),"r") as f:
                        file_content = f.read()
                    vpkg_sftw["script"][file_name] = {
                        "platform": "x64-win",
                        "name": file,
                        "version": "void",
                        "website": "void",
                        "local_path": vpkg_root_tree["root_script"],
                        "content": file_content,
                        "install_statu": True,
                    }
        exist_tool = tuple(idx for idx, v in vpkg_sftw["tool"].items() if v["install_statu"] == True)
        for idx in os.listdir(vpkg_root_tree["root_tool"]):    # 不是软件库的文件夹全部删除, 安装不成功的软件文件夹全部删除
            if idx not in exist_tool:
                shutil.rmtree("%s/%s"%(vpkg_root_tree["root_tool"],idx))
                log_warn("warn->tool_dir: del the empty or illegal dir...>%s<"%(idx))
        return vpkg_placeHolder
    def _install_script() -> str:
        for idx in vpkg_sftw["script"].keys():
            script_path = "%s/%s" % (vpkg_sftw["script"][idx]["local_path"], vpkg_sftw["script"][idx]["name"])
            if vpkg_sftw["script"][idx]["install_statu"] == True:
                continue
            with open(script_path, "w") as f:
                f.write(vpkg_sftw["script"][idx]["content"])
            log_info("info->func:extra_config._install_script, install script...>%s<" % (script_path,))
        return vpkg_placeHolder
    if os.path.exists(vpkg_config_file) == False:
        log_warn("warn->config file miss...>%s<" % (vpkg_config_file,))
        _item_extra()
        _item_check()
        _install_script()
        return vpkg_placeHolder
    _item_match()
    _item_extra()
    _item_check()
    _install_script()
    return vpkg_placeHolder

def extra_command() -> str: # 命令解析
    def _check_basic_sftw_statu() -> bool:
        sftw_statu = True
        for idx in vpkg_sftw_tool_basic:
            if vpkg_sftw["tool"][idx]["install_statu"] == False:
                sftw_statu = False
                log_erro("erro->lack of basic sftw...>%s<" % (idx,))
        return sftw_statu
    def _get_cli_arg() -> tuple:
        sys_argv = sys.argv
        if len(sys_argv) == 1:
            return (vpkg_placeHolder, list())
        return (sys_argv[1], sys_argv[2:])
    def _clean_dir(aim_path: str) -> str:
        if os.path.exists(aim_path) == False:
            log_warn("warn->not exists the dir...>%s<" % (aim_path,))
            return vpkg_placeHolder
        shutil.rmtree(aim_path)
        os.mkdir(aim_path)
        log_warn("warn->clean the dir...>%s<" % (aim_path,))
        return vpkg_placeHolder
    def _system_run_cmd(cmd) -> bool:
        try:
            if isinstance(cmd, str):
                result = subprocess.run(cmd, shell=True)
            else:
                result = subprocess.run(cmd)
        except (OSError, FileNotFoundError) as e:
            log_erro("erro->_system_run_cmd...%s...%s" % (cmd, e))
            return False
        if result.returncode != 0:
            log_erro("erro->_system_run_cmd...%s" % (cmd,))
        return result.returncode == 0
    def _file_download(file_url: str, out_dir: str) -> bool:
        file_url_real = file_url
        if vpkg_info["proxy"] == True:
            for idx in vpkg_download_proxy.keys():
                if idx in file_url_real:
                    file_url_real = file_url_real.replace(idx, vpkg_download_proxy[idx])
        aria2_statu = vpkg_sftw["tool"]["aria2"]["install_statu"]
        aria2_excu = vpkg_sftw["tool"]["aria2"]["symbol_excu"]
        wget_entry = vpkg_sftw["tool"].get("wget", {})
        wget_statu = wget_entry.get("install_statu", False)
        wget_excu = wget_entry.get("symbol_excu", "")
        cmd = [aria2_excu, file_url_real, "--dir=%s" % (out_dir,),
               "--allow-overwrite=true", "--max-connection-per-server=16", "--min-split-size=1M"]
        if aria2_statu == False and wget_statu == True:
            cmd = [wget_excu, "-P", out_dir, file_url_real]
        log_info("info->running command...\n\t%s" % " ".join(cmd))
        try:
            result = subprocess.run(cmd)
        except (OSError, FileNotFoundError) as e:
            log_erro("erro->download failed...>%s<...%s" % (file_url, e))
            return False
        if result.returncode != 0:
            log_erro("erro->download failed (code=%d): %s" % (result.returncode, file_url))
        return result.returncode == 0
    def _file_unzip(file_path: str, out_dir: str) -> bool:
        unzip_cmd_tool = vpkg_sftw["tool"]["a7z"]["symbol_excu"]
        cmd = [unzip_cmd_tool, "x", file_path, "-o" + out_dir, "-y"]
        log_info("info->running command...\n\t%s" % " ".join(cmd))
        try:
            result = subprocess.run(cmd)
        except (OSError, FileNotFoundError) as e:
            log_erro("erro->unzip failed...>%s<...%s" % (file_path, e))
            return False
        if result.returncode != 0:
            log_erro("erro->unzip failed (code=%d): %s" % (result.returncode, file_path))
        return result.returncode == 0
    def _cmd_help(cmd_valu: list) -> str:
        log_warn("info->vpkg sftw info start!!!")
        for idx in vpkg_info.keys():
            log_info("\t%-12s->\t%s" % (idx, vpkg_info[idx]))
        log_warn("info->vpkg usage...>vpkg \\[command] \\[argument]<")
        for idx in vpkg_cmd:
            log_info("\tsupport command: {cmd}".format(cmd=idx))
        log_warn("info->vpkg sftw info end!!!")
        return vpkg_placeHolder
    def _cmd_list(cmd_valu: list) -> str:
        log_warn("info->list software install status!!!")
        log_info("\t%-15s->%-15s->%-10s" % ("name", "install_status", "website"))
        for idx in vpkg_sftw["tool"].keys():
            tmp_tool_name = vpkg_sftw["tool"][idx]["name"]
            tmp_tool_install_statu = vpkg_sftw["tool"][idx]["install_statu"]
            tmp_tool_website = vpkg_sftw["tool"][idx]["website"]
            if tmp_tool_install_statu == True:
                log_info("\t%-15s->%-15s->%-10s" % (tmp_tool_name, tmp_tool_install_statu, tmp_tool_website))
                continue
            log_erro("\t%-15s->%-15s->%-10s" % (tmp_tool_name, tmp_tool_install_statu, tmp_tool_website))
        return vpkg_placeHolder
    def _cmd_shell(cmd_valu: list) -> str:
        origin_var = os.environ.copy()
        shell_var = {}
        path_key = "PATH"
        for idx in origin_var.keys():
            shell_var[idx] = origin_var[idx].replace("\\", "/")
            if idx.lower() == "path":
                path_key = idx
        for idx in vpkg_sftw["tool"].keys():
            if vpkg_sftw["tool"][idx]["install_statu"] == False:
                continue
            for k, vlist in vpkg_sftw["tool"][idx]["env_arg"].items():
                val = ";".join(vlist)
                existing = next((ek for ek in shell_var if ek.lower() == k.lower()), None)
                if existing:
                    shell_var[existing] = "%s;%s" % (shell_var[existing], val)
                else:
                    shell_var[k] = val
        if path_key not in shell_var:
            shell_var[path_key] = ""
        shell_var[path_key] = "%s;%s" % (shell_var[path_key], vpkg_root_tree["root_script"])
        if os.name == "nt":
            new_shell_arg = "title vpkg && prompt (vpkg) $P$G"
            subprocess.run(["cmd", "/k", new_shell_arg], env=shell_var)
            sys.exit(0)
        return vpkg_placeHolder
    def _cmd_install(cmd_valu: str) -> str:
        def _get_file_and_dir(aim_path: str) -> tuple:
            file_list = list()
            dir_list = list()
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
                entries = os.listdir(current)
                entries = [e for e in entries if not e.startswith('.')]
                subdirs = [e for e in entries if os.path.isdir(os.path.join(current, e))]
                if len(entries) != 1 or len(subdirs) != 1:
                    return current
                current = os.path.join(current, subdirs[0])
        def _install_script(script_name: str) -> str:
            if script_name not in vpkg_sftw["script"].keys():
                log_erro("erro->not exist script config...>%s<" % (script_name,))
                return vpkg_placeHolder
            script_file = vpkg_sftw["script"][script_name]["name"]
            script_root = vpkg_sftw["script"][script_name]["local_path"]
            script_path = "%s/%s" % (script_root, script_file)
            script_content = vpkg_sftw["script"][script_name]["content"]
            with open(script_path, "w") as f:
                f.write(script_content)
            return vpkg_placeHolder
        def _install_sftw(tool_name: str) -> str:
            cache_dir = vpkg_root_tree["root_cache"]
            extra_dir = vpkg_root_tree["root_extra"]
            _clean_dir(cache_dir)
            if os.path.exists(extra_dir) == False:
                os.makedirs(extra_dir, exist_ok=True)
            cache_init_file, _ = _get_file_and_dir(cache_dir)
            for install_item in vpkg_sftw["tool"][tool_name]["install"].keys():
                install_dir = install_item
                download_url_list = vpkg_sftw["tool"][tool_name]["install"][install_item]
                os.makedirs(install_dir, exist_ok=True)
                _clean_dir(install_dir)
                for url in download_url_list:
                    if not _file_download(url, cache_dir):
                        log_erro("erro->abort install %s, download failed" % (tool_name,))
                        return vpkg_placeHolder
                cache_over_file, _ = _get_file_and_dir(cache_dir)
                download_file_list = _get_differ_item(cache_init_file, cache_over_file)
                pack_file = list()
                move_file = list()
                for idx in download_file_list:
                    file = os.path.split(idx)[1]
                    ispack_flag = False
                    for pack_ext in vpkg_zip_ext["default"]:
                        if file.endswith(pack_ext):
                            pack_file.append(idx)
                            ispack_flag = True
                            break
                    if ispack_flag == False:
                        move_file.append(idx)
                for idx in pack_file:
                    _clean_dir(extra_dir)
                    if not _file_unzip(idx, extra_dir):
                        log_erro("erro->abort install %s, unzip failed" % (tool_name,))
                        return vpkg_placeHolder
                    unpack_dir = _get_stop_dir(extra_dir)
                    shutil.copytree(unpack_dir, install_dir, dirs_exist_ok=True)
                for idx in move_file:
                    old_file = idx
                    file = os.path.split(idx)[1]
                    new_file = os.path.join(install_dir, file)
                    if os.path.exists(new_file):
                        os.remove(new_file)
                    os.rename(old_file, new_file)
            return vpkg_placeHolder
        def _unique_handle(tool_name: str) -> str:
            if tool_name == "pixi":
                log_info("info->install DLC(init home) for...>pixi<")
                pixi_excu = vpkg_sftw["tool"][tool_name]["symbol_excu"]
                pixi_home = vpkg_sftw["tool"][tool_name]["local_path"]
                _system_run_cmd([pixi_excu, "init", pixi_home])
                vpkg_sftw["script"]["prefix"] = {
                    "platform": "x64-win",
                    "name": "prefix.bat",
                    "version": "1.0",
                    "website": "void",
                    "local_path": "{vpkg_script}".format(vpkg_script=vpkg_root_tree["root_script"]),
                    "content": "@echo off\ncall {pixi_excu} shell --manifest-path {pixi_config}".format(
                        pixi_excu=vpkg_sftw["tool"]["pixi"]["symbol_excu"],
                        pixi_config="%s/pixi.toml" % (vpkg_sftw["tool"]["pixi"]["local_path"],)),
                    "install_statu": bool(),
                }
                _install_script("prefix")
            if tool_name == "python":
                log_info("info->install DLC(pip) for...>python<")
                path_install = list(vpkg_sftw["tool"][tool_name]["install"].keys())[0]
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
                    with open(file_net_contorl, "r") as f:
                        new_content = f.read()
                    new_content = new_content.replace("#import site", "import site")
                    with open(file_net_contorl, "w") as f:
                        f.write(new_content)
                if file_net_contorl and file_get_pip and file_python_excu:
                    _system_run_cmd([file_python_excu, file_get_pip])
            if tool_name == "rust":
                log_info("info->install DLC for...>rust<")
                rust_env_arg = vpkg_sftw["tool"][tool_name]["env_arg"]
                rustup_home = rust_env_arg["rustup_home"][0]
                cargo_home = rust_env_arg["cargo_home"][0]
                os.environ["rustup_home"] = rustup_home
                os.environ["cargo_home"] = cargo_home
                rustup_excu = vpkg_sftw["tool"][tool_name]["symbol_excu"]
                _system_run_cmd([rustup_excu])
            if tool_name == "lua":
                log_info("info->install DLC(luarocks config.lua) for...>lua<")
                lua_ver = "5.5.0"
                lua_root = vpkg_sftw["tool"]["lua"]["local_path"]
                lua_include = "%s/include" % (lua_root,)
                lua_excu = vpkg_sftw["tool"]["lua"]["symbol_excu"]
                for file in os.listdir(lua_root):
                    if file.startswith("luac") and file.endswith(".exe"):
                        lua_excu = "%s/%s" % (lua_root, file)
                lua_excu_copy = "%s/lua.exe" % (lua_root,)
                shutil.copy2(lua_excu, lua_excu_copy)
                config_content = (
                    'lua_version = "<lua_ver>"\n',
                    'rocks_trees = {\n',
                    '\t{name = "user",root = "<lua_root>",},\n',
                    '}\n',
                    'variables = {\n',
                    '\tCC = "gcc",\n',
                    '\tCXX = "g++",\n',
                    '\tLINKFLAGS = "-shared",\n',
                    '\tLUA_VERSION = "<lua_ver>",\n',
                    '\tLUA = "<lua_excu>",\n',
                    '\tLUA_BINDIR = "<lua_root>",\n',
                    '\tLUA_INCDIR = "<lua_include>",\n',
                    '\tLUA_LIBDIR = "<lua_root>",\n',
                    '}',
                )
                vpkg_sftw["script"]["luarocks_config"] = {
                    "platform": "x64-win",
                    "name": "config.lua",
                    "version": "v1.0",
                    "website": "void",
                    "local_path": lua_root,
                    "content": "".join(config_content).replace(
                        "<lua_ver>", lua_ver
                    ).replace(
                        "<lua_root>", lua_root
                    ).replace(
                        "<lua_excu>", lua_excu_copy
                    ).replace(
                        "<lua_include>", lua_include
                    ),
                    "install_statu": bool(),
                }
                _install_script("luarocks_config")
            return vpkg_placeHolder
        def _run(tool_name: str) -> str:
            log_info("info->cheak the repo for aim sftw...")
            if not tool_name or tool_name == vpkg_placeHolder:
                log_erro("erro->command “install” argu is empty...")
                return vpkg_placeHolder
            if tool_name not in vpkg_sftw["tool"].keys():
                log_erro("erro->platform...>%s<...the repo not contain...>%s<" % (vpkg_info["platform"], tool_name))
                return vpkg_placeHolder
            log_info("info->check the basic sftw...")
            if not _check_basic_sftw_statu():
                log_erro("erro->lack of basic sftw...>%s<" % (vpkg_sftw_tool_basic,))
                return vpkg_placeHolder
            if vpkg_sftw["tool"][tool_name]["install_statu"] == True:
                log_info("info->the sftw >%s< already install!!!" % (tool_name,))
                return vpkg_placeHolder
            _install_sftw(tool_name)
            _unique_handle(tool_name)
            if not os.path.exists(vpkg_sftw["tool"][tool_name]["symbol_excu"]):
                log_erro("erro->install faild...>%s<" % (tool_name,))
                return vpkg_placeHolder
            log_info("info->install success...>%s<" % (tool_name,))
            return vpkg_placeHolder
        _run(cmd_valu)
        return vpkg_placeHolder
    def _cmd_remove(cmd_valu: str) -> str:
        tool_name = cmd_valu
        if tool_name in vpkg_sftw_tool_basic:
            log_erro("erro->can not remove the basic sftw...>%s<" % (tool_name,))
            return vpkg_placeHolder
        if tool_name not in vpkg_sftw["tool"].keys():
            log_erro("erro->repo not exist...>%s<" % (tool_name,))
            return vpkg_placeHolder
        if vpkg_sftw["tool"][tool_name]["install_statu"] == False:
            log_erro("erro->not install the sftw...>%s<" % (tool_name,))
            return vpkg_placeHolder
        install_path = vpkg_sftw["tool"][tool_name]["local_path"]
        install_path_father = os.path.split(install_path)[0]
        shutil.rmtree(install_path)
        if os.path.exists(install_path_father) and len(os.listdir(install_path_father)) == 0:
            shutil.rmtree(install_path_father)
        log_warn("warn->success remove sftw...>%s<" % (tool_name,))
        return vpkg_placeHolder
    def _cmd_excu(cmd_valu: list) -> bool:
        if not cmd_valu:
            log_erro("erro->command “excu” argument is empty...")
            return False
        tool_name = cmd_valu[0]
        if tool_name in vpkg_sftw["tool"].keys():
            tool_excu = vpkg_sftw["tool"][tool_name]["symbol_excu"]
            cmd = [tool_excu] + list(cmd_valu[1:])
            log_info("info->running command...\n\t%s" % " ".join(cmd))
            result = subprocess.run(cmd)
            if result.returncode != 0:
                log_erro("erro->running command...erro exit!!!")
            return result.returncode == 0
        if tool_name in vpkg_sftw["script"].keys():
            tool_excu = "%s/%s"%(vpkg_sftw["script"][tool_name]["local_path"],vpkg_sftw["script"][tool_name]["name"])
            cmd = ["cmd", "/c", tool_excu] + list(cmd_valu[1:])
            log_info("info->running command...\n\t%s" % " ".join(cmd))
            result = subprocess.run(cmd)
            if result.returncode != 0:
                log_erro("erro->running command...erro exit!!!")
            return result.returncode == 0
        log_erro("erro->platform...>%s<...repo not exist...>%s<" % (vpkg_info["platform"], tool_name))
        return False
    cmd_type, cmd_valu = _get_cli_arg()
    log_warn("warn->func extra_command: %s...%s" % (cmd_type, cmd_valu))
    if cmd_type not in vpkg_cmd:
        log_erro("erro->vpkg not support command...>%s<" % (cmd_type,))
        return vpkg_placeHolder
    if cmd_type == "help":
        _cmd_help(cmd_valu)
    if cmd_type == "list":
        _cmd_list(cmd_valu)
    if cmd_type == "install":
        tool_name = vpkg_placeHolder
        if len(cmd_valu) > 0:
            tool_name = cmd_valu[0]
        _cmd_install(tool_name)
    if cmd_type == "remove":
        tool_name = vpkg_placeHolder
        if len(cmd_valu) > 0:
            tool_name = cmd_valu[0]
        _cmd_remove(tool_name)
    if cmd_type == "shell":
        _cmd_shell(cmd_valu)
    if cmd_type == "excu":
        _cmd_excu(cmd_valu)
    return vpkg_placeHolder

def main() -> str:
    init_program()
    log_info("info->vpkg local_path...>%s<" % (vpkg_root,))
    log_info("info->vpkg config_file path...>%s<" % (vpkg_config_file,))
    log_info("info->vpkg config_file exist...>%s<" % (os.path.exists(vpkg_config_file),))
    extra_config()
    _info_width = max(len(k) for k in vpkg_info.keys())
    _info_rows = ["info->vpkg_info:"]
    for _k, _v in vpkg_info.items():
        _info_rows.append("    {key:<{width}} -> {val}".format(key=_k, width=_info_width, val=_v))
    log_info("\n".join(_info_rows))
    extra_command()
    return vpkg_placeHolder

if __name__ == "__main__":
    main()