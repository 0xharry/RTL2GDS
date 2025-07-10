#include <sim_v.h>
#include <stdio.h>
#include <utils.h>
#include <memory/paddr.h>
#include <cpu/ifetch.h>
#include <cpu/cpu.h>
#include <cpu/difftest.h>

VerilatedContext    *contextp = NULL;
VerilatedFstC       *tfp      = NULL;
VysyxSoCFull *top;

uint32_t mvendorid;
uint32_t marchid;

uint64_t cycle_times;      //总时钟周期数
uint8_t inst_kind; //指令类别
uint64_t inst_start_cycle; //指令开始时钟周期
uint64_t ifu_end_cycle;    //ifu结束时的时钟周期
uint64_t idu_end_cycle;    //idu结束时的时钟周期
uint64_t exu_end_cycle;    //exu结束时的时钟周期
uint64_t load_end_cycle;   //load结束时的时钟周期
uint64_t store_end_cycle;  //store结束时的时钟周期

enum {
    /* 各个阶段的性能计数器*/
    IFU_PERF,//0
    EXU_PERF,
    MEM_LOAD_PERF,
    MEM_WRITE_PERF,
    /* 不同指令类别的性能计数器*/
    INST_CACL_PERF,
    INST_LOAD_PERF,
    INST_WRITE_PERF,
    INST_JUMP_PERF,
    INST_CSR_PERF,
};

struct PERF_COUNTER {
    uint64_t times; //总计次数
    uint64_t total_cycles; //总计周期数
    double    average_cycles; //平均周期数
    uint64_t cycles; //当次周期数
}perf_counter[15];

uint8_t digtal_tube[16] = {
    0b11111100, // 0
    0b01100000, // 1
    0b11011010, // 2
    0b11110010, // 3
    0b01100110, // 4
    0b10110110, // 5
    0b10111110, // 6
    0b11100000, // 7
    0b11111110, // 8
    0b11110110, // 9
    0b11101110, // A
    0b00111110, // B
    0b10011100, // C
    0b01111010, // D
    0b10011110, // E
    0b10001110  // F
};

/* @brief : 初始化仿真相关参数
 * @return: None
 */
void sim_init (void) {
    contextp = new VerilatedContext;
    tfp      = new VerilatedFstC;
    top      = new VysyxSoCFull;
    contextp->traceEverOn (true);

#ifdef CONFIG_LOG_TRACE
    top->trace (tfp, 0);
    tfp->open ("wave.fst");
#endif
}


/* @brief : 初始化nvboard
 * @return: None
 */
void my_nvboard_init(void) {
    //extern void nvboard_bind_all_pins(VysyxSoCFull* top);
    //nvboard_bind_all_pins(top);
    //nvboard_init();
}

/* @brief : 推进仿真
 * @return: None
 */
void step_and_dump_wave (int time) {
    top->eval();
    contextp->timeInc (time);
#ifdef CONFIG_LOG_TRACE
    tfp->dump (contextp->time());
#endif
}



/* @brief : 结束仿真
 * @return: None
 */
void sim_exit (void) {
    step_and_dump_wave(1);
#ifdef CONFIG_LOG_TRACE
    tfp->close();
#endif
}




/* @brief : 模仿n个clk周期
 * @return: None
 */
void step_n_clk(uint32_t n) {
    while (n--) {
        top->clock  ^= 1;
        step_and_dump_wave(1);
#ifdef CONFIG_NVBOARD
        nvboard_update();
#endif
        top->clock  ^= 1;
        step_and_dump_wave(1);
        cycle_times++;
    }
}

/* @brief : 初始化npc的时序,pc
 * @return: None
 */
void init_SimClk(void) {
    //初始化时序
    top->clock = 0;
    top->reset = 1;
    step_and_dump_wave(1);
    step_n_clk(20);
    top->clock ^=1;
    top->reset = 0;
    step_and_dump_wave(1);
    npc_state.state = NPC_RUNNING;
}


void npc_update_pc(int addr) {
  cpu.pc = addr;
}

extern "C" void psram_trap(void){
    npc_state.state = NPC_END;
}

