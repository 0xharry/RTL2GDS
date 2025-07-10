// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design internal header
// See VysyxSoCFull.h for the primary calling header

#ifndef VERILATED_VYSYXSOCFULL___024UNIT_H_
#define VERILATED_VYSYXSOCFULL___024UNIT_H_  // guard

#include "verilated.h"
#include "verilated_threads.h"


class VysyxSoCFull__Syms;

class alignas(VL_CACHE_LINE_BYTES) VysyxSoCFull___024unit final : public VerilatedModule {
  public:

    // INTERNAL VARIABLES
    VysyxSoCFull__Syms* const vlSymsp;

    // CONSTRUCTORS
    VysyxSoCFull___024unit(VysyxSoCFull__Syms* symsp, const char* v__name);
    ~VysyxSoCFull___024unit();
    VL_UNCOPYABLE(VysyxSoCFull___024unit);

    // INTERNAL METHODS
    void __Vconfigure(bool first);
};


#endif  // guard
