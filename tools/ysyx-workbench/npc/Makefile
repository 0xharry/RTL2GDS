#===============================================
#Run time parameters
#===============================================
MAX_SIM_TIME = $(MAX_SIMULATE_TIME)				# define the max simulation time
RUN_THREADS ?= 2						# define the number of threads for running NPC
# CONFIG_LOG_TRACE = $(CONFIG_LOG_TRACE)	# enable waveform trace

#===============================================
#TOP层名字: 根据工程实时更改
#===============================================
TOP_NAME = ysyxSoCFull
RTL_FILE ?= 
#===============================================
# 设置makeflag为静默执行
#===============================================
#MAKEFLAGS += --silent

#===============================================
# 创建目标文件夹
#===============================================
BUILD_DIR   = $(RESULT_DIR)/Vbuild
## ysyxSoC目录: 用于介入SoC
ysyxSOC_DIR = $(SOC_HOME)
LOG_DIR = $(RESULT_DIR)
$(shell mkdir -p $(BUILD_DIR))
#===============================================
# 编译器别名
#===============================================
CC = g++
VERILATOR = verilator
#===============================================
# 编译选项
#===============================================

## 1.添加源文件
CXXSRC = $(wildcard $(shell find ./csrc -name  *.cpp))
# VSRC = $(wildcard $(shell find ./vsrc -name *.v -or -name *.vh -or -name *.sv -or -name *.svh))
VSRC += $(wildcard $(shell find $(ysyxSOC_DIR)/perip -name *.v -or -name *.vh -or -name *.sv -or -name *.svh))
VSRC += $()

ifneq ($(RTL_FILE),)
    VSRC += $(RTL_FILE)
endif

VSRC += $(ysyxSOC_DIR)/ysyxSoCFull.v

## 2. 添加头文件路径
C_INCPATH += $(NPC_HOME)/include $(INC_PATH) \
			 $(NPC_HOME)build
C_INCFLAGS += $(addprefix -I, $(C_INCPATH))

## 3. 添加编译选项
### 添加Cflag,ldflags
VERILATOR_CFLAGS =  -CFLAGS "-MMD $(C_INCFLAGS) $(CXXFLAGS) -Ofast"
VERILATOR_CFLAGS += -CFLAGS " -DMAX_SIM_TIME=$(MAX_SIM_TIME) "
# -D$(CONFIG_LOG_TRACE) \

#VERILATOR_LDFLAGS =  -LDFLAGS "-lreadline $(LIBS) -lSDL2 -lSDL2_image -lSDL2_ttf"
VERILATOR_LDFLAGS =  -LDFLAGS "-lreadline $(LIBS) -lSDL2  "

### 指定输出文件夹
VERILATOR_FLAG = --Mdir $(BUILD_DIR)
### 添加soc rtl路径
VERILATOR_FLAG += -I$(ysyxSOC_DIR)/perip/uart16550/rtl -I$(ysyxSOC_DIR)/perip/spi/rtl
VERILATOR_FLAG += -I$(NPC_HOME)/vsrc
VERILATOR_FLAG += -I$(SOC_MUX)
VERILATOR_FLAG += -I$(SOC_MUX)/src/soc
VERILATOR_FLAG += -I$(SOC_MUX)/src/core
VERILATOR_FLAG += --cc -j `nproc` -O3  --exe --build  -Wno-DECLFILENAME --timescale "1ns/1ns" --no-timing --trace-fst $(VERILATOR_CFLAGS) $(VERILATOR_LDFLAGS) --top-module $(TOP_NAME) -I./vsrc
VERILATOR_FLAG += --threads $(RUN_THREADS)
# VERILATOR_FLAG += -no-timing
VERILATOR_FLAG += -Wno-lint --Wno-UNOPTTHREADS --autoflush


#===============================================
# Include all filelist.mk to merge file lists
#===============================================
FILELIST_MK = $(shell find ./csrc -name "filelist.mk")
include $(FILELIST_MK)


#===============================================
IMG?=
ifneq ($(IMG),)
	ELF = --elf="$(addsuffix .elf,$(basename $(IMG)))"
endif
## 3. 批处理选项
BATCH_MODE = -b

#===============================================
# 编译规则
#===============================================
CONFIG_MACRO = $(NPC_HOME)/include/config_macro.h

$(BUILD_DIR)/V$(TOP_NAME): $(SRC_AUTO_BIND) $(NVBOARD_ARCHIVE) $(VSRC) $(CXXSRC) $(CONFIG_MACRO)
	$(VERILATOR) $(VERILATOR_FLAG)  $(VSRC) $(CXXSRC) $(SRC_AUTO_BIND) > $(RESULT_DIR)/build.log 2>&1

## 2. 启动gtkwave查看仿真波形
sim:
	$(call git_commit, "sim RTL") # DO NOT REMOVE THIS LINE!!!
	@echo "Write this Makefile by your self."
	gtkwave wave.fst

## 3. 基本规则
all:  $(BUILD_DIR)/V$(TOP_NAME)

## 4. 运行NPC,当有文件更新时，自动更新

run: $(BUILD_DIR)/V$(TOP_NAME)
	$(BUILD_DIR)/V$(TOP_NAME)  $(BATCH_MODE) $(ELF) $(PORT) $(DIFF_FILE) $(IMG)

## 4. 通过gdb调试NPC
gdb:
	gdb --args $(BUILD_DIR)/V$(TOP_NAME)  $(ARGS) $(ELF) $(PORT) $(DIFF_FILE) $(IMG)


## 5. clean
.PHONY: clean  count_v
clean:
	rm -rf $(BUILD_DIR) ./wave.fst

.DEFAULT_GOAL = all
