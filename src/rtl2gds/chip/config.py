from dataclasses import dataclass


@dataclass
class Keyword:
    TOP_NAME = "TOP_NAME"

    # PATH_SETTING = "PATH_SETTING"
    RTL_FILE = "RTL_FILE"
    RESULT_DIR = "RESULT_DIR"
    NETLIST_FILE = "NETLIST_FILE"
    DEF_FILE = "DEF_FILE"
    GDS_FILE = "GDS_FILE"
    SDC_FILE = "SDC_FILE"

    # CONSTRAIN = "CONSTRAIN"
    CLK_PORT_NAME = "CLK_PORT_NAME"
    CLK_FREQ_MHZ = "CLK_FREQ_MHZ"
    DIE_BBOX = "DIE_BBOX"
    CORE_BBOX = "CORE_BBOX"
    CORE_UTIL = "CORE_UTIL"
    CELL_AREA = "CELL_AREA"

    # context
    FINISHED_STEP = "FINISHED_STEP"
    EXPECTED_STEP = "EXPECTED_STEP"
    NUM_EXECUTED_STEPS = "NUM_EXECUTED_STEPS"
    INIT_TIME = "INIT_TIME"
    LAST_UPDATE_TIME = "LAST_UPDATE_TIME"
    # LAST_UPDATE_INFO = "LAST_UPDATE_INFO" top+f_step+time
