"""
@file test_memory.py

@brief Tests for CHIP-8 memory instructions.
"""

from unittest import TestCase

from emulator.constants import FONT_CHARACTER_SIZE, FONT_START
from tests.helpers import create_machine, write_opcode


class TestMemoryInstructions(TestCase):
    ###########################################################################
    # FX1E - ADD I, Vx
    ###########################################################################
    def test_add_register_to_i(self) -> None:
        machine = create_machine()
        machine.registers.i = 0x300
        machine.registers[2] = 5
        write_opcode(machine, 0xF21E)
        machine.execute_cycle()
        self.assertEqual(machine.registers.i, 0x305)
        self.assertEqual(machine.registers[2], 5)


    def test_add_register_to_i_wraps(self) -> None:
        machine = create_machine()
        machine.registers.i = 0xFFF
        machine.registers[2] = 2
        machine.registers[0xF] = 1
        write_opcode(machine, 0xF21E)
        machine.execute_cycle()
        self.assertEqual(machine.registers.i, 0x001)
        self.assertEqual(machine.registers[0xF], 1)


    ###########################################################################
    # FX29 - LD F, Vx
    ###########################################################################
    def test_load_font_zero(self) -> None:
        machine = create_machine()
        machine.registers[4] = 0
        write_opcode(machine, 0xF429)
        machine.execute_cycle()
        self.assertEqual(machine.registers.i, FONT_START)


    def test_load_font_five(self) -> None:
        machine = create_machine()
        machine.registers[4] = 5
        write_opcode(machine, 0xF429)
        machine.execute_cycle()
        self.assertEqual( machine.registers.i, FONT_START + 5 * FONT_CHARACTER_SIZE)


    def test_load_font_f(self) -> None:
        machine = create_machine()
        machine.registers[4] = 0xF
        write_opcode(machine, 0xF429)
        machine.execute_cycle()
        self.assertEqual( machine.registers.i, FONT_START + 15 * FONT_CHARACTER_SIZE)
        self.assertEqual(machine.registers[4], 0xf)


    ###########################################################################
    # FX33 - LD B, Vx
    ###########################################################################
    def test_store_bcd_zero(self) -> None:
        machine = create_machine()
        machine.registers.i = 0x300
        machine.registers[1] = 0
        write_opcode(machine, 0xF133)
        machine.execute_cycle()
        self.assertEqual(machine.memory.read_byte(0x300), 0)
        self.assertEqual(machine.memory.read_byte(0x301), 0)
        self.assertEqual(machine.memory.read_byte(0x302), 0)


    def test_store_bcd_five(self) -> None:
        machine = create_machine()
        machine.registers.i = 0x300
        machine.registers[1] = 5
        write_opcode(machine, 0xF133)
        machine.execute_cycle()
        self.assertEqual(machine.memory.read_byte(0x300), 0)
        self.assertEqual(machine.memory.read_byte(0x301), 0)
        self.assertEqual(machine.memory.read_byte(0x302), 5)


    def test_store_bcd_42(self) -> None:
        machine = create_machine()
        machine.registers.i = 0x300
        machine.registers[1] = 42
        write_opcode(machine, 0xF133)
        machine.execute_cycle()
        self.assertEqual(machine.memory.read_byte(0x300), 0)
        self.assertEqual(machine.memory.read_byte(0x301), 4)
        self.assertEqual(machine.memory.read_byte(0x302), 2)


    def test_store_bcd_123(self) -> None:
        machine = create_machine()
        machine.registers.i = 0x300
        machine.registers[1] = 123
        write_opcode(machine, 0xF133)
        machine.execute_cycle()
        self.assertEqual(machine.memory.read_byte(0x300), 1)
        self.assertEqual(machine.memory.read_byte(0x301), 2)
        self.assertEqual(machine.memory.read_byte(0x302), 3)


    def test_store_bcd_255(self) -> None:
        machine = create_machine()
        machine.registers.i = 0x300
        machine.registers[1] = 255
        write_opcode(machine, 0xF133)
        machine.execute_cycle()
        self.assertEqual(machine.memory.read_byte(0x300), 2)
        self.assertEqual(machine.memory.read_byte(0x301), 5)
        self.assertEqual(machine.memory.read_byte(0x302), 5)


    ###########################################################################
    # FX55 - LD [I], V0..Vx
    ###########################################################################
    def test_store_registers(self) -> None:
        machine = create_machine()
        machine.registers.i = 0x300
        machine.registers[0] = 10
        machine.registers[1] = 20
        machine.registers[2] = 30
        write_opcode(machine, 0xF255)
        machine.execute_cycle()
        self.assertEqual(machine.memory.read_byte(0x300), 10)
        self.assertEqual(machine.memory.read_byte(0x301), 20)
        self.assertEqual(machine.memory.read_byte(0x302), 30)


    def test_store_registers_leaves_i_unchanged(self) -> None:
        machine = create_machine()
        machine.registers.i = 0x350
        write_opcode(machine, 0xF055)
        machine.execute_cycle()
        self.assertEqual(machine.registers.i, 0x350)


    def test_store_all_registers(self) -> None:
        machine = create_machine()
        machine.registers.i = 0x300
        for register in range(16):
            machine.registers[register] = register
        write_opcode(machine, 0xFF55)
        machine.execute_cycle()
        for register in range(16):
            self.assertEqual( machine.memory.read_byte(0x300 + register), register)


    def test_store_registers_preserves_source_registers(self) -> None:
        machine = create_machine()
        machine.registers.i = 0x300
        machine.registers[0] = 10
        machine.registers[1] = 20
        machine.registers[2] = 30
        machine.registers[0xF] = 99
        write_opcode(machine, 0xF255)
        machine.execute_cycle()
        self.assertEqual(machine.registers[0], 10)
        self.assertEqual(machine.registers[1], 20)
        self.assertEqual(machine.registers[2], 30)
        self.assertEqual(machine.registers[0xF], 99)


    def test_store_registers_does_not_store_registers_above_x(self) -> None:
        machine = create_machine()
        machine.registers.i = 0x300
        machine.memory.write_byte(0x303, 0xAA)
        machine.registers[0] = 10
        machine.registers[1] = 20
        machine.registers[2] = 30
        machine.registers[3] = 40
        write_opcode(machine, 0xF255)
        machine.execute_cycle()
        self.assertEqual(machine.memory.read_byte(0x300), 10)
        self.assertEqual(machine.memory.read_byte(0x301), 20)
        self.assertEqual(machine.memory.read_byte(0x302), 30)
        self.assertEqual(machine.memory.read_byte(0x303), 0xAA)


    ###########################################################################
    # FX65 - LD V0..Vx, [I]
    ###########################################################################
    def test_load_registers(self) -> None:
        machine = create_machine()
        machine.registers.i = 0x300
        machine.memory.write_byte(0x300, 11)
        machine.memory.write_byte(0x301, 22)
        machine.memory.write_byte(0x302, 33)
        write_opcode(machine, 0xF265)
        machine.execute_cycle()
        self.assertEqual(machine.registers[0], 11)
        self.assertEqual(machine.registers[1], 22)
        self.assertEqual(machine.registers[2], 33)


    def test_load_registers_leaves_i_unchanged(self) -> None:
        machine = create_machine()
        machine.registers.i = 0x350
        write_opcode(machine, 0xF065)
        machine.execute_cycle()
        self.assertEqual(machine.registers.i, 0x350)


    def test_load_all_registers(self) -> None:
        machine = create_machine()
        machine.registers.i = 0x300
        for register in range(16):
            machine.memory.write_byte(0x300 + register, register)
        write_opcode(machine, 0xFF65)
        machine.execute_cycle()
        for register in range(16):
            self.assertEqual( machine.registers[register], register)


    def test_load_registers_preserves_registers_above_x(self) -> None:
        machine = create_machine()
        machine.registers.i = 0x300
        machine.memory.write_byte(0x300, 11)
        machine.memory.write_byte(0x301, 22)
        machine.memory.write_byte(0x302, 33)
        machine.registers[3] = 44
        machine.registers[4] = 55
        machine.registers[0xF] = 99
        write_opcode(machine, 0xF265)
        machine.execute_cycle()
        self.assertEqual(machine.registers[3], 44)
        self.assertEqual(machine.registers[4], 55)
        self.assertEqual(machine.registers[0xF], 99)


    def test_load_register_zero_only(self) -> None:
        machine = create_machine()
        machine.registers.i = 0x300
        machine.memory.write_byte(0x300, 123)
        machine.registers[1] = 77
        write_opcode(machine, 0xF065)
        machine.execute_cycle()
        self.assertEqual(machine.registers[0], 123)
        self.assertEqual(machine.registers[1], 77)


if __name__ == "__main__":
    import unittest

    unittest.main(verbosity=2)
