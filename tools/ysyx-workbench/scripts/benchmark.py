import os
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, Iterable, Tuple, List
import argparse
import sys

class BenchmarkLogParser:
    """
    Parses multiple benchmark log files (CoreMark, Dhrystone, MicroBench)
    to generate a single, structured JSON summary.
    """
    # CoreMark Regex
    _CM_SIZE_RE = re.compile(r"CoreMark Size\s*:\s*(\d+)")
    _CM_TIME_RE = re.compile(r"Total time \(ms\)\s*:\s*(\d+)")
    _CM_ITER_RE = re.compile(r"Iterations\s*:\s*(\d+)")
    _CM_CRC_RE = re.compile(r"\[0\]crc\w+\s*:\s*0x([0-9a-fA-F]{4})")
    _CM_FINAL_RE = re.compile(r"CoreMark (PASS|FAIL)\s+([\d.]+)", re.IGNORECASE)

    # Dhrystone Regex
    _DH_ITER_RE = re.compile(r"Trying\s+(\d+)\s+runs")
    _DH_TIME_RE = re.compile(r"Finished in\s+(\d+)\s*ms")
    _DH_FINAL_RE = re.compile(r"Dhrystone (PASS|FAIL)\s+([\d.]+)", re.IGNORECASE)

    # MicroBench Regex
    _MB_INPUT_RE = re.compile(r'input \*(.*?)\*')
    _MB_TEST_RE = re.compile(r"\[(\w+)\]\s+(.+?):\s+\*\s+(\w+)\.")
    _MB_SCORED_TIME_RE = re.compile(r"Scored time:\s*([\d.]+)\s*ms")
    _MB_TOTAL_TIME_RE = re.compile(r"Total\s+time:\s*([\d.]+)\s*ms")
    _MB_FINAL_RE = re.compile(r"MicroBench (PASS|FAIL)", re.IGNORECASE)

    def __init__(self, log_dir: str):
        if not log_dir:
            raise ValueError("log_dir cannot be empty.")
        
        top_name = os.environ.get("TOP_NAME", "unknown_top")
        log_path = Path(log_dir)
        
        self.log_files = {
            "coremark": log_path / f"{top_name}_coremark.log",
            "dhrystone": log_path / f"{top_name}_dhrystone.log",
            "microbench": log_path / f"{top_name}_microbench.log",
        }
        self.result_json = log_path / f"{top_name}_benchmark.json"
        
        self.result_json.parent.mkdir(parents=True, exist_ok=True)

    def _parse_coremark(self, lines: Iterable[str]) -> Dict[str, Any]:
        results: Dict[str, Any] = {"status": "FAIL", "details": {}}
        crc_values: List[str] = []

        for line in lines:
            if (m := self._CM_SIZE_RE.search(line)):
                results["details"]["CoreMark Size"] = int(m.group(1))
            elif (m := self._CM_TIME_RE.search(line)):
                results["details"]["Total time (ms)"] = int(m.group(1))
            elif (m := self._CM_ITER_RE.search(line)):
                results["details"]["Iterations"] = int(m.group(1))
            elif (m := self._CM_CRC_RE.search(line)):
                crc_values.append(m.group(1))
            elif (m := self._CM_FINAL_RE.search(line)):
                results["status"] = m.group(1).upper()
                results["details"]["Marks"] = m.group(2)
        
        crc_pass = all(val == crc_values[0] for val in crc_values if crc_values)
        results["details"]["crc_values"] = crc_values
        results["details"]["crc_check"] = "PASS" if crc_pass else "FAIL"
        
        if results["status"] == "PASS" and not crc_pass:
            results["status"] = "FAIL"

        return results

    def _parse_dhrystone(self, lines: Iterable[str]) -> Dict[str, Any]:
        results: Dict[str, Any] = {"status": "FAIL", "details": {}}
        for line in lines:
            if (m := self._DH_ITER_RE.search(line)):
                results["details"]["Iterations"] = int(m.group(1))
            elif (m := self._DH_TIME_RE.search(line)):
                results["details"]["Total time (ms)"] = int(m.group(1))
            elif (m := self._DH_FINAL_RE.search(line)):
                results["status"] = m.group(1).upper()
                results["details"]["Marks"] = m.group(2)
        return results

    def _parse_microbench(self, lines: Iterable[str]) -> Dict[str, Any]:
        results: Dict[str, Any] = {"status": "FAIL", "details": {"tests": []}}
        pass_count = 0
        for line in lines:
            if (m := self._MB_INPUT_RE.search(line)):
                results["details"]["input"] = m.group(1)
            elif (m := self._MB_TEST_RE.match(line)):
                test_result = {"name": m.group(1), "desc": m.group(2).strip(), "result": m.group(3)}
                results["details"]["tests"].append(test_result)
                if test_result["result"].lower() == "passed":
                    pass_count += 1
            elif (m := self._MB_SCORED_TIME_RE.search(line)):
                results["details"]["Scored time (ms)"] = float(m.group(1))
            elif (m := self._MB_TOTAL_TIME_RE.search(line)):
                results["details"]["Total time (ms)"] = float(m.group(1))
            elif (m := self._MB_FINAL_RE.search(line)):
                results["status"] = m.group(1).upper()
        
        total_count = len(results["details"]["tests"])
        results["summary"] = {
            "passed": pass_count, "total": total_count,
            "pass_rate": f"{pass_count/total_count:.2%}" if total_count > 0 else "N/A"
        }
        return results

    def _parse_single_log(self, name: str, parser_func) -> Dict[str, Any]:
        log_file = self.log_files.get(name)
        if not log_file or not log_file.is_file():
            return {"status": "FAIL", "error": f"Log file not found at {log_file}"}
        
        try:
            with log_file.open("r", encoding="utf-8") as f:
                return parser_func(f)
        except Exception as e:
            return {"status": "FAIL", "error": f"Error parsing {log_file}: {e}"}

    def parse(self):
        benchmark_results = {
            "coremark": self._parse_single_log("coremark", self._parse_coremark),
            "dhrystone": self._parse_single_log("dhrystone", self._parse_dhrystone),
            "microbench": self._parse_single_log("microbench", self._parse_microbench),
        }

        final_report = {
            "metadata": {
                "source_logs": {k: str(v) for k, v in self.log_files.items()},
                "parser": self.__class__.__name__,
                "parsed_at_utc": datetime.now(timezone.utc).isoformat(),
                "parsed_by":  os.environ.get("USER", "unknown_user"),
            },
            "benchmarks": benchmark_results
        }
        
        self._write_json(final_report)
        self._print_summary(final_report)

    def _write_json(self, data: Dict[str, Any]):
        try:
            with self.result_json.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error: Could not write JSON to {self.result_json}. Reason: {e}", file=sys.stderr)

    def _print_summary(self, report: Dict[str, Any]):
        print("Benchmark Summary:")
        for name, result in report.get("benchmarks", {}).items():
            status = result.get('status', 'FAIL')
            summary_str = ""
            if name == "microbench" and "summary" in result:
                summary = result["summary"]
                summary_str = f"({summary['passed']}/{summary['total']})"
            elif name == "coremark" and result.get("details", {}).get("crc_check"):
                summary_str = f"(CRC Check: {result['details']['crc_check']})"

            print(f"- {name:<12}: {status} {summary_str}")
        print(f"Result JSON saved to: {self.result_json}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse benchmark logs into a JSON summary.")
    parser.add_argument(
        "--log_dir",
        type=str,
        default=os.environ.get("LOG_DIR", "./log"),
        help="Directory containing the log files. Defaults to LOG_DIR env var or './log'."
    )
    args = parser.parse_args()
    
    try:
        log_parser = BenchmarkLogParser(log_dir=args.log_dir)
        log_parser.parse()
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)