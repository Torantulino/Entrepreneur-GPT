# Date: 2023-5-12
# Author: Generated by GoCodeo.


import unittest
from unittest.mock import MagicMock, patch
from io import StringIO
from autogpt.commands.file_operations import ingest_file

patch_func1 = 'autogpt.commands.file_operations.read_file'
patch_func2 = 'autogpt.commands.file_operations.split_file'

class TestIngestFile(unittest.TestCase):

    def setUp(self):
        self.memory = MagicMock()
        self.memory.add = MagicMock()

    # Positive test case
    @patch("builtins.open", new_callable=lambda: StringIO("This is a test file content."))
    def test_ingest_file_positive(self, mock_open):
        with patch(patch_func1, return_value="This is a test file content.") as mock_read_file:
            with patch(patch_func2, return_value=["This is a test file content."]) as mock_split_file:
                ingest_file("test.txt", self.memory, max_length=4000, overlap=200)

                mock_read_file.assert_called_once_with("test.txt")
                mock_split_file.assert_called_once_with("This is a test file content.", max_length=4000, overlap=200)
                self.memory.add.assert_called_once()

    # Negative test case
    @patch("builtins.open", side_effect=FileNotFoundError("File not found"))
    def test_ingest_file_negative(self, mock_open):
        with patch(patch_func1, side_effect=FileNotFoundError("File not found")) as mock_read_file:
            with self.assertRaises(FileNotFoundError):
                ingest_file("non_existent.txt", self.memory, max_length=4000, overlap=200)

                mock_read_file.assert_called_once_with("non_existent.txt")
                self.memory.add.assert_not_called()

    # Error test case
    @patch("builtins.open", new_callable=lambda: StringIO("This is a test file content."))
    def test_ingest_file_error(self, mock_open):
        with patch(patch_func1, return_value="This is a test file content.") as mock_read_file:
            with patch(patch_func2, side_effect=Exception("Error while splitting file")) as mock_split_file:
                with self.assertRaises(Exception):
                    ingest_file("test.txt", self.memory, max_length=4000, overlap=200)

                    mock_read_file.assert_called_once_with("test.txt")
                    mock_split_file.assert_called_once_with("This is a test file content.", max_length=4000, overlap=200)
                    self.memory.add.assert_not_called()

    # Edge test case
    @patch("builtins.open", new_callable=lambda: StringIO("This is a test file content."))
    def test_ingest_file_edge(self, mock_open):
        with patch(patch_func1, return_value="This is a test file content.") as mock_read_file:
            with patch(patch_func2, return_value=["This is a test file content."]) as mock_split_file:
                ingest_file("test.txt", self.memory, max_length=1, overlap=0)

                mock_read_file.assert_called_once_with("test.txt")
                mock_split_file.assert_called_once_with("This is a test file content.", max_length=1, overlap=0)
                self.memory.add.assert_called()

if __name__ == "__main__":
    unittest.main()