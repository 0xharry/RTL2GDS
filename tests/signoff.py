import logging

from rtl2gds import Chip, flow
from rtl2gds.global_configs import R2G_BASE_DIR


def main():
    logging.basicConfig(
        format="[%(asctime)s - %(levelname)s - %(name)s]: %(message)s",
        level=logging.INFO,
        force=True,
    )
    logging.info("Start signoff flow")
    test_design = Chip(
        config_dict={
            "DEF_FILE": f"{R2G_BASE_DIR}/design_zoo/gcd/gcd_results/08_filler_gcd/gcd_filler.def",
            "TOP_NAME": "gcd",
            "RESULT_DIR": f"{R2G_BASE_DIR}/design_zoo/gcd/gcd_results/10_signoff",
            "DIE_BBOX": "0 0 101.627 101.627",
            "CLK_PORT_NAME": "clk",
            "CLK_FREQ_MHZ": 200,
        }
    )
    flow.signoff.run(test_design)
    logging.info("Signoff flow finished")


if __name__ == "__main__":
    main()
