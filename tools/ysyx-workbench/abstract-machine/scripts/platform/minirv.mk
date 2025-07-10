AM_SRCS := riscv/minirv/start.S \
           riscv/minirv/trm.c \
           riscv/minirv/ioe.c \
           riscv/minirv/timer.c \
           riscv/minirv/input.c \
           riscv/minirv/cte.c \
           riscv/minirv/trap.S \
           platform/dummy/vme.c \
           platform/dummy/mpe.c

CFLAGS    += -fdata-sections -ffunction-sections
LDSCRIPTS += $(AM_HOME)/scripts/ysyxsoc_linker.ld
# LDSCRIPTS += $(AM_HOME)/scripts/linker.ld
LDFLAGS   += --defsym=_pmem_start=0x30000000 --defsym=_entry_offset=0x0 --print-map > map.txt
LDFLAGS   += --gc-sections -e _start

MAINARGS_MAX_LEN = 64
MAINARGS_PLACEHOLDER = the_insert-arg_rule_in_Makefile_will_insert_mainargs_here
CFLAGS += -DMAINARGS_MAX_LEN=$(MAINARGS_MAX_LEN) -DMAINARGS_PLACEHOLDER=$(MAINARGS_PLACEHOLDER)

insert-arg: image
	@python3 $(AM_HOME)/tools/insert-arg.py $(IMAGE).bin $(MAINARGS_MAX_LEN) $(MAINARGS_PLACEHOLDER) "$(mainargs)"

image: image-dep
	@$(OBJDUMP) -d $(IMAGE).elf > $(IMAGE).txt
	@echo + OBJCOPY "->" $(IMAGE_REL).bin
	@$(OBJCOPY) -S --set-section-flags .bss=alloc,contents -O binary $(IMAGE).elf $(IMAGE).bin

run: insert-arg
	@echo $(NPC_HOME) $(ISA) $(IMAGE).bin $(RESULT_DIR)
	@if [ "$(NAME)" = "coremark" ] || [ "$(NAME)" = "dhrystone" ] || [ "$(NAME)" = "microbench" ]; then \
        $(MAKE) -C $(NPC_HOME) ISA=$(ISA) run IMG=$(IMAGE).bin > $(RESULT_DIR)/$(TOP_NAME)_$(NAME).log 2>&1; \
    else \
        $(MAKE) -C $(NPC_HOME) ISA=$(ISA) run IMG=$(IMAGE).bin; \
    fi

.PHONY: insert-arg
