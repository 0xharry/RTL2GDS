.PHONY: all run gdb clean latest $(ALL)

RESULT_DIR ?= .
RESULT_FILE = $(RESULT_DIR)/.result
TMP_MAKE_DIR = $(RESULT_DIR)/.makefiles
$(shell mkdir -p $(TMP_MAKE_DIR))
$(shell > $(RESULT_FILE))

ALL = $(basename $(notdir $(shell find tests/. -name "*.c")))

PASS_FILES = $(patsubst %,$(TMP_MAKE_DIR)/%.pass,$(ALL))

all: $(PASS_FILES)
	# This target just ensures all tests run. The output is handled in 'run'.

run:
	@start_time=$$(date +%s%N); \
	$(MAKE) all > /dev/null; \
	end_time=$$(date +%s%N); \
	duration=$$(echo "scale=3; ($$end_time - $$start_time)/1000000000" | bc); \
	echo "All tests finished. Results saved to log."; \
	cat $(RESULT_FILE) | sort > $(RESULT_DIR)/$(TOP_NAME)_cpu_test.log; \
	printf "[%14s]       %ss\n" "Total Time" $$duration >> $(RESULT_DIR)/$(TOP_NAME)_cpu_test.log; \
	echo "Detailed log saved to $(RESULT_DIR)/$(TOP_NAME)_cpu_test.log"; \
	rm -f $(RESULT_FILE); \
	rm -rf $(TMP_MAKE_DIR);

$(TMP_MAKE_DIR)/%.pass: tests/%.c latest
	@echo "[ RUN      ] $*"
	@/bin/echo -e "NAME = $*\nSRCS = tests/$*.c\nBUILD_DIR = build/$*\ninclude $${AM_HOME}/Makefile" > $(TMP_MAKE_DIR)/Makefile.$*
	
	@start_time=$$(date +%s%N); \
	if make -s -f $(TMP_MAKE_DIR)/Makefile.$* ARCH=$(ARCH) run > $(TMP_MAKE_DIR)/$*.log 2>&1; then \
	    end_time=$$(date +%s%N); \
	    duration=$$(echo "scale=3; ($$end_time - $$start_time)/1000000000" | bc); \
	    printf "[%14s] PASS  %ss\n" $* $$duration >> $(RESULT_FILE); \
	    touch $@; \
	else \
	    end_time=$$(date +%s%N); \
	    duration=$$(echo "scale=3; ($$end_time - $$start_time)/1000000000" | bc); \
	    printf "[%14s] FAIL  %ss\n" $* $$duration >> $(RESULT_FILE); \
	    echo "-------------------- START OF FAIL LOG: $* --------------------"; \
	    cat $(TMP_MAKE_DIR)/$*.log; \
	    echo "--------------------  END OF FAIL LOG: $*  --------------------"; \
	fi

gdb:
	@echo "GDB must be run on a single test. Example: make gdb-add"
	@echo "Available tests for gdb: $(addprefix gdb-, $(ALL))"

.PHONY: $(addprefix gdb-, $(ALL))
$(addprefix gdb-, $(ALL)): gdb-%:
	@/bin/echo -e "NAME = $*\nSRCS = tests/$*.c\nBUILD_DIR = build/$*\ninclude $${AM_HOME}/Makefile" > $(TMP_MAKE_DIR)/Makefile.$*
	@make -f $(TMP_MAKE_DIR)/Makefile.$* ARCH=$(ARCH) gdb

clean:
	rm -rf Makefile.* build/ .result .makefiles $(RESULT_DIR)/$(TOP_NAME)_cpu_test.log

latest: