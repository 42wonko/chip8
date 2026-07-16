"""
@file test_shift.py

@brief Tests for the 8XY6 and 8XYE shift instructions.
"""

import unittest

from tests.helpers import create_machine, write_opcode


class TestShiftInstructions(unittest.TestCase):
    def test_shift_right(self) -> None:
        machine = create_machine()
        machine.registers[4] = 0b10010000
        write_opcode(machine, 0x8406)
        machine.execute_cycle()
        self.assertEqual(machine.registers[4], 0b01001000)
        self.assertEqual(machine.registers[0xF], 0)


    def test_shift_right_sets_flag(self) -> None:
        machine = create_machine()
        machine.registers[4] = 0b10100001
        write_opcode(machine, 0x8406)
        machine.execute_cycle()
        self.assertEqual(machine.registers[4], 0b01010000)
        self.assertEqual(machine.registers[0xF], 1)


    def test_shift_right_null(self) -> None:
        machine = create_machine()
        machine.registers[4] = 0b00000000
        write_opcode(machine, 0x8406)
        machine.execute_cycle()
        self.assertEqual(machine.registers[4], 0b00000000)
        self.assertEqual(machine.registers[0xF], 0)


    def test_shift_right_sets_flag_ignores_VY(self) -> None:
        machine = create_machine()
        machine.registers[4] = 0b10100001
        machine.registers[6] = 42
        write_opcode(machine, 0x8466)
        machine.execute_cycle()
        self.assertEqual(machine.registers[4], 0b01010000)
        self.assertEqual(machine.registers[6], 42)
        self.assertEqual(machine.registers[0xF], 1)


    def test_shift_left(self) -> None:
        machine = create_machine()
        machine.registers[4] = 0b00100001
        write_opcode(machine, 0x840E)
        machine.execute_cycle()
        self.assertEqual(machine.registers[4], 0b01000010)
        self.assertEqual(machine.registers[0xF], 0)


    def test_shift_left_sets_flag(self) -> None:
        machine = create_machine()
        machine.registers[4] = 0b10000001
        write_opcode(machine, 0x840E)
        machine.execute_cycle()
        self.assertEqual(machine.registers[4], 0b00000010)
        self.assertEqual(machine.registers[0xF], 1)

    def test_shift_left_null(self) -> None:
        machine = create_machine()
        machine.registers[4] = 0b00000000
        write_opcode(machine, 0x840E)
        machine.execute_cycle()
        self.assertEqual(machine.registers[4], 0b00000000)
        self.assertEqual(machine.registers[0xF], 0)


    def test_shift_left_sets_flag_ignores_VY(self) -> None:
        machine = create_machine()
        machine.registers[4] = 0b10000001
        machine.registers[6] = 42
        write_opcode(machine, 0x846E)
        machine.execute_cycle()
        self.assertEqual(machine.registers[4], 0b00000010)
        self.assertEqual(machine.registers[6], 42)
        self.assertEqual(machine.registers[0xF], 1)


if __name__ == "__main__":
    unittest.main()
