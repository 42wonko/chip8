"""
@file operand.py

@brief Evaluated operands used by the assembler-to-ISA interface.
"""

from dataclasses import dataclass
from enum import Enum


class AssemblerOperandType(Enum):
    """
    @brief Types of evaluated assembler operands.
    """
    REGISTER        = "REGISTER"
    INDEX_REGISTER  = "INDEX_REGISTER"
    DELAY_REGISTER  = "DELAY_REGISTER"
    SOUND_REGISTER  = "SOUND_REGISTER"
    KEY             = "KEY"
    BCD_REGISTER    = "BCD_REGISTER"
    FONT_REGISTER   = "FONT_REGISTER"
    VALUE           = "VALUE"
    ADDRESS         = "ADDRESS"


@dataclass(frozen=True, slots=True)
class AssemblerOperand:
    """
    @brief An evaluated operand supplied to the ISA assembler interface.

    The operand contains no parser AST information. Its value has already
    been evaluated by the assembler semantic-analysis stage.
    """
    type: AssemblerOperandType
    value: int
