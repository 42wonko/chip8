"""
@file instruction.py

@brief Immutable assembler instruction.

@author
Michael Dlubatz

@copyright
MIT License
"""

from __future__ import annotations

from dataclasses import dataclass

from chip8.isa.instructionid import InstructionId


@dataclass(frozen=True, slots=True)
class AssemblerInstruction:
    """
    @brief Immutable instruction representation used during assembly.

    An AssemblerInstruction contains only the information required to
    encode an instruction for a target instruction set architecture.

    Unlike a decoded Instruction, an AssemblerInstruction has no memory
    address and no machine opcode. Those values are determined during
    assembly and code generation.

    Operand fields are optional because different instructions require
    different combinations of CHIP-8 encoding fields.
    """

    id: InstructionId

    x: int | None = None
    y: int | None = None
    n: int | None = None
    nn: int | None = None
    nnn: int | None = None

