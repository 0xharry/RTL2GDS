import sys
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mainargs', default='train')
    parser.add_argument('--tests', nargs='*', choices=['cpu-tests', 'coremark', 'dhrystone', 'microbench', 'all'], default=['all'])
    args, unknown = parser.parse_known_args()

    from simulate import Simulator
    Simulator.run(args)

    from cpu_test import CpuTestLogParser
    from benchmark import BenchmarkLogParser
    import os

    log_dir = os.environ.get("RESULT_DIR")
    CpuTestLogParser(log_dir).parse()
    BenchmarkLogParser(log_dir).parse()

if __name__ == "__main__":
    main()