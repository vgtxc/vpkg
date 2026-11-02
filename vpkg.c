//lastEdit=>2026.11.03-00:41
//creat:2026.11.03
/*
    reference: vpkg.py[2026.11.03]
    build: llvm_mingw
    writeby: deepseek
*/
/* vpkg.c — 单文件纯 C 实现（含 remove 残留目录清理） */
#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#include <ctype.h>
#include <windows.h>

#define MAXP 1024
#define MAXB (MAXP*4)

/* ======================= 0. 彩色日志 ======================= */
#define COL_GREEN "\033[32m"
#define COL_BLUE  "\033[34m"
#define COL_RED   "\033[31m"
#define COL_RESET "\033[0m"

void enable_ansi(void){
    HANDLE h = GetStdHandle(STD_OUTPUT_HANDLE); DWORD m=0;
    if(GetConsoleMode(h,&m)){ m|=0x0004; SetConsoleMode(h,m); }
    SetConsoleOutputCP(65001);
}
void log_info(const char *fmt,...){
    va_list ap; printf(COL_GREEN); va_start(ap,fmt); vprintf(fmt,ap); va_end(ap); printf(COL_RESET "\n");
}
void log_warn(const char *fmt,...){
    va_list ap; printf(COL_BLUE);  va_start(ap,fmt); vprintf(fmt,ap); va_end(ap); printf(COL_RESET "\n");
}
void log_erro(const char *fmt,...){
    va_list ap; printf(COL_RED);   va_start(ap,fmt); vprintf(fmt,ap); va_end(ap); printf(COL_RESET "\n");
}

/* ======================= 1. 字符串辅助 ======================= */
static char *str_dup(const char *s){
    if(!s) return NULL; size_t n=strlen(s);
    char *r=(char*)malloc(n+1); memcpy(r,s,n+1); return r;
}
static char *str_replace_all(const char *src,const char *old_s,const char *new_s){
    if(!src) return NULL;
    if(!old_s||!*old_s||!new_s) return str_dup(src);
    size_t sl=strlen(src), ol=strlen(old_s), nl=strlen(new_s);
    size_t cap = sl+32; char *out=(char*)malloc(cap); size_t oc=0;
    const char *p=src;
    while(1){
        const char *hit=strstr(p,old_s);
        size_t seg = hit? (size_t)(hit-p): strlen(p);
        if(oc+seg+nl+1>cap){ cap=(oc+seg+nl+1)*2; out=(char*)realloc(out,cap); }
        memcpy(out+oc,p,seg); oc+=seg;
        if(!hit) break;
        memcpy(out+oc,new_s,nl); oc+=nl; p=hit+ol;
    }
    out[oc]=0; return out;
}
static int str_starts_with(const char *s,const char *pre){ return strncmp(s,pre,strlen(pre))==0; }
static int str_ends_with(const char *s,const char *suf){
    size_t sl=strlen(s), fl=strlen(suf); return sl>=fl && strcmp(s+sl-fl,suf)==0;
}
static char *str_trim_inplace(char *s){
    while(*s && isspace((unsigned char)*s)) s++;
    if(!*s) return s;
    char *e=s+strlen(s)-1;
    while(e>s && isspace((unsigned char)*e)) *e--=0;
    return s;
}
static int str_in_list(const char *s,const char *const *list,int n){
    for(int i=0;i<n;i++) if(list[i] && strcmp(s,list[i])==0) return 1;
    return 0;
}
static void splitext(const char *path,char **out_name,char **out_ext){
    const char *slash=strrchr(path,'/');
    const char *bslash=strrchr(path,'\\');
    const char *sep=(slash>bslash)?slash:bslash;
    const char *base= sep? sep+1: path;
    const char *dot=strrchr(base,'.');
    if(!dot){ *out_name=str_dup(base); *out_ext=str_dup(""); return; }
    size_t n=(size_t)(dot-base);
    *out_name=(char*)malloc(n+1); memcpy(*out_name,base,n); (*out_name)[n]=0;
    *out_ext=str_dup(dot);
}

/* ======================= 2. 动态数组 ======================= */
typedef struct { char **items; int count; int cap; } str_list;
static void list_init(str_list *l){ l->items=NULL; l->count=0; l->cap=0; }
static void list_push(str_list *l,const char *s){
    if(l->count>=l->cap){ l->cap=l->cap? l->cap*2:8; l->items=(char**)realloc(l->items,l->cap*sizeof(char*)); }
    l->items[l->count++]=str_dup(s);
}
static void list_free(str_list *l){
    for(int i=0;i<l->count;i++) free(l->items[i]);
    free(l->items); l->items=NULL; l->count=0; l->cap=0;
}
static int list_contains(str_list *l,const char *s){
    for(int i=0;i<l->count;i++) if(strcmp(l->items[i],s)==0) return 1;
    return 0;
}

/* ======================= 3. 键->值列表映射 ======================= */
typedef struct url_kv { char *key; str_list values; struct url_kv *next; } url_kv;
typedef struct { url_kv *head; } url_kv_map;

static url_kv *url_kv_find(url_kv_map *m,const char *key){
    for(url_kv *p=m->head;p;p=p->next) if(strcmp(p->key,key)==0) return p;
    return NULL;
}
static url_kv *url_kv_get_or_create(url_kv_map *m,const char *key){
    url_kv *kv=url_kv_find(m,key); if(kv) return kv;
    kv=(url_kv*)calloc(1,sizeof(url_kv)); kv->key=str_dup(key); list_init(&kv->values);
    if(!m->head) m->head=kv;
    else{ url_kv *p=m->head; while(p->next) p=p->next; p->next=kv; }
    return kv;
}
static void url_kv_map_free(url_kv_map *m){
    url_kv *p=m->head;
    while(p){ url_kv *n=p->next; free(p->key); list_free(&p->values); free(p); p=n; }
    m->head=NULL;
}

/* ======================= 4. 条目 ======================= */
typedef struct sftw_item {
    char *key;
    char *platform;
    char *name;
    char *version;
    char *website;
    char *local_path;
    char *symbol_excu;
    char *content;
    url_kv_map install;
    url_kv_map env_arg;
    int   install_statu;
    struct sftw_item *next;
} sftw_item;

typedef struct { sftw_item *head; int count; } sftw_dict;
static void sftw_dict_init(sftw_dict *d){ d->head=NULL; d->count=0; }
static sftw_item *sftw_find(sftw_dict *d,const char *key){
    for(sftw_item *p=d->head;p;p=p->next) if(strcmp(p->key,key)==0) return p;
    return NULL;
}
static sftw_item *sftw_add(sftw_dict *d,const char *key,const char *name){
    sftw_item *it=(sftw_item*)calloc(1,sizeof(sftw_item));
    it->key=str_dup(key);
    it->name=str_dup(name); it->platform=str_dup("");
    it->version=str_dup(""); it->website=str_dup("");
    it->local_path=str_dup(""); it->symbol_excu=str_dup(""); it->content=str_dup("");
    if(!d->head) d->head=it;
    else{ sftw_item *p=d->head; while(p->next) p=p->next; p->next=it; }
    d->count++; return it;
}

