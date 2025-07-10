#include <am.h>

#define VGA_BASE 0x21000000
// 同步信号，开始传输给vga
#define SYNC_ADDR (0x21000000 + 0x0)
// 帧缓冲地址
#define FB_ADDR (0x21000000 + 0x4)

void __am_gpu_init () {}
void __am_gpu_config (AM_GPU_CONFIG_T *cfg) {
    uint32_t w = 640;
    uint32_t h = 480;
    *cfg       = (AM_GPU_CONFIG_T){.present   = true,
                                   .has_accel = false,
                                   .width     = w,
                                   .height    = h,
                                   .vmemsz    = w * h * 4};
}
void __am_gpu_fbdraw (AM_GPU_FBDRAW_T *ctl) {
    uint32_t *pixel = ctl->pixels;
    int       x = ctl->x, y = ctl->y, w = ctl->w, h = ctl->h;
    if (pixel != NULL) {
        int screen_width = 640;
        for (int i = y; i < (y + h); i++) {
            for (int j = x; j < (x + w); j++) {
                *(volatile uint32_t *)(FB_ADDR + ((i)*screen_width + j)*4) =
                    pixel[(i - y) * w + j - x];
            }
        }
    }
    // 将sync的值存入vgactl_port_base[1]
    if (ctl->sync) {  *(volatile uint32_t *)SYNC_ADDR = 1; }
}

void __am_gpu_status (AM_GPU_STATUS_T *status) {
    status->ready = true;
}
