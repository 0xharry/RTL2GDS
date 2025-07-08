import json
import logging
import math
import os  # Added for file operations if needed
import re
import subprocess
import tempfile

from rtl2gds.global_configs import ENV_TOOLS_PATH


def save_module_preview(
    verilog_file,
    output_svg=None,
    module_name=None,
    flatten=False,
    aig=False,
    skin_file=None,
):
    """
    Export a Verilog to an SVG diagram preview using **Yosys** and **netlistsvg**.

    Args:
        verilog_file (str): Path to the input Verilog file
        output_svg (str, optional): Path to the output SVG file. Defaults to input filename or module_name with .svg extension.
        module_name (str, optional): Name of the top module. If None, Yosys will auto-detect.
        flatten (bool, optional): If True, flatten the design to basic logic gates. Defaults to False.
        aig (bool, optional): If True, convert to AND-inverter graph representation. Defaults to False.
        skin_file (str, optional): Path to a custom skin file for netlistsvg. Defaults to None.

    Returns:
        str: Path to the generated SVG file

    Raises:
        FileNotFoundError: If the input Verilog file doesn't exist
        subprocess.CalledProcessError: If Yosys or netlistsvg commands fail
    """
    # Check if input file exists
    if not os.path.isfile(verilog_file):
        raise FileNotFoundError(f"Input Verilog file not found: {verilog_file}")

    # Set default output SVG filename if not provided
    if output_svg is None:
        base_name = os.path.splitext(verilog_file)[0] if module_name is None else module_name
        output_svg = f"{base_name}.svg"

    # Create a temporary JSON file
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_json:
        json_file = temp_json.name

    try:
        # Construct Yosys command
        yosys_cmd = ["yosys", "-p"]

        # Build the prep command
        prep_cmd = "prep"
        if module_name:
            prep_cmd += f" -top {module_name}"
        if flatten:
            prep_cmd += " -flatten"

        # Complete Yosys command
        if aig:
            yosys_cmd_str = f"{prep_cmd}; aigmap; write_json {json_file}"
        else:
            yosys_cmd_str = f"{prep_cmd}; write_json {json_file}"

        yosys_cmd.append(yosys_cmd_str)
        yosys_cmd.append(verilog_file)

        # Run Yosys
        # https://github.com/nturley/netlistsvg/blob/master/README.md#generating-input_json_file-with-yosys
        # yosys -p "prep -top my_top_module; write_json output.json" input.v
        # yosys -p "prep -top my_top_module -flatten; write_json output.json" input.v
        # yosys -p "prep -top my_top_module; aigmap; write_json output.json" input.v
        logging.info("Running Yosys: %s", " ".join(yosys_cmd))
        subprocess.run(yosys_cmd, check=True, env=ENV_TOOLS_PATH)

        # Construct netlistsvg command
        netlistsvg_cmd = ["netlistsvg", json_file, "-o", output_svg]
        if skin_file:
            netlistsvg_cmd.extend(["--skin", skin_file])

        # Run netlistsvg
        # netlistsvg input_json_file [-o output_svg_file] [--skin skin_file]
        logging.info("Running netlistsvg: %s", " ".join(netlistsvg_cmd))
        subprocess.run(netlistsvg_cmd, check=True)

        logging.info("SVG diagram generated successfully: %s", output_svg)
        return output_svg

    finally:
        # Clean up temporary JSON file
        if os.path.exists(json_file):
            os.remove(json_file)


def parse_synth_stat(synth_stat_json: str):
    """Extract top module area and name from yosys report and simplify cell names"""
    stats = {
        "num_cells": 0,
        "cell_area": 0.0,
        "sequential_ratio": 0.0,
        "cell_types": {},
    }
    # cell_prefix = "sg13g2_"
    # cell_prefix_match_pattern = f"     {cell_prefix}"

    with open(
        synth_stat_json,
        "r",
        encoding="utf-8",
    ) as f:
        summary = json.load(f)
        # logging.debug(summary)
        stats["num_cells"] = int(summary["design"]["num_cells"])
        stats["cell_area"] = float(summary["design"]["area"])

    return stats


