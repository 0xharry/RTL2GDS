#include <am.h>
#include <klib-macros.h>
#include <klib.h>

extern char _heap_start;
int main(const char *args);

// extern char _pmem_start;
// #define PMEM_SIZE (128 * 1024 * 1024)
// #define PMEM_END  ((uintptr_t)&_pmem_start + PMEM_SIZE)
extern char _pmem_start;
extern char _heap_end;
#define PMEM_SIZE (4 * 1024)
#define PMEM_END  ((uintptr_t)&_heap_end  )

Area heap = RANGE(&_heap_start, PMEM_END);
static const char mainargs[MAINARGS_MAX_LEN] = TOSTRING(MAINARGS_PLACEHOLDER); // defined in CFLAGS

//个人添加的宏
#define UART_BASE 0x10000000
#define UART_TX_ADDR   UART_BASE + 0x0
#define UART_REG_FC    UART_BASE + 0x2
#define UART_REG_LC    UART_BASE + 0x3
#define UART_REG_LS    UART_BASE + 0x5

void init_uart (void) {
    *(volatile uint8_t *)(UART_REG_LC) = 0b10000011;    // 1停止位，无校验位，禁止中断，开始写divisor
    *(volatile uint8_t *)(UART_TX_ADDR) = 0x01;    // 写Divisor
    *(volatile uint8_t *)(UART_REG_LC) = 0b00000011;    // 1停止位，无校验位，禁止中断，停止写divisor
}

void putch (char ch) {
    *(volatile uint8_t *)(UART_TX_ADDR) = ch;
    /*uint8_t lsr = *(volatile uint8_t *)(UART_REG_LS);*/
    /*while ((lsr & 0x40) != 0x40) { //等待lsr6为1,即等待uart数据发送完成*/
        /*lsr = *(volatile uint8_t *)(UART_REG_LS);*/
    /*}*/
    /*while(((*(volatile uint8_t *)(UART_REG_LS))&0x20) != 0x20); //等待传输FIFO为空*/
    /**(volatile uint8_t *)(UART_REG_FC) = 0b11000100; //强制清空缓存区*/
}

void print_hex(uint32_t num) { //简单的输出32位十六进制数
    char hex_digits[] = "0123456789ABCDEF";
    char hex_string[8];
    int num_digits = 0;
    do {
        hex_string[num_digits++] = hex_digits[num % 16];
        num /= 16;
    } while (num != 0);
    for (int i = num_digits - 1; i >= 0; i--) {
        putch(hex_string[i]); // Output each hex digit
    }
    putch('\n');
}

// 通过在psram保留区写入特殊数据来实现trap;
void halt (int code) {
    *(uint8_t *)0x80000000 = 0xaa;
    // asm volatile("ebreak");
    while (1)
        ;
}

/* @brief : 从MROM赋值数据段到SRAM
 * @return: None
 */

extern char _ssbl_SA [];
extern char _ssbl_MA [];
extern char _ssbl_end [];
extern char _text_SA [];
extern char _text_MA [];
extern char _text_end [];
extern char _rodata_SA [];
extern char _rodata_MA [];
extern char _rodata_end [];
extern char _data_SA [];
extern char _data_MA [];
extern char _data_end [];

/* 用于将my_memcpy 和memcpy分别放在entry,fsbl中，方便内存的移动*/
void my_memcpy(void *dest, const void *src, size_t n)__attribute__((section(".entry")));
void my_memcpy(void *dest, const void *src, size_t n) {
    unsigned char *d = (unsigned char *)dest;
    const unsigned char *s = (const unsigned char *)src;

    for (size_t i = 0; i < n; i++) {
        d[i] = s[i];
    }
}

void _FSBL (void)__attribute__((section(".entry")));
// 将_init_memory移动到sram中
void _FSBL (void) {
    my_memcpy (_ssbl_SA, _ssbl_MA, (_ssbl_end - _ssbl_SA));
    asm volatile (
        "lui t0, %hi(_init_memory)\n"  // _init_memory的高20位
        "addi t0, t0, %lo(_init_memory)\n" // 得到_init_memory的低12位
        "jalr ra, 0(t0)\n"
    );
}

//通过弱定义提供默认值
extern char __fsymtab_start [] __attribute__((weak));
extern char __am_apps_data_end [] __attribute__((weak));
extern char __extra_ma [] __attribute__((weak));

void _init_memory (void) __attribute__((section(".ssbl")));
void _init_memory (void) {
    memcpy (_text_SA, _text_MA, (_text_end - _text_SA)); //复制text节
    memcpy (_rodata_SA, _rodata_MA, (_rodata_end - _rodata_SA)); //复制rodata节
    if (__fsymtab_start != 0) {
        memcpy (__fsymtab_start, __extra_ma, (__am_apps_data_end - __fsymtab_start));
    }else {
        //....不执行
    }
    print_hex((uint32_t)_data_SA);
    print_hex((uint32_t)_data_MA);
    print_hex((uint32_t)_data_end);
    print_hex(_data_end - _data_SA);
    memcpy (_data_SA, _data_MA, (_data_end - _data_SA)); //赋值data节

    /*memcpy (_text_SA, _text_MA, data_end - _text_SA);*/
    // 如何跳转到ram的main中呢
    asm volatile (
        "lui t0, %hi(_trm_init)\n"  // main的高20位
        "addi t0, t0, %lo(_trm_init)\n" // 得到main的低12位跳转到main
        "jalr ra, 0(t0)\n"
    );
}

void _trm_init () {
    init_uart();
    extern void malloc_reset();
    malloc_reset();
    int ret = main (mainargs);
    halt (ret);
}
