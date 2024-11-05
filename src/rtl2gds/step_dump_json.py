"""
use for 云平台
"""

import os
import re
from concurrent.futures import ThreadPoolExecutor

import orjson

DEFAULT_MAX_FILE_SIZE = 19 * 1024 * 1024  # 19MB in bytes


def _save_chunk(data_chunk, file_no_suffix, index):
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
    try:
        with open(file_name, "wb") as file:
            file.write(orjson.dumps(chunk_data))
        return file_name
    except IOError as e:
        print(f"Error writing file {file_name}: {e}")
        return None


def _remove_bracket_trailing_commas(json_str):
    """
    Remove trailing commas before closing square or curly brackets in a JSON string.

    Parameters:
    json_str (str): The JSON string to process.

    Returns:
    str: The JSON string with trailing commas removed.
    """
    return re.sub(r",\s*([\]}])", r"\1", json_str)


def _read_and_validate_json(filename):
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


def _extract_header(data):
    """
    Extract header from the JSON data.

    Parameters:
    data (dict): The JSON data.

    Returns:
    dict: The header data.
    """
    return {key: value for key, value in data.items() if key != "data"}


def _split_data_into_chunks(data, max_file_size):
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


def split_gds_json(filename: str, max_file_size=DEFAULT_MAX_FILE_SIZE) -> list:
    """
    Split a GDS JSON file into smaller chunks and save them along with their headers.

    This function reads a GDS JSON file, extracts the header and data parts,
    and splits the data into multiple smaller chunks based on the maximum file size limit.
    Each chunk along with its header is saved as a separate JSON file.

    Parameters:
    filename (str): The name of the GDS JSON file to be split.
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

    with open(f"{file_no_suffix}-header.json", "wb") as file:
        file.write(orjson.dumps(header))

    chunks = _split_data_into_chunks(data["data"], max_file_size)

    file_names = []
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(_save_chunk, chunk, file_no_suffix, idx)
            for idx, chunk in enumerate(chunks)
        ]
        for future in futures:
            result = future.result()
            if result:
                file_names.append(result)

    return file_names


if __name__ == "__main__":
    # note: get test file name from cmd line arg
    result_files = split_gds_json(os.sys.argv[1])
    print(result_files)
