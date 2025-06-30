from rtl2gds.chip import Chip
from rtl2gds.flow.step_wrapper import StepWrapper


def run(chip: Chip):
    """
    chip = Chip(
        config_dict={
            "DEF_FILE": "——",
            "TOP_NAME": "——",
            "RESULT_DIR": "——",
            "DIE_BBOX": "——",
            "CLK_PORT_NAME": "——",
            "CLK_FREQ_MHZ": "——",
        }
    )
    """
    runner = StepWrapper(chip)

    runner.run_sta()
    runner.run_gds()
    runner.run_drc()
