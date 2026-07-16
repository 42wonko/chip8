"""
@file test_jump.py

@brief Tests for CHIP-8 jump instructions.
"""

import unittest

from tests.helpers import create_machine, execute_opcode, write_opcode


class TestJumpInstructions(unittest.TestCase):
    ###########################################################################
    # 1NNN
    ###########################################################################
    def test_jp(self) -> None:
        machine = execute_opcode(0x1456)
        self.assertEqual(machine.registers.pc, 0x456)


    ###########################################################################
    # BNNN
    ###########################################################################
    def test_jump_v0_zero(self) -> None:
        """
        @brief Test JP V0, addr with a zero offset.
        """
        machine = create_machine()
        machine.registers.i = 0x000
        machine.registers[0] = 0x00
        machine.registers[0xf] = 0x01
        write_opcode(machine, 0xB300)
        machine.execute_cycle()
        self.assertEqual(machine.registers.pc, 0x0300)
        self.assertEqual(machine.registers.i, 0)
        self.assertEqual(machine.registers[0xf], 0x01)

    def test_jump_v0_offset(self) -> None:
        """
        @brief Test JP V0, addr with a register offset.
        """
        machine = create_machine()
        machine.registers[0] = 0x12
        machine.registers[3] = 0x100    # later chip8 versions changed to PC = NNN+VX. we don't
        write_opcode(machine, 0xB300)
        machine.execute_cycle()
        self.assertEqual(machine.registers.pc, 0x0312)

    def test_jump_v0_ignores_other_registers(self) -> None:
        """
        @brief Test that JP V0, addr only uses register V0.
        """
        machine = create_machine()
        for register in range(16):
            machine.registers[register] = 0xFF
        machine.registers[0] = 0x05
        write_opcode(machine, 0xB300)
        machine.execute_cycle()
        self.assertEqual(machine.registers.pc, 0x0305)

if __name__ == "__main__":
    unittest.main(verbosity=2)