/* ======================= 5. 文件/目录 ======================= */
static int path_exists(const char *p){ return GetFileAttributesA(p)!=INVALID_FILE_ATTRIBUTES; }
static int is_dir(const char *p){
    DWORD a=GetFileAttributesA(p);
    return a!=INVALID_FILE_ATTRIBUTES && (a & FILE_ATTRIBUTE_DIRECTORY);
}
static int is_file(const char *p){
    DWORD a=GetFileAttributesA(p);
    return a!=INVALID_FILE_ATTRIBUTES && !(a & FILE_ATTRIBUTE_DIRECTORY);
}
static void mkdir_recursive(const char *path){
    char tmp[MAXB]; snprintf(tmp,sizeof(tmp),"%s",path);
    for(char *p=tmp;*p;p++) if(*p=='\\') *p='/';
    for(char *p=tmp+1;*p;p++) if(*p=='/'){ char c=*p; *p=0; CreateDirectoryA(tmp,NULL); *p=c; }
    CreateDirectoryA(tmp,NULL);
}
/* 返回 0 成功，非 0 表示至少一个文件/目录失败 */
static int rmtree(const char *path){
    if(!path_exists(path)) return 0;
    int err=0;
    if(is_file(path)){
        if(!DeleteFileA(path)) err=1;
        return err;
    }
    WIN32_FIND_DATAA fd; char pat[MAXB]; snprintf(pat,sizeof(pat),"%s/*",path);
    HANDLE h=FindFirstFileA(pat,&fd);
    if(h!=INVALID_HANDLE_VALUE){
        do{
            if(strcmp(fd.cFileName,".")==0||strcmp(fd.cFileName,"..")==0) continue;
            char sub[MAXB]; snprintf(sub,sizeof(sub),"%s/%s",path,fd.cFileName);
            if(rmtree(sub)) err=1;
        }while(FindNextFileA(h,&fd));
        FindClose(h);
    }
    if(!RemoveDirectoryA(path)) err=1;
    return err;
}
static void clean_dir(const char *aim_path){
    if(!path_exists(aim_path)){ log_warn("warn->not exists the dir...>%s<",aim_path); return; }
    rmtree(aim_path); CreateDirectoryA(aim_path,NULL);
    log_warn("warn->clean the dir...>%s<",aim_path);
}
typedef struct { str_list files; str_list dirs; } dir_scan;
static dir_scan scan_dir(const char *path){
    dir_scan ds; list_init(&ds.files); list_init(&ds.dirs);
    char pat[MAXB]; snprintf(pat,sizeof(pat),"%s/*",path);
    WIN32_FIND_DATAA fd; HANDLE h=FindFirstFileA(pat,&fd);
    if(h==INVALID_HANDLE_VALUE) return ds;
    do{
        if(strcmp(fd.cFileName,".")==0||strcmp(fd.cFileName,"..")==0) continue;
        char full[MAXB]; snprintf(full,sizeof(full),"%s/%s",path,fd.cFileName);
        if(fd.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) list_push(&ds.dirs,full);
        else                                               list_push(&ds.files,full);
    }while(FindNextFileA(h,&fd));
    FindClose(h); return ds;
}
static void copy_tree(const char *src,const char *dst){
    mkdir_recursive(dst);
    dir_scan ds=scan_dir(src);
    for(int i=0;i<ds.files.count;i++){
        const char *b=strrchr(ds.files.items[i],'/'); b=b?b+1:ds.files.items[i];
        char d[MAXB]; snprintf(d,sizeof(d),"%s/%s",dst,b);
        CopyFileA(ds.files.items[i],d,FALSE);
    }
    for(int i=0;i<ds.dirs.count;i++){
        const char *b=strrchr(ds.dirs.items[i],'/'); b=b?b+1:ds.dirs.items[i];
        char d[MAXB]; snprintf(d,sizeof(d),"%s/%s",dst,b);
        copy_tree(ds.dirs.items[i],d);
    }
    list_free(&ds.files); list_free(&ds.dirs);
}
static char *read_file_all(const char *path){
    FILE *fp=fopen(path,"rb"); if(!fp) return NULL;
    fseek(fp,0,SEEK_END); long sz=ftell(fp); fseek(fp,0,SEEK_SET);
    char *b=(char*)malloc(sz+1); fread(b,1,sz,fp); b[sz]=0; fclose(fp); return b;
}
static int write_file_all(const char *path,const char *content){
    FILE *fp=fopen(path,"wb"); if(!fp) return 0;
    fwrite(content,1,strlen(content),fp); fclose(fp); return 1;
}

/* ======================= 6. 进程执行 ======================= */
static int run_command(char *const argv[]){
    char cl[MAXB*4]; cl[0]=0;
    for(int i=0;argv[i];i++){
        if(i) strcat(cl," ");
        int need=strchr(argv[i],' ')||strchr(argv[i],'\t');
        if(need) strcat(cl,"\"");
        strcat(cl,argv[i]);
        if(need) strcat(cl,"\"");
    }
    STARTUPINFOA si; PROCESS_INFORMATION pi; memset(&si,0,sizeof(si)); si.cb=sizeof(si);
    memset(&pi,0,sizeof(pi));
    char copy[MAXB*4]; snprintf(copy,sizeof(copy),"%s",cl);
    if(!CreateProcessA(NULL,copy,NULL,NULL,TRUE,0,NULL,NULL,&si,&pi)) return -1;
    WaitForSingleObject(pi.hProcess,INFINITE);
    DWORD code=0; GetExitCodeProcess(pi.hProcess,&code);
    CloseHandle(pi.hProcess); CloseHandle(pi.hThread); return (int)code;
}
static int run_cmd_line(const char *cmdline){
    STARTUPINFOA si; PROCESS_INFORMATION pi; memset(&si,0,sizeof(si)); si.cb=sizeof(si);
    memset(&pi,0,sizeof(pi));
    char copy[MAXB*4]; snprintf(copy,sizeof(copy),"%s",cmdline);
    if(!CreateProcessA(NULL,copy,NULL,NULL,TRUE,0,NULL,NULL,&si,&pi)) return -1;
    WaitForSingleObject(pi.hProcess,INFINITE);
    DWORD code=0; GetExitCodeProcess(pi.hProcess,&code);
    CloseHandle(pi.hProcess); CloseHandle(pi.hThread); return (int)code;
}

/* ======================= 7. 全局变量 ======================= */
char *vpkg_root=NULL;
char *vpkg_config_file=NULL;
char *vpkg_root_tree[5]={NULL,NULL,NULL,NULL,NULL};
const char *vpkg_root_tree_keys[5]={"root_vpkg","root_system","root_tool","root_script","root_cache"};
const char *vpkg_config_symbol[6]={
    "info->sftw","info=>sftw","info->tool","info=>tool","info->script","info=>script"
};
struct {
    char *platform,*name,*version,*website,*autor,*publish,*description;
} vpkg_info;
const char *vpkg_info_kwOrder[7]={
    "platform","name","version","website","autor","publish","description"
};
const char *vpkg_sftw_tool_basic[2]={"a7z","aria2"};
const char *vpkg_placeHolder="ugv";
const char *vpkg_cmd[5]={"help","list","install","remove","shell"};
sftw_dict vpkg_sftw_tool;
sftw_dict vpkg_sftw_script;

const char *vpkg_zip_default[7]={
    ".7z",".zip",".rar",".7z.exe",".7z.001",".zip.001",".part001.rar"
};
const char *vpkg_zip_filter[22]={
    ".7z",".zip",".rar",".7z.exe",
    ".7z.001",".7z.002",".7z.003",".7z.004",".7z.005",".7z.006",
    ".zip.001",".zip.002",".zip.003",".zip.004",".zip.005",".zip.006",
    ".part001.rar",".part002.rar",".part003.rar",".part004.rar",".part005.rar",".part006.rar"
};
#define ROOT_VPKG   (vpkg_root_tree[0])
#define ROOT_SYSTEM (vpkg_root_tree[1])
#define ROOT_TOOL   (vpkg_root_tree[2])
#define ROOT_SCRIPT (vpkg_root_tree[3])
#define ROOT_CACHE  (vpkg_root_tree[4])

/* ======================= 8. init_program ======================= */
static void add_install(sftw_item *it,const char *k,const char *v){
    url_kv *kv=url_kv_get_or_create(&it->install,k); list_push(&kv->values,v);
}
static void add_env(sftw_item *it,const char *k,const char *v){
    url_kv *kv=url_kv_get_or_create(&it->env_arg,k); list_push(&kv->values,v);
}
static sftw_item *add_tool(const char *name,const char *version,const char *website,
                           const char *local_path,const char *symbol_excu){
    sftw_item *it=sftw_find(&vpkg_sftw_tool,name);
    if(!it) it=sftw_add(&vpkg_sftw_tool,name,name);
    free(it->platform); it->platform=str_dup("x64-win");
    free(it->version);  it->version =str_dup(version);
    free(it->website);  it->website =str_dup(website);
    free(it->local_path); it->local_path=str_dup(local_path);
    free(it->symbol_excu); it->symbol_excu=str_dup(symbol_excu);
    return it;
}
static sftw_item *add_script(const char *key,const char *name,const char *version,
                             const char *website,const char *local_path,const char *content){
    sftw_item *it=sftw_find(&vpkg_sftw_script,key);
    if(!it) it=sftw_add(&vpkg_sftw_script,key,name);
    free(it->platform); it->platform=str_dup("x64-win");
    free(it->version);  it->version =str_dup(version);
    free(it->website);  it->website =str_dup(website);
    free(it->local_path); it->local_path=str_dup(local_path);
    free(it->content);  it->content =str_dup(content);
    return it;
}

