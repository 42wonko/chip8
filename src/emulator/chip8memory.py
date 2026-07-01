"""
@file chip8memory.py

@brief CHIP-8 memory implementation.

@details
Implements the 4096-byte memory of the CHIP-8 virtual machine.

The class provides safe access to memory through methods for reading
and writing bytes and words, loading ROM images, and clearing memory.

Memory addresses are validated according to the CHIP-8 specification.
Negative addresses and accesses beyond the end of memory are rejected.

@author
Michael Dlubatz

@copyright
MIT License
"""

from __future__ import annotations

from emulator.constants import MEMORY_SIZE, PROGRAM_START


class Chip8Memory:
    """
    @brief CHIP-8 main memory.
    """
    def __init__(self) -> None:
        """
        @brief Construct an empty memory.
        """
        self._memory: bytearray = bytearray(MEMORY_SIZE)


    ###########################################################################
    # Public interface
    ###########################################################################
    def reset(self) -> None:
        """
        @brief Reset and clear the complete memory.
        """
        self._memory[:] = b"\x00" * MEMORY_SIZE


    def read_byte(self, address: int) -> int:
        """
        @brief Read a single byte.

        @param address
            Memory address.

        @return
            Byte stored at the specified address.
        """
        self._validate_address(address)
        return self._memory[address]


    def write_byte(self, address: int, value: int) -> None:
        """
        @brief Write a single byte.

        @param address
            Memory address.

        @param value
            Byte value.
        """
        self._validate_address(address)
        self._memory[address] = value


    def load_rom(self, data: bytes) -> None:
        """
        @brief Load a ROM image.

        @param data
            ROM contents.
        """
        end: int = PROGRAM_START + len(data)
        if end > MEMORY_SIZE:
            raise ValueError("ROM image exceeds available memory.")

        self.reset()
        self._memory[PROGRAM_START:end] = data


    def size(self) -> int:
        """
        @brief Return memory size.

        @return
            Memory size in bytes.
        """
        return MEMORY_SIZE


    ###########################################################################
    # Python convenience methods
    ###########################################################################
    def __len__(self) -> int:
        """
        @brief Return the memory size.

        @return
            Memory size.
        """

        return MEMORY_SIZE

    def __getitem__(self, address: int) -> int:
        """
        @brief Read a byte using index notation.

        @param address
            Memory address.

        @return
            Byte stored at the specified address.
        """

        return self.read_byte(address)

    ###########################################################################
    # Private helpers
    ###########################################################################
    def _validate_address(self, address: int, length: int = 1) -> None:
        """
        @brief Validate a memory access.

        @param address
            Start address.

        @param length
            Number of bytes to access.

        @exception IndexError
            Address outside valid memory.
        """

        if address < 0:
            raise IndexError( f"Memory address 0x{address:X} is out of range.")

        if address + length > MEMORY_SIZE:
            raise IndexError( f"Memory address 0x{address:03X} is out of range.")
