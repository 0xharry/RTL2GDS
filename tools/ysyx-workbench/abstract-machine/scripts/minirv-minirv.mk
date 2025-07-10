include $(AM_HOME)/scripts/isa/riscv.mk
include $(AM_HOME)/scripts/platform/minirv.mk


export PATH := $(PATH):$(abspath $(AM_HOME)/tools/minirv)
CC = minirv-gcc
AS = minirv-gcc
CXX = minirv-g++

COMMON_CFLAGS += -march=rv32e_zicsr -mabi=ilp32e  # overwrite
LDFLAGS       += -melf32lriscv                    # overwrite

AM_SRCS += riscv/minirv/libgcc/div.S \
           riscv/minirv/libgcc/muldi3.S \
           riscv/minirv/libgcc/multi3.c \
           riscv/minirv/libgcc/ashldi3.c \
           riscv/minirv/libgcc/unused.c
