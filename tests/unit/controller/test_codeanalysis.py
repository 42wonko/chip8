import unittest

from controller.codeanalysis import CodeAnalysis
from controller.codeanalysis import CodeStatus
from emulator.chip8memory import Chip8Memory
from emulator.constants import PROGRAM_START


class TestCodeAnalysis(unittest.TestCase):
    """
    @brief Unit tests for CodeAnalysis.
    """
    
    def load_rom(self, *bytes_: int) -> None:
        """
        @brief Load a synthetic ROM into memory.

        @param bytes_
            ROM bytes beginning at PROGRAM_START.
        """
        address = PROGRAM_START

        for value in bytes_:
            self.memory.write_byte(address, value)
            address += 1

        self.analysis.set_rom_range(PROGRAM_START, address)


    def setUp(self) -> None:
        """
        @brief Create a fresh analyzer.
        """
        self.memory = Chip8Memory()
        self.analysis = CodeAnalysis(self.memory)


    def test_empty_memory_is_data(self) -> None:
        """
        @brief Verify that memory is DATA before a ROM is loaded.
        """
        self.analysis.rebuild()
        self.assertEqual( self.analysis.row_count(), self.memory.size(),)
        for index in range(self.analysis.row_count()):
            row = self.analysis.row(index)
            self.assertEqual(row.status, CodeStatus.DATA)


    def test_linear_program(self) -> None:
        """
        @brief Verify that linear code is discovered.
        """
        self.load_rom(
            0x60, 0x01,     # LD V0, 01
            0x61, 0x02,     # LD V1, 02
        )

        self.analysis.rebuild()

        row = self.analysis.row(self.analysis.find_row(PROGRAM_START))
        self.assertEqual(row.interpretation, "LD V0, 01")
        self.assertEqual(row.status, CodeStatus.CODE)
        self.assertEqual(row.length, 2)

        row = self.analysis.row(self.analysis.find_row(PROGRAM_START + 2))
        self.assertEqual(row.interpretation, "LD V1, 02")
        self.assertEqual(row.status, CodeStatus.CODE)
        self.assertEqual(row.length, 2)

