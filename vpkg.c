//lastEdit=>2026.11.06-01:03
//lastEdit=>2026.11.04-00:43
//lastEdit=>2026.11.03-00:41
//creat:2026.11.03
// gcc -std=c99 -O2 -Wall vpkg.c -o vpkg_c.exe
/*
    reference: vpkg.py[2026.11.03]
    build: llvm_mingw
    writeby: deepseek
    bug->安装软件A后再安装软件B,不会自动清空extra_dir,压缩包解压的clean_dir(extra_dir)失效
*/
/* vpkg.c - 单文件 C 实现 (对应 vpkg.py)
 * lastEdit: 2026.11.06
 * creat:    2026.11.06
 * aut:      vgtxc (port)
 * 依赖:     仅 C 标准库 + Windows API(可选 POSIX)
 */
/*
    deepseek prompt
    1.需求：使用纯c实现vpkg.py的全部功能；(0)必须使用c单文件实现所有功能; (1)c与py的逻辑必须完全一致；(2)c与py变量名函数的命名规则必须完全一致，严禁随意改变大小写; (3)c禁止随意使用第三方库, 头文件尽量少; (4)c在内部使用链表实现list和dict结构, 结构体名称必须分别为str_list, kv_map，实现增删改查时直接修改链表本身而非复制链表后修改，使用函数重载功能，保证str_list与kv_map的增删改查的函数名相同; (5)c内部处结构体和辅助函数外, 一切能闭包的函数全部闭包, 最好能与py的闭包保持一致; (6)需要考虑超长路径名称;
    2.文件说明: readme.txt为项目整体说明, vpkg.py为python源文件, vpkg_config.txt为配置文件;
*/
/* vpkg.c - C99 implementation of vpkg.py
 * lastEdit: 2026.11.07
 * 编译: gcc -O2 -std=c11 -o vpkg.exe vpkg.c
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#include <stdbool.h>
#include <ctype.h>

#ifdef _WIN32
#include <windows.h>
#include <direct.h>
#include <io.h>
#include <process.h>
#ifndef ENABLE_VIRTUAL_TERMINAL_PROCESSING
#  define ENABLE_VIRTUAL_TERMINAL_PROCESSING 0x0004
#endif
#else
#include <unistd.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <dirent.h>
#endif

/* ============================================================
 * 数据结构: str_list / kv_map
 * ============================================================ */
typedef enum { VAL_STR, VAL_BOOL, VAL_DICT, VAL_LIST } val_type;
typedef struct str_node { char *value; struct str_node *next; } str_node;
typedef struct str_list { str_node *head, *tail; size_t size; } str_list;
typedef struct kv_map kv_map;
typedef struct value {
    val_type type;
    union { char *str; int bool_val; kv_map *dict_val; str_list *list_val; } as;
} value;
typedef struct kv_node { char *key; value val; struct kv_node *next; } kv_node;
struct kv_map { kv_node *head, *tail; size_t size; };

/* ============================================================
 * 基础辅助
 * ============================================================ */
static int os_is_win(void) {
#ifdef _WIN32
    return 1;
#else
    return 0;
#endif
}

static char *xstrdup(const char *s) {
    if (!s) return NULL;
    size_t n = strlen(s) + 1;
    char *p = (char *)malloc(n);
    if (p) memcpy(p, s, n);
    return p;
}

/* 修复: 不使用 va_copy —— 每次循环从 va_start 重启, 避免参数读取错位 */
static char *xfmt(const char *fmt, ...) {
    va_list ap;
    size_t cap = 512;
    char *buf = (char *)malloc(cap);
    while (buf) {
        va_start(ap, fmt);
        int n = vsnprintf(buf, cap, fmt, ap);
        va_end(ap);
        if (n >= 0 && (size_t)n < cap) return buf;
        free(buf);
        cap *= 2;
        if (cap > 65536) return xstrdup("");
        buf = (char *)malloc(cap);
    }
    return xstrdup("");
}

static char *str_replace_all(const char *src, const char *from, const char *to) {
    if (!src) return xstrdup("");
    if (!from || !*from || !to) return xstrdup(src);
    size_t lf = strlen(from), lt = strlen(to), n = 0;
    const char *p = src;
    while ((p = strstr(p, from)) != NULL) { n++; p += lf; }
    size_t out_len = strlen(src) + n * (lt > lf ? lt - lf : 0) + 1;
    char *out = (char *)malloc(out_len); if (!out) return xstrdup("");
    char *w = out; const char *cur = src;
    while (1) {
        const char *hit = strstr(cur, from);
        if (!hit) { strcpy(w, cur); break; }
        size_t seg = (size_t)(hit - cur);
        memcpy(w, cur, seg); w += seg;
        memcpy(w, to, lt); w += lt;
        cur = hit + lf;
    }
    return out;
}

static char *path_join(const char *a, const char *b) {
    if (!a) return xstrdup(b ? b : "");
    if (!b) return xstrdup(a);
    size_t la = strlen(a), lb = strlen(b);
    char *out = (char *)malloc(la + lb + 2); if (!out) return NULL;
    memcpy(out, a, la); size_t pos = la;
    if (la > 0 && out[la-1] != '/' && out[la-1] != '\\') out[pos++] = '/';
    memcpy(out + pos, b, lb); out[pos + lb] = 0;
    return out;
}
static char *path_dir(const char *p) {
    if (!p) return xstrdup("");
    char *s = xstrdup(p); if (!s) return NULL;
    for (long i = (long)strlen(s) - 1; i >= 0; i--)
        if (s[i] == '/' || s[i] == '\\') { s[i] = 0; break; }
    return s;
}
static char *path_base(const char *p) {
    if (!p) return xstrdup("");
    const char *sep = strrchr(p, '/'), *sep2 = strrchr(p, '\\');
    if (sep2 && (!sep || sep2 > sep)) sep = sep2;
    return xstrdup(sep ? sep + 1 : p);
}
static int path_exists(const char *p) {
    if (!p) return 0;
#ifdef _WIN32
    return _access(p, 0) == 0;
#else
    return access(p, F_OK) == 0;
#endif
}
static int dir_exists(const char *p) {
    if (!p || !path_exists(p)) return 0;
#ifdef _WIN32
    DWORD a = GetFileAttributesA(p);
    return a != INVALID_FILE_ATTRIBUTES && (a & FILE_ATTRIBUTE_DIRECTORY);
#else
    struct stat st; if (stat(p, &st) != 0) return 0; return S_ISDIR(st.st_mode);
#endif
}
static int mkdir_single(const char *p) {
#ifdef _WIN32
    return _mkdir(p) == 0;
#else
    return mkdir(p, 0755) == 0;
#endif
}
static void mkdirs(const char *p) {
    if (!p || !*p || path_exists(p)) return;
    char *tmp = xstrdup(p); if (!tmp) return;
    for (char *q = tmp + 1; *q; q++) {
        if (*q == '/' || *q == '\\') { char c = *q; *q = 0; if (!path_exists(tmp)) mkdir_single(tmp); *q = c; }
    }
    if (!path_exists(tmp)) mkdir_single(tmp);
    free(tmp);
}
static void rmtree_rec(const char *p) {
    if (!p || !path_exists(p)) return;
    if (dir_exists(p)) {
#ifdef _WIN32
        char *pat = xfmt("%s\\*", p); WIN32_FIND_DATAA fd;
        HANDLE h = FindFirstFileA(pat, &fd); free(pat);
        if (h != INVALID_HANDLE_VALUE) {
            do {
                if (!strcmp(fd.cFileName, ".") || !strcmp(fd.cFileName, "..")) continue;
                char *full = path_join(p, fd.cFileName); rmtree_rec(full); free(full);
            } while (FindNextFileA(h, &fd));
            FindClose(h);
        }
        RemoveDirectoryA(p);
#else
        DIR *d = opendir(p);
        if (d) {
            struct dirent *e;
            while ((e = readdir(d))) {
                if (!strcmp(e->d_name, ".") || !strcmp(e->d_name, "..")) continue;
                char *full = path_join(p, e->d_name); rmtree_rec(full); free(full);
            }
            closedir(d);
        }
        rmdir(p);
#endif
    } else {
#ifdef _WIN32
        DeleteFileA(p);
#else
        unlink(p);
#endif
    }
}
static char *read_whole(const char *p) {
    if (!p) return NULL;
    FILE *f = fopen(p, "rb"); if (!f) return NULL;
    fseek(f, 0, SEEK_END); long n = ftell(f); fseek(f, 0, SEEK_SET);
    if (n < 0) n = 0;
    char *buf = (char *)malloc((size_t)n + 1);
    if (!buf) { fclose(f); return NULL; }
    size_t r = fread(buf, 1, (size_t)n, f); buf[r] = 0;
    fclose(f); return buf;
}
static int write_whole(const char *p, const char *content) {
    if (!p) return 0;
    FILE *f = fopen(p, "wb"); if (!f) return 0;
    if (content) fwrite(content, 1, strlen(content), f);
    fclose(f); return 1;
}
static int copy_file(const char *src, const char *dst) {
    FILE *in = fopen(src, "rb"); if (!in) return 0;
    FILE *out = fopen(dst, "wb"); if (!out) { fclose(in); return 0; }
    char buf[8192]; size_t r;
    while ((r = fread(buf, 1, sizeof(buf), in)) > 0) fwrite(buf, 1, r, out);
    fclose(in); fclose(out); return 1;
}

/* ============================================================
 * str_list 操作
 * ============================================================ */
static str_list *str_list_new(void) { return (str_list *)calloc(1, sizeof(str_list)); }
static void str_list_add(str_list *l, const char *s, const value *unused);
static int str_list_find(str_list *l, const char *s) {
    if (!l || !s) return 0;
    for (str_node *n = l->head; n; n = n->next)
        if (strcmp(n->value, s) == 0) return 1;
    return 0;
}
static char *str_list_get(str_list *l, size_t i) {
    if (!l) return NULL;
    str_node *n = l->head;
    while (n && i--) n = n->next;
    return n ? n->value : NULL;
}
static int str_list_remove(str_list *l, const char *s) {
    if (!l) return 0;
    str_node *prev = NULL;
    for (str_node *n = l->head; n; prev = n, n = n->next) {
        if (strcmp(n->value, s) == 0) {
            if (prev) prev->next = n->next; else l->head = n->next;
            if (l->tail == n) l->tail = prev;
            free(n->value); free(n); l->size--;
            return 1;
        }
    }
    return 0;
}
static size_t str_list_size(str_list *l) { return l ? l->size : 0; }
static void str_list_free(str_list *l) {
    if (!l) return;
    str_node *n = l->head;
    while (n) { str_node *nx = n->next; free(n->value); free(n); n = nx; }
    free(l);
}
static void str_list_add(str_list *l, const char *s, const value *unused) {
    (void)unused;
    if (!l || !s) return;
    str_node *n = (str_node *)calloc(1, sizeof(str_node));
    if (!n) return;
    n->value = xstrdup(s);
    if (l->tail) l->tail->next = n; else l->head = n;
    l->tail = n; l->size++;
}

/* ============================================================
 * kv_map 操作
 * ============================================================ */
static kv_map *kv_map_new(void) { return (kv_map *)calloc(1, sizeof(kv_map)); }
static void kv_map_free(kv_map *m);
static void kv_map_add(kv_map *m, const char *k, const value *v) {
    if (!m || !k || !v) return;
    kv_node *n = (kv_node *)calloc(1, sizeof(kv_node));
    if (!n) return;
    n->key = xstrdup(k); n->val = *v;
    if (m->tail) m->tail->next = n; else m->head = n;
    m->tail = n; m->size++;
}
static int kv_map_find(kv_map *m, const char *k) {
    if (!m || !k) return 0;
    for (kv_node *n = m->head; n; n = n->next)
        if (strcmp(n->key, k) == 0) return 1;
    return 0;
}
static value *kv_map_get(kv_map *m, const char *k) {
    if (!m || !k) return NULL;
    for (kv_node *n = m->head; n; n = n->next)
        if (strcmp(n->key, k) == 0) return &n->val;
    return NULL;
}
static int kv_map_remove(kv_map *m, const char *k) {
    if (!m) return 0;
    kv_node *prev = NULL;
    for (kv_node *n = m->head; n; prev = n, n = n->next) {
        if (strcmp(n->key, k) == 0) {
            if (prev) prev->next = n->next; else m->head = n->next;
            if (m->tail == n) m->tail = prev;
            free(n->key);
            if (n->val.type == VAL_STR) free(n->val.as.str);
            else if (n->val.type == VAL_DICT) kv_map_free(n->val.as.dict_val);
            else if (n->val.type == VAL_LIST) str_list_free(n->val.as.list_val);
            free(n); m->size--;
            return 1;
        }
    }
    return 0;
}
static size_t kv_map_size(kv_map *m) { return m ? m->size : 0; }
static void kv_map_free(kv_map *m) {
    if (!m) return;
    kv_node *n = m->head;
    while (n) {
        kv_node *nx = n->next;
        free(n->key);
        if (n->val.type == VAL_STR) free(n->val.as.str);
        else if (n->val.type == VAL_DICT) kv_map_free(n->val.as.dict_val);
        else if (n->val.type == VAL_LIST) str_list_free(n->val.as.list_val);
        free(n); n = nx;
    }
    free(m);
}