static void _item_default(void){
    vpkg_info.platform    = str_dup("x64-win");
    vpkg_info.name        = str_dup("vpkg");
    vpkg_info.version     = str_dup("v20261102");
    vpkg_info.website     = str_dup("https://github.com/vgtxc/vpkg.git");
    vpkg_info.autor       = str_dup("vgtxc");
    vpkg_info.publish     = str_dup("None");
    vpkg_info.description = str_dup("A lightWight sftw manager!!!");
    free(ROOT_VPKG);   ROOT_VPKG   = str_dup("{vpkg_root}");
    free(ROOT_SYSTEM); ROOT_SYSTEM = str_dup("{vpkg_root}/{platform}");
    free(ROOT_TOOL);   ROOT_TOOL   = str_dup("{vpkg_root}/{platform}/tool");
    free(ROOT_SCRIPT); ROOT_SCRIPT = str_dup("{vpkg_root}/{platform}/script");
    free(ROOT_CACHE);  ROOT_CACHE  = str_dup("{vpkg_root}/{platform}/cache");

    const char *LP="{vpkg_tool}/<name>/<version>";
    sftw_item *it;

    it=add_tool("a7z","v26.04","https://www.7-zip.org/",LP,"<local_path>/7za.exe");
    add_install(it,"<local_path>","https://github.com/ip7z/7zip/releases/download/26.04/7z2604-extra.7z");
    add_env(it,"path","<local_path>");

    it=add_tool("aria2","v1.37.0","https://github.com/aria2/aria2",LP,"<local_path>/aria2c.exe");
    add_install(it,"<local_path>","https://github.com/aria2/aria2/releases/latest/download/aria2-1.37.0-win-64bit-build1.zip");
    add_env(it,"aria2_home","<local_path>");
    add_env(it,"path","<local_path>");

    it=add_tool("ffmpeg","v.latest","https://github.com/BtbN/FFmpeg-Builds",LP,"<local_path>/bin/ffmpeg.exe");
    add_install(it,"<local_path>","https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip");
    add_env(it,"path","<local_path>/bin");

    it=add_tool("git","v2.55.0","https://git-scm.com/",LP,"<local_path>/bin/git.exe");
    add_install(it,"<local_path>","https://github.com/git-for-windows/git/releases/download/v2.55.0.windows.5/PortableGit-2.55.0.5-64-bit.7z.exe");
    add_env(it,"path","<local_path>");
    add_env(it,"path","<local_path>/bin");

    it=add_tool("pixi","v0.80.0","https://github.com/prefix-dev/pixi",LP,"<local_path>/pixi.exe");
    add_install(it,"<local_path>","https://github.com/prefix-dev/pixi/releases/download/v0.80.0/pixi-x86_64-pc-windows-msvc.zip");
    add_env(it,"path","<local_path>");

    it=add_tool("uv","v0.12.13","https://github.com/astral-sh/uv",LP,"<local_path>/uv.exe");
    add_install(it,"<local_path>","https://releases.astral.sh/github/uv/releases/download/0.12.13/uv-x86_64-pc-windows-msvc.zip");
    add_env(it,"path","<local_path>");

    it=add_tool("cmake","v4.5.0-rc1","https://github.com/Kitware/CMake",LP,"<local_path>/bin/cmake.exe");
    add_install(it,"<local_path>","https://github.com/Kitware/CMake/releases/download/v4.5.0-rc1/cmake-4.5.0-rc1-windows-x86_64.zip");
    add_env(it,"path","<local_path>");

    it=add_tool("xmake","v3.1.1","https://github.com/xmake-io/xmake",LP,"<local_path>/xmake.exe");
    add_install(it,"<local_path>","https://github.com/xmake-io/xmake/releases/download/v3.1.1/xmake-v3.1.1.win64.zip");
    add_env(it,"path","<local_path>");

    it=add_tool("vcpkg","v20260926","https://github.com/microsoft/vcpkg-tool",LP,"<local_path>/vcpkg.exe");
    add_install(it,"<local_path>","https://github.com/microsoft/vcpkg-tool/releases/download/2026-09-26/vcpkg.exe");
    add_env(it,"path","<local_path>");
    add_env(it,"vcpkg_root","<local_path>");

    it=add_tool("nodejs","v26.8.2","https://nodejs.org",LP,"<local_path>/node.exe");
    add_install(it,"<local_path>","https://nodejs.org/dist/v26.8.2/node-v26.8.2-win-x64.zip");
    add_env(it,"path","<local_path>");

    it=add_tool("python","v3.14.7","https://www.python.org",LP,"<local_path>/python.exe");
    add_install(it,"<local_path>","https://www.python.org/ftp/python/3.14.7/python-3.14.7-embed-amd64.zip");
    add_install(it,"<local_path>","https://bootstrap.pypa.io/get-pip.py");
    add_env(it,"path","<local_path>");
    add_env(it,"path","<local_path>/Scripts");

    it=add_tool("rust","v1.98.1","https://rust-lang.org/",LP,"<local_path>/rustup-init.exe");
    add_install(it,"<local_path>","https://static.rust-lang.org/rustup/dist/x86_64-pc-windows-msvc/rustup-init.exe");
    add_env(it,"rustup_home","<local_path>/rustup_home");
    add_env(it,"cargo_home","<local_path>/cargo_home");
    add_env(it,"path","<local_path>");
    add_env(it,"path","<local_path>/cargo_home/bin");
    add_env(it,"path","<local_path>/rustup_home");

    it=add_tool("java","v26","https://www.java.com",LP,"<local_path>/java.exe");
    add_install(it,"<local_path>","https://download.oracle.com/java/26/latest/jdk-26_windows-x64_bin.zip");
    add_env(it,"path","<local_path>");

    it=add_tool("golang","v1.27.1","https://golang.google.cn/",LP,"<local_path>/bin/go.exe");
    add_install(it,"<local_path>","https://golang.google.cn/dl/go1.27.1.windows-amd64.zip");
    add_env(it,"go_root","<local_path>");
    add_env(it,"path","<local_path>/bin");

    it=add_tool("zig","v0.17.0","https://ziglang.org/",LP,"<local_path>/zig.exe");
    add_install(it,"<local_path>","https://ziglang.org/builds/zig-x86_64-windows-0.17.0-dev.2125+0d600e488.zip");
    add_env(it,"path","<local_path>");

    it=add_tool("vlang","v0.5","https://vlang.io/",LP,"<local_path>/v.exe");
    add_install(it,"<local_path>","https://github.com/vlang/v/releases/latest/download/v_windows.zip");
    add_env(it,"path","<local_path>");

    it=add_tool("lua","v5.5.0","https://www.lua.org/",LP,"<local_path>/lua55.exe");
    add_install(it,"<local_path>","https://downloads.sourceforge.net/project/luabinaries/5.5.0/Tools%20Executables/lua-5.5.0_Win64_bin.zip?viasf=1");
    add_install(it,"<local_path>","http://downloads.sourceforge.net/project/luabinaries/5.5.0/Windows%20Libraries/Static/lua-5.5.0_Win64_mingw6_lib.zip?viasf=1");
    add_install(it,"<local_path>","https://luarocks.github.io/luarocks/releases/luarocks-3.13.0-windows-64.zip");
    add_env(it,"luarocks_config","<local_path>/config.lua");
    add_env(it,"path","<local_path>");

    it=add_tool("mingw_w64","v16.2.0","https://github.com/niXman/mingw-builds-binaries",LP,"<local_path>/bin/gcc.exe");
    add_install(it,"<local_path>","https://github.com/niXman/mingw-builds-binaries/releases/download/16.2.0-rt_v14-rev1/x86_64-16.2.0-release-posix-seh-ucrt-rt_v14-rev1.7z");
    add_env(it,"path","<local_path>/bin");

    it=add_tool("llvm_mingw","v20260908","https://github.com/mstorsjo/llvm-mingw",LP,"<local_path>/bin/gcc.exe");
    add_install(it,"<local_path>","https://github.com/mstorsjo/llvm-mingw/releases/download/20260908/llvm-mingw-20260908-ucrt-x86_64.zip");
    add_env(it,"path","<local_path>/bin");

    it=add_tool("llvm_msvc","v777.3.1","https://github.com/aftermathlabs/llvm-msvc",LP,"<local_path>/bin/clang-cl.exe");
    add_install(it,"<local_path>","https://github.com/aftermathlabs/llvm-msvc/releases/download/llvm-msvc-v777.3.1/windows-wrapper-llvm-msvc-PDB.zip.001");
    add_install(it,"<local_path>","https://github.com/aftermathlabs/llvm-msvc/releases/download/llvm-msvc-v777.3.1/windows-wrapper-llvm-msvc-PDB.zip.002");
    add_env(it,"path","<local_path>/bin");

    it=add_tool("llvm_winlibs","v16.2.0","https://github.com/brechtsanders/winlibs_mingw",LP,"<local_path>/bin/gcc.exe");
    add_install(it,"<local_path>","https://github.com/brechtsanders/winlibs_mingw/releases/download/16.2.0posix-23.1.3-14.0.0-ucrt-r3/winlibs-x86_64-posix-seh-gcc-16.2.0-llvm-23.1.3-mingw-w64ucrt-14.0.0-r3.7z");
    add_env(it,"path","<local_path>/bin");

    it=add_tool("mingw_winlibs","v16.2.0","https://github.com/brechtsanders/winlibs_mingw",LP,"<local_path>/bin/gcc.exe");
    add_install(it,"<local_path>","https://github.com/brechtsanders/winlibs_mingw/releases/download/16.2.0posix-23.1.3-14.0.0-ucrt-r3/winlibs-x86_64-posix-seh-gcc-16.2.0-mingw-w64ucrt-14.0.0-r3.7z");
    add_env(it,"path","<local_path>/bin");

    it=add_tool("llvm_qt","v6.11.2","https://github.com/yuanpeirong/buildQt",LP,"<local_path>/bin/qmake.exe");
    add_install(it,"<local_path>","https://github.com/yuanpeirong/buildQt/releases/download/Qt6.11.2_rev0/Qt_6.11.2-static-Release_llvm-mingw22.1.8_64_UCRT.7z");
    add_env(it,"path","<local_path>/bin");

    it=add_tool("mingw_qt","v6.11.2","https://github.com/yuanpeirong/buildQt",LP,"<local_path>/bin/qmake.exe");
    add_install(it,"<local_path>","https://github.com/yuanpeirong/buildQt/releases/download/Qt6.11.2_rev0/Qt_6.11.2-static-Release_mingw1620_64_UCRT.7z");
    add_env(it,"path","<local_path>/bin");

    it=add_tool("msvc_qt","v6.11.2","https://github.com/yuanpeirong/buildQt",LP,"<local_path>/bin/qmake.exe");
    add_install(it,"<local_path>","https://github.com/yuanpeirong/buildQt/releases/download/Qt6.11.2_rev0/Qt_6.11.2-static-Release_msvc2026_64.7z");
    add_env(it,"path","<local_path>/bin");

    add_script("unproxy","unproxy.bat","1.0","void","{vpkg_script}",
        "@echo off\nset http_proxy=\nset https_proxy=\necho info-}remove the proxy\n\n");
    add_script("proxy_clash","proxy_clash.bat","v1.0","void","{vpkg_script}",
        "@echo off\nset http_proxy=127.0.0.1:7890\nset https_proxy=127.0.0.1:7890\necho info-}set the proxy to http://127.0.0.1:7890\n\n");
    add_script("proxy_v2ray","proxy_v2ray.bat","v1.0","void","{vpkg_script}",
        "@echo off\nset http_proxy=127.0.0.1:7880\nset https_proxy=127.0.0.1:7880\necho info-}set the proxy to http://127.0.0.1:7880\n\n");
}

