#include <am.h>
#include <amdev.h>

#define KEYBOARD_BASE_ADDR 0x10011000
static inline uint8_t  inb(uintptr_t addr) { return *(volatile uint8_t  *)addr; } 

static int kbd_lut[0x100] = {
    [0x00] = AM_KEY_NONE,          // 未定义
    [0x76] = AM_KEY_ESCAPE, // ESC
    [0x05] = AM_KEY_F1,     // F1
    [0x06] = AM_KEY_F2,     // F2
    [0x04] = AM_KEY_F3,     // F3
    [0x0C] = AM_KEY_F4,     // F4
    [0x03] = AM_KEY_F5,     // F5
    [0x0B] = AM_KEY_F6,     // F6
    [0x83] = AM_KEY_F7,     // F7
    [0x0A] = AM_KEY_F8,     // F8
    [0x01] = AM_KEY_F9,     // F9
    [0x09] = AM_KEY_F10,    // F10
    [0x78] = AM_KEY_F11,    // F11
    [0x07] = AM_KEY_F12,    // F12

    [0x0E] = AM_KEY_GRAVE,  // ~
    [0x16] = AM_KEY_1,      // 1!
    [0x1E] = AM_KEY_2,      // 2@
    [0x26] = AM_KEY_3,      // 3#
    [0x25] = AM_KEY_4,      // 4$
    [0x2E] = AM_KEY_5,      // 5%
    [0x36] = AM_KEY_6,      // 6^
    [0x3D] = AM_KEY_7,      // 7&
    [0x3E] = AM_KEY_8,      // 8*
    [0x46] = AM_KEY_9,      // 9(
    [0x45] = AM_KEY_0,      // 0)
    [0x4E] = AM_KEY_MINUS,  // -
    [0x55] = AM_KEY_EQUALS,  // =
    [0x5D] = AM_KEY_BACKSLASH,// '\,|`
    [0x66] = AM_KEY_BACKSPACE,// Backspace

    [0x0D] = AM_KEY_TAB,     // TAB
    [0x15] = AM_KEY_Q,       // Q
    [0x1D] = AM_KEY_W,       // W
    [0x24] = AM_KEY_E,       // E
    [0x2D] = AM_KEY_R,       // R
    [0x2C] = AM_KEY_T,       // T
    [0x35] = AM_KEY_Y,       // Y
    [0x3C] = AM_KEY_U,       // U
    [0x43] = AM_KEY_I,       // I
    [0x44] = AM_KEY_O,       // O
    [0x4D] = AM_KEY_P,       // P
    [0x54] = AM_KEY_LEFTBRACKET,       //( 
    [0x5B] = AM_KEY_RIGHTBRACKET,      //)

    [0x58] = AM_KEY_CAPSLOCK,//CAPS
    [0x1C] = AM_KEY_A,       // A
    [0x1B] = AM_KEY_S,       // S
    [0x23] = AM_KEY_D,       // D
    [0x2B] = AM_KEY_F,       // F
    [0x34] = AM_KEY_G,       // G
    [0x33] = AM_KEY_H,       // H
    [0x3B] = AM_KEY_J,       // J
    [0x42] = AM_KEY_K,       // K
    [0x4B] = AM_KEY_L,       // L
    [0x4C] = AM_KEY_SEMICOLON,// ;
    [0x52] = AM_KEY_APOSTROPHE,//' 
    [0x5A] = AM_KEY_RETURN, //return

    [0x12] = AM_KEY_LSHIFT,  // LSHIFT
    [0x1A] = AM_KEY_Z,       // Z
    [0x22] = AM_KEY_X,       // X
    [0x21] = AM_KEY_C,       // C
    [0x2A] = AM_KEY_V,       // V
    [0x32] = AM_KEY_B,       // B
    [0x31] = AM_KEY_N,       // N
    [0x3A] = AM_KEY_M,       // M
    [0x41] = AM_KEY_COMMA,   // ,
    [0x49] = AM_KEY_PERIOD,  // .
    [0x4A] = AM_KEY_SLASH,   // /
    [0x59] = AM_KEY_RSHIFT,  // RSHIFT

    [0x14] = AM_KEY_LCTRL,
    /*[0x] = AM_KEY_APPLICATION, //啥玩意*/
    [0x11] = AM_KEY_LALT, 
    [0x29] = AM_KEY_SPACE, 
    /*[0x] = AM_KEY_RALT,  //晚点实现*/
    /*[0x] = AM_KEY_RCTRL, //晚点实现*/

    /*[0x] = AM_KEY_UP,       // 向上箭头*/
    /*[0x] = AM_KEY_DOWN,     // 向下箭头*/
    /*[0x] = AM_KEY_LEFT,     // 向左箭头*/
    /*[0x] = AM_KEY_RIGHT,    // 向右箭头*/
    /*[0x] = AM_KEY_INSERT,   // 插入键*/
    /*[0x] = AM_KEY_DELETE,   // 删除键*/
    /*[0x] = AM_KEY_HOME,     // Home 键*/
    /*[0x] = AM_KEY_END,      // End 键*/
    /*[0x] = AM_KEY_PAGEUP,   // Page Up 键*/
};

void __am_input_keybrd(AM_INPUT_KEYBRD_T *kbd) {
    int scancode = inb(KEYBOARD_BASE_ADDR); //通过inb(KBD_ADDR),访问键盘地址，将会生成指令load,从而调用函数paddr_read().经过一系列步骤后，会得到i8042_data_port_base[0]的值，是一个字节的数据
    if (scancode != AM_KEY_NONE) {// 这个scancode其实是通过device_updata函数检测到按键按下，再将键码存入key_queue.然后当我调用paddr_read时，会调用key_dequeue()函数，得到键码
        kbd->keydown = 1;
        kbd->keycode = kbd_lut[scancode&0xFF]; //避免超出数组范围，有些按键没实现
    }else {
        kbd->keydown = 0;
        kbd->keycode = AM_KEY_NONE;
    }
}
