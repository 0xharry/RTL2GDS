from pathlib import Path
import json

from rtl2gds import step
from rtl2gds.chip import Chip
from rtl2gds.global_configs import DEFAULT_SDC_FILE, RTL2GDS_FLOW_STEPS, StepName
from rtl2gds.utils import process
from rtl2gds.utils.time import save_execute_time_data

from rtl2gds.step import step_abc


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
        self.step_counter = 1
        self.timing_setup = {
            "SDC_FILE": DEFAULT_SDC_FILE,
            "CLK_PORT_NAME": self.chip.constrain.clk_port_name,
            "CLK_FREQ_MHZ": str(self.chip.constrain.clk_freq_mhz),
        }

    def _check_expected_step(self, step_name: str) -> None:
        expected_step = get_expected_step(self.chip.finished_step)
        if expected_step != step_name:
            raise ValueError(f"Expected step: {expected_step}, but got: {step_name}")

    def run_synthesis(self) -> dict:
        """Run synthesis step"""
        step_name = StepName.SYNTHESIS
        self._check_expected_step(step_name)

        # @TODO: temporarily migrate from synthesis.py, need to be refactored
        from rtl2gds.step.synthesis import parse_synth_stat, _calculate_areas, _convert_sv_to_v

        rtl_file = _convert_sv_to_v(
            self.chip.path_setting.rtl_file, self.chip.path_setting.result_dir, self.chip.top_name
        )
        if isinstance(rtl_file, list):
            # check if all files exist
            for rtl in rtl_file:
                if not Path(rtl).exists():
                    raise FileNotFoundError(f"File {rtl} does not exist")
            rtl_file = " \n ".join(rtl_file)
        #############################################

        synth_step = step_abc.Step(step_name)
        synth_parameters = {
            "RTL_FILE": rtl_file,
            "RESULT_DIR": self.chip.path_setting.result_dir,
            "CLK_FREQ_MHZ": self.chip.constrain.clk_freq_mhz,
            "TOP_NAME": self.chip.top_name,
        }
        _, step_reproducible, _ = synth_step.run(
            parameters=synth_parameters,
            output_prefix=f"{self.step_counter:02d}",
        )
        self.step_counter += 1

        # @TODO: temporarily migrate from synthesis.py, need to be refactored
        stats = parse_synth_stat(step_reproducible["output_files"]["SYNTH_STAT_JSON"])
        cell_area = stats["cell_area"]
        assert 0 < cell_area
        MAX_CELL_AREA = 1_000_000
        if cell_area > MAX_CELL_AREA:
            raise ValueError(f"Cell area ({cell_area}) exceeds RTL2GDS limit ({MAX_CELL_AREA})")
        die_bbox, core_bbox, core_util = _calculate_areas(
            cell_area,
            self.chip.constrain.core_util,
            self.chip.constrain.die_bbox,
            self.chip.constrain.core_bbox,
        )
        #############################################
        self.chip.path_setting.netlist_file = step_reproducible["output_files"]["NETLIST_FILE"]

        self.chip.constrain.die_bbox = die_bbox
        self.chip.constrain.core_bbox = core_bbox
        self.chip.constrain.core_util = core_util

        self.chip.metrics.num_instances = stats["num_cells"]
        self.chip.metrics.area.cell = cell_area
        self.chip.metrics.area.core_util = core_util

        self.chip.finished_step = step_name
        self.chip.expected_step = get_expected_step(step_name)

        self.chip.update2config()
        self.chip.dump_config_yaml(
            config_yaml=Path(
                f"{self.chip.path_setting.result_dir}/{self.chip.top_name}_{step_name}.yaml"
            )
        )

        return step_reproducible["output_files"]

    def run_floorplan(self) -> dict:
        """Run floorplan step"""
        step_name = StepName.FLOORPLAN
        self._check_expected_step(step_name)

        fp_step = step_abc.Step(step_name)
        fp_parameters = {
            "NETLIST_FILE": self.chip.path_setting.netlist_file,
            "TOP_NAME": self.chip.top_name,
            "DIE_BBOX": self.chip.constrain.die_bbox,
            "CORE_BBOX": self.chip.constrain.core_bbox,
            "RESULT_DIR": self.chip.path_setting.result_dir,
        }
        fp_parameters.update(self.timing_setup)
        _, step_reproducible, _ = fp_step.run(
            parameters=fp_parameters,
            output_prefix=f"{self.step_counter:02d}",
        )
        self.step_counter += 1

        self.chip.path_setting.def_file = step_reproducible["output_files"]["OUTPUT_DEF"]

        # @TODO: migrate from floorplan.py
        with open(
            step_reproducible["output_files"]["DESIGN_STAT_JSON"],
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

        self.chip.constrain.die_bbox = f"0 0 {die_width} {die_height}"
        self.chip.constrain.core_bbox = (
            f"{margin_width} {margin_height} {margin_width+core_width} {margin_height+core_height}"
        )
        self.chip.constrain.core_util = core_util

        self.chip.metrics.area.die = die_area
        self.chip.metrics.area.core = core_area

        self.chip.metrics.area.cell = cell_area
        self.chip.metrics.area.die_util = die_util
        self.chip.metrics.area.core_util = core_util
        self.chip.metrics.num_instances = num_instances

        self.chip.finished_step = step_name
        self.chip.expected_step = get_expected_step(step_name)

        self.chip.update2config()
        self.chip.dump_config_yaml(
            config_yaml=Path(
                f"{self.chip.path_setting.result_dir}/{self.chip.top_name}_{step_name}.yaml"
            )
        )

        return step_reproducible["output_files"]

    pr_step_map = {
        StepName.NETLIST_OPT: step_abc.Step(StepName.NETLIST_OPT),
        StepName.PLACEMENT: step_abc.Step(StepName.PLACEMENT),
        StepName.CTS: step_abc.Step(StepName.CTS),
        StepName.LEGALIZATION: step_abc.Step(StepName.LEGALIZATION),
        StepName.ROUTING: step_abc.Step(StepName.ROUTING),
        StepName.FILLER: step_abc.Step(StepName.FILLER),
    }

    def run_pr_step(self, step_name: str) -> dict:
        """Run a specific place & route step"""
        self._check_expected_step(step_name)

        step_obj = StepWrapper.pr_step_map.get(step_name)
        if not step_obj:
            raise ValueError(f"Unknown PR step: {step_name}")

        step_parameters = {
            "INPUT_DEF": self.chip.path_setting.def_file,
            "TOP_NAME": self.chip.top_name,
            "RESULT_DIR": self.chip.path_setting.result_dir,
        }
        step_parameters.update(self.timing_setup)
        _, step_reproducible, _ = step_obj.run(
            parameters=step_parameters,
            output_prefix=f"{self.step_counter:02d}",
        )
        self.step_counter += 1

        self.chip.path_setting.def_file = step_reproducible["output_files"]["OUTPUT_DEF"]

        self.chip.finished_step = step_name
        self.chip.expected_step = get_expected_step(step_name)

        # @TODO: migrate from step.py
        with open(
            step_reproducible["output_files"]["DESIGN_STAT_JSON"],
            "r",
            encoding="utf-8",
        ) as f:
            summary = json.load(f)
            self.chip.metrics.area.core_util = float(summary["Design Layout"]["core_usage"])
            self.chip.metrics.area.die_util = float(summary["Design Layout"]["die_usage"])
            self.chip.metrics.area.cell = float(summary["Instances"]["total"]["area"])
            self.chip.metrics.num_instances = int(summary["Design Statis"]["num_instances"])

        self.chip.update2config()
        self.chip.dump_config_yaml(
            config_yaml=Path(
                f"{self.chip.path_setting.result_dir}/{self.chip.top_name}_{step_name}.yaml"
            )
        )

        return step_reproducible["output_files"]

    def run_save_layout_gds(self, step_name: str, take_snapshot: bool = False) -> dict:
        """Run dump layout GDS step"""
        gds_file = f"{self.chip.path_setting.result_dir}/{self.chip.top_name}_{step_name}.gds"
        snapshot_file = f"{self.chip.path_setting.result_dir}/{self.chip.top_name}_{step_name}.png"

        step.layout_gds.run(
            top_name=self.chip.top_name,
            input_def=self.chip.path_setting.def_file,
            die_area_bbox=self.chip.constrain.die_bbox,
            gds_file=gds_file,
            snapshot_file=snapshot_file if take_snapshot else None,
            tool="magic",
        )

        self.chip.path_setting.gds_file = gds_file

        self.chip.update2config()
        self.chip.dump_config_yaml(
            config_yaml=Path(
                f"{self.chip.path_setting.result_dir}/{self.chip.top_name}_{step_name}_gds.yaml"
            )
        )

        if take_snapshot:
            return dict({"gds_file": gds_file, "snapshot_file": snapshot_file})
        else:
            return dict({"gds_file": gds_file})

    def run_collect_timing_metrics(self) -> dict:
        """Run collect timing metrics step"""

        output_file = f"{self.chip.path_setting.result_dir}/{self.chip.top_name}.timing.json"
        process.merge_timing_reports(
            result_dir=f"{self.chip.path_setting.result_dir}",
            log_path=f"{self.chip.path_setting.result_dir}/{self.chip.top_name}.log",
        )

        return dict({output_file: output_file})

    def save_execute_time_report(self) -> str:
        """Save execute time report"""
        return save_execute_time_data(self.chip.path_setting.result_dir, self.chip.top_name)

    def save_merged_metrics(self, execute_time_json: str):
        """Merge and save the metrics from execution time and timing reports"""
        from ..utils import time as time_utils

        return time_utils.save_merged_metrics(self.chip, execute_time_json=execute_time_json)
