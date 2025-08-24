#!/bin/bash

# RTL2GDS Metrics Collection Script
# Usage: ./collect_metrics.sh [output_file.csv]
# If no output file is specified, defaults to rtl2gds_metrics.csv

declare -A step_mapping=(
    ["00_synthesis"]="synthesis"
    ["01_floorplan"]="floorplan"
    ["02_netlist_opt"]="netlist_opt"
    ["03_placement"]="placement"
    ["04_cts"]="cts"
    ["05_to"]="to"
    ["06_legalization"]="legalization"
    ["07_routing"]="routing"
    ["08_filler"]="filler"
    ["09_sta"]="sta"
)

# Define the order of steps
step_order=("synthesis" "floorplan" "netlist_opt" "placement" "cts" "to" "legalization" "routing" "filler" "sta")

function collect_design_data() {
    local design_name=$1
    local dir_prefix="design_zoo" # set your base directory here
    local results_dir="$dir_prefix/$design_name/results"
    
    if [ ! -d "$results_dir" ]; then
        echo "No results directory found for $design_name, skipping." >&2
        return
    fi
    
    echo "Collecting metrics for $design_name" >&2
    
    declare -A step_times
    
    for dir in "$results_dir"/??_*_"$design_name"/; do
        if [ -d "$dir" ]; then
            local dir_name=$(basename "$dir")
            local step_prefix=${dir_name:0:2}_${dir_name:3}
            step_prefix=${step_prefix%_$design_name}
            
            local metrics_file="$dir/metrics.json"
            if [ -f "$metrics_file" ]; then
                local elapsed_time=$(jq -r '.elapsed_time' "$metrics_file" 2>/dev/null)
                if [ "$elapsed_time" != "null" ] && [ "$elapsed_time" != "" ]; then
                    local step_name=${step_mapping[$step_prefix]}
                    if [ "$step_name" ]; then
                        step_times[$step_name]=$(printf "%.2f" "$elapsed_time")
                    fi
                fi
            fi
        fi
    done
    
    # Construct output line
    local output_line="$design_name"
    for step in "${step_order[@]}"; do
        if [ "${step_times[$step]}" ]; then
            output_line="$output_line,${step_times[$step]}"
        else
            output_line="$output_line,"
        fi
    done
    
    echo "$output_line"
}

function collect_all_designs() {
    local output_file=${1:-"rtl2gds_metrics.csv"}
    
    # Init CSV header
    echo "design_name,synthesis,floorplan,netlist_opt,placement,cts,to,legalization,routing,filler,sta" > "$output_file"
    
    local designs=("aes" "gcd" "picorv32a")
    
    for design in "${designs[@]}"; do
        local result=$(collect_design_data "$design")
        if [ -n "$result" ]; then
            echo "$result" >> "$output_file"
        fi
    done
    
    echo "Metrics collected and saved to: $output_file" >&2
}

function main() {
    # Check if jq is installed
    if ! command -v jq &> /dev/null; then
        echo "Error: jq is required but not installed." >&2
        exit 1
    fi
    
    if [ "$#" -gt 1 ] || [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
        echo "Collect RTL2GDS metrics for predefined designs." >&2
        echo "Design: aes, gcd, picorv32a" >&2
        echo "Usage: collect-metrics [output_file.csv]" >&2
        exit 1
    fi

    # acquire output file name, default to rtl2gds_metrics.csv
    local output_file=${1:-"rtl2gds_metrics.csv"}
    
    collect_all_designs "$output_file"
}

# If the script is run directly, execute main
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi