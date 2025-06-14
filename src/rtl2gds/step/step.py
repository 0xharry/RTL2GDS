"""
description: behavior of each RTL2GDS step
"""

import json
import logging
import os
import subprocess

from rtl2gds.global_configs import DEFAULT_SDC_FILE, ENV_TOOLS_PATH, StepName
from rtl2gds.step import configs


class Step:
    def __init__(self):
        self.step_name: str
        self.tool_name: str
        self.description: str
        self.shell_cmd: list
        self.filename_stat_text: str
        self.filename_stat_json: str
        self.filename_metrics_json: str = None
        self.dirname_tool_report: str = None

    def run(
        self,
        top_name: str,
        input_def: str,
        result_dir: str,
        output_def: str,
        output_verilog: str,
        clk_port_name: str,
        clk_freq_mhz: float,
    ):
        assert os.path.exists(input_def)

        artifacts = {
            "def": output_def,
            "verilog": output_verilog,
            "design_stat_text": f"{result_dir}/{self.filename_stat_text}",
            "design_stat_json": f"{result_dir}/{self.filename_stat_json}",
            "timing_eval_report": f"{result_dir}/evaluation/{self.step_name}",
        }

        shell_env = {
            "TOP_NAME": top_name,
            "INPUT_DEF": input_def,
            "OUTPUT_DEF": artifacts["def"],
            "OUTPUT_VERILOG": artifacts["verilog"],
            "DESIGN_STAT_TEXT": artifacts["design_stat_text"],
            "DESIGN_STAT_JSON": artifacts["design_stat_json"],
            "DESIGN_EVAL_REPORT": artifacts["timing_eval_report"],
            "RESULT_DIR": result_dir,
            "SDC_FILE": DEFAULT_SDC_FILE,
            "CLK_PORT_NAME": clk_port_name,
            "CLK_FREQ_MHZ": str(clk_freq_mhz),
            "ROUTING_TYPE": "HPWL",
        }

        if self.filename_metrics_json:
            artifacts["tool_metrics_json"] = f"{result_dir}/{self.filename_metrics_json}"
            shell_env["TOOL_METRICS_JSON"] = artifacts["tool_metrics_json"]

        if self.dirname_tool_report:
            artifacts["tool_report_dir"] = f"{result_dir}/{self.dirname_tool_report}"
            shell_env["TOOL_REPORT_DIR"] = artifacts["tool_report_dir"]

        logging.info(
            "(step.%s) \n subprocess cmd: %s \n subprocess env: %s",
            self.step_name,
            str(self.shell_cmd),
            str(shell_env),
        )

        shell_env.update(ENV_TOOLS_PATH)

        from rtl2gds.utils.time import end_step_timer, start_step_timer

        start_datetime, start_time, timer_step_name = start_step_timer(step_name=self.step_name)
        try:
            ret_code = subprocess.call(self.shell_cmd, env=shell_env)
            if ret_code != 0:
                raise subprocess.CalledProcessError(ret_code, self.shell_cmd)
        except subprocess.CalledProcessError as e:
            raise subprocess.CalledProcessError(
                e.returncode,
                e.cmd,
                output=f"Step {self.step_name} failed with return code {e.returncode}",
            ) from e

        end_step_timer(
            start_datetime=start_datetime,
            start_time=start_time,
            step_name=timer_step_name,
        )

        # iterate through artifacts and check if they exist
        for key, value in artifacts.items():
            if not os.path.exists(value):
                raise FileNotFoundError(
                    f"Step({self.step_name}) Expected artifact {key} not found: {value}"
                )

        # collect results
        with open(
            artifacts["design_stat_json"],
            "r",
            encoding="utf-8",
        ) as f:
            summary = json.load(f)
            metrics = {
                "core_util": float(summary["Design Layout"]["core_usage"]),
                "die_util": float(summary["Design Layout"]["die_usage"]),
                "cell_area": float(summary["Instances"]["total"]["area"]),
                "num_instances": int(summary["Design Statis"]["num_instances"]),
            }

        return metrics, artifacts


