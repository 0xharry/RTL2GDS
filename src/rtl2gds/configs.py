import os

PKG_SRC_DIR = os.path.dirname(os.path.abspath(__file__))
PKG_BIN_DIR = os.path.abspath(PKG_SRC_DIR + "/../../bin")
PKG_PDK_DIR = os.path.abspath(PKG_SRC_DIR + "/../../foundry/sky130")
PKG_TOOL_DIR = os.path.abspath(PKG_SRC_DIR + "/../../tools")

_BIN_ENV = os.environ["PATH"] if "PATH" in os.environ else ""
_LIB_ENV = os.environ["LD_LIBRARY_PATH"] if "LD_LIBRARY_PATH" in os.environ else ""

ENV_TOOLS_PATH = {
    "PATH": f"{PKG_BIN_DIR}/iEDA:{PKG_BIN_DIR}/yosys/bin:{_BIN_ENV}",
    "LD_LIBRARY_PATH": f"{PKG_BIN_DIR}/lib:{_LIB_ENV}",
    "FOUNDRY_DIR": PKG_PDK_DIR,
    "TCL_SCRIPT_DIR": f"{PKG_TOOL_DIR}/iEDA/script",
    "CONFIG_DIR": f"{PKG_TOOL_DIR}/iEDA/iEDA_config",
    "SDC_FILE": f"{PKG_TOOL_DIR}/default.sdc",
    "RUST_BACKTRACE": "1",
    "VERILOG_INCLUDE_DIRS": "",
}

CONFIG_KEYWORDS = {
    "NETLIST_FILE",
    "SDC_FILE",
    "SPEF_FILE",
    "FOUNDRY_DIR",
    "TCL_SCRIPT_DIR",
    "CONFIG_DIR",
    "GDS_JSON_FILE",
    "RESULT_DIR",
    "DESIGN_TOP",
    "RTL_FILE",
    "GDS_FILE",
    "CLK_PORT_NAME",
    "CLK_FREQ_MHZ",
    "DIE_AREA",
    "CORE_AREA",
}

SHELL_CMD = {
    "synthesis": ["yosys", f"{PKG_TOOL_DIR}/yosys/yosys.tcl"],
    "floorplan": [
        "iEDA",
        "-script",
        f'{ENV_TOOLS_PATH["TCL_SCRIPT_DIR"]}/iFP_script/run_iFP.tcl',
    ],
    "fixfanout": [
        "iEDA",
        "-script",
        f'{ENV_TOOLS_PATH["TCL_SCRIPT_DIR"]}/iNO_script/run_iNO_fix_fanout.tcl',
    ],
    "place": [
        "iEDA",
        "-script",
        f'{ENV_TOOLS_PATH["TCL_SCRIPT_DIR"]}/iPL_script/run_iPL.tcl',
    ],
    "cts": [
        "iEDA",
        "-script",
        f'{ENV_TOOLS_PATH["TCL_SCRIPT_DIR"]}/iCTS_script/run_iCTS.tcl',
    ],
    "drv_opt": [
        "iEDA",
        "-script",
        f'{ENV_TOOLS_PATH["TCL_SCRIPT_DIR"]}/iTO_script/run_iTO_drv.tcl',
    ],
    "hold_opt": [
        "iEDA",
        "-script",
        f'{ENV_TOOLS_PATH["TCL_SCRIPT_DIR"]}/iTO_script/run_iTO_hold.tcl',
    ],
    "legalize": [
        "iEDA",
        "-script",
        f'{ENV_TOOLS_PATH["TCL_SCRIPT_DIR"]}/iPL_script/run_iPL_legalization.tcl',
    ],
    "route": [
        "iEDA",
        "-script",
        f'{ENV_TOOLS_PATH["TCL_SCRIPT_DIR"]}/iRT_script/run_iRT.tcl',
    ],
    "filler": [
        "iEDA",
        "-script",
        f'{ENV_TOOLS_PATH["TCL_SCRIPT_DIR"]}/iPL_script/run_iPL_filler.tcl',
    ],
    "layout_gds": [
        "iEDA",
        "-script",
        f'{ENV_TOOLS_PATH["TCL_SCRIPT_DIR"]}/DB_script/run_def_to_gds_text.tcl',
    ],
    "layout_json": [
        "iEDA",
        "-script",
        f'{ENV_TOOLS_PATH["TCL_SCRIPT_DIR"]}/DB_script/run_def_to_json_text.tcl',
    ],
}


# "sv2v": [
#     "sv2v",
#     f"--incdir={default_vars["FOUNDRY_DIR"]}/verilog",
#     f"--top={default_vars["DESIGN_TOP"]}",
#     f"--write={default_vars["DESIGN_TOP"]}.v",
#     default_vars["RTL_FILE"],
# ]


def main():
    print(
        PKG_SRC_DIR,
        "\n",
        PKG_BIN_DIR,
        "\n",
        PKG_PDK_DIR,
        "\n",
        ENV_TOOLS_PATH,
        "\n",
        ENV_TOOLS_PATH,
        "\n",
        CONFIG_KEYWORDS,
        "\n",
        SHELL_CMD,
        "\n",
    )


if __name__ == "__main__":
    main()

