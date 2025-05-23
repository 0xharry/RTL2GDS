""" Step runner factory """

from . import drc, floorplan, layout_gds, layout_json, synthesis
from .step import (CTS, DrvOpt, Filler, HoldOpt, Legalization, NetlistOpt,
                   Placement, Routing)

__all__ = [
    "synthesis",
    "floorplan",
    "layout_gds",
    "layout_json",
    "pr_step_map",
    "drc",
    "sta",
]

from ..global_configs import StepName

pr_step_map = {
    StepName.NETLIST_OPT: NetlistOpt(),
    StepName.PLACEMENT: Placement(),
    StepName.CTS: CTS(),
    StepName.DRV_OPT: DrvOpt(),
    StepName.HOLD_OPT: HoldOpt(),
    StepName.LEGALIZATION: Legalization(),
    StepName.ROUTING: Routing(),
    StepName.FILLER: Filler(),
}
