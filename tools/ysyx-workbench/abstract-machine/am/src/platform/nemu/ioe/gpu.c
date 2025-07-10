#include <am.h>
#include <nemu.h>

#define SYNC_ADDR (VGACTL_ADDR + 4)

void __am_gpu_init() {
}
void __am_gpu_config(AM_GPU_CONFIG_T *cfg) {
  uint32_t wh = inl(VGACTL_ADDR);
  uint32_t w = (wh >> 16)&0xFFFF;
  uint32_t h = wh&0xFFFF;
  *cfg = (AM_GPU_CONFIG_T) {
    .present = true, .has_accel = false,
    .width = w, .height = h,
    .vmemsz = w*h*4
  };
}
void __am_gpu_fbdraw (AM_GPU_FBDRAW_T *ctl) {
  uint32_t *pixel = ctl->pixels;
  int       x = ctl->x, y = ctl->y, w = ctl->w, h = ctl->h;
  uint32_t *fb = (uint32_t *)(uintptr_t)FB_ADDR;
  if (pixel != NULL) {
      int screen_width = io_read (AM_GPU_CONFIG).width;
      for (int i = y; i < (y + h); i++) {
          for (int j = x; j < (x + w); j++) {
              fb[(i)*screen_width + j] = pixel[(i - y) * w + j-x];
          }
      }
  }
  // 将sync的值存入vgactl_port_base[1]
  if (ctl->sync) { outl (SYNC_ADDR, 1); }
}

void __am_gpu_status (AM_GPU_STATUS_T *status) {
  status->ready = true;
}
