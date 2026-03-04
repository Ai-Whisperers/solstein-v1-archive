import unittest

from . import system


class TestCommandSystem(unittest.TestCase):
    def test_register_command(self):
        def test_func():
            return "test"

        system.register_command("test", test_func, "Test command")
        self.assertIn("test", system.commands)
        self.assertEqual(system.command_descriptions["test"], "Test command")

    def test_execute_command(self):
        def hello():
            return "hello"

        system.register_command("hello", hello, "Hello command")
        result = system.execute_command("hello")
        self.assertEqual(result, "hello")

    def test_unknown_command(self):
        result = system.execute_command("unknown")
        self.assertIsNone(result)

    def test_list_commands(self):
        def cmd1():
            pass

        def cmd2():
            pass

        system.register_command("cmd1", cmd1, "Command 1")
        system.register_command("cmd2", cmd2, "Command 2")

        commands = system.list_commands()
        self.assertIn("cmd1", commands)
        self.assertIn("cmd2", commands)
        self.assertEqual(commands["cmd1"], "Command 1")
        self.assertEqual(commands["cmd2"], "Command 2")


if __name__ == "__main__":
    unittest.main()
