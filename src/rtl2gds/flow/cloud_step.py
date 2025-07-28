import logging
from pathlib import Path

from rtl2gds.chip import Chip
from rtl2gds.flow.step_wrapper import StepWrapper
from rtl2gds.global_configs import CLOUD_FLOW_STEPS, StepName

CLOUD_STEP_IO = {
    StepName.INIT: {
        "input": [
            "TOP_NAME",
            "RESULT_DIR",
            "CLK_PORT_NAME",
            "CLK_FREQ_MHZ",
        ],
        "output": [
            "None",
        ],
    },
    StepName.SYNTHESIS: {
        "input": [
            "RTL_FILE",
            "KEEP_HIERARCHY",
        ],
        "output": [
            "TIMING_CELL_STAT_RPT",
            "TIMING_CELL_COUNT_JSON",
            "GENERIC_STAT_JSON",
            "SYNTH_STAT_JSON",
            "SYNTH_CHECK_RPT",
        ],
    },
    StepName.FLOORPLAN: {
        "input": [
            "NETLIST_FILE",
            "CORE_UTIL",
            "CELL_AREA",
            "USE_FIXED_BBOX",
            "DIE_BBOX",
            "CORE_BBOX",
        ],
        "output": [
            "DESIGN_STAT_JSON",  # no
        ],
    },
    StepName.PLACEMENT: {
        "input": [
            "DEF_FILE",
            "TARGET_DENSITY",
            "TARGET_OVERFLOW",
            "MAX_ITERATIVE",
        ],
        "output": [
            "CONGESTION_MAP",
            "DESIGN_STAT_JSON",
            "TOOL_METRICS_JSON",
        ],
    },
    StepName.CTS: {
        "input": [
            "DEF_FILE",
            "MAX_FANOUT",
        ],
        "output": [
            "CLOCK_TREE_JSON",
            "TOOL_METRICS_JSON",
            "DESIGN_STAT_JSON",  # lg
        ],
    },
    StepName.ROUTING: {
        "input": [
            "DEF_FILE",
            "FAST_ROUTE",
        ],
        "output": [
            "DESIGN_STAT_JSON",
            # "TOOL_METRICS_JSON",
        ],
    },
    StepName.SIGNOFF: {
        "input": [
            "INPUT_DEF",
            "DIE_BBOX",
            "FAST_SIGNOFF",
        ],
        "output": [
            "DRC_REPORT_JSON",
            "DESIGN_STAT_JSON",  # filler
        ],
    },
    StepName.STA: {
        "input": [
            "USE_VERILOG",
            "INPUT_VERILOG",
            "INPUT_DEF",
        ],
        "output": [
            "STA_SUMMARY_JSON",
            "POWER_SUMMARY_JSON",
            "POWER_INSTANCE_CSV",
        ],
    },
}


def _check_expected_step(expect_step: str, chip_finished_step: str) -> None:
    if expect_step not in CLOUD_FLOW_STEPS:
        raise ValueError(f"Invalid step: {expect_step}")
    # check order by chip.finished_step
    if CLOUD_FLOW_STEPS.index(expect_step) < CLOUD_FLOW_STEPS.index(chip_finished_step):
        raise ValueError(f"Invalid step: {expect_step}, ")


def _check_file_exist(file_list: list[str], files: dict[str, str]):
    for file in file_list:
        if not Path(files[file]).exists():
            raise FileNotFoundError(f"File {file}: {files[file]} does not exist")


def run_synthesis(runner: StepWrapper) -> dict:
    result_files = runner.run_synthesis()
    expect_file_key = CLOUD_STEP_IO[StepName.SYNTHESIS]["output"]
    _check_file_exist(expect_file_key, result_files)
    return result_files


def run_floorplan(runner: StepWrapper) -> dict:
    result_fp = runner.run_floorplan()
    result_no = runner.run_pr_step(StepName.NETLIST_OPT)
    runner.chip.finished_step = StepName.FLOORPLAN
    result_files = {**result_fp, **result_no}
    expect_file_key = CLOUD_STEP_IO[StepName.FLOORPLAN]["output"]
    _check_file_exist(expect_file_key, result_files)
    return result_files


def run_placement(runner: StepWrapper) -> dict:
    result_files = runner.run_pr_step(StepName.PLACEMENT)
    expect_file_key = CLOUD_STEP_IO[StepName.PLACEMENT]["output"]
    _check_file_exist(expect_file_key, result_files)
    return result_files


def run_cts(runner: StepWrapper) -> dict:
    result_cts = runner.run_pr_step(StepName.CTS)
    result_lg = runner.run_pr_step(StepName.LEGALIZATION)
    runner.chip.finished_step = StepName.CTS
    result_files = {**result_cts, **result_lg}
    expect_file_key = CLOUD_STEP_IO[StepName.CTS]["output"]
    _check_file_exist(expect_file_key, result_files)
    return result_files


def run_routing(runner: StepWrapper) -> dict:
    result_files = runner.run_pr_step(StepName.ROUTING)
    expect_file_key = CLOUD_STEP_IO[StepName.ROUTING]["output"]
    _check_file_exist(expect_file_key, result_files)
    return result_files


def run_signoff(runner: StepWrapper) -> dict:
    result_fill = runner.run_pr_step(StepName.FILLER)
    result_gds = runner.run_gds()
    result_drc = runner.run_drc()
    result_files = {**result_fill, **result_gds, **result_drc}
    expect_file_key = CLOUD_STEP_IO[StepName.SIGNOFF]["output"]
    _check_file_exist(expect_file_key, result_files)
    return result_files


def run_sta_and_power(runner: StepWrapper) -> dict:
    result_files = runner.run_sta()
    expect_file_key = CLOUD_STEP_IO[StepName.STA]["output"]
    _check_file_exist(expect_file_key, result_files)
    return result_files


def run(
    chip: Chip,
    expect_step: str,
) -> dict:
    """
    Step Router for cloud api call
    - SYNTHESIS = synth + sta
    - FLOORPLAN = fp + no + sta
    - PLACEMENT = pl + sta
    - CTS       = cts + lg + sta
    - ROUTING   = rt + sta
    - SIGNOFF   = filler + sta + gds + drc
    """
    result_files = {}
    runner = StepWrapper(chip)

    _check_expected_step(expect_step, chip.finished_step)
    match expect_step:
        case StepName.SYNTHESIS:
            result_files = run_synthesis(runner)
        case StepName.FLOORPLAN:
            result_files = run_floorplan(runner)
        case StepName.PLACEMENT:
            result_files = run_placement(runner)
        case StepName.CTS:
            result_files = run_cts(runner)
        case StepName.ROUTING:
            result_files = run_routing(runner)
        case StepName.SIGNOFF:
            result_files = run_signoff(runner)
        case _:
            raise ValueError(f"Invalid step: {expect_step}")

    if (
        expect_step == StepName.FLOORPLAN
        or expect_step == StepName.PLACEMENT
        or expect_step == StepName.CTS
        or expect_step == StepName.SIGNOFF
    ):
        logging.info("Saving layout json for step %s", expect_step)
        layout_files = runner.run_save_layout_json(expect_step)
        result_files.update({"layout_files": layout_files})

    result_sta = run_sta_and_power(runner)
    result_files.update(result_sta)

    return result_files
