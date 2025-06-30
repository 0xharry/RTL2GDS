import logging

from rtl2gds import Chip, flow
from rtl2gds.flow import cloud_step
from rtl2gds.global_configs import R2G_BASE_DIR, StepName


def main():
    logging.basicConfig(
        format="[%(asctime)s - %(levelname)s - %(name)s]: %(message)s",
        level=logging.INFO,
        force=True,
    )
    logging.info("Start test")
    top_name = "NPC"
    rtl_file = f"{R2G_BASE_DIR}/demo/minirv.sv"
    init_config = {
        "RTL_FILE": rtl_file,
        "CORE_UTIL": 0.5,
        "TOP_NAME": top_name,
        "CLK_FREQ_MHZ": 200,
        "CLK_PORT_NAME": "clock",
        "RESULT_DIR": f"{R2G_BASE_DIR}/tmp/test_cloud_step_{top_name}",
    }
    test_design = Chip(config_dict=init_config)
    cloud_step.run(chip=test_design, expect_step=StepName.SYNTHESIS)
    cloud_step.run(chip=test_design, expect_step=StepName.FLOORPLAN)
    cloud_step.run(chip=test_design, expect_step=StepName.PLACEMENT)
    cloud_step.run(chip=test_design, expect_step=StepName.CTS)
    cloud_step.run(chip=test_design, expect_step=StepName.ROUTING)
    cloud_step.run(chip=test_design, expect_step=StepName.SIGNOFF)
    logging.info("Test finished")


if __name__ == "__main__":
    main()
