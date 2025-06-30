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
    logging.info(f"Starting RTL2GDS execution for step: {step_name}")

    try:
        # Create Chip design from config dictionary
        logging.info("Initializing Chip design...")
        chip_design = Chip(config_yaml=config_yaml)

        logging.info(f"Chip design initialized: {chip_design.top_name}")
        logging.info("Ignoring config dict for now")

        logging.info(f"Running flow step: {step_name}")
        result_files = cloud_step.run(chip_design, expect_step=step_name)
        logging.info(f"Step {step_name} completed. Result files: {result_files}")

        logging.info("Dumping final config YAML...")
        logging.info(f"Config YAML: {config_yaml}, finished_step: {chip_design.finished_step}")
        chip_design.dump_config_yaml(config_yaml=config_yaml)  # overwrite the config file

        logging.info("Preparing notify result_files...")
        task_result_files_json = (
            f"{Path(chip_design.path_setting.result_dir).parent}/current_task_result_files.json"
        )
        with open(task_result_files_json, "w") as f:
            json.dump(result_files, f)

        # Check if execution was successful
        if result_files and chip_design.finished_step == step_name:
            logging.info(
                f"Step {step_name} for Chip ({chip_design.top_name}) completed successfully"
            )
            return result_files
        else:
            logging.error(
                f"Step {step_name} for Chip ({chip_design.top_name}) failed: No result files or step not completed"
            )
            return {}

    except Exception as e:
        logging.exception(
            f"An error occurred during the step {step_name} for Chip ({chip_design.top_name}): {e}"
        )
        raise


def test_main():
    """Test main function."""
    logging.info("Test RTL2GDS cloud_main, that'll be all. Exiting...")
    return


def main_cli():
    """
    Command-line interface for cloud_main.py.
    Command: python3 /<rtl2gds-module>/cloud_main.py <step_name> <config_yaml_path>
    """
    logging.info(f"Starting cloud_main.py with args: {sys.argv}")

    if len(sys.argv) < 3:
        raise ValueError("Insufficient arguments")

    step_name = sys.argv[1]
    config_yaml = Path(sys.argv[2])
    # step_params = Path(sys.argv[3]) # <step_params_config>
    logging.info(f"Target step: {step_name}")

    if not config_yaml.exists():
        raise ValueError(f"Config file not found: {config_yaml}")

    main(config_yaml=config_yaml, config={}, step_name=step_name)
    # test_main()

    logging.info("cloud_main.py finished.")


def generate_complete_config(config_yaml: Path, rtl_path: Path, workspace_path: Path):
    """Loads, completes, and saves the configuration YAML."""
    logging.info(f"Loading config from {config_yaml}")
    with open(config_yaml, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
        if config is None:
            config = {}
            logging.warning(f"Config file {config_yaml} was empty.")

    config["RTL_FILE"] = str(rtl_path.resolve())
    workspace_abs_path = str(workspace_path.resolve())

    required_keys = ["TOP_NAME", "CLK_PORT_NAME"]
    missing_keys = [key for key in required_keys if key not in config]
    if missing_keys:
        error_msg = f"Missing required keys in config.yaml: {', '.join(missing_keys)}"
        logging.error(error_msg)
        raise ValueError(error_msg)

    top_name = config["TOP_NAME"]
    default_configs = {
        "RESULT_DIR": workspace_abs_path,
        "NETLIST_FILE": f"{workspace_abs_path}/{top_name}.v",
        "GDS_FILE": f"{workspace_abs_path}/{top_name}.gds",
        "CLK_FREQ_MHZ": 50,
        "CORE_UTIL": 0.5,
    }

    for key, value in default_configs.items():
        if key not in config:
            config[key] = value

    logging.info(f"Saving updated config to {config_yaml}")
    with open(config_yaml, "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False)


if __name__ == "__main__":
    main_cli()
