"""
@file test_controller.py

@brief Unit tests for the application controller.
"""

import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
from PyQt6.QtCore import QSettings
from emulator.stepresult import StepResult
from controller.emulatorconfiguration import EmulatorConfiguration
from controller.controller import Chip8Controller

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
