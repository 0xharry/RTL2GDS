#!/usr/bin/env python3
"""Single step main entry point"""
import argparse
import logging
import pathlib

from rtl2gds.chip import Chip
from rtl2gds.flow.single_step import run
from rtl2gds.global_configs import StepName


def main():
    """Single step flow main entry point"""
    parser = argparse.ArgumentParser(prog="rtl2gds_single_step")
    parser.add_argument(
        "--log_level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="log level",
    )
    parser.add_argument(
        "-c",
        "--config",
        type=pathlib.Path,
        required=True,
        help="design config file",
    )
    # Get available step names from StepName class
    available_steps = [
        attr
        for attr in dir(StepName)
        if not attr.startswith("_") and not callable(getattr(StepName, attr))
    ]

    parser.add_argument(
        "--step",
        type=str,
        required=True,
        help=f"step to run. Available steps: {', '.join(available_steps)}",
    )
    parser.add_argument(
        "--take_snapshot",
        action="store_true",
        help="take snapshot of current step",
    )
    parser.add_argument(
        "--cloud_outputs",
        action="store_true",
        help="generate cloud outputs (layout json)",
    )
    parser.add_argument(
        "--result_dir",
        type=str,
        help="custom result directory path",
    )
    parser.add_argument(
        "--input_def",
        type=str,
        help="custom input DEF file path for routing steps",
    )
    args = parser.parse_args()

    logging.basicConfig(
        format="[%(asctime)s - %(levelname)s - %(name)s]: %(message)s",
        level=args.log_level,
        force=True,
    )

    logging.info(f"rtl2gds single step starting for step: {args.step}")

    chip_design = Chip(config_yaml=args.config)

    # Override result directory if specified
    if args.result_dir:
        chip_design.path_setting.result_dir = args.result_dir
        # Ensure the directory exists
        import os

        os.makedirs(args.result_dir, exist_ok=True)
        logging.info(f"Using custom result directory: {args.result_dir}")

    # Override input DEF file if specified
    if args.input_def:
        chip_design.path_setting.def_file = args.input_def
        logging.info(f"Using custom input DEF file: {args.input_def}")

    result_files = run(
        chip=chip_design,
        expect_step=args.step,
        take_snapshot=args.take_snapshot,
        cloud_outputs=args.cloud_outputs,
    )

    logging.info(f"rtl2gds single step finished. Results: {result_files}")


if __name__ == "__main__":
    main()
