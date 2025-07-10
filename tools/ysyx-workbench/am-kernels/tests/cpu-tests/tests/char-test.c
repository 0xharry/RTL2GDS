#include "trap.h"
#define UART_BASE 0x10000000L
#define UART_TX   0x0
int main () {
    putch(0b00111111);
    printf("hello\n");
    return 0;
}
