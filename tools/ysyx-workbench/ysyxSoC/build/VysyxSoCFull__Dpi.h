// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Prototypes for DPI import and export functions.
//
// Verilator includes this file in all generated .cpp files that use DPI functions.
// Manually include this file where DPI .c import functions are declared to ensure
// the C functions match the expectations of the DPI imports.

#ifndef VERILATED_VYSYXSOCFULL__DPI_H_
#define VERILATED_VYSYXSOCFULL__DPI_H_  // guard

#include "svdpi.h"

#ifdef __cplusplus
extern "C" {
#endif


    // DPI IMPORTS
    // DPI import at /opt/rtl2gds/tools/ysyx-workbench/ysyxSoC/perip/flash/flash.v:84:30
    extern void flash_read(int addr, int* data);
    // DPI import at vsrc/ysyxSoCFull.v:5402:30
    extern void mrom_read(int raddr, int* rdata);
    // DPI import at vsrc/ysyx_22050499.v:2009:30
    extern void npc_update_pc(int addr);
    // DPI import at vsrc/ysyx_22050499.v:1835:29
    extern int pmem_read(int raddr);
    // DPI import at vsrc/ysyx_22050499.v:1836:30
    extern void pmem_write(int waddr, int wdata, char wmask);
    // DPI import at /opt/rtl2gds/tools/ysyx-workbench/ysyxSoC/perip/psram/psram.v:111:34
    extern void psram_trap();
    // DPI import at vsrc/ysyx_22050499.v:2008:30
    extern void update_perf_counter(int tags);

#ifdef __cplusplus
}
#endif

#endif  // guard
