import os
import json
import re
from typing import Dict, Any, Optional

class CpuTestLogParser:
    def __init__(self, log_dir: str):
        top_name = os.environ.get("TOP_NAME", "default")
        self.log_file = os.path.join(log_dir, f"{top_name}_cpu_test.log")
        self.result_json = os.path.join(log_dir, f"{top_name}_cpu_test.json")
        os.makedirs(log_dir, exist_ok=True)

    def parse(self):
        test_details: Dict[str, Dict[str, Any]] = {}
        total_exec_time: Optional[float] = None
        
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except FileNotFoundError:
            print(f"Error: Log file not found at {self.log_file}")
            summary = self._create_error_summary(f"Log file not found: {self.log_file}")
            self._write_json(summary)
            return

        for line in lines:
            # Regex for individual test lines, e.g., "[           add] PASS  1.488s"
            m_test = re.match(r"\[\s*([^\]]+)\]\s+(PASS|FAIL)\s+([.\d]+)s", line)
            if m_test:
                test_name = m_test.group(1).strip()
                status = m_test.group(2)
                elapsed = float(m_test.group(3))
                
                test_details[test_name] = {
                    "status": status,
                    "time_s": elapsed
                }
                continue 

            m_total = re.match(r"\[\s*Total Time\s*\]\s+([.\d]+)s", line)
            if m_total:
                total_exec_time = float(m_total.group(1))

        pass_count = sum(1 for detail in test_details.values() if detail["status"] == "PASS")
        total_count = len(test_details)
        all_pass = (pass_count == total_count) and (total_count > 0)

        summary = {
            "summary": {
                "overall_status": "pass" if all_pass else "fail",
                "total_tests": total_count,
                "passed_tests": pass_count,
                "failed_tests": total_count - pass_count,
                "pass_rate": f"{pass_count}/{total_count}" if total_count > 0 else "0/0",
                "total_execution_time_s": total_exec_time,
            },
            "details": test_details
        }

        self._write_json(summary)
        
        print(f"CPU test summary: {summary['summary']['overall_status']} ({summary['summary']['pass_rate']})")
        if summary['summary']['total_execution_time_s'] is not None:
            print(f"Total execution time: {summary['summary']['total_execution_time_s']}s")
        print(f"Result JSON saved to: {self.result_json}")

    def _create_error_summary(self, error_message: str) -> Dict[str, Any]:
        return {
            "summary": {
                "overall_status": "fail",
                "error": error_message
            }
        }

    def _write_json(self, data: Dict[str, Any]):
        with open(self.result_json, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

if __name__ == "__main__":
    result_dir = os.environ.get("RESULT_DIR", ".")
    parser = CpuTestLogParser(log_dir=result_dir)
    parser.parse()