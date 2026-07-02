"""
@file test_system.py

@brief Tests for CHIP-8 system instructions.
"""

import unittest

from emulator.chip8machine import Chip8Machine
from tests.helpers import write_opcode


class TestSystemInstructions(unittest.TestCase):
    """
    @brief Tests for system instructions.
    """
    ###########################################################################
    # 00E0 - CLS
    ###########################################################################

    def test_cls(self) -> None:
        machine = Chip8Machine()
        machine.framebuffer.set_pixel(10, 5, True)
        write_opcode(machine, 0x00E0)
        machine.execute_cycle()
        self.assertFalse(machine.framebuffer.get_pixel(10, 5))

    ###########################################################################
    # 00EE - RET
    ###########################################################################
    def test_ret(self) -> None:
        machine = Chip8Machine()
        machine.stack.push(0x456)
        write_opcode(machine, 0x00EE)
        machine.execute_cycle()
        self.assertEqual(machine.registers.pc, 0x456)

    def test_unknown_opcode_raises(self) -> None:
        machine = Chip8Machine()
        write_opcode(machine, 0xFFFF)
        with self.assertRaises(NotImplementedError):
            machine.execute_cycle()

    def test_unknown_opcode_raises_2(self) -> None:
        machine = Chip8Machine()
        write_opcode(machine, 0xFFFF)
        with self.assertRaisesRegex( NotImplementedError, r"FFFF",):
            machine.execute_cycle()

if __name__ == "__main__":
    unittest.main(verbosity=2)
