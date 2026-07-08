"""
@file test_load.py

@brief Tests for the CHIP-8 Load instructions.
"""

import unittest

from emulator.chip8machine import Chip8Machine
from emulator.constants import PROGRAM_START
from tests.helpers import execute_opcode, write_opcode
from emulator.instruction import Instruction


class TestInstruction(unittest.TestCase):
    ###########################################################################
    # 6XNN
    ###########################################################################
    def test_ld_byte(self) -> None:
        machine = execute_opcode(0x61AB)
        self.assertEqual(machine.registers[1], 0xAB)

    ###########################################################################
    # 8XY0 
    ###########################################################################
    def test_ld_register_preserves_source(self) -> None:
        machine = Chip8Machine()
        machine.registers[1] = 0x12
        machine.registers[2] = 0xAB
        write_opcode(machine, 0x8120)
        machine.execute_cycle()
        self.assertEqual(machine.registers[2], 0xAB)

    def test_ld_register_preserves_vf(self) -> None:
        machine = Chip8Machine()
        machine.registers[0xF] = 0x42
        machine.registers[1] = 0x12
        machine.registers[2] = 0xAB
        write_opcode(machine, 0x8120)
        machine.execute_cycle()
        self.assertEqual(machine.registers[1], 0xAB)
        self.assertEqual(machine.registers[0xF], 0x42)


    ###########################################################################
    # ANNN
    ###########################################################################
    def test_ld_i(self) -> None:
        machine = execute_opcode(0xA456)
        self.assertEqual(machine.registers.i, 0x456)
        self.assertEqual(machine.registers.pc, PROGRAM_START + 2)

    def test_ld_registers_unchanged(self) -> None:
        machine = Chip8Machine();
        machine.registers[0] = 1
        machine.registers[1] = 1
        machine.registers[2] = 1
        machine.registers[3] = 1
        machine.registers[4] = 1
        machine.registers[5] = 1
        machine.registers[6] = 1
        machine.registers[7] = 1
        machine.registers[8] = 1
        machine.registers[9] = 1
        machine.registers[0xa] = 1
        machine.registers[0xb] = 1
        machine.registers[0xc] = 1
        machine.registers[0xd] = 1
        machine.registers[0xe] = 1
        machine.registers[0xf] = 1
        machine.timers.delay_timer = 42
        machine.timers.sound_timer = 42
        write_opcode(machine, 0xA456)
        machine.execute_cycle()
        self.assertEqual(machine.registers.i, 0x456)
        self.assertEqual(machine.registers.pc, PROGRAM_START + 2)
        self.assertEqual(machine.registers[0], 1)
        self.assertEqual(machine.registers[1], 1)
        self.assertEqual(machine.registers[2], 1)
        self.assertEqual(machine.registers[3], 1)
        self.assertEqual(machine.registers[4], 1)
        self.assertEqual(machine.registers[5], 1)
        self.assertEqual(machine.registers[6], 1)
        self.assertEqual(machine.registers[7], 1)
        self.assertEqual(machine.registers[8], 1)
        self.assertEqual(machine.registers[9], 1)
        self.assertEqual(machine.registers[0xa], 1)
        self.assertEqual(machine.registers[0xb], 1)
        self.assertEqual(machine.registers[0xc], 1)
        self.assertEqual(machine.registers[0xd], 1)
        self.assertEqual(machine.registers[0xe], 1)
        self.assertEqual(machine.registers[0xf], 1)
        self.assertEqual(machine.timers.delay_timer, 42)
        self.assertEqual(machine.timers.sound_timer, 42)