static void init_program(void){
    char exe[MAXP]; GetModuleFileNameA(NULL,exe,MAXP);
    char *slash=strrchr(exe,'\\'); if(!slash) slash=strrchr(exe,'/');
    if(slash) *slash=0;
    for(char *p=exe;*p;p++) if(*p=='\\') *p='/';
    vpkg_root=str_dup(exe);
    char buf[MAXB]; snprintf(buf,sizeof(buf),"%s/vpkg_config.txt",vpkg_root);
    vpkg_config_file=str_dup(buf);

    sftw_dict_init(&vpkg_sftw_tool);
    sftw_dict_init(&vpkg_sftw_script);
    vpkg_info.platform=NULL; vpkg_info.name=NULL; vpkg_info.version=NULL;
    vpkg_info.website=NULL; vpkg_info.autor=NULL;
    vpkg_info.publish=NULL; vpkg_info.description=NULL;

    _item_default();
}

/* ======================= 9. 占位符展开 ======================= */
static char *expand_root(const char *s){
    if(!s) return str_dup("");
    char *r=str_dup(s),*t;
    t=str_replace_all(r,"{vpkg_root}",ROOT_VPKG);        free(r); r=t;
    t=str_replace_all(r,"{vpkg_system}",ROOT_SYSTEM);    free(r); r=t;
    t=str_replace_all(r,"{vpkg_tool}",ROOT_TOOL);        free(r); r=t;
    t=str_replace_all(r,"{vpkg_script}",ROOT_SCRIPT);    free(r); r=t;
    t=str_replace_all(r,"{vpkg_cache}",ROOT_CACHE);      free(r); r=t;
    t=str_replace_all(r,"{platform}",vpkg_info.platform?vpkg_info.platform:""); free(r); r=t;
    return r;
}

static char *expand_keywords_tool(const char *s,sftw_item *it,int max_level){
    if(!s) return str_dup("");
    char *r=str_dup(s),*t;
    t=str_replace_all(r,"<platform>",it->platform?it->platform:""); free(r); r=t;
    t=str_replace_all(r,"<name>",it->name?it->name:"");             free(r); r=t;
    t=str_replace_all(r,"<version>",it->version?it->version:"");    free(r); r=t;
    if(max_level>=1){
        t=str_replace_all(r,"<local_path>",it->local_path?it->local_path:""); free(r); r=t;
    }
    if(max_level>=2){
        t=str_replace_all(r,"<symbol_excu>",it->symbol_excu?it->symbol_excu:""); free(r); r=t;
    }
    return r;
}

static char *expand_cross_ref(const char *s,sftw_dict *tools,sftw_dict *scripts){
    if(!s||!strchr(s,'<')) return str_dup(s?s:"");
    char *r=str_dup(s);

    const char *tool_fields[6]={"platform","name","version","website","local_path","symbol_excu"};
    for(sftw_item *it=tools->head;it;it=it->next){
        const char *vals[6]={it->platform,it->name,it->version,it->website,it->local_path,it->symbol_excu};
        for(int i=0;i<6;i++){
            char pat[MAXB]; snprintf(pat,sizeof(pat),"<tool.%s.%s>",it->key,tool_fields[i]);
            if(strstr(r,pat)){
                char *t=str_replace_all(r,pat,vals[i]?vals[i]:""); free(r); r=t;
            }
        }
    }
    const char *script_fields[6]={"platform","name","version","website","local_path","content"};
    for(sftw_item *it=scripts->head;it;it=it->next){
        const char *vals[6]={it->platform,it->name,it->version,it->website,it->local_path,it->content};
        for(int i=0;i<6;i++){
            char pat[MAXB]; snprintf(pat,sizeof(pat),"<script.%s.%s>",it->key,script_fields[i]);
            if(strstr(r,pat)){
                char *t=str_replace_all(r,pat,vals[i]?vals[i]:""); free(r); r=t;
            }
        }
    }
    const char *info_fields[7]={"platform","name","version","website","autor","publish","description"};
    const char *info_vals[7]={
        vpkg_info.platform,vpkg_info.name,vpkg_info.version,vpkg_info.website,
        vpkg_info.autor,vpkg_info.publish,vpkg_info.description
    };
    const char *nm = vpkg_info.name? vpkg_info.name : "vpkg";
    for(int i=0;i<7;i++){
        char pat[MAXB]; snprintf(pat,sizeof(pat),"<sftw.%s.%s>",nm,info_fields[i]);
        if(strstr(r,pat)){
            char *t=str_replace_all(r,pat,info_vals[i]?info_vals[i]:""); free(r); r=t;
        }
    }
    return r;
}

/* ======================= 10. extra_config ======================= */
static void _item_root_prepare(void){
    for(int i=0;i<5;i++){
        char *t=str_replace_all(vpkg_root_tree[i],"{vpkg_root}",vpkg_root); free(vpkg_root_tree[i]);
        char *u=str_replace_all(t,"{platform}",vpkg_info.platform?vpkg_info.platform:""); free(t);
        vpkg_root_tree[i]=u;
    }
    for(int i=0;i<5;i++){
        if(!path_exists(vpkg_root_tree[i])){
            mkdir_recursive(vpkg_root_tree[i]);
            log_warn("info->creat dir...>%s<",vpkg_root_tree[i]);
        }
    }
}

static void _item_expand_root(void){
    for(sftw_item *it=vpkg_sftw_tool.head;it;it=it->next){
        it->local_path = expand_root(it->local_path);
        it->symbol_excu= expand_root(it->symbol_excu);
        url_kv_map nm; nm.head=NULL;
        for(url_kv *kv=it->install.head;kv;kv=kv->next){
            char *nk=expand_root(kv->key);
            url_kv *nn=url_kv_get_or_create(&nm,nk); free(nk);
            for(int i=0;i<kv->values.count;i++){
                char *nv=expand_root(kv->values.items[i]);
                list_push(&nn->values,nv); free(nv);
            }
        }
        url_kv_map_free(&it->install); it->install=nm;

        url_kv_map ne; ne.head=NULL;
        for(url_kv *kv=it->env_arg.head;kv;kv=kv->next){
            char *nk=expand_root(kv->key);
            url_kv *nn=url_kv_get_or_create(&ne,nk); free(nk);
            for(int i=0;i<kv->values.count;i++){
                char *nv=expand_root(kv->values.items[i]);
                list_push(&nn->values,nv); free(nv);
            }
        }
        url_kv_map_free(&it->env_arg); it->env_arg=ne;
    }
    for(sftw_item *it=vpkg_sftw_script.head;it;it=it->next){
        it->local_path = expand_root(it->local_path);
    }
}

static void _item_expand_keywords(void){
    for(sftw_item *it=vpkg_sftw_tool.head;it;it=it->next){
        char *lp = expand_keywords_tool(it->local_path,it,0);
        lp = expand_cross_ref(lp,&vpkg_sftw_tool,&vpkg_sftw_script);
        free(it->local_path); it->local_path=lp;

        char *se = expand_keywords_tool(it->symbol_excu,it,1);
        se = expand_cross_ref(se,&vpkg_sftw_tool,&vpkg_sftw_script);
        free(it->symbol_excu); it->symbol_excu=se;

        url_kv_map nm; nm.head=NULL;
        for(url_kv *kv=it->install.head;kv;kv=kv->next){
            char *nk = expand_keywords_tool(kv->key,it,2);
            nk = expand_cross_ref(nk,&vpkg_sftw_tool,&vpkg_sftw_script);
            url_kv *nn=url_kv_get_or_create(&nm,nk); free(nk);
            for(int i=0;i<kv->values.count;i++){
                char *nv = expand_keywords_tool(kv->values.items[i],it,2);
                nv = expand_cross_ref(nv,&vpkg_sftw_tool,&vpkg_sftw_script);
                list_push(&nn->values,nv); free(nv);
            }
        }
        url_kv_map_free(&it->install); it->install=nm;

        url_kv_map ne; ne.head=NULL;
        for(url_kv *kv=it->env_arg.head;kv;kv=kv->next){
            char *nk = expand_keywords_tool(kv->key,it,2);
            nk = expand_cross_ref(nk,&vpkg_sftw_tool,&vpkg_sftw_script);
            url_kv *nn=url_kv_get_or_create(&ne,nk); free(nk);
            for(int i=0;i<kv->values.count;i++){
                char *nv = expand_keywords_tool(kv->values.items[i],it,2);
                nv = expand_cross_ref(nv,&vpkg_sftw_tool,&vpkg_sftw_script);
                list_push(&nn->values,nv); free(nv);
            }
        }
        url_kv_map_free(&it->env_arg); it->env_arg=ne;
    }
    for(sftw_item *it=vpkg_sftw_script.head;it;it=it->next){
        char *lp = expand_keywords_tool(it->local_path,it,0);
        lp = expand_cross_ref(lp,&vpkg_sftw_tool,&vpkg_sftw_script);
        free(it->local_path); it->local_path=lp;

        char *ct = expand_keywords_tool(it->content,it,1);
        ct = expand_cross_ref(ct,&vpkg_sftw_tool,&vpkg_sftw_script);
        free(it->content); it->content=ct;
    }
}

static void _item_extra(void){
    _item_root_prepare();
    _item_expand_root();
    _item_expand_keywords();
    for(sftw_item *it=vpkg_sftw_tool.head;it;it=it->next)
        it->install_statu = is_file(it->symbol_excu)?1:0;
}

static void _item_check(void){
    const char *plat=vpkg_info.platform;
    sftw_item **pp=&vpkg_sftw_tool.head;
    while(*pp){
        if(strcmp((*pp)->platform,plat)!=0){
            sftw_item *del=*pp; *pp=del->next;
            free(del->key); free(del->platform); free(del->name); free(del->version);
            free(del->website); free(del->local_path); free(del->symbol_excu); free(del->content);
            url_kv_map_free(&del->install); url_kv_map_free(&del->env_arg);
            free(del); vpkg_sftw_tool.count--;
        }else pp=&(*pp)->next;
    }
    sftw_item **qq=&vpkg_sftw_script.head;
    while(*qq){
        if(strcmp((*qq)->platform,plat)!=0){
            sftw_item *del=*qq; *qq=del->next;
            free(del->key); free(del->platform); free(del->name); free(del->version);
            free(del->website); free(del->local_path); free(del->symbol_excu); free(del->content);
            url_kv_map_free(&del->install); url_kv_map_free(&del->env_arg);
            free(del); vpkg_sftw_script.count--;
        }else qq=&(*qq)->next;
    }
    for(sftw_item *it=vpkg_sftw_tool.head;it;it=it->next)
        it->install_statu = is_file(it->symbol_excu)?1:0;
    for(sftw_item *it=vpkg_sftw_script.head;it;it=it->next){
        char p[MAXB]; snprintf(p,sizeof(p),"%s/%s",it->local_path,it->name);
        it->install_statu = is_file(p)?1:0;
    }
}

static void _install_script(const char *filter_key){
    for(sftw_item *it=vpkg_sftw_script.head;it;it=it->next){
        if(filter_key && strcmp(it->key,filter_key)!=0) continue;
        char path[MAXB]; snprintf(path,sizeof(path),"%s/%s",it->local_path,it->name);
        if(it->install_statu) continue;
        write_file_all(path,it->content?it->content:"");
        log_info("info->func:extra_config._install_script, install script...>%s<",path);
    }
}

static int is_block_header(const char *s){
    for(int i=0;i<6;i++) if(strcmp(s,vpkg_config_symbol[i])==0) return 1;
    return 0;
}
static void parse_sftw_block(char **lines,int n){
    char *platform=NULL,*name=NULL,*version=NULL,*website=NULL;
    char *autor=NULL,*publish=NULL,*description=NULL;
    for(int i=1;i<n;i++){
        char *lc=str_dup(lines[i]);
        char *t=str_trim_inplace(lc);
        if(!*t){ free(lc); continue; }
        char *colon=strchr(t,':');
        if(!colon){ free(lc); continue; }
        *colon=0;
        char *k=str_trim_inplace(t);
        char *v=str_trim_inplace(colon+1);
        if     (strcmp(k,"platform")==0) platform=str_dup(v);
        else if(strcmp(k,"name")==0)     name=str_dup(v);
        else if(strcmp(k,"version")==0)  version=str_dup(v);
        else if(strcmp(k,"website")==0)  website=str_dup(v);
        else if(strcmp(k,"autor")==0)    autor=str_dup(v);
        else if(strcmp(k,"publish")==0)  publish=str_dup(v);
        else if(strcmp(k,"description")==0) description=str_dup(v);
        free(lc);
    }
    if(platform){ free(vpkg_info.platform); vpkg_info.platform=platform; }
    if(name){ free(vpkg_info.name); vpkg_info.name=name; }
    if(version){ free(vpkg_info.version); vpkg_info.version=version; }
    if(website){ free(vpkg_info.website); vpkg_info.website=website; }
    if(autor){ free(vpkg_info.autor); vpkg_info.autor=autor; }
    if(publish){ free(vpkg_info.publish); vpkg_info.publish=publish; }
    if(description){ free(vpkg_info.description); vpkg_info.description=description; }
}
static void parse_tool_block(char **lines,int n){
    char *platform=NULL,*name=NULL,*version=NULL,*website=NULL;
    char *local_path=NULL,*symbol_excu=NULL;
    url_kv_map inst; inst.head=NULL;
    url_kv_map env;  env.head=NULL;
    int mode=0;
    for(int i=1;i<n;i++){
        char *lc=str_dup(lines[i]);
        char *t=str_trim_inplace(lc);
        if(!*t){ free(lc); continue; }
        if(strcmp(t,"init->install")==0){ mode=1; free(lc); continue; }
        if(strcmp(t,"over->install")==0){ mode=0; free(lc); continue; }
        if(strcmp(t,"init->env_arg")==0){ mode=2; free(lc); continue; }
        if(strcmp(t,"over->env_arg")==0){ mode=0; free(lc); continue; }
        if(mode==0){
            char *colon=strchr(t,':');
            if(colon){
                *colon=0;
                char *k=str_trim_inplace(t);
                char *v=str_trim_inplace(colon+1);
                if     (strcmp(k,"platform")==0)    platform=str_dup(v);
                else if(strcmp(k,"name")==0)        name=str_dup(v);
                else if(strcmp(k,"version")==0)     version=str_dup(v);
                else if(strcmp(k,"website")==0)     website=str_dup(v);
                else if(strcmp(k,"local_path")==0)  local_path=str_dup(v);
                else if(strcmp(k,"symbol_excu")==0) symbol_excu=str_dup(v);
            }
        }else{
            char *eq=strchr(t,'=');
            if(eq){
                *eq=0;
                char *k=str_trim_inplace(t);
                char *v=str_trim_inplace(eq+1);
                url_kv *kv=url_kv_get_or_create(mode==1?&inst:&env,k);
                list_push(&kv->values,v);
            }
        }
        free(lc);
    }
    if(name && platform && strcmp(platform,vpkg_info.platform)!=0){
        log_info("info->\"%s\"...\"%s\"...not match system platform...\"%s\"!!!",
                 name,platform,vpkg_info.platform);
        free(platform);free(name);free(version);free(website);
        free(local_path);free(symbol_excu);
        url_kv_map_free(&inst); url_kv_map_free(&env); return;
    }
    if(name && platform){
        sftw_item *it=sftw_find(&vpkg_sftw_tool,name);
        if(!it) it=sftw_add(&vpkg_sftw_tool,name,name);
        free(it->platform); it->platform=platform;
        free(it->version);  it->version = version?version:str_dup("");
        free(it->website);  it->website = website?website:str_dup("");
        free(it->local_path); it->local_path=local_path?local_path:str_dup("");
        free(it->symbol_excu); it->symbol_excu=symbol_excu?symbol_excu:str_dup("");
        url_kv_map_free(&it->install); it->install=inst;
        url_kv_map_free(&it->env_arg); it->env_arg=env;
    }else{
        free(platform);free(name);free(version);free(website);
        free(local_path);free(symbol_excu);
        url_kv_map_free(&inst); url_kv_map_free(&env);
    }
}
static void parse_script_block(char **lines,int n){
    char *platform=NULL,*name=NULL,*version=NULL,*website=NULL,*local_path=NULL;
    int in_content=0;
    str_list cl; list_init(&cl);
    for(int i=1;i<n;i++){
        char *lc=str_dup(lines[i]);
        char *t=str_trim_inplace(lc);
        if(!*t){ free(lc); continue; }
        if(strcmp(t,"init->content")==0){ in_content=1; free(lc); continue; }
        if(strcmp(t,"over->content")==0){ in_content=0; free(lc); continue; }
        if(in_content){ list_push(&cl,lines[i]); free(lc); continue; }
        char *colon=strchr(t,':');
        if(colon){
            *colon=0;
            char *k=str_trim_inplace(t);
            char *v=str_trim_inplace(colon+1);
            if     (strcmp(k,"platform")==0)    platform=str_dup(v);
            else if(strcmp(k,"name")==0)        name=str_dup(v);
            else if(strcmp(k,"version")==0)     version=str_dup(v);
            else if(strcmp(k,"website")==0)     website=str_dup(v);
            else if(strcmp(k,"local_path")==0)  local_path=str_dup(v);
        }
        free(lc);
    }
    size_t tot=1; for(int i=0;i<cl.count;i++) tot+=strlen(cl.items[i])+2;
    char *content=(char*)calloc(1,tot);
    for(int i=0;i<cl.count;i++){
        const char *s=cl.items[i];
        while(*s==' '||*s=='\t') s++;
        strcat(content,s); strcat(content,"\n");
    }
    if(name && platform && strcmp(platform,vpkg_info.platform)!=0){
        log_info("info->\"%s\"...\"%s\"...not match system platform...\"%s\"!!!",
                 name,platform,vpkg_info.platform);
        free(platform);free(name);free(version);free(website);free(local_path);free(content);
        list_free(&cl); return;
    }
    if(name && platform){
        sftw_item *it=sftw_find(&vpkg_sftw_script,name);
        if(!it) it=sftw_add(&vpkg_sftw_script,name,name);
        free(it->platform); it->platform=platform;
        free(it->version);  it->version = version?version:str_dup("");
        free(it->website);  it->website = website?website:str_dup("");
        free(it->local_path); it->local_path=local_path?local_path:str_dup("");
        free(it->content);  it->content = content?content:str_dup("");
    }else{
        free(platform);free(name);free(version);free(website);free(local_path);free(content);
    }
    list_free(&cl);
}
static void _item_match(void){
    char *raw=read_file_all(vpkg_config_file); if(!raw) return;
    int in_comment=0;
    for(char *p=raw;*p;p++){
        if(*p=='#') in_comment=1;
        else if(*p=='\n') in_comment=0;
        else if(in_comment) *p=' ';
    }
    str_list lines; list_init(&lines);
    char *p=raw;
    while(*p){
        char *nl=strchr(p,'\n');
        size_t len= nl? (size_t)(nl-p): strlen(p);
        char *one=(char*)malloc(len+1); memcpy(one,p,len); one[len]=0;
        char *t=one; while(*t==' '||*t=='\t') t++;
        if(*t) list_push(&lines,one);
        free(one);
        if(!nl) break;
        p=nl+1;
    }
    free(raw);

    int *split=(int*)malloc((lines.count+1)*sizeof(int));
    int sc=0;
    for(int i=0;i<lines.count;i++){
        char *c=str_dup(lines.items[i]);
        char *t=str_trim_inplace(c);
        if(is_block_header(t)) split[sc++]=i;
        free(c);
    }
    split[sc++]=lines.count;

    for(int i=0;i<sc-1;i++){
        int start=split[i], end=split[i+1];
        char *h=str_dup(lines.items[start]);
        char *ht=str_trim_inplace(h);
        if(strcmp(ht,"info->sftw")==0||strcmp(ht,"info=>sftw")==0)
            parse_sftw_block(&lines.items[start],end-start);
        else if(strcmp(ht,"info->tool")==0||strcmp(ht,"info=>tool")==0)
            parse_tool_block(&lines.items[start],end-start);
        else if(strcmp(ht,"info->script")==0||strcmp(ht,"info=>script")==0)
            parse_script_block(&lines.items[start],end-start);
        free(h);
    }
    free(split); list_free(&lines);
}
void extra_config(void){
    if(!path_exists(vpkg_config_file)){
        log_warn("warn->config file miss...>%s<",vpkg_config_file);
        _item_extra(); _item_check(); _install_script(NULL); return;
    }
    _item_match(); _item_extra(); _item_check(); _install_script(NULL);
}

