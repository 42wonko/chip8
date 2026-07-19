"""
@file helpers.py

@brief Helper functions for emulator unit tests.
"""

from controller.diagnostic import DiagnosticSource
from controller.diagnostics import Diagnostics
from controller.logging import LogManager
from emulator.chip8framebuffer import Chip8Framebuffer
from emulator.chip8keyboard import Chip8Keyboard
from emulator.chip8machine import Chip8Machine
from emulator.chip8memory import Chip8Memory
from emulator.chip8registers import Chip8Registers
from emulator.chip8stack import Chip8Stack
from emulator.chip8timers import Chip8Timers
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
    diagnostics = Diagnostics()
    return Chip8Machine(diagnostics.reporter(DiagnosticSource.UNIT_TEST), log_manager.application_logger(DiagnosticSource.UNIT_TEST), log_manager.execution_trace_reporter())

def create_framebuffer() -> Chip8Framebuffer:
    log_manager = LogManager()
    diagnostics = Diagnostics()
    return Chip8Framebuffer(diagnostics.reporter(DiagnosticSource.UNIT_TEST), log_manager.application_logger(DiagnosticSource.UNIT_TEST))

def create_keyboard() -> Chip8Keyboard:
    log_manager = LogManager()
    diagnostics = Diagnostics()
    return Chip8Keyboard(diagnostics.reporter(DiagnosticSource.UNIT_TEST), log_manager.application_logger(DiagnosticSource.UNIT_TEST), log_manager.execution_trace_reporter(), lambda: 0)

def create_memory() -> Chip8Memory:
    log_manager = LogManager()
    diagnostics = Diagnostics()
    return Chip8Memory(diagnostics.reporter(DiagnosticSource.UNIT_TEST), log_manager.application_logger(DiagnosticSource.UNIT_TEST))

def create_registers() -> Chip8Registers:
    log_manager = LogManager()
    diagnostics = Diagnostics()
    return Chip8Registers(diagnostics.reporter(DiagnosticSource.UNIT_TEST), log_manager.application_logger(DiagnosticSource.UNIT_TEST))

def create_stack() -> Chip8Stack:
    log_manager = LogManager()
    diagnostics = Diagnostics()
    return Chip8Stack(diagnostics.reporter(DiagnosticSource.UNIT_TEST), log_manager.application_logger(DiagnosticSource.UNIT_TEST) )

def create_timers() -> Chip8Timers:
    log_manager = LogManager()
    diagnostics = Diagnostics()
    return Chip8Timers(diagnostics.reporter(DiagnosticSource.UNIT_TEST), log_manager.application_logger(DiagnosticSource.UNIT_TEST))


