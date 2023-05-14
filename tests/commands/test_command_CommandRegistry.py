# Date: 2023-5-13
# Author: Generated by GoCodeo.


import unittest
from unittest.mock import MagicMock, patch
from autogpt.commands.command import CommandRegistry, Command

class TestCommandRegistry(unittest.TestCase):

    def setUp(self):
        self.registry = CommandRegistry()

    # Positive test
    def test_register(self):
        cmd = Command("test_command")
        self.registry.register(cmd)
        self.assertIn("test_command", self.registry.commands)

    # Negative test
    def test_unregister_not_found(self):
        with self.assertRaises(KeyError):
            self.registry.unregister("non_existent_command")

    # Positive test
    def test_unregister(self):
        cmd = Command("test_command")
        self.registry.register(cmd)
        self.registry.unregister("test_command")
        self.assertNotIn("test_command", self.registry.commands)

    # Positive test
    def test_get_command(self):
        cmd = Command("test_command")
        self.registry.register(cmd)
        retrieved_cmd = self.registry.get_command("test_command")
        self.assertEqual(cmd, retrieved_cmd)

    # Negative test
    def test_get_command_not_found(self):
        with self.assertRaises(KeyError):
            self.registry.get_command("non_existent_command")

    # Positive test
    def test_call(self):
        cmd = Command("test_command", lambda: "test_result")
        self.registry.register(cmd)
        result = self.registry.call("test_command")
        self.assertEqual("test_result", result)

    # Negative test
    def test_call_not_found(self):
        with self.assertRaises(KeyError):
            self.registry.call("non_existent_command")

    # Positive test
    def test_command_prompt(self):
        cmd1 = Command("test_command1")
        cmd2 = Command("test_command2")
        self.registry.register(cmd1)
        self.registry.register(cmd2)
        prompt = self.registry.command_prompt()
        self.assertIn("1. test_command1", prompt)
        self.assertIn("2. test_command2", prompt)

    # Positive test
    @patch("importlib.import_module")
    def test_import_commands(self, mock_import_module):
        mock_module = MagicMock()
        mock_command = Command("test_command")
        mock_module.test_command = mock_command
        mock_module.test_command.command = mock_command
        mock_module.AUTO_GPT_COMMAND_IDENTIFIER = True
        mock_import_module.return_value = mock_module

        self.registry.import_commands("test_module")
        self.assertIn("test_command", self.registry.commands)

if __name__ == "__main__":
    unittest.main()
