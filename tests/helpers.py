"""
@file helpers.py

@brief Helper functions for emulator unit tests.
"""

from emulator.chip8machine import Chip8Machine
from emulator.constants import PROGRAM_START


def write_opcode(
    machine: Chip8Machine,
    opcode: int,
    address: int = PROGRAM_START,
) -> None:
    """
    @brief Write one CHIP-8 instruction into memory.

    @param machine
        Target machine.

    @param opcode
        16-bit CHIP-8 instruction.

    @param address
        Memory address.
    """

    machine.memory.write_byte(address, (opcode >> 8) & 0xFF)
    machine.memory.write_byte(address + 1, opcode & 0xFF)
