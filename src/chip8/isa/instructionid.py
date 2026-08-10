"""
@file instructionid.py

@brief Symbolic instruction identifiers for the CHIP-8 Instruction Set Architecture.

@author
Michael Dlubatz

@copyright
MIT License
"""

from __future__ import annotations

from enum import IntEnum


class InstructionId(IntEnum):
    """
    @brief Symbolic identifiers for all supported CHIP-8 instructions.

    Every legal CHIP-8 instruction encoding has its own unique identifier.
    Instruction identifiers are used internally by the Instruction Set
    Architecture to dispatch instruction execution, formatting and static
    analysis.
    """

    SYS          = 1    # 0x0***
    CLS          = 2
    RET          = 3

    JP           = 4    # 0x1***

    CALL         = 5    # 0x2***

    SE_BYTE      = 6    # 0x3***

    SNE_BYTE     = 7    # 0x4***

    SE_REGISTER  = 8    # 0x5***

    LD_BYTE      = 9    # 0x6***

    ADD_BYTE     = 10    # 0x7***

    LD_REGISTER  = 11    # 0x8***
    OR           = 12
    AND          = 13
    XOR          = 14
    ADD_REGISTER = 15
    SUB          = 16
    SHR          = 17
    SUBN         = 18
    SHL          = 19

    SNE_REGISTER = 20    # 0x9***

    LD_I         = 21    # 0xA***

    JP_V0        = 22    # 0xB***

    RND          = 23    # 0xC***

    DRW          = 24    # 0xD***

    SKP          = 25    # 0xE***
    SKNP         = 26

    LD_VX_DT     = 27    # 0xF***
    LD_VX_K      = 28
    LD_DT_VX     = 29
    LD_ST_VX     = 30
    ADD_I_VX     = 31
    LD_F_VX      = 32
    LD_B_VX      = 33
    LD_I_VX      = 34
    LD_VX_I      = 35

    UNKNOWN      = 255    # Decoder could not identify the instruction.
