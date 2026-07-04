"""
@file codeanalysis.py

@brief Code Analysis subsystem.

@details
Maintains the interpreted representation of CHIP-8 program memory for
the Code View.

@author
Michael Dlubatz

@copyright
MIT License
"""

from __future__ import annotations

from emulator.chip8memory import Chip8Memory


class CodeAnalysis:
    """
    @brief Maintains the Code View analysis state.
    """

    def __init__(self, memory: Chip8Memory) -> None:
        """
        @brief Construct a CodeAnalysis object.

        @param memory
            Emulator memory to analyse.
        """
        self._memory = memory
