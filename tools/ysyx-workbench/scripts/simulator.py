import os
import sys
import subprocess
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import concurrent.futures
import math

# --- 环境检查 (保持不变) ---
try:
    YSYX_HOME = Path(os.environ["YSYX_HOME"])
    AM_KERNELS_HOME = Path(os.environ["AM_KERNELS_HOME"])
    NPC_HOME = Path(os.environ["NPC_HOME"])
    TOP_NAME = os.environ.get("TOP_NAME", "ysyxSoCFull")
    ARCH = os.environ.get("ARCH", "riscv32e-ysyxsoc")
    CROSS_COMPILE = os.environ.get("CROSS_COMPILE", "riscv64-linux-gnu-")
    CPU_COUNT = os.cpu_count() or 1
except KeyError as e:
    print(f"Error: Environment variable {e} is not set. Please source your environment setup script.", file=sys.stderr)
    sys.exit(1)


class Simulator:
    """
    A parallel test simulator that can auto-discover available tests
    """

    _AVAILABLE_TESTS: Dict[str, Dict[str, any]] = {
        "cpu-tests": {
            "path": AM_KERNELS_HOME / "tests" / "cpu-tests",
            "type": "test"
        },
        "coremark": {
            "path": AM_KERNELS_HOME / "benchmarks" / "coremark",
            "type": "benchmark"
        },
        "dhrystone": {
            "path": AM_KERNELS_HOME / "benchmarks" / "dhrystone",
            "type": "benchmark"
        },
        "microbench": {
            "path": AM_KERNELS_HOME / "benchmarks" / "microbench",
            "type": "benchmark"
        },
    }

    def __init__(self, rtl_file: Optional[Path] = None, max_parallel_jobs: int = 4):
        self.rtl_file = rtl_file
        self.max_parallel_jobs = min(max_parallel_jobs, CPU_COUNT)
        self._validate_paths()

    def _validate_paths(self):
        for name, path in [("AM_KERNELS_HOME", AM_KERNELS_HOME), ("NPC_HOME", NPC_HOME)]:
            if not path.is_dir():
                print(f"Error: Path for {name} ('{path}') does not exist or is not a directory.", file=sys.stderr)
                sys.exit(1)
        print("Environment and paths validated successfully.")

    @staticmethod
    def _run_command(cmd: List[str], title: str) -> Tuple[str, int, str, str]:
        print(f"Starting: {title}")
        result = subprocess.run(cmd, capture_output=True, text=True, errors='replace')
        return title, result.returncode, result.stdout, result.stderr

    def _build_simulator(self) -> bool:
        title = "Build Verilator Simulator"
        cmd = ["make", "-C", str(NPC_HOME), "all", f"-j{CPU_COUNT}"]
        if self.rtl_file:
            cmd.append(f"RTL_FILE={self.rtl_file}")
        
        print(f"\nExecuting: {title}")
        print(f"Command: {' '.join(cmd)}")
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors='replace')
        for line in iter(proc.stdout.readline, ''):
            sys.stdout.write(line)
        rc = proc.wait()

        if rc != 0:
            print(f"Failed: {title} returned error code {rc}.")
            return False
        
        print(f"Success: {title} finished.")
        return True

    def _discover_available_tests(self) -> List[str]:
        """
        Checks for the existence of test directories and returns a list of available tests.
        """
        print("\nAuto-discovering available tests (checking directories)...")
        discovered_tests = []
        for name, info in self._AVAILABLE_TESTS.items():
            if info["path"].is_dir():
                print(f"  - Found: {name}")
                discovered_tests.append(name)
            else:
                print(f"  - Not found, skipping: {name} (directory '{info['path']}' is missing)")
        return discovered_tests

    def run_tests(self, tests_to_run: List[str], mainargs: str) -> bool:
        if not tests_to_run:
            print("\nWarning: No tests selected or discovered to run.")
            return True

        num_tests = len(tests_to_run)
        num_parallel_jobs = min(num_tests, self.max_parallel_jobs)
        cores_per_job = max(1, math.floor(CPU_COUNT / num_parallel_jobs))
        
        print(f"\nRunning {num_tests} tests in parallel using up to {num_parallel_jobs} workers.")
        print(f"Allocating ~{cores_per_job} cores per test job.")

        test_results: Dict[str, bool] = {}
        all_passed = True

        with concurrent.futures.ThreadPoolExecutor(max_workers=num_parallel_jobs) as executor:
            futures = []
            for test_name in tests_to_run:
                test_info = self._AVAILABLE_TESTS.get(test_name)
                if not test_info:
                    print(f"Warning: Unknown test '{test_name}' specified in list. Skipping.")
                    continue
                
                test_dir = test_info["path"]
                specific_args = []
                if test_name == "microbench":
                    specific_args.append(f"mainargs={mainargs}")
                
                common_args = [f"-j{cores_per_job}", f"ARCH={ARCH}", f"CROSS_COMPILE={CROSS_COMPILE}", "run"]
                if self.rtl_file:
                    common_args.append(f"RTL_FILE={self.rtl_file}")
                
                cmd = ["make", "-C", str(test_dir)] + common_args + specific_args
                futures.append(executor.submit(self._run_command, cmd, test_name))

            for future in concurrent.futures.as_completed(futures):
                title, rc, stdout, stderr = future.result()
                if rc == 0:
                    print(f"Success: {title} finished.")
                    test_results[title] = True
                else:
                    print(f"Failed: {title} returned error code {rc}.", file=sys.stderr)
                    sys.stderr.write(f"\n--- ERROR OUTPUT FOR [{title}] ---\n")
                    sys.stderr.write(stdout)
                    sys.stderr.write(stderr)
                    sys.stderr.write(f"--- END OF ERROR OUTPUT FOR [{title}] ---\n\n")
                    test_results[title] = False
                    all_passed = False

        print("\nFinal Test Summary:")
        sorted_results = {name: test_results.get(name, False) for name in tests_to_run}
        for name, passed in sorted_results.items():
            status = "PASSED" if passed else "FAILED"
            print(f"- {name:<12}: {status}")
        
        return all_passed

    # 我们保留 main 方法，以防您需要独立运行此脚本进行调试
    @classmethod
    def main(cls):
        parser = argparse.ArgumentParser(description="Run am-kernels tests. Auto-discovers tests if 'all' is specified.")
        parser.add_argument('--mainargs', default='train', help='mainargs for microbench (default: train)')
        parser.add_argument(
            '--tests', nargs='*', 
            choices=list(cls._AVAILABLE_TESTS.keys()) + ['all'],
            default=['all'], 
            help='Specify which tests to run. Default is "all", which auto-discovers available tests.'
        )
        parser.add_argument('--rtl_file', type=Path, help='Path to the RTL file for simulation')
        parser.add_argument('--max-parallel-jobs', type=int, default=4, help='Maximum number of tests to run in parallel')
        args = parser.parse_args()

        sim = cls(rtl_file=args.rtl_file, max_parallel_jobs=args.max_parallel_jobs)

        if not sim._build_simulator():
            print("\nAborting due to simulator build failure.", file=sys.stderr)
            sys.exit(1)

        if 'all' in args.tests:
            selected_tests = sim._discover_available_tests()
        else:
            selected_tests = args.tests
        
        all_tests_passed = sim.run_tests(tests_to_run=selected_tests, mainargs=args.mainargs)

        if not all_tests_passed:
            print("\nSome tests failed. Please review the error output above.", file=sys.stderr)
            sys.exit(1)

        print("\nAll executed tests completed successfully!")


if __name__ == "__main__":
    Simulator.main()