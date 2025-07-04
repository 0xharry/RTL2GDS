"""
Synthesis step implementation using yosys
"""

import json
import logging
import math
import os
import subprocess
import tempfile

from rtl2gds.global_configs import ENV_TOOLS_PATH, StepName
from rtl2gds.step.configs import SHELL_CMD

MAX_CELL_AREA = 1_000_000


def generate_filelist(
    sv_files: list[str], output_file: str, incdirs: list[str] = None, defines: list[str] = None
):
    """
    Generate a filelist for a Verilog toolchain.

    Args:
        sv_files (list[str]): List of SystemVerilog source file paths.
        output_file (str): Path to the output filelist.
        incdirs (list[str], optional): List of include directories.
        defines (list[str], optional): List of Verilog defines ("NAME" or "NAME=VALUE").
    """
    incdirs = incdirs or []
    defines = defines or []
    with open(output_file, "w", encoding="utf-8") as f:
        for incdir in incdirs:
            f.write(f"+incdir+{incdir}\n")
        for define in defines:
            if "=" in define:
                name, value = define.split("=", 1)
                f.write(f"+define+{name}={value}\n")
            else:
                f.write(f"+define+{define}\n")
        for sv_file in sv_files:
            f.write(f"{sv_file}\n")


def convert_sv_to_filelist(sv_files: str | list[str], output_filelist: str):
    """
    Convert a list of SystemVerilog files to a filelist for Yosys-slang.
    """
    if isinstance(sv_files, str) and sv_files.endswith(".sv"):
        sv_files = [sv_files]
    elif isinstance(sv_files, list) and not any(sv_file.endswith(".sv") for sv_file in sv_files):
        return

    generate_filelist(sv_files, output_filelist)


def save_module_preview(
    verilog_file,
    output_svg=None,
    module_name=None,
    flatten=False,
    aig=False,
    skin_file=None,
):
    """
    Export a Verilog to an SVG diagram preview using **Yosys** and **netlistsvg**.

    Args:
        verilog_file (str): Path to the input Verilog file
        output_svg (str, optional): Path to the output SVG file. Defaults to input filename or module_name with .svg extension.
        module_name (str, optional): Name of the top module. If None, Yosys will auto-detect.
        flatten (bool, optional): If True, flatten the design to basic logic gates. Defaults to False.
        aig (bool, optional): If True, convert to AND-inverter graph representation. Defaults to False.
        skin_file (str, optional): Path to a custom skin file for netlistsvg. Defaults to None.

    Returns:
        str: Path to the generated SVG file

    Raises:
        FileNotFoundError: If the input Verilog file doesn't exist
        subprocess.CalledProcessError: If Yosys or netlistsvg commands fail
    """
    # Check if input file exists
    if not os.path.isfile(verilog_file):
        raise FileNotFoundError(f"Input Verilog file not found: {verilog_file}")

    # Set default output SVG filename if not provided
    if output_svg is None:
        base_name = os.path.splitext(verilog_file)[0] if module_name is None else module_name
        output_svg = f"{base_name}.svg"

    # Create a temporary JSON file
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_json:
        json_file = temp_json.name

    try:
        # Construct Yosys command
        yosys_cmd = ["yosys", "-p"]

        # Build the prep command
        prep_cmd = "prep"
        if module_name:
            prep_cmd += f" -top {module_name}"
        if flatten:
            prep_cmd += " -flatten"

        # Complete Yosys command
        if aig:
            yosys_cmd_str = f"{prep_cmd}; aigmap; write_json {json_file}"
        else:
            yosys_cmd_str = f"{prep_cmd}; write_json {json_file}"

        yosys_cmd.append(yosys_cmd_str)
        yosys_cmd.append(verilog_file)

        # Run Yosys
        # https://github.com/nturley/netlistsvg/blob/master/README.md#generating-input_json_file-with-yosys
        # yosys -p "prep -top my_top_module; write_json output.json" input.v
        # yosys -p "prep -top my_top_module -flatten; write_json output.json" input.v
        # yosys -p "prep -top my_top_module; aigmap; write_json output.json" input.v
        logging.info(f"Running Yosys: {' '.join(yosys_cmd)}")
        subprocess.run(yosys_cmd, check=True, env=ENV_TOOLS_PATH)

        # Construct netlistsvg command
        netlistsvg_cmd = ["netlistsvg", json_file, "-o", output_svg]
        if skin_file:
            netlistsvg_cmd.extend(["--skin", skin_file])

        # Run netlistsvg
        # netlistsvg input_json_file [-o output_svg_file] [--skin skin_file]
        logging.info(f"Running netlistsvg: {' '.join(netlistsvg_cmd)}")
        subprocess.run(netlistsvg_cmd, check=True)

        logging.info(f"SVG diagram generated successfully: {output_svg}")
        return output_svg

    finally:
        # Clean up temporary JSON file
        if os.path.exists(json_file):
            os.remove(json_file)


