import subprocess
import sys
import os

class LogParser:
    def __init__(self, script_dir):
        self.script_dir = script_dir

    def run_script(self, script_path):
        print(f"Running {script_path} ...")
        result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
        print(result.stdout)
        if result.returncode != 0:
            print(f"Error running {script_path}:\n{result.stderr}")

    def main(self):
        test_py = os.path.join(self.script_dir, "cpu-test.py")
        benchmark_py = os.path.join(self.script_dir, "benchmark.py")
        self.run_script(test_py)
        self.run_script(benchmark_py)

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    LogParser(script_dir).main()