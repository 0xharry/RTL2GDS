#!/usr/bin/env python3
"""test flow"""

import logging

from rtl2gds import Chip, flow


def main():
    """picorv32 + rtl2gds flow"""

    logging.basicConfig(
        format="[%(asctime)s - %(levelname)s - %(name)s]: %(message)s",
        level=logging.INFO,
        force=True,
    )

    picorv32 = Chip("./pico.yaml")

    flow.rtl2gds_flow.run(picorv32)


if __name__ == "__main__":
    main()
