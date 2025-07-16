import argparse
import sys
import os
from pathlib import Path

try:
    from simulator import Simulator
    from cpu_test import CpuTestLogParser
    from benchmark import BenchmarkLogParser
except ImportError as e:
    print(f"Error: Could not import required classes.", file=sys.stderr)
    print(f"Make sure 'simulator.py', 'cpu_test.py', and 'benchmark.py' are accessible.", file=sys.stderr)
    print(f"Details: {e}", file=sys.stderr)
    sys.exit(1)

class MainWorkflow:
    """
    Orchestrates the entire Test -> Parse workflow.
    """
    def __init__(self, log_dir: Path, rtl_file: Path = None, mainargs: str = 'train', max_jobs: int = 4):
        self.log_dir = log_dir
        self.simulator = Simulator(rtl_file=rtl_file, max_parallel_jobs=max_jobs)
        self.mainargs = mainargs

    def run_parsers(self, executed_tests: list[str]):
        tasks_to_parse = set()
        if "cpu-tests" in executed_tests:
            tasks_to_parse.add("cpu-test")
        
        benchmark_tests_executed = any(t in executed_tests for t in ["coremark", "dhrystone", "microbench"])
        if benchmark_tests_executed:
            tasks_to_parse.add("benchmark")

        if not tasks_to_parse:
            print("No logs to parse based on the tests that were run.")
            return

        parser_map = {
            "cpu-test": CpuTestLogParser,
            "benchmark": BenchmarkLogParser
        }

        for task_name in tasks_to_parse:
            parser_class = parser_map[task_name]
            print(f"\nRunning parser for: {task_name}")
            try:
                parser_instance = parser_class(log_dir=str(self.log_dir))
                parser_instance.parse()
            except Exception as e:
                print(f"Error while running parser for {task_name}: {e}", file=sys.stderr)

    def execute(self, tests_arg: list[str]) -> bool:
        if not self.simulator._build_simulator():
            print("\nAborting workflow due to simulator build failure.", file=sys.stderr)
            sys.exit(1)

        if 'all' in tests_arg:
            selected_tests = self.simulator._discover_available_tests()
        else:
            selected_tests = tests_arg
        
        if not selected_tests:
            print("\nNo tests were selected or discovered. Workflow finished.")
            return True 

        print(f"\nWorkflow will execute the following tests: {', '.join(selected_tests)}")
        
        tests_passed = self.simulator.run_tests(
            tests_to_run=selected_tests, 
            mainargs=self.mainargs
        )

        if not tests_passed:
            print("\nWarning: Some tests failed. Proceeding with log parsing anyway.", file=sys.stderr)
        
        self.run_parsers(executed_tests=selected_tests)

        return tests_passed

def main():
    parser = argparse.ArgumentParser(
        description="A unified workflow to run tests and then parse their logs."
    )
    test_choices = list(Simulator._AVAILABLE_TESTS.keys()) + ['all']
    
    parser.add_argument('--log_dir', type=Path, default=Path(os.environ.get("RESULT_DIR", ".")), help="Directory for logs and JSON results.")
    parser.add_argument('--tests', nargs='*', choices=test_choices, default=['all'], help='Specify tests to run. Default="all" for auto-discovery.')
    parser.add_argument('--rtl_file', type=Path, help='Path to the RTL file for simulation')
    parser.add_argument('--mainargs', default='train', help='mainargs for microbench (default: train)')
    parser.add_argument('--max-parallel-jobs', type=int, default=4, help='Maximum number of tests to run in parallel')
    
    args = parser.parse_args()

    workflow = MainWorkflow(
        log_dir=args.log_dir,
        rtl_file=args.rtl_file,
        mainargs=args.mainargs,
        max_jobs=args.max_parallel_jobs
    )
    
    all_tests_succeeded = workflow.execute(tests_arg=args.tests)

    if all_tests_succeeded:
        print("\nWorkflow completed successfully (All tests passed).")
        sys.exit(0)
    else:
        print("\nWorkflow completed, but some tests failed. Please review the logs and JSON results.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()