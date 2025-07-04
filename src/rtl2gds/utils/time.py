import logging
import os
from datetime import datetime

from .json_helper import dump_json, load_json

# Save all step timing data in a global dictionary
time_data = {
    "steps": {},
    "summary": {"total_time": 0, "start_time": "", "end_time": ""},
}


def start_step_timer(step_name: str):
    """
    Start a timer for a specific step and return the start time and datetime.
    Args:
        step_name (str): Name of the step to start timing for.
    Returns:
        tuple: A tuple containing the start datetime, start time, and step name.
    Raises:
        ValueError: If step_name is not provided.
    """
    import time

    if step_name is None or step_name == "":
        raise ValueError("step_name must be provided and cannot be empty")

    start_time = time.perf_counter()
    start_datetime = datetime.now().isoformat()

    return start_datetime, start_time, step_name


def end_step_timer(start_datetime: str, start_time: float, step_name: str):
    """
    End the timer for a specific step and record the elapsed time.
    Args:
        start_datetime (str): Start datetime of the step.
        start_time (float): Start time in seconds.
        step_name (str): Name of the step to end timing for.
    Raises:
        ValueError: If step_name is not provided.
    """
    import time

    end_time = time.perf_counter()
    end_datetime = datetime.now().isoformat()
    elapsed = end_time - start_time

    # Record the timing data
    time_data["steps"][step_name] = {
        "start_time": start_datetime,
        "end_time": end_datetime,
        "elapsed_seconds": elapsed,
    }

    # If it's the first step, record the total start time
    if not time_data["summary"]["start_time"]:
        time_data["summary"]["start_time"] = start_datetime
    # Update the total time
    time_data["summary"]["end_time"] = end_datetime
    time_data["summary"]["total_time"] += elapsed


def save_execute_time_data(result_dir: str, chip_name: str) -> str:
    """
    Save the execution time data to a JSON file.
    Args:
        result_dir (str): Directory to save the JSON file.
        chip_name (str): Name of the chip.
    Returns:
        str: Path to the saved JSON file.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_file = os.path.join(result_dir, f"evaluation/{chip_name}_execution_time_{timestamp}.json")
    os.makedirs(os.path.dirname(json_file), exist_ok=True)
    dump_json(json_file=json_file, data=time_data)
    return json_file


from rtl2gds.chip import Chip


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
    timing_report_path = f"{chip.path_setting.result_dir}/evaluation/timing_report.json"
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
    logging.info("Merge metrics %s", execute_time_report_path)
    exec_time_data = load_json(execute_time_json)

    # # Load timing data
    # logging.info("Merge metrics %s", timing_report_path)
    # timing_data = load_json(timing_report_path)

    merged_data["summary"] = exec_time_data.get("summary", {})

    # Merge metrics from different steps
    for step_name, step_exec_time in exec_time_data.get("steps", {}).items():
        if step_name not in merged_data["steps"]:
            merged_data["steps"][step_name] = {}
            logging.info("Step %s not found in merged data, adding it.", step_name)

        # Add execution time data
        merged_data["steps"][step_name]["execution_time"] = step_exec_time

        # # Add timing data
        # if step_name in timing_data:
        #     merged_data["steps"][step_name]["timing"] = timing_data.get(step_name, {})

    dump_json(merged_report_path, merged_data)

    logging.info("Merged metrics saved to: %s", merged_report_path)
    return merged_report_path