/* ======================= 11. extra_command ======================= */
static int _check_basic_sftw_statu(void){
    int ok=1;
    for(int i=0;i<2;i++){
        sftw_item *it=sftw_find(&vpkg_sftw_tool,vpkg_sftw_tool_basic[i]);
        if(!it||!it->install_statu){
            ok=0;
            log_erro("erro->lack of basic sftw...>%s<",vpkg_sftw_tool_basic[i]);
        }
    }
    return ok;
}
static void _get_file_and_dir(const char *aim_path,str_list *files,str_list *dirs){
    list_init(files); list_init(dirs);
    dir_scan ds=scan_dir(aim_path);
    for(int i=0;i<ds.files.count;i++) list_push(files,ds.files.items[i]);
    for(int i=0;i<ds.dirs.count;i++)  list_push(dirs,ds.dirs.items[i]);
    list_free(&ds.files); list_free(&ds.dirs);
}
static void _get_differ_item(str_list *A,str_list *B,str_list *out){
    list_init(out);
    for(int i=0;i<B->count;i++)
        if(!list_contains(A,B->items[i])) list_push(out,B->items[i]);
}
static char *_get_stop_dir(const char *aim_path){
    char *cur=str_dup(aim_path);
    while(1){
        dir_scan ds=scan_dir(cur);
        int visible=0, subdirs=0;
        for(int i=0;i<ds.files.count;i++){
            const char *b=strrchr(ds.files.items[i],'/'); b=b?b+1:ds.files.items[i];
            if(b[0]!='.') visible++;
        }
        for(int i=0;i<ds.dirs.count;i++){
            const char *b=strrchr(ds.dirs.items[i],'/'); b=b?b+1:ds.dirs.items[i];
            if(b[0]!='.'){ visible++; subdirs++; }
        }
        if(visible!=1||subdirs!=1){ list_free(&ds.files); list_free(&ds.dirs); return cur; }
        char *next=NULL;
        for(int i=0;i<ds.dirs.count;i++){
            const char *b=strrchr(ds.dirs.items[i],'/'); b=b?b+1:ds.dirs.items[i];
            if(b[0]!='.'){ next=str_dup(ds.dirs.items[i]); break; }
        }
        list_free(&ds.files); list_free(&ds.dirs);
        if(!next) return cur;
        free(cur); cur=next;
    }
}
static int _file_download(const char *file_url,const char *out_dir){
    sftw_item *aria=sftw_find(&vpkg_sftw_tool,"aria2");
    if(!aria){ log_erro("erro->aria2 not in repo"); return 0; }
    char *argv[6];
    argv[0]=aria->symbol_excu; argv[1]=(char*)file_url;
    argv[2]="-d"; argv[3]=(char*)out_dir;
    argv[4]="--allow-overwrite=true"; argv[5]=NULL;
    log_info("info->running command...\n\t%s %s -d %s --allow-overwrite=true",
             aria->symbol_excu,file_url,out_dir);
    int code=run_command(argv);
    if(code!=0){ log_erro("erro->download failed (code=%d): %s",code,file_url); return 0; }
    return 1;
}
static int _file_unzip(const char *file_path,const char *out_dir){
    sftw_item *a7z=sftw_find(&vpkg_sftw_tool,"a7z");
    if(!a7z){ log_erro("erro->a7z not in repo"); return 0; }
    char outarg[MAXB]; snprintf(outarg,sizeof(outarg),"-o%s",out_dir);
    char *argv[6];
    argv[0]=a7z->symbol_excu; argv[1]="x"; argv[2]=(char*)file_path;
    argv[3]=outarg; argv[4]="-y"; argv[5]=NULL;
    log_info("info->running command...\n\t%s x %s %s -y",a7z->symbol_excu,file_path,outarg);
    int code=run_command(argv);
    if(code!=0){ log_erro("erro->unzip failed (code=%d): %s",code,file_path); return 0; }
    return 1;
}
static void _cmd_help(const char *valu){
    (void)valu;
    log_warn("info->vpkg sftw info start!!!");
    const char *vals[7]={vpkg_info.platform,vpkg_info.name,vpkg_info.version,
        vpkg_info.website,vpkg_info.autor,vpkg_info.publish,vpkg_info.description};
    for(int i=0;i<7;i++) log_info("\t%-12s->\t%s",vpkg_info_kwOrder[i],vals[i]?vals[i]:"");
    log_warn("info->vpkg usage...>vpkg \\[command] \\[argument]<");
    for(int i=0;i<5;i++) log_info("\tsupport command: %s",vpkg_cmd[i]);
    log_warn("info->vpkg sftw info end!!!");
}
static void _cmd_list(const char *valu){
    (void)valu;
    log_warn("info->list software install status!!!");
    log_info("\t%-15s->%-15s->%-10s","name","install_status","website");
    for(sftw_item *it=vpkg_sftw_tool.head;it;it=it->next){
        const char *st=it->install_statu?"True":"False";
        if(it->install_statu)
            log_info("\t%-15s->%-15s->%-10s",it->name,st,it->website?it->website:"");
        else
            log_erro("\t%-15s->%-15s->%-10s",it->name,st,it->website?it->website:"");
    }
}

