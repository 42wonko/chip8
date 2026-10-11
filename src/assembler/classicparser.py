"""
@file classicparser.py

@brief Classic CHIP-8 assembler parser.
"""

from __future__ import annotations

from assembler.parser import Parser
from chip8.isa.isa import InstructionSetArchitecture


class ClassicParser(Parser):
    """
    @brief Parser for the Classic CHIP-8 assembler language.
    """

    def __init__(self, isa: InstructionSetArchitecture) -> None:
        """
        @brief Initialize the Classic CHIP-8 parser.

        @param isa
            ISA providing the supported assembler mnemonics.
        """
        super().__init__()
        self._isa = isa


    def _is_instruction_mnemonic(self, mnemonic: str) -> bool:
        """
        @brief Determine whether a mnemonic is supported by Classic CHIP-8.

        @param mnemonic
            Instruction mnemonic.

        @return
            True if the mnemonic is supported by the selected ISA.
        """
        return mnemonic.upper() in self._isa.assembler_mnemonics()