def check_v(rtl_file: str | list[str]) -> str | list[str]:
    """Check RTL file(s) existence and return the original file path(s).

    Note: SystemVerilog files are now handled directly by yosys with slang plugin,
    so no conversion is needed.

    Args:
        rtl_file: Path(s) to the input RTL file(s)

    Returns:
        Path(s) to the original RTL file(s)

    Raises:
        FileNotFoundError: If any RTL file doesn't exist
    """
    if isinstance(rtl_file, str):
        if not os.path.exists(rtl_file):
            raise FileNotFoundError(f"RTL file {rtl_file} not found")
        return rtl_file
    elif isinstance(rtl_file, list):
        for file in rtl_file:
            if not os.path.exists(file):
                raise FileNotFoundError(f"RTL file {file} not found")
        return rtl_file


def calculate_areas(cell_area, core_util, die_bbox=None, core_bbox=None):
    """Calculate die and core areas based on synthesis statistics.

    Args:
        stats (dict): Synthesis statistics from Yosys
        core_util (float): Core utilization percentage
        die_bbox (str, optional): Die area coordinates. Defaults to None
        core_bbox (str, optional): Core area coordinates. Defaults to None

    Returns:
        tuple: (die_bbox, core_bbox, core_util)
    """
    if not (die_bbox and core_bbox):
        core_length = math.sqrt(cell_area / core_util)
        io_margin = 10
        die_bbox = f"0 0 {core_length+io_margin*2} {core_length+io_margin*2}"
        core_bbox = f"{io_margin} {io_margin} {core_length+io_margin} {core_length+io_margin}"

    elif not core_util:
        core = core_bbox.split(" ")
        core_len_x = float(core[2]) - float(core[0])
        core_len_y = float(core[3]) - float(core[1])
        core_area = core_len_x * core_len_y
        core_util = cell_area / core_area
        assert 0 < core_util < 1, "Core utilization out of range"

    return die_bbox, core_bbox, core_util


class HierarchyNode:
    """Represents a node in the design hierarchy."""

    def __init__(self, name, count=1):
        # Sanitize name on creation
        self.name = self._sanitize_name(name)
        self.count = count
        self.children = []

    def _sanitize_name(self, name):
        """Removes potentially problematic characters like leading/trailing quotes or backslashes."""
        name = name.strip()
        # Remove leading/trailing backslash common in some tools
        if name.startswith("\\"):
            name = name[1:]
        # Remove leading/trailing single quotes
        name = name.strip("'")
        return name

    def add_child(self, node):
        self.children.append(node)

    def __repr__(self):
        return f"Node(name='{self.name}', count={self.count}, children={len(self.children)})"

    def to_dict(self):
        """Convert the node and its children to a dictionary representation."""
        return {
            "module_name": self.name,
            "instance_count": self.count,
            "submodules": [child.to_dict() for child in self.children],
        }


