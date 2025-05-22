import json


def check_json_exists(json_file: str) -> bool:
    """
    Check if a JSON file exists and is not empty.

    Args:
        json_file (str): Path to the JSON file.

    Returns:
        bool: True if the file exists and is not empty, False otherwise.
    """
    try:
        with open(json_file, "r") as f:
            data = json.load(f)
            return bool(data)
    except (FileNotFoundError, json.JSONDecodeError):
        return False


def load_json(json_file: str) -> dict:
    """
    Load a JSON file and return its content.

    Args:
        json_file (str): Path to the JSON file.

    Returns:
        dict: Content of the JSON file.
    """
    if check_json_exists(json_file):
        try:
            with open(json_file, "r") as f:
                data = json.load(f)
            return data
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON format in file: {json_file}")
    else:
        raise FileNotFoundError(f"JSON file {json_file} does not exist or is empty.")


def dump_json(json_file: str, data: dict) -> str:
    """
    Dump a dictionary to a JSON file.

    Args:
        json_file (str): Path to the JSON file.
        data (dict): Data to be dumped.

    Returns:
        str: Path to the dumped JSON file.
    """

    try:
        with open(json_file, "w") as f:
            json.dump(data, f, indent=2)
        return json_file
    except Exception as e:
        raise ValueError(f"Failed to dump JSON file {json_file}: {e}")
