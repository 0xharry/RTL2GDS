#include <am.h>
#include <klib-macros.h>
#include <klib.h>

extern char _heap_start;
int main(const char *args);

extern char _pmem_start;
#define PMEM_SIZE (128 * 1024 * 1024)
#define PMEM_END  ((uintptr_t)&_pmem_start + PMEM_SIZE)

Area heap = RANGE(&_heap_start, PMEM_END);
#ifndef MAINARGS
#define MAINARGS ""
#endif
static const char mainargs[] = MAINARGS;

//个人添加的宏
#define DEVICE_BASE 0xa0000000
#define MMIO_BASE 0xa0000000
#define SERIAL_PORT     (DEVICE_BASE + 0x00003f8)

void putch(char ch) {
    *(volatile uint8_t *)(SERIAL_PORT) = ch;
}

void halt(int code) {
  /*printf("EXIT CODE = %d\n",code);*/
  asm volatile ("ebreak");
  while (1);
}

void _trm_init() {

  /*extern void malloc_reset();*/
  /*malloc_reset();*/

  int ret = main(mainargs);
  halt(ret);
}