/* ---- shell ---- */
typedef struct { char *k; char *v; } envpair;
typedef struct { envpair *items; int count; int cap; } env_list;
static void env_list_init(env_list *l){ l->items=NULL; l->count=0; l->cap=0; }
static void env_list_push(env_list *l,const char *k,const char *v){
    for(int i=0;i<l->count;i++) if(_stricmp(l->items[i].k,k)==0){
        free(l->items[i].v); l->items[i].v=str_dup(v); return;
    }
    if(l->count>=l->cap){ l->cap=l->cap?l->cap*2:32; l->items=(envpair*)realloc(l->items,l->cap*sizeof(envpair)); }
    l->items[l->count].k=str_dup(k); l->items[l->count].v=str_dup(v); l->count++;
}
static void env_list_append(env_list *l,const char *k,const char *add){
    for(int i=0;i<l->count;i++) if(_stricmp(l->items[i].k,k)==0){
        char buf[MAXB*2]; snprintf(buf,sizeof(buf),"%s;%s",l->items[i].v,add);
        free(l->items[i].v); l->items[i].v=str_dup(buf); return;
    }
    env_list_push(l,k,add);
}
static void env_list_free(env_list *l){
    for(int i=0;i<l->count;i++){ free(l->items[i].k); free(l->items[i].v); }
    free(l->items); l->items=NULL; l->count=0; l->cap=0;
}
static void _cmd_shell(const char *valu){
    (void)valu;
    char *orig=GetEnvironmentStringsA();
    env_list envs; env_list_init(&envs);
    char *path_key=NULL;
    char *p=orig;
    while(*p){
        char *eq=strchr(p,'=');
        if(eq&&eq>p){
            char *k=(char*)malloc(eq-p+1); memcpy(k,p,eq-p); k[eq-p]=0;
            env_list_push(&envs,k,eq+1);
            if(!path_key && _stricmp(k,"path")==0) path_key=str_dup(k);
            free(k);
        }
        p+=strlen(p)+1;
    }
    FreeEnvironmentStringsA(orig);
    if(!path_key) path_key=str_dup("PATH");

    for(sftw_item *it=vpkg_sftw_tool.head;it;it=it->next){
        if(!it->install_statu) continue;
        for(url_kv *kv=it->env_arg.head;kv;kv=kv->next){
            char buf[MAXB*4]; buf[0]=0;
            for(int i=0;i<kv->values.count;i++){
                if(i) strcat(buf,";");
                strcat(buf,kv->values.items[i]);
            }
            env_list_append(&envs,kv->key,buf);
        }
    }
    env_list_append(&envs,path_key,ROOT_SCRIPT);

    size_t tot=1;
    for(int i=0;i<envs.count;i++) tot+=strlen(envs.items[i].k)+1+strlen(envs.items[i].v)+1;
    char *block=(char*)calloc(1,tot); char *d=block;
    for(int i=0;i<envs.count;i++){
        size_t kl=strlen(envs.items[i].k), vl=strlen(envs.items[i].v);
        memcpy(d,envs.items[i].k,kl); d+=kl; *d++='=';
        memcpy(d,envs.items[i].v,vl); d+=vl; *d++=0;
    }
    *d=0;
    char cmdline[]="cmd /k \"title vpkg && prompt (vpkg) $P$G\"";
    STARTUPINFOA si; PROCESS_INFORMATION pi; memset(&si,0,sizeof(si)); si.cb=sizeof(si);
    memset(&pi,0,sizeof(pi));
    CreateProcessA(NULL,cmdline,NULL,NULL,TRUE,0,block,NULL,&si,&pi);
    WaitForSingleObject(pi.hProcess,INFINITE);
    CloseHandle(pi.hProcess); CloseHandle(pi.hThread);
    free(block); free(path_key); env_list_free(&envs);
}

