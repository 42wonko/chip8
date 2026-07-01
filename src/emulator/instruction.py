"""
@file instruction.py

@brief Decoded CHIP-8 instruction.

@details
Represents a single decoded CHIP-8 instruction.

The instruction is immutable and contains the opcode together with its
decoded operands. It does not execute itself; execution is performed by
the CHIP-8 machine.

The instruction address is stored to support debugging, tracing,
disassembly and breakpoint handling.

@author
Michael Dlubatz

@copyright
MIT License
"""

from __future__ import annotations

from dataclasses import dataclass

from emulator.constants import ADDRESS_MASK, BYTE_MASK, NIBBLE_MASK


@dataclass(frozen=True, slots=True)
class Instruction:
    """
    @brief Decoded CHIP-8 instruction.
    """
    address: int
    opcode: int
    x: int
    y: int
    n: int
    nn: int
    nnn: int

    def __str__(self) -> str:
        """
        @brief provides a string representation of the instruction.
        """
        raise NotImplementedError


    @property
    def family(self) -> int:
        """
        @brief Return the primary opcode family.

        @return
            Upper opcode nibble.
        """
        return (self.opcode >> 12) & NIBBLE_MASK


    @classmethod
    def decode( cls, address: int, opcode: int) -> Instruction:
        """
        @brief Decode an opcode.

        @param address
            Address of the instruction.

        @param opcode
            16-bit opcode.

        @return
            Decoded instruction.
        """
        return cls(
            address=address & ADDRESS_MASK,
            opcode=opcode,
            x=(opcode >> 8) & NIBBLE_MASK,
            y=(opcode >> 4) & NIBBLE_MASK,
            n=opcode & NIBBLE_MASK,
            nn=opcode & BYTE_MASK,
            nnn=opcode & ADDRESS_MASK
        )


