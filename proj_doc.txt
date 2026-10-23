v20261013
    项目说明
    """
    >>>项目占位符: 
        ugv
    >>>项目文件:
        |-vpkg.py; 功能实现
        |-vpkg_config.txt; 配置文件
        |-cache; 临时文件夹
        |-platform; 平台根目录, 目前仅支持[x64-win,x64-linux,x64-mac,x64-unix]
        |---tool; 工具文件夹
        |---script; 脚本文件夹
    >>>vpkg.py中的核心dict:
        vpkg_info = {
            platform: str(),
            name: "vpkg",
            version: str(),
            website: str(),
            autor: "github@vgtxc, gitee@vgtxc",
            publish: str(),
            description: str(),
        }
        vpkg_sftw = {
            tool: {
                name: {
                    name: str(),
                    version: str(),
                    website: str(),
                    local_path: str(),
                    symbol_excu: str(),
                    install: {
                        install_path01: [download_pack01,download_pack02],
                        install_path02: ...,
                    },
                    env_arg: {
                        sys_env_name01: [add_value01,add_value02],
                        sys_env_name02: ...,
                    },
                },
                name02: {...},
            },
            script: {
                name: {
                    name: str(),
                    version: str(),
                    website: str(),
                    local_path: str(),
                    file_content: str()
                },
                name02: {...},
            },
        },
    >>>vpkg_config.txt规范
        A.严格要求缩进;
        B.禁止同行注释,只允许单行使用“#”开头注释;
        C.条目[info->sftw,info->tool,info->script]之间无顺序要求,关键词需要严格安装顺序[platform->name->version->website->local_path->symbol_excu->install,env_arg];
    """
    ##################################################
    ##################################################
    ##################################################
    # 1.只允许使用“#”进行单行注释
    # 2.合法的“条目(item)”
    #   |-item_type: [info->sftw,info->tool,info->script]
    #   |-“info->sftw”:vpkg软件信息
    #   |-“info->tool”:可安装工具信息
    #   |-“info->script”:创建的脚本信息
    # 3.“{}”:由python传入全局变量
    #   |-{vpkg_root}: vpkg.py,vpkg_config.txt等文件所在的路径
    #   |-{vpkg_x64-win} = {vpkg_root}/x64-win: x64-win平台根目录
    #   |---{vpkg_x64-win_tool} = {vpkg_x64-win}/tool: x64-win工具默认安装根目录
    #   |---{vpkg_x64-win_script} = {vpkg_x64-win}/script: x64-win脚本默认写入根目录
    #   |-{vpkg_x64-linux} = {vpkg_root}/x64-linux
    #   |---{vpkg_x64-linux_tool} = {vpkg_x64-linux}/tool
    #   |---{vpkg_x64-linux_script} = {vpkg_x64-linux}/script
    # 3.“关键词<keyword>”:由python实现每个条目内部的自引用
    #   |-sftw不允许内部自引用
    #   |-sftw关键字顺序: platform,name,version,website,autor->publish->description
    #   |-tool关键词顺序及引用层级: platform,name,version,website->local_path->symbol_excu->install->env_arg
    #   |-script关键词顺序及引用层级: platform,name,version,website->local_path->content
    #   |-只允许向前引用关键词,在python中通过按顺序替换字符实现该功能
    #   |-支持的keyword: 可选platform/name/version/local_path/symbol_excu
    #   |-每个条目的关键字类型,数量,顺序必须严格匹配,匹配到的值可以为空,但关键字不能缺失
    # 3.“<item_type.item_name.keyword>”:由python实现跨条目的互相引用
    #   |-只允许向前引用,只允许后续条目引用前面条目
    #   |-item_type可选sftw/tool/script: 指定引用条目类型
    #   |-item_name为选定类型下属的“条目”
    #   |-keyword为选定“条目”下的关键词: 可选platform/name/version/local_path/symbol_excu
    # 4.tool条目下软件的一般安装路径:{vpkg_root}/<platform>/tool/<name>/<version>
    #   |-下载文件为“单个其他文件”: 直接下载后移动到“安装路径”
    #   |-下载文件为“单个可执行文件”: 直接下载后移动到“安装路径”
    #   |-下载文件为“单个压缩包文件”: 下载后解压->找到解压文件夹下“包含非单个文件夹”的层级->将该层级的所有文件移动到“安装路径”
    #   |-err->(原生支持困难,需要借助7z工具)下载文件为“分卷压缩包文件”: 下载后解压->找到解压文件夹下“包含非单个文件夹”的层级->将该层级的所有文件移动到“安装路径”
    # 5.tool条目输入规范
    #   |-install关键词下的“分卷压缩包”必须放在“紧邻”的位置，不允许间隔放置
    #   |-env_arg关键词下的“统一变量”必须放在“紧邻”的位置，不允许间隔放置
    ##################################################
    ##################################################
    ##################################################