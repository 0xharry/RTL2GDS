import os
import json
import subprocess
import logging


def replace_one(text, item):
    """
    Replace a placeholder in the text with a value.
    Args:
        text (str): The text to process.
        item (tuple): A tuple containing the placeholder and the value to replace it with.
    Returns:
        str: The processed text with the placeholder replaced by the value.
    """
    placeholder, value = item
    return text.replace(placeholder, value)


def cmd_run(shell_cmd: list, shell_env: dict, period_name: str, log_path: str):
    """
    Process the shell command and log the output.
    Args:
        shell_cmd (list): The shell command to run.
        shell_env (dict): The environment variables for the shell command.
        period_name (str): The name of the period for logging.
        log_path (str): The path to the log file.
    Raises:
        subprocess.CalledProcessError: If the shell command fails.
    """
    try:
        timing_output_path = f"{log_path}"
        with open(timing_output_path, "w", encoding="utf-8") as output_file:
            process = subprocess.Popen(
                shell_cmd,
                env=shell_env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
            )

            for line in process.stdout:
                print(line, end="")
                output_file.write(line)

            stderr_content = process.stderr.read()
            if stderr_content:
                logging.error("(%s) \n stderr: %s", period_name, stderr_content)
                output_file.write(stderr_content)

            ret_code = process.wait()

            if ret_code != 0:
                logging.error("(%s) \n stderr: %s", period_name, stderr_content)
                raise subprocess.CalledProcessError(ret_code, shell_cmd)

        logging.info(
            f"The output of the command has been saved to: {timing_output_path}"
        )

    except Exception as e:
        logging.error(f"Error command: {shell_cmd}, Error: {e}")
        raise


def merge_timing_reports(result_dir: str, log_path: str, output_file: str = None):
    """
    Merge timing reports from multiple files into a single file.
    Args:
        result_dir (str): The directory containing the timing reports.
        log_path (str): The path to the log file.
        output_file (str, optional): The path to the output file. If None, a default name will be used.
    Raises:
        FileNotFoundError: If the timing evaluation directory does not exist.
    Returns:
        dict: A dictionary containing the merged timing data.
    """
    if output_file is None:
        output_file = f"{result_dir}/evaluation/timing/timing_report.json"

    timing_dir = f"{result_dir}/evaluation/timing"
    if not os.path.exists(timing_dir):
        raise FileNotFoundError(
            f"Failed to find timing evaluation directory: {timing_dir}"
        )

    step_dirs = [
        d for d in os.listdir(timing_dir) if os.path.isdir(os.path.join(timing_dir, d))
    ]

    merged_data = {}
    for step_name in step_dirs:
        report_path = os.path.join(
            timing_dir, step_name, f"{step_name}_timing_power_report.json"
        )
        if os.path.exists(report_path):
            try:
                with open(report_path, "r") as f:
                    step_data = json.load(f)
                merged_data[step_name] = step_data
            except json.JSONDecodeError:
                logging.warning(f"Warning: {report_path} file format is invalid")
            except Exception as e:
                logging.error(f"Error occurred while reading {report_path}: {e}")

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(merged_data, f, indent=2, ensure_ascii=False)

    logging.info(f"Has been merged all timing reports to: {output_file}")
    return merged_data
