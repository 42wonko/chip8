"""
@file instruction.py

@brief Immutable decoded CHIP-8 instruction.

@author
Michael Dlubatz

@copyright
MIT License
"""

from __future__ import annotations

from dataclasses import dataclass

from chip8.isa.instructionid import InstructionId


@dataclass(frozen=True, slots=True)
class Instruction:
    """
    @brief Immutable decoded CHIP-8 instruction.

    An Instruction represents one decoded instruction located at a specific
    memory address. It contains only decoded instruction data and exposes
    no behaviour. Execution, formatting and static analysis are provided
    by the Instruction Set Architecture.
    """

    address: int
    opcode: int

    id: InstructionId

    x: int
    y: int
    n: int
    nn: int
    nnn: int
