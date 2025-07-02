"""
Floorplan step implementation using iEDA-iFP
"""

import json
import logging
import subprocess

from rtl2gds.global_configs import ENV_TOOLS_PATH, StepName
from rtl2gds.step.configs import SHELL_CMD


def run(
    top_name: str,
    result_dir: str,
    sdc_file: str,
    input_netlist: str,
    output_def: str,
    die_bbox: str,
    core_bbox: str,
    clk_port_name: str,
    clk_freq_mhz: float,
):
    """
    Run floorplan step using iEDA-iFP.

    Args:
        design_path (DesignPath): Design paths including netlist and DEF files
        design_constrain (DesignConstrain): Design timing and area constraints

    Returns:
        metrics (dict): Updated environment variables
        artifacts (dict): Expected artifacts from the step

    Raises:
        subprocess.CalledProcessError: If floorplan fails
    """
    shell_cmd = SHELL_CMD[StepName.FLOORPLAN]

    artifacts = {
        "def": output_def,
        "design_stat_text": f"{result_dir}/report/floorplan_stat.rpt",
        "design_stat_json": f"{result_dir}/report/floorplan_stat.json",
        "timing_eval_report": f"{result_dir}/evaluation/{StepName.FLOORPLAN}",
    }

    # Prepare environment variables
    shell_env = {
        "TOP_NAME": top_name,
        "RESULT_DIR": result_dir,
        "SDC_FILE": sdc_file,
        "NETLIST_FILE": input_netlist,
        "OUTPUT_DEF": output_def,
        "DIE_AREA": die_bbox,
        "CORE_AREA": core_bbox,
        "DESIGN_STAT_TEXT": artifacts["design_stat_text"],
        "DESIGN_STAT_JSON": artifacts["design_stat_json"],
        "DESIGN_EVAL_REPORT": artifacts["timing_eval_report"],
        "CLK_PORT_NAME": clk_port_name,
        "CLK_FREQ_MHZ": str(clk_freq_mhz),
        "ROUTING_TYPE": "HPWL",
    }

    logging.info(
        "(step.%s) \n subprocess cmd: %s \n subprocess env: %s",
        StepName.FLOORPLAN,
        str(shell_cmd),
        str(shell_env),
    )

    shell_env.update(ENV_TOOLS_PATH)
    ret_code = subprocess.call(shell_cmd, env=shell_env)
    if ret_code != 0:
        raise subprocess.CalledProcessError(ret_code, shell_cmd)

    # collect results
    with open(
        artifacts["design_stat_json"],
        "r",
        encoding="utf-8",
    ) as f:
        summary = json.load(f)
        die_width = float(summary["Design Layout"]["die_bounding_width"])
        die_height = float(summary["Design Layout"]["die_bounding_height"])
        core_width = float(summary["Design Layout"]["core_bounding_width"])
        core_height = float(summary["Design Layout"]["core_bounding_height"])

        core_area = float(summary["Design Layout"]["core_area"])
        core_util = float(summary["Design Layout"]["core_usage"])
        die_area = float(summary["Design Layout"]["die_area"])
        die_util = float(summary["Design Layout"]["die_usage"])
        cell_area = float(summary["Instances"]["total"]["area"])
        num_instances = int(summary["Design Statis"]["num_instances"])

        margin_width = float(die_width - core_width) / 2
        margin_height = float(die_height - core_height) / 2

        # @TODO: collect core_bbox from summary.json
        # core_lower_left_x = summary["Design Layout"]["core_lower_left_x"]
        # core_lower_left_y = summary["Design Layout"]["core_lower_left_y"]
        # core_upper_right_x = summary["Design Layout"]["core_upper_right_x"]
        # core_upper_right_y = summary["Design Layout"]["core_upper_right_y"]
        # {"core_bbox": f"{core_lower_left_x} {core_lower_left_y} {core_upper_right_x} {core_upper_right_y}"}

    metrics = {
        "die_bbox": f"0 0 {die_width} {die_height}",
        "core_bbox": f"{margin_width} {margin_height} {margin_width+core_width} {margin_height+core_height}",
        "core_area": core_area,
        "core_util": core_util,
        "die_area": die_area,
        "die_util": die_util,
        "cell_area": cell_area,
        "num_instances": num_instances,
    }

    return metrics, artifacts


# if __name__ == "__main__":
#     logging.basicConfig(
#         format="[%(asctime)s - %(levelname)s - %(name)s]: %(message)s",
#         level=logging.INFO,
#     )

#     logging.info("Testing floorplan...")

#     # Setup test design
#     TEST_DESIGN_TOP = "aes_cipher_top"
#     RESULT_DIR = "./results"
#     INPUT_NETLIST = "./results/aes_netlist.v"
#     OUTPUT_DEF = "./results/aes_fp.def"

#     from ..design_constrain import DesignConstrain
#     from ..design_path import DesignPath
#     from ..global_configs import DEFAULT_SDC_FILE

#     test_path = DesignPath(
#         rtl_file="",
#         sdc_file=DEFAULT_SDC_FILE,
#         netlist_file=INPUT_NETLIST,
#         def_file=OUTPUT_DEF,
#         result_dir=RESULT_DIR,
#     )

#     test_constrain = DesignConstrain(
#         clk_port_name="",
#         clk_freq_mhz="",
#         die_area="0 0 700 700",
#         core_area="10 10 690 690",
#     )

#     env = run(
#         top_name=TEST_DESIGN_TOP,
#         design_path=test_path,
#         design_constrain=test_constrain,
#     )

#     import os

#     assert os.path.exists(OUTPUT_DEF)
#     logging.info("Generated def: %s", env["OUTPUT_DEF"])
#     logging.info("env: %s", env)
