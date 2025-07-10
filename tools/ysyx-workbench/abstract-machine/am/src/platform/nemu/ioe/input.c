#include <am.h>
#include <nemu.h>

#define KEYDOWN_MASK 0x8000

void __am_input_keybrd(AM_INPUT_KEYBRD_T *kbd) {
    int scancode = inb(KBD_ADDR); //通过inb(KBD_ADDR),访问键盘地址，将会生成指令load,从而调用函数paddr_read().经过一系列步骤后，会得到i8042_data_port_base[0]的值，是一个字节的数据
    if (scancode != AM_KEY_NONE) {// 这个scancode其实是通过device_updata函数检测到按键按下，再将键码存入key_queue.然后当我调用paddr_read时，会调用key_dequeue()函数，得到键码
        kbd->keydown = 1;
        kbd->keycode = scancode;
    }else {
        kbd->keydown = 0;
        kbd->keycode = AM_KEY_NONE;
    }
}
