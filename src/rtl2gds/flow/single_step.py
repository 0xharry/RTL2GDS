from .. import step
from ..chip import Chip
from ..global_configs import StepName
from . import rtl2gds_flow
from .step_wrapper import StepWrapper


def run(
    chip: Chip, 
    expect_step: str, 
    take_snapshot: bool = False,
    cloud_outputs: bool = False, 
) -> dict:
    """
    Step Router
    """
    dump_json = False
    result_files = {}
    if expect_step == StepName.RTL2GDS_ALL:
        rtl2gds_flow.run(chip)
        dump_json = True
    else:
        runner = StepWrapper(chip)

        if expect_step == StepName.SYNTHESIS:
            result_files = runner.run_synthesis()
        elif expect_step == StepName.FLOORPLAN:
            result_files = runner.run_floorplan()
            dump_json = True
        else:
            result_files = runner.run_pr_step(expect_step)
            if cloud_outputs and expect_step == StepName.PLACEMENT:
                result_files.update({
                    "congestion map": f"{chip.path_setting.result_dir}/report/iEDA-iPL/rt/place_egr_union_overflow.csv"
                })
            if expect_step in [
                StepName.PLACEMENT,
                StepName.CTS,
                StepName.LEGALIZATION,
                StepName.ROUTING,
                StepName.FILLER,
            ]:
                dump_json = True

    if take_snapshot:
        layout_files = runner.run_dump_layout_gds(step_name=expect_step, take_snapshot=True)
        result_files.update(layout_files)

    # Dump and return json files
    if cloud_outputs and dump_json:
        json_files = step.layout_json.run(
            input_def=chip.path_setting.def_file,
            result_dir=chip.path_setting.result_dir,
            layout_json_file=f"{chip.path_setting.result_dir}/{chip.top_name}_{chip.finished_step}.json",
        )
        result_files.update({"json_files": json_files})

    return result_files
