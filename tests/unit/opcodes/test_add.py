"""
@file test_add.py

@brief Tests for the CHIP-8 add instructions.
"""

import unittest

from emulator.instruction import Instruction
from tests.helpers import create_machine, write_opcode


class TestInstruction(unittest.TestCase):
    ###########################################################################
    # 7XNN
    ###########################################################################
    def test_add_byte(self) -> None:
        machine = create_machine()
        machine.registers[2] = 5
        write_opcode(machine, 0x7207)
        machine.execute_cycle()
        self.assertEqual(machine.registers[2], 12)

    def test_add_byte_wraps(self) -> None:
        machine = create_machine()
        machine.registers[2] = 250
        write_opcode(machine, 0x720A)
        machine.execute_cycle()
        self.assertEqual(machine.registers[2], 4)

    def test_add_byte_preserves_vf(self) -> None:
        machine = create_machine()
        machine.registers[0xF] = 0x42
        machine.registers[2] = 250
        write_opcode(machine, 0x720A)
        machine.execute_cycle()
        self.assertEqual(machine.registers[2], 4)
        self.assertEqual(machine.registers[0xF], 0x42)

    def test_instruction_str_add_byte(self) -> None:
        instruction = Instruction.decode(0x200, 0x720A)
        self.assertEqual(str(instruction), "ADD V2, 0A")

    ###########################################################################
    # 8XY4
    ###########################################################################
    def test_add_register(self) -> None:
        machine = create_machine()
        machine.registers[1] = 10
        machine.registers[2] = 20
        write_opcode(machine, 0x8124)
        machine.execute_cycle()
        self.assertEqual(machine.registers[1], 30)
        self.assertEqual(machine.registers[0xF], 0)


    def test_add_register_sets_carry(self) -> None:
        machine = create_machine()
        machine.registers[1] = 250
        machine.registers[2] = 20
        write_opcode(machine, 0x8124)
        machine.execute_cycle()
        self.assertEqual(machine.registers[1], 14)
        self.assertEqual(machine.registers[0xF], 1)

    def test_add_register_is_not_effected_by_previous_carry(self) -> None:
        machine = create_machine()
        machine.registers[1] = 10
        machine.registers[2] = 20
        machine.registers[0xF] = 1
        write_opcode(machine, 0x8124)
        machine.execute_cycle()
        self.assertEqual(machine.registers[1], 30)
        self.assertEqual(machine.registers[0xF], 0)


    def test_add_register_sets_carry_is_not_effected_by_prvious_carry(self) -> None:
        machine = create_machine()
        machine.registers[1] = 250
        machine.registers[2] = 20
        machine.registers[0xF] = 1
        write_opcode(machine, 0x8124)
        machine.execute_cycle()
        self.assertEqual(machine.registers[1], 14)
        self.assertEqual(machine.registers[0xF], 1)