#define DEVICE_BASE 0xa0000000
#define SERIAL_PORT     (DEVICE_BASE + 0x00003f8)
#define RTC_ADDR        (DEVICE_BASE + 0x0000048)
extern "C" int pmem_read (int raddr) {
    // 总是读取地址为`raddr & ~0x3u`的4字节返回(对地址的最后两位清零，确保地址访问总是4的倍数)
    raddr = raddr & ~0x3u;
#ifdef CONFIG_MTRACE
  /*添加mtrace*/
  // 输出当前访问的内存
  printf(ANSI_FMT("Read memory:  0x%x\n",ANSI_FG_YELLOW),raddr);
#endif
    return paddr_read(raddr,4);
}


extern "C" void pmem_write (int waddr, int wdata, char wmask) {
    // int shift_bits = 8*(waddr & 0x3u);//因为地址按字节对其，所以需要对数据进行一些处理
    //// 总是往地址为`waddr & ~0x3u`的4字节按写产度`wlen`写入`wdata`
    // waddr = waddr & ~0x3u;
#ifdef CONFIG_MTRACE
    /*添加mtrace*/
    // 输出当前访问的内存
    printf (ANSI_FMT ("Write memory: 0x%x\n", ANSI_FG_YELLOW), waddr);
#endif
    if (wmask == 0b1) {    // 写入一个字节
        paddr_write (waddr, 1, wdata);
    } else if (wmask == 0b11) {    // 写入两个字节
        paddr_write (waddr, 2, wdata);
    } else if (wmask == 0b1111) {    // 写入4个字节
        paddr_write (waddr, 4, wdata);
    }
}

extern "C" void flash_read(int32_t addr, int32_t *data) {
    addr = addr & ~0x3u;
    *data = flash_addr_read(addr);
}
extern "C" void mrom_read(int32_t addr, int32_t *data) {
    addr = addr & ~0x3u;
    *data = mrom_addr_read(addr);
    //assert(1);
}


uint64_t read_sram (uint32_t addr) {
    addr = (addr&0x0001FFF8) >> 3;
    if ((int32_t)addr >= 0 && (int32_t)addr < 0x2000) {
        // uint64_t data = top->rootp->ysyxSoCFull__DOT__asic__DOT__axi4ram__DOT__mem_ext__DOT__Memory[addr];
        // return data;
    }
    Assert(1,"访问sram内存错误");
    return 0;
}


/* @brief : 更新性能计数器
 * @return: NULL
 */

