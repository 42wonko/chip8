"""
@file test_machine.py
@brief Test for the CHIP-8 machine.
"""
import unittest

from tests.helpers import create_machine


class TestChip8Machine(unittest.TestCase):
    def test_fetch_instruction(self) -> None:
        machine = create_machine()
        machine.memory.write_byte( 0x200, 0x6A)
        machine.memory.write_byte( 0x201, 0x05)
        instruction = machine.fetch_instruction()
        self.assertEqual(instruction.address, 0x200)
        self.assertEqual(instruction.opcode, 0x6A05)
        self.assertEqual(machine.registers.pc, 0x202)

if __name__ == "__main__":
    unittest.main(verbosity=2)

