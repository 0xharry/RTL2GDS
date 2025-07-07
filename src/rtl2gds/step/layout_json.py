"""
use for rtl2gds cloud
"""

import logging
import os
import pathlib
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor

import orjson

from rtl2gds.global_configs import DEFAULT_SDC_FILE, ENV_TOOLS_PATH, StepName
from rtl2gds.step.configs import SHELL_CMD

DEFAULT_MAX_FILE_SIZE = 19 * 1024 * 1024  # 19MB in bytes


def _save_chunk(data_chunk: list[object], file_no_suffix: str, index: int) -> str:
    """
    Save a chunk of data to a JSON file.

    Parameters:
    data_chunk (list): The chunk of data to save.
    file_no_suffix (str): The base file name (without suffix).
    index (int): The index to append to the file name.

    Returns:
    str: The name of the created JSON file.
    """
    chunk_data = {"data": data_chunk}
    file_name = f"{file_no_suffix}-{index}.json"

    with open(file_name, "wb") as file:
        file.write(orjson.dumps(chunk_data))
    return file_name


def _remove_bracket_trailing_commas(json_str: str) -> str:
    """
    Remove trailing commas before closing square or curly brackets in a JSON string.

    Parameters:
    json_str (str): The JSON string to process.

    Returns:
    str: The JSON string with trailing commas removed.
    """
    return re.sub(r",\s*([\]}])", r"\1", json_str)


def _read_and_validate_json(filename: str) -> dict:
    """
    Read and validate the JSON file.

    Parameters:
    filename (str): The name of the JSON file to read.

    Returns:
    dict: The loaded JSON data.
    """
    with open(filename, "rb") as f:
        data = _remove_bracket_trailing_commas(f.read().decode("utf-8"))
        data = orjson.loads(data)

    assert "data" in data, "Invalid data format: 'data' key missing"
    assert isinstance(data["data"], list), "Invalid data format: not a list"
    return data


def _extract_header(data: dict) -> dict:
    """
    Extract header from the JSON data.

    Parameters:
    data (dict): The JSON data.

    Returns:
    dict: The header data.
    """
    return {key: value for key, value in data.items() if key != "data"}


def _split_data_into_chunks(data: list[object], max_file_size: int) -> list[list[object]]:
    """
    Split JSON data into smaller chunks.

    Parameters:
    data (list): The list of data to split.
    max_file_size (int): The maximum size of each chunk in bytes.

    Returns:
    list: A list of tuples containing the chunks and their indices.
    """
    chunks = []
    current_chunk = []
    current_size = 0

    for item in data:
        item_serialized = orjson.dumps(item)
        item_size = len(item_serialized)
        if current_size + item_size > max_file_size:
            chunks.append(current_chunk)
            current_chunk = []
            current_size = 0
        current_chunk.append(item)
        current_size += item_size

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def _split_layout_json(filename: str, max_file_size=DEFAULT_MAX_FILE_SIZE) -> list[str]:
    """
    Split a Layout JSON file into smaller chunks, delete the original file, and save them along with their headers.

    This function reads a Layout JSON file, extracts the header and data parts,
    and splits the data into multiple smaller chunks based on the maximum file size limit.
    Each chunk along with its header is saved as a separate JSON file.

    Parameters:
    filename (str): The name of the Layout JSON file to be split.
    max_file_size (int): The maximum size of each chunk in bytes (default: 1 MB).

    Returns:
    list: A list of names of the created JSON files.
    """
    try:
        data = _read_and_validate_json(filename)
        header = _extract_header(data)
        file_no_suffix = os.path.splitext(filename)[0]
    except IOError as e:
        print(f"Error reading file {filename}: {e}")
        return []

    header_name = f"{file_no_suffix}-header.json"
    with open(header_name, "wb") as file:
        file.write(orjson.dumps(header))

    chunks = _split_data_into_chunks(data["data"], max_file_size)

    file_names = [header_name]
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(_save_chunk, chunk, file_no_suffix, idx)
            for idx, chunk in enumerate(chunks)
        ]
        for future in futures:
            file_names.append(future.result())

    os.remove(filename)

    return file_names


def run(input_def: str, result_dir: str, layout_json_file: str) -> list[str]:
    """
    in:
    (fix) IEDA_CONFIG_DIR, IEDA_TCL_SCRIPT_DIR, RESULT_DIR
    (var) INPUT_DEF, LAYOUT_JSON_FILE
    out: list of layout json files

    Raises:
        subprocess.CalledProcessError: If the GDS dump command fails
    """
    step_name = StepName.LAYOUT_JSON
    step_cmd = SHELL_CMD[step_name]
    assert pathlib.Path(input_def).exists(), f"Input DEF file not found: {input_def}"
    pathlib.Path(layout_json_file).parent.mkdir(parents=True, exist_ok=True)

    step_env = {
        "INPUT_DEF": input_def,
        "RESULT_DIR": result_dir,
        "LAYOUT_JSON_FILE": layout_json_file,
        "SDC_FILE": DEFAULT_SDC_FILE,
    }

    logging.info(
        "(step.%s) \n subprocess cmd: %s \n subprocess env: %s",
        step_name,
        str(step_cmd),
        str(step_env),
    )

    step_env.update(ENV_TOOLS_PATH)
    ret_code = subprocess.call(step_cmd, env=step_env)
    if ret_code != 0:
        raise subprocess.CalledProcessError(ret_code, step_cmd)

    return _split_layout_json(layout_json_file)


# if __name__ == "__main__":
#     # # note: get test file name from cmd line arg
#     # result_files = _split_layout_json(os.sys.argv[1])
#     # print(result_files)
#     logging.basicConfig(
#         format="[%(asctime)s - %(levelname)s - %(name)s]: %(message)s",
#         level=logging.INFO,
#     )
#     run("/path/to/input_def.def", "layout.json")