void update_perf_counter(int tags) {
    switch (tags) {
        case 0: /* IFU perf counter */
            perf_counter[IFU_PERF].times ++;
            perf_counter[IFU_PERF].cycles = cycle_times - inst_start_cycle;
            perf_counter[IFU_PERF].total_cycles += perf_counter[IFU_PERF].cycles;
            perf_counter[IFU_PERF].average_cycles = perf_counter[IFU_PERF].total_cycles * 1.0 / perf_counter[IFU_PERF].times;
            ifu_end_cycle = cycle_times;
            #ifdef CONFIG_IFU_PERF_TRACE
            perf_counter_trace();
            #endif
            break;
        case 1: /* IDU-计算类指令(times) perf counter */
            inst_kind = 1;//得到类别
            idu_end_cycle = cycle_times;
            break;
        case 2: /* IDU-LOAD类指令(times) perf counter */
            inst_kind = 2;
            idu_end_cycle = cycle_times;
            break;
        case 3: /* IDU-WRITE类指令(times) perf counter */
            inst_kind = 3;
            idu_end_cycle = cycle_times;
            break;
        case 4: /* IDU-CSR类指令(times) perf counter */
            inst_kind = 4;
            idu_end_cycle = cycle_times;
            break;
        case 5: /* IDU-跳转类指令(times) perf counter */
            inst_kind = 5;
            idu_end_cycle = cycle_times;
            break;
        case 6: /* EXU完成计算的 perf counter */
            perf_counter[EXU_PERF].times ++;
            perf_counter[EXU_PERF].cycles = cycle_times - idu_end_cycle;
            perf_counter[EXU_PERF].total_cycles += perf_counter[EXU_PERF].cycles;
            perf_counter[EXU_PERF].average_cycles = perf_counter[EXU_PERF].total_cycles * 1.0 / perf_counter[EXU_PERF].times;
            exu_end_cycle = cycle_times;
            break;
        case 7: /* MEM阶段:LOAD取到数据 perf counter */
            perf_counter[MEM_LOAD_PERF].times ++;
            perf_counter[MEM_LOAD_PERF].cycles = cycle_times - exu_end_cycle;
            perf_counter[MEM_LOAD_PERF].total_cycles += perf_counter[MEM_LOAD_PERF].cycles;
            perf_counter[MEM_LOAD_PERF].average_cycles = perf_counter[MEM_LOAD_PERF].total_cycles * 1.0 / perf_counter[MEM_LOAD_PERF].times;
            break;
        case 8: /* MEM阶段:Write写入数据 perf counter */
            perf_counter[MEM_WRITE_PERF].times ++;
            perf_counter[MEM_WRITE_PERF].cycles = cycle_times - exu_end_cycle;
            perf_counter[MEM_WRITE_PERF].total_cycles += perf_counter[MEM_WRITE_PERF].cycles;
            perf_counter[MEM_WRITE_PERF].average_cycles = perf_counter[MEM_WRITE_PERF].total_cycles * 1.0 / perf_counter[MEM_WRITE_PERF].times;
            break;
        case 9: /* WB写回阶段(总结各个命令的耗时) perf counter */
            if (inst_kind == 1) {
                perf_counter[INST_CACL_PERF].times ++;
                perf_counter[INST_CACL_PERF].cycles = cycle_times - inst_start_cycle;
                perf_counter[INST_CACL_PERF].total_cycles += perf_counter[INST_CACL_PERF].cycles;
                perf_counter[INST_CACL_PERF].average_cycles = perf_counter[INST_CACL_PERF].total_cycles * 1.0 / perf_counter[INST_CACL_PERF].times;
            }else if (inst_kind == 2) {
                perf_counter[INST_LOAD_PERF].times ++;
                perf_counter[INST_LOAD_PERF].cycles = cycle_times - inst_start_cycle;
                perf_counter[INST_LOAD_PERF].total_cycles += perf_counter[INST_LOAD_PERF].cycles;
                perf_counter[INST_LOAD_PERF].average_cycles = perf_counter[INST_LOAD_PERF].total_cycles * 1.0 / perf_counter[INST_LOAD_PERF].times;
            }else if (inst_kind == 3) {
                perf_counter[INST_WRITE_PERF].times ++;
                perf_counter[INST_WRITE_PERF].cycles = cycle_times - inst_start_cycle;
                perf_counter[INST_WRITE_PERF].total_cycles += perf_counter[INST_WRITE_PERF].cycles;
                perf_counter[INST_WRITE_PERF].average_cycles = perf_counter[INST_WRITE_PERF].total_cycles * 1.0 / perf_counter[INST_WRITE_PERF].times;
            }else if (inst_kind == 4) {
                perf_counter[INST_CSR_PERF].times ++;
                perf_counter[INST_CSR_PERF].cycles = cycle_times - inst_start_cycle;
                perf_counter[INST_CSR_PERF].total_cycles += perf_counter[INST_CSR_PERF].cycles;
                perf_counter[INST_CSR_PERF].average_cycles = perf_counter[INST_CSR_PERF].total_cycles * 1.0 / perf_counter[INST_CSR_PERF].times;
            }else if (inst_kind == 5) {
                perf_counter[INST_JUMP_PERF].times ++;
                perf_counter[INST_JUMP_PERF].cycles = cycle_times - inst_start_cycle;
                perf_counter[INST_JUMP_PERF].total_cycles += perf_counter[INST_JUMP_PERF].cycles;
                perf_counter[INST_JUMP_PERF].average_cycles = perf_counter[INST_JUMP_PERF].total_cycles * 1.0 / perf_counter[INST_JUMP_PERF].times;
            }
            break;
        default: break;
    }
}