/* ============================================================
 * 统一"重载"宏
 * ============================================================ */
#define list_add(o, k, v)  _Generic((o), str_list*: str_list_add, kv_map*: kv_map_add)(o, k, v)
#define list_find(o, k)    _Generic((o), str_list*: str_list_find, kv_map*: kv_map_find)(o, k)
#define list_get(o, k)     _Generic((o), str_list*: str_list_get, kv_map*: kv_map_get)(o, k)
#define list_remove(o, k)  _Generic((o), str_list*: str_list_remove, kv_map*: kv_map_remove)(o, k)
#define list_size(o)       _Generic((o), str_list*: str_list_size, kv_map*: kv_map_size)(o)
#define list_free(o)       _Generic((o), str_list*: str_list_free, kv_map*: kv_map_free)(o)

/* ============================================================
 * 类型化读写
 * ============================================================ */
static const char *_getstr(kv_map *m, const char *k) {
    value *v = kv_map_get(m, k); return (v && v->type == VAL_STR) ? v->as.str : "";
}
static int _getbool(kv_map *m, const char *k) {
    value *v = kv_map_get(m, k); return (v && v->type == VAL_BOOL) ? v->as.bool_val : 0;
}
static kv_map *_getdict(kv_map *m, const char *k) {
    value *v = kv_map_get(m, k); return (v && v->type == VAL_DICT) ? v->as.dict_val : NULL;
}
static str_list *_getlist(kv_map *m, const char *k) {
    value *v = kv_map_get(m, k); return (v && v->type == VAL_LIST) ? v->as.list_val : NULL;
}
static void _clean_val(value *v) {
    if (v->type == VAL_STR) free(v->as.str);
    else if (v->type == VAL_DICT) kv_map_free(v->as.dict_val);
    else if (v->type == VAL_LIST) str_list_free(v->as.list_val);
}
static void _setstr(kv_map *m, const char *k, const char *s) {
    value *v = kv_map_get(m, k);
    if (!v) { value nv; nv.type = VAL_STR; nv.as.str = xstrdup(s ? s : ""); kv_map_add(m, k, &nv); return; }
    _clean_val(v); v->type = VAL_STR; v->as.str = xstrdup(s ? s : "");
}
static void _setbool(kv_map *m, const char *k, int b) {
    value *v = kv_map_get(m, k);
    if (!v) { value nv; nv.type = VAL_BOOL; nv.as.bool_val = b; kv_map_add(m, k, &nv); return; }
    _clean_val(v); v->type = VAL_BOOL; v->as.bool_val = b;
}
static void _setdict(kv_map *m, const char *k, kv_map *d) {
    value *v = kv_map_get(m, k);
    if (!v) { value nv; nv.type = VAL_DICT; nv.as.dict_val = d; kv_map_add(m, k, &nv); return; }
    _clean_val(v); v->type = VAL_DICT; v->as.dict_val = d;
}
static void _setlist(kv_map *m, const char *k, str_list *l) {
    value *v = kv_map_get(m, k);
    if (!v) { value nv; nv.type = VAL_LIST; nv.as.list_val = l; kv_map_add(m, k, &nv); return; }
    _clean_val(v); v->type = VAL_LIST; v->as.list_val = l;
}

/* ============================================================
 * scandir / walk / copy_tree
 * ============================================================ */
static void scandir_paths(const char *p, str_list *files, str_list *dirs) {
    if (!p) return;
#ifdef _WIN32
    char *pat = xfmt("%s\\*", p); WIN32_FIND_DATAA fd;
    HANDLE h = FindFirstFileA(pat, &fd); free(pat);
    if (h == INVALID_HANDLE_VALUE) return;
    do {
        if (!strcmp(fd.cFileName, ".") || !strcmp(fd.cFileName, "..")) continue;
        char *full = path_join(p, fd.cFileName);
        if (fd.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) { if (dirs) str_list_add(dirs, full, NULL); }
        else { if (files) str_list_add(files, full, NULL); }
        free(full);
    } while (FindNextFileA(h, &fd));
    FindClose(h);
#else
    DIR *d = opendir(p); if (!d) return;
    struct dirent *e;
    while ((e = readdir(d))) {
        if (!strcmp(e->d_name, ".") || !strcmp(e->d_name, "..")) continue;
        char *full = path_join(p, e->d_name);
        struct stat st;
        if (stat(full, &st) == 0 && S_ISDIR(st.st_mode)) { if (dirs) str_list_add(dirs, full, NULL); }
        else { if (files) str_list_add(files, full, NULL); }
        free(full);
    }
    closedir(d);
#endif
}
typedef void (*walk_cb)(const char *path, const char *fname, void *ud);
static void walk_dir(const char *p, walk_cb cb, void *ud) {
    if (!p || !dir_exists(p)) return;
    str_list *files = str_list_new(), *dirs = str_list_new();
    scandir_paths(p, files, dirs);
    for (str_node *n = files ? files->head : NULL; n; n = n->next) {
        char *base = path_base(n->value); cb(n->value, base, ud); free(base);
    }
    for (str_node *n = dirs ? dirs->head : NULL; n; n = n->next) walk_dir(n->value, cb, ud);
    str_list_free(files); str_list_free(dirs);
}
static void copy_tree(const char *src, const char *dst) {
    if (!src || !dst) return;
    mkdirs(dst);
    str_list *files = str_list_new(), *dirs = str_list_new();
    scandir_paths(src, files, dirs);
    for (str_node *n = files ? files->head : NULL; n; n = n->next) {
        char *base = path_base(n->value);
        char *to = path_join(dst, base);
        copy_file(n->value, to);
        free(base); free(to);
    }
    for (str_node *n = dirs ? dirs->head : NULL; n; n = n->next) {
        char *base = path_base(n->value);
        char *to = path_join(dst, base);
        copy_tree(n->value, to);
        free(base); free(to);
    }
    str_list_free(files); str_list_free(dirs);
}

/* ============================================================
 * 日志 / ANSI
 * ============================================================ */
static const char *vpkg_placeHolder;
static int _ansi_enabled = -1;
static int _enable_ansi(void) {
    if (!os_is_win()) return 1;
#ifdef _WIN32
    HANDLE h = GetStdHandle(STD_OUTPUT_HANDLE);
    DWORD mode;
    if (h == INVALID_HANDLE_VALUE || !GetConsoleMode(h, &mode)) return 0;
    return SetConsoleMode(h, mode | ENABLE_VIRTUAL_TERMINAL_PROCESSING) ? 1 : 0;
#else
    return 1;
#endif
}
static void _log_color(const char *color, const char *msg) {
    if (_ansi_enabled < 0) _ansi_enabled = _enable_ansi();
    if (_ansi_enabled) printf("%s%s\033[0m\n", color, msg ? msg : "");
    else printf("%s\n", msg ? msg : "");
}
static void log_info(const char *msg) { _log_color("\033[32m", msg); }
static void log_warn(const char *msg) { _log_color("\033[34m", msg); }
static void log_erro(const char *msg) { _log_color("\033[31m", msg); }

/* ============================================================
 * 全局变量
 * ============================================================ */
static char *vpkg_root;
static char *vpkg_config_file;
static const char *vpkg_config_default;
static kv_map *vpkg_root_tree;
static str_list *vpkg_config_symbol;
static kv_map *vpkg_info;
static str_list *vpkg_info_kwOrder;
static kv_map *vpkg_sftw;
static kv_map *vpkg_sftw_toolFmt;
static kv_map *vpkg_sftw_scriptFmt;
static str_list *vpkg_sftw_tool_kwOrder;
static str_list *vpkg_sftw_script_kwOrder;
static str_list *vpkg_sftw_tool_basic;
static str_list *vpkg_cmd;
static kv_map *vpkg_zip_ext;
static kv_map *vpkg_download_proxy;

/* ============================================================
 * init_program
 * ============================================================ */
