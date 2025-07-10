#include <am.h>

#define UART_BASE_ADDR 0x10000000
#define UART_RX_ADDR (UART_BASE_ADDR + 0x0)
#define UART_LS_ADDR (UART_BASE_ADDR + 0x5)
void __am_uart_rx(AM_UART_RX_T *rx) {
    char get_ch = 0xFF;
    if ((*(volatile uint8_t *)(UART_LS_ADDR) & 0x01) == 0x01) {
        //没有判断是否溢出
        get_ch = *(volatile uint8_t *)(UART_RX_ADDR);
        rx->data = get_ch; 
    } else {
        rx->data = 0xFF; 
    }
}
