"""
@file helpers.py

@brief Helper functions for emulator unit tests.
"""

from controller.logging import LogManager
from emulator.chip8machine import Chip8Machine
from emulator.constants import PROGRAM_START


def write_opcode( machine: Chip8Machine, opcode: int, address: int = PROGRAM_START) -> None:
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


def execute_opcode( opcode: int) -> Chip8Machine:
    """
    @brief Execute a single opcode on a fresh machine.

    @return
        Machine after execution.
    """
    machine = create_machine()
    write_opcode(machine, opcode)
    machine.execute_cycle()

    return machine


def create_machine() -> Chip8Machine:
    log_manager = LogManager()
    return Chip8Machine(log_manager.execution_trace_reporter())


