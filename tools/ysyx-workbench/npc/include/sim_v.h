#ifndef __SIM_V_H__
#define __SIM_V_H__

#include "VysyxSoCFull.h"   // create `top.v`,so use `Vtop.h`
#include <verilated.h>
//#include <verilated_vcd_c.h>
#include <verilated_fst_c.h>

/* 用于建立DPI-C */
#include "svdpi.h"
#include "VysyxSoCFull__Dpi.h"
#include <VysyxSoCFull___024root.h>

// 接入nvboard
//#include <nvboard.h>

#include <cpu/decode.h>

void sim_exit(void);
void sim_init(void);
void init_SimClk(void);
void step_and_dump_wave(int time);

void step_n_clk(uint32_t n);
void inst_clk_cycle(Decode *s);
void npc_update_pc(int addr);
void npc_trap(void);
void npc_assert(int addr);
//void cpu_mem_write(long long int addr, long long int data);
//uint32_t cpu_mem_read(long long  paddr, int len);
void isa_reg_display();
void isa_csrs_display (void);
uint32_t get_regs(int index);
void my_nvboard_init(void);
uint64_t read_sram (uint32_t addr);
void update_perf_counter(int tags);
void print_perf_counter(void);
void perf_counter_trace(void);
void perf_trace_init(void);
void get_cache_amat(int hit, int start_end);
#endif
