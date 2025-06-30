#!/usr/bin/env python3
"""module main"""
import argparse
import logging
import pathlib

from rtl2gds import flow
from rtl2gds.chip import Chip


def main():
    """rtl2gds flow"""
    parser = argparse.ArgumentParser(prog="rtl2gds")
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
    args = parser.parse_args()

    logging.basicConfig(
        format="[%(asctime)s - %(levelname)s - %(name)s]: %(message)s",
        level=args.log_level,
        force=True,
    )

    logging.info("rtl2gds starting...")

    chip_design = Chip(config_yaml=args.config)

    flow.rtl2gds_flow.run(chip_design)

    logging.info("rtl2gds finished")


if __name__ == "__main__":
    main()
