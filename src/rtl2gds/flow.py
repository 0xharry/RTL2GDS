import yaml

from . import chip, metrics, step


class _Flow:
    """interface class for flow"""

    def __init__(self):
        pass
        # self.chip: chip.Chip
        # self.metrics: FlowMetrics
        # self._steps: list[str]

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

    def __init__(self, cc: chip.Chip):
        self.chip = cc
        self.metrics: FlowMetrics
        self._steps = [
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


class FlowMetrics:

    def __init__(self):
        self.design: metrics.DesignMetrics
        self.step: metrics.EDAMetrics

    def dump(self):
        return yaml.dump(self.__dict__)
