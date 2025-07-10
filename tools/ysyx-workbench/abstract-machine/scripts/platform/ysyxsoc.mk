AM_SRCS := riscv/ysyxsoc/start.S \
           riscv/ysyxsoc/trm.c \
           riscv/ysyxsoc/ioe.c \
           riscv/ysyxsoc/timer.c \
           riscv/ysyxsoc/input.c \
           riscv/ysyxsoc/uart.c \
           riscv/ysyxsoc/gpu.c \
           riscv/ysyxsoc/cte.c \
           riscv/ysyxsoc/trap.S \
           platform/dummy/vme.c \
           platform/dummy/mpe.c

CFLAGS    += -fdata-sections -ffunction-sections
LDFLAGS   += -T $(AM_HOME)/scripts/ysyxsoc_linker.ld \
						 --defsym=_pmem_start=0x30000000 --defsym=_entry_offset=0x0 --print-map > map.txt
LDFLAGS   += --gc-sections -e _start
CFLAGS += -DMAINARGS=\"$(mainargs)\"
.PHONY: $(AM_HOME)/am/src/riscv/ysyxsoc/trm.c

image: $(IMAGE).elf
	@$(OBJDUMP) -d $(IMAGE).elf > $(IMAGE).txt
	@echo + OBJCOPY "->" $(IMAGE_REL).bin
	@$(OBJCOPY) -S --set-section-flags .bss=alloc,contents -O binary $(IMAGE).elf $(IMAGE).bin

run: image
	@echo $(NPC_HOME) $(ISA) $(IMAGE).bin $(RESULT_DIR)
	@if [ "$(NAME)" = "coremark" ] || [ "$(NAME)" = "dhrystone" ] || [ "$(NAME)" = "microbench" ]; then \
		$(MAKE) -C $(NPC_HOME) ISA=$(ISA) run IMG=$(IMAGE).bin > $(RESULT_DIR)/$(TOP_NAME)_$(NAME).log 2>&1; \
	else \
		$(MAKE) -C $(NPC_HOME) ISA=$(ISA) run IMG=$(IMAGE).bin; \
	fi

#gdb: image
    #$(MAKE) -C $(NPC_HOME) ISA=$(ISA) gdb  IMG=$(IMAGE).bin
