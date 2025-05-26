import os

from .. import step
from ..chip import Chip
from ..global_configs import RTL2GDS_FLOW_STEPS, StepName
from ..utils import process
from ..utils.time import time_decorator, save_execute_time_data


def get_expected_step(finished_step: str) -> str | None:
    """Get the expected step for the rtl2gds flow"""
    if finished_step == RTL2GDS_FLOW_STEPS[-1]:
        return None
    return RTL2GDS_FLOW_STEPS[RTL2GDS_FLOW_STEPS.index(finished_step) + 1]


class StepWrapper:
    """
    translate the chip constrains/metrics to step io parameters
    return step metrics file
    """

    def __init__(self, chip: Chip):
        self.chip = chip

    def _check_expected_step(self, step_name: str) -> None:
        expected_step = get_expected_step(self.chip.finished_step)
        if expected_step != step_name:
            raise ValueError(f"Expected step: {expected_step}, but got: {step_name}")

    @time_decorator
    def run_synthesis(self) -> dict:
        """Run synthesis step"""
        step_name = StepName.SYNTHESIS
        self._check_expected_step(step_name)

        metrics, artifacts = step.synthesis.run(
            top_name      = self.chip.top_name,
            rtl_file      = self.chip.path_setting.rtl_file,
            netlist_file  = self.chip.path_setting.netlist_file,
            sdc_file      = self.chip.path_setting.sdc_file,
            result_dir    = self.chip.path_setting.result_dir,
            clk_port_name = self.chip.constrain.clk_port_name,
            clk_freq_mhz  = self.chip.constrain.clk_freq_mhz,
            die_bbox      = self.chip.constrain.die_bbox,
            core_bbox     = self.chip.constrain.core_bbox,
            core_util     = self.chip.constrain.core_util,
        )

        self.chip.constrain.die_bbox = metrics["die_bbox"]
        self.chip.constrain.core_bbox = metrics["core_bbox"]
        self.chip.constrain.core_util = metrics["core_util"]

        self.chip.metrics.num_instances = metrics["total_cells"]
        self.chip.metrics.area.cell = metrics["cell_area"]
        self.chip.metrics.area.core_util = metrics["core_util"]

        self.chip.finished_step = step_name
        self.chip.expected_step = get_expected_step(step_name)

        self.chip.update2config()

        return artifacts

    @time_decorator
    def run_floorplan(self) -> dict:
        """Run floorplan step"""
        step_name = StepName.FLOORPLAN
        self._check_expected_step(step_name)
        # Create metrics directory (iEDA issue workaround)
        os.makedirs(f"{self.chip.path_setting.result_dir}/metrics", exist_ok=True)

        output_def = f"{self.chip.path_setting.result_dir}/{self.chip.top_name}_{step_name}.def"
        self.chip.path_setting.def_file = output_def

        metrics, artifacts = step.floorplan.run(
            top_name      = self.chip.top_name,
            result_dir    = self.chip.path_setting.result_dir,
            sdc_file      = self.chip.path_setting.sdc_file,
            input_netlist = self.chip.path_setting.netlist_file,
            output_def    = self.chip.path_setting.def_file,
            die_bbox      = self.chip.constrain.die_bbox,
            core_bbox     = self.chip.constrain.core_bbox,
        )

        self.chip.constrain.die_bbox = metrics["die_bbox"]
        self.chip.constrain.core_bbox = metrics["core_bbox"]
        self.chip.constrain.core_util = metrics["core_util"]

        self.chip.metrics.area.die = metrics["die_area"]
        self.chip.metrics.area.core = metrics["core_area"]

        self.chip.metrics.area.cell = metrics["cell_area"]
        self.chip.metrics.area.die_util = metrics["die_util"]
        self.chip.metrics.area.core_util = metrics["core_util"]
        self.chip.metrics.num_instances = metrics["num_instances"]

        self.chip.finished_step = step_name
        self.chip.expected_step = get_expected_step(step_name)

        self.chip.update2config()

        return artifacts

    @time_decorator
    def run_pr_step(self, step_name: str) -> dict:
        """Run a specific place & route step"""
        self._check_expected_step(step_name)

        step_obj = step.pr_step_map.get(step_name)
        if not step_obj:
            raise ValueError(f"Unknown PR step: {step_name}")

        step_file_prefix = f"{self.chip.path_setting.result_dir}/{self.chip.top_name}_{step_name}"
        output_def = f"{step_file_prefix}.def"
        output_verilog = f"{step_file_prefix}.v"
        # Create metrics directory (iEDA issue workaround)
        os.makedirs(f"{self.chip.path_setting.result_dir}/metrics", exist_ok=True)

        metrics, artifacts = step_obj.run(
            top_name       = self.chip.top_name,
            input_def      = self.chip.path_setting.def_file,
            result_dir     = self.chip.path_setting.result_dir,
            output_def     = output_def,
            output_verilog = output_verilog,
            clk_port_name  = self.chip.constrain.clk_port_name,
            clk_freq_mhz   = self.chip.constrain.clk_freq_mhz,
        )

        self.chip.path_setting.def_file = output_def

        self.chip.finished_step = step_name
        self.chip.expected_step = get_expected_step(step_name)

        self.chip.metrics.area.cell = metrics["cell_area"]
        self.chip.metrics.area.die_util = metrics["die_util"]
        self.chip.metrics.area.core_util = metrics["core_util"]
        self.chip.metrics.num_instances = metrics["num_instances"]

        self.chip.update2config()

        return artifacts

    @time_decorator
    def run_dump_layout_gds(self, step_name: str, take_snapshot: bool = False) -> dict:
        """Run dump layout GDS step"""
        gds_file = f"{self.chip.path_setting.result_dir}/{self.chip.top_name}_{step_name}.gds"
        snapshot_file = f"{self.chip.path_setting.result_dir}/{self.chip.top_name}_{step_name}.png"

        step.layout_gds.run(
            input_def     = self.chip.path_setting.def_file,
            gds_file      = gds_file,
            result_dir    = self.chip.path_setting.result_dir,
            snapshot_file = snapshot_file if take_snapshot else None,
        )

        self.chip.path_setting.gds_file = gds_file

        self.chip.update2config()

        if take_snapshot:
            return dict({"gds_file": gds_file, "snapshot_file": snapshot_file})
        else:
            return dict({"gds_file": gds_file})

    def run_collect_timing_metrics(
        self
    ) -> dict:
        """Run collect timing metrics step"""

        output_file = f"{self.chip.path_setting.result_dir}/{self.chip.top_name}.timing.json"
        process.merge_timing_reports(
            result_dir=f"{self.chip.path_setting.result_dir}",
            log_path=f"{self.chip.path_setting.result_dir}/{self.chip.top_name}.log",
        )

        return dict({output_file: output_file})

    def save_execute_time_report(self) -> str:
        """Save execute time report"""
        return save_execute_time_data(
            self.chip.path_setting.result_dir,
            self.chip.top_name
        )

    def save_merged_metrics(self, execute_time_json: str):
        """Merge and save the metrics from execution time and timing reports"""
        from ..utils import time as time_utils

        return time_utils.save_merged_metrics(self.chip, execute_time_json=execute_time_json)
