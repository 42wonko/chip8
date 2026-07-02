"""
@file test_jump.py

@brief Tests for CHIP-8 jump instructions.
"""

import unittest

from tests.helpers import execute_opcode


class TestJumpInstructions(unittest.TestCase):
    ###########################################################################
    # 1NNN
    ###########################################################################
    def test_jp(self) -> None:
        machine = execute_opcode(0x1456)
        self.assertEqual(machine.registers.pc, 0x456)

    ###########################################################################
    # 2NNN
    ###########################################################################
    def test_call(self) -> None:
        machine = execute_opcode(0x2456)
        self.assertEqual(machine.registers.pc, 0x456)
        self.assertEqual(machine.stack.pop(), 0x202)


if __name__ == "__main__":
    unittest.main(verbosity=2)
