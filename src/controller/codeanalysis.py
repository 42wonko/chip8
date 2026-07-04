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

from dataclasses import dataclass
from enum import StrEnum

from emulator.chip8memory import Chip8Memory


class CodeStatus(StrEnum):
    """
    @brief Classification of a Code View entry.
    """

    UNKNOWN = "Unknown"
    CODE = "Code"
    DATA = "Data"


@dataclass(frozen=True, slots=True)
class CodeRow:
    """
    @brief One row displayed by the Code View.
    """

    address: int
    raw_bytes: bytes
    interpretation: str
    status: CodeStatus

    @property
    def length(self) -> int:
        """
        @brief Length of the represented memory region.
        """
        return len(self.raw_bytes)


class CodeAnalysis:
    """
    @brief Maintains the interpreted Code View.
    """
    def __init__(self, memory: Chip8Memory) -> None:
        """
        @brief Construct the Code Analysis subsystem.

        @param memory
            Emulator memory.
        """
        self._memory = memory
        self._rows: list[CodeRow] = []

    def rebuild(self) -> None:
        """
        @brief Rebuild the complete analysis.

        """
        self._rows.clear()

        #
        # TODO:
        # Only display the program region once ROM loading is integrated.
        #
        for address in range(self._memory.size()):
            value = self._memory[address]
            self._rows.append( CodeRow( address=address, raw_bytes=bytes((value,)), interpretation=f"{value:02X}", status=CodeStatus.UNKNOWN))

    def row_count(self) -> int:
        """
        @brief Return the number of visible rows.
        """
        return len(self._rows)

    def row(self, index: int) -> CodeRow:
        """
        @brief Return the specified row.
        """
        return self._rows[index]

    def find_row(self, address: int) -> int | None:
        """
        @brief Find the row representing the specified address.

        @return
            Row index or None if the address is not represented.
        """
        for row_index, row in enumerate(self._rows):
            if row.address <= address < row.address + row.length:
                return row_index

        return None
