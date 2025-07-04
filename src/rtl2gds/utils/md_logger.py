import json


class MDLogger:
    def __init__(self, markdown_log_file):
        self.log_file = markdown_log_file
        self.num_executed_steps = 0
        with open(self.log_file, "w", encoding="utf-8") as f:
            f.write("# RTL2GDS exec result:\n")

    def end_log(self) -> None:
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write("\n\n---\n\n")
            f.write(f"End with {self.num_executed_steps} RTL2GDS steps\n\n")

    def add_header(self, step: str) -> None:
        with open(self.log_file, "a", encoding="utf-8") as f:
            self.num_executed_steps += 1
            f.write("\n\n---\n\n")
            f.write(f"## {self.num_executed_steps}.{step}\n\n")

    def _add_dict_in_json(self, dict_name: str, dict_data: dict[str, object]) -> None:
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"\n\n### {dict_name}:\n\n")
            f.write("```json\n")
            f.write(json.dumps(dict_data, indent=4))
            f.write("\n```\n\n")

    def add_metrics_dict(self, metrics: dict[str, object]) -> None:
        self._add_dict_in_json("Metrics", metrics)

    def add_result_files(self, result_files: dict[str, object]) -> None:
        self._add_dict_in_json("Result files", result_files)

    def add_report_txt(self, report_file: str) -> None:
        with open(report_file, "r", encoding="utf-8") as f:
            contents = f.read()
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write("\n\n### Report:\n\n")
            f.write("```text\n")
            f.write(contents)
            f.write("\n```\n\n")

    def add_stat_json(self, stat_file: str) -> None:
        with open(stat_file, "r", encoding="utf-8") as f:
            contents = f.read()
            stat = json.loads(contents)
        self._add_dict_in_json("Stat", stat)

    def add_metrics_json(self, metrics_file: str) -> None:
        with open(metrics_file, "r", encoding="utf-8") as f:
            contents = f.read()
            metrics = json.loads(contents)
        self.add_metrics_dict(metrics)

    def add_pr_res_all(self, step: str, res_files: dict[str, object]) -> None:
        self.add_header(step)
        self.add_result_files(res_files)
        self.add_stat_json(res_files["design_stat_json"])
        if "tool_metrics_json" in res_files:
            self.add_metrics_json(res_files["tool_metrics_json"])
