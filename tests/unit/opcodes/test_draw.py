"""
@file test_draw.py

@brief Tests for CHIP-8 draw instructions.
"""

import unittest

from emulator.chip8machine import Chip8Machine
from tests.helpers import write_opcode


class TestDrawInstructions(unittest.TestCase):
    def test_draw_single_row(self) -> None:
        machine = Chip8Machine()
        machine.registers.i = 0x300
        machine.memory.write_byte(0x300, 0b11110000)
        machine.registers[1] = 10
        machine.registers[2] = 5
        write_opcode(machine, 0xD121)
        machine.execute_cycle()
        self.assertTrue(machine.framebuffer.get_pixel(10, 5))
        self.assertTrue(machine.framebuffer.get_pixel(11, 5))
        self.assertTrue(machine.framebuffer.get_pixel(12, 5))
        self.assertTrue(machine.framebuffer.get_pixel(13, 5))
        self.assertFalse(machine.framebuffer.get_pixel(14, 5))
        self.assertFalse(machine.framebuffer.get_pixel(15, 5))
        self.assertEqual(machine.registers[0xF], 0)


    def test_draw_multiple_rows(self) -> None:
        machine = Chip8Machine()
        machine.registers.i = 0x300
        machine.memory.write_byte(0x300, 0b10000000)
        machine.memory.write_byte(0x301, 0b01000000)
        machine.registers[1] = 20
        machine.registers[2] = 8
        write_opcode(machine, 0xD122)
        machine.execute_cycle()
        self.assertTrue(machine.framebuffer.get_pixel(20, 8))
        self.assertTrue(machine.framebuffer.get_pixel(21, 9))
        self.assertEqual(machine.registers[0xF], 0)


    def test_draw_collision_sets_vf(self) -> None:
        machine = Chip8Machine()
        machine.registers.i = 0x300
        machine.memory.write_byte(0x300, 0b10000000)
        machine.framebuffer.set_pixel(5, 6, True)
        machine.registers[1] = 5
        machine.registers[2] = 6
        write_opcode(machine, 0xD121)
        machine.execute_cycle()
        self.assertFalse(machine.framebuffer.get_pixel(5, 6))
        self.assertEqual(machine.registers[0xF], 1)


    def test_draw_without_collision_clears_vf(self) -> None:
        machine = Chip8Machine()
        machine.registers[0xF] = 1
        machine.registers.i = 0x300
        machine.memory.write_byte(0x300, 0b10000000)
        machine.registers[1] = 12
        machine.registers[2] = 7
        write_opcode(machine, 0xD121)
        machine.execute_cycle()
        self.assertEqual(machine.registers[0xF], 0)


    def test_draw_twice_erases_sprite(self) -> None:
        machine = Chip8Machine()
        machine.registers.i = 0x300
        machine.memory.write_byte(0x300, 0b11000000)
        machine.registers[1] = 3
        machine.registers[2] = 4
        write_opcode(machine, 0xD121)
        machine.execute_cycle()
        self.assertTrue(machine.framebuffer.get_pixel(3, 4))
        self.assertTrue(machine.framebuffer.get_pixel(4, 4))
        machine.registers.pc = 0x200
        machine.execute_cycle()
        self.assertFalse(machine.framebuffer.get_pixel(3, 4))
        self.assertFalse(machine.framebuffer.get_pixel(4, 4))
        self.assertEqual(machine.registers[0xF], 1)


    def test_draw_wraps_horizontally(self) -> None:
        machine = Chip8Machine()
        machine.registers.i = 0x300
        machine.memory.write_byte(0x300, 0b11000000)
        machine.registers[1] = 63
        machine.registers[2] = 10
        write_opcode(machine, 0xD121)
        machine.execute_cycle()
        self.assertTrue(machine.framebuffer.get_pixel(63, 10))
        self.assertTrue(machine.framebuffer.get_pixel(0, 10))


    def test_draw_wraps_vertically(self) -> None:
        machine = Chip8Machine()
        machine.registers.i = 0x300
        machine.memory.write_byte(0x300, 0b10000000)
        machine.memory.write_byte(0x301, 0b10000000)
        machine.registers[1] = 15
        machine.registers[2] = 31
        write_opcode(machine, 0xD122)
        machine.execute_cycle()
        self.assertTrue(machine.framebuffer.get_pixel(15, 31))
        self.assertTrue(machine.framebuffer.get_pixel(15, 0))


    def test_draw_wraps_both_axes(self) -> None:
        machine = Chip8Machine()
        machine.registers.i = 0x300
        machine.memory.write_byte(0x300, 0b10000001)
        machine.registers[1] = 63
        machine.registers[2] = 31
        write_opcode(machine, 0xD121)
        machine.execute_cycle()
        self.assertTrue(machine.framebuffer.get_pixel(63, 31))
        self.assertTrue(machine.framebuffer.get_pixel(6, 31))


    def test_draw_zero_height(self) -> None:
        machine = Chip8Machine()
        machine.registers.i = 0x300
        machine.memory.write_byte(0x300, 0xFF)
        machine.registers[1] = 5
        machine.registers[2] = 5
        write_opcode(machine, 0xD120)
        machine.execute_cycle()
        self.assertEqual(machine.registers[0xF], 0)
        for y in range(32):
            for x in range(64):
                self.assertFalse(machine.framebuffer.get_pixel(x, y))


if __name__ == "__main__":
    unittest.main(verbosity=2)
