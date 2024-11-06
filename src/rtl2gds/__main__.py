#!/usr/bin/env python3
"""module main"""
import argparse
import pathlib

from . import chip, flow


def main():
    """rtl2gds flow"""
    parser = argparse.ArgumentParser(prog="rtl2gds")
    parser.add_argument("-t", "--top", type=str, help="design top name")
    parser.add_argument(
        "-c",
        "--config",
        type=pathlib.Path,
        required=True,
        help="design config file, overrides --top",
    )
    args = parser.parse_args()

    chip_design = chip.Chip(args.top)
    chip_design.load_config(args.config)

    rtl2gds_flow = flow.RTL2GDS(chip_design)
    rtl2gds_flow.run()

    rtl2gds_flow.dump_metrics()
    rtl2gds_flow.dump_gds()


if __name__ == "__main__":
    main()
