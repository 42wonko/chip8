"""
@file test_skip.py

@brief Tests for CHIP-8 skip instructions.
"""

import unittest

from emulator.chip8machine import Chip8Machine
from tests.helpers import write_opcode


class TestSkipInstructions(unittest.TestCase):
    ###########################################################################
    # 3XNN - SKIP if Vx == NN
    ###########################################################################
    def test_se_byte_skips(self) -> None:
        machine = Chip8Machine()
        machine.registers[1] = 0x42
        write_opcode(machine, 0x3142)
        machine.execute_cycle()
        self.assertEqual(machine.registers.pc, 0x204)

    def test_se_byte_does_not_skip(self) -> None:
        machine = Chip8Machine()
        machine.registers[1] = 0x43
        write_opcode(machine, 0x3142)
        machine.execute_cycle()
        self.assertEqual(machine.registers.pc, 0x202)

    ###########################################################################
    # 4XNN - SKIP if Vx != NN
    ###########################################################################
    def test_sne_byte_skips(self) -> None:
        machine = Chip8Machine()
        machine.registers[1] = 0x43
        write_opcode(machine, 0x4142)
        machine.execute_cycle()
        self.assertEqual(machine.registers.pc, 0x204)

    def test_sne_byte_does_not_skip(self) -> None:
        machine = Chip8Machine()
        machine.registers[1] = 0x42
        write_opcode(machine, 0x4142)
        machine.execute_cycle()
        self.assertEqual(machine.registers.pc, 0x202)

    ###########################################################################
    # 5XY0 - SE Vx, Vy
    ###########################################################################
    def test_se_register_skip(self) -> None:
        machine = Chip8Machine()
        machine.registers[1] = 0x55
        machine.registers[2] = 0x55
        write_opcode(machine, 0x5120)
        machine.execute_cycle()
        self.assertEqual(machine.registers.pc, 0x204)


    def test_se_register_no_skip(self) -> None:
        machine = Chip8Machine()
        machine.registers[1] = 0x55
        machine.registers[2] = 0x66
        write_opcode(machine, 0x5120)
        machine.execute_cycle()
        self.assertEqual(machine.registers.pc, 0x202)


    ###########################################################################
    # 9XY0 - SNE Vx, Vy
    ###########################################################################
    def test_sne_register_skip(self) -> None:
        machine = Chip8Machine()
        machine.registers[1] = 0x55
        machine.registers[2] = 0x66
        write_opcode(machine, 0x9120)
        machine.execute_cycle()
        self.assertEqual(machine.registers.pc, 0x204)
        self.assertEqual(machine.registers[1],0x55)
        self.assertEqual(machine.registers[2],0x66)


    def test_sne_register_no_skip(self) -> None:
        machine = Chip8Machine()
        machine.registers[1] = 0x55
        machine.registers[2] = 0x55
        write_opcode(machine, 0x9120)
        machine.execute_cycle()
        self.assertEqual(machine.registers.pc, 0x202)
        self.assertEqual(machine.registers[1],0x55)
        self.assertEqual(machine.registers[2],0x55)


    ###########################################################################
    # EX9E - SKP Vx
    ###########################################################################
    def test_skip_if_key_pressed(self) -> None:
        machine = Chip8Machine()
        machine.registers[1] = 5
        machine.keyboard.press(5)

        write_opcode(machine, 0xE19E)
        machine.execute_cycle()

        self.assertEqual(machine.registers.pc, 0x204)


    def test_skip_if_key_not_pressed(self) -> None:
        machine = Chip8Machine()
        machine.registers[1] = 5

        write_opcode(machine, 0xE19E)
        machine.execute_cycle()

        self.assertEqual(machine.registers.pc, 0x202)


    def test_skip_if_key_pressed_preserves_registers(self) -> None:
        machine = Chip8Machine()
        machine.registers[1] = 5
        machine.registers.i = 0x345
        machine.registers[0xF] = 0x42
        machine.keyboard.press(5)

        write_opcode(machine, 0xE19E)
        machine.execute_cycle()

        self.assertEqual(machine.registers[1], 5)
        self.assertEqual(machine.registers.i, 0x345)
        self.assertEqual(machine.registers[0xF], 0x42)


    ###########################################################################
    # EXA1 - SKNP Vx
    ###########################################################################
    def test_skip_if_key_not_pressed_instruction(self) -> None:
        machine = Chip8Machine()
        machine.registers[1] = 5

        write_opcode(machine, 0xE1A1)
        machine.execute_cycle()

        self.assertEqual(machine.registers.pc, 0x204)


    def test_do_not_skip_if_key_pressed_instruction(self) -> None:
        machine = Chip8Machine()
        machine.registers[1] = 5
        machine.keyboard.press(5)

        write_opcode(machine, 0xE1A1)
        machine.execute_cycle()

        self.assertEqual(machine.registers.pc, 0x202)


    def test_skip_if_key_not_pressed_preserves_registers(self) -> None:
        machine = Chip8Machine()
        machine.registers[1] = 5
        machine.registers.i = 0x345
        machine.registers[0xF] = 0x42

        write_opcode(machine, 0xE1A1)
        machine.execute_cycle()

        self.assertEqual(machine.registers[1], 5)
        self.assertEqual(machine.registers.i, 0x345)
        self.assertEqual(machine.registers[0xF], 0x42)


    ###########################################################################
    # Unsupported variants
    ###########################################################################
    def test_invalid_5xy_opcode(self) -> None:
        machine = Chip8Machine()
        write_opcode(machine, 0x5123)
        with self.assertRaises(NotImplementedError):
            machine.execute_cycle()


    def test_invalid_9xy_opcode(self) -> None:
        machine = Chip8Machine()
        write_opcode(machine, 0x9123)
        with self.assertRaises(NotImplementedError):
            machine.execute_cycle()


if __name__ == "__main__":
    unittest.main(verbosity=2)
