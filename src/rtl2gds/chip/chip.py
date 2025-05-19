import os
import pathlib
import time
from pathlib import Path
from typing import Dict

import yaml

from rtl2gds import global_configs
from rtl2gds.chip.config import Keyword
from rtl2gds.chip.design_constrain import DesignConstrain
from rtl2gds.chip.design_path import DesignPath
from rtl2gds.chip.metrics import DesignMetrics


class Chip:
    """
    Main design object that manages chip design flow from RTL to GDS.

    This class centralizes all design information and provides interfaces
    for running design flow steps like synthesis, floorplanning, etc.
    """

    def __init__(
        self,
        config_yaml: str|Path = None,
        config_dict: Dict = None,
        top_name: str = None,
        path_setting: DesignPath = None,
        constrain: DesignConstrain = None,
        finished_step: str = global_configs.StepName.INIT,
        expected_step: str = global_configs.StepName.INIT
    ):
        """
        Initialize a Chip object from YAML file `config_yaml` or a config dict `config_dict`, or init parameters `top_name`, `path_setting` and `constrain`.
        """
        assert top_name or config_yaml or (Keyword.TOP_NAME in config_dict) or (Keyword.TOP_NAME.lower() in config_dict),\
            "top_name is required"

        if config_yaml:
            if config_dict:
                raise ValueError("config_yaml and config_dict cannot be set at the same time.")
            if not os.path.exists(config_yaml):
                raise FileNotFoundError(f"Config file {config_yaml} does not exist. ")
            with open(config_yaml, "r", encoding="utf-8") as f:
                config_dict = yaml.safe_load(f)
            self.config_yaml = config_yaml
        elif config_dict:
            if (Keyword.TOP_NAME not in config_dict) and (Keyword.TOP_NAME.lower() not in config_dict):
                if top_name:
                    config_dict[Keyword.TOP_NAME] = top_name
                else:
                    raise ValueError("top_name is required in config_dict")
            if path_setting and constrain:
                raise ValueError("config_yaml or config_dict, or path_setting and constrain must be set")

        self.top_name = top_name
        self.path_setting = path_setting
        self.constrain = constrain
        self.metrics = DesignMetrics()
        # Contexts
        self.config = config_dict
        self.config_yaml = config_yaml
        self.finished_step = finished_step
        self.expected_step = expected_step
        self.init_time = self._strtime()
        self.last_update_time = self.init_time

        # config setup
        if config_yaml:
            with open(config_yaml, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f)
            self._init_from_config(self.config)
        else:
            if self.config is None:
                self.update2config()
            else:
                self._init_from_config(self.config)
            self.config_yaml = f"{self.path_setting.result_dir}/rtl2gds_{self.top_name}.yaml"
            path = pathlib.Path(self.config_yaml)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()
            self.dump_config_yaml(override=True)


    def _strtime(self):
        return time.strftime("%Y%m%d_%H%M%S")

    def _init_from_config(self, config: Dict):
        """
        Init a `top_name`, `path_setting` and `constrain` from a config dict

        The minimal config should contain:
        - path_settings:
            - `rtl_file` (`str` or `List[str]`) for synthesis
            - or `netlist_file` (`str`) for floorplanning
            - or `def_file` (`str`) for placement&routing
        - constraints:
            - `clk_port_name` (`str`)
            - `clk_freq_mhz` (`str`)
            - `core_util` (`float`) or `die_bbox`+`core_bbox` (both `str`)
        """

        uc_config = {key.upper(): value for key, value in config.items()}

        if (Keyword.TOP_NAME in uc_config):
            self.top_name = uc_config[Keyword.TOP_NAME]
        else:
            assert self.top_name, f"{Keyword.TOP_NAME} is required"

        self.path_setting = DesignPath(
            rtl_file=uc_config[Keyword.RTL_FILE],
            result_dir=uc_config.get(Keyword.RESULT_DIR, global_configs.DEFAULT_RESULT_DIR),
            netlist_file=uc_config.get(Keyword.NETLIST_FILE, global_configs.DEFAULT_NETLIST_FILE),
            def_file=uc_config.get(Keyword.DEF_FILE, global_configs.DEFAULT_DEF_FILE),
            gds_file=uc_config.get(Keyword.GDS_FILE, global_configs.DEFAULT_GDS_FILE),
        )

        self.constrain = DesignConstrain(
            clk_port_name=uc_config[Keyword.CLK_PORT_NAME],
            clk_freq_mhz=uc_config[Keyword.CLK_FREQ_MHZ],
            die_bbox=uc_config.get(Keyword.DIE_BBOX, ""),
            core_bbox=uc_config.get(Keyword.CORE_BBOX, ""),
            core_util=uc_config.get(Keyword.CORE_UTIL, 0),
        )

        if Keyword.FINISHED_STEP in uc_config:
            self.finished_step = uc_config[Keyword.FINISHED_STEP]
        if Keyword.EXPECTED_STEP in uc_config:
            self.expected_step = uc_config[Keyword.EXPECTED_STEP]

        self.config = uc_config

    def update2config(self, save_yaml: bool = False):
        self.last_update_time = self._strtime()
        self.config.update({
            Keyword.TOP_NAME: self.top_name,

            Keyword.RTL_FILE: self.path_setting.rtl_file,
            Keyword.RESULT_DIR: self.path_setting.result_dir,
            Keyword.NETLIST_FILE: self.path_setting.netlist_file,
            Keyword.DEF_FILE: self.path_setting.def_file,
            Keyword.GDS_FILE: self.path_setting.gds_file,

            Keyword.CLK_PORT_NAME: self.constrain.clk_port_name,
            Keyword.CLK_FREQ_MHZ: self.constrain.clk_freq_mhz,
            Keyword.DIE_BBOX: self.constrain.die_bbox,
            Keyword.CORE_BBOX: self.constrain.core_bbox,
            Keyword.CORE_UTIL: self.constrain.core_util,

            Keyword.FINISHED_STEP: self.finished_step,
            Keyword.EXPECTED_STEP: self.expected_step,
            Keyword.LAST_UPDATE_TIME: self.last_update_time,
        })

        if save_yaml:
            self.dump_config_yaml(override=True)

    def to_env(self) -> Dict[str, str]:
        """Get environment variables for running tools"""
        io_env = global_configs.ENV_TOOLS_PATH.copy()
        io_env[Keyword.TOP_NAME] = self.top_name
        io_env.update(self.path_setting.to_env_dict())
        io_env.update(self.constrain.to_env_dict())
        return io_env

    def dump_config_yaml(self, config_yaml: str = None, override: bool = False) -> str:
        """Dump the config to the yaml file"""
        config_dict = self.config

        if config_yaml is None:
            if override:
                config_yaml = self.config_yaml
            else:
                config_yaml = f"{self.config_yaml.split('.')[0]}_checkpoint_{self.last_update_time}_{self.finished_step}.yaml"
                path = pathlib.Path(config_yaml)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.touch()

        with open(config_yaml, "w", encoding="utf-8") as f:
            yaml.dump(config_dict, f)

        return config_yaml


if __name__ == "__main__":

    # minimal config
    config = {
        "top_name": "picorv32a",
        "rtl_file": "/home/user/RTL2GDS/design_zoo/picorv32a/picorv32a.v",
        "clk_port_name": "clk",
        "clk_freq_mhz": 100,
        "core_util": 0.6,
    }

    test_chip = Chip(config_dict=config)

    chip_config_yaml = test_chip.dump_config_yaml()
    from pprint import pprint
    pprint(test_chip.to_env())

    test_chip1 = Chip(config_yaml=chip_config_yaml)
    assert test_chip1.to_env() == test_chip.to_env()
    assert test_chip.config == test_chip1.config
