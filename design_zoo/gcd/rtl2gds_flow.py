#!/usr/bin/env python3
"""test flow"""

import logging

from rtl2gds import Chip, flow


def main():
    """gcd + rtl2gds flow"""

    logging.basicConfig(
        format="[%(asctime)s - %(levelname)s - %(name)s]: %(message)s",
        level=logging.INFO,
        force=True,
    )

    gcd = Chip("./gcd.yaml")

    flow.rtl2gds_flow.run(gcd)


if __name__ == "__main__":
    main()
