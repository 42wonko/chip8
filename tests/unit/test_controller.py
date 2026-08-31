"""
@file test_controller.py

@brief Unit tests for the application controller.
"""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

from PyQt6.QtCore import QSettings

from assembler.options import AssemblyOptions
from assembler.result import AssemblyResult
from assembler.target import Target
from controller.controller import Chip8Controller
from controller.emulatorconfiguration import EmulatorConfiguration
from emulator.stepresult import StepResult
from tests.helpers import create_controller


class Chip8ControllerTest(unittest.TestCase):
    """
    @brief Tests for Chip8Controller.
    """

    def test_execute_cycle_preserves_display_changed_result(self) -> None:
        """
        @brief Verify that the controller preserves the StepResult returned
        by the emulator and refreshes the display when it changes.
        """
        from controller.controller import Chip8Controller

        with patch.object(Chip8Controller, "__init__", return_value=None):
            controller = Chip8Controller()
        controller._machine = MagicMock()
        controller._debugger = MagicMock()
        controller._stopped_on_breakpoint = False
        controller._configuration = MagicMock()
        controller._configuration.disable_display_updates = False
        controller._code_analysis = MagicMock()
        controller._code_model = MagicMock()
        controller._update_display = MagicMock()
        controller.update_gui = MagicMock()

        controller._machine.registers.pc = 0x200
        controller._debugger.temporary_breakpoint = None
        controller._debugger.has_any_breakpoint.return_value = False

        result = StepResult(display_changed=True)
        controller._machine.execute_cycle.return_value = result

        controller._execute_cycle()

        controller._machine.execute_cycle.assert_called_once_with()
        controller.update_gui.assert_called_once_with(result)

    def test_execute_cycle_preserves_bnnn_target_result(self) -> None:
        """
        @brief Verify that the controller preserves the BNNN target returned
        by the emulator.
        """

        with patch.object(Chip8Controller, "__init__", return_value=None):
            controller = Chip8Controller()

        controller._machine = MagicMock()
        controller._debugger = MagicMock()
        controller._stopped_on_breakpoint = False
        controller._configuration = MagicMock()
        controller._configuration.disable_display_updates = False
        controller._code_analysis = MagicMock()
        controller._code_model = MagicMock()
        controller.update_gui = MagicMock()

        controller._machine.registers.pc = 0x200
        controller._debugger.temporary_breakpoint = None
        controller._debugger.has_any_breakpoint.return_value = False

        result = StepResult(
            bnnn_target=(0x200, 0x234)
        )
        controller._machine.execute_cycle.return_value = result
        controller._code_analysis.analyze_observed_bnnn_target.return_value = False

        controller._execute_cycle()

        controller._code_analysis.analyze_observed_bnnn_target.assert_called_once_with(
            0x200,
            0x234,
        )
        controller.update_gui.assert_called_once_with(result)


    def test_assembler_file_defaults(self) -> None:
        configuration = EmulatorConfiguration()
        self.assertEqual(configuration.assembler_source_file, "")
        self.assertEqual(configuration.assembler_rom_file, "")
        self.assertEqual(configuration.assembler_listing_file, "")

    def test_assembler_file_settings_round_trip(self) -> None:
        settings = QSettings( QSettings.Format.IniFormat, QSettings.Scope.UserScope, "CHIP8-test", "configuration-test")
        settings.clear()
        configuration = EmulatorConfiguration()
        configuration.assembler_source_file = "/tmp/test.asm"
        configuration.assembler_rom_file = "/tmp/test.ch8"
        configuration.assembler_listing_file = "/tmp/test.lst"
        configuration.write_settings(settings)
        restored = EmulatorConfiguration()
        restored.read_settings(settings)
        self.assertEqual(restored.assembler_source_file, "/tmp/test.asm")
        self.assertEqual(restored.assembler_rom_file, "/tmp/test.ch8")
        self.assertEqual(restored.assembler_listing_file, "/tmp/test.lst")
        settings.clear()

    def test_assembler_file_paths_are_loaded_from_configuration(self) -> None:
        """
        @brief Verify that assembler file paths are initialized from the
        emulator configuration.
        """
        configuration = EmulatorConfiguration()
        configuration.assembler_source_file = "/tmp/test.asm"
        configuration.assembler_rom_file = "/tmp/test.ch8"
        configuration.assembler_listing_file = "/tmp/test.lst"

        with patch.object(Chip8Controller, "__init__", return_value=None):
            controller = Chip8Controller()

        controller._configuration = configuration
        controller._assembler_source_file = (
            Path(configuration.assembler_source_file)
            if configuration.assembler_source_file
            else None
        )
        controller._assembler_rom_file = (
            Path(configuration.assembler_rom_file)
            if configuration.assembler_rom_file
            else None
        )
        controller._assembler_listing_file = (
            Path(configuration.assembler_listing_file)
            if configuration.assembler_listing_file
            else None
        )

        self.assertEqual( controller.assembler_source_file, Path("/tmp/test.asm"))
        self.assertEqual( controller.assembler_rom_file, Path("/tmp/test.ch8"))
        self.assertEqual( controller.assembler_listing_file, Path("/tmp/test.lst"))


    def test_assemble_source_saves_binary_rom(self) -> None:
        """
        @brief Verify that a successful assembly writes the binary ROM.
        """
        with tempfile.TemporaryDirectory() as directory:
            source_file = Path(directory) / "test.asm"
            rom_file = Path(directory) / "test.ch8"
            configuration = EmulatorConfiguration()
            configuration.assembler_source_file     = str(source_file)
            configuration.assembler_rom_file        = str(rom_file)
            configuration.assembler_listing_file    = None
            controller = create_controller(configuration)
            controller._assembler = MagicMock()
            controller._assembler.assemble.return_value = AssemblyResult( success=True, binary_image=bytes([0x00, 0xE0]))
            result = controller.assemble_source( "CLS\n", Target.COSMAC, AssemblyOptions())
            self.assertTrue(result)
            self.assertEqual( rom_file.read_bytes(), bytes([0x00, 0xE0]))


    def test_assemble_source_does_not_save_rom_when_assembly_fails(self) -> None:
        """
        @brief Verify that a failed assembly does not write a ROM.
        """
        with tempfile.TemporaryDirectory() as directory:
            rom_file = Path(directory) / "test.ch8"
            rom_file.write_bytes(bytes([0xAA, 0x55]))

            configuration = EmulatorConfiguration()
            configuration.assembler_source_file     = str(Path(directory) / "test.asm")
            configuration.assembler_rom_file        = str(rom_file)
            configuration.assembler_listing_file    = str(Path(directory) / "test.lst")
            controller = create_controller(configuration)
            controller._assembler = MagicMock()
            controller._assembler.assemble.return_value = AssemblyResult( success=False)
            result = controller.assemble_source( "INVALID\n", Target.COSMAC, AssemblyOptions())
            self.assertFalse(result)
            self.assertEqual( rom_file.read_bytes(), bytes([0xAA, 0x55]))


    def test_save_assembler_source_writes_existing_file(self) -> None:
        """
        @brief Verify that the controller saves assembler source text.
        """
        with tempfile.TemporaryDirectory() as directory:
            source_file = Path(directory) / "test.asm"
            with patch.object(Chip8Controller, "__init__", return_value=None):
                controller = Chip8Controller()
            controller._assembler_source_file = source_file
            controller._configuration = EmulatorConfiguration()
            controller._diagnostics_reporter = MagicMock()
            result = controller.save_assembler_source("CLS\n")
            self.assertTrue(result)
            self.assertEqual( source_file.read_text(encoding="utf-8"), "CLS\n")

    @patch("controller.controller.QFileDialog.getSaveFileName")
    def test_save_assembler_source_establishes_output_files( self, get_save_file_name: Mock) -> None:
        """
        @brief Verify that selecting a source filename establishes the
        default assembler output filenames.
        """
        with tempfile.TemporaryDirectory() as directory:
            source_file = Path(directory) / "test.asm"
            get_save_file_name.return_value         = (str(source_file), "")
            configuration = EmulatorConfiguration()
            configuration.assembler_source_file     = Path(directory) / "test.asm"
            configuration.assembler_rom_file        = Path(directory) / "test.ch8"
            configuration.assembler_listing_file    = Path(directory) / "test.lst"
            controller = create_controller(configuration)
            result = controller.save_assembler_source("CLS\n")
            self.assertTrue(result)
            self.assertEqual(controller.assembler_source_file, source_file)
            self.assertEqual( controller.assembler_rom_file, source_file.with_suffix(".ch8"))
            self.assertEqual( controller.assembler_listing_file, source_file.with_suffix(".lst"))


    @patch("controller.controller.QFileDialog.getSaveFileName")
    def test_save_assembler_source_can_be_cancelled( self, get_save_file_name: Mock) -> None:
        """
        @brief Verify that cancelling the source-file selection aborts Save.
        """
        get_save_file_name.return_value = ("", "")
        configuration = EmulatorConfiguration()
        configuration.assembler_source_file     = None
        configuration.assembler_rom_file        = None
        configuration.assembler_listing_file    = None
        controller = create_controller(configuration)
        result = controller.save_assembler_source("CLS\n")
        self.assertFalse(result)
        self.assertIsNone(controller.assembler_source_file)


    @patch("controller.controller.QFileDialog.getOpenFileName")
    def test_load_assembler_source_reads_source_file( self, get_open_file_name: Mock) -> None:
        """
        @brief Verify that the controller loads assembler source text.
        """
        with tempfile.TemporaryDirectory() as directory:
            source_file = Path(directory) / "test.asm"
            source_file.write_text("CLS\n", encoding="utf-8")
            get_open_file_name.return_value = (str(source_file), "")
            configuration = EmulatorConfiguration()
            configuration.assembler_rom_file        = None
            configuration.assembler_listing_file    = None
            controller = create_controller(configuration)
            source = controller.load_assembler_source()
            self.assertEqual(source, "CLS\n")
            self.assertEqual(controller.assembler_source_file, source_file)
            self.assertEqual( controller.assembler_rom_file, source_file.with_suffix(".ch8"))
            self.assertEqual( controller.assembler_listing_file, source_file.with_suffix(".lst"))


    @patch("controller.controller.QFileDialog.getOpenFileName")
    def test_load_assembler_source_can_be_cancelled( self, get_open_file_name: Mock) -> None:
        """
        @brief Verify that cancelling Open leaves the assembler source unset.
        """
        get_open_file_name.return_value = ("", "")
        configuration = EmulatorConfiguration()
        configuration.assembler_source_file     = None
        controller = create_controller(configuration)
        self.assertIsNone(controller.load_assembler_source())
        self.assertIsNone(controller.assembler_source_file)


    def test_assemble_source_clears_previous_assembler_diagnostics(self) -> None:
        """
        @brief Verify that a new assembly starts with an empty diagnostics
        collection.
        """
        with tempfile.TemporaryDirectory() as directory:
            source_file = Path(directory) / "test.asm"
            configuration = EmulatorConfiguration()
            configuration.assembler_source_file     = str(source_file)
            controller = create_controller(configuration)
            controller._assembler_diagnostics.reporter().error( "Old diagnostic.")
            self.assertEqual( len(controller._assembler_diagnostics._diagnostics), 1)
            controller._assembler = MagicMock()
            controller._assembler.assemble.return_value = AssemblyResult( success=True)
            controller.assemble_source( "CLS\n", Target.COSMAC, AssemblyOptions())
            self.assertEqual( len(controller._assembler_diagnostics._diagnostics), 0)


    @patch("controller.controller.QFileDialog.getSaveFileName")
    def test_save_assembler_source_as_can_be_cancelled( self, get_save_file_name: Mock) -> None:
        """
        @brief Verify that cancelling Save As leaves the source unchanged.
        """
        get_save_file_name.return_value = ("", "")

        controller = create_controller()

        result = controller.save_assembler_source_as("CLS\n")

        self.assertFalse(result)

    @patch("controller.controller.QFileDialog.getSaveFileName")
    def test_save_assembler_source_as_establishes_output_files( self, get_save_file_name: Mock) -> None:
        """
        @brief Verify that Save As establishes the source and output filenames.
        """
        with tempfile.TemporaryDirectory() as directory:
            source_file = Path(directory) / "new_source.asm"

            get_save_file_name.return_value = (str(source_file), "")

            controller = create_controller()

            result = controller.save_assembler_source_as("CLS\n")

            self.assertTrue(result)
            self.assertEqual(
                controller.assembler_source_file,
                source_file
            )
            self.assertEqual(
                controller.assembler_rom_file,
                source_file.with_suffix(".ch8")
            )
            self.assertEqual(
                controller.assembler_listing_file,
                source_file.with_suffix(".lst")
            )

    @patch("controller.controller.QFileDialog.getSaveFileName")
    def test_save_assembler_source_as_writes_source( self, get_save_file_name: Mock) -> None:
        """
        @brief Verify that Save As writes the supplied source text.
        """
        with tempfile.TemporaryDirectory() as directory:
            source_file = Path(directory) / "new_source.asm"

            get_save_file_name.return_value = (str(source_file), "")

            controller = create_controller()

            result = controller.save_assembler_source_as("CLS\n")

            self.assertTrue(result)
            self.assertEqual(
                source_file.read_text(encoding="utf-8"),
                "CLS\n"
            )