class NetlistOpt(Step):
    def __init__(self):
        super().__init__()
        self.step_name = StepName.NETLIST_OPT
        self.tool_name = "iEDA-iNO"
        self.description = "Fixing fanout by iEDA-iNO"
        self.shell_cmd = configs.SHELL_CMD[self.step_name]
        self.filename_stat_text = f"report/{self.step_name}_stat.rpt"
        self.filename_stat_json = f"report/{self.step_name}_stat.json"
        self.filename_metrics_json = f"metrics/{self.tool_name}_{self.step_name}.json"


class Placement(Step):
    def __init__(self):
        super().__init__()
        self.step_name = StepName.PLACEMENT
        self.tool_name = "iEDA-iPL"
        self.description = "Standard Cell Placement by iEDA-iPL"
        self.shell_cmd = configs.SHELL_CMD[self.step_name]
        self.filename_stat_text = f"report/{self.step_name}_stat.rpt"
        self.filename_stat_json = f"report/{self.step_name}_stat.json"
        self.filename_metrics_json = f"metrics/{self.tool_name}_{self.step_name}.json"
        self.dirname_tool_report = f"report/{self.tool_name}/"


class CTS(Step):
    def __init__(self):
        super().__init__()
        self.step_name = StepName.CTS
        self.tool_name = "iEDA-iCTS"
        self.description = "Clock Tree Synthesis by iEDA-iCTS"
        self.shell_cmd = configs.SHELL_CMD[self.step_name]
        self.filename_stat_text = f"report/{self.step_name}_stat.rpt"
        self.filename_stat_json = f"report/{self.step_name}_stat.json"
        self.filename_metrics_json = f"metrics/{self.tool_name}_{self.step_name}.json"
        self.dirname_tool_report = f"report/{self.tool_name}/"


class DrvOpt(Step):
    def __init__(self):
        super().__init__()
        self.step_name = StepName.DRV_OPT
        self.tool_name = "iEDA-iTO"
        self.description = "Optimization Design Rule Voilation by iEDA-iTO"
        self.shell_cmd = configs.SHELL_CMD[self.step_name]
        self.filename_stat_text = f"report/{self.step_name}_stat.rpt"
        self.filename_stat_json = f"report/{self.step_name}_stat.json"
        self.filename_metrics_json = f"metrics/{self.tool_name}_{self.step_name}.json"


class HoldOpt(Step):
    def __init__(self):
        super().__init__()
        self.step_name = StepName.HOLD_OPT
        self.tool_name = "iEDA-iTO"
        self.description = "Optimization Hold Time Voilation by iEDA-iTO"
        self.shell_cmd = configs.SHELL_CMD[self.step_name]
        self.filename_stat_text = f"report/{self.step_name}_stat.rpt"
        self.filename_stat_json = f"report/{self.step_name}_stat.json"
        self.filename_metrics_json = f"metrics/{self.tool_name}_{self.step_name}.json"


class Legalization(Step):
    def __init__(self):
        super().__init__()
        self.step_name = StepName.LEGALIZATION
        self.tool_name = "iEDA-iPL"
        self.description = "Incremental legalization for new cells by iEDA-iPL"
        self.shell_cmd = configs.SHELL_CMD[self.step_name]
        self.filename_stat_text = f"report/{self.step_name}_stat.rpt"
        self.filename_stat_json = f"report/{self.step_name}_stat.json"


class Routing(Step):
    def __init__(self):
        super().__init__()
        self.step_name = StepName.ROUTING
        self.tool_name = "iEDA-iRT"
        self.description = "Routing by iEDA-iRT"
        self.shell_cmd = configs.SHELL_CMD[self.step_name]
        self.filename_stat_text = f"report/{self.step_name}_stat.rpt"
        self.filename_stat_json = f"report/{self.step_name}_stat.json"
        self.filename_metrics_json = f"metrics/{self.tool_name}_{self.step_name}.json"
        self.dirname_tool_report = f"report/{self.tool_name}/"


class Filler(Step):
    def __init__(self):
        super().__init__()
        self.step_name = StepName.FILLER
        self.description = "Adding Filler for DFM by iEDA-iPL"
        self.shell_cmd = configs.SHELL_CMD[self.step_name]
        self.filename_stat_text = f"report/{self.step_name}_stat.rpt"
        self.filename_stat_json = f"report/{self.step_name}_stat.json"
