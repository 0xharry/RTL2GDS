set dont_use_cells "sg13g2_dfrbp_1"

set top_design              "$::env(TOP_NAME)"
set clk_freq_mhz            "$::env(CLK_FREQ_MHZ)"
set verilog_files           "$::env(RTL_FILE)"
set pdk_dir                 "$::env(FOUNDRY_DIR)"
set final_netlist_file      "$::env(NETLIST_FILE)"
set timing_cell_stat_rpt    "$::env(TIMING_CELL_STAT_RPT)"
set timing_cell_count_rpt   "$::env(TIMING_CELL_COUNT_RPT)"
set generic_stat_json       "$::env(GENERIC_STAT_JSON)"
set synth_stat_json         "$::env(SYNTH_STAT_JSON)"
set synth_check_rpt         "$::env(SYNTH_CHECK_RPT)"
set keep_hierarchy          [string tolower "$::env(KEEP_HIERARCHY)"]

set tmp_dir        "$::env(RESULT_DIR)/tmp"

set clk_period_ps  [expr 1000000.0 / ${clk_freq_mhz}]

file mkdir $tmp_dir
set stat_dir [file dirname $synth_stat_json]
if {![file isdirectory $stat_dir]} {
    file mkdir $stat_dir
}