static void init_program(void) {
#ifdef _WIN32
    char exepath[4096];
    DWORD n = GetModuleFileNameA(NULL, exepath, (DWORD)sizeof(exepath));
    if (n > 0) {
        for (long i = (long)n - 1; i >= 0; i--)
            if (exepath[i] == '\\' || exepath[i] == '/') { exepath[i] = 0; break; }
        for (char *p = exepath; *p; p++) if (*p == '\\') *p = '/';
        vpkg_root = xstrdup(exepath);
    } else vpkg_root = xstrdup(".");
#else
    char buf[4096]; ssize_t n = readlink("/proc/self/exe", buf, sizeof(buf) - 1);
    if (n > 0) {
        buf[n] = 0;
        for (ssize_t i = n - 1; i >= 0; i--) if (buf[i] == '/') { buf[i] = 0; break; }
        vpkg_root = xstrdup(buf);
    } else vpkg_root = xstrdup(".");
#endif
    vpkg_config_file = path_join(vpkg_root, "vpkg_config.txt");
    vpkg_config_symbol = str_list_new();
    str_list_add(vpkg_config_symbol, "info->sftw", NULL);
    str_list_add(vpkg_config_symbol, "info=>sftw", NULL);
    str_list_add(vpkg_config_symbol, "info->tool", NULL);
    str_list_add(vpkg_config_symbol, "info=>tool", NULL);
    str_list_add(vpkg_config_symbol, "info->script", NULL);
    str_list_add(vpkg_config_symbol, "info=>script", NULL);
    vpkg_info = kv_map_new();
    { const char *ks[] = {"platform","name","version","website","autor","publish","description"};
      for (int i = 0; i < 7; i++) _setstr(vpkg_info, ks[i], "");
      _setbool(vpkg_info, "proxy", 0); }
    vpkg_info_kwOrder = str_list_new();
    { const char *ks[] = {"platform","name","version","website","autor","publish","description","proxy"};
      for (int i = 0; i < 8; i++) str_list_add(vpkg_info_kwOrder, ks[i], NULL); }
    vpkg_sftw = kv_map_new();
    _setdict(vpkg_sftw, "tool", kv_map_new());
    _setdict(vpkg_sftw, "script", kv_map_new());
    vpkg_sftw_toolFmt = kv_map_new();
    { const char *ks[] = {"platform","name","version","website","local_path","symbol_excu"};
      for (int i = 0; i < 6; i++) _setstr(vpkg_sftw_toolFmt, ks[i], "");
      _setstr(vpkg_sftw_toolFmt, "install", ""); _setstr(vpkg_sftw_toolFmt, "env_arg", "");
      _setbool(vpkg_sftw_toolFmt, "install_statu", 0); }
    vpkg_sftw_scriptFmt = kv_map_new();
    { const char *ks[] = {"platform","name","version","website","local_path","content"};
      for (int i = 0; i < 6; i++) _setstr(vpkg_sftw_scriptFmt, ks[i], "");
      _setbool(vpkg_sftw_scriptFmt, "install_statu", 0); }
    vpkg_sftw_tool_kwOrder = str_list_new();
    { const char *ks[] = {"platform","name","version","website","local_path","symbol_excu","install","env_arg","install_statu"};
      for (int i = 0; i < 9; i++) str_list_add(vpkg_sftw_tool_kwOrder, ks[i], NULL); }
    vpkg_sftw_script_kwOrder = str_list_new();
    { const char *ks[] = {"platform","name","version","website","local_path","content","install_statu"};
      for (int i = 0; i < 7; i++) str_list_add(vpkg_sftw_script_kwOrder, ks[i], NULL); }
    vpkg_sftw_tool_basic = str_list_new();
    str_list_add(vpkg_sftw_tool_basic, "a7z", NULL);
    str_list_add(vpkg_sftw_tool_basic, "aria2", NULL);
    vpkg_placeHolder = "ugv";
    vpkg_cmd = str_list_new();
    { const char *cs[] = {"help","list","install","remove","shell","excu"};
      for (int i = 0; i < 6; i++) str_list_add(vpkg_cmd, cs[i], NULL); }
    vpkg_root_tree = kv_map_new();
    _setstr(vpkg_root_tree, "root_vpkg",   "{vpkg_root}");
    _setstr(vpkg_root_tree, "root_system", "{vpkg_root}/{platform}");
    _setstr(vpkg_root_tree, "root_tool",   "{vpkg_root}/{platform}/tool");
    _setstr(vpkg_root_tree, "root_script", "{vpkg_root}/{platform}/script");
    _setstr(vpkg_root_tree, "root_cache",  "{vpkg_root}/{platform}/cache");
    _setstr(vpkg_root_tree, "root_extra",  "{vpkg_root}/{platform}/cache/extra_dir");
    vpkg_zip_ext = kv_map_new();
    {
        str_list *l;
        l = str_list_new(); { const char *v[] = {".7z", ".zip", ".rar", ".7z.exe"}; for (int i = 0; i < 4; i++) str_list_add(l, v[i], NULL); } _setlist(vpkg_zip_ext, "single_file", l);
        l = str_list_new(); { const char *v[] = {".7z.001", ".7z.002", ".7z.003", ".7z.004", ".7z.005", ".7z.006"}; for (int i = 0; i < 6; i++) str_list_add(l, v[i], NULL); } _setlist(vpkg_zip_ext, "multi_7z", l);
        l = str_list_new(); { const char *v[] = {".zip.001", ".zip.002", ".zip.003", ".zip.004", ".zip.005", ".zip.006"}; for (int i = 0; i < 6; i++) str_list_add(l, v[i], NULL); } _setlist(vpkg_zip_ext, "multi_zip", l);
        l = str_list_new(); { const char *v[] = {".part001.rar", ".part002.rar", ".part003.rar", ".part004.rar", ".part005.rar", ".part006.rar"}; for (int i = 0; i < 6; i++) str_list_add(l, v[i], NULL); } _setlist(vpkg_zip_ext, "multi_rar", l);
        l = str_list_new(); { const char *v[] = {".7z", ".zip", ".rar", ".7z.exe", ".7z.001", ".zip.001", ".part001.rar"}; for (int i = 0; i < 7; i++) str_list_add(l, v[i], NULL); } _setlist(vpkg_zip_ext, "default", l);
        l = str_list_new(); { const char *v[] = {".7z", ".zip", ".rar", ".7z.exe",
            ".7z.001", ".7z.002", ".7z.003", ".7z.004", ".7z.005", ".7z.006",
            ".zip.001", ".zip.002", ".zip.003", ".zip.004", ".zip.005", ".zip.006",
            ".part001.rar", ".part002.rar", ".part003.rar", ".part004.rar", ".part005.rar", ".part006.rar"};
          for (int i = 0; i < 22; i++) str_list_add(l, v[i], NULL); } _setlist(vpkg_zip_ext, "filter", l);
    }
    vpkg_download_proxy = kv_map_new();
    {
        const char *ps[][2] = {
            {"https://github.com/","https://xget.xi-xu.me/gh/"},
            {"https://gist.github.com/","https://xget.xi-xu.me/gist/"},
            {"https://gitlab.com/","https://xget.xi-xu.me/gl/"},
            {"https://gitea.com/","https://xget.xi-xu.me/gitea/"},
            {"https://codeberg.org/","https://xget.xi-xu.me/codeberg/"},
            {"https://sourceforge.net/","https://xget.xi-xu.me/sf/"},
            {"https://android.googlesource.com/","https://xget.xi-xu.me/aosp/"},
            {"https://huggingface.co/","https://xget.xi-xu.me/hf/"},
            {"https://civitai.com/","https://xget.xi-xu.me/civitai/"},
            {"https://registry.npmjs.org/","https://xget.xi-xu.me/npm/"},
            {"https://pypi.org/","https://xget.xi-xu.me/pypi/"},
            {"https://repo.anaconda.com/","https://xget.xi-xu.me/conda/"},
            {"https://conda.anaconda.org/","https://xget.xi-xu.me/conda/community/"},
            {"https://repo1.maven.org/","https://xget.xi-xu.me/maven/"},
            {"https://downloads.apache.org/","https://xget.xi-xu.me/apache/"},
            {"https://plugins.gradle.org/","https://xget.xi-xu.me/gradle/"},
            {"https://github.com/Homebrew/","https://xget.xi-xu.me/homebrew/"},
            {"https://rubygems.org/","https://xget.xi-xu.me/rubygems/"},
            {"https://cran.r-project.org/","https://xget.xi-xu.me/cran/"},
            {"https://www.cpan.org/","https://xget.xi-xu.me/cpan/"},
            {"https://tug.ctan.org/","https://xget.xi-xu.me/ctan/"},
            {"https://proxy.golang.org/","https://xget.xi-xu.me/golang/"},
            {"https://api.nuget.org/","https://xget.xi-xu.me/nuget/"},
            {"https://crates.io/","https://xget.xi-xu.me/crates/"},
            {"https://repo.packagist.org/","https://xget.xi-xu.me/packagist/"},
            {"https://dl.flathub.org/","https://xget.xi-xu.me/flathub/"},
            {"https://deb.debian.org/","https://xget.xi-xu.me/debian/"},
            {"https://archive.ubuntu.com/","https://xget.xi-xu.me/ubuntu/"},
            {"https://mirrors.kernel.org/fedora/","https://xget.xi-xu.me/fedora/"},
            {"https://download.rockylinux.org/","https://xget.xi-xu.me/rocky/"},
            {"https://download.opensuse.org/","https://xget.xi-xu.me/opensuse/"},
            {"https://geo.mirror.pkgbuild.com/","https://xget.xi-xu.me/arch/"},
            {"https://arxiv.org/","https://xget.xi-xu.me/arxiv/"},
            {"https://f-droid.org/","https://xget.xi-xu.me/fdroid/"},
            {"https://updates.jenkins.io/","https://xget.xi-xu.me/jenkins/"},
        };
        for (int i = 0; i < (int)(sizeof(ps)/sizeof(ps[0])); i++) _setstr(vpkg_download_proxy, ps[i][0], ps[i][1]);
    }

    vpkg_config_default =
"info->sftw\n"
"    platform: x64-win\n"
"    name: vpkg\n"
"    version: v20261102\n"
"    website: https://github.com/vgtxc/vpkg.git\n"
"    autor: vgtxc\n"
"    publish: None\n"
"    description: A lightWight sftw manager!!!\n"
"    proxy: False\n"
"info->tool\n"
"    platform: x64-win\n"
"    name: a7z\n"
"    version: v26.04\n"
"    website: https://www.7-zip.org/\n"
"    local_path: {vpkg_tool}/<name>/<version>\n"
"    symbol_excu: <local_path>/7za.exe\n"
"    init->install\n"
"        <local_path>=https://github.com/ip7z/7zip/releases/download/26.04/7z2604-extra.7z\n"
"    over->install\n"
"    init->env_arg\n"
"        path=<local_path>\n"
"    over->env_arg\n"
"info->tool\n"
"    platform: x64-win\n"
"    name: aria2\n"
"    version: v1.37.0\n"
"    website: https://github.com/aria2/aria2\n"
"    local_path: {vpkg_tool}/<name>/<version>\n"
"    symbol_excu: <local_path>/aria2c.exe\n"
"    init->install\n"
"        <local_path>=https://github.com/aria2/aria2/releases/latest/download/aria2-1.37.0-win-64bit-build1.zip\n"
"    over->install\n"
"    init->env_arg\n"
"        aria2_home=<local_path>\n"
"        path=<local_path>\n"
"    over->env_arg\n"
"info->tool\n"
"    platform: x64-win\n"
"    name: wget\n"
"    version: v1.25.0\n"
"    website: https://eternallybored.org/misc/wget/\n"
"    local_path: {vpkg_tool}/<name>/<version>\n"
"    symbol_excu: <local_path>/wget.exe\n"
"    init->install\n"
"        <local_path>=https://eternallybored.org/misc/wget/releases/wget-1.25.0-win64.zip\n"
"    over->install\n"
"    init->env_arg\n"
"        wget_home=<local_path>\n"
"        path=<local_path>\n"
"    over->env_arg\n"
"info->tool\n"
"    platform: x64-win\n"
"    name: fastCapture\n"
"    version: v11.3\n"
"    website: https://www.faststone.org/\n"
"    local_path: {vpkg_tool}/<name>/<version>\n"
"    symbol_excu: <local_path>/FSCapture.exe\n"
"    init->install\n"
"        <local_path>=https://www.faststonesoft.net/DN/FSCapture113.zip\n"
"    over->install\n"
"    init->env_arg\n"
"        path=<local_path>\n"
"    over->env_arg\n"
"info->tool\n"
"    platform: x64-win\n"
"    name: ncnn_vulkan\n"
"    version: v20250915\n"
"    website: https://github.com/BtbN/FFmpeg-Builds\n"
"    local_path: {vpkg_tool}/<name>/<version>\n"
"    symbol_excu: <local_path>/waifu2x-ncnn-vulkan.exe\n"
"    init->install\n"
"        <local_path>=https://github.com/nihui/waifu2x-ncnn-vulkan/releases/download/20250915/waifu2x-ncnn-vulkan-20250915-windows.zip\n"
"    over->install\n"
"    init->env_arg\n"
"        path=<local_path>\n"
"    over->env_arg\n"
"info->tool\n"
"    platform: x64-win\n"
"    name: ffmpeg\n"
"    version: v.latest\n"
"    website: https://github.com/BtbN/FFmpeg-Builds\n"
"    local_path: {vpkg_tool}/<name>/<version>\n"
"    symbol_excu: <local_path>/bin/ffmpeg.exe\n"
"    init->install\n"
"        <local_path>=https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip\n"
"    over->install\n"
"    init->env_arg\n"
"        path=<local_path>/bin\n"
"    over->env_arg\n"
"info->tool\n"
"    platform: x64-win\n"
"    name: git\n"
"    version: v2.55.0\n"
"    website: https://git-scm.com/\n"
"    local_path: {vpkg_tool}/<name>/<version>\n"
"    symbol_excu: <local_path>/bin/git.exe\n"
"    init->install\n"
"        <local_path>=https://github.com/git-for-windows/git/releases/download/v2.55.0.windows.5/PortableGit-2.55.0.5-64-bit.7z.exe\n"
"    over->install\n"
"    init->env_arg\n"
"        path=<local_path>\n"
"        path=<local_path>/bin\n"
"    over->env_arg\n"
"info->tool\n"
"    platform: x64-win\n"
"    name: pixi\n"
"    version: v0.80.0\n"
"    website: https://github.com/prefix-dev/pixi\n"
"    local_path: {vpkg_tool}/<name>/<version>\n"
"    symbol_excu: <local_path>/pixi.exe\n"
"    init->install\n"
"        <local_path>=https://github.com/prefix-dev/pixi/releases/download/v0.80.0/pixi-x86_64-pc-windows-msvc.zip\n"
"    over->install\n"
"    init->env_arg\n"
"        path=<local_path>\n"
"    over->env_arg\n"
"info->tool\n"
"    platform: x64-win\n"
"    name: cmake\n"
"    version: v4.5.0-rc1\n"
"    website: https://github.com/Kitware/CMake\n"
"    local_path: {vpkg_tool}/<name>/<version>\n"
"    symbol_excu: <local_path>/bin/cmake.exe\n"
"    init->install\n"
"        <local_path>=https://github.com/Kitware/CMake/releases/download/v4.5.0-rc1/cmake-4.5.0-rc1-windows-x86_64.zip\n"
"    over->install\n"
"    init->env_arg\n"
"        path=<local_path>/bin\n"
"    over->env_arg\n"
"info->tool\n"
"    platform: x64-win\n"
"    name: xmake\n"
"    version: v3.1.1\n"
"    website: https://github.com/xmake-io/xmake\n"
"    local_path: {vpkg_tool}/<name>/<version>\n"
"    symbol_excu: <local_path>/xmake.exe\n"
"    init->install\n"
"        <local_path>=https://github.com/xmake-io/xmake/releases/download/v3.1.1/xmake-v3.1.1.win64.zip\n"
"    over->install\n"
"    init->env_arg\n"
"        path=<local_path>\n"
"    over->env_arg\n"
"info->tool\n"
"    platform: x64-win\n"
"    name: vcpkg\n"
"    version: v20261016\n"
"    website: https://github.com/microsoft/vcpkg\n"
"    local_path: {vpkg_tool}/<name>/<version>\n"
"    symbol_excu: <local_path>/vcpkg.exe\n"
"    init->install\n"
"        <local_path>=https://github.com/microsoft/vcpkg/archive/refs/tags/2026.10.16.zip\n"
"        <local_path>=https://github.com/microsoft/vcpkg-tool/releases/download/2026-09-26/vcpkg.exe\n"
"    over->install\n"
"    init->env_arg\n"
"        path=<local_path>\n"
"        vcpkg_root=<local_path>\n"
"        vcpkg_default_triplet=x64-mingw-static\n"
"        vcpkg_default_host_triplet=x64-mingw-static\n"
"        X_VCPKG_ASSET_SOURCES=x-azurl,https://mirrors.tuna.tsinghua.edu.cn/vcpkg/assets/\n"
"        VCPKG_BINARY_SOURCES=clear;x-https,https://mirrors.tuna.tsinghua.edu.cn/vcpkg-ce/cache/,readwrite\n"
"    over->env_arg\n"
"info->tool\n"
"    platform: x64-win\n"
"    name: nodejs\n"
"    version: v26.8.2\n"
"    website: https://nodejs.org\n"
"    local_path: {vpkg_tool}/<name>/<version>\n"
"    symbol_excu: <local_path>/node.exe\n"
"    init->install\n"
"        <local_path>=https://nodejs.org/dist/v26.8.2/node-v26.8.2-win-x64.zip\n"
"    over->install\n"
"    init->env_arg\n"
"        path=<local_path>\n"
"        path=<local_path>/node_modules\n"
"        path=<local_path>/node_pkg\n"
"        npm_config_prefix=<local_path>/npm_pkg\n"
"        npm_config_cache=<local_path>/npm_cache\n"
"    over->env_arg\n"
"info->tool\n"
"    platform: x64-win\n"
"    name: python\n"
"    version: v3.15.2\n"
"    website: https://www.python.org\n"
"    local_path: {vpkg_tool}/<name>/<version>\n"
"    symbol_excu: <local_path>/python.exe\n"
"    init->install\n"
"        <local_path>=https://www.python.org/ftp/python/3.15.2/python-3.15.2-embed-amd64.zip\n"
"        <local_path>=https://bootstrap.pypa.io/get-pip.py\n"
"    over->install\n"
"    init->env_arg\n"
"        path=<local_path>\n"
"        path=<local_path>/Scripts\n"
"    over->env_arg\n"
"info->tool\n"
"    platform: x64-win\n"
"    name: rust\n"
"    version: v1.98.1\n"
"    website: https://rust-lang.org/\n"
"    local_path: {vpkg_tool}/<name>/<version>\n"
"    symbol_excu: <local_path>/rustup-init.exe\n"
"    init->install\n"
"        <local_path>=https://static.rust-lang.org/rustup/dist/x86_64-pc-windows-msvc/rustup-init.exe\n"
"    over->install\n"
"    init->env_arg\n"
"        rustup_home=<local_path>/rustup_home\n"
"        cargo_home=<local_path>/cargo_home\n"
"        path=<local_path>\n"
"        path=<local_path>/cargo_home/bin\n"
"        path=<local_path>/rustup_home\n"
"    over->env_arg\n"
"info->tool\n"
"    platform: x64-win\n"
"    name: java\n"
"    version: v27\n"
"    website: https://www.java.com\n"
"    local_path: {vpkg_tool}/<name>/<version>\n"
"    symbol_excu: <local_path>/bin/java.exe\n"
"    init->install\n"
"        <local_path>=https://download.oracle.com/java/27/latest/jdk-27_windows-x64_bin.zip\n"
"    over->install\n"
"    init->env_arg\n"
"        path=<local_path>/bin\n"
"    over->env_arg\n"
"info->tool\n"
"    platform: x64-win\n"
"    name: golang\n"
"    version: v1.27.3\n"
"    website: https://golang.google.cn/\n"
"    local_path: {vpkg_tool}/<name>/<version>\n"
"    symbol_excu: <local_path>/bin/go.exe\n"
"    init->install\n"
"        <local_path>=https://go.dev/dl/go1.27.3.windows-amd64.zip\n"
"    over->install\n"
"    init->env_arg\n"
"        go_root=<local_path>\n"
"        path=<local_path>\n"
"    over->env_arg\n"
"info->tool\n"
"    platform: x64-win\n"
"    name: zig\n"
"    version: v0.17.1\n"
"    website: https://ziglang.org/\n"
"    local_path: {vpkg_tool}/<name>/<version>\n"
"    symbol_excu: <local_path>/zig.exe\n"
"    init->install\n"
"        <local_path>=https://ziglang.com.cn/download/0.17.1/zig-x86_64-windows-0.17.1.zip\n"
"    over->install\n"
"    init->env_arg\n"
"        path=<local_path>\n"
"    over->env_arg\n"
"info->tool\n"
"    platform: x64-win\n"
"    name: vlang\n"
"    version: v0.5\n"
"    website: https://vlang.io/\n"
"    local_path: {vpkg_tool}/<name>/<version>\n"
"    symbol_excu: <local_path>/v.exe\n"
"    init->install\n"
"        <local_path>=https://github.com/vlang/v/releases/latest/download/v_windows.zip\n"
"    over->install\n"
"    init->env_arg\n"
"        path=<local_path>\n"
"    over->env_arg\n"
"info->tool\n"
"    platform: x64-win\n"
"    name: lua\n"
"    version: v5.5.0\n"
"    website: https://www.lua.org/\n"
"    local_path: {vpkg_tool}/<name>/<version>\n"
"    symbol_excu: <local_path>/lua55.exe\n"
"    init->install\n"
"        <local_path>=https://xget.xi-xu.me/sf/projects/luabinaries/files/5.5.0/Tools%20Executables/lua-5.5.0_Win64_bin.zip\n"
"        <local_path>=https://xget.xi-xu.me/sf/projects/luabinaries/files/5.5.0/Windows%20Libraries/Static/lua-5.5.0_Win64_mingw6_lib.zip\n"
"        <local_path>=https://github.com/luarocks/luarocks/releases/download/v3.12.2/luarocks-3.12.2-windows-64.zip\n"
"    over->install\n"
"    init->env_arg\n"
"        luarocks_config=<local_path>/config.lua\n"
"        path=<local_path>\n"
"    over->env_arg\n"
"info->tool\n"
"    platform: x64-win\n"
"    name: mingw_w64\n"
"    version: v16.2.0\n"
"    website: https://github.com/niXman/mingw-builds-binaries\n"
"    local_path: {vpkg_tool}/<name>/<version>\n"
"    symbol_excu: <local_path>/bin/gcc.exe\n"
"    init->install\n"
"        <local_path>=https://github.com/niXman/mingw-builds-binaries/releases/download/16.2.0-rt_v14-rev1/x86_64-16.2.0-release-posix-seh-ucrt-rt_v14-rev1.7z\n"
"    over->install\n"
"    init->env_arg\n"
"        path=<local_path>/bin\n"
"    over->env_arg\n"
"info->tool\n"
"    platform: x64-win\n"
"    name: llvm_mingw\n"
"    version: v20260908\n"
"    website: https://github.com/mstorsjo/llvm-mingw\n"
"    local_path: {vpkg_tool}/<name>/<version>\n"
"    symbol_excu: <local_path>/bin/gcc.exe\n"
"    init->install\n"
"        <local_path>=https://github.com/mstorsjo/llvm-mingw/releases/download/20260908/llvm-mingw-20260908-ucrt-x86_64.zip\n"
"    over->install\n"
"    init->env_arg\n"
"        path=<local_path>/bin\n"
"    over->env_arg\n"
"info->tool\n"
"    platform: x64-win\n"
"    name: llvm_msvc\n"
"    version: v777.3.1\n"
"    website: https://github.com/aftermathlabs/llvm-msvc\n"
"    local_path: {vpkg_tool}/<name>/<version>\n"
"    symbol_excu: <local_path>/bin/clang-cl.exe\n"
"    init->install\n"
"        <local_path>=https://github.com/aftermathlabs/llvm-msvc/releases/download/llvm-msvc-v777.3.1/windows-wrapper-llvm-msvc-PDB.zip.001\n"
"        <local_path>=https://github.com/aftermathlabs/llvm-msvc/releases/download/llvm-msvc-v777.3.1/windows-wrapper-llvm-msvc-PDB.zip.002\n"
"    over->install\n"
"    init->env_arg\n"
"        path=<local_path>/bin\n"
"    over->env_arg\n"
"info->tool\n"
"    platform: x64-win\n"
"    name: llvm_winlibs\n"
"    version: v16.2.0\n"
"    website: https://github.com/brechtsanders/winlibs_mingw\n"
"    local_path: {vpkg_tool}/<name>/<version>\n"
"    symbol_excu: <local_path>/bin/gcc.exe\n"
"    init->install\n"
"        <local_path>=https://github.com/brechtsanders/winlibs_mingw/releases/download/16.2.0posix-23.1.3-14.0.0-ucrt-r3/winlibs-x86_64-posix-seh-gcc-16.2.0-llvm-23.1.3-mingw-w64ucrt-14.0.0-r3.7z\n"
"    over->install\n"
"    init->env_arg\n"
"        path=<local_path>/bin\n"
"    over->env_arg\n"
"info->tool\n"
"    platform: x64-win\n"
"    name: mingw_winlibs\n"
"    version: v16.2.0\n"
"    website: https://github.com/brechtsanders/winlibs_mingw\n"
"    local_path: {vpkg_tool}/<name>/<version>\n"
"    symbol_excu: <local_path>/bin/gcc.exe\n"
"    init->install\n"
"        <local_path>=https://github.com/brechtsanders/winlibs_mingw/releases/download/16.2.0posix-23.1.3-14.0.0-ucrt-r3/winlibs-x86_64-posix-seh-gcc-16.2.0-mingw-w64ucrt-14.0.0-r3.7z\n"
"    over->install\n"
"    init->env_arg\n"
"        path=<local_path>/bin\n"
"    over->env_arg\n"
"info->tool\n"
"    platform: x64-win\n"
"    name: llvm_qt\n"
"    version: v6.11.2\n"
"    website: https://github.com/yuanpeirong/buildQt\n"
"    local_path: {vpkg_tool}/<name>/<version>\n"
"    symbol_excu: <local_path>/bin/qmake.exe\n"
"    init->install\n"
"        <local_path>=https://github.com/yuanpeirong/buildQt/releases/download/Qt6.11.2_rev0/Qt_6.11.2-static-Release_llvm-mingw22.1.8_64_UCRT.7z\n"
"    over->install\n"
"    init->env_arg\n"
"        path=<local_path>/bin\n"
"    over->env_arg\n"
"info->tool\n"
"    platform: x64-win\n"
"    name: mingw_qt\n"
"    version: v6.11.2\n"
"    website: https://github.com/yuanpeirong/buildQt\n"
"    local_path: {vpkg_tool}/<name>/<version>\n"
"    symbol_excu: <local_path>/bin/qmake.exe\n"
"    init->install\n"
"        <local_path>=https://github.com/yuanpeirong/buildQt/releases/download/Qt6.11.2_rev0/Qt_6.11.2-static-Release_mingw1620_64_UCRT.7z\n"
"    over->install\n"
"    init->env_arg\n"
"        path=<local_path>/bin\n"
"    over->env_arg\n"
"info->tool\n"
"    platform: x64-win\n"
"    name: msvc_qt\n"
"    version: v6.11.2\n"
"    website: https://github.com/yuanpeirong/buildQt\n"
"    local_path: {vpkg_tool}/<name>/<version>\n"
"    symbol_excu: <local_path>/bin/qmake.exe\n"
"    init->install\n"
"        <local_path>=https://github.com/yuanpeirong/buildQt/releases/download/Qt6.11.2_rev0/Qt_6.11.2-static-Release_msvc2026_64.7z\n"
"    over->install\n"
"    init->env_arg\n"
"        path=<local_path>/bin\n"
"    over->env_arg\n"
"info->tool\n"
"    platform: x64-win\n"
"    name: motrix\n"
"    version: v2.2.1\n"
"    website: https://motrix.app/zh/\n"
"    local_path: {vpkg_tool}/<name>/<version>\n"
"    symbol_excu: <local_path>/Motrix.exe\n"
"    init->install\n"
"        <local_path>=https://dl.motrix.app/releases/Motrix-2.2.1-win.zip\n"
"    over->install\n"
"    init->env_arg\n"
"        path=<local_path>\n"
"    over->env_arg\n"
"info->tool\n"
"    platform: x64-win\n"
"    name: ScreenCapture\n"
"    version: v2.5.15\n"
"    website: https://github.com/xland/ScreenCapture\n"
"    local_path: {vpkg_tool}/<name>/<version>\n"
"    symbol_excu: <local_path>/ScreenCapture.exe\n"
"    init->install\n"
"        <local_path>=https://github.com/xland/ScreenCapture/releases/download/2.5.15/ScreenCapture.exe\n"
"    over->install\n"
"    init->env_arg\n"
"        path=<local_path>\n"
"    over->env_arg\n"
"info->tool\n"
"    platform: x64-win\n"
"    name: sharex\n"
"    version: v22.1.0\n"
"    website: https://github.com/ShareX/ShareX\n"
"    local_path: {vpkg_tool}/<name>/<version>\n"
"    symbol_excu: <local_path>/ShareX.exe\n"
"    init->install\n"
"        <local_path>=https://github.com/ShareX/ShareX/releases/download/v22.1.0/ShareX-22.1.0-portable-x64.zip\n"
"    over->install\n"
"    init->env_arg\n"
"        path=<local_path>\n"
"    over->env_arg\n"
"info->tool\n"
"    platform: x64-win\n"
"    name: FlClash\n"
"    version: v0.9.2\n"
"    website: https://github.com/chen08209/FlClash\n"
"    local_path: {vpkg_tool}/<name>/<version>\n"
"    symbol_excu: <local_path>/FlClash.exe\n"
"    init->install\n"
"        <local_path>=https://github.com/chen08209/FlClash/releases/download/v0.9.2/FlClash-0.9.2-windows-amd64.zip\n"
"    over->install\n"
"    init->env_arg\n"
"        path=<local_path>\n"
"    over->env_arg\n"
"info->tool\n"
"    platform: x64-win\n"
"    name: v2rayN\n"
"    version: v7.25.6\n"
"    website: https://github.com/2dust/v2rayN\n"
"    local_path: {vpkg_tool}/<name>/<version>\n"
"    symbol_excu: <local_path>/v2rayN.exe\n"
"    init->install\n"
"        <local_path>=https://github.com/2dust/v2rayN/releases/download/7.25.6/v2rayN-windows-64.zip\n"
"    over->install\n"
"    init->env_arg\n"
"        path=<local_path>\n"
"    over->env_arg\n"
"info->script\n"
"    platform: x64-win\n"
"    name: unproxy.bat\n"
"    version: 1.0\n"
"    website: void\n"
"    local_path: {vpkg_script}\n"
"    init->content\n"
"        @echo off\n"
"        set http_proxy=\n"
"        set https_proxy=\n"
"        echo info-}remove the proxy\n"
"    over->content\n"
"info->script\n"
"    platform: x64-win\n"
"    name: proxy_clash.bat\n"
"    version: v1.0\n"
"    website: void\n"
"    local_path: {vpkg_script}\n"
"    init->content\n"
"        @echo off\n"
"        set http_proxy=127.0.0.1:7890\n"
"        set https_proxy=127.0.0.1:7890\n"
"        echo info-}set the proxy to http://127.0.0.1:7890\n"
"    over->content\n"
"info->script\n"
"    platform: x64-win\n"
"    name: proxy_v2ray.bat\n"
"    version: v1.0\n"
"    website: void\n"
"    local_path: {vpkg_script}\n"
"    init->content\n"
"        @echo off\n"
"        set http_proxy=127.0.0.1:7880\n"
"        set https_proxy=127.0.0.1:7880\n"
"        echo info-}set the proxy to http://127.0.0.1:7880\n"
"    over->content\n";
}

