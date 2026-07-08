"""
@file test_keyboard.py

@brief Tests for CHIP-8 keyboard instructions.
"""

import unittest

from emulator.chip8machine import Chip8Machine
from tests.helpers import write_opcode


class TestKeyboardInstructions(unittest.TestCase):
    def test_skip_if_key_pressed(self) -> None:
        machine = Chip8Machine()
        machine.registers[3] = 5
        machine.keyboard.press(5)
        write_opcode(machine, 0xE39E)
        machine.execute_cycle()
        self.assertEqual(machine.registers.pc, 0x204)


    def test_skip_if_key_pressed_not_pressed(self) -> None:
        machine = Chip8Machine()
        machine.registers[3] = 5
        write_opcode(machine, 0xE39E)
        machine.execute_cycle()
        self.assertEqual(machine.registers.pc, 0x202)


    def test_skip_if_key_not_pressed(self) -> None:
        machine = Chip8Machine()
        machine.registers[4] = 7
        write_opcode(machine, 0xE4A1)
        machine.execute_cycle()
        self.assertEqual(machine.registers.pc, 0x204)


    def test_skip_if_key_not_pressed_pressed(self) -> None:
        machine = Chip8Machine()
        machine.registers[4] = 7
        machine.keyboard.press(7)
        write_opcode(machine, 0xE4A1)
        machine.execute_cycle()
        self.assertEqual(machine.registers.pc, 0x202)

    def test_wait_key_no_key_pressed(self) -> None:
        machine = Chip8Machine()
        machine.registers[3] = 0x55
        write_opcode(machine, 0xF30A)
        machine.execute_cycle()
        self.assertEqual(machine.registers.pc, 0x200)
        self.assertEqual(machine.registers[3], 0x55)


    def test_wait_key_returns_pressed_key(self) -> None:
        machine = Chip8Machine()
        machine.keyboard.press(0xA)
        write_opcode(machine, 0xF30A)
        machine.execute_cycle()
        self.assertEqual(machine.registers.pc, 0x202)
        self.assertEqual(machine.registers[3], 0xA)


    def test_wait_key_returns_first_pressed_key(self) -> None:
        machine = Chip8Machine()
        machine.keyboard.press(9)
        machine.keyboard.press(2)
        machine.keyboard.press(15)
        write_opcode(machine, 0xF30A)
        machine.execute_cycle()
        self.assertEqual(machine.registers.pc, 0x202)
        self.assertEqual(machine.registers[3], 2)


    def test_wait_key_does_not_modify_other_registers(self) -> None:
        machine = Chip8Machine()
        machine.registers[1] = 0x11
        machine.registers[2] = 0x22
        machine.registers[3] = 0x33
        machine.registers.i = 0x345
        machine.keyboard.press(5)
        write_opcode(machine, 0xF20A)
        machine.execute_cycle()
        self.assertEqual(machine.registers[1], 0x11)
        self.assertEqual(machine.registers[2], 5)
        self.assertEqual(machine.registers[3], 0x33)
        self.assertEqual(machine.registers.i, 0x345)


    def test_wait_key_retries_until_key_is_pressed(self) -> None:
        machine = Chip8Machine()
        write_opcode(machine, 0xF10A)
        machine.execute_cycle()
        self.assertEqual(machine.registers.pc, 0x200)
        machine.keyboard.press(4)
        machine.execute_cycle()
        self.assertEqual(machine.registers.pc, 0x202)
        self.assertEqual(machine.registers[1], 4)

if __name__ == "__main__":
    unittest.main(verbosity=2)
