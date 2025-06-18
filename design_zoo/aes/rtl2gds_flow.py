#!/usr/bin/env python3
"""test flow"""

import logging

from rtl2gds import Chip, flow


def main():
    """aes + rtl2gds flow"""

    logging.basicConfig(
        format="[%(asctime)s - %(levelname)s - %(name)s]: %(message)s",
        level=logging.INFO,
        force=True,
    )

    aes = Chip("./aes.yaml")

    flow.rtl2gds_flow.run(aes)


if __name__ == "__main__":
    main()
