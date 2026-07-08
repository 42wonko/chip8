"""
@file test_timer.py

@brief Tests for the CHIP-8 timer instructions.
"""

from unittest import TestCase

from emulator.chip8machine import Chip8Machine
from tests.helpers import write_opcode


class TestTimerInstructions(TestCase):
    def test_load_delay_timer_into_register(self) -> None:
        machine = Chip8Machine()
        machine.timers.delay_timer = 42
        write_opcode(machine, 0xF207)
        machine.execute_cycle()
        self.assertEqual(machine.registers[2], 42)


    def test_store_register_into_delay_timer(self) -> None:
        machine = Chip8Machine()
        machine.registers[3] = 77
        write_opcode(machine, 0xF315)
        machine.execute_cycle()
        self.assertEqual(machine.timers.delay_timer, 77)


    def test_store_register_into_sound_timer(self) -> None:
        machine = Chip8Machine()
        machine.registers[7] = 99
        write_opcode(machine, 0xF718)
        machine.execute_cycle()
        self.assertEqual(machine.timers.sound_timer, 99)

    def test_store_delay_timer_does_not_modify_register(self) -> None:
        machine = Chip8Machine()
        machine.registers[5] = 123
        write_opcode(machine, 0xF515)
        machine.execute_cycle()
        self.assertEqual(machine.registers[5], 123)
        self.assertEqual(machine.timers.delay_timer, 123)


    def test_load_delay_timer_does_not_modify_delay_timer(self) -> None:
        machine = Chip8Machine()
        machine.timers.delay_timer = 42

        write_opcode(machine, 0xF207)
        machine.execute_cycle()

        self.assertEqual(machine.registers[2], 42)
        self.assertEqual(machine.timers.delay_timer, 42)


    def test_load_delay_timer_preserves_registers(self) -> None:
        machine = Chip8Machine()
        machine.timers.delay_timer = 42
        machine.registers.i = 0x345
        machine.registers[0xF] = 0xAA

        write_opcode(machine, 0xF207)
        machine.execute_cycle()

        self.assertEqual(machine.registers[2], 42)
        self.assertEqual(machine.registers.i, 0x345)
        self.assertEqual(machine.registers[0xF], 0xAA)


    def test_store_delay_timer_preserves_index_register(self) -> None:
        machine = Chip8Machine()
        machine.registers.i = 0x345
        machine.registers[5] = 123

        write_opcode(machine, 0xF515)
        machine.execute_cycle()

        self.assertEqual(machine.registers.i, 0x345)
        self.assertEqual(machine.timers.delay_timer, 123)


    def test_store_sound_timer_does_not_modify_register(self) -> None:
        machine = Chip8Machine()
        machine.registers[7] = 99

        write_opcode(machine, 0xF718)
        machine.execute_cycle()

        self.assertEqual(machine.registers[7], 99)
        self.assertEqual(machine.timers.sound_timer, 99)


    def test_store_sound_timer_preserves_index_register(self) -> None:
        machine = Chip8Machine()
        machine.registers.i = 0x345
        machine.registers[7] = 99

        write_opcode(machine, 0xF718)
        machine.execute_cycle()

        self.assertEqual(machine.registers.i, 0x345)
        self.assertEqual(machine.timers.sound_timer, 99)


if __name__ == "__main__":
    import unittest

    unittest.main()
