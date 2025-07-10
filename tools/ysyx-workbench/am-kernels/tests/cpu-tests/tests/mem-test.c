#include "trap.h"
#define MEM_BASE 0x80000000L
#define CHECK_RANGE 0x0000010 /* 4*1024即4*2^10 */
int main() {
    /*uint32_t mem_addr = MEM_BASE;*/
    /*uint32_t data;*/

    /*uint32_t lenmask = 0xFF;*/
     /*[>1字节<]*/
    /*for (int i = 0; i < CHECK_RANGE; i ++) {*/
        /*data = mem_addr & lenmask;*/
        /**(volatile char *)(mem_addr) = (uint8_t)data;*/
        /*mem_addr += 1;*/
    /*}*/
    /*mem_addr = MEM_BASE;*/

    /*for (int i = 0; i < CHECK_RANGE; i++) {*/
        /*data = *(volatile char *)(mem_addr);*/
        /*check(data == (mem_addr & lenmask));*/
        /*mem_addr += 1;*/
    /*}*/
    /*// 2字节*/
    /*lenmask = 0xFFFF;*/
    /*mem_addr = MEM_BASE;*/
    /*for (int i = 0; i < CHECK_RANGE/2; i ++) {*/
        /*data = mem_addr & lenmask;*/
        /**(volatile uint16_t *)(mem_addr) = (uint16_t)data;*/
        /*mem_addr += 2;*/
    /*}*/
    /*mem_addr = MEM_BASE;*/
    /*for (int i = 0; i < CHECK_RANGE/2; i++) {*/
        /*data = *(volatile uint16_t *)(mem_addr);*/
        /*check(data == (mem_addr & lenmask));*/
        /*mem_addr += 2;*/
    /*}*/


    /*// 4字节*/
    /*lenmask = 0xFFFFFFFF;*/
    /*mem_addr = MEM_BASE;*/
    /*for (int i = 0; i < CHECK_RANGE/4; i ++) {*/
        /*data = mem_addr & lenmask;*/
        /**(volatile uint32_t *)(mem_addr) = (uint32_t)data;*/
        /*mem_addr += 4;*/
    /*}*/
    /*mem_addr = MEM_BASE;*/
    /*for (int i = 0; i < CHECK_RANGE/4; i++) {*/
        /*data = *(volatile uint32_t *)(mem_addr);*/
        /*check(data == (mem_addr & lenmask));*/
        /*mem_addr += 4;*/
    /*}*/
    return 0;
}



