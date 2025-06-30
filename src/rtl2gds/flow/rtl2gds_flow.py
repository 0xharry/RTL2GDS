import logging
import os
import time

from rtl2gds.chip import Chip
from rtl2gds.flow.step_wrapper import StepWrapper
from rtl2gds.global_configs import PR_FLOW_STEPS, StepName


def run(chip: Chip):
    start_time = time.perf_counter()
    runner = StepWrapper(chip)

    # Run synthesis
    runner.run_synthesis()

    # Run floorplan
    runner.run_floorplan()
    runner.run_save_layout_gds(step_name=StepName.FLOORPLAN)
    runner.run_save_layout_json(StepName.FLOORPLAN)

    # Run P&R flow
    for step_name in PR_FLOW_STEPS:
        runner.run_pr_step(step_name)
        if step_name in [StepName.PLACEMENT, StepName.FILLER]:
            runner.run_save_layout_gds(step_name=step_name, take_snapshot=True)
            runner.run_save_layout_json(step_name)

    assert chip.finished_step == StepName.FILLER

    runner.run_sta()
    runner.run_gds()
    runner.run_drc()

    assert os.path.exists(chip.path_setting.gds_file)
    end_time = time.perf_counter()
    logging.info("Total elapsed time: %.2f seconds", end_time - start_time)
