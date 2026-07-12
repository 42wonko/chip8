"""
@file test_random.py

@brief Tests for the CHIP-8 random instruction.
"""

from unittest import TestCase
from unittest.mock import patch

from emulator.chip8machine import Chip8Machine
from emulator.constants import PROGRAM_START
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

    def test_random_VX_only_masking(self) -> None:
        machine = Chip8Machine()
        machine.registers[0] = 42
        machine.registers[1] = 42
        machine.registers[2] = 42
        machine.registers[3] = 42
        machine.registers[4] = 42
        machine.registers[5] = 42
        machine.registers[6] = 42
        machine.registers[7] = 42
        machine.registers[8] = 42
        machine.registers[9] = 42
        machine.registers[0xa] = 42
        machine.registers[0xb] = 42
        machine.registers[0xc] = 42
        machine.registers[0xd] = 42
        machine.registers[0xe] = 42
        machine.registers[0xf] = 42
        machine.registers.i = 123
        write_opcode(machine, 0xC30F)   # random 4-bit value in V4
        machine.execute_cycle()
        self.assertEqual(machine.registers.pc, PROGRAM_START + 2)
        self.assertEqual(machine.registers[0], 42)
        self.assertEqual(machine.registers[1], 42)
        self.assertEqual(machine.registers[2], 42)
        self.assertEqual(machine.registers[4], 42)
        self.assertEqual(machine.registers[5], 42)
        self.assertEqual(machine.registers[6], 42)
        self.assertEqual(machine.registers[7], 42)
        self.assertEqual(machine.registers[8], 42)
        self.assertEqual(machine.registers[9], 42)
        self.assertEqual(machine.registers[0xa], 42)
        self.assertEqual(machine.registers[0xb], 42)
        self.assertEqual(machine.registers[0xc], 42)
        self.assertEqual(machine.registers[0xd], 42)
        self.assertEqual(machine.registers[0xe], 42)
        self.assertEqual(machine.registers[0xf], 42)
        self.assertEqual(machine.registers.i, 123)
        self.assertIn(machine.registers[3], list(range(0,15)))


