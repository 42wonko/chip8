
"""
@file test_call.py

@brief Tests for CHIP-8 call instructions.
"""

import unittest

from emulator.chip8machine import Chip8Machine
from tests.helpers import execute_opcode


class TestCallInstructions(unittest.TestCase):
    ###########################################################################
    # 2NNN
    ###########################################################################
    def test_call(self) -> None:
        machine = execute_opcode(0x2456)
        self.assertEqual(machine.registers.pc, 0x456)
        self.assertEqual(machine.stack.pop(), 0x202)


