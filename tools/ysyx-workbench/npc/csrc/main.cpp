#include <cinttypes>
#include <cstdint>
#include <cstdio>
#include <stdint.h>
#include <stdlib.h>
#include <unistd.h>
#include <sim_v.h>
#include "utils.h"
#include <cpu/decode.h>
#include <cpu/cpu.h>


extern VerilatedContext    *contextp;
extern VerilatedFstC       *tfp;
extern VysyxSoCFull *top;

extern NPCState npc_state;

extern uint32_t mvendorid;
extern uint32_t marchid;
extern uint8_t digtal_tube[16];

void init_monitor (int argc, char *argv[]);
void sdb_mainloop();
int is_exit_status_bad();

// 主函数
void show_study_code(void);
int main (int argc, char *argv[]) {
    Verilated::commandArgs(argc, argv);
    // 1. 初始化监视器
    init_monitor(argc,argv);
    // 2. 初始化仿真模块
    sim_init();

    // printf("define Max simulation cycles: %ld\n", MAX_SIM_TIME);
    // 初始化npc时序
    init_SimClk();
    extern riscv32_CPU_state cpu;
    uint32_t pc = cpu.pc;
    uint32_t dnpc = 0;
    uint64_t counter = 0;
    //inst_start_cycle = cycle_times;
    while (npc_state.state == NPC_RUNNING && counter  < MAX_SIM_TIME) {
        step_n_clk(1);
        counter ++;
    }

    sim_exit();
    return is_exit_status_bad();
}
