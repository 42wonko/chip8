
import unittest

from chip8.exceptions import CallStackUnderflowError, Chip8Error


class TestChip8Error(unittest.TestCase):
    def test_inherits_from_runtime_error(self) -> None:
        self.assertTrue(issubclass(Chip8Error, RuntimeError))

    def test_can_be_raised_and_caught_as_runtime_error(self) -> None:
        with self.assertRaises(RuntimeError):
            raise Chip8Error("Emulator error")


class TestCallStackUnderflowError(unittest.TestCase):
    def test_inherits_from_chip8_error(self) -> None:
        self.assertTrue(issubclass(CallStackUnderflowError, Chip8Error))

    def test_can_be_raised_and_caught_as_chip8_error(self) -> None:
        with self.assertRaises(Chip8Error):
            raise CallStackUnderflowError("RET executed with an empty call stack")

