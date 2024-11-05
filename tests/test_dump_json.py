import os
import unittest
from unittest.mock import MagicMock, mock_open, patch

import orjson

from rtl2gds.step_dump_json import (
    _extract_header,
    _read_and_validate_json,
    _remove_bracket_trailing_commas,
    _save_chunk,
    _split_data_into_chunks,
    split_gds_json,
)


class TestJsonSplitter(unittest.TestCase):

    def setUp(self):
        self.max_file_size = 1024 * 1024  # 1 MB
        self.sample_data = {
            "header": {"key1": "value1"},
            "data": [{"id": 1}, {"id": 2}, {"id": 3}],
        }
        self.sample_json_str = (
            '{"header": {"key1": "value1"}, "data": [{"id": 1}, {"id": 2}, {"id": 3}]}'
        )
        self.cleaned_json_str = (
            '{"header": {"key1": "value1"}, "data": [{"id": 1}, {"id": 2}, {"id": 3}]}'
        )

    def test_remove_bracket_trailing_commas(self):
        result = _remove_bracket_trailing_commas(self.sample_json_str)
        self.assertEqual(result, self.cleaned_json_str)

    def test_save_chunk(self):
        data_chunk = [{"id": 1}]
        file_no_suffix = "testfile"
        index = 0
        with patch("builtins.open", mock_open()) as mocked_file:
            file_name = _save_chunk(data_chunk, file_no_suffix, index)
            self.assertEqual(file_name, "testfile-0.json")
            mocked_file.assert_called_once_with("testfile-0.json", "wb")
            handle = mocked_file()
            handle.write.assert_called_once()

    def test_read_and_validate_json(self):
        with patch("builtins.open", mock_open(read_data=self.cleaned_json_str)):
            result = _read_and_validate_json("fakefile.json")
            self.assertIn("data", result)
            self.assertIsInstance(result["data"], list)

    def test_extract_header(self):
        header = _extract_header(self.sample_data)
        self.assertIn("key1", header)
        self.assertNotIn("data", header)

    def test_split_data_into_chunks(self):
        chunks = _split_data_into_chunks(self.sample_data["data"], self.max_file_size)
        self.assertEqual(
            len(chunks), 1
        )  # Since the data size is small, it should be in one chunk
        self.assertEqual(chunks[0], self.sample_data["data"])

    def test_split_gds_json(self):
        with patch("builtins.open", mock_open(read_data=self.cleaned_json_str)), patch(
            "rtl2gds.step_dump_json._save_chunk", return_value="testfile-0.json"
        ) as mock_save_chunk, patch(
            "rtl2gds.step_dump_json._read_and_validate_json",
            return_value=self.sample_data,
        ):
            result = split_gds_json("fakefile.json")
            self.assertEqual(len(result), 1)
            self.assertIn("testfile-0.json", result)
            mock_save_chunk.assert_called()


if __name__ == "__main__":
    unittest.main()
