import os
import subprocess
import argparse
import re
from pathlib import Path
import concurrent.futures

class Simulator:
    def __init__(self, config_path=None):
        self.ysyx_home = os.environ.get("YSYX_HOME")
        self.am_kernels_home = os.environ.get("AM_KERNELS_HOME")
        self.npc_home = os.environ.get("NPC_HOME")
        self.top_name = os.environ.get("TOP_NAME")
        self.arch = os.environ.get("ARCH")

    def patch_soc_full_v(self):
        src_v = os.path.join(self.ysyx_home, "ysyxSoC/ysyxSoCFull.v")
        dst_v = os.path.join(self.npc_home, "vsrc/ysyxSoCFull.v")
        src_v = os.path.expandvars(src_v)
        dst_v = os.path.expandvars(dst_v)
        if not os.path.isfile(src_v):
            raise FileNotFoundError(f"File not found: {src_v}")
        os.makedirs(os.path.dirname(dst_v), exist_ok=True)
        subprocess.run(["cp", src_v, dst_v], check=True)
        with open(dst_v, "r", encoding="utf-8") as f:
            content = f.read()
        if f"module {self.top_name}" not in content:
            new_content = re.sub(r"ysyx_00000000", self.top_name, content)
            with open(dst_v, "w", encoding="utf-8") as f:
                f.write(new_content)

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
        test_cmds = {
            "cpu-tests": ["make", "-C", f"{self.am_kernels_home}/tests/cpu-tests", f"ARCH={arch}", f"CROSS_COMPILE={cross_compile}", "-j8", "run"],
            "coremark": ["make", "-C", f"{self.am_kernels_home}/benchmarks/coremark", f"ARCH={arch}", f"CROSS_COMPILE={cross_compile}", "-j1", "run"],
            "dhrystone": ["make", "-C", f"{self.am_kernels_home}/benchmarks/dhrystone", f"ARCH={arch}", f"CROSS_COMPILE={cross_compile}", "-j1", "run"],
            "microbench": ["make", "-C", f"{self.am_kernels_home}/benchmarks/microbench", f"ARCH={arch}", f"CROSS_COMPILE={cross_compile}", f"mainargs={mainargs}", "-j1", "run"],
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
            args = parser.parse_args()
        sim = cls()
        sim.patch_soc_full_v()
        os.system(f"make -C {sim.npc_home} all")
        selected_tests = ["cpu-tests", "coremark", "dhrystone", "microbench"] if 'all' in args.tests else args.tests
        sim.run_tests(mainargs=args.mainargs, tests=selected_tests)

if __name__ == "__main__":
    Simulator.run()