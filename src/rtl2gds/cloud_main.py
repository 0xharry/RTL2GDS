#!/usr/bin/env python3
"""module main"""
import json
import logging
import os
import sys
from pathlib import Path

import yaml

from rtl2gds.chip import Chip
from rtl2gds.flow import cloud_step

logging.basicConfig(
    format="[%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d]: %(message)s",
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    force=True,
)


def main(config_yaml: Path, config: dict, step_name: str):
    """
    RTL2GDS cloud execution function.

    Args:
        config_yaml: Path to the configuration YAML file for creating a Chip
        config: Step configuration dictionary containing step parameters
        step_name: The RTL2GDS step to execute

    Returns:
        dict: Result files from the execution, empty dict if failed
    """
    logging.info("Starting RTL2GDS execution for step: %s", step_name)

    try:
        # Create Chip design from config dictionary
        logging.info("Initializing Chip design...")
        chip_design = Chip(config_yaml=config_yaml)

        logging.info("Chip design initialized: %s", chip_design.top_name)
        logging.info("Ignoring config dict for now")

        logging.info("Running flow step: %s", step_name)
        result_files = cloud_step.run(chip_design, expect_step=step_name)
        logging.info("Step %s completed. Result files: %s", step_name, result_files)

        logging.info("Dumping final config YAML...")
        logging.info("Config YAML: %s, finished_step: %s", config_yaml, chip_design.finished_step)
        chip_design.dump_config_yaml(config_yaml=config_yaml)  # overwrite the config file
        task_workspace = chip_design.path_setting.result_dir
        project_workspace = Path(task_workspace).parent

        logging.info("Preparing notify result_files...")
        task_result_files_json = f"{project_workspace}/result_files.json"
        with open(f"{task_workspace}/result_files.json", "w", encoding="utf-8") as f:
            json.dump(result_files, f)  # inside task
        with open(task_result_files_json, "w", encoding="utf-8") as f:
            # filter `result_dir` from folder name
            for k, v in result_files.items():
                if isinstance(v, str):
                    result_files[k] = v.replace(f"{project_workspace}/", "")
                elif isinstance(v, list):
                    result_files[k] = [x.replace(f"{project_workspace}/", "") for x in v]
            json.dump(result_files, f)  # inside project

        # Check if execution was successful
        if result_files and chip_design.finished_step == step_name:
            logging.info(
                "Step %s for Chip (%s) completed successfully", step_name, chip_design.top_name
            )
            return result_files
        else:
            logging.error(
                "Step %s for Chip (%s) failed: No result files or step not completed",
                step_name,
                chip_design.top_name,
            )
            return {}

    except Exception as e:
        logging.exception(
            "An error occurred during the step %s for Chip (%s): %s",
            step_name,
            chip_design.top_name,
            e,
        )
        raise


def main_cli():
    """
    Command-line interface for cloud_main.py.
    Command: python3 /<rtl2gds-module>/cloud_main.py <step_name> <config_yaml_path>
    """
    logging.info("Starting cloud_main.py with args: %s", sys.argv)

    if len(sys.argv) < 3:
        raise ValueError("Insufficient arguments")

    step_name = sys.argv[1]
    config_yaml = Path(sys.argv[2])
    # step_params = Path(sys.argv[3]) # <step_params_config>
    logging.info("Target step: %s", step_name)

    if not config_yaml.exists():
        raise ValueError(f"Config file not found: {config_yaml}")

    main(config_yaml=config_yaml, config={}, step_name=step_name)

    logging.info("cloud_main.py finished.")


if __name__ == "__main__":
    main_cli()