/* ---- install ---- */
static int _install_sftw(const char *tool_name){
    sftw_item *it=sftw_find(&vpkg_sftw_tool,tool_name);
    if(!it) return 0;
    const char *cache_dir=ROOT_CACHE;
    char extra_dir[MAXB]; snprintf(extra_dir,sizeof(extra_dir),"%s/extra_dir",cache_dir);
    clean_dir(cache_dir);
    if(!path_exists(extra_dir)) mkdir_recursive(extra_dir);

    str_list init_files, init_dirs;
    _get_file_and_dir(cache_dir,&init_files,&init_dirs);

    for(url_kv *kv=it->install.head;kv;kv=kv->next){
        const char *install_dir=kv->key;
        mkdir_recursive(install_dir);
        clean_dir(install_dir);
        for(int i=0;i<kv->values.count;i++){
            if(!_file_download(kv->values.items[i],cache_dir)){
                log_erro("erro->abort install %s, download failed",tool_name);
                list_free(&init_files); list_free(&init_dirs); return 0;
            }
        }
        str_list over_files, over_dirs;
        _get_file_and_dir(cache_dir,&over_files,&over_dirs);
        str_list diff;
        _get_differ_item(&init_files,&over_files,&diff);

        str_list pack_file, move_file;
        list_init(&pack_file); list_init(&move_file);
        for(int i=0;i<diff.count;i++){
            const char *path=diff.items[i];
            const char *b=strrchr(path,'/'); b=b?b+1:path;
            char *name=NULL,*ext=NULL;
            splitext(b,&name,&ext);
            if(str_in_list(ext,vpkg_zip_default,7)) list_push(&pack_file,path);
            int is_filter=str_in_list(ext,vpkg_zip_filter,22);
            free(name); free(ext);
            if(is_filter) continue;
            list_push(&move_file,path);
        }
        for(int i=0;i<pack_file.count;i++){
            clean_dir(extra_dir);
            _file_unzip(pack_file.items[i],extra_dir);
            char *stop=_get_stop_dir(extra_dir);
            copy_tree(stop,install_dir);
            free(stop);
        }
        for(int i=0;i<move_file.count;i++){
            const char *old_file=move_file.items[i];
            const char *b=strrchr(old_file,'/'); b=b?b+1:old_file;
            char new_file[MAXB]; snprintf(new_file,sizeof(new_file),"%s/%s",install_dir,b);
            MoveFileExA(old_file,new_file,MOVEFILE_REPLACE_EXISTING);
        }
        list_free(&diff); list_free(&pack_file); list_free(&move_file);
        list_free(&over_files); list_free(&over_dirs);
    }
    list_free(&init_files); list_free(&init_dirs);
    return 1;
}
static void _unique_git(void){
    log_info("info->install DLC(init home) for...>git<");
    sftw_item *git=sftw_find(&vpkg_sftw_tool,"git");
    if(!git) return;
    const char *cache_dir=ROOT_CACHE;
    char extra_dir[MAXB]; snprintf(extra_dir,sizeof(extra_dir),"%s/extra_dir",cache_dir);
    const char *git_root=git->local_path;
    dir_scan ds=scan_dir(git_root);
    char pack[MAXB]="";
    for(int i=0;i<ds.files.count;i++){
        const char *b=strrchr(ds.files.items[i],'/'); b=b?b+1:ds.files.items[i];
        if(str_ends_with(b,".7z.exe")){ snprintf(pack,sizeof(pack),"%s",b); break; }
    }
    list_free(&ds.files); list_free(&ds.dirs);
    if(!pack[0]) return;
    char oldp[MAXB], newp[MAXB];
    snprintf(oldp,sizeof(oldp),"%s/%s",git_root,pack);
    snprintf(newp,sizeof(newp),"%s/%s",cache_dir,pack);
    MoveFileExA(oldp,newp,MOVEFILE_REPLACE_EXISTING);
    clean_dir(extra_dir);
    clean_dir(git_root);
    _file_unzip(newp,extra_dir);
    char *stop=_get_stop_dir(extra_dir);
    copy_tree(stop,git_root); free(stop);
}
static void _unique_pixi(void){
    log_info("info->install DLC(init home) for...>pixi<");
    sftw_item *pixi=sftw_find(&vpkg_sftw_tool,"pixi"); if(!pixi) return;
    char cmd[MAXB*2];
    snprintf(cmd,sizeof(cmd),"\"%s\" init \"%s\"",pixi->symbol_excu,pixi->local_path);
    run_cmd_line(cmd);
    char content[MAXB*3];
    snprintf(content,sizeof(content),
        "@echo off\ncall %s shell --manifest-path %s/pixi.toml",
        pixi->symbol_excu,pixi->local_path);
    sftw_item *it=sftw_find(&vpkg_sftw_script,"prefix");
    if(!it) it=sftw_add(&vpkg_sftw_script,"prefix","prefix.bat");
    free(it->platform); it->platform=str_dup("x64-win");
    free(it->version);  it->version =str_dup("1.0");
    free(it->website);  it->website =str_dup("void");
    free(it->local_path); it->local_path=str_dup(ROOT_SCRIPT);
    free(it->content);  it->content =str_dup(content);
    it->install_statu=0;
    _install_script("prefix");
}
static void _unique_python(void){
    log_info("info->install DLC(pip) for...>python<");
    sftw_item *py=sftw_find(&vpkg_sftw_tool,"python");
    if(!py||!py->install.head) return;
    const char *path_install=py->install.head->key;
    printf("%s\n",path_install);
    char f_pth[MAXB]="", f_pip[MAXB]="", f_py[MAXB]="";
    dir_scan ds=scan_dir(path_install);
    for(int i=0;i<ds.files.count;i++){
        if(str_ends_with(ds.files.items[i],"._pth")) snprintf(f_pth,sizeof(f_pth),"%s",ds.files.items[i]);
        if(str_ends_with(ds.files.items[i],"get-pip.py")) snprintf(f_pip,sizeof(f_pip),"%s",ds.files.items[i]);
        if(str_ends_with(ds.files.items[i],"python.exe")) snprintf(f_py,sizeof(f_py),"%s",ds.files.items[i]);
    }
    list_free(&ds.files); list_free(&ds.dirs);
    if(f_pth[0]){
        char *c=read_file_all(f_pth);
        if(c){
            char *nc=str_replace_all(c,"#import site","import site");
            write_file_all(f_pth,nc);
            free(nc); free(c);
        }
    }
    if(f_pth[0]&&f_pip[0]&&f_py[0]){
        char cmd[MAXB*2]; snprintf(cmd,sizeof(cmd),"\"%s\" \"%s\"",f_py,f_pip);
        run_cmd_line(cmd);
    }
}
static void _unique_rust(void){
    log_info("info->install DLC for...>rust<");
    sftw_item *rust=sftw_find(&vpkg_sftw_tool,"rust"); if(!rust) return;
    url_kv *rh=url_kv_find(&rust->env_arg,"rustup_home");
    url_kv *ch=url_kv_find(&rust->env_arg,"cargo_home");
    if(rh&&rh->values.count>0) SetEnvironmentVariableA("rustup_home",rh->values.items[0]);
    if(ch&&ch->values.count>0) SetEnvironmentVariableA("cargo_home",ch->values.items[0]);
    char cmd[MAXB*2]; snprintf(cmd,sizeof(cmd),"\"%s\"",rust->symbol_excu);
    run_cmd_line(cmd);
}
static void _unique_lua(void){
    log_info("info->install DLC(luarocks config.lua) for...>lua<");
    sftw_item *lua=sftw_find(&vpkg_sftw_tool,"lua"); if(!lua) return;
    const char *lua_ver="5.5.0";
    const char *lua_root=lua->local_path;
    char lua_include[MAXB]; snprintf(lua_include,sizeof(lua_include),"%s/include",lua_root);
    char lua_excu[MAXB];    snprintf(lua_excu,sizeof(lua_excu),"%s",lua->symbol_excu);
    dir_scan ds=scan_dir(lua_root);
    for(int i=0;i<ds.files.count;i++){
        const char *b=strrchr(ds.files.items[i],'/'); b=b?b+1:ds.files.items[i];
        if(str_starts_with(b,"luac") && str_ends_with(b,".exe"))
            snprintf(lua_excu,sizeof(lua_excu),"%s",ds.files.items[i]);
    }
    list_free(&ds.files); list_free(&ds.dirs);
    char lua_excu_copy[MAXB]; snprintf(lua_excu_copy,sizeof(lua_excu_copy),"%s/lua.exe",lua_root);
    CopyFileA(lua_excu,lua_excu_copy,FALSE);
    char config[MAXB*3];
    snprintf(config,sizeof(config),
        "lua_version = \"%s\"\n"
        "rocks_trees = {\n"
        "\t{name = \"user\",root = \"%s\",},\n"
        "}\n"
        "variables = {\n"
        "\tCC = \"gcc\",\n"
        "\tCXX = \"g++\",\n"
        "\tLINKFLAGS = \"-shared\",\n"
        "\tLUA_VERSION = \"%s\",\n"
        "\tLUA = \"%s\",\n"
        "\tLUA_BINDIR = \"%s\",\n"
        "\tLUA_INCDIR = \"%s\",\n"
        "\tLUA_LIBDIR = \"%s\",\n"
        "}",
        lua_ver,lua_root,lua_ver,lua_excu_copy,lua_root,lua_include,lua_root);
    char path[MAXB]; snprintf(path,sizeof(path),"%s/config.lua",lua_root);
    write_file_all(path,config);
}
static void _unique_handle(const char *tool_name){
    if(strcmp(tool_name,"git")==0)    _unique_git();
    if(strcmp(tool_name,"pixi")==0)   _unique_pixi();
    if(strcmp(tool_name,"python")==0) _unique_python();
    if(strcmp(tool_name,"rust")==0)   _unique_rust();
    if(strcmp(tool_name,"lua")==0)    _unique_lua();
}
static void _cmd_install(const char *tool_name){
    log_info("info->cheak the repo for aim sftw...");
    if(!tool_name||!*tool_name){ log_erro("erro->command \"install\" argu is empty..."); return; }
    sftw_item *it=sftw_find(&vpkg_sftw_tool,tool_name);
    if(!it){
        log_erro("erro->platform...>%s<...the repo not contain...>%s<",
                 vpkg_info.platform,tool_name);
        return;
    }
    log_info("info->check the basic sftw...");
    (void)_check_basic_sftw_statu();
    if(it->install_statu){
        log_info("info->the sftw >%s< already install!!!",tool_name);
        return;
    }
    _install_sftw(tool_name);
    _unique_handle(tool_name);
    if(!is_file(it->symbol_excu)){
        log_erro("erro->install faild...>%s<",tool_name);
        return;
    }
    log_info("info->install success...>%s<",tool_name);
}
/* 完全删除安装目录；若目录已残留但未安装，也同样清除残留目录树 */
static void _cmd_remove(const char *tool_name){
    if(!tool_name||!*tool_name){
        log_erro("erro->command \"remove\" argu is empty..."); return;
    }
    if(str_in_list(tool_name,vpkg_sftw_tool_basic,2)){
        log_erro("erro->can not remove the basic sftw...>%s<",tool_name); return;
    }
    sftw_item *it=sftw_find(&vpkg_sftw_tool,tool_name);
    if(!it){ log_erro("erro->repo not exist...>%s<",tool_name); return; }

    char path[MAXB]; snprintf(path,sizeof(path),"%s",it->local_path);
    int existed = path_exists(path);

    /* 既未安装也无残留目录：报“未安装” */
    if(!it->install_statu && !existed){
        log_erro("erro->not install the sftw...>%s<",tool_name);
        return;
    }

    /* (01) 删除安装目录（正常安装 / 残留目录都覆盖） */
    int rm_failed = 0;
    if(existed){
        if(rmtree(path) != 0) rm_failed = 1;
    }

    /* (02) 逐级向上清理空目录，边界为 tool 根（不删 tool 根本身）
     *   例如 .../tool/mingw_w64/v16.2.0 删除后：
     *     .../tool/mingw_w64 若空则删
     *     .../tool           到达 ROOT_TOOL 长度，停止
     */
    char *cur = str_dup(path);
    for(;;){
        char *last = strrchr(cur,'/');
        if(!last) break;
        *last = 0;                                /* cur 变为父目录 */
        if(strlen(cur) <= strlen(ROOT_TOOL)) break;
        if(!path_exists(cur)) break;
        dir_scan ds = scan_dir(cur);
        int empty = (ds.files.count==0 && ds.dirs.count==0);
        list_free(&ds.files); list_free(&ds.dirs);
        if(!empty) break;
        if(rmtree(cur) != 0){ rm_failed = 1; break; }
    }
    free(cur);

    if(rm_failed){
        log_erro("erro->remove sftw failed (some files may be in use)...>%s<",tool_name);
        return;
    }

    it->install_statu = 0;
    log_warn("warn->success remove sftw...>%s<",tool_name);
}
void extra_command(int argc,char **argv){
    const char *cmd_type=vpkg_placeHolder;
    const char *cmd_valu=NULL;
    if(argc>=2) cmd_type=argv[1];
    if(argc>=3) cmd_valu=argv[2];
    log_warn("warn->func extra_command: %s...%s",cmd_type,cmd_valu?cmd_valu:"");
    if(!str_in_list(cmd_type,vpkg_cmd,5)){
        log_erro("erro->vpkg not support command...>%s<",cmd_type); return;
    }
    if(strcmp(cmd_type,"help")==0)         _cmd_help(cmd_valu);
    else if(strcmp(cmd_type,"list")==0)    _cmd_list(cmd_valu);
    else if(strcmp(cmd_type,"install")==0) _cmd_install(cmd_valu);
    else if(strcmp(cmd_type,"remove")==0)  _cmd_remove(cmd_valu);
    else if(strcmp(cmd_type,"shell")==0)   _cmd_shell(cmd_valu);
}

/* ======================= 12. main ======================= */
int main(int argc,char **argv){
    enable_ansi();
    init_program();
    log_info("info->vpkg local_path...>%s<",vpkg_root);
    extra_config();
    extra_command(argc,argv);
    return 0;
}