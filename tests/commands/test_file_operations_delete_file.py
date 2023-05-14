# Date: 2023-5-13
# Author: Generated by GoCodeo.


import os
import unittest
from unittest.mock import MagicMock, patch
from autogpt.commands.file_operations import delete_file
patch_func1 = 'autogpt.commands.file_operations.is_duplicate_operation'
patch_func2 = 'autogpt.commands.file_operations.log_operation'

class TestDeleteFile(unittest.TestCase):

    # Positive test case
    @patch(patch_func1)
    @patch("os.remove")
    @patch(patch_func2)
    def test_delete_file_success(self, mock_log_operation, mock_os_remove, mock_is_duplicate_operation):
        mock_is_duplicate_operation.return_value = False
        filename = "test_file.txt"
        expected_result = "File deleted successfully."

        result = delete_file(filename)

        self.assertEqual(result, expected_result)
        mock_os_remove.assert_called_once_with(filename)
        mock_log_operation.assert_called_once_with("delete", filename)

    # Negative test case
    @patch(patch_func1)
    def test_delete_file_already_deleted(self, mock_is_duplicate_operation):
        mock_is_duplicate_operation.return_value = True
        filename = "test_file.txt"
        expected_result = "Error: File has already been deleted."

        result = delete_file(filename)

        self.assertEqual(result, expected_result)

    # Error test case
    @patch(patch_func1)
    @patch("os.remove")
    def test_delete_file_error(self, mock_os_remove, mock_is_duplicate_operation):
        mock_is_duplicate_operation.return_value = False
        mock_os_remove.side_effect = Exception("File not found")
        filename = "test_file.txt"
        expected_result = "Error: File not found"

        result = delete_file(filename)

        self.assertEqual(result, expected_result)

    # Edge test case
    @patch(patch_func1)
    @patch("os.remove")
    @patch(patch_func2)
    def test_delete_file_empty_filename(self, mock_log_operation, mock_os_remove, mock_is_duplicate_operation):
        mock_is_duplicate_operation.return_value = False
        filename = ""
        expected_result = "Error: File not found"

        with self.assertRaises(Exception) as context:
            delete_file(filename)
            self.assertTrue(expected_result in str(context.exception))

if __name__ == "__main__":
    unittest.main()