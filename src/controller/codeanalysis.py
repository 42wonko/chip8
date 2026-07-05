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
from emulator.constants import PROGRAM_START


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

    Derived from the number of raw bytes represented by this row.
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


@dataclass(frozen=True, slots=True)
class WorkItem:
    """
    @brief Analysis work item.

    @details
    Represents one analysis state to be processed by the worklist
    algorithm.

    The call stack is intentionally omitted for now but the type is kept
    separate from a plain address so future analysis phases can extend it
    without changing the traversal algorithm.
    """
    address: int


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

        self._status: list[CodeStatus] = []         # Classification for every memory byte.

        # Instructions discovered by analysis.
        # Key:
        #     Start address.
        # Value:
        #     Decoded instruction.
        self._instructions: dict[int, object] = {}

        # Address range occupied by the currently loaded ROM.
        # An empty range indicates that no ROM is loaded.
        self._rom_start = PROGRAM_START
        self._rom_end = PROGRAM_START

    def set_rom_range(self, start: int, end: int) -> None:
        """
        @brief Set the address range occupied by the loaded ROM.

        @param start
            First ROM address.

        @param end
            First address beyond the ROM.
        """
        if start > end:
            raise ValueError("Invalid ROM range.")
        self._rom_start = start
        self._rom_end = end


    def rebuild(self) -> None:
        """
        @brief Rebuild the complete analysis.
        """
        self._instructions.clear()
        self._initialize_status()
        self._analyze()
        self._build_rows()


    def _initialize_status(self) -> None:
        """
        @brief Initialize the byte classification.

        Bytes inside the ROM are initially UNKNOWN.
        Everything else is DATA.
        """
        self._status = []

        for address in range(self._memory.size()):
            if self._rom_start <= address < self._rom_end:
                self._status.append(CodeStatus.UNKNOWN)
            else:
                self._status.append(CodeStatus.DATA)


    def _get_word(self, address: int) -> int | None:
        """
        @brief Read a 16-bit word from memory.

        @param address
            Address of the first byte.

        @return
            The 16-bit big-endian value or None if the word extends beyond
            memory.
        """
        if address < 0:
            return None
        if address + 1 >= self._memory.size():
            return None
        return (self._memory[address] << 8) | self._memory[address + 1]


    def _analyze(self) -> None:
        """
        @brief Perform code analysis.
        """
        self._instructions.clear()

    def _build_rows(self) -> None:
        """
        @brief Build the immutable CodeRow list.
        """
        rows: list[CodeRow] = []

        address = 0

        while address < self._memory.size():
            instruction = self._instructions.get(address)
            if instruction is not None:
                rows.append( CodeRow( address=address, raw_bytes=bytes((self._memory[address],)), interpretation="", status=CodeStatus.CODE,))
                address += 1
                continue
            rows.append( CodeRow( address=address, raw_bytes=bytes((self._memory[address],)), interpretation=f"{self._memory[address]:02X}", status=self._status[address],))
            address += 1
        self._rows = rows

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
