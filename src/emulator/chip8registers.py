"""
@file chip8registers.py

@brief CHIP-8 CPU register implementation.

@details
Stores the complete register set of the CHIP-8 virtual machine.

The class contains no emulator logic. It merely stores register values
and ensures that each register behaves according to its hardware width.

@author
Michael Dlubatz

@copyright
MIT License
"""

from __future__ import annotations

from emulator.constants import (
    ADDRESS_MASK,
    BYTE_MASK,
    PROGRAM_START,
    REGISTER_COUNT,
    STACK_POINTER_MASK,
)


class Chip8Registers:
    """
    @brief CHIP-8 CPU registers.
    """

    def __init__(self) -> None:
        """
        @brief Construct the register set.
        """
        self._v: bytearray = bytearray(REGISTER_COUNT)  # registers V0-V15, 8bit
        self._i: int = 0                                # index regiser 12 bit
        self._pc: int = PROGRAM_START                   # program counter, 12 bit
        self._sp: int = 0                               # stack pointer 4 bit

    ###########################################################################
    # General-purpose registers
    ###########################################################################
    def read_register(self, index: int) -> int:
        """
        @brief Read a V register.

        @param index
            Register number.

        @return
            Register value.
        """
        self._validate_register(index)
        return self._v[index]


    def write_register(self, index: int, value: int) -> None:
        """
        @brief Write a V register.

        @param index
            Register number.

        @param value
            Register value.
        """
        self._validate_register(index)
        self._v[index] = value & BYTE_MASK


    ###########################################################################
    # Index register
    ###########################################################################
    @property
    def i(self) -> int:
        """
        @brief Return the index register.
        """
        return self._i

    @i.setter
    def i(self, value: int) -> None:
        """
        @brief Set the index register.
        """
        self._i = value & ADDRESS_MASK


    ###########################################################################
    # Program counter
    ###########################################################################
    @property
    def pc(self) -> int:
        """
        @brief Return the program counter.
        """
        return self._pc

    @pc.setter
    def pc(self, value: int) -> None:
        """
        @brief Set the program counter.
        """
        self._pc = value & ADDRESS_MASK


    ###########################################################################
    # Stack pointer
    ###########################################################################
    @property
    def sp(self) -> int:
        """
        @brief Return the stack pointer.
        """
        return self._sp

    @sp.setter
    def sp(self, value: int) -> None:
        """
        @brief Set the stack pointer.
        """
        self._sp = value & STACK_POINTER_MASK


    ###########################################################################
    # Utility
    ###########################################################################
    def reset(self) -> None:
        """
        @brief Reset all registers.
        """

        self._v[:] = b"\x00" * REGISTER_COUNT

        self._i = 0
        self._pc = PROGRAM_START
        self._sp = 0


    ###########################################################################
    # Python convenience methods
    ###########################################################################
    def __getitem__(self, index: int) -> int:
        """
        @brief Read a register using index notation.
        """
        return self.read_register(index)

    def __setitem__(self, index: int, value: int) -> None:
        """
        @brief Write a register using index notation.
        """
        self.write_register(index, value)


    ###########################################################################
    # Private helpers
    ###########################################################################
    def _validate_register(self, index: int) -> None:
        """
        @brief Validate a register number.

        @param index
            Register number.

        @exception IndexError
            Register number is invalid.
        """
        if index < 0 or index >= REGISTER_COUNT:
            raise IndexError( f"Register V{index:X} is out of range.")