class SynthStatParser:
    """
    Parses a logic synthesis statistics file (synth_stat.txt)
    to extract module statistics and design hierarchy. Handles complex module names.
    """

    # Regex patterns pre-compiled for efficiency
    # Match module headers like === module_name ===
    _RE_MODULE_HEADER = re.compile(r"^=== (.*) ===$")
    # Match key-value lines, allowing floats and optional percentage
    _RE_KV_LINE = re.compile(r"^\s*(.*?):\s+([\d.]+)\s*(\(.*\))?$")
    # Match cell count lines (handles complex names with $, \, ', = etc.)
    _RE_CELL_LINE = re.compile(r"^\s+([$a-zA-Z0-9_\\~.\'=\\]+)\s+(\d+)$")
    # Match area lines (handles optional quotes and 'top module')
    _RE_AREA_LINE = re.compile(r"^\s*Chip area for (?:module|top module)\s+'?([^']*)'?:\s+([\d.]+)")
    # Match sequential area lines
    _RE_SEQ_AREA_LINE = re.compile(
        r"^\s*of which used for sequential elements:\s+([\d.]+)\s+\(([\d.]+)%\)"
    )
    # Match hierarchy lines (handles complex names)
    _RE_HIERARCHY_LINE = re.compile(r"^(\s*)([$a-zA-Z0-9_\\~.\'=\\]+)\s+(\d+)$")
    # Match ignored "Area unknown" lines
    _RE_AREA_UNKNOWN = re.compile(r"^\s*Area for cell type .* is unknown!")

    def __init__(self, file_path):
        self.file_path = file_path
        self.module_stats = {}
        self.hierarchy_root = None
        self.total_stats = {}
        self._parse()

    def _sanitize_name(self, name):
        """Removes potentially problematic characters like leading/trailing quotes or backslashes."""
        name = name.strip()
        # Remove leading/trailing backslash common in some tools
        if name.startswith("\\"):
            name = name[1:]
        # Remove leading/trailing single quotes (often seen in area lines)
        name = name.strip("'")
        # Note: Internal backslashes within names like $paramod\dff are kept.
        return name

    def _parse_kv_line(self, line, stats_dict):
        """Parses a key-value line like 'Number of wires: 123'."""
        match = self._RE_KV_LINE.match(line)
        if match:
            key = match.group(1).strip().lower().replace(" ", "_").replace("\\", "")
            value_str = match.group(2).strip()
            try:
                # Try converting to int, then float if it fails
                try:
                    value = int(value_str)
                except ValueError:
                    value = float(value_str)
                stats_dict[key] = value
                # Check for percentage in parenthesis (like sequential area)
                if match.group(3):
                    percent_match = re.search(r"\(([\d.]+)%\)", match.group(3))
                    if percent_match:
                        stats_dict[key + "_percent"] = float(percent_match.group(1))
                return True
            except ValueError:
                print(
                    f"Warning: Could not parse value '{value_str}' for key '{key}' in line: {line}"
                )
        return False

    def _parse_cell_line(self, line, stats_dict):
        """Parses an indented cell line like '  sky130_...  123'."""
        # Cell lines must start with significant indentation
        if not line.startswith(" " * 5):  # Heuristic: require at least 5 spaces
            return False
        match = self._RE_CELL_LINE.match(line)
        if match:
            cell_name = self._sanitize_name(match.group(1))  # Sanitize here
            count = int(match.group(2))
            if "cells" not in stats_dict:
                stats_dict["cells"] = {}
            stats_dict["cells"][cell_name] = count
            return True
        # else:
        #    if line.strip() and line[0].isspace(): # Debugging unmatched indented lines
        #        print(f"Debug: Did not match cell line regex: '{line}'")
        return False

    def _parse_area_line(self, line, stats_dict):
        """Parses the 'Chip area for module...' line."""
        match = self._RE_AREA_LINE.match(line)
        if match:
            # module_name_in_line = self._sanitize_name(match.group(1)) # Sanitize
            # We don't strictly need the name here as we get it from the header,
            # but could be used for verification if needed.
            try:
                stats_dict["chip_area"] = float(match.group(2))
                return True
            except ValueError:
                print(f"Warning: Could not parse area value '{match.group(2)}' in line: {line}")
        return False

    def _parse_sequential_area_line(self, line, stats_dict):
        """Parses the 'of which used for sequential elements...' line."""
        match = self._RE_SEQ_AREA_LINE.match(line)
        if match:
            try:
                stats_dict["sequential_area"] = float(match.group(1))
                stats_dict["sequential_area_percent"] = float(match.group(2))
                return True
            except ValueError:
                print(f"Warning: Could not parse sequential area values in line: {line}")
        return False

    def _parse_hierarchy_line(self, line):
        """Parses a line from the design hierarchy section."""
        match = self._RE_HIERARCHY_LINE.match(line)
        if match:
            indentation = len(match.group(1))
            # Name is sanitized when creating the HierarchyNode object
            module_name = match.group(2).strip()  # Keep original for Node creation
            count = int(match.group(3))
            return indentation, module_name, count
        return None, None, None

    def _parse(self):
        """Main parsing logic."""
        current_module_name_sanitized = None
        current_stats = None
        mode = "start"  # Modes: start, module_stats, hierarchy_tree, hierarchy_summary
        indent_stack = []  # Stores (indentation_level, node) pairs for hierarchy
        pending_line = None  # Holds the next line if not processed after area line

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                # Use an iterator for easier handling of lookahead/pending lines
                line_iter = iter(f)

                while True:
                    # --- Get the next line to process ---
                    if pending_line is not None:
                        line = pending_line.rstrip()
                        pending_line = None  # Consume the pending line
                    else:
                        try:
                            line = next(line_iter).rstrip()
                        except StopIteration:
                            break  # End of file

                    # print(f"Debug - Mode: {mode}, Line: '{line}'") # Debug print

                    # --- Mode Switching ---
                    module_header_match = self._RE_MODULE_HEADER.match(line)
                    if module_header_match:
                        raw_module_name = module_header_match.group(1).strip()
                        sanitized_name = self._sanitize_name(raw_module_name)

                        if sanitized_name == "design hierarchy":
                            mode = "hierarchy_tree"
                            if current_stats:  # Save last module before hierarchy
                                self.module_stats[current_module_name_sanitized] = current_stats
                            current_module_name_sanitized = None
                            current_stats = None
                            indent_stack = []  # Reset hierarchy stack
                            # print(f"Debug - Switched to mode: {mode}") # Debug print
                        else:
                            mode = "module_stats"
                            if current_stats:  # Save previous module's stats
                                self.module_stats[current_module_name_sanitized] = current_stats
                            current_module_name_sanitized = sanitized_name
                            current_stats = {"name": current_module_name_sanitized}
                            # print(f"Debug - Parsing module: {current_module_name_sanitized}") # Debug print
                        continue  # Move to next line after header

                    # Skip blank lines
                    if not line.strip():
                        continue

                    # --- Parsing based on Mode ---
                    if mode == "module_stats":
                        if current_stats is None:
                            continue  # Should not happen

                        # Check for specific lines first
                        if self._RE_AREA_UNKNOWN.match(line):
                            # print(f"Debug - Ignoring unknown area line: {line}") # Debug print
                            continue  # Ignore these specific warning lines

                        if self._parse_area_line(line, current_stats):
                            # Check immediately for sequential area on the *next* line
                            try:
                                next_line_content = next(line_iter)
                                # Temporarily strip for matching, but keep original if needed elsewhere
                                if not self._parse_sequential_area_line(
                                    next_line_content.rstrip(), current_stats
                                ):
                                    # If it wasn't sequential area, save it for the next iteration
                                    pending_line = next_line_content
                            except StopIteration:
                                pass  # End of file after area line
                            continue  # Area line (and maybe seq area) processed

                        if self._parse_kv_line(line, current_stats):
                            continue  # Key-value line processed

                        if self._parse_cell_line(line, current_stats):
                            continue  # Cell line processed

                        # If none of the above matched, it might be noise or unexpected format
                        # print(f"Warning: Unparsed line in module_stats: '{line}'")

                    elif mode == "hierarchy_tree":
                        indent, raw_name, count = self._parse_hierarchy_line(line)
                        if indent is not None:
                            # Create node (name sanitized inside constructor)
                            new_node = HierarchyNode(raw_name, count)
                            # print(f"Debug - Hierarchy node: indent={indent}, name='{new_node.name}', count={count}") # Debug print

                            # Adjust stack based on indentation
                            while indent_stack and indent <= indent_stack[-1][0]:
                                indent_stack.pop()

                            if not indent_stack:
                                # This is the root node
                                self.hierarchy_root = new_node
                            else:
                                # Add as child to the node currently at the top of the stack
                                parent_node = indent_stack[-1][1]
                                parent_node.add_child(new_node)

                            # Push the new node and its indentation level onto the stack
                            indent_stack.append((indent, new_node))
                        else:
                            # If line doesn't match hierarchy format, assume it's the start
                            # of the hierarchy summary statistics section
                            mode = "hierarchy_summary"
                            self.total_stats = {}
                            # print(f"Debug - Switched to mode: {mode}") # Debug print
                            # Re-process the current line in the new mode
                            # Use a temporary dict for parsing attempts
                            temp_stats = {}
                            if self._parse_kv_line(line, temp_stats):
                                self.total_stats.update(temp_stats)
                                continue
                            if self._parse_cell_line(line, temp_stats):
                                # Handle merging cell dicts
                                if "cells" not in self.total_stats:
                                    self.total_stats["cells"] = {}
                                self.total_stats["cells"].update(temp_stats["cells"])
                                continue
                            if self._parse_area_line(line, temp_stats):
                                self.total_stats.update(temp_stats)
                                # Check immediately for sequential area on the *next* line
                                try:
                                    next_line_content = next(line_iter)
                                    if not self._parse_sequential_area_line(
                                        next_line_content.rstrip(), self.total_stats
                                    ):
                                        pending_line = next_line_content
                                except StopIteration:
                                    pass
                                continue
                            # else: print(f"Warning: Unparsed line at start of hierarchy_summary: '{line}'")

                    elif mode == "hierarchy_summary":
                        # Parse remaining lines as key-value or cell counts for total stats
                        # Use a temporary dict for parsing attempts
                        temp_stats = {}
                        if self._parse_kv_line(line, temp_stats):
                            self.total_stats.update(temp_stats)
                            continue
                        if self._parse_cell_line(line, temp_stats):
                            # Handle merging cell dicts
                            if "cells" not in self.total_stats:
                                self.total_stats["cells"] = {}
                            self.total_stats["cells"].update(temp_stats["cells"])
                            continue
                        if self._parse_area_line(line, temp_stats):
                            self.total_stats.update(temp_stats)
                            # Check immediately for sequential area on the *next* line
                            try:
                                next_line_content = next(line_iter)
                                if not self._parse_sequential_area_line(
                                    next_line_content.rstrip(), self.total_stats
                                ):
                                    pending_line = next_line_content
                            except StopIteration:
                                pass
                            continue
                        # else: print(f"Warning: Unparsed line in hierarchy_summary: '{line}'")

                # End of loop
                if current_stats:  # Save the very last module's stats
                    self.module_stats[current_module_name_sanitized] = current_stats
                # print("Debug - Reached end of file processing.") # Debug print

        except FileNotFoundError:
            print(f"Error: File not found at {self.file_path}")
            self.module_stats = {}
            self.hierarchy_root = None
            self.total_stats = {}
        except Exception as e:
            print(f"An unexpected error occurred during parsing: {e}")
            import traceback

            traceback.print_exc()

    def get_module_stats(self, module_name=None):
        """Returns statistics for a specific module or all modules."""
        if module_name:
            # Sanitize the requested name for lookup
            sanitized_key = self._sanitize_name(module_name)
            return self.module_stats.get(sanitized_key)
        return self.module_stats

    def get_hierarchy(self):
        """Returns the root node of the design hierarchy."""
        return self.hierarchy_root

    def get_total_stats(self):
        """Returns the summary statistics for the entire design."""
        return self.total_stats

    def hierarchy_to_dict(self):
        """Returns the hierarchy as a nested dictionary."""
        if self.hierarchy_root:
            return self.hierarchy_root.to_dict()
        return None

    def print_summary(self, detail_level=1):
        """
        Prints a summary of the parsed data.
        detail_level=0: Minimal summary
        detail_level=1: Module names and basic stats (default)
        detail_level=2: Full stats per module
        """
        print("--- Parsed Synthesis Statistics ---")
        print(f"File: {self.file_path}\n")

        print("Individual Module Statistics:")
        if not self.module_stats:
            print("  (No module statistics found or parsed)")
        else:
            print(f"  Found {len(self.module_stats)} modules.")
            if detail_level >= 1:
                for name, stats in sorted(self.module_stats.items()):
                    area = stats.get("chip_area", "N/A")
                    seq_area = stats.get("sequential_area", "N/A")
                    num_cells_key = "number_of_cells"  # Primary key
                    if num_cells_key not in stats and "cells" in stats:
                        cells_val = sum(stats.get("cells", {}).values())
                    elif num_cells_key in stats:
                        cells_val = stats[num_cells_key]
                    else:
                        cells_val = "N/A"

                    print(f"  Module: {name}")
                    print(f"    Cells: {cells_val}, Area: {area}, Seq Area: {seq_area}")
                    if detail_level >= 2:
                        for k, v in stats.items():
                            if k not in [
                                "name",
                                "chip_area",
                                "sequential_area",
                                "number_of_cells",
                                "cells",
                            ] and not k.endswith("_percent"):
                                print(f"      {k}: {v}")
                        if "cells" in stats:
                            print(f"      Cell Counts: {len(stats['cells'])} types")
                            if detail_level >= 3:
                                for cell, count in stats["cells"].items():
                                    print(f"        {cell}: {count}")
        print("-" * 20)

        print("Design Hierarchy:")
        if not self.hierarchy_root:
            print("  (Hierarchy not found or parsed)")
        else:

            def print_node(node, indent=2):
                print(f"{' ' * indent}Module: {node.name}, Instances: {node.count}")
                for child in node.children:
                    print_node(child, indent + 2)

            print_node(self.hierarchy_root)
        print("-" * 20)

        print("Total Design Statistics (Hierarchy Summary Section):")
        if not self.total_stats:
            print("  (Total statistics not found or parsed)")
        else:
            for key, value in self.total_stats.items():
                if key == "cells":
                    print(f"  Total Cell Types: {len(value)}")
                    print(f"  Total Cell Instances: {sum(value.values())}")
                elif isinstance(value, dict):  # Should not happen with current parsing for totals
                    print(
                        f"  {key.replace('_', ' ').title()}: [Dictionary with {len(value)} items]"
                    )
                else:
                    print(f"  {key.replace('_', ' ').title()}: {value}")
        print("-" * 20)


