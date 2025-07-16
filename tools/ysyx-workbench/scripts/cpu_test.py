import os
import json
import re
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Iterable, Tuple
import argparse
import sys
from pathlib import Path

class CpuTestLogParser:
    """
    Parses a CPU test log file to generate a structured JSON summary.
    """

    _TEST_LINE_RE = re.compile(
        r"^\[\s*(?P<name>[^\]]+?)\s*\]\s+(?P<status>PASS|FAIL)\s+(?P<time>[\d.]+)(?P<unit>s|ms|us)",
        re.IGNORECASE
    )
    _TOTAL_TIME_RE = re.compile(
        r"^\[\s*Total Time\s*\]\s+(?P<time>[\d.]+)(?P<unit>s|ms|us)",
        re.IGNORECASE
    )

    def __init__(self, log_dir: str):
        if not log_dir:
            raise ValueError("log_dir cannot be empty.")
            
        top_name = os.environ.get("TOP_NAME", "unknown_top")
        self.log_file = Path(log_dir) / f"{top_name}_cpu_test.log"
        self.result_json = Path(log_dir) / f"{top_name}_cpu_test.json"
        
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def _convert_to_seconds(self, time_str: str, unit: str) -> float:
        try:
            time_val = float(time_str)
            if unit.lower() == 'ms':
                return time_val / 1000.0
            if unit.lower() == 'us':
                return time_val / 1_000_000.0
            return time_val
        except (ValueError, TypeError):
            return -1.0

    def _parse_lines(self, lines: Iterable[str]) -> Tuple[Dict[str, Any], Optional[float]]:
        test_details: Dict[str, Any] = {}
        total_exec_time: Optional[float] = None

        for line in lines:
            m_test = self._TEST_LINE_RE.match(line)
            if m_test:
                data = m_test.groupdict()
                elapsed_s = self._convert_to_seconds(data['time'], data['unit'])
                test_details[data['name']] = {
                    "status": data['status'].upper(),
                    "time_s": elapsed_s
                }
                continue

            m_total = self._TOTAL_TIME_RE.match(line)
            if m_total:
                data = m_total.groupdict()
                total_exec_time = self._convert_to_seconds(data['time'], data['unit'])
        
        return test_details, total_exec_time

    def parse(self):
        if not self.log_file.is_file():
            error_msg = f"Log file not found at {self.log_file}"
            print(f"Error: {error_msg}")
            summary = self._create_error_summary(error_msg)
            self._write_json(summary)
            return

        try:
            with self.log_file.open("r", encoding="utf-8") as f:
                test_details, total_exec_time = self._parse_lines(f)
        except Exception as e:
            error_msg = f"An unexpected error occurred while parsing {self.log_file}: {e}"
            print(f"Error: {error_msg}")
            summary = self._create_error_summary(error_msg)
            self._write_json(summary)
            return

        pass_count = sum(1 for detail in test_details.values() if detail["status"] == "PASS")
        total_count = len(test_details)
        all_pass = (pass_count == total_count) and (total_count > 0)

        summary_data = {
            "overall_status": "PASS" if all_pass else "FAIL",
            "total_tests": total_count,
            "passed": pass_count,
            "failed": total_count - pass_count,
            "pass_rate": f"{pass_count/total_count:.2%}" if total_count > 0 else "N/A",
            "total_execution_time_s": total_exec_time,
        }
        
        final_report = {
            "metadata": {
                "source_log_file": str(self.log_file),
                "parser": self.__class__.__name__,
                "parsed_at_utc": datetime.now(timezone.utc).isoformat(),
                "parsed_by": os.environ.get("USER", "unknown_user"),
            },
            "summary": summary_data,
            "details": test_details
        }

        self._write_json(final_report)
        
        print(f"CPU Test Summary: {summary_data['overall_status']} ({summary_data['passed']}/{summary_data['total_tests']})")
        if summary_data['total_execution_time_s'] is not None:
            print(f"Total Execution Time: {summary_data['total_execution_time_s']:.3f}s")
        print(f"Result JSON saved to: {self.result_json}")

    def _create_error_summary(self, error_message: str) -> Dict[str, Any]:
        return {
            "metadata": {
                "source_log_file": str(self.log_file),
                "parser": self.__class__.__name__,
                "parsed_at_utc": datetime.now(timezone.utc).isoformat(),
            },
            "summary": {
                "overall_status": "FAIL",
                "error": error_message,
            },
            "details": {}
        }

    def _write_json(self, data: Dict[str, Any]):
        try:
            with self.result_json.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except IOError as e:
            print(f"Error: Could not write JSON to {self.result_json}. Reason: {e}", file=sys.stderr)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse CPU test logs into a JSON summary.")
    parser.add_argument(
        "--log_dir",
        type=str,
        default=os.environ.get("RESULT_DIR", "."),
        help="Directory containing the log file. Defaults to RESULT_DIR env var or current directory."
    )
    args = parser.parse_args()
    
    try:
        log_parser = CpuTestLogParser(log_dir=args.log_dir)
        log_parser.parse()
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)