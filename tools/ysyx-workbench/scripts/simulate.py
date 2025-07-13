import os
import subprocess
import argparse
import re
from pathlib import Path
import concurrent.futures
from rtl2gds.global_configs import R2G_BASE_DIR, YSYX_HOME

class Simulator:
    def __init__(self, rtl_file=None, config_path=None):
        self.ysyx_home = YSYX_HOME
        self.r2g_base = R2G_BASE_DIR
        self.am_kernels_home = os.environ.get("AM_KERNELS_HOME")
        self.npc_home = os.environ.get("NPC_HOME")
        self.top_name = os.environ.get("TOP_NAME")
        self.arch = os.environ.get("ARCH")
        self.rtl_file = rtl_file

    @staticmethod
    def run_make(cmd):
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd)
        if result.returncode != 0:
            print(f"Command failed: {' '.join(cmd)}")
        return result.returncode

    def run_tests(self, mainargs="test", tests=None):
        if tests is None:
            tests = ["cpu-tests", "coremark", "dhrystone", "microbench"]
        cross_compile = os.environ.get("CROSS_COMPILE", "riscv64-linux-gnu-")
        arch = self.arch if self.arch else "riscv32e-ysyxsoc"

        rtl_arg = []
        if self.rtl_file:
            rtl_arg = [f"RTL_FILE={self.rtl_file}"]
        
        test_cmds = {
            "cpu-tests": ["make", "-C", f"{self.am_kernels_home}/tests/cpu-tests", f"ARCH={arch}", f"CROSS_COMPILE={cross_compile}", "-j4", "run"] + rtl_arg,
            "coremark": ["make", "-C", f"{self.am_kernels_home}/benchmarks/coremark", f"ARCH={arch}", f"CROSS_COMPILE={cross_compile}", "-j1", "run"] + rtl_arg,
            "dhrystone": ["make", "-C", f"{self.am_kernels_home}/benchmarks/dhrystone", f"ARCH={arch}", f"CROSS_COMPILE={cross_compile}", "-j1", "run"] + rtl_arg,
            "microbench": ["make", "-C", f"{self.am_kernels_home}/benchmarks/microbench", f"ARCH={arch}", f"CROSS_COMPILE={cross_compile}", f"mainargs={mainargs}", "-j1", "run"] + rtl_arg,
        }
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(self.run_make, test_cmds[test]) for test in tests]
            for future in concurrent.futures.as_completed(futures):
                rc = future.result()
                if rc != 0:
                    print("One of the make commands failed.")

    @classmethod
    def run(cls, args=None):
        if args is None:
            parser = argparse.ArgumentParser(description="Run am-kernels simulation tests.")
            parser.add_argument('--mainargs', default='train', help='mainargs for microbench (default: train)')
            parser.add_argument('--tests', nargs='*', choices=['cpu-tests', 'coremark', 'dhrystone', 'microbench', 'all'],
                                default=['all'], help='Specify which tests to run')
            parser.add_argument('--rtl_file', help='Path to the RTL file for simulation')
            args = parser.parse_args()

        rtl_file = getattr(args, 'rtl_file', None)
        sim = cls(rtl_file=rtl_file)

        make_all_cmd = f"make -C {sim.npc_home} all"
        if sim.rtl_file:
            make_all_cmd += f" RTL_FILE={sim.rtl_file}"
        os.system(make_all_cmd)

        selected_tests = ["cpu-tests", "coremark", "dhrystone", "microbench"] if 'all' in args.tests else args.tests
        sim.run_tests(mainargs=args.mainargs, tests=selected_tests)

if __name__ == "__main__":
    Simulator.run()