import json
import os
import logging
from datetime import datetime
from typing import Callable
from .json_helper import load_json, dump_json

# Save all step timing data in a global dictionary
time_data = {
    "steps": {},
    "summary": {"total_time": 0, "start_time": "", "end_time": ""},
}


def time_decorator(func: Callable) -> Callable:
    """
    Record the time taken by a function and store it in a global dictionary.
    Args:
        func (Callable): The function to be decorated.
    Returns:
        Callable: The wrapped function with timing functionality.
    """

    import time
    import functools

    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if len(args) > 0 and isinstance(args[0], str):
            step_name = args[0]
        elif "step_name" in kwargs:
            step_name = kwargs["step_name"]
        else:
            step_name = func.__name__.replace("run_", "")

        # Record the start time
        start_time = time.perf_counter()
        start_datetime = datetime.now().isoformat()

        try:
            result = func(self, *args, **kwargs)
            status = "success"
        except Exception as e:
            status = f"failed: {str(e)}"
            raise
        finally:
            # Record the end time
            end_time = time.perf_counter()
            end_datetime = datetime.now().isoformat()
            elapsed = end_time - start_time

            # Record the timing data
            time_data["steps"][step_name] = {
                "start_time": start_datetime,
                "end_time": end_datetime,
                "elapsed_seconds": elapsed,
                "status": status,
            }

            # If it's the first step, record the total start time
            if not time_data["summary"]["start_time"]:
                time_data["summary"]["start_time"] = start_datetime

            # Update the total time
            time_data["summary"]["end_time"] = end_datetime
            time_data["summary"]["total_time"] += elapsed

        # Lazy import to avoid circular dependency
        from ..evaluation.timing import timing_eval

        # TODO: Can we merge the execution time data with the timing evaluation data?
        try:
            chip = self.chip
            if hasattr(chip.path_setting, "def_file") and os.path.exists(
                chip.path_setting.def_file
            ):
                timing_eval(
                    step_name=step_name,
                    top_name=self.chip.top_name,
                    result_dir=self.chip.path_setting.result_dir,
                    sdc_file=self.chip.path_setting.sdc_file,
                    input_netlist=self.chip.path_setting.netlist_file,
                    input_def=self.chip.path_setting.def_file,
                    route_type="HPWL",  # TODO: make this configurable
                    clock_freq=str(self.chip.constrain.clk_freq_mhz),
                )
                logging.info(f"Finished {step_name}")
        except Exception as e:
            logging.error(f"Error during timing evaluation for {step_name}: {str(e)}")
        return result

    return wrapper


def save_execute_time_data(result_dir: str, chip_name: str) -> str:
    """
    Save the execution time data to a JSON file.
    Args:
        result_dir (str): Directory to save the JSON file.
        chip_name (str): Name of the chip.
    Returns:
        str: Path to the saved JSON file.
    """
    os.makedirs(result_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_file = os.path.join(
        result_dir, f"evaluation/{chip_name}_execution_time_{timestamp}.json"
    )
    dump_json(json_file=json_file, data=time_data)
    return json_file


from src.rtl2gds.chip import Chip


def save_merged_metrics(chip: Chip, execute_time_json: str):
    """
    Merge and save the metrics from different steps into a single JSON file.

    Args:
        chip: Chip object containing the design and metrics information.
        execute_time_json: Path to the JSON file containing execution time data.

    Returns:
        str: Saved path of the merged metrics JSON file.
    """
    import json
    import os
    import time

    # Define the paths for the merged report and other reports
    merged_report_path = f"{chip.path_setting.result_dir}/evaluation/final_metrics.json"
    timing_report_path = (
        f"{chip.path_setting.result_dir}/evaluation/timing/timing_report.json"
    )
    execute_time_report_path = execute_time_json

    # Ensure the directory exists
    os.makedirs(os.path.dirname(merged_report_path), exist_ok=True)

    merged_data = {
        "design": {
            "top_name": chip.top_name,
            "finished_step": chip.finished_step,
            "completed_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        },
        "steps": {},
        "metrics": {},
    }

    # Load execution time data
    logging.info(f"Merge metrics {execute_time_report_path}")
    exec_time_data = load_json(execute_time_json)

    # Load timing data
    logging.info(f"Merge metrics {timing_report_path}")
    timing_data = load_json(timing_report_path)

    merged_data["summary"] = exec_time_data.get("summary", {})

    # Merge metrics from different steps
    for step_name, step_exec_time in exec_time_data.get("steps", {}).items():
        if step_name not in merged_data["steps"]:
            merged_data["steps"][step_name] = {}
            logging.info(f"Step {step_name} not found in merged data, adding it.")

        # Add execution time data
        merged_data["steps"][step_name]["execution_time"] = step_exec_time

        # Add timing data
        if step_name in timing_data:
            merged_data["steps"][step_name]["timing"] = timing_data.get(step_name, {})

    dump_json(merged_report_path, merged_data)

    logging.info(f"Merged metrics saved to: {merged_report_path}")
    return merged_report_path
