#===========================================================
##   init flow config
#===========================================================
flow_init -config $::env(CONFIG_DIR)/flow_config.json

#===========================================================
##   read db config
#===========================================================
db_init -config $::env(CONFIG_DIR)/db_default_config.json -output_dir_path $::env(RESULT_DIR)

#===========================================================
##   reset data path
#===========================================================
source $::env(TCL_SCRIPT_DIR)/DB_script/db_path_setting.tcl

#===========================================================
##   reset lib
#===========================================================
source $::env(TCL_SCRIPT_DIR)/DB_script/db_init_lib.tcl

#===========================================================
##   reset sdc
#===========================================================
source $::env(TCL_SCRIPT_DIR)/DB_script/db_init_sdc.tcl

#===========================================================
##   read lef
#===========================================================
source $::env(TCL_SCRIPT_DIR)/DB_script/db_init_lef.tcl

#===========================================================
##   read def
#===========================================================
set DEFAULT_INPUT_DEF "$::env(RESULT_DIR)/iPL_lg_result.def"
def_init -path [expr {[info exists ::env(INPUT_DEF)] ? $::env(INPUT_DEF) : $DEFAULT_INPUT_DEF}]

#===========================================================
##   run Router
#===========================================================
init_rt -temp_directory_path "$::env(RESULT_DIR)/rt/" \
        -bottom_routing_layer "met1" \
        -top_routing_layer "met4" \
        -thread_number 16

run_rt

# init_sta -output $::env(RESULT_DIR)/rt/sta/
# report_timing -stage "dr"
feature_tool -path $::env(RESULT_DIR)/feature/irt.json -step route

destroy_rt

#===========================================================
##   save def & netlist
#===========================================================
set DEFAULT_OUTPUT_DEF "$::env(RESULT_DIR)/iRT_result.def"
def_save -path [expr {[info exists ::env(OUTPUT_DEF)] ? $::env(OUTPUT_DEF) : $DEFAULT_OUTPUT_DEF}]

#===========================================================
##   save netlist 
#===========================================================
# netlist_save -path $::env(RESULT_DIR)/iRT_result.v -exclude_cell_names {}

#===========================================================
##   report db summary
#===========================================================
report_db -path "$::env(RESULT_DIR)/report/rt_db.rpt"

feature_summary -path $::env(RESULT_DIR)/feature/summary_irt.json -step route

#===========================================================
##   Exit 
#===========================================================
flow_exit
