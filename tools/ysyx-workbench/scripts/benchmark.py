import json
import re
import os

class BenchmarkLogParser:
    def __init__(self, log_dir):
        top_name = os.environ.get("TOP_NAME")
        self.coremark_log = os.path.join(log_dir, f"{top_name}_coremark.log")
        self.dhrystone_log = os.path.join(log_dir, f"{top_name}_dhrystone.log")
        self.microbench_log = os.path.join(log_dir, f"{top_name}_microbench.log")
        self.result_json = os.path.join(log_dir, f"{top_name}_benchmark.json")

    def parse_coremark(self, log_file):
        details_list = []
        if not os.path.exists(log_file):
            return {"coremark": "fail", "details": [], "pass_count": 0, "total_count": 0}
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        i = 0
        pass_count = 0
        total_count = 0
        while i < len(lines):
            line = lines[i]
            if "CoreMark Size" in line:
                details = {}
                m = re.search(r"CoreMark Size\s*:\s*(\d+)", line)
                if m:
                    details["CoreMark Size"] = int(m.group(1))
                m = re.search(r"Total time \(ms\)\s*:\s*(\d+)", lines[i+1])
                if m:
                    details["Total time (ms)"] = int(m.group(1))
                m = re.search(r"Iterations\s*:\s*(\d+)", lines[i+2])
                if m:
                    details["Iterations"] = int(m.group(1))
                crc_items = [
                    ("[0]crclist", r"\[0\]crclist\s*:\s*(\S+)"),
                    ("[0]crcmatrix", r"\[0\]crcmatrix\s*:\s*(\S+)"),
                    ("[0]crcstate", r"\[0\]crcstate\s*:\s*(\S+)"),
                    ("[0]crcfinal", r"\[0]crcfinal\s*:\s*(\S+)")
                ]
                crc_pass = 0
                crc_total = 0
                for idx, (key, pattern) in enumerate(crc_items):
                    m = re.search(pattern, lines[i+5+idx])
                    if m:
                        details[key] = m.group(1)
                        crc_total += 1
                        if m.group(1) != "":
                            crc_pass += 1
                for j in range(i+9, min(i+20, len(lines))):
                    if "CoreMark PASS" in lines[j]:
                        m = re.search(r"CoreMark PASS\s+(\d+)", lines[j])
                        details["Marks"] = m.group(1) if m else ""
                        details["status"] = "pass"
                        pass_count += crc_pass
                        total_count += crc_total
                        break
                    elif "CoreMark FAIL" in lines[j]:
                        m = re.search(r"CoreMark FAIL\s+(\d+)", lines[j])
                        details["Marks"] = m.group(1) if m else ""
                        details["status"] = "fail"
                        total_count += crc_total
                        break
                details_list.append(details)
                i += 10
            else:
                i += 1
        overall_status = "pass" if pass_count == total_count and total_count > 0 else "fail"
        return {
            "coremark": overall_status,
            "details": details_list,
            "pass_count": pass_count,
            "total_count": total_count
        }

    def parse_dhrystone(self, log_file):
        details = {}
        status = "fail"
        if not os.path.exists(log_file):
            return {"dhrystone": "fail", "details": {}}
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                if "Trying" in line and "runs through Dhrystone" in line:
                    m = re.search(r"Trying\s+(\d+)\s+runs", line)
                    if m:
                        details["Iterations"] = int(m.group(1))
                if "Finished in" in line:
                    m = re.search(r"Finished in\s+(\d+)\s*ms", line)
                    if m:
                        details["Total time (ms)"] = int(m.group(1))
                if "Dhrystone PASS" in line:
                    m = re.search(r"Dhrystone PASS\s+(\d+)", line)
                    details["Marks"] = m.group(1) if m else ""
                    status = "pass"
                elif "Dhrystone FAIL" in line:
                    m = re.search(r"Dhrystone FAIL\s+(\d+)", line)
                    details["Marks"] = m.group(1) if m else ""
                    status = "fail"
        return {
            "dhrystone": status,
            "details": details
        }

    def parse_microbench(self, log_file):
        details = {
            "input": "",
            "tests": [],
            "Scored time (ms)": None,
            "Total time (ms)": None
        }
        status = "fail"
        pass_count = 0
        total_count = 0
        if not os.path.exists(log_file):
            return {"microbench": "fail", "details": details, "pass_count": 0, "total_count": 0}
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                if "Running MicroBench [input" in line:
                    m = re.search(r'input \*(.*?)\*', line)
                    if m:
                        details["input"] = m.group(1)
                m = re.match(r"\[(\w+)\]\s+(.+?):\s+\*\s+(\w+)\.", line)
                if m:
                    test_name = m.group(1)
                    desc = m.group(2).strip()
                    result = m.group(3)
                    details["tests"].append({
                        "name": test_name,
                        "desc": desc,
                        "result": result
                    })
                    total_count += 1
                    if result.lower() == "passed":
                        pass_count += 1
                m = re.search(r"Scored time:\s*([\d.]+)\s*ms", line)
                if m:
                    details["Scored time (ms)"] = float(m.group(1))
                m = re.search(r"Total\s+time:\s*([\d.]+)\s*ms", line)
                if m:
                    details["Total time (ms)"] = float(m.group(1))
                if "MicroBench PASS" in line:
                    status = "pass"
                elif "MicroBench FAIL" in line:
                    status = "fail"
        return {
            "microbench": status,
            "details": details,
            "pass_count": pass_count,
            "total_count": total_count
        }

    def parse(self):
        coremark_result = self.parse_coremark(self.coremark_log)
        dhrystone_result = self.parse_dhrystone(self.dhrystone_log)
        microbench_result = self.parse_microbench(self.microbench_log)
        result = {
            "coremark": coremark_result["coremark"],
            "coremark_details": coremark_result["details"],
            "coremark_stat": f"{coremark_result['pass_count']}/{coremark_result['total_count']}",
            "dhrystone": dhrystone_result["dhrystone"],
            "dhrystone_details": dhrystone_result["details"],
            "microbench": microbench_result["microbench"],
            "microbench_details": microbench_result["details"],
            "microbench_stat": f"{microbench_result['pass_count']}/{microbench_result['total_count']}"
        }
        with open(self.result_json, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"coremark: {result['coremark']} ({result['coremark_stat']})")
        print(f"dhrystone: {result['dhrystone']}")
        print(f"microbench: {result['microbench']} ({result['microbench_stat']})")

if __name__ == "__main__":
    log_dir = os.environ.get("LOG_DIR", "./log")
    BenchmarkLogParser(log_dir).parse()