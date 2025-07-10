#include <am.h>
#include <nemu.h>

void __am_timer_init() {
}

void __am_timer_uptime(AM_TIMER_UPTIME_T *uptime) {
    // 当偏移OFFSET为4时，更新RTCspace空间的值，然后进行读取inl读取
    uint64_t now = inl(RTC_ADDR) | ((uint64_t)inl(RTC_ADDR + 4) << 32);
    uptime->us = now;
}

void __am_timer_rtc(AM_TIMER_RTC_T *rtc) {
  rtc->second = 0;
  rtc->minute = 0;
  rtc->hour   = 0;
  rtc->day    = 0;
  rtc->month  = 0;
  rtc->year   = 1900;
}
