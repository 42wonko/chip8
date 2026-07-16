"""
@file test_logic.py

@brief Tests for the 8XY0-8XY7 logic instructions.
"""

import unittest

from tests.helpers import create_machine, write_opcode


class TestLogicInstructions(unittest.TestCase):
    def test_ld_register(self) -> None:
        machine = create_machine()
        machine.registers[1] = 0x12
        machine.registers[2] = 0xAB
        write_opcode(machine, 0x8120)
        machine.execute_cycle()
        self.assertEqual(machine.registers[1], 0xAB)


    def test_or_register(self) -> None:
        machine = create_machine()
        machine.registers[1] = 0b1100
        machine.registers[2] = 0b1010
        machine.registers[0xf] = 42
        write_opcode(machine, 0x8121)
        machine.execute_cycle()
        self.assertEqual(machine.registers[1], 0b1110)  # OR works
        self.assertEqual(machine.registers[0xf], 42)    # VF not modified
        self.assertEqual(machine.registers[2], 0b1010)  # V2 not modified


    def test_and_register(self) -> None:
        machine = create_machine()
        machine.registers[1] = 0b1100
        machine.registers[2] = 0b1010
        machine.registers[0xf] = 42
        write_opcode(machine, 0x8122)
        machine.execute_cycle()
        self.assertEqual(machine.registers[1], 0b1000)
        self.assertEqual(machine.registers[0xf], 42)    # VF not modified
        self.assertEqual(machine.registers[2], 0b1010)  # V2 not modified


    def test_xor_register(self) -> None:
        machine = create_machine()
        machine.registers[1] = 0b1100
        machine.registers[2] = 0b1010
        machine.registers[0xf] = 42
        write_opcode(machine, 0x8123)
        machine.execute_cycle()
        self.assertEqual(machine.registers[1], 0b0110)
        self.assertEqual(machine.registers[0xf], 42)    # VF not modified
        self.assertEqual(machine.registers[2], 0b1010)  # V2 not modified



    def test_sub_register(self) -> None:
        machine = create_machine()
        machine.registers[1] = 20
        machine.registers[2] = 5
        write_opcode(machine, 0x8125)
        machine.execute_cycle()
        self.assertEqual(machine.registers[1], 15)
        self.assertEqual(machine.registers[0xF], 1)

    def test_sub_register_equal(self) -> None:
        machine = create_machine()
        machine.registers[1] = 20
        machine.registers[2] = 20
        write_opcode(machine, 0x8125)
        machine.execute_cycle()
        self.assertEqual(machine.registers[1], 0)
        self.assertEqual(machine.registers[0xF], 1)


    def test_sub_register_sets_borrow(self) -> None:
        machine = create_machine()
        machine.registers[1] = 5
        machine.registers[2] = 20
        write_opcode(machine, 0x8125)
        machine.execute_cycle()
        self.assertEqual(machine.registers[1], 241)
        self.assertEqual(machine.registers[0xF], 0)

    def test_sub_register_is_not_effected_by_previous_carry(self) -> None:
        machine = create_machine()
        machine.registers[1] = 20
        machine.registers[2] = 5
        machine.registers[0xF] = 1
        write_opcode(machine, 0x8125)
        machine.execute_cycle()
        self.assertEqual(machine.registers[1], 15)
        self.assertEqual(machine.registers[0xF], 1)


    def test_sub_register_sets_borrow_is_not_effected_by_previous_carry(self) -> None:
        machine = create_machine()
        machine.registers[1] = 5
        machine.registers[2] = 20
        machine.registers[0xF] = 1
        write_opcode(machine, 0x8125)
        machine.execute_cycle()
        self.assertEqual(machine.registers[1], 241)
        self.assertEqual(machine.registers[0xF], 0)


    def test_subn_register(self) -> None:
        machine = create_machine()
        machine.registers[1] = 5
        machine.registers[2] = 20
        write_opcode(machine, 0x8127)
        machine.execute_cycle()
        self.assertEqual(machine.registers[1], 15)
        self.assertEqual(machine.registers[0xF], 1)


    def test_subn_register_sets_borrow(self) -> None:
        machine = create_machine()
        machine.registers[1] = 20
        machine.registers[2] = 5
        write_opcode(machine, 0x8127)
        machine.execute_cycle()
        self.assertEqual(machine.registers[1], 241)
        self.assertEqual(machine.registers[0xF], 0)


    def test_subn_register_ignores_previous_VF(self) -> None:
        machine = create_machine()
        machine.registers[1] = 5
        machine.registers[2] = 20
        machine.registers[0xF] = 1
        write_opcode(machine, 0x8127)
        machine.execute_cycle()
        self.assertEqual(machine.registers[1], 15)
        self.assertEqual(machine.registers[0xF], 1)


    def test_subn_register_sets_borrow_ignores_previous_VF(self) -> None:
        machine = create_machine()
        machine.registers[1] = 20
        machine.registers[2] = 5
        machine.registers[0xF] = 1
        write_opcode(machine, 0x8127)
        machine.execute_cycle()
        self.assertEqual(machine.registers[1], 241)
        self.assertEqual(machine.registers[0xF], 0)


    def test_subn_register_equal(self) -> None:
        machine = create_machine()
        machine.registers[1] = 42
        machine.registers[2] = 42
        write_opcode(machine, 0x8127)
        machine.execute_cycle()
        self.assertEqual(machine.registers[1], 0)
        self.assertEqual(machine.registers[0xF], 1)


if __name__ == "__main__":
    unittest.main()
