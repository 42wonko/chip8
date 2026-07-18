"""
@file test_registers.py

@brief Unit tests for the CHIP-8 register set.
"""

import unittest

from emulator.constants import (
    ADDRESS_MASK,
    BYTE_MASK,
    PROGRAM_START,
    REGISTER_COUNT,
    STACK_POINTER_MASK,
)
from tests.helpers import create_registers


class TestcreateRegisters(unittest.TestCase):
    """
    @brief Tests for the CHIP-8 CPU registers.
    """

    ###########################################################################
    # Construction
    ###########################################################################

    def test_initial_state(self) -> None:
        registers = create_registers()

        for index in range(REGISTER_COUNT):
            self.assertEqual(registers[index], 0)

        self.assertEqual(registers.i, 0)
        self.assertEqual(registers.pc, PROGRAM_START)
        self.assertEqual(registers.sp, 0)

    ###########################################################################
    # General-purpose registers
    ###########################################################################
    def test_read_write_register(self) -> None:
        registers = create_registers()
        registers[0] = 0x12
        registers[5] = 0xAB
        registers[0xF] = 0xFF
        self.assertEqual(registers[0], 0x12)
        self.assertEqual(registers[5], 0xAB)
        self.assertEqual(registers[0xF], 0xFF)

    def test_register_index_too_small(self) -> None:
        registers = create_registers()
        with self.assertRaises(IndexError):
            registers[-1] = 0

    def test_register_index_too_large(self) -> None:
        registers = create_registers()
        with self.assertRaises(IndexError):
            registers[REGISTER_COUNT] = 0

    def test_register_value_wraps(self) -> None:
        registers = create_registers()
        registers[0] = 300
        self.assertEqual(registers[0], 300 & BYTE_MASK)

    ###########################################################################
    # Special registers
    ###########################################################################

    def test_index_register_wraps_to_12_bits(self) -> None:
        registers = create_registers()
        registers.i = 0xFFFF
        self.assertEqual(registers.i, ADDRESS_MASK)

    def test_program_counter_wraps_to_12_bits(self) -> None:
        registers = create_registers()
        registers.pc = 0xFFFF
        self.assertEqual(registers.pc, ADDRESS_MASK)

    def test_stack_pointer_wraps_to_4_bits(self) -> None:
        registers = create_registers()
        registers.sp = 0xFF
        self.assertEqual(registers.sp, STACK_POINTER_MASK)

    def test_program_counter_wraparound(self) -> None:
        registers = create_registers()
        registers.pc = 0x1000
        self.assertEqual(registers.pc, 0)

    def test_stack_pointer_wraparound(self) -> None:
        registers = create_registers()
        registers.sp = 0x10
        self.assertEqual(registers.sp, 0)

    ###########################################################################
    # Reset
    ###########################################################################

    def test_reset(self) -> None:
        registers = create_registers()

        registers[3] = 0x42
        registers.i = 0x456
        registers.pc = 0xAAA
        registers.sp = 7

        registers.reset()

        for index in range(REGISTER_COUNT):
            self.assertEqual(registers[index], 0)

        self.assertEqual(registers.i, 0)
        self.assertEqual(registers.pc, PROGRAM_START)
        self.assertEqual(registers.sp, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
