"""
@file test_random.py

@brief Tests for the CHIP-8 random instruction.
"""

from unittest import TestCase
from unittest.mock import patch

from emulator.chip8machine import Chip8Machine
from tests.helpers import write_opcode


class TestRandomInstructions(TestCase):
    def test_random_byte_is_masked(self) -> None:
        machine = Chip8Machine()
        write_opcode(machine, 0xC2F0)
        with patch("random.randint", return_value=0xAB):
            machine.execute_cycle()
        self.assertEqual(machine.registers[2], 0xA0)


    def test_random_byte_zero_mask(self) -> None:
        machine = Chip8Machine()
        write_opcode(machine, 0xC300)
        with patch("random.randint", return_value=0xFF):
            machine.execute_cycle()
        self.assertEqual(machine.registers[3], 0)


    def test_random_byte_full_mask(self) -> None:
        machine = Chip8Machine()
        write_opcode(machine, 0xC4FF)
        with patch("random.randint", return_value=0x5A):
            machine.execute_cycle()
        self.assertEqual(machine.registers[4], 0x5A)
