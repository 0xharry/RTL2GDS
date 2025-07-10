#include <elf.h>
#include <stdio.h>
#include <common.h>

extern FILE *elf_file;
static int call_times = 0;
static int ret_times = 0;

typedef struct elf {
    Elf32_Ehdr elf_header;
    Elf32_Shdr strtab;
    Elf32_Sym *symtab;
    int symtab_num;
}ELF;

ELF ELF_ftrace;
void ftrace_init () {
    if (elf_file == NULL) {
        Assert(0,"文件为空");
    }
    int         fread_num = 0;
    char       str[100];
    Elf32_Ehdr elf_header;
    fread_num = fread (&elf_header, sizeof (Elf32_Ehdr), 1, elf_file);    // 将elf头的地址赋给elf_header
    if (fread_num != 1) {
        Assert(0,"fread读取失败,读取项数%d小于要求数1",fread_num);
    }

    /* 得到section header */
    Elf32_Shdr *section_header = (Elf32_Shdr *)malloc (sizeof (Elf32_Shdr) * elf_header.e_shnum);

    fseek (elf_file, elf_header.e_shoff, SEEK_SET);
    fread_num = fread (section_header, sizeof (Elf32_Shdr), elf_header.e_shnum,elf_file);    // 得到节头表地址
    if (fread_num != elf_header.e_shnum) {
        Assert(0,"fread读取失败,读取项数%d小于要求数%d",fread_num,elf_header.e_shnum);
    }

    /* 得到节头字符串节*/
    Elf32_Shdr shstrtab = section_header[elf_header.e_shstrndx];
    Elf32_Shdr strtab;
    Elf32_Shdr section_symtab = {}; // 初始化section_symtab

    /* 从节头字符串节中得到字符串节.strtab*/
    for (int j = 0; j < elf_header.e_shnum; j++) {
        fseek (elf_file, shstrtab.sh_offset + section_header[j].sh_name, SEEK_SET);
        int  i = 0;
        char ch;
        while ((ch = fgetc (elf_file)) != EOF && ch != '\0') { str[i++] = ch; }
        str[i] = '\0';
        // 找到了strtab节,即得到了字符串表
        if (strcmp (str, ".strtab") == 0) {
            strtab = section_header[j];    // 得到strtab节
        }
        // 找到了symtab节
        if (strcmp (str, ".symtab") == 0) {
            section_symtab = section_header[j];    // 得到strtab节
        }
    }
    /* 得到了符号表 */
    int        symtab_num = section_symtab.sh_size/sizeof(Elf32_Sym);
    Elf32_Sym *symtab     = (Elf32_Sym *)malloc (section_symtab.sh_size);
    fseek (elf_file, section_symtab.sh_offset, SEEK_SET);
    fread_num = fread (symtab, sizeof (Elf32_Sym), symtab_num, elf_file);
    ELF_ftrace.symtab_num = symtab_num;
    ELF_ftrace.elf_header = elf_header;
    ELF_ftrace.symtab = symtab;
    ELF_ftrace.strtab = strtab;
    
    // 遍历符号表的值
    /*for (int i = 0; i < symtab_num; i++) {*/
        /*printf("symtab[%d].st_value = 0x%lx\n",i,symtab[i].st_value);*/
    /*}*/
}

/* @param: pc: jal,jalr跳转的地址,即dnpc(动态pc)
 * @param: kind 0: jal,jalr 调用函数
 *              1: ret,返回函数
 */
void ftrace (uint64_t pc, int kind) {
    char  str[100] = "";
    char  str1[120] = "";
    char  str_out[10000] = "";
    // 为调用返回显示层次
    if (kind == 0) {    // 是函数调用
        for (int i = 0; i < ELF_ftrace.symtab_num; i++) {
            if (pc == ELF_ftrace.symtab[i].st_value &&
                pc != 0x20000000) {    // 找到对应的项
                if (ELF32_ST_TYPE (ELF_ftrace.symtab[i].st_info) ==
                    STT_FUNC) {    // 如果对应项是函数,得到函数名
                    fseek (elf_file,
                           ELF_ftrace.strtab.sh_offset + ELF_ftrace.symtab[i].st_name,
                           SEEK_SET);
                    int  j = 0;
                    char ch;
                    while ((ch = fgetc (elf_file)) != EOF && ch != '\0') {
                        str[j++] = ch;
                    }
                    str[j] = '\0';    // 得到了函数名
                    for (int i = 0; i < (call_times - ret_times); i++) { strcat (str_out, "   "); }

                    call_times++;
                    sprintf (str1, "call [%s]@0x%lx", str, pc);
                    strcat (str_out, str1);
                    printf (ANSI_FG_GREEN "%s" ANSI_NONE "\n", str_out);
                    break;
                }
            }
        }
    }else if (kind == 1) { //判断地址是否属于某段函数区域
        for (int i = 0; i < ELF_ftrace.symtab_num; i++) {
            if ((pc >= ELF_ftrace.symtab[i].st_value)  && (pc <= ELF_ftrace.symtab[i].st_value + ELF_ftrace.symtab[i].st_size)) {
                if (ELF32_ST_TYPE (ELF_ftrace.symtab[i].st_info) ==
                    STT_FUNC) {    // 如果对应项是函数,得到函数名
                    fseek (elf_file,
                           ELF_ftrace.strtab.sh_offset + ELF_ftrace.symtab[i].st_name,
                           SEEK_SET);
                    int  j = 0;
                    char ch;
                    while ((ch = fgetc (elf_file)) != EOF && ch != '\0') {
                        str[j++] = ch;
                    }
                    str[j] = '\0';    // 得到了函数名
                    ret_times++;
                    for (int i = 0; i < (call_times - ret_times); i++) { strcat (str_out, "   "); }
                    sprintf (str1, "ret [%s]", str);
                    strcat (str_out, str1);
                    printf (ANSI_FG_GREEN "%s" ANSI_NONE "\n", str_out);
                    break;
                }

            }
        }

    }
}
