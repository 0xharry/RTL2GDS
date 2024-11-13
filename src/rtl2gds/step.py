"""
description: behavior of each RTL2GDS step
"""

import math
import subprocess

from . import configs, step_dump_json


class Step:
    def __init__(self):
        # self.input: str
        # self.output: str
        self.name: str
        self.description: str
        self.shell_cmd: list

    def run(self, io_env: dict):
        """
        TCL KEY IO ENV:
        INPUT_DEF
        GDS_FILE
        """
        print("step." + self.name)
        ret_code = subprocess.call(self.shell_cmd, env=io_env)
        assert ret_code == 0, f"Step {self.name} failed with return code {ret_code}"

    def update_progress_bar(self):
        pass


def get_yosys_top_info(file_path):
    """return top module area and name from synth_stat.txt"""
    # assert os.path.basename(file_path) != "synth_stat.txt",
    # "Input file name must be 'synth_stat.txt'"

    found_design_hierarchy = False

    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            if "=== design hierarchy ===" in line:
                found_design_hierarchy = True
            if found_design_hierarchy and "Chip area for top module" in line:
                # Extract the top name and area from the line
                parts = line.split(":")
                top_name = parts[0].split("'\\")[-1].strip("': ")
                top_area = float(parts[1].strip())
                return top_area, top_name

    return None, None


class Synthesis(Step):
    def __init__(self):
        super().__init__()
        self.name = "synthesis"
        self.description = "synthesis by yosys"
        # RTL_FILE, DESIGN_TOP, SDC
        # NETLIST_FILE, MODULE_AREA
        self.shell_cmd = configs.SHELL_CMD[self.name]

    def run(self, io_env: dict):
        """
        RTL_FILE, DESIGN_TOP, SDC
        NETLIST_FILE, MODULE_AREA
        """
        print("step." + self.name)
        ret_code = subprocess.call(self.shell_cmd, env=io_env)
        assert ret_code == 0, f"Step {self.name} failed with return code {ret_code}"

        if not {"DIE_AREA", "CORE_AREA"}.issubset(io_env.keys()):
            assert "UTILIZATION" in io_env.keys(), "UTILIZATION must be set"
            yosys_report_path = io_env["RESULT_DIR"] + "/yosys/synth_stat.txt"
            top_area, top_name = get_yosys_top_info(yosys_report_path)
            assert top_name == io_env["DESIGN_TOP"], "Top module name mismatch"
            length = math.sqrt(top_area / float(io_env["UTILIZATION"]))
            io_env["DIE_AREA"] = f"0 0 {length} {length}"
            io_env["CORE_AREA"] = f"10 10 {length-10} {length-10}"


class Floorplan(Step):
    def __init__(self):
        super().__init__()
        self.name = "floorplan"
        self.description = "Floorplaning by iEDA-iFP"
        # NETLIST_FILE, DESIGN_TOP, (MODULE_AREA+Utilization) or (DIE_AREA+CORE_AREA)
        # OUTPUT_DEF
        self.shell_cmd = configs.SHELL_CMD[self.name]


class FixFanout(Step):
    def __init__(self):
        super().__init__()
        self.name = "fixfanout"
        self.description = "Fixing fanout by iEDA-iNO"
        self.shell_cmd = configs.SHELL_CMD[self.name]


class Place(Step):
    def __init__(self):
        super().__init__()
        self.name = "place"
        self.description = "Standard Cell Placement by iEDA-iPL"
        self.shell_cmd = configs.SHELL_CMD[self.name]


class CTS(Step):
    def __init__(self):
        super().__init__()
        self.name = "cts"
        self.description = "Clock Tree Synthesis by iEDA-iCTS"
        self.shell_cmd = configs.SHELL_CMD[self.name]


class DrvOpt(Step):
    def __init__(self):
        super().__init__()
        self.name = "drv_opt"
        self.description = "Optimization Design Rule Voilation by iEDA-iTO"
        self.shell_cmd = configs.SHELL_CMD[self.name]


class HoldOpt(Step):
    def __init__(self):
        super().__init__()
        self.name = "hold_opt"
        self.description = "Optimization Hold Time Voilation by iEDA-iTO"
        self.shell_cmd = configs.SHELL_CMD[self.name]


class Legalize(Step):
    def __init__(self):
        super().__init__()
        self.name = "legalize"
        self.description = "Standard Cell Legalization by iEDA-iPL"
        self.shell_cmd = configs.SHELL_CMD[self.name]


class Filler(Step):
    def __init__(self):
        super().__init__()
        self.name = "filler"
        self.description = "Adding Filler for DFM by iEDA-iPL"
        self.shell_cmd = configs.SHELL_CMD[self.name]


class Route(Step):
    def __init__(self):
        super().__init__()
        self.name = "route"
        self.description = "Routing by iEDA-iRT"
        self.shell_cmd = configs.SHELL_CMD[self.name]


class DumpLayout(Step):
    def __init__(self, layout_fmt="gds"):
        super().__init__()
        self.description = "Dump Layout by iEDA-DB"
        if layout_fmt == "gds":
            self.name = "layout_gds"
            # INPUT_DEF
            # GDS_FILE
            self.shell_cmd = configs.SHELL_CMD[self.name]
        elif layout_fmt == "json":
            self.name = "layout_json"
            # INPUT_DEF
            # GDS_JSON_FILE
            self.shell_cmd = configs.SHELL_CMD[self.name]

    def run(self, io_env: dict):
        """
        INPUT_DEF
        GDS_JSON_FILE
        """
        print("step." + self.name)
        ret_code = subprocess.call(self.shell_cmd, env=io_env)
        assert ret_code == 0, f"Step {self.name} failed with return code {ret_code}"
        if self.name == "layout_json":
            step_dump_json.split_gds_json(io_env["GDS_JSON_FILE"])


def factory(step_name: str):
    step_map = {
        "synthesis": Synthesis,
        "floorplan": Floorplan,
        "fixfanout": FixFanout,
        "place": Place,
        "cts": CTS,
        "drv_opt": DrvOpt,
        "hold_opt": HoldOpt,
        "legalize": Legalize,
        "route": Route,
        "filler": Filler,
        "layout_gds": DumpLayout("gds"),
        "layout_json": DumpLayout("json"),
    }
    return step_map[step_name]()


from klayout import lay


def save_gds_image(gds_file: str, img_file: str, weight: int = 800, height: int = 800):
    """
    Takes a screenshot of a GDS file and saves it as an image.

    Parameters:
    gds_file (str): Path to the input GDS file.
    img_file (str): Path to the output image file.

    Reference:
    https://gist.github.com/sequoiap/48af5f611cca838bb1ebc3008eef3a6e
    """
    # Set display configuration options
    lv = lay.LayoutView()
    lv.set_config("background-color", "#ffffff")
    lv.set_config("grid-visible", "false")
    lv.set_config("grid-show-ruler", "false")
    lv.set_config("text-visible", "false")

    # Load the GDS file
    lv.load_layout(gds_file, 0)
    lv.max_hier()

    # event processing for delayed configuration events
    lv.timer()

    # Save the image
    lv.save_image(img_file, weight, height)
