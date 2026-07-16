import unittest

from controller.codeanalysis import CodeAnalysis, CodeStatus
from controller.diagnostic import DiagnosticSource
from controller.diagnostics import Diagnostics
from controller.emulatorconfiguration import EmulatorConfiguration
from controller.logging import LogManager
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
        diagnostics = Diagnostics()
        log_manager = LogManager()
        configuration = EmulatorConfiguration()
        log_manager.configure(configuration)
        self.analysis = CodeAnalysis(self.memory, diagnostics.reporter(DiagnosticSource.ANALYZER), log_manager.application_logger(DiagnosticSource.ANALYZER))


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
        @brief Verify that linear instructions are discovered.
        """
        self.load_rom(
            0x60, 0x01,     # LD V0, 01
            0x61, 0x02,     # LD V1, 02
        )

        self.analysis.rebuild()

        self.assertEqual(self.analysis.row_count(), self.memory.size() - 2)

        row = self.analysis.row(self.analysis.find_row(PROGRAM_START))
        self.assertEqual(row.address, PROGRAM_START)
        self.assertEqual(row.raw_bytes, bytes((0x60, 0x01)))
        self.assertEqual(row.interpretation, "LD V0, 01")
        self.assertEqual(row.status, CodeStatus.CODE)
        self.assertEqual(row.length, 2)

        row = self.analysis.row(self.analysis.find_row(PROGRAM_START + 2))
        self.assertEqual(row.address, PROGRAM_START + 2)
        self.assertEqual(row.raw_bytes, bytes((0x61, 0x02)))
        self.assertEqual(row.interpretation, "LD V1, 02")
        self.assertEqual(row.status, CodeStatus.CODE)
        self.assertEqual(row.length, 2)


    def test_jump_terminates_analysis(self) -> None:
        """
        @brief Verify that JP terminates the current analysis path.
        """
        self.load_rom(
            0x12, 0x04,     # JP 206
            0x60, 0x01,     # LD V0, 01
            0x61, 0x02,     # LD V1, 02
        )
        self.analysis.rebuild()
        row = self.analysis.row(self.analysis.find_row(PROGRAM_START))          # The jump instruction is discovered.
        self.assertEqual(row.interpretation, "JP 204")
        self.assertEqual(row.status, CodeStatus.CODE)
        row = self.analysis.row(self.analysis.find_row(PROGRAM_START + 2))      # The remaining ROM is still unknown because
        self.assertEqual(row.status, CodeStatus.UNKNOWN)
        row = self.analysis.row(self.analysis.find_row(PROGRAM_START + 4))
        self.assertEqual(row.status, CodeStatus.CODE)


    def test_call_follows_subroutine(self) -> None:
        """
        @brief Verify that CALL follows the subroutine entry.

        @details
        Phase 3.3 follows the call target but does not yet return from the
        subroutine. Therefore, execution after the CALL remains unknown.
        """
        self.load_rom(
            0x22, 0x06,     # CALL 206
            0x60, 0x01,     # LD V0, 01
            0x61, 0x02,     # LD V1, 02
            0x62, 0x03,     # LD V2, 03
            0x00, 0xEE,     # RET
        )

        self.analysis.rebuild()
        row = self.analysis.row(self.analysis.find_row(PROGRAM_START))        # CALL is discovered.
        self.assertEqual(row.interpretation, "CALL 206")
        self.assertEqual(row.status, CodeStatus.CODE)
        row = self.analysis.row(self.analysis.find_row(PROGRAM_START + 2))        # Execution after the CALL is not yet discovered.
        self.assertEqual(row.interpretation, "LD V0, 01")
        self.assertEqual(row.status, CodeStatus.CODE)
        row = self.analysis.row(self.analysis.find_row(PROGRAM_START + 4))
        self.assertEqual(row.interpretation, "LD V1, 02")
        self.assertEqual(row.status, CodeStatus.CODE)
        row = self.analysis.row(self.analysis.find_row(PROGRAM_START + 6))        # The subroutine is discovered.
        self.assertEqual(row.interpretation, "LD V2, 03")
        self.assertEqual(row.status, CodeStatus.CODE)
        row = self.analysis.row(self.analysis.find_row(PROGRAM_START + 8))        # RET is also discovered.
        self.assertEqual(row.interpretation, "RET")
        self.assertEqual(row.status, CodeStatus.CODE)


    def test_call_terminates_analysis(self) -> None:
        """
        @brief Verify that CALL terminates the current analysis path.
        """
        self.load_rom(
            0x22, 0x06,     # CALL 206
            0x60, 0x01,     # LD V0, 01
            0x61, 0x02,     # LD V1, 02
        )
        self.analysis.rebuild()
        row = self.analysis.row(self.analysis.find_row(PROGRAM_START))    # The call instruction is discovered.
        self.assertEqual(row.interpretation, "CALL 206")
        self.assertEqual(row.status, CodeStatus.CODE)
        row = self.analysis.row(self.analysis.find_row(PROGRAM_START + 2))    # Phase 3.2 does not follow calls.
        self.assertEqual(row.status, CodeStatus.UNKNOWN)
        row = self.analysis.row(self.analysis.find_row(PROGRAM_START + 4))
        self.assertEqual(row.status, CodeStatus.UNKNOWN)


    def test_return_terminates_analysis(self) -> None:
        """
        @brief Verify that RET terminates the current analysis path.
        """
        self.load_rom(
            0x60, 0x01,     # LD V0, 01
            0x00, 0xEE,     # RET
            0x61, 0x02,     # LD V1, 02
        )
        self.analysis.rebuild()
        row = self.analysis.row(self.analysis.find_row(PROGRAM_START))    # First instruction.
        self.assertEqual(row.status, CodeStatus.CODE)
        row = self.analysis.row(self.analysis.find_row(PROGRAM_START + 2))    # RET is discovered.
        self.assertEqual(row.interpretation, "RET")
        self.assertEqual(row.status, CodeStatus.CODE)
        row = self.analysis.row(self.analysis.find_row(PROGRAM_START + 4))    # Analysis terminates here.
        self.assertEqual(row.status, CodeStatus.UNKNOWN)


    def test_find_row_returns_instruction_start(self) -> None:
        """
        @brief Verify that only instruction start addresses are mapped.
        """
        self.load_rom(
            0x60, 0x01,     # LD V0, 01
        )
        self.analysis.rebuild()
        row = self.analysis.find_row(PROGRAM_START)
        self.assertIsNotNone(row)
        self.assertIsNone(self.analysis.find_row(PROGRAM_START + 1))


    def test_unknown_bytes_remain_unknown(self) -> None:
        """
        @brief Verify that unreachable ROM bytes remain UNKNOWN.
        """
        self.load_rom(
            0x12, 0x06,     # JP 206
            0xFF, 0xFF,     # unreachable
        )
        self.analysis.rebuild()
        row = self.analysis.row(
            self.analysis.find_row(PROGRAM_START + 2)
        )
        self.assertEqual(row.status, CodeStatus.UNKNOWN)


    def test_se_explores_both_paths(self) -> None:
        """
        @brief Verify that SE explores both successor paths.
        """
        self.load_rom(
            0x30, 0x00,     # SE V0, 00
            0x60, 0x01,     # LD V0, 01
            0x61, 0x02,     # LD V1, 02
        )

        self.analysis.rebuild()

        row = self.analysis.row(self.analysis.find_row(PROGRAM_START))
        self.assertEqual(row.status, CodeStatus.CODE)

        row = self.analysis.row(self.analysis.find_row(PROGRAM_START + 2))
        self.assertEqual(row.status, CodeStatus.CODE)

        row = self.analysis.row(self.analysis.find_row(PROGRAM_START + 4))
        self.assertEqual(row.status, CodeStatus.CODE)

    def test_sne_explores_both_paths(self) -> None:
        """
        @brief Verify that SNE explores both successor paths.
        """
        self.load_rom(
            0x40, 0x00,     # SNE V0, 00
            0x60, 0x01,
            0x61, 0x02,
        )

        self.analysis.rebuild()

        for address in (
            PROGRAM_START,
            PROGRAM_START + 2,
            PROGRAM_START + 4,
        ):
            row = self.analysis.row(self.analysis.find_row(address))
            self.assertEqual(row.status, CodeStatus.CODE)

    def test_se_register_explores_both_paths(self) -> None:
        """
        @brief Verify that SE Vx, Vy explores both successor paths.
        """
        self.load_rom(
            0x50, 0x10,     # SE V0, V1
            0x60, 0x01,
            0x61, 0x02,
        )

        self.analysis.rebuild()

        for address in (
            PROGRAM_START,
            PROGRAM_START + 2,
            PROGRAM_START + 4,
        ):
            row = self.analysis.row(self.analysis.find_row(address))
            self.assertEqual(row.status, CodeStatus.CODE)

    def test_analysis_invalid_5xy1_has_no_successors(self) -> None:
        """
        """
        self.load_rom(
            0x00, 0xE0,     # CLS, we need one valid instruction a the beginning
            0x51, 0x21,     # SE V1, V2 (but low nibbe != 0 -> Invalid)
            0x00, 0xE0
        )
        self.analysis.rebuild()
        row = self.analysis.row(self.analysis.find_row(PROGRAM_START))
        self.assertEqual(row.status, CodeStatus.CODE)
        row = self.analysis.row(self.analysis.find_row(PROGRAM_START + 2))
        self.assertEqual(row.status, CodeStatus.DATA)
        row = self.analysis.row(self.analysis.find_row(PROGRAM_START + 4))
        self.assertEqual(row.status, CodeStatus.UNKNOWN)


    def test_sne_register_explores_both_paths(self) -> None:
        """
        @brief Verify that SE Vx, Vy explores both successor paths.
        """
        self.load_rom(
            0x90, 0x10,     # SNE V0, V1
            0x60, 0x01,
            0x61, 0x02,
        )
        self.analysis.rebuild()
        for address in (
            PROGRAM_START,
            PROGRAM_START + 2,
            PROGRAM_START + 4,
        ):
            row = self.analysis.row(self.analysis.find_row(address))
            self.assertEqual(row.status, CodeStatus.CODE)

    def test_sne_ivalid_variants_are_data(self) -> None:
        """
        @brief Verify that ivalid variants of this op-code are categorized as DATA instead of CODE.
        """
        self.load_rom(
            0x00, 0xE0,     # CLS
            0x90, 0x11,     # SNE V=, V1 but last nibble is invalid
            0x60, 0x01,
            0x61, 0x02
        )
        self.analysis.rebuild()
        row = self.analysis.row(self.analysis.find_row(PROGRAM_START))
        self.assertEqual(row.status, CodeStatus.CODE)
        row = self.analysis.row(self.analysis.find_row(PROGRAM_START + 2))
        self.assertEqual(row.status, CodeStatus.DATA)
        row = self.analysis.row(self.analysis.find_row(PROGRAM_START + 4))
        self.assertEqual(row.status, CodeStatus.UNKNOWN)


    def test_skp_register_explores_both_paths(self) -> None:
        """
        @brief Verify that SE Vx, Vy explores both successor paths.
        """
        self.load_rom(
            0xE0, 0x9E,     # SKP
            0x60, 0x01,
            0x61, 0x02,
        )

        self.analysis.rebuild()

        for address in (
            PROGRAM_START,
            PROGRAM_START + 2,
            PROGRAM_START + 4,
        ):
            row = self.analysis.row(self.analysis.find_row(address))
            self.assertEqual(row.status, CodeStatus.CODE)

    def test_sknp_register_explores_both_paths(self) -> None:
        """
        @brief Verify that SE Vx, Vy explores both successor paths.
        """
        self.load_rom(
            0xE0, 0xA1,     # SKNP
            0x60, 0x01,
            0x61, 0x02,
        )

        self.analysis.rebuild()

        for address in (
            PROGRAM_START,
            PROGRAM_START + 2,
            PROGRAM_START + 4,
        ):
            row = self.analysis.row(self.analysis.find_row(address))
            self.assertEqual(row.status, CodeStatus.CODE)


    def test_analysis_invalid_8xy8_has_no_successors(self) -> None:
        """
        """
        self.load_rom(
            0x00, 0xE0,     # CLS
            0x81, 0x28,     # Invalid 8XY8
            0x00, 0xE0,
        )
        self.analysis.rebuild()

        row = self.analysis.row(self.analysis.find_row(PROGRAM_START))
        self.assertEqual(row.status, CodeStatus.CODE)

        row = self.analysis.row(self.analysis.find_row(PROGRAM_START + 2))
        self.assertEqual(row.status, CodeStatus.DATA)

        row = self.analysis.row(self.analysis.find_row(PROGRAM_START + 4))
        self.assertEqual(row.status, CodeStatus.UNKNOWN)