def parse_synth_stat(synth_stat_json: str):
    """Extract top module area and name from yosys report and simplify cell names"""
    stats = {
        "num_cells": 0,
        "cell_area": 0.0,
        "sequential_ratio": 0.0,
        "cell_types": {},
    }
    # cell_prefix = "sg13g2_"
    # cell_prefix_match_pattern = f"     {cell_prefix}"

    with open(
        synth_stat_json,
        "r",
        encoding="utf-8",
    ) as f:
        summary = json.load(f)
        # logging.debug(summary)
        stats["num_cells"] = int(summary["design"]["num_cells"])
        stats["cell_area"] = float(summary["design"]["area"])

    return stats


def _calculate_areas(cell_area, core_util, die_bbox=None, core_bbox=None):
    """Calculate die and core areas based on synthesis statistics.

    Args:
        stats (dict): Synthesis statistics from Yosys
        core_util (float): Core utilization percentage
        die_bbox (str, optional): Die area coordinates. Defaults to None
        core_bbox (str, optional): Core area coordinates. Defaults to None

    Returns:
        tuple: (die_bbox, core_bbox, core_util)
    """
    if not (die_bbox and core_bbox):
        core_length = math.sqrt(cell_area / core_util)
        io_margin = 10
        die_bbox = f"0 0 {core_length+io_margin*2} {core_length+io_margin*2}"
        core_bbox = f"{io_margin} {io_margin} {core_length+io_margin} {core_length+io_margin}"

    elif not core_util:
        core = core_bbox.split(" ")
        core_len_x = float(core[2]) - float(core[0])
        core_len_y = float(core[3]) - float(core[1])
        core_area = core_len_x * core_len_y
        core_util = cell_area / core_area
        assert 0 < core_util < 1, "Core utilization out of range"

    return die_bbox, core_bbox, core_util


