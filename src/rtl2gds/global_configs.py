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
# Set the environment variable `RTL2GDS_USE_PROJ_BIN_LIB` to "1" to use the
# local iEDA tools and libraries in the project's `bin` directory. Defaults to "0".
_USE_PROJ_BIN_LIB = os.environ.get("RTL2GDS_USE_PROJ_BIN_LIB", "0") == "1"

if _USE_PROJ_BIN_LIB:
    _TOOL_PATH = f"{R2G_BIN_DIR}/iEDA:{R2G_BIN_DIR}/sv2v-Linux:{R2G_BIN_DIR}/yosys/bin:{_BIN_ENV}"
    _TOOL_LIB = f"{R2G_BIN_DIR}/lib:{_LIB_ENV}"
else:
    _TOOL_PATH = _BIN_ENV
    _TOOL_LIB = _LIB_ENV

ENV_TOOLS_PATH = {
    "PATH": _TOOL_PATH,
    "LD_LIBRARY_PATH": _TOOL_LIB,
    "FOUNDRY_DIR": R2G_PDK_DIR_IHP130,
    "IEDA_TCL_SCRIPT_DIR": f"{R2G_TOOL_DIR}/iEDA/script",
    "IEDA_CONFIG_DIR": f"{R2G_TOOL_DIR}/iEDA/iEDA_config",
    "LIBERTY_FILE": f"{R2G_PDK_DIR_IHP130}/ihp-sg13g2/libs.ref/sg13g2_stdcell/lib/sg13g2_stdcell_typ_1p20V_25C.lib",
    "RUST_BACKTRACE": "1",
    "VERILOG_INCLUDE_DIRS": "",
    "RTL2GDS_DIR": R2G_SRC_DIR,
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
    LEGALIZATION = "legalization"
    ROUTING = "routing"
    FILLER = "filler"
    LAYOUT_GDS = "layout_gds"
    LAYOUT_JSON = "layout_json"
    STA = "sta"
    DRC = "drc"


# Flow step sequences
RTL2GDS_FLOW_STEPS = [
    StepName.INIT,
    StepName.SYNTHESIS,
    StepName.FLOORPLAN,
    StepName.NETLIST_OPT,
    StepName.PLACEMENT,
    StepName.CTS,
    StepName.LEGALIZATION,
    StepName.ROUTING,
    StepName.FILLER,
    StepName.STA,
]

_start_idx = RTL2GDS_FLOW_STEPS.index(StepName.NETLIST_OPT)
_end_idx = RTL2GDS_FLOW_STEPS.index(StepName.FILLER)

PR_FLOW_STEPS = RTL2GDS_FLOW_STEPS[_start_idx : _end_idx + 1]

assert PR_FLOW_STEPS[0] == StepName.NETLIST_OPT and PR_FLOW_STEPS[-1] == StepName.FILLER
