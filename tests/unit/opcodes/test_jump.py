"""
@file test_jump.py

@brief Tests for CHIP-8 jump instructions.
"""

import unittest

from emulator.chip8machine import Chip8Machine
from tests.helpers import execute_opcode, write_opcode
from emulator.instruction import Instruction


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

    
    ###########################################################################
    # BNNN
    ###########################################################################
    def test_jump_v0_zero(self) -> None:
        """
        @brief Test JP V0, addr with a zero offset.
        """
        machine = Chip8Machine()
        machine.registers.i = 0x000
        machine.registers[0] = 0x00
        write_opcode(machine, 0xB300)
        machine.execute_cycle()
        self.assertEqual(machine.registers.pc, 0x0300)

    def test_jump_v0_offset(self) -> None:
        """
        @brief Test JP V0, addr with a register offset.
        """
        machine = Chip8Machine()
        machine.registers[0] = 0x12
        write_opcode(machine, 0xB300)
        machine.execute_cycle()
        self.assertEqual(machine.registers.pc, 0x0312)

    def test_jump_v0_ignores_other_registers(self) -> None:
        """
        @brief Test that JP V0, addr only uses register V0.
        """
        machine = Chip8Machine()
        for register in range(16):
            machine.registers[register] = 0xFF
        machine.registers[0] = 0x05
        write_opcode(machine, 0xB300)
        machine.execute_cycle()
        self.assertEqual(machine.registers.pc, 0x0305)

if __name__ == "__main__":
    unittest.main(verbosity=2)