def run(
    top_name: str,
    rtl_file: str | list[str],
    netlist_file: str,
    result_dir: str,
    clk_freq_mhz: str,
    die_bbox: str | None = None,
    core_bbox: str | None = None,
    core_util: float | None = None,
):
    """Run synthesis step using Yosys.

    Args:
        top_name (str): Name of the top-level module
        rtl_file (str | list[str]): Path(s) to the input RTL file(s)
        netlist_file (str): Path to the output netlist file
        result_dir (str): Directory to store synthesis results
        clk_freq_mhz (str): Clock frequency in MHz
        die_bbox (str, optional): Die area coordinates. Defaults to None
        core_bbox (str, optional): Core area coordinates. Defaults to None
        core_util (float, optional): Core utilization percentage. Defaults to None

    Returns:
        dict: Dictionary containing synthesis results including:
            - DIE_AREA: Die area coordinates
            - CORE_AREA: Core area coordinates
            - CORE_UTIL: Core utilization percentage
            - NUM_CELLS: Total number of cells
            - CELL_AREA: Total cell area
            - CELL_TYPES: Dictionary of cell types and their counts

    Raises:
        subprocess.CalledProcessError: If synthesis fails
        AssertionError: If required parameters are missing or invalid
        RuntimeError: If SystemVerilog conversion fails
    """
    # Convert SystemVerilog files if necessary and also check RTL file existence
    result_dir = os.path.abspath(result_dir)
    netlist_file = os.path.abspath(netlist_file)
    rtl_file = _check_v(rtl_file)

    # flatten rtl_file if it is a list (pass ENV var to yosys.tcl)
    if isinstance(rtl_file, list):
        rtl_file = " \n ".join(rtl_file)

    step_cmd = SHELL_CMD[StepName.SYNTHESIS]

    # Setup Yosys report directory
    yosys_report_dir = f"{result_dir}/report"
    os.makedirs(yosys_report_dir, exist_ok=True)

    artifacts = {
        "synth_stat_json": f"{yosys_report_dir}/synth_stat.json",
        "synth_check_txt": f"{yosys_report_dir}/synth_check.txt",
        "netlist": netlist_file,
    }

    # Setup environment variables
    step_env = _setup_step_env(
        top_name,
        rtl_file,
        netlist_file,
        artifacts["synth_stat_json"],
        artifacts["synth_check_txt"],
        clk_freq_mhz,
        result_dir,
    )

    # Run synthesis
    logging.info(
        "(step.%s) \n subprocess cmd: %s \n subprocess env: %s",
        StepName.SYNTHESIS,
        str(step_cmd),
        step_env,
    )

    ret_code = subprocess.call(step_cmd, env=step_env)
    if ret_code != 0:
        raise subprocess.CalledProcessError(ret_code, step_cmd)

    # collect results
    synth_stat = artifacts["synth_stat_json"]
    assert os.path.exists(synth_stat), "Synthesis statistic file not found"
    assert os.path.exists(netlist_file), "Netlist file not found"

    stats = parse_synth_stat(synth_stat)
    cell_area = stats["cell_area"]
    assert 0 < cell_area
    assert (
        cell_area < MAX_CELL_AREA
    ), f"Cell area ({cell_area}) exceeds processing limit ({MAX_CELL_AREA})"

    # Calculate areas
    die_bbox, core_bbox, core_util = _calculate_areas(cell_area, core_util, die_bbox, core_bbox)

    metrics = {
        "die_bbox": die_bbox,
        "core_bbox": core_bbox,
        "core_util": core_util,
        "num_cells": stats["num_cells"],
        "cell_area": cell_area,
    }

    return metrics, artifacts


if __name__ == "__main__":
    logging.basicConfig(
        format="[%(asctime)s - %(levelname)s - %(name)s]: %(message)s",
        level=logging.INFO,
    )

    logging.info("Testing synthesis...")

    # Setup test design
    aes_top = "aes_cipher_top"
    aes_rtl = [
        "/opt/rtl2gds/design_zoo/aes/aes_cipher_top.v",
        "/opt/rtl2gds/design_zoo/aes/aes_inv_cipher_top.v",
        "/opt/rtl2gds/design_zoo/aes/aes_inv_sbox.v",
        "/opt/rtl2gds/design_zoo/aes/aes_key_expand_128.v",
        "/opt/rtl2gds/design_zoo/aes/aes_rcon.v",
        "/opt/rtl2gds/design_zoo/aes/aes_sbox.v",
        "/opt/rtl2gds/design_zoo/aes/timescale.v",
    ]

    kianv_top = "tt_um_kianV_rv32ima_uLinux_SoC"
    kianv_rtl = [
        "/home/user/demo/KianV-RV32IMA-RISC-V-uLinux-SoC/src/spi.v",
        "/home/user/demo/KianV-RV32IMA-RISC-V-uLinux-SoC/src/divider.v",
        "/home/user/demo/KianV-RV32IMA-RISC-V-uLinux-SoC/src/rx_uart.v",
        "/home/user/demo/KianV-RV32IMA-RISC-V-uLinux-SoC/src/defines_soc.vh",
        "/home/user/demo/KianV-RV32IMA-RISC-V-uLinux-SoC/src/csr_exception_handler.v",
        "/home/user/demo/KianV-RV32IMA-RISC-V-uLinux-SoC/src/riscv_defines.vh",
        "/home/user/demo/KianV-RV32IMA-RISC-V-uLinux-SoC/src/rv32_amo_opcodes.vh",
        "/home/user/demo/KianV-RV32IMA-RISC-V-uLinux-SoC/src/design_elements.v",
        "/home/user/demo/KianV-RV32IMA-RISC-V-uLinux-SoC/src/fifo.v",
        "/home/user/demo/KianV-RV32IMA-RISC-V-uLinux-SoC/src/mcause.vh",
        "/home/user/demo/KianV-RV32IMA-RISC-V-uLinux-SoC/src/soc.v",
        "/home/user/demo/KianV-RV32IMA-RISC-V-uLinux-SoC/src/alu_decoder.v",
        "/home/user/demo/KianV-RV32IMA-RISC-V-uLinux-SoC/src/datapath_unit.v",
        "/home/user/demo/KianV-RV32IMA-RISC-V-uLinux-SoC/src/extend.v",
        "/home/user/demo/KianV-RV32IMA-RISC-V-uLinux-SoC/src/load_alignment.v",
        "/home/user/demo/KianV-RV32IMA-RISC-V-uLinux-SoC/src/alu.v",
        "/home/user/demo/KianV-RV32IMA-RISC-V-uLinux-SoC/src/csr_utilities.vh",
        "/home/user/demo/KianV-RV32IMA-RISC-V-uLinux-SoC/src/qqspi.v",
        "/home/user/demo/KianV-RV32IMA-RISC-V-uLinux-SoC/src/load_decoder.v",
        "/home/user/demo/KianV-RV32IMA-RISC-V-uLinux-SoC/src/riscv_priv_csr_status.vh",
        "/home/user/demo/KianV-RV32IMA-RISC-V-uLinux-SoC/src/multiplier_decoder.v",
        "/home/user/demo/KianV-RV32IMA-RISC-V-uLinux-SoC/src/csr_decoder.v",
        "/home/user/demo/KianV-RV32IMA-RISC-V-uLinux-SoC/src/clint.v",
        "/home/user/demo/KianV-RV32IMA-RISC-V-uLinux-SoC/src/register_file.v",
        "/home/user/demo/KianV-RV32IMA-RISC-V-uLinux-SoC/src/misa.vh",
        "/home/user/demo/KianV-RV32IMA-RISC-V-uLinux-SoC/src/tx_uart.v",
        "/home/user/demo/KianV-RV32IMA-RISC-V-uLinux-SoC/src/tt_um_kianV_rv32ima_uLinux_SoC.v",
        "/home/user/demo/KianV-RV32IMA-RISC-V-uLinux-SoC/src/main_fsm.v",
        "/home/user/demo/KianV-RV32IMA-RISC-V-uLinux-SoC/src/divider_decoder.v",
        "/home/user/demo/KianV-RV32IMA-RISC-V-uLinux-SoC/src/multiplier_extension_decoder.v",
        "/home/user/demo/KianV-RV32IMA-RISC-V-uLinux-SoC/src/multiplier.v",
        "/home/user/demo/KianV-RV32IMA-RISC-V-uLinux-SoC/src/store_alignment.v",
        "/home/user/demo/KianV-RV32IMA-RISC-V-uLinux-SoC/src/store_decoder.v",
        "/home/user/demo/KianV-RV32IMA-RISC-V-uLinux-SoC/src/control_unit.v",
        "/home/user/demo/KianV-RV32IMA-RISC-V-uLinux-SoC/src/kianv_harris_mc_edition.v",
    ]

    RESULT_DIR = "./results"
    OUTPUT_NETLIST = "./results/netlist.v"

    import shutil

    shutil.rmtree(RESULT_DIR, ignore_errors=True)
    os.makedirs(RESULT_DIR, exist_ok=True)

    metrics, artifacts = run(
        top_name="picorv32a",
        rtl_file="/opt/rtl2gds/design_zoo/picorv32a/picorv32a.v",
        netlist_file=OUTPUT_NETLIST,
        result_dir=RESULT_DIR,
        clk_freq_mhz=100,
        core_util=0.5,
    )

    logging.info("Synthesis completed successfully")
    logging.info("Generated netlist: %s", artifacts["netlist"])
    logging.info("Die area: %s", metrics["die_bbox"])
    logging.info("Core area: %s", metrics["core_bbox"])
    logging.info("metrics: %s", str(metrics))
    logging.info("artifacts: %s", str(artifacts))
