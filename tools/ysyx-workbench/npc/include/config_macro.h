#ifndef __CONFIG_MACRO_H__
#define __CONFIG_MACRO_H__


#define CONFIG_ISA_riscv32 1
#define CONFIG_WATCHPOINT 0 //先关闭
#define CONFIG_PC_RESET_OFFSET 0x0

#define SRAM_BASE    0x0f000000
#define SRAM_SIZE    0x00002000

#define CONFIG_MSIZE 0x20000000
#define CONFIG_MBASE 0x30000000

// #define CONFIG_DIFFTEST 1 //先关闭
#define CONFIG_TIMER_GETTIMEOFDAY 1

#define CONFIG_TRACE 1
#define CONFIG_TRACE_START 0
#define CONFIG_TRACE_END 1000
#define CONFIG_TARGET_NATIVE_ELF 1
#define CONFIG_ITRACE 1
#define CONFIG_ITRACE_COND "true"
//#define CONFIG_ETRACE 1
//#define CONFIG_FTRACE 1
//#define CONFIG_MTRACE 1

//记录波形的开关
// #define CONFIG_LOG_TRACE

//#define CONFIG_ITRACE_INF

//#define CONFIG_NVBOARD

// 开启ifu性能计算器trace的开关
//#define CONFIG_IFU_PERF_TRACE
#endif