/* ============================================================
 * extra_config
 * ============================================================ */
static char *_resolve_placeholders(const char *text, const char *platform, const char *name,
                                   const char *version, const char *local_path) {
    if (!text) return NULL;
    char *cur = xstrdup(text);
    const char *ks[] = {"{vpkg_root}","{vpkg_system}","{vpkg_tool}","{vpkg_script}","{vpkg_cache}",
                        "<platform>","<name>","<version>","<website>","<local_path>","<symbol_excu>"};
    const char *vs[] = {
        _getstr(vpkg_root_tree, "root_vpkg"), _getstr(vpkg_root_tree, "root_system"),
        _getstr(vpkg_root_tree, "root_tool"), _getstr(vpkg_root_tree, "root_script"),
        _getstr(vpkg_root_tree, "root_cache"),
        platform, name, version, version, local_path, local_path
    };
    for (int i = 0; i < 11; i++) { char *n = str_replace_all(cur, ks[i], vs[i]); free(cur); cur = n; }
    return cur;
}
static void _syntax_panic(const char *head, str_list *block) {
    const char *seg = strstr(head, "->");
    log_erro(xfmt("erro->func:<extra_config>...config file “%s” syntax panic!!!", seg ? seg + 2 : head));
    log_erro("...source config_file part as follow...");
    { size_t total = 1; str_node *n = block->head;
      while (n) { total += strlen(n->value) + 1; n = n->next; }
      char *buf = (char *)calloc(1, total);
      n = block->head;
      while (n) { if (n != block->head) strcat(buf, "\n"); strcat(buf, n->value); n = n->next; }
      log_warn(buf); free(buf); }
    log_erro("...source config_file part over...");
}
/* value 前后都 trim, 去掉 '    platform: x64-win' 中 ':' 后的前导空格 */
static char *_extract_value(const char *line, const char *prefix) {
    const char *val = line + strlen(prefix);
    const char *e = val + strlen(val);
    while (e > val && isspace((unsigned char)e[-1])) e--;
    while (val < e && isspace((unsigned char)*val)) val++;
    size_t len = (size_t)(e - val);
    char *trimmed = (char *)malloc(len + 1);
    memcpy(trimmed, val, len); trimmed[len] = 0;
    return trimmed;
}
static int _parse_sftw_block(str_list *block) {
    const char *expected[] = {"platform","name","version","website","autor","publish","description","proxy"};
    if (str_list_size(block) < 9) { _syntax_panic(str_list_get(block, 0), block); return 0; }
    kv_map *kv = kv_map_new();
    for (int i = 0; i < 8; i++) {
        char *prefix = xfmt("    %s:", expected[i]);
        const char *line = str_list_get(block, (size_t)i + 1);
        if (!line || strncmp(line, prefix, strlen(prefix)) != 0) {
            free(prefix); kv_map_free(kv);
            _syntax_panic(str_list_get(block, 0), block);
            return 0;
        }
        char *trimmed = _extract_value(line, prefix);
        _setstr(kv, expected[i], trimmed);
        free(trimmed); free(prefix);
    }
    for (str_node *kn = vpkg_info_kwOrder->head; kn; kn = kn->next) {
        const char *key = kn->value;
        const char *value = _getstr(kv, key);
        if (!strcmp(key, "proxy")) {
            int b = (!strcmp(value,"True") || !strcmp(value,"true") || !strcmp(value,"T") ||
                     !strcmp(value,"t")    || !strcmp(value,"1"));
            _setbool(vpkg_info, key, b);
            continue;
        }
        _setstr(vpkg_info, key, value);
    }
    kv_map_free(kv);
    return 1;
}
static int _parse_tool_block(str_list *block) {
    const char *pre[] = {"platform","name","version","website","local_path","symbol_excu"};
    if (str_list_size(block) < 9) { _syntax_panic(str_list_get(block, 0), block); return 0; }
    kv_map *common = kv_map_new();
    for (int i = 0; i < 6; i++) {
        char *prefix = xfmt("    %s:", pre[i]);
        const char *line = str_list_get(block, (size_t)i + 1);
        if (!line || strncmp(line, prefix, strlen(prefix)) != 0) {
            free(prefix); kv_map_free(common);
            _syntax_panic(str_list_get(block, 0), block);
            return 0;
        }
        char *trimmed = _extract_value(line, prefix);
        _setstr(common, pre[i], trimmed);
        free(trimmed); free(prefix);
    }
    kv_map *install = kv_map_new(), *env_arg = kv_map_new();
    const char *state = NULL;
    for (size_t i = 7; i < str_list_size(block); i++) {
        const char *line = str_list_get(block, i);
        const char *s = line;
        while (*s && isspace((unsigned char)*s)) s++;
        size_t elen = strlen(s);
        while (elen && isspace((unsigned char)s[elen-1])) elen--;
        if (elen == 13 && !strncmp(s, "init->install", 13)) { state = "install"; continue; }
        if (elen == 13 && !strncmp(s, "over->install", 13)) { state = NULL; continue; }
        if (elen == 13 && !strncmp(s, "init->env_arg", 13)) { state = "env_arg"; continue; }
        if (elen == 13 && !strncmp(s, "over->env_arg", 13)) { state = NULL; continue; }
        if (elen == 0) continue;
        if (state) {
            const char *eq = memchr(s, '=', elen);
            if (!eq) { kv_map_free(common); kv_map_free(install); kv_map_free(env_arg); _syntax_panic(str_list_get(block, 0), block); return 0; }
            size_t klen = (size_t)(eq - s);
            while (klen && isspace((unsigned char)s[klen-1])) klen--;
            char *k = (char *)malloc(klen + 1); memcpy(k, s, klen); k[klen] = 0;
            const char *vs = eq + 1;
            while (*vs && isspace((unsigned char)*vs)) vs++;
            const char *ve = vs + strlen(vs);
            while (ve > vs && isspace((unsigned char)ve[-1])) ve--;
            size_t vlen = (size_t)(ve - vs);
            char *v = (char *)malloc(vlen + 1); memcpy(v, vs, vlen); v[vlen] = 0;
            kv_map *target = (!strcmp(state, "install")) ? install : env_arg;
            str_list *lst = _getlist(target, k);
            if (!lst) { lst = str_list_new(); _setlist(target, k, lst); }
            str_list_add(lst, v, NULL);
            free(k); free(v);
        }
    }
    const char *platform = _getstr(common, "platform");
    const char *tool_name = _getstr(common, "name");
    if (strcmp(platform, _getstr(vpkg_info, "platform")) != 0) {
        log_info(xfmt("info->“%s”...“%s”...not match system platform...“%s”!!!",
                      tool_name, platform, _getstr(vpkg_info, "platform")));
        kv_map_free(common); kv_map_free(install); kv_map_free(env_arg);
        return 0;
    }
    kv_map *entry = kv_map_new();
    _setstr(entry, "platform", platform);
    _setstr(entry, "name", tool_name);
    _setstr(entry, "version", _getstr(common, "version"));
    _setstr(entry, "website", _getstr(common, "website"));
    _setstr(entry, "local_path", _getstr(common, "local_path"));
    _setstr(entry, "symbol_excu", _getstr(common, "symbol_excu"));
    _setdict(entry, "install", install);
    _setdict(entry, "env_arg", env_arg);
    _setbool(entry, "install_statu", 0);
    kv_map *tools = _getdict(vpkg_sftw, "tool");
    kv_map_remove(tools, tool_name);
    { value v; v.type = VAL_DICT; v.as.dict_val = entry; kv_map_add(tools, tool_name, &v); }
    kv_map_free(common);
    return 1;
}
static int _parse_script_block(str_list *block) {
    const char *pre[] = {"platform","name","version","website","local_path"};
    if (str_list_size(block) < 7) { _syntax_panic(str_list_get(block, 0), block); return 0; }
    kv_map *common = kv_map_new();
    for (int i = 0; i < 5; i++) {
        char *prefix = xfmt("    %s:", pre[i]);
        const char *line = str_list_get(block, (size_t)i + 1);
        if (!line || strncmp(line, prefix, strlen(prefix)) != 0) {
            free(prefix); kv_map_free(common);
            _syntax_panic(str_list_get(block, 0), block);
            return 0;
        }
        char *trimmed = _extract_value(line, prefix);
        _setstr(common, pre[i], trimmed);
        free(trimmed); free(prefix);
    }
    str_list *content_lines = str_list_new();
    int in_content = 0;
    for (size_t i = 6; i < str_list_size(block); i++) {
        const char *line = str_list_get(block, i);
        const char *s = line; while (*s && isspace((unsigned char)*s)) s++;
        size_t elen = strlen(s);
        while (elen && isspace((unsigned char)s[elen-1])) elen--;
        if (elen == 13 && !strncmp(s, "init->content", 13)) { in_content = 1; continue; }
        if (elen == 13 && !strncmp(s, "over->content", 13)) { in_content = 0; continue; }
        if (in_content) {
            size_t L = strlen(line);
            str_list_add(content_lines, L >= 8 ? line + 8 : line, NULL);
        }
    }
    const char *platform = _getstr(common, "platform");
    const char *script_name = _getstr(common, "name");
    if (strcmp(platform, _getstr(vpkg_info, "platform")) != 0) {
        log_info(xfmt("info->“%s”...“%s”...not match system platform...“%s”!!!",
                      script_name, platform, _getstr(vpkg_info, "platform")));
        kv_map_free(common); str_list_free(content_lines);
        return 0;
    }
    size_t total = 1;
    for (str_node *n = content_lines->head; n; n = n->next) total += strlen(n->value) + 1;
    char *content = (char *)calloc(1, total);
    for (str_node *n = content_lines->head; n; n = n->next) {
        if (!n->value[0]) continue;
        strcat(content, n->value); strcat(content, "\n");
    }
    kv_map *entry = kv_map_new();
    _setstr(entry, "platform", platform);
    _setstr(entry, "name", script_name);
    _setstr(entry, "version", _getstr(common, "version"));
    _setstr(entry, "website", _getstr(common, "website"));
    _setstr(entry, "local_path", _getstr(common, "local_path"));
    _setstr(entry, "content", content);
    _setbool(entry, "install_statu", 0);
    kv_map *scripts = _getdict(vpkg_sftw, "script");
    kv_map_remove(scripts, script_name);
    { value v; v.type = VAL_DICT; v.as.dict_val = entry; kv_map_add(scripts, script_name, &v); }
    free(content); kv_map_free(common); str_list_free(content_lines);
    return 1;
}
static void _item_match(const char *config_text) {
    if (!config_text) return;
    char *raw = xstrdup(config_text);
    char *p = raw;
    while (*p) {
        char *eol = p;
        while (*eol && *eol != '\n' && *eol != '\r') eol++;
        for (char *q = p; q < eol; q++) if (*q == '#') { *q = 0; eol = q; break; }
        p = eol;
        while (*p == '\n' || *p == '\r') p++;
    }
    str_list *lines = str_list_new();
    char *line = raw;
    while (*line) {
        char *eol = strchr(line, '\n');
        if (eol) *eol = 0;
        size_t L = strlen(line);
        if (L && line[L-1] == '\r') line[L-1] = 0;
        int blank = 1;
        for (char *q = line; *q; q++) if (!isspace((unsigned char)*q)) { blank = 0; break; }
        if (!blank) str_list_add(lines, line, NULL);
        if (!eol) break;
        line = eol + 1;
    }
    free(raw);
    int *split_idx = (int *)malloc(sizeof(int) * (str_list_size(lines) + 1));
    int cnt = 0;
    for (size_t i = 0; i < str_list_size(lines); i++)
        if (str_list_find(vpkg_config_symbol, str_list_get(lines, i))) split_idx[cnt++] = (int)i;
    split_idx[cnt++] = (int)str_list_size(lines);
    for (int b = 0; b < cnt - 1; b++) {
        size_t s = (size_t)split_idx[b], e = (size_t)split_idx[b+1];
        if (s >= e) continue;
        const char *head = str_list_get(lines, s);
        str_list *block = str_list_new();
        for (size_t i = s; i < e; i++) str_list_add(block, str_list_get(lines, i), NULL);
        if (!strcmp(head, "info->sftw") || !strcmp(head, "info=>sftw")) _parse_sftw_block(block);
        else if (!strcmp(head, "info->tool") || !strcmp(head, "info=>tool")) _parse_tool_block(block);
        else if (!strcmp(head, "info->script") || !strcmp(head, "info=>script")) _parse_script_block(block);
        str_list_free(block);
    }
    free(split_idx); str_list_free(lines);
}
static void _item_extra(void) {
    for (kv_node *n = vpkg_root_tree->head; n; n = n->next) {
        char *a = str_replace_all(n->val.as.str, "{vpkg_root}", vpkg_root);
        char *b = str_replace_all(a, "{platform}", _getstr(vpkg_info, "platform"));
        free(a);
        _clean_val(&n->val); n->val.type = VAL_STR; n->val.as.str = b;
        if (!path_exists(b)) { mkdir_single(b); log_warn(xfmt("info->creat dir...>%s<", b)); }
    }
    kv_map *tools = _getdict(vpkg_sftw, "tool");
    for (kv_node *n = tools->head; n; n = n->next) {
        kv_map *t = n->val.as.dict_val;
        const char *platform = _getstr(t, "platform");
        const char *name = _getstr(t, "name");
        const char *version = _getstr(t, "version");
        const char *old_lp = _getstr(t, "local_path");
        char *new_lp = _resolve_placeholders(old_lp, platform, name, version, old_lp);
        char *new_sym = _resolve_placeholders(_getstr(t, "symbol_excu"), platform, name, version, new_lp);
        kv_map *inst_old = _getdict(t, "install");
        kv_map *env_old = _getdict(t, "env_arg");
        kv_map *inst_new = kv_map_new();
        kv_map *env_new = kv_map_new();
        if (inst_old) for (kv_node *m = inst_old->head; m; m = m->next) {
            char *nk = _resolve_placeholders(m->key, platform, name, version, new_lp);
            str_list *lst = str_list_new();
            str_list *old = m->val.as.list_val;
            for (str_node *v = old ? old->head : NULL; v; v = v->next) {
                char *nv = _resolve_placeholders(v->value, platform, name, version, new_lp);
                str_list_add(lst, nv, NULL); free(nv);
            }
            _setlist(inst_new, nk, lst); free(nk);
        }
        if (env_old) for (kv_node *m = env_old->head; m; m = m->next) {
            char *nk = _resolve_placeholders(m->key, platform, name, version, new_lp);
            str_list *lst = str_list_new();
            str_list *old = m->val.as.list_val;
            for (str_node *v = old ? old->head : NULL; v; v = v->next) {
                char *nv = _resolve_placeholders(v->value, platform, name, version, new_lp);
                str_list_add(lst, nv, NULL); free(nv);
            }
            _setlist(env_new, nk, lst); free(nk);
        }
        _setstr(t, "local_path", new_lp);
        _setstr(t, "symbol_excu", new_sym);
        _setdict(t, "install", inst_new);
        _setdict(t, "env_arg", env_new);
        free(new_lp); free(new_sym);
    }
    kv_map *scripts = _getdict(vpkg_sftw, "script");
    for (kv_node *n = scripts->head; n; n = n->next) {
        kv_map *s = n->val.as.dict_val;
        char *new_lp = xstrdup(_getstr(s, "local_path"));
        const char *keys[] = {"{vpkg_root}","{vpkg_system}","{vpkg_tool}","{vpkg_script}","{vpkg_cache}",
                              "<platform>","<name>","<version>"};
        const char *rks[] = {"root_vpkg","root_system","root_tool","root_script","root_cache"};
        const char *platform = _getstr(s, "platform");
        for (int i = 0; i < 5; i++) {
            char *nx = str_replace_all(new_lp, keys[i], _getstr(vpkg_root_tree, rks[i]));
            free(new_lp); new_lp = nx;
        }
        for (int i = 5; i < 8; i++) { char *nx = str_replace_all(new_lp, keys[i], platform); free(new_lp); new_lp = nx; }
        _setstr(s, "local_path", new_lp);
        free(new_lp);
    }
    for (kv_node *n = tools->head; n; n = n->next) {
        kv_map *t = n->val.as.dict_val;
        _setbool(t, "install_statu", path_exists(_getstr(t, "symbol_excu")));
    }
}
typedef struct { kv_map *scripts; } _walk_add_ud;
static void _walk_add_script(const char *path, const char *basename, void *ud) {
    _walk_add_ud *u = (_walk_add_ud *)ud;
    char *fname = xstrdup(basename);
    char *dot = strrchr(fname, '.');
    if (dot) *dot = 0;
    char *content = read_whole(path);
    if (content) {
        kv_map *s = kv_map_new();
        _setstr(s, "platform", "x64-win");
        _setstr(s, "name", basename);
        _setstr(s, "version", "void");
        _setstr(s, "website", "void");
        _setstr(s, "local_path", _getstr(vpkg_root_tree, "root_script"));
        _setstr(s, "content", content);
        _setbool(s, "install_statu", 1);
        kv_map_remove(u->scripts, fname);
        { value v; v.type = VAL_DICT; v.as.dict_val = s; kv_map_add(u->scripts, fname, &v); }
        free(content);
    }
    free(fname);
}
static void _item_check(void) {
    const char *platform = _getstr(vpkg_info, "platform");
    const char *kinds[] = {"tool", "script"};
    for (int k = 0; k < 2; k++) {
        kv_map *m = _getdict(vpkg_sftw, kinds[k]);
        str_list *del = str_list_new();
        for (kv_node *n = m->head; n; n = n->next) {
            if (strcmp(_getstr(n->val.as.dict_val, "platform"), platform) != 0) str_list_add(del, n->key, NULL);
        }
        for (str_node *d = del->head; d; d = d->next) kv_map_remove(m, d->value);
        str_list_free(del);
    }
    kv_map *tools = _getdict(vpkg_sftw, "tool");
    kv_map *scripts = _getdict(vpkg_sftw, "script");
    for (kv_node *n = tools->head; n; n = n->next)
        _setbool(n->val.as.dict_val, "install_statu", path_exists(_getstr(n->val.as.dict_val, "symbol_excu")));
    for (kv_node *n = scripts->head; n; n = n->next) {
        kv_map *s = n->val.as.dict_val;
        char *path = path_join(_getstr(s, "local_path"), _getstr(s, "name"));
        _setbool(s, "install_statu", path_exists(path));
        free(path);
    }
    _walk_add_ud ud = { scripts };
    walk_dir(_getstr(vpkg_root_tree, "root_script"), _walk_add_script, &ud);
    /* 安全: 只清理"不在软件库中"的目录, 避免 install_statu 判断异常误删已装软件 */
    str_list *exist_tool = str_list_new();
    for (kv_node *n = tools->head; n; n = n->next) str_list_add(exist_tool, n->key, NULL);
    str_list *entries = str_list_new();
    scandir_paths(_getstr(vpkg_root_tree, "root_tool"), NULL, entries);
    for (str_node *n = entries->head; n; n = n->next) {
        char *base = path_base(n->value);
        if (!str_list_find(exist_tool, base)) {
            rmtree_rec(n->value);
            log_warn(xfmt("warn->tool_dir: del the illegal dir...>%s<", base));
        }
        free(base);
    }
    str_list_free(entries); str_list_free(exist_tool);
}
static void _install_script_all(void) {
    kv_map *scripts = _getdict(vpkg_sftw, "script");
    for (kv_node *n = scripts->head; n; n = n->next) {
        kv_map *s = n->val.as.dict_val;
        char *path = path_join(_getstr(s, "local_path"), _getstr(s, "name"));
        if (!_getbool(s, "install_statu")) {
            write_whole(path, _getstr(s, "content"));
            log_info(xfmt("info->func:extra_config._install_script, install script...>%s<", path));
        }
        free(path);
    }
}
static void extra_config(void) {
    char *user_text = NULL;
    if (path_exists(vpkg_config_file)) user_text = read_whole(vpkg_config_file);
    char *merged = user_text
        ? xfmt("%s\n%s", vpkg_config_default, user_text)
        : xstrdup(vpkg_config_default);
    free(user_text);
    _item_match(merged);
    free(merged);
    _item_extra();
    _item_check();
    _install_script_all();
}

/* ============================================================
 * extra_command
 * ============================================================ */
static int _check_basic_sftw_statu(void) {
    int ok = 1;
    kv_map *tools = _getdict(vpkg_sftw, "tool");
    for (str_node *n = vpkg_sftw_tool_basic->head; n; n = n->next) {
        kv_map *t = _getdict(tools, n->value);
        if (!t || !_getbool(t, "install_statu")) { ok = 0; log_erro(xfmt("erro->lack of basic sftw...>%s<", n->value)); }
    }
    return ok;
}
static void _clean_dir(const char *aim_path) {
    if (!path_exists(aim_path)) {
        log_warn(xfmt("warn->not exists the dir...>%s<", aim_path));
        return;
    }
    rmtree_rec(aim_path);
    mkdir_single(aim_path);
    log_warn(xfmt("warn->clean the dir...>%s<", aim_path));
}
static int _system_run_cmd(const char *cmd) {
    int rc = system(cmd);
    if (rc != 0) log_erro(xfmt("erro->_system_run_cmd...%s", cmd));
    return rc == 0;
}
static int _file_download(const char *file_url, const char *out_dir) {
    char *real = xstrdup(file_url);
    if (_getbool(vpkg_info, "proxy")) {
        for (kv_node *n = vpkg_download_proxy->head; n; n = n->next) {
            if (strstr(real, n->key)) {
                char *nx = str_replace_all(real, n->key, n->val.as.str);
                free(real); real = nx;
            }
        }
    }
    kv_map *tools = _getdict(vpkg_sftw, "tool");
    kv_map *aria2 = _getdict(tools, "aria2");
    kv_map *wget = _getdict(tools, "wget");
    int aria2_statu = aria2 ? _getbool(aria2, "install_statu") : 0;
    const char *aria2_excu = aria2 ? _getstr(aria2, "symbol_excu") : "";
    int wget_statu = wget ? _getbool(wget, "install_statu") : 0;
    const char *wget_excu = wget ? _getstr(wget, "symbol_excu") : "";
    char *cmd;
    if (aria2_statu || !wget_statu) {
        cmd = xfmt("\"%s\" \"%s\" --dir=\"%s\" --allow-overwrite=true --max-connection-per-server=16 --min-split-size=1M",
                   aria2_excu, real, out_dir);
    } else {
        cmd = xfmt("\"%s\" -P \"%s\" \"%s\"", wget_excu, out_dir, real);
    }
    log_info(xfmt("info->running command...\n\t%s", cmd));
    int rc = system(cmd);
    if (rc != 0) log_erro(xfmt("erro->download failed (code=%d): %s", rc, file_url));
    free(cmd); free(real);
    return rc == 0;
}
static int _file_unzip(const char *file_path, const char *out_dir) {
    kv_map *tools = _getdict(vpkg_sftw, "tool");
    kv_map *a7z = _getdict(tools, "a7z");
    const char *exe = a7z ? _getstr(a7z, "symbol_excu") : "";
    char *cmd = xfmt("\"%s\" x \"%s\" -o\"%s\" -y", exe, file_path, out_dir);
    log_info(xfmt("info->running command...\n\t%s", cmd));
    int rc = system(cmd);
    if (rc != 0) log_erro(xfmt("erro->unzip failed (code=%d): %s", rc, file_path));
    free(cmd);
    return rc == 0;
}
static void _cmd_help(void) {
    log_warn("info->vpkg sftw info start!!!");
    for (kv_node *n = vpkg_info->head; n; n = n->next) {
        if (n->val.type == VAL_STR)  log_info(xfmt("\t%-12s->\t%s", n->key, n->val.as.str));
        else if (n->val.type == VAL_BOOL) log_info(xfmt("\t%-12s->\t%s", n->key, n->val.as.bool_val ? "True" : "False"));
    }
    log_warn("info->vpkg usage...>vpkg \\[command] \\[argument]<");
    for (str_node *n = vpkg_cmd->head; n; n = n->next)
        log_info(xfmt("\tsupport command: %s", n->value));
    log_warn("info->vpkg sftw info end!!!");
}
static void _cmd_list(void) {
    log_warn("info->list software install status!!!");
    log_info(xfmt("\t%-15s->%-15s->%-10s", "name", "install_status", "website"));
    kv_map *tools = _getdict(vpkg_sftw, "tool");
    for (kv_node *n = tools->head; n; n = n->next) {
        kv_map *t = n->val.as.dict_val;
        const char *nm = _getstr(t, "name");
        const char *web = _getstr(t, "website");
        int st = _getbool(t, "install_statu");
        if (st) log_info(xfmt("\t%-15s->%-15s->%-10s", nm, "True", web));
        else    log_erro(xfmt("\t%-15s->%-15s->%-10s", nm, "False", web));
    }
}
/* 修复: env_path 用副本, 防止 _putenv_s 后指针悬空 */
static void _cmd_shell(void) {
#ifdef _WIN32
    const char *orig_path = getenv("PATH");
    char *env_path = xstrdup(orig_path ? orig_path : "");
    kv_map *tools = _getdict(vpkg_sftw, "tool");
    for (kv_node *n = tools->head; n; n = n->next) {
        kv_map *t = n->val.as.dict_val;
        if (!_getbool(t, "install_statu")) continue;
        kv_map *em = _getdict(t, "env_arg");
        if (!em) continue;
        for (kv_node *m = em->head; m; m = m->next) {
            str_list *lst = m->val.as.list_val;
            size_t total = 1;
            for (str_node *s = lst ? lst->head : NULL; s; s = s->next) total += strlen(s->value) + 1;
            char *buf = (char *)calloc(1, total);
            int first = 1;
            for (str_node *s = lst ? lst->head : NULL; s; s = s->next) {
                if (!first) strcat(buf, ";");
                strcat(buf, s->value); first = 0;
            }
            const char *old = getenv(m->key);
            char *combined = (old && *old) ? xfmt("%s;%s", old, buf) : xstrdup(buf);
            _putenv_s(m->key, combined);
            free(combined); free(buf);
        }
    }
    {
        const char *script_dir = _getstr(vpkg_root_tree, "root_script");
        char *newpath = xfmt("%s;%s", env_path, script_dir);
        _putenv_s("PATH", newpath);
        free(newpath);
    }
    free(env_path);
    system("title vpkg && cmd /k \"prompt (vpkg) $P$G\"");
    exit(0);
#endif
}
static void _get_file_and_dir(const char *aim_path, str_list *out_files, str_list *out_dirs) {
    scandir_paths(aim_path, out_files, out_dirs);
}
static str_list *_get_differ_item(str_list *a, str_list *b) {
    str_list *r = str_list_new();
    for (str_node *n = b ? b->head : NULL; n; n = n->next)
        if (!a || !str_list_find(a, n->value)) str_list_add(r, n->value, NULL);
    return r;
}
static char *_get_stop_dir(const char *aim_path) {
    char *cur = xstrdup(aim_path);
    while (1) {
        str_list *files = str_list_new(), *dirs = str_list_new();
        scandir_paths(cur, files, dirs);
        size_t nf = 0, nd = 0;
        const char *first_dir = NULL;
        for (str_node *n = files->head; n; n = n->next) {
            char *b = path_base(n->value); if (b[0] != '.') nf++; free(b);
        }
        for (str_node *n = dirs->head; n; n = n->next) {
            char *b = path_base(n->value);
            if (b[0] != '.') { nd++; if (!first_dir) first_dir = n->value; }
            free(b);
        }
        char *next = (nf + nd == 1 && nd == 1 && first_dir) ? xstrdup(first_dir) : NULL;
        str_list_free(files); str_list_free(dirs);
        if (!next) return cur;
        free(cur); cur = next;
    }
}
static void _cmd_install_install_script(const char *script_name) {
    kv_map *scripts = _getdict(vpkg_sftw, "script");
    kv_map *s = _getdict(scripts, script_name);
    if (!s) { log_erro(xfmt("erro->not exist script config...>%s<", script_name)); return; }
    char *path = path_join(_getstr(s, "local_path"), _getstr(s, "name"));
    write_whole(path, _getstr(s, "content"));
    free(path);
}
/* 修复: 返回 int, 让 _cmd_install 感知失败 */
static int _install_sftw(const char *tool_name) {
    kv_map *tools = _getdict(vpkg_sftw, "tool");
    kv_map *t = _getdict(tools, tool_name);
    if (!t) return 0;
    const char *cache_dir = _getstr(vpkg_root_tree, "root_cache");
    const char *extra_dir = _getstr(vpkg_root_tree, "root_extra");
    _clean_dir(cache_dir);
    if (!path_exists(extra_dir)) mkdirs(extra_dir);
    str_list *cache_init_files = str_list_new(), *dummy = str_list_new();
    _get_file_and_dir(cache_dir, cache_init_files, dummy);
    str_list_free(dummy);
    kv_map *install = _getdict(t, "install");
    for (kv_node *item = install->head; item; item = item->next) {
        const char *install_dir = item->key;
        str_list *urls = item->val.as.list_val;
        mkdirs(install_dir);
        _clean_dir(install_dir);
        for (str_node *u = urls ? urls->head : NULL; u; u = u->next) {
            if (!_file_download(u->value, cache_dir)) {
                log_erro(xfmt("erro->abort install %s, download failed", tool_name));
                str_list_free(cache_init_files);
                return 0;
            }
        }
        str_list *cache_over_files = str_list_new(), *dd = str_list_new();
        _get_file_and_dir(cache_dir, cache_over_files, dd);
        str_list_free(dd);
        str_list *diff = _get_differ_item(cache_init_files, cache_over_files);
        str_list *pack_file = str_list_new(), *move_file = str_list_new();
        str_list *default_ext = _getlist(vpkg_zip_ext, "default");
        for (str_node *n = diff->head; n; n = n->next) {
            char *base = path_base(n->value);
            int ispack = 0;
            for (str_node *e = default_ext ? default_ext->head : NULL; e; e = e->next) {
                size_t L = strlen(base), E = strlen(e->value);
                if (L >= E && !strcmp(base + L - E, e->value)) { ispack = 1; break; }
            }
            if (ispack) str_list_add(pack_file, n->value, NULL);
            else        str_list_add(move_file, n->value, NULL);
            free(base);
        }
        for (str_node *n = pack_file->head; n; n = n->next) {
            _clean_dir(extra_dir);
            if (!_file_unzip(n->value, extra_dir)) {
                log_erro(xfmt("erro->abort install %s, unzip failed", tool_name));
                str_list_free(cache_init_files); str_list_free(cache_over_files);
                str_list_free(diff); str_list_free(pack_file); str_list_free(move_file);
                return 0;
            }
            char *stop = _get_stop_dir(extra_dir);
            copy_tree(stop, install_dir);
            free(stop);
        }
        for (str_node *n = move_file->head; n; n = n->next) {
            char *base = path_base(n->value);
            char *dest = path_join(install_dir, base);
            if (path_exists(dest)) remove(dest);
            rename(n->value, dest);
            free(base); free(dest);
        }
        str_list_free(cache_over_files);
        str_list_free(diff); str_list_free(pack_file); str_list_free(move_file);
    }
    str_list_free(cache_init_files);
    return 1;
}
static void _unique_handle(const char *tool_name) {
    kv_map *tools = _getdict(vpkg_sftw, "tool");
    kv_map *t = _getdict(tools, tool_name);
    if (!strcmp(tool_name, "pixi")) {
        log_info("info->install DLC(init home) for...>pixi<");
        char *cmd = xfmt("\"%s\" init \"%s\"", _getstr(t, "symbol_excu"), _getstr(t, "local_path"));
        _system_run_cmd(cmd); free(cmd);
        kv_map *s = kv_map_new();
        _setstr(s, "platform", "x64-win"); _setstr(s, "name", "prefix.bat");
        _setstr(s, "version", "1.0"); _setstr(s, "website", "void");
        _setstr(s, "local_path", _getstr(vpkg_root_tree, "root_script"));
        kv_map *pixi = _getdict(tools, "pixi");
        char *c = xfmt("@echo off\ncall %s shell --manifest-path %s/pixi.toml",
                       _getstr(pixi, "symbol_excu"), _getstr(pixi, "local_path"));
        _setstr(s, "content", c); free(c);
        _setbool(s, "install_statu", 0);
        kv_map *scripts = _getdict(vpkg_sftw, "script");
        kv_map_remove(scripts, "prefix");
        { value v; v.type = VAL_DICT; v.as.dict_val = s; kv_map_add(scripts, "prefix", &v); }
        _cmd_install_install_script("prefix");
    }
    if (!strcmp(tool_name, "python")) {
        log_info("info->install DLC(pip) for...>python<");
        kv_map *inst = _getdict(t, "install");
        const char *path_install = inst ? inst->head->key : "";
        char *file_pth = NULL, *file_pip = NULL, *file_py = NULL;
        str_list *files = str_list_new(), *dd = str_list_new();
        _get_file_and_dir(path_install, files, dd);
        str_list_free(dd);
        for (str_node *n = files->head; n; n = n->next) {
            size_t L = strlen(n->value);
            if (L >= 5 && !strcmp(n->value + L - 5, "._pth")) { free(file_pth); file_pth = xstrdup(n->value); }
            if (L >= 10 && !strcmp(n->value + L - 10, "get-pip.py")) { free(file_pip); file_pip = xstrdup(n->value); }
            if (L >= 10 && !strcmp(n->value + L - 10, "python.exe")) { free(file_py); file_py = xstrdup(n->value); }
        }
        str_list_free(files);
        if (file_pth) {
            char *content = read_whole(file_pth);
            if (content) {
                char *replaced = str_replace_all(content, "#import site", "import site");
                write_whole(file_pth, replaced);
                free(replaced); free(content);
            }
        }
        if (file_pth && file_pip && file_py) {
            char *cmd = xfmt("\"%s\" \"%s\"", file_py, file_pip);
            _system_run_cmd(cmd); free(cmd);
        }
        free(file_pth); free(file_pip); free(file_py);
    }
    if (!strcmp(tool_name, "rust")) {
        log_info("info->install DLC for...>rust<");
        kv_map *em = _getdict(t, "env_arg");
        str_list *rh = _getlist(em, "rustup_home"), *ch = _getlist(em, "cargo_home");
        if (rh && rh->head) _putenv_s("rustup_home", rh->head->value);
        if (ch && ch->head) _putenv_s("cargo_home", ch->head->value);
        char *cmd = xfmt("\"%s\"", _getstr(t, "symbol_excu"));
        _system_run_cmd(cmd); free(cmd);
    }
    if (!strcmp(tool_name, "lua")) {
        log_info("info->install DLC(luarocks config.lua) for...>lua<");
        kv_map *lua = _getdict(tools, "lua");
        const char *lua_root = _getstr(lua, "local_path");
        char *lua_include = xfmt("%s/include", lua_root);
        char *lua_excu = xstrdup(_getstr(lua, "symbol_excu"));
        {
            str_list *files = str_list_new(), *dd = str_list_new();
            scandir_paths(lua_root, files, dd);
            str_list_free(dd);
            for (str_node *n = files->head; n; n = n->next) {
                char *b = path_base(n->value);
                if (!strncmp(b, "luac", 4) && strlen(b) > 4 && !strcmp(b + strlen(b) - 4, ".exe")) {
                    free(lua_excu); lua_excu = xstrdup(n->value);
                }
                free(b);
            }
            str_list_free(files);
        }
        char *lua_copy = xfmt("%s/lua.exe", lua_root);
        copy_file(lua_excu, lua_copy);
        char *content = xfmt(
            "lua_version = \"5.5.0\"\n"
            "rocks_trees = {\n"
            "\t{name = \"user\",root = \"%s\",},\n"
            "}\n"
            "variables = {\n"
            "\tCC = \"gcc\",\n"
            "\tCXX = \"g++\",\n"
            "\tLINKFLAGS = \"-shared\",\n"
            "\tLUA_VERSION = \"5.5.0\",\n"
            "\tLUA = \"%s\",\n"
            "\tLUA_BINDIR = \"%s\",\n"
            "\tLUA_INCDIR = \"%s\",\n"
            "\tLUA_LIBDIR = \"%s\",\n"
            "}", lua_root, lua_copy, lua_root, lua_include, lua_root);
        kv_map *s = kv_map_new();
        _setstr(s, "platform", "x64-win");
        _setstr(s, "name", "config.lua");
        _setstr(s, "version", "v1.0");
        _setstr(s, "website", "void");
        _setstr(s, "local_path", lua_root);
        _setstr(s, "content", content);
        _setbool(s, "install_statu", 0);
        kv_map *scripts = _getdict(vpkg_sftw, "script");
        kv_map_remove(scripts, "luarocks_config");
        { value v; v.type = VAL_DICT; v.as.dict_val = s; kv_map_add(scripts, "luarocks_config", &v); }
        _cmd_install_install_script("luarocks_config");
        free(content); free(lua_copy); free(lua_include); free(lua_excu);
    }
}
/* 修复: 检查 _install_sftw 返回值, 失败不跑 _unique_handle */
static void _cmd_install(const char *tool_name) {
    log_info("info->cheak the repo for aim sftw...");
    if (!tool_name || !*tool_name || !strcmp(tool_name, vpkg_placeHolder)) {
        log_erro("erro->command “install” argu is empty...");
        return;
    }
    kv_map *tools = _getdict(vpkg_sftw, "tool");
    if (!_getdict(tools, tool_name)) {
        log_erro(xfmt("erro->platform...>%s<...the repo not contain...>%s<", _getstr(vpkg_info, "platform"), tool_name));
        return;
    }
    log_info("info->check the basic sftw...");
    if (!_check_basic_sftw_statu()) {
        log_erro("erro->lack of basic sftw...");
        return;
    }
    kv_map *t = _getdict(tools, tool_name);
    if (_getbool(t, "install_statu")) {
        log_info(xfmt("info->the sftw >%s< already install!!!", tool_name));
        return;
    }
    if (!_install_sftw(tool_name)) {
        log_erro(xfmt("erro->install faild...>%s<", tool_name));
        return;
    }
    _unique_handle(tool_name);
    if (!path_exists(_getstr(t, "symbol_excu"))) {
        log_erro(xfmt("erro->install faild...>%s<", tool_name));
        return;
    }
    log_info(xfmt("info->install success...>%s<", tool_name));
}
static void _cmd_remove(const char *tool_name) {
    if (str_list_find(vpkg_sftw_tool_basic, tool_name)) {
        log_erro(xfmt("erro->can not remove the basic sftw...>%s<", tool_name));
        return;
    }
    kv_map *tools = _getdict(vpkg_sftw, "tool");
    kv_map *t = _getdict(tools, tool_name);
    if (!t) { log_erro(xfmt("erro->repo not exist...>%s<", tool_name)); return; }
    if (!_getbool(t, "install_statu")) { log_erro(xfmt("erro->not install the sftw...>%s<", tool_name)); return; }
    const char *install_path = _getstr(t, "local_path");
    char *father = path_dir(install_path);
    rmtree_rec(install_path);
    if (path_exists(father)) {
        str_list *files = str_list_new(), *dirs = str_list_new();
        scandir_paths(father, files, dirs);
        if (str_list_size(files) == 0 && str_list_size(dirs) == 0) rmtree_rec(father);
        str_list_free(files); str_list_free(dirs);
    }
    free(father);
    log_warn(xfmt("warn->success remove sftw...>%s<", tool_name));
}
static int _cmd_excu(int argc, char **argv) {
    if (argc < 1) { log_erro("erro->command “excu” argument is empty..."); return 0; }
    const char *tool_name = argv[0];
    kv_map *tools = _getdict(vpkg_sftw, "tool");
    kv_map *scripts = _getdict(vpkg_sftw, "script");
    kv_map *entry = _getdict(tools, tool_name);
    if (entry) {
        char *cmd = xfmt("\"%s\"", _getstr(entry, "symbol_excu"));
        for (int i = 1; i < argc; i++) { char *nx = xfmt("%s \"%s\"", cmd, argv[i]); free(cmd); cmd = nx; }
        log_info(xfmt("info->running command...\n\t%s", cmd));
        int rc = system(cmd); free(cmd);
        if (rc != 0) log_erro("erro->running command...erro exit!!!");
        return rc == 0;
    }
    kv_map *script = _getdict(scripts, tool_name);
    if (script) {
        char *sp = path_join(_getstr(script, "local_path"), _getstr(script, "name"));
        char *cmd = xfmt("cmd /c \"%s\"", sp);
        for (int i = 1; i < argc; i++) { char *nx = xfmt("%s \"%s\"", cmd, argv[i]); free(cmd); cmd = nx; }
        log_info(xfmt("info->running command...\n\t%s", cmd));
        int rc = system(cmd); free(cmd); free(sp);
        if (rc != 0) log_erro("erro->running command...erro exit!!!");
        return rc == 0;
    }
    log_erro(xfmt("erro->platform...>%s<...repo not exist...>%s<", _getstr(vpkg_info, "platform"), tool_name));
    return 0;
}
static void extra_command(int argc, char **argv) {
    const char *cmd_type = vpkg_placeHolder;
    int cmd_valu_start = 2;
    if (argc >= 2) cmd_type = argv[1];
    {
        size_t total = 1;
        for (int i = 2; i < argc; i++) total += strlen(argv[i]) + 3;
        char *buf = (char *)calloc(1, total);
        strcat(buf, "[");
        for (int i = 2; i < argc; i++) { if (i > 2) strcat(buf, ", "); strcat(buf, "'"); strcat(buf, argv[i]); strcat(buf, "'"); }
        strcat(buf, "]");
        log_warn(xfmt("warn->func extra_command: %s...%s", cmd_type, buf));
        free(buf);
    }
    if (!str_list_find(vpkg_cmd, cmd_type)) { log_erro(xfmt("erro->vpkg not support command...>%s<", cmd_type)); return; }
    if (!strcmp(cmd_type, "help")) _cmd_help();
    else if (!strcmp(cmd_type, "list")) _cmd_list();
    else if (!strcmp(cmd_type, "install")) _cmd_install(argc > cmd_valu_start ? argv[cmd_valu_start] : vpkg_placeHolder);
    else if (!strcmp(cmd_type, "remove"))  _cmd_remove(argc > cmd_valu_start ? argv[cmd_valu_start] : vpkg_placeHolder);
    else if (!strcmp(cmd_type, "shell"))   _cmd_shell();
    else if (!strcmp(cmd_type, "excu"))    _cmd_excu(argc - cmd_valu_start, argv + cmd_valu_start);
}

int main(int argc, char **argv) {
    init_program();
    log_info(xfmt("info->vpkg local_path...>%s<", vpkg_root));
    log_info(xfmt("info->vpkg config_file path...>%s<", vpkg_config_file));
    log_info(xfmt("info->vpkg config_file exist...>%s<", path_exists(vpkg_config_file) ? "True" : "False"));
    extra_config();
    {
        size_t w = 0;
        for (kv_node *n = vpkg_info->head; n; n = n->next) if (strlen(n->key) > w) w = strlen(n->key);
        log_info("info->vpkg_info:");
        for (kv_node *n = vpkg_info->head; n; n = n->next) {
            if (n->val.type == VAL_STR)  log_info(xfmt("    %-*s -> %s", (int)w, n->key, n->val.as.str));
            else if (n->val.type == VAL_BOOL) log_info(xfmt("    %-*s -> %s", (int)w, n->key, n->val.as.bool_val ? "True" : "False"));
        }
    }
    extra_command(argc, argv);
    return 0;
}