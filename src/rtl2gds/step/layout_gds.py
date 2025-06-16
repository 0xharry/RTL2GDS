"""
Dump layout GDS step for RTL2GDS flow.
"""

import logging
import os
import subprocess
from pathlib import Path

from klayout import lay

from rtl2gds.global_configs import (
    DEFAULT_SDC_FILE,
    ENV_TOOLS_PATH,
    R2G_PDK_DIR_IHP130,
    R2G_TOOL_DIR,
    StepName,
)
from rtl2gds.step.configs import SHELL_CMD


def save_snapshot_image(gds_file: str, img_file: str, weight: int = 800, height: int = 800):
    """
    Takes a screenshot of a GDS file and saves it as an image.
    @Reference: https://gist.github.com/sequoiap/48af5f611cca838bb1ebc3008eef3a6e

    Args:
        gds_file (str): Path to the input GDS file
        img_file (str): Path to the output image file
        weight (int, optional): Image width. Defaults to 800
        height (int, optional): Image height. Defaults to 800
    """
    # Set display configuration options
    lv = lay.LayoutView()
    lv.set_config("background-color", "#ffffff")
    lv.set_config("grid-visible", "false")
    lv.set_config("grid-show-ruler", "false")
    lv.set_config("text-visible", "false")

    # Load the GDS file
    lv.load_layout(gds_file, 0)
    lv.max_hier()

    # Event processing for delayed configuration events
    lv.timer()

    # Save the image
    lv.save_image(img_file, weight, height)


def ensure_parent_directory_exists(file_path: str) -> str:
    parent_dir = Path(file_path).parent
    parent_dir.mkdir(parents=True, exist_ok=True)
    return str(parent_dir)


def run_ieda(
    input_def: str,
    gds_file: str,
):
    """
    Run the layout GDS dump step.

    Args:
        input_def (str): Input DEF file path
        gds_file (str): Output GDS file path
        snapshot_file (str | None, optional): Output snapshot image path. Defaults to None.

    Raises:
        subprocess.CalledProcessError: If the GDS dump command fails
    """
    step_name = StepName.LAYOUT_GDS
    step_cmd = SHELL_CMD[step_name]

    result_dir = ensure_parent_directory_exists(gds_file)

    # Prepare environment variables
    step_env = {
        "INPUT_DEF": input_def,
        "RESULT_DIR": result_dir,
        "GDS_FILE": gds_file,
        "SDC_FILE": DEFAULT_SDC_FILE,
    }
    step_env.update(ENV_TOOLS_PATH)

    logging.info(
        "(step.%s) \n subprocess cmd: %s \n subprocess env: %s",
        step_name,
        step_cmd,
        step_env,
    )

    # Run GDS dump command
    try:
        ret_code = subprocess.call(step_cmd, env=step_env)
        if ret_code != 0:
            raise subprocess.CalledProcessError(ret_code, step_cmd)
    except subprocess.CalledProcessError as e:
        raise subprocess.CalledProcessError(
            e.returncode,
            e.cmd,
            output=f"GDS dump step failed with return code {e.returncode}",
        ) from e


def run_magic(
    top_name: str,
    input_def: str,
    die_bbox: str,
    gds_file: str,
):
    """
    Generates an abstract LEF file using Magic.
    """

    result_dir = ensure_parent_directory_exists(gds_file)

    # Prepare environment variables that the Tcl script will use
    pdk_stdcell_base = f"{R2G_PDK_DIR_IHP130}/ihp-sg13g2/libs.ref/sg13g2_stdcell"
    tmp_test_macro_name = "gcd"
    tmp_test_macro_gds = "/opt/rtl2gds/design_zoo/merge_result/gcd_magic.gds"
    tmp_test_macro_lef = "/opt/rtl2gds/design_zoo/gcd/gcd_results/gcd_filler.lef"
    tmp_test_macro_bbox = "0 0 108.07 108.07"
    step_env = {
        "MAGIC_SCRIPTS_DIR": f"{R2G_TOOL_DIR}/magic",
        "TECH_LEF": f"{pdk_stdcell_base}/lef/sg13g2_tech.lef",
        "CELL_GDS": f"{pdk_stdcell_base}/gds/sg13g2_stdcell.gds",
        "__MACRO_GDS": f"{tmp_test_macro_name} {tmp_test_macro_gds} {tmp_test_macro_bbox}",
        "MACRO_LEFS": tmp_test_macro_lef,
    }

    # Prepare the command-line arguments for Magic and the Tcl script
    shell_cmd = [
        "magic",
        "-noconsole",
        "-dnull",
        "-rcfile",
        f"{R2G_PDK_DIR_IHP130}/ihp-sg13g2/libs.tech/magic/ihp-sg13g2.magicrc",
        f"{R2G_TOOL_DIR}/magic/gds.tcl",
        top_name,
        die_bbox,
        input_def,
        result_dir,
        gds_file,
    ]

    full_env = os.environ.copy()
    full_env.update(step_env)

    logging.info(
        "(step.%s) \n subprocess cmd: %s \n subprocess env: %s",
        StepName.LAYOUT_GDS,
        str(shell_cmd),
        str(step_env),
    )

    try:
        e = subprocess.run(
            shell_cmd,
            check=True,
            # text=True,
            # capture_output=True,
            stdin=subprocess.DEVNULL,
            env=full_env,
        )
        if e.returncode != 0:
            raise subprocess.CalledProcessError(e, shell_cmd)
        # print("Magic stdout:", e.stdout)
        # print("Magic stderr:", e.stderr)

    except subprocess.CalledProcessError as e:
        print(f"Command '{e.cmd}' failed with signal or non-zero exit code {e.returncode}.")
        print("Magic stdout:", e.stdout)
        print("Magic stderr:", e.stderr)


def run(
    top_name: str,
    input_def: str,
    die_bbox: str,
    gds_file: str,
    snapshot_file: str | None = None,
    tool: str = "magic",
):
    """
    Run the layout GDS dump step.

    Args:
        top_name (str): Top module name
        input_def (str): Input DEF file path
        die_bbox (str): Die area bounding box (for magic)
        gds_file (str): Output GDS file path
        result_dir (str): Result directory path
        tool (str): Tool to use for GDS dump. Default is "magic".
        snapshot_file (str | None, optional): Output snapshot image path. Defaults to None.

    Returns:
        tuple: Metrics(ususally empty) and artifacts(design.gds, snapshot.png) from the GDS dump run.

    Raises:
        subprocess.CalledProcessError: If the GDS dump command fails
    """
    if tool == "magic":
        run_magic(top_name, input_def, die_bbox, gds_file)
    elif tool == "ieda":
        run_ieda(input_def, gds_file)
    elif tool == "klayout":
        raise NotImplementedError("KLayout GDS dump is not implemented yet.")
    else:
        raise ValueError(f"Unsupported GDS dump tool: {tool}")

    if snapshot_file:
        save_snapshot_image(gds_file, snapshot_file)

    metrics = {}
    artifacts = {"gds_file": gds_file}

    return metrics, artifacts


if __name__ == "__main__":
    logging.basicConfig(
        format="[%(asctime)s - %(levelname)s - %(name)s]: %(message)s",
        level=logging.INFO,
    )
    # Example usage
    # run(
    #     top_name="gcd",
    #     input_def="/opt/rtl2gds/design_zoo/gcd/gcd_results/gcd_filler.def",
    #     die_bbox="0 0 108.07 108.07",
    #     gds_file="/opt/rtl2gds/design_zoo/merge_result/gcd_magic.gds",
    #     snapshot_file="/opt/rtl2gds/design_zoo/merge_result/gcd_magic.png",
    #     tool="magic",
    # )

    run(
        top_name="top",
        input_def="/opt/rtl2gds/design_zoo/merge_result/top_macro_fp.def",
        die_bbox="0 0 2000 2000",
        gds_file="./merge_result/top_macro_fp.gds",
        snapshot_file="./merge_result/top_macro_fp.png",
        tool="magic",
    )
