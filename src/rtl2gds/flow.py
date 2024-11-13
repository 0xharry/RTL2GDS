import yaml

from . import chip, metrics, step


class _Flow:
    """interface class for flow"""

    rtl2gds_flow = [
        "synthesis",
        "floorplan",
        "fixfanout",
        "place",
        "cts",
        "drv_opt",
        "hold_opt",
        "legalize",
        "route",
        "filler",
        "layout_gds",
    ]

    def run(self):
        """execute costum steps"""

    def update_metrics(self):
        """update tool/chip related metrics"""

    def dump_metrics(self):
        """print metrics"""

    def dump_gds(self):
        """dump gds"""


class RTL2GDS(_Flow):
    """run rtl to gds"""

    def __init__(self, chip_inst: chip.Chip):
        self.chip = chip_inst
        self._steps = _Flow.rtl2gds_flow

    def run(self):
        synthesis = step.Synthesis()
        synthesis.run(self.chip.io_env)
        # netlist_file = self.chip.path_setting.netlist_file
        floorplan = step.Floorplan()
        # input=netlist_file, output=self.chip.path_setting.def_file
        floorplan.run(self.chip.io_env)
        # self.update_metrics()

        # iterate over steps except theose with special input and output
        # (synthesis, floorplan and layout_gds)
        for step_name in self._steps[2:-1]:
            s = step.factory(step_name)
            s.run(self.chip.io_env)
            # step.input = self.chip.path_setting.def_file
            # step.output = self.chip.path_setting.def_file
            # self.update_metrics()

        layout_gds = step.DumpLayout("gds")
        # input=self.chip.path_setting.def_file, output=self.chip.gds_file
        layout_gds.run(self.chip.io_env)
        # self.update_metrics()


def _find_index_range(lst, elem1, elem2):
    start_index = lst.index(elem1)
    end_index = lst.index(elem2)
    return start_index, end_index


class CostumFlow(_Flow):
    """run costum flow"""

    def __init__(self, start_step: str, end_step: str, cc: chip.Chip):
        self.chip = cc

        start_index, end_index = _find_index_range(
            _Flow.rtl2gds_flow, start_step, end_step
        )
        self._steps = _Flow.rtl2gds_flow[start_index : end_index + 1]

    def run(self):
        for step_name in self._steps:
            s = step.factory(step_name)
            s.run(self.chip.io_env)


# class FlowMetrics:

#     def __init__(self):
#         self.design: metrics.DesignMetrics
#         self.step: metrics.EDAMetrics

#     def dump(self):
#         return yaml.dump(self.__dict__)
