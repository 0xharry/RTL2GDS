#===========================================================
#   report timing and power
#   the environment variables must be set:
#   - TOP_NAME        - TOOL_REPORT_DIR
#   - FOUNDRY_DIR     - IEDA_CONFIG_DIR
#   - SDC_FILE        - IEDA_TCL_SCRIPT_DIR
#   optional:
#   - USE_VERILOG     - INPUT_VERILOG
#   - INPUT_DEF       - MAX_TIMING_PATH
#===========================================================

set RESULT_DIR          "$::env(TOOL_REPORT_DIR)"

# input variables
set TOP_NAME            "$::env(TOP_NAME)"
if { [info exists ::env(MAX_TIMING_PATH)] } {
    set MAX_TIMING_PATH "$::env(MAX_TIMING_PATH)"
} else {
    set MAX_TIMING_PATH 5
}

# input files
if { [info exists ::env(USE_VERILOG)] && [string tolower $::env(USE_VERILOG)] == "true" } {
    set USE_VERILOG    true
    set INPUT_VERILOG       "$::env(INPUT_VERILOG)"
} else {
    set USE_VERILOG    false
    set INPUT_DEF           "$::env(INPUT_DEF)"
}

# script path
set IEDA_CONFIG_DIR     "$::env(IEDA_CONFIG_DIR)"
set IEDA_TCL_SCRIPT_DIR "$::env(IEDA_TCL_SCRIPT_DIR)"

# require: env(SDC_FILE), env(FOUNDRY_DIR) and optional: env(SPEF_FILE)
# to set up SDC_FILE, TECH_LEF_PATH, LEF_PATH, LIB_PATH and SPEF_FILE if exist
source $IEDA_TCL_SCRIPT_DIR/DB_script/db_path_setting.tcl

#===========================================================

set_design_workspace $RESULT_DIR

# read_liberty must come before read def
read_liberty $LIB_PATH

if { $USE_VERILOG } {
    read_netlist $INPUT_VERILOG
    link_design $TOP_NAME
} else {
    set MERGED_LEF_PATH "$TECH_LEF_PATH  $LEF_PATH"
    read_lef_def -lef $MERGED_LEF_PATH -def $INPUT_DEF
}

read_sdc  $SDC_FILE

report_timing -max_path $MAX_TIMING_PATH -json
report_power -toggle 0.1 -json
