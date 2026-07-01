"""
@file chip8machine.py

@brief CHIP-8 virtual machine.

@details
Owns all hardware components of the CHIP-8 virtual machine.

The machine provides a single point of access to the virtual hardware.
Instruction execution will be added in a later milestone.

@author
Michael Dlubatz

@copyright
MIT License
"""

from __future__ import annotations

from emulator.chip8framebuffer import Chip8Framebuffer
from emulator.chip8keyboard import Chip8Keyboard
from emulator.chip8memory import Chip8Memory
from emulator.chip8registers import Chip8Registers
from emulator.chip8stack import Chip8Stack
from emulator.chip8timers import Chip8Timers
from emulator.constants import PROGRAM_START
from emulator.instruction import Instruction


class Chip8Machine:
    """
    @brief CHIP-8 virtual machine.
    """
    def __init__(self) -> None:
        """
        @brief Construct the virtual machine.
        @detail All members are private to prevent other classes from accidentally
        replacing any of the hardware components. By decorating them with @property
        we can still use them, though.
        """
        self._memory        = Chip8Memory()
        self._registers     = Chip8Registers()
        self._stack         = Chip8Stack()
        self._timers        = Chip8Timers()
        self._keyboard      = Chip8Keyboard()
        self._framebuffer   = Chip8Framebuffer()


    ###########################################################################
    # Hardware access
    ###########################################################################
    @property
    def memory(self) -> Chip8Memory:
        """
        @brief Return the main memory.
        """
        return self._memory


    @property
    def registers(self) -> Chip8Registers:
        """
        @brief Return the CPU registers.
        """
        return self._registers


    @property
    def stack(self) -> Chip8Stack:
        """
        @brief Return the call stack.
        """
        return self._stack


    @property
    def timers(self) -> Chip8Timers:
        """
        @brief Return the timer registers.
        """
        return self._timers


    @property
    def keyboard(self) -> Chip8Keyboard:
        """
        @brief Return the hexadecimal keypad.
        """
        return self._keyboard


    @property
    def framebuffer(self) -> Chip8Framebuffer:
        """
        @brief Return the framebuffer.
        """
        return self._framebuffer


    ###########################################################################
    # Machine control
    ###########################################################################
    def reset(self) -> None:
        """
        @brief Reset the complete virtual machine.
        """
        self._memory.reset()
        self._registers.reset()
        self._stack.reset()
        self._timers.reset()
        self._keyboard.reset()
        self._framebuffer.reset()


    def load_rom(self, data: bytes) -> None:
        """
        @brief Load a ROM image.

        @param data
            ROM contents.
        """
        self._memory.load_rom(data)
        self._registers.pc = PROGRAM_START


    def tick_timers(self) -> None:
        """
        @brief Advance the hardware timers.
        """
        self._timers.tick()


    def fetch_instruction(self) -> Instruction:
        """
        @brief Fetch and decode the next instruction.
        """
        address = self._registers.pc
        msb = self._memory.read_byte(address)
        lsb = self._memory.read_byte(address + 1)
        opcode = (msb << 8) | lsb
        self._registers.pc += 2
        return Instruction.decode( address, opcode)


    def execute_cycle(self) -> None:
        """
        @brief Execute one instruction.
        """
        instruction = self.fetch_instruction()
        raise NotImplementedError( f"{instruction.opcode:04X}")

