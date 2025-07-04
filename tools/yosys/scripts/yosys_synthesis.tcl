# Copyright (c) 2022 ETH Zurich and University of Bologna.
# Licensed under the Apache License, Version 2.0, see LICENSE for details.
# SPDX-License-Identifier: Apache-2.0
#
# Authors:
# - Philippe Sauter <phsauter@iis.ee.ethz.ch>

# This flows assumes it is beign executed in the yosys/ directory
# but just to be sure, we go there
if {[info script] ne ""} {
    cd "[file dirname [info script]]/../"
}
source global_var.tcl

# process ABC script and write to temporary directory
proc processAbcScript {abc_script} {
    global tmp_dir
    set src_dir [file join [file dirname [info script]] ../src]
    set abc_out_path $tmp_dir/[file tail $abc_script]

    set raw [read -nonewline [open $abc_script r]]
    set abc_script_recaig [string map -nocase [list "{REC_AIG}" [subst "$src_dir/lazy_man_synth_library.aig"]] $raw]
    set abc_out [open $abc_out_path w]
    puts -nonewline $abc_out $abc_script_recaig

    flush $abc_out
    close $abc_out
    return $abc_out_path
}

# read liberty files and prepare some variables
source scripts/init_tech.tcl

yosys plugin -i slang
yosys read_slang $verilog_files --top $top_design \
        --compat-mode --keep-hierarchy \
        --allow-use-before-declare --ignore-unknown-modules

# -----------------------------------------------------------------------------
# this section heavily borrows from the yosys synth command:
# synth - check
yosys hierarchy -top $top_design
yosys check
yosys proc

# synth - coarse:
# similar to yosys synth -run coarse -noalumacc
yosys opt_expr
yosys opt -noff
yosys fsm
yosys wreduce 
yosys peepopt
yosys opt_clean
yosys opt -full
yosys booth
yosys share
yosys opt
yosys memory -nomap
yosys memory_map
yosys opt -fast

yosys opt_dff -sat -nodffe -nosdff
yosys share
yosys opt -full
yosys clean -purge

yosys techmap
yosys opt -fast
yosys clean -purge

yosys tee -q -o "${generic_stat_json}" stat -json -tech cmos
# yosys tee -q -o "${generic_stat_json}.rpt" stat -tech cmos
# -----------------------------------------------------------------------------
if {$keep_hierarchy == "false"} {
    yosys flatten
    yosys clean -purge
}

# -----------------------------------------------------------------------------
# Preserve flip-flop names as far as possible
# split internal nets
yosys splitnets -format __v
# rename DFFs from the driven signal
yosys rename -wire -suffix _reg_p t:*DFF*_P*
yosys rename -wire -suffix _reg_n t:*DFF*_N*
# rename all other cells
yosys autoname t:*DFF* %n
yosys clean -purge

yosys select -write ${timing_cell_stat_rpt} t:*DFF*
yosys tee -q -o ${timing_cell_count_rpt} select -count t:*DFF*_P*
yosys tee -q -a ${timing_cell_count_rpt} select -count t:*DFF*_N*
yosys tee -q -a ${timing_cell_count_rpt} select -count */t:*_DLATCH*_ */t:*_SR*_

# yosys tee -q -o "${generic_stat_json}" stat -json -tech cmos
# yosys tee -q -o "${generic_stat_json}.rpt" stat -tech cmos
# -----------------------------------------------------------------------------
# mapping to technology

# set don't use cells
set dfflibmap_args ""
foreach cell $dont_use_cells {
    lappend dfflibmap_args -dont_use $cell
}
# first map flip-flops
yosys dfflibmap {*}$tech_cells_args {*}$dfflibmap_args

# then perform bit-level optimization and mapping on all combinational clouds in ABC
# pre-process abc file (written to tmp directory)
set abc_comb_script   [processAbcScript scripts/abc-opt.script]
# call ABC
yosys abc {*}$tech_cells_args -D $clk_period_ps -script $abc_comb_script -constr src/abc.constr -showtmp

yosys clean -purge


# -----------------------------------------------------------------------------
# prep for openROAD
# yosys write_verilog -norename -noexpr -attr2comment ${tmp_dir}/${top_design}_yosys_debug.v

# yosys splitnets -driver
yosys splitnets -ports
yosys setundef -zero
yosys clean -purge
# map constants to tie cells
yosys hilomap -singleton -hicell {*}$tech_cell_tiehi -locell {*}$tech_cell_tielo

# final reports
yosys tee -q -o "${synth_stat_json}" stat -json {*}$liberty_args
# yosys tee -q -o "${synth_stat_json}.rpt" stat {*}$liberty_args
yosys tee -q -o "${synth_check_rpt}" check

# final netlist
yosys write_verilog -noattr -noexpr -nohex -nodec ${final_netlist_file}