if __name__ == "__main__":
    synth_stat_file_path = "/opt/rtl2gds/kianv_results/yosys/synth_stat.txt"

    if not os.path.exists(synth_stat_file_path):
        print(f"Error: Input file '{synth_stat_file_path}' not found.")
        print("Please create the file or update the 'synth_stat_file_path' variable.")
    else:
        # --- Parse the file ---
        print(f"Parsing file: {synth_stat_file_path}...")
        parser = SynthStatParser(synth_stat_file_path)
        print("Parsing complete.")

        # --- Print a summary ---
        # Use detail_level=1 for overview, 2 for more details per module
        parser.print_summary(detail_level=1)

        print("\n--- Detailed Data Access Examples ---")

        # Get stats for a specific module (use sanitized name if needed, but lookup handles it)
        # Example using a complex name:
        complex_module_name = (
            "$paramod\\register_file\\REGISTER_DEPTH=s32'00000000000000000000000000100000"
        )
        specific_stats = parser.get_module_stats(complex_module_name)
        if specific_stats:
            print(f"\nStats for '{complex_module_name}':")  # Print original requested name
            print(f"  (Parsed Name: {specific_stats.get('name')})")  # Show how it was stored
            print(
                f"  Number of Cells: {specific_stats.get('number_of_cells', sum(specific_stats.get('cells', {}).values()))}"
            )
            print(f"  Chip Area: {specific_stats.get('chip_area')}")
            print(
                f"  Cell sky130_fd_sc_hs__dfxtp_1 count: {specific_stats.get('cells', {}).get('sky130_fd_sc_hs__dfxtp_1', 'N/A')}"
            )
        else:
            print(f"\nStats for '{complex_module_name}' not found.")

        # Get the hierarchy root
        hierarchy = parser.get_hierarchy()
        if hierarchy:
            print(f"\nHierarchy Root Node: {hierarchy.name} (Count: {hierarchy.count})")
            # Example: Accessing a specific child path if known (error prone if structure changes)
            try:
                soc_node = next(c for c in hierarchy.children if c.name == "soc")
                kianv_node = next(
                    c
                    for c in soc_node.children
                    if c.name.startswith("$paramod\\kianv_harris_mc_edition")
                )
                datapath_node = next(
                    c
                    for c in kianv_node.children
                    if c.name.startswith("$paramod$24d21e9bf399c82f9599919af6e14cda3f6192c2")
                )
                print(
                    f"  Found datapath node: {datapath_node.name} (Instance count: {datapath_node.count})"
                )
                alu_node = next((c for c in datapath_node.children if c.name == "alu"), None)
                if alu_node:
                    print(f"    ALU instances under datapath: {alu_node.count}")
            except (StopIteration, AttributeError):
                print("  Could not traverse hierarchy to find specific example child.")

        # Get hierarchy as dictionary (useful for JSON export etc.)
        hierarchy_dict = parser.hierarchy_to_dict()
        if hierarchy_dict:
            print("\nHierarchy as Dictionary (showing root level):")
            # Limit printing depth for very large hierarchies
            # print(json.dumps(hierarchy_dict, indent=2)) # Full dump can be huge
            print(
                f"  Root: {hierarchy_dict.get('module_name')}, Instances: {hierarchy_dict.get('instance_count')}"
            )
            print(f"  Submodules: {len(hierarchy_dict.get('submodules', []))} direct children")

        # Get total design stats from the summary section
        totals = parser.get_total_stats()
        print("\nTotal Design Stats (from Hierarchy Summary section):")
        if totals:
            # The key for total area might vary based on the top module name
            area_key = next(
                (k for k in totals if k.startswith("chip_area_for_top_module")),
                "chip_area",
            )  # Fallback
            print(f"  Total Area: {totals.get(area_key, 'N/A')}")
            print(f"  Total Sequential Area: {totals.get('sequential_area', 'N/A')}")
            print(
                f"  Total Cell Instances: {totals.get('number_of_cells', sum(totals.get('cells', {}).values()))}"
            )
        else:
            print("  Total stats section not found or empty.")

        # Example: Save parsed data to JSON
        output_data = {
            "module_stats": parser.get_module_stats(),
            "hierarchy": parser.hierarchy_to_dict(),
            "total_stats": parser.get_total_stats(),
        }
        json_output_path = "parsed_synth_stat.json"
        try:
            with open(json_output_path, "w") as jf:
                json.dump(output_data, jf, indent=2)
            print(f"\nSaved parsed data to {json_output_path}")
        except Exception as e:
            print(f"\nError saving JSON: {e}")
