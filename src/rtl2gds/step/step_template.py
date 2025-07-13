import json
import logging
import os
import resource
import subprocess
import time
from pathlib import Path
from string import Template

import yaml

from rtl2gds.global_configs import R2G_BASE_DIR, R2G_BIN_DIR, R2G_PDK_DIR_IHP130, R2G_TOOL_DIR, YSYX_HOME

STEP_CONFIG = os.path.dirname(os.path.abspath(__file__)) + "/step.yaml"


class Step:
    # construct R2G_TEMPLATE
    r2g_template_value = {
        "R2G_PDK_DIR_IHP130": R2G_PDK_DIR_IHP130,
        "R2G_BIN_DIR": R2G_BIN_DIR,
        "R2G_TOOL_DIR": R2G_TOOL_DIR,
        "R2G_BASE_DIR": R2G_BASE_DIR,
        "YSYX_HOME": YSYX_HOME,
    }

    def __init__(self, step_name: str):
        self.step_name: str = step_name
        # self.raw_config: dict[str, object]
        self.tool_name: str

        self.cmd_template: list[str]
        self.output_dir_template: str

        # will merge to shell_env at run time
        self.tool_env: dict[str, str]
        self.default_env: dict[str, str]  # fixed default env for EDA tool
        self.input_files: dict[str, str]  # rtl, def, sdc, etc
        self.input_parameters: dict[str, str]  # top_name, die/core_area_bbox, etc
        self.output_files: dict[str, str]
        self.output_metrics: dict[str, object]  # suppose to extract from output_files

        self._init_from_step_yaml()

    def _init_from_step_yaml(self):
        with open(STEP_CONFIG, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            step_config = config[self.step_name]
            # self.raw_config = step_config
            self.tool_name = step_config["tool_name"]
            self.cmd_template = step_config["cmd_template"]  # substitute at run time
            self.output_metrics = step_config["output_env"]["metrics"]
            self.output_dir_template = step_config["output_env"]["dir_template"]
            tool_env = None
            if "tool_env" in config and self.tool_name in config["tool_env"]:
                tool_env = config["tool_env"][self.tool_name]
            else:
                tool_env = {}
            input_files = step_config["input_env"].get("files", {})
            input_parameters = step_config["input_env"].get("parameters", {})
            output_files = step_config["output_env"].get("files", {})
            env = {**config["default_env"]}

        # make env upper case
        env = Step._upper_dict_key(env)
        tool_env = Step._upper_dict_key(tool_env)
        self.input_files = Step._upper_dict_key(input_files)
        self.input_parameters = Step._upper_dict_key(input_parameters)
        self.output_files = Step._upper_dict_key(output_files)

        # substitute yaml value variables from r2g_template_value
        self.tool_env = Step._substitute_template_dict(tool_env, Step.r2g_template_value)
        self.default_env = Step._substitute_template_dict(env, Step.r2g_template_value)
        logging.debug(
            "Init step.%s: \n[template] default_env:\n %s\n[template] tool_env:\n %s\n"
            "[template] input_files:\n %s\n[template] input_parameters:\n %s\n"
            "[template] output_files:\n %s\n[template] output_metrics:\n %s",
            self.step_name,
            self.default_env,
            self.tool_env,
            self.input_files,
            self.input_parameters,
            self.output_files,
            self.output_metrics,
        )

    @staticmethod
    def _check_files_exist(files: dict[str, str]):
        for name, path in files.items():
            # @TODO: should filter out list of RTL files
            if name == "RTL_FILE":
                continue
            if not Path(path).exists():
                raise FileNotFoundError(f"File {name}: {path} does not exist")

    @staticmethod
    def _substitute_template_list(list_str: list[str], template_value: dict[str, str]) -> list[str]:
        return [Template(_str).safe_substitute(template_value) for _str in list_str]

    @staticmethod
    def _substitute_template_dict(
        dict_str: dict[str, object], template_value: dict[str, str]
    ) -> dict[str, object]:
        env = dict_str.copy()
        for k, v in env.items():
            # for extra_env
            if isinstance(v, dict):
                env[k] = Step._substitute_template_dict(v, template_value)
                continue
            if not isinstance(v, str):
                logging.warning(
                    "_substitute_template_dict: dict['%s'] = %s is not string", k, str(v)
                )
                # convert to string and not substitute
                env[k] = str(v)
                continue
            env[k] = Template(v).safe_substitute(template_value)
        return env

    @staticmethod
    def _upper_dict_key(dict_str: dict[str, object]) -> dict[str, object]:
        res = {}
        for k, v in dict_str.items():
            if isinstance(v, dict):
                res[k] = Step._upper_dict_key(v)
                continue
            res[k.upper()] = v
        return res

    def _run_shell(self, shell_cmd: list[str], shell_env: dict[str, str], output_dir: str):
        """
        Note: this function is a pure subprocess run, without bussiness logic
        """
        env = os.environ.copy()
        env.update(shell_env)
        cmd_reproducible = {
            "cmd": shell_cmd,
            "env": env,
        }

        # Create log file path based on step name
        log_filename = "subprocess_runtime.log"
        log_path = os.path.join(output_dir, log_filename)

        # Ensure the output directory exists
        try:
            os.makedirs(output_dir, exist_ok=True)
        except OSError as e:
            logging.error(
                "(step.%s) Failed to create output directory %s: %s",
                self.step_name,
                output_dir,
                str(e),
            )
            raise

        logging.info(
            "(step.%s) \n subprocess cmd: %s \n subprocess env: %s",
            self.step_name,
            str(shell_cmd),
            str(shell_env),
        )

        try:
            start_time = time.perf_counter()
            rusage_start = resource.getrusage(resource.RUSAGE_CHILDREN)
            # @TODO: may add capture_output=True in the future
            # It is short for stdout=subprocess.PIPE and stderr=subprocess.PIPE
            # Now we redirect stderr to stdout
            e = subprocess.run(
                shell_cmd,
                check=True,
                text=True,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                env=env,
                timeout=2400,
            )
            rusage_end = resource.getrusage(resource.RUSAGE_CHILDREN)
            elapsed_time = time.monotonic() - start_time
            peak_memory_mb = (rusage_end.ru_maxrss - rusage_start.ru_maxrss) / 1024
            logging.info(
                "(step.%s) \n elapsed time: %s \n peak memory: %s MB",
                self.step_name,
                elapsed_time,
                peak_memory_mb,
            )

            # Save stdout/stderr output to log file
            try:
                with open(log_path, "w", encoding="utf-8") as log_file:
                    log_file.write(f"Command: {' '.join(shell_cmd)}\n")
                    log_file.write(f"Step: {self.step_name}\n")
                    log_file.write(f"Elapsed time: {elapsed_time:.2f} seconds\n")
                    log_file.write(f"Peak memory: {peak_memory_mb:.2f} MB\n")
                    log_file.write("=" * 80 + "\n")
                    log_file.write("STDOUT/STDERR OUTPUT:\n")
                    log_file.write("=" * 80 + "\n")
                    if e.stdout:
                        log_file.write(e.stdout)
                    else:
                        log_file.write("(No output captured)\n")
                logging.info("(step.%s) Subprocess output saved to: %s", self.step_name, log_path)
            except IOError as e_io:
                logging.error(
                    "(step.%s) Failed to write log file %s: %s", self.step_name, log_path, str(e_io)
                )
                # Don't raise here - the subprocess succeeded, just log writing failed

        except subprocess.CalledProcessError as e:
            # Save error output to log file even when subprocess fails
            try:
                with open(log_path, "w", encoding="utf-8") as log_file:
                    log_file.write(f"Command: {' '.join(shell_cmd)}\n")
                    log_file.write(f"Step: {self.step_name}\n")
                    log_file.write(f"Return code: {e.returncode}\n")
                    log_file.write("=" * 80 + "\n")
                    log_file.write("ERROR OUTPUT:\n")
                    log_file.write("=" * 80 + "\n")
                    if e.output:
                        log_file.write(e.output)
                    else:
                        log_file.write("(No output captured)\n")
                logging.error("(step.%s) Error output saved to: %s", self.step_name, log_path)
                raise
            except IOError:
                logging.error(
                    "(step.%s) Failed to write error log file %s", self.step_name, log_path
                )

            logging.error(
                "(step.%s) \n subprocess.CalledProcessError(return code: %d)",
                self.step_name,
                e.returncode,
            )
            raise
        except subprocess.TimeoutExpired as e:
            # Save timeout output to log file
            try:
                with open(log_path, "w", encoding="utf-8") as log_file:
                    log_file.write(f"Command: {' '.join(shell_cmd)}\n")
                    log_file.write(f"Step: {self.step_name}\n")
                    log_file.write("Process timed out after 1800 seconds\n")
                    log_file.write("=" * 80 + "\n")
                    log_file.write("TIMEOUT OUTPUT:\n")
                    log_file.write("=" * 80 + "\n")
                    if e.output:
                        log_file.write(e.output)
                    else:
                        log_file.write("(No output captured)\n")
                logging.info("(step.%s) Timeout output saved to: %s", self.step_name, log_path)
            except IOError:
                logging.error(
                    "(step.%s) Failed to write timeout log file %s", self.step_name, log_path
                )

            logging.error(
                "(step.%s) \n subprocess.TimeoutExpired",
                self.step_name,
            )
            raise

        subprocess_metrics = {
            "elapsed_time": elapsed_time,
            "peak_memory_mb": peak_memory_mb,
            "log_file": log_path,
        }

        return e.stdout, cmd_reproducible, subprocess_metrics

    @staticmethod
    def _update_matching_keys(base_dict: dict[str, str], updates: dict[str, str]) -> dict[str, str]:
        result = base_dict.copy()
        for key in updates.keys() & base_dict.keys():
            result[key] = updates[key]
        return result

    @staticmethod
    def _convert_to_abs_path(files: dict[str, str]) -> dict[str, str]:
        return {k: os.path.abspath(v) for k, v in files.items()}

    @staticmethod
    def _generate_resolved_env(
        env: dict[str, str],
        parameters: dict[str, str],
        template_value: dict[str, str] = {},
    ) -> dict[str, str]:
        parameters = Step._upper_dict_key(parameters)
        env = Step._update_matching_keys(env, parameters)
        env = Step._substitute_template_dict(env, {**Step.r2g_template_value, **template_value})
        return env

    @staticmethod
    def _add_dir_to_file_paths(file_paths: dict[str, str], dir_path: str) -> dict[str, str]:
        processed = {}
        for key, path in file_paths.items():
            expanded_path = os.path.expanduser(path)
            if os.path.isabs(expanded_path):
                processed[key] = expanded_path
            else:
                processed[key] = os.path.join(dir_path, expanded_path)
        return processed

    def process_output_files(
        self, user_parameters: dict[str, str], output_base_dir: str, output_prefix: str
    ):
        # construct output template
        # see rule '6. Special reminder for outputs' in `step.yaml`
        output_template_value = {
            "OUTPUT_PREFIX": output_prefix,
            "OUTPUT_STEP_NAME": self.step_name,
            "OUTPUT_TOP_NAME": user_parameters["TOP_NAME"],
        }
        output_files = Step._generate_resolved_env(
            self.output_files, user_parameters, output_template_value
        )
        output_dir_name = Template(self.output_dir_template).safe_substitute(output_template_value)
        output_dir = os.path.join(output_base_dir, output_dir_name)
        output_files = Step._add_dir_to_file_paths(file_paths=output_files, dir_path=output_dir)
        for file in output_files.values():
            os.makedirs(os.path.dirname(file), exist_ok=True)
        output_files["RESULT_DIR"] = output_dir
        return output_files

    def process_input_files(self, user_parameters: dict[str, str]):
        tmp_files = Step._generate_resolved_env(self.input_files, user_parameters)
        input_files = {k: os.path.abspath(v) for k, v in tmp_files.items() if v != "__optional__"}
        return input_files

    def process_input_parameters(self, user_parameters: dict[str, str]):
        return Step._generate_resolved_env(self.input_parameters, user_parameters)

    def process_shell_cmd(self, merged_env: dict[str, str]):
        return Step._substitute_template_list(self.cmd_template, merged_env)

    def process_shell_env(self, merged_env: dict[str, str]):
        shell_env = {**self.default_env, **merged_env}
        if "extra_env" in self.tool_env:
            shell_env.update(self.tool_env["extra_env"])

        from rtl2gds.global_configs import _USE_PROJ_BIN_LIB

        if _USE_PROJ_BIN_LIB:
            shell_env["PATH"] = os.pathsep.join(
                [self.tool_env.get("PATH", ""), os.environ.get("PATH", "")]
            )
            shell_env["LD_LIBRARY_PATH"] = os.pathsep.join(
                [self.tool_env.get("LD_LIBRARY_PATH", ""), os.environ.get("LD_LIBRARY_PATH", "")]
            )
        else:
            shell_env["PATH"] = os.environ.get("PATH", "")
            shell_env["LD_LIBRARY_PATH"] = os.environ.get("LD_LIBRARY_PATH", "")
        return shell_env

    def run(self, parameters: dict[str, str], output_prefix: str = "rtl2gds"):
        input_files = self.process_input_files(parameters)
        Step._check_files_exist(input_files)
        input_parameters = self.process_input_parameters(parameters)
        # generate actual RESULT_DIR path
        # @TODO: should be a better way to handle RESULT_DIR
        # @idea: we need two levels of RESULT_DIR: 1. base(project) result_dir 2. step(task) result_dir
        if "RESULT_DIR" in parameters:
            output_base_dir = parameters["RESULT_DIR"]
        else:
            output_base_dir = self.default_env["RESULT_DIR"]
        output_files = self.process_output_files(input_parameters, output_base_dir, output_prefix)

        logging.info("(step.%s) input_files: %s", self.step_name, input_files)
        logging.info("(step.%s) user_parameters: %s", self.step_name, input_parameters)
        logging.info("(step.%s) output_files: %s", self.step_name, output_files)

        merged_env = {
            **Step.r2g_template_value,
            **parameters,
            **input_files,
            **input_parameters,
            **output_files,
        }
        shell_cmd = self.process_shell_cmd(merged_env)
        shell_env = self.process_shell_env(merged_env)

        from rtl2gds.utils.time import end_step_timer, start_step_timer

        start_datetime, start_time, timer_step_name = start_step_timer(step_name=self.step_name)
        runtime_log, cmd_reproducible, subprocess_metrics = self._run_shell(
            shell_cmd, shell_env, output_files["RESULT_DIR"]
        )
        end_step_timer(
            start_datetime=start_datetime,
            start_time=start_time,
            step_name=timer_step_name,
        )

        Step._check_files_exist(output_files)

        step_reproducible = {
            "shell": cmd_reproducible,
            "input_files": input_files,
            "parameters": input_parameters,
            "output_files": output_files,
        }

        with open(f"{output_files['RESULT_DIR']}/reproducible.json", "w", encoding="utf-8") as f:
            json.dump(step_reproducible, f, indent=4)
        with open(f"{output_files['RESULT_DIR']}/metrics.json", "w", encoding="utf-8") as f:
            json.dump(subprocess_metrics, f, indent=4)

        return runtime_log, step_reproducible, subprocess_metrics


if __name__ == "__main__":
    # tests:
    logging.basicConfig(level=logging.INFO)

    # inputs
    rtl_file = f"{R2G_BASE_DIR}/demo/minirv.sv"
    top_name = "minirv"   # ysyx_22050499
    clk_port_name = "clock"
    clk_freq_mhz = "100"
    netlist_file = "minirv_nl.v"
    core_util = "0.5"

    timing_patch = {
        "SDC_FILE": f"{R2G_TOOL_DIR}/default.sdc",
        "CLK_PORT_NAME": clk_port_name,
        "CLK_FREQ_MHZ": clk_freq_mhz,
    }

    num_executed_steps = 1

    def run_step(step_name: str, parameters: dict[str, str]):
        global num_executed_steps
        step = Step(step_name)
        _, reproducible, _ = step.run(parameters, f"{num_executed_steps:02d}")
        num_executed_steps += 1
        return reproducible

    test_benchmark = {
        "TOP_NAME": top_name,
        "STAGE": "D",
        "ARCH": "minirv-minirv",
        "MAX_SIMULATE_TIME": "1000000000",
        "TESTS": "cpu-tests",  # or "coremark", "dhrystone", "cpu-tests", "all"
        "MICROBENCH_ARGS": "test",  # or "train"
    }
    run_step("benchmark", test_benchmark)

    test_synth = {
        "RTL_FILE": rtl_file,
        "TOP_NAME": top_name,
        "NETLIST_FILE": netlist_file,
    }
    reproducible = run_step("synthesis", test_synth)

    test_sta = {
        "USE_VERILOG": "true",
        "INPUT_VERILOG": reproducible["output_files"]["NETLIST_FILE"],
        "TOP_NAME": top_name,
    }
    test_sta.update(timing_patch)
    run_step("sta", test_sta)

    test_floorplan = {
        "NETLIST_FILE": reproducible["output_files"]["NETLIST_FILE"],
        "TOP_NAME": top_name,
        # "CORE_UTIL": core_util,
        "USE_FIXED_BBOX": "true",
        "DIE_BBOX": "0 0 410 410",
        "CORE_BBOX": "10 10 400 400",
    }
    test_floorplan.update(timing_patch)
    reproducible = run_step("floorplan", test_floorplan)

    test_netlist_opt = {
        "INPUT_DEF": reproducible["output_files"]["OUTPUT_DEF"],
        "TOP_NAME": top_name,
    }
    test_netlist_opt.update(timing_patch)
    reproducible = run_step("netlist_opt", test_netlist_opt)

    test_placement = {
        "INPUT_DEF": reproducible["output_files"]["OUTPUT_DEF"],
        "TOP_NAME": top_name,
    }
    test_placement.update(timing_patch)
    reproducible = run_step("placement", test_placement)

    test_cts = {
        "INPUT_DEF": reproducible["output_files"]["OUTPUT_DEF"],
        "TOP_NAME": top_name,
    }
    test_cts.update(timing_patch)
    reproducible = run_step("cts", test_cts)

    test_legalization = {
        "INPUT_DEF": reproducible["output_files"]["OUTPUT_DEF"],
        "TOP_NAME": top_name,
    }
    test_legalization.update(timing_patch)
    reproducible = run_step("legalization", test_legalization)

    test_routing = {
        "INPUT_DEF": reproducible["output_files"]["OUTPUT_DEF"],
        "TOP_NAME": top_name,
    }
    test_routing.update(timing_patch)
    reproducible = run_step("routing", test_routing)

    test_fill = {
        "INPUT_DEF": reproducible["output_files"]["OUTPUT_DEF"],
        "TOP_NAME": top_name,
    }
    test_fill.update(timing_patch)
    reproducible = run_step("filler", test_fill)

    test_gds = {
        "INPUT_DEF": reproducible["output_files"]["OUTPUT_DEF"],
        "TOP_NAME": top_name,
        "DIE_BBOX": "0 0 410 410",
    }
    reproducible = run_step("gds", test_gds)

    test_drc = {
        "GDS_FILE": reproducible["output_files"]["GDS_FILE"],
        "TOP_NAME": top_name,
    }
    run_step("drc", test_drc)