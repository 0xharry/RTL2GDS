import os
from dataclasses import dataclass

R2G_SRC_DIR = os.path.dirname(os.path.abspath(__file__))
R2G_BIN_DIR = os.path.abspath(R2G_SRC_DIR + "/../../bin")
R2G_PDK_DIR = os.path.abspath(R2G_SRC_DIR + "/../../foundry")
R2G_PDK_DIR_SKY130 = os.path.abspath(R2G_PDK_DIR + "/sky130")
R2G_PDK_DIR_IHP130 = os.path.abspath(R2G_PDK_DIR + "/ihp130")
R2G_TOOL_DIR = os.path.abspath(R2G_SRC_DIR + "/../../tools")

_BIN_ENV = os.environ["PATH"] if "PATH" in os.environ else ""
_LIB_ENV = os.environ["LD_LIBRARY_PATH"] if "LD_LIBRARY_PATH" in os.environ else ""

ENV_TOOLS_PATH = {
    "PATH": f"{R2G_BIN_DIR}/iEDA:{R2G_BIN_DIR}/yosys/bin:{R2G_BIN_DIR}/sv2v-Linux:{_BIN_ENV}",
    "LD_LIBRARY_PATH": f"{R2G_BIN_DIR}/lib:{_LIB_ENV}",
    "FOUNDRY_DIR": R2G_PDK_DIR_SKY130,
    "IEDA_TCL_SCRIPT_DIR": f"{R2G_TOOL_DIR}/iEDA/script",
    "IEDA_CONFIG_DIR": f"{R2G_TOOL_DIR}/iEDA/iEDA_config",
    "RUST_BACKTRACE": "1",
    "VERILOG_INCLUDE_DIRS": "",
}

DEFAULT_SDC_FILE = f"{R2G_TOOL_DIR}/default.sdc"
DEFAULT_RESULT_DIR = "rtl2gds_result"
DEFAULT_NETLIST_FILE = f"{DEFAULT_RESULT_DIR}/rtl2gds_top_netlist.v"
DEFAULT_DEF_FILE = f"{DEFAULT_RESULT_DIR}/rtl2gds_top_step.def"
DEFAULT_GDS_FILE = f"{DEFAULT_RESULT_DIR}/rtl2gds_top_layout.gds"

# Flow & Step settings
@dataclass
class StepName:
    """RTL2GDS flow step names"""

    RTL2GDS_ALL = "rtl2gds_all"
    INIT = "init"
    SYNTHESIS = "synthesis"
    FLOORPLAN = "floorplan"
    NETLIST_OPT = "netlist_opt"
    PLACEMENT = "placement"
    CTS = "cts"
    DRV_OPT = "drv_opt"
    HOLD_OPT = "hold_opt"
    LEGALIZATION = "legalization"
    ROUTING = "routing"
    FILLER = "filler"
    LAYOUT_GDS = "layout_gds"
    LAYOUT_JSON = "layout_json"
    STA = "sta"
    DRC = "drc"


# Flow step sequences
RTL2GDS_FLOW_STEP = [
    StepName.INIT,
    StepName.SYNTHESIS,
    StepName.FLOORPLAN,
    StepName.NETLIST_OPT,
    StepName.PLACEMENT,
    StepName.CTS,
    StepName.DRV_OPT,
    StepName.HOLD_OPT,
    StepName.LEGALIZATION,
    StepName.ROUTING,
    StepName.FILLER,
]

PR_FLOW_STEP = RTL2GDS_FLOW_STEP[3:]
