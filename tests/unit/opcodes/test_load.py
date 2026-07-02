"""
@file test_load.py

@brief Tests for the CHIP-8 Load instructions.
"""

import unittest

from emulator.chip8machine import Chip8Machine
from tests.helpers import execute_opcode, write_opcode


class TestInstruction(unittest.TestCase):
    ###########################################################################
    # 6XNN
    ###########################################################################
    def test_ld_byte(self) -> None:
        machine = execute_opcode(0x61AB)
        self.assertEqual(machine.registers[1], 0xAB)

    ###########################################################################
    # 7XNN
    ###########################################################################
    def test_add_byte(self) -> None:
        machine = Chip8Machine()
        machine.registers[2] = 5
        write_opcode(machine, 0x7207)
        machine.execute_cycle()
        self.assertEqual(machine.registers[2], 12)

    def test_add_byte_wraps(self) -> None:
        machine = Chip8Machine()
        machine.registers[2] = 250
        write_opcode(machine, 0x720A)
        machine.execute_cycle()
        self.assertEqual(machine.registers[2], 4)

    ###########################################################################
    # ANNN
    ###########################################################################
    def test_ld_i(self) -> None:
        machine = execute_opcode(0xA456)
        self.assertEqual(machine.registers.i, 0x456)
