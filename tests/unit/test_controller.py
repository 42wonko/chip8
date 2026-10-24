"""
@file test_controller.py

@brief Unit tests for the application controller.
"""

import tempfile
import unittest
from pathlib import Path
from typing import cast
from unittest.mock import MagicMock, Mock, patch, call

from PyQt6.QtCore import QPoint, QSettings

from assembler.classicparser import ClassicParser
from assembler.options import AssemblyOptions
from assembler.result import AssemblyResult
from assembler.target import Target
from assembler.target_selector import TargetSelection, TargetSelectionError
from chip8.isa.classicisa import ClassicInstructionSetArchitecture
from chip8.isa.schipcisa import SCHIPCInstructionSetArchitecture
from chip8.isa.superchip10isa import SuperChip10InstructionSetArchitecture
from chip8.isa.superchip11isa import SuperChip11InstructionSetArchitecture
from chip8.isa.superchipmodernisa import SuperChipModernInstructionSetArchitecture
from controller.controller import Chip8Controller
from controller.diagnostics import AssemblerDiagnostics
from controller.emulatorconfiguration import EmulationMode, EmulatorConfiguration
from emulator.stepresult import StepResult
from tests.helpers import create_controller


class Chip8ControllerTest(unittest.TestCase):
    """
    @brief Tests for Chip8Controller.
    """

    def _set_assembler_mock( self, controller: Chip8Controller, result: AssemblyResult,) -> None:
        assembler = MagicMock()
        assembler.assemble.return_value = result
        controller._create_assembler = MagicMock(return_value=assembler)

    def _invoke_code_context_menu( self, breakpoint_state: str, selected_action: str | None) -> tuple[Chip8Controller, MagicMock, dict[str, MagicMock]]:
        """Invoke the code context menu with a mocked Qt menu."""
        controller = create_controller()
        address = 0x345
        controller._code_analysis.row = MagicMock(return_value=Mock(address=address))
        controller._code_model.refresh = MagicMock()
        controller._diagnostics.clear()
        if breakpoint_state == "enabled":
            controller._debugger.set_breakpoint(address)
        elif breakpoint_state == "disabled":
            controller._debugger.set_breakpoint(address)
            controller._debugger.disable_breakpoint(address)
        actions = {
            name: MagicMock(name=name)
            for name in (
                "Set Breakpoint",
                "Clear Breakpoint",
                "Enable Breakpoint",
                "Disable Breakpoint",
                "Clear All Breakpoints"
            )
        }
        menu = MagicMock()
        menu.addAction.side_effect = lambda action: ( action if not isinstance(action, str) else actions[action])
        actions["Set PC"] = MagicMock(name="Set PC")
        with (
            patch("controller.controller.QMenu", return_value=menu),
            patch("controller.controller.QAction", return_value=actions["Set PC"])
        ):
            menu.exec.return_value = ( None if selected_action is None else actions[selected_action])
            controller._show_code_context_menu(0, QPoint(0, 0))
        return controller, menu, actions


    ##########################################################################
    # Testing context menu
    ##########################################################################
    def test_code_context_menu_sets_breakpoint(self) -> None:
        controller, menu, actions = self._invoke_code_context_menu(
            "none",
            "Set Breakpoint"
        )
        self.assertTrue(controller._debugger.is_breakpoint_enabled(0x345))
        controller._code_model.refresh.assert_called_once_with()
        self.assertIn(
            "Breakpoint set at address 0x345.",
            [diagnostic.message for diagnostic in controller._diagnostics]
        )

    def test_code_context_menu_disables_breakpoint(self) -> None:
        controller, menu, actions = self._invoke_code_context_menu(
            "enabled",
            "Disable Breakpoint"
        )
        self.assertTrue(controller._debugger.is_breakpoint_disabled(0x345))
        controller._code_model.refresh.assert_called_once_with()

    def test_code_context_menu_enables_breakpoint(self) -> None:
        controller, menu, actions = self._invoke_code_context_menu(
            "disabled",
            "Enable Breakpoint"
        )
        self.assertTrue(controller._debugger.is_breakpoint_enabled(0x345))
        controller._code_model.refresh.assert_called_once_with()

    def test_code_context_menu_clears_breakpoint(self) -> None:
        controller, menu, actions = self._invoke_code_context_menu(
            "enabled",
            "Clear Breakpoint"
        )
        self.assertFalse(controller._debugger.has_breakpoints())
        controller._code_model.refresh.assert_called_once_with()

    def test_code_context_menu_dismissal_does_not_refresh_model(self) -> None:
        controller, menu, actions = self._invoke_code_context_menu(
            "none",
            None
        )
        controller._code_model.refresh.assert_not_called()
        self.assertFalse(controller._debugger.has_breakpoints())

    def test_code_context_menu_clears_all_breakpoints(self) -> None:
        controller = create_controller()
        controller._debugger.set_breakpoint(0x345)
        controller._debugger.set_breakpoint(0x346)
        controller._debugger.disable_breakpoint(0x346)
        controller._debugger.set_temporary_breakpoint(0x347)
        actions = {
            name: MagicMock(name=name)
            for name in (
                "Set Breakpoint",
                "Clear Breakpoint",
                "Enable Breakpoint",
                "Disable Breakpoint",
                "Clear All Breakpoints"
            )
        }
        menu = MagicMock()
        menu.addAction.side_effect = lambda action: ( action if not isinstance(action, str) else actions[action])
        clear_all_action = actions["Clear All Breakpoints"]
        with (
            patch("controller.controller.QMenu", return_value=menu),
            patch( "controller.controller.QAction", return_value=MagicMock(name="Set PC"))
        ):
            menu.exec.return_value = clear_all_action
            controller._code_analysis.row = MagicMock( return_value=Mock(address=0x345))
            controller._code_model.refresh = MagicMock()
            controller._show_code_context_menu(0, QPoint(0, 0))
        self.assertFalse(controller._debugger.has_breakpoints())
        self.assertIsNone(controller._debugger.temporary_breakpoint)
        controller._code_model.refresh.assert_called_once_with()

    @patch("controller.controller.QMenu")
    @patch("controller.controller.QAction")
    def test_code_context_menu_clears_all_breakpoints( self, action_class: Mock, menu_class: Mock) -> None:
        """Verify the context menu clears all breakpoints and refreshes code."""
        controller = create_controller()
        address = 0x234
        controller._code_analysis.row = MagicMock( return_value=MagicMock(address=address))
        controller._debugger.is_breakpoint_enabled = MagicMock( return_value=False)
        controller._debugger.is_breakpoint_disabled = MagicMock( return_value=False)
        controller._debugger.has_breakpoints = MagicMock(return_value=True)
        controller._debugger.clear_all_breakpoints = MagicMock()
        controller._code_model.refresh = MagicMock()
        controller._diagnostics_reporter.info = MagicMock()
        set_pc_action = MagicMock()
        set_breakpoint_action = MagicMock()
        clear_all_action = MagicMock()
        action_class.return_value = set_pc_action
        menu = menu_class.return_value
        menu.addAction.side_effect = [ set_pc_action, set_breakpoint_action, clear_all_action ]
        menu.exec.return_value = clear_all_action
        controller._show_code_context_menu(0, QPoint(0, 0))
        controller._debugger.clear_all_breakpoints.assert_called_once_with()
        controller._diagnostics_reporter.info.assert_called_with( "All breakpoints cleared.")
        controller._code_model.refresh.assert_called_once_with()

    @patch("controller.controller.QMenu")
    @patch("controller.controller.QAction")
    def test_code_context_menu_refreshes_when_unrecognized_action_selected( self, action_class: Mock, menu_class: Mock) -> None:
        """Verify the code model refreshes for an unrecognized menu action."""
        controller = create_controller()
        address = 0x234
        controller._code_analysis.row = MagicMock( return_value=MagicMock(address=address))
        controller._debugger.is_breakpoint_enabled = MagicMock( return_value=False)
        controller._debugger.is_breakpoint_disabled = MagicMock( return_value=False)
        controller._debugger.has_breakpoints = MagicMock(return_value=True)
        controller._debugger.clear_all_breakpoints = MagicMock()
        controller._code_model.refresh = MagicMock()
        set_pc_action = MagicMock()
        unknown_action = object()
        action_class.return_value = set_pc_action
        menu = menu_class.return_value
        menu.addAction.side_effect = [ set_pc_action, MagicMock(), MagicMock() ]
        menu.exec.return_value = unknown_action
        controller._main_window.codeTableView.viewport.return_value.mapToGlobal.return_value = QPoint(0, 0)
        controller._show_code_context_menu(0, QPoint(0, 0))
        controller._debugger.clear_all_breakpoints.assert_not_called()
        controller._code_model.refresh.assert_called_once_with()

    @patch("controller.controller.QAction")
    @patch("controller.controller.QMenu")
    def test_show_code_context_menu_sets_program_counter( self, mock_menu_class: MagicMock, mock_action_class: MagicMock) -> None:
        """Verify that selecting Set PC delegates to the controller."""
        controller = create_controller()
        address = 0x234
        row = 3
        controller._code_analysis.row = MagicMock( return_value=MagicMock(address=address))
        controller._running = False
        controller._set_program_counter = MagicMock()
        controller._code_model.refresh = MagicMock()
        menu = mock_menu_class.return_value
        set_pc_action = mock_action_class.return_value
        menu.exec.return_value = set_pc_action
        controller._debugger.has_breakpoints = MagicMock(return_value=False)
        controller._debugger.is_breakpoint_enabled = MagicMock(return_value=False)
        controller._debugger.is_breakpoint_disabled = MagicMock(return_value=False)
        controller._show_code_context_menu(row, MagicMock())
        controller._set_program_counter.assert_called_once_with(address)
        controller._code_model.refresh.assert_not_called()

    ##########################################################################
    # CPU failure and temporary-breakpoint paths.
    ##########################################################################
    def test_execute_cycle_stops_when_instruction_is_not_implemented(self) -> None:
        controller = create_controller()
        controller._running = True
        controller._debugger.clear_all_breakpoints()
        controller._debugger.clear_temporary_breakpoint()
        controller._stopped_on_breakpoint = False
        controller._machine.execute_cycle = MagicMock( side_effect=NotImplementedError)
        controller.update_gui = MagicMock()
        controller._diagnostics.clear()
        controller._execute_cycle()
        self.assertFalse(controller._running)
        controller._machine.execute_cycle.assert_called_once_with()
        controller.update_gui.assert_called_once_with()
        messages = [diagnostic.message for diagnostic in controller._diagnostics]
        self.assertTrue( any("Not implemented!" in message for message in messages), messages)

    ##########################################################################
    # hardware timer coverage
    ##########################################################################
    def test_timer_tick_starts_beeper_when_sound_timer_is_positive(self) -> None:
        controller = create_controller()
        controller._machine.timers.sound_timer = 1
        controller._beeper = MagicMock()
        controller._update_register_view = MagicMock()
        with patch.object(controller._machine, "tick_timers") as tick_timers:
            controller._timer_tick()
        tick_timers.assert_called_once_with()
        controller._beeper.start.assert_called_once_with()
        controller._beeper.stop.assert_not_called()
        controller._update_register_view.assert_called_once_with()


    def test_timer_tick_stops_beeper_when_sound_timer_is_zero(self) -> None:
        controller = create_controller()
        controller._machine.timers.sound_timer = 0
        controller._beeper = MagicMock()
        controller._update_register_view = MagicMock()
        with patch.object(controller._machine, "tick_timers") as tick_timers:
            controller._timer_tick()
        tick_timers.assert_called_once_with()
        controller._beeper.stop.assert_called_once_with()
        controller._beeper.start.assert_not_called()
        controller._update_register_view.assert_called_once_with()


    def test_timer_tick_skips_register_update_when_display_updates_disabled(self) -> None:
        configuration = EmulatorConfiguration()
        configuration.disable_display_updates = True
        controller = create_controller(configuration)
        controller._beeper = MagicMock()
        controller._update_register_view = MagicMock()
        with patch.object(controller._machine, "tick_timers") as tick_timers:
            controller._timer_tick()
        tick_timers.assert_called_once_with()
        controller._update_register_view.assert_not_called()

    ##########################################################################
    # assembler source-file read failure path
    ##########################################################################
    @patch("controller.controller.Path.read_text", side_effect=OSError("Permission denied"))
    @patch("controller.controller.QFileDialog.getOpenFileName")
    def test_load_assembler_source_reports_read_failure( self, get_open_file_name: Mock, read_text: Mock) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source_file = Path(directory) / "test.asm"
            get_open_file_name.return_value = (str(source_file), "")
            controller = create_controller()
            source = controller.load_assembler_source()
            self.assertIsNone(source)
            read_text.assert_called_once_with(encoding="utf-8")
            self.assertIsNone(controller.assembler_source_file)
            messages = [ diagnostic.message for diagnostic in controller._assembler_diagnostics ]
            self.assertEqual(
                messages,
                [
                    "Loading assembly source file 'test.asm'.",
                    "Unable to load assembly source 'test.asm': Permission denied"
                ]
            )

    def test_missing_remembered_rom_is_removed_from_settings(self) -> None:
        configuration = EmulatorConfiguration()
        settings = MagicMock()
        def settings_value(key: str, default: object = None, **kwargs: object) -> object:
            if key == "recent/last_rom":
                return "/missing/remembered.rom"
            return default
        settings.value.side_effect = settings_value
        settings_manager = MagicMock()
        settings_manager.settings.return_value = settings
        main_window = MagicMock()
        with patch(
            "controller.controller.EmulatorConfiguration",
            return_value=configuration
        ), patch(
            "controller.controller.SettingsManager",
            return_value=settings_manager
        ), patch(
            "controller.controller.MainWindow",
            return_value=main_window
        ), patch.object(
            Path,
            "exists",
            return_value=False
        ):
            controller = Chip8Controller()
        settings.remove.assert_called_once_with("recent/last_rom")
        self.assertIsNone(controller.current_rom)


    ##########################################################################
    # Cancelling the ROM file dialog
    ##########################################################################
    @patch("controller.controller.QFileDialog.getOpenFileName")
    def test_load_rom_does_nothing_when_file_dialog_is_cancelled( self, get_open_file_name: Mock) -> None:
        controller = create_controller()
        get_open_file_name.return_value = ("", "")
        controller._load_rom = MagicMock()
        controller.load_rom()
        get_open_file_name.assert_called_once_with(
            controller._main_window,
            "Open CHIP-8 ROM",
            "",
            "CHIP-8 ROM (*.ch8 *.rom *.bin);;All files (*)"
        )
        controller._load_rom.assert_not_called()

    ##########################################################################
    # Searching in ROM file
    ##########################################################################
    @patch("controller.controller.QInputDialog.getText")
    def test_search_rom_bytes_returns_when_input_is_cancelled( self, get_text: Mock) -> None:
        controller = create_controller()
        controller._current_rom_data = bytes([0xA2, 0x30])
        get_text.return_value = ("A2", False)
        with patch.object(controller._memory_model, "refresh_range") as refresh_range:
            with patch("controller.controller.QMessageBox.information") as information:
                controller.search_rom_bytes()
        information.assert_not_called()
        refresh_range.assert_not_called()


    @patch("controller.controller.QInputDialog.getText")
    @patch("controller.controller.QMessageBox.warning")
    def test_search_rom_bytes_reports_empty_input( self, warning: Mock, get_text: Mock) -> None:
        controller = create_controller()
        controller._current_rom_data = bytes([0xA2, 0x30])
        get_text.return_value = ("   ", True)
        with patch.object(controller._memory_model, "refresh_range") as refresh_range:
            controller.search_rom_bytes()
        warning.assert_called_once_with(
            controller._main_window,
            "Invalid Byte Sequence",
            "Enter one or more bytes as two hexadecimal digits each, separated by spaces."
        )
        refresh_range.assert_not_called()

    @patch("controller.controller.QInputDialog.getText")
    @patch("controller.controller.QMessageBox.information")
    def test_search_rom_bytes_reports_sequence_not_found( self, information: Mock, get_text: Mock) -> None:
        controller = create_controller()
        controller._current_rom_data = bytes.fromhex("A2 30 00 E0")
        get_text.return_value = ("FF FF", True)
        with patch.object(controller._memory_model, "refresh_range") as refresh_range:
            controller.search_rom_bytes()
        information.assert_called_once_with(
            controller._main_window,
            "Search ROM Bytes",
            "The byte sequence was not found in the loaded ROM."
        )
        refresh_range.assert_not_called()

    @patch("controller.controller.QInputDialog.getText")
    @patch("controller.controller.QInputDialog.getItem")
    def test_search_rom_bytes_returns_when_match_selection_is_cancelled( self, get_item: Mock, get_text: Mock) -> None:
        controller = create_controller()
        controller._current_rom_data = bytes.fromhex("A2 30 00 A2 30")
        get_text.return_value = ("A2 30", True)
        get_item.return_value = ("", False)
        with patch.object(controller._memory_model, "refresh_range") as refresh_range:
            controller.search_rom_bytes()
        get_item.assert_called_once_with(
            controller._main_window,
            "ROM Search Results",
            "Found 2 matches. Select an address:",
            ["0x200", "0x203"],
            0,
            False
        )
        refresh_range.assert_not_called()

    @patch("controller.controller.QInputDialog.getText")
    def test_search_rom_bytes_highlights_single_match( self, get_text: Mock) -> None:
        controller = create_controller()
        controller._current_rom_data = bytes.fromhex("A2 30 00 E0")
        get_text.return_value = ("A2 30", True)
        with patch.object(controller._memory_model, "refresh_range") as refresh_range:
            with patch.object(controller._diagnostics_reporter, "info") as info:
                controller.search_rom_bytes()
        refresh_range.assert_called_once_with(0x200, 0x201)
        info.assert_called_once_with("Found byte sequence at address 0x200.")

    @patch("controller.controller.QInputDialog.getText")
    @patch("controller.controller.QMessageBox.information")
    def test_search_rom_bytes_reports_when_no_rom_is_loaded( self, information: Mock, get_text: Mock) -> None:
        controller = create_controller()
        controller._current_rom_data = None
        controller.search_rom_bytes()
        information.assert_called_once_with(
            controller._main_window,
            "Search ROM Bytes",
            "Load a ROM before searching for bytes."
        )
        get_text.assert_not_called()

    def test_reload_rom_without_rom_path_resets_without_reload_message(self) -> None:
        controller = create_controller()
        controller._current_rom = None
        controller._current_rom_data = bytes.fromhex("00 E0")
        controller._diagnostics.clear()
        with patch.object(controller, "reset") as reset:
            controller.reload_rom()
        reset.assert_called_once_with()
        controller._main_window.show_status_message.assert_not_called()
        messages = [diagnostic.message for diagnostic in controller._diagnostics]
        self.assertFalse( any(message.startswith("Reloaded ROM file") for message in messages))

    @patch("controller.controller.QMessageBox.information")
    @patch("controller.controller.QInputDialog.getText")
    def test_search_rom_bytes_without_loaded_rom( self, get_text: Mock, information: Mock) -> None:
        """Verify byte search requests a ROM to be loaded first."""
        with patch.object(Chip8Controller, "__init__", return_value=None):
            controller = Chip8Controller()
        controller._main_window = MagicMock()
        controller._current_rom_data = None
        controller.search_rom_bytes()
        information.assert_called_once_with(
            controller._main_window,
            "Search ROM Bytes",
            "Load a ROM before searching for bytes."
        )
        get_text.assert_not_called()

    @patch("controller.controller.QMessageBox.warning")
    @patch("controller.controller.QInputDialog.getText", return_value=("G1", True))
    def test_search_rom_bytes_rejects_invalid_byte_sequence( self, get_text: Mock, warning: Mock) -> None:
        """Verify invalid hexadecimal input produces a warning."""
        with patch.object(Chip8Controller, "__init__", return_value=None):
            controller = Chip8Controller()
        controller._main_window = MagicMock()
        controller._current_rom_data = bytes.fromhex("A2 30")
        controller._memory_model = MagicMock()
        controller._diagnostics_reporter = MagicMock()
        controller.search_rom_bytes()
        get_text.assert_called_once()
        warning.assert_called_once_with(
            controller._main_window,
            "Invalid Byte Sequence",
            "Enter one or more bytes as two hexadecimal digits each, separated by spaces."
        )
        controller._memory_model.refresh_range.assert_not_called()
        controller._diagnostics_reporter.info.assert_not_called()

    @patch("controller.controller.QMessageBox.information")
    @patch("controller.controller.find_byte_sequences", return_value=[])
    @patch( "controller.controller.QInputDialog.getText", return_value=("A2 30", True))
    def test_search_rom_bytes_sequence_not_found( self, get_text: Mock, find_sequences: Mock, information: Mock) -> None:
        """Verify a missing byte sequence produces an informational message."""
        with patch.object(Chip8Controller, "__init__", return_value=None):
            controller = Chip8Controller()
        controller._main_window = MagicMock()
        controller._current_rom_data = bytes.fromhex("00 E0 12 00")
        controller._memory_model = MagicMock()
        controller._diagnostics_reporter = MagicMock()
        controller.search_rom_bytes()
        get_text.assert_called_once()
        find_sequences.assert_called_once_with( controller._current_rom_data, bytes.fromhex("A2 30"))
        information.assert_called_once_with(
            controller._main_window,
            "Search ROM Bytes",
            "The byte sequence was not found in the loaded ROM."
        )
        controller._memory_model.refresh_range.assert_not_called()
        controller._diagnostics_reporter.info.assert_not_called()

    @patch("controller.controller.find_byte_sequences", return_value=[2])
    @patch( "controller.controller.QInputDialog.getText", return_value=("A2 30", True))
    def test_search_rom_bytes_single_match( self, get_text: Mock, find_sequences: Mock) -> None:
        """Verify a single match refreshes its memory range and reports its address."""
        with patch.object(Chip8Controller, "__init__", return_value=None):
            controller = Chip8Controller()
        controller._main_window = MagicMock()
        controller._current_rom_data = bytes.fromhex("00 E0 A2 30 12 00")
        controller._memory_model = MagicMock()
        controller._diagnostics_reporter = MagicMock()
        controller.search_rom_bytes()
        get_text.assert_called_once()
        find_sequences.assert_called_once_with(
            controller._current_rom_data,
            bytes.fromhex("A2 30")
        )
        controller._memory_model.refresh_range.assert_called_once_with(
            0x202,
            0x203
        )
        controller._diagnostics_reporter.info.assert_called_once_with(
            "Found byte sequence at address 0x202."
        )

    @patch( "controller.controller.QInputDialog.getItem", return_value=("0x204", True))
    @patch( "controller.controller.QInputDialog.getText", return_value=("A2 30", True))
    @patch("controller.controller.find_byte_sequences", return_value=[2, 4])
    def test_search_rom_bytes_multiple_matches_selects_address( self, find_sequences: Mock, get_text: Mock, get_item: Mock) -> None:
        """Verify selecting a search result refreshes the selected address."""
        with patch.object(Chip8Controller, "__init__", return_value=None):
            controller = Chip8Controller()
        controller._main_window = MagicMock()
        controller._current_rom_data = bytes.fromhex( "00 E0 A2 30 A2 30 12 00")
        controller._memory_model = MagicMock()
        controller._diagnostics_reporter = MagicMock()
        controller.search_rom_bytes()
        find_sequences.assert_called_once_with( controller._current_rom_data, bytes.fromhex("A2 30"))
        get_text.assert_called_once()
        get_item.assert_called_once_with(
            controller._main_window,
            "ROM Search Results",
            "Found 2 matches. Select an address:",
            ["0x202", "0x204"],
            0,
            False
        )
        controller._memory_model.refresh_range.assert_called_once_with( 0x204, 0x205)
        controller._diagnostics_reporter.info.assert_called_once_with( "Found byte sequence at address 0x204.")

    @patch( "controller.controller.QInputDialog.getItem", return_value=("", False))
    @patch( "controller.controller.QInputDialog.getText", return_value=("A2 30", True))
    @patch("controller.controller.find_byte_sequences", return_value=[2, 4])
    def test_search_rom_bytes_multiple_matches_cancelled( self, find_sequences: Mock, get_text: Mock, get_item: Mock) -> None:
        """Verify cancelling match selection leaves the views unchanged."""
        with patch.object(Chip8Controller, "__init__", return_value=None):
            controller = Chip8Controller()
        controller._main_window = MagicMock()
        controller._current_rom_data = bytes.fromhex( "00 E0 A2 30 A2 30 12 00")
        controller._memory_model = MagicMock()
        controller._diagnostics_reporter = MagicMock()
        controller.search_rom_bytes()
        find_sequences.assert_called_once_with( controller._current_rom_data, bytes.fromhex("A2 30"))
        get_text.assert_called_once()
        get_item.assert_called_once()
        controller._memory_model.refresh_range.assert_not_called()
        controller._diagnostics_reporter.info.assert_not_called()

    @patch("controller.controller.find_byte_sequences", return_value=[2])
    @patch( "controller.controller.QInputDialog.getText", return_value=("0xA2 0x30", True))
    def test_search_rom_bytes_accepts_hexadecimal_prefixes( self, get_text: Mock, find_sequences: Mock) -> None:
        """Verify byte search accepts hexadecimal tokens with 0x prefixes."""
        with patch.object(Chip8Controller, "__init__", return_value=None):
            controller = Chip8Controller()
        controller._main_window = MagicMock()
        controller._current_rom_data = bytes.fromhex("00 E0 A2 30 12 00")
        controller._memory_model = MagicMock()
        controller._diagnostics_reporter = MagicMock()
        controller.search_rom_bytes()
        get_text.assert_called_once()
        find_sequences.assert_called_once_with(
            controller._current_rom_data,
            bytes.fromhex("A2 30")
        )
        controller._memory_model.refresh_range.assert_called_once_with(
            0x202,
            0x203
        )
        controller._diagnostics_reporter.info.assert_called_once_with(
            "Found byte sequence at address 0x202."
        )

    @patch("controller.controller.find_byte_sequences")
    @patch( "controller.controller.QInputDialog.getText", return_value=("", False))
    def test_search_rom_bytes_input_cancelled( self, get_text: Mock, find_sequences: Mock) -> None:
        """Verify cancelling byte-sequence input stops the search."""
        with patch.object(Chip8Controller, "__init__", return_value=None):
            controller = Chip8Controller()
        controller._main_window = MagicMock()
        controller._current_rom_data = bytes.fromhex("00 E0 A2 30 12 00")
        controller._memory_model = MagicMock()
        controller._diagnostics_reporter = MagicMock()
        controller.search_rom_bytes()
        get_text.assert_called_once()
        find_sequences.assert_not_called()
        controller._memory_model.refresh_range.assert_not_called()
        controller._diagnostics_reporter.info.assert_not_called()

    @patch("controller.controller.QMessageBox.warning")
    @patch( "controller.controller.QInputDialog.getText", return_value=("   ", True))
    @patch("controller.controller.find_byte_sequences")
    def test_search_rom_bytes_rejects_empty_input( self, find_sequences: Mock, get_text: Mock, warning: Mock) -> None:
        """Verify empty byte-sequence input produces a warning."""
        with patch.object(Chip8Controller, "__init__", return_value=None):
            controller = Chip8Controller()
        controller._main_window = MagicMock()
        controller._current_rom_data = bytes.fromhex("00 E0 A2 30")
        controller._memory_model = MagicMock()
        controller._diagnostics_reporter = MagicMock()
        controller.search_rom_bytes()
        get_text.assert_called_once()
        find_sequences.assert_not_called()
        warning.assert_called_once_with(
            controller._main_window,
            "Invalid Byte Sequence",
            "Enter one or more bytes as two hexadecimal digits each, separated by spaces."
        )
        controller._memory_model.refresh_range.assert_not_called()
        controller._diagnostics_reporter.info.assert_not_called()

    ##########################################################################
    # Keyboard tests
    ##########################################################################
    def test_key_down_and_up_ignore_unmapped_keys(self) -> None:
        """Verify unmapped Qt keys do not affect the CHIP-8 keyboard."""
        controller = create_controller()
        controller._keyboard_map.chip8_key = MagicMock(return_value=None)
        controller._machine.keyboard.press = MagicMock()
        controller._machine.keyboard.release = MagicMock()
        qt_key = -1
        controller.key_down(qt_key)
        controller.key_up(qt_key)
        controller._keyboard_map.chip8_key.assert_has_calls([ call(qt_key), call(qt_key) ])
        controller._machine.keyboard.press.assert_not_called()
        controller._machine.keyboard.release.assert_not_called()

    def test_key_up_releases_mapped_chip8_key(self) -> None:
        """Verify releasing a mapped Qt key releases the corresponding CHIP-8 key."""
        controller = create_controller()
        controller._keyboard_map.chip8_key = MagicMock(return_value=0xA)
        controller._machine.keyboard.release = MagicMock()
        controller.key_up(42)
        controller._keyboard_map.chip8_key.assert_called_once_with(42)
        controller._machine.keyboard.release.assert_called_once_with(0xA)

    def test_key_down_presses_mapped_chip8_key(self) -> None:
        """Verify pressing a mapped Qt key presses the corresponding CHIP-8 key."""
        controller = create_controller()
        controller._keyboard_map.chip8_key = MagicMock(return_value=0xA)
        controller._machine.keyboard.press = MagicMock()
        controller.key_down(42)
        controller._keyboard_map.chip8_key.assert_called_once_with(42)
        controller._machine.keyboard.press.assert_called_once_with(0xA)

    ##########################################################################
    # assembler related tests
    ##########################################################################
    def test_save_assembler_source_reports_write_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source_file = Path(directory) / "test.asm"
            controller = create_controller()
            controller._assembler_source_file = source_file
            with patch.object(
                Path,
                "write_text",
                side_effect=OSError("Test source write error.")
            ):
                result = controller.save_assembler_source("CLS\n")
            self.assertFalse(result)
            messages = [ diagnostic.message for diagnostic in controller._assembler_diagnostics ]
            self.assertEqual(
                messages,
                [
                    "Saving assembly source file 'test.asm'.",
                    "Unable to save assembly source 'test.asm': Test source write error."
                ]
            )

    def test_create_assembler_uses_matching_isa_and_parser(self) -> None:
        """
        @brief Verify that the real assembler factory injects a parser
        configured for the same ISA as the assembler.
        """
        controller = create_controller()
        assembler = controller._create_assembler(Target.COSMAC)
        self.assertIsInstance(assembler._parser, ClassicParser)
        self.assertIs(assembler._parser._isa, assembler._isa)
        result = assembler.assemble("CLS\n", AssemblyOptions())
        self.assertTrue(result.success)
        result = assembler.assemble("PLANE 1\n", AssemblyOptions())
        self.assertFalse(result.success)
        self.assertIn( "Unsupported instruction 'PLANE'.", [diagnostic.message for diagnostic in result.diagnostics])


    def test_create_assembler_supports_superchip_10(self) -> None:
        controller = create_controller()
        assembler = controller._create_assembler(Target.SUPERCHIP_10)
        self.assertIsInstance(assembler._isa, SuperChip10InstructionSetArchitecture)
        self.assertIsInstance(assembler._parser, ClassicParser)
        self.assertIs(assembler._parser._isa, assembler._isa)
        result = assembler.assemble("LOW\n", AssemblyOptions())
        self.assertTrue(result.success)
        self.assertEqual(result.binary_image, bytes.fromhex("00 FE"))


    def test_create_assembler_supports_superchip_11(self) -> None:
        controller = create_controller()
        assembler = controller._create_assembler(Target.SUPERCHIP_11)
        self.assertIsInstance(assembler._isa, SuperChip11InstructionSetArchitecture)
        self.assertIsInstance(assembler._parser, ClassicParser)
        self.assertIs(assembler._parser._isa, assembler._isa)
        result = assembler.assemble("SCD 3\nSCR\nSCL", AssemblyOptions())
        self.assertTrue(result.success)
        self.assertEqual(result.binary_image, bytes.fromhex("00 C3 00 FB 00 FC"))


    def test_create_assembler_supports_superchip_modern(self) -> None:
        controller = create_controller()
        assembler = controller._create_assembler(Target.SUPERCHIP_MODERN)
        self.assertIsInstance(assembler._isa, SuperChipModernInstructionSetArchitecture)
        self.assertIsInstance(assembler._parser, ClassicParser)
        self.assertIs(assembler._parser._isa, assembler._isa)
        result = assembler.assemble("SCD 3\nSCR\nSCL", AssemblyOptions())
        self.assertTrue(result.success, [diagnostic.message for diagnostic in result.diagnostics])
        self.assertEqual(result.binary_image, bytes.fromhex("00 C3 00 FB 00 FC"))


    def test_create_assembler_supports_schipc(self) -> None:
        controller = create_controller()
        assembler = controller._create_assembler(Target.SCHIPC)
        self.assertIsInstance(assembler._isa, SCHIPCInstructionSetArchitecture)
        result = assembler.assemble("JP V0, 0x234\nSCR\n", AssemblyOptions())
        self.assertTrue(result.success, [diagnostic.message for diagnostic in result.diagnostics])
        self.assertEqual(result.binary_image, bytes.fromhex("B234 00FB"))
        result = assembler.assemble("SCD 0\n", AssemblyOptions())
        self.assertFalse(result.success)
        self.assertIsNone(result.binary_image)
        self.assertTrue(
            any(
                "SCHIPC SCD row count must be in the range 1 to 15."
                in diagnostic.message
                for diagnostic in result.diagnostics
            ),
            [diagnostic.message for diagnostic in result.diagnostics]
        )


    def test_schipc_jump_resolves_forward_label(self) -> None:
        controller = create_controller()
        assembler = controller._create_assembler(Target.SCHIPC)
        result = assembler.assemble(
            "JP V0, target\n"
            "SCR\n"
            "target:\n"
            "CLS\n",
            AssemblyOptions()
        )
        self.assertTrue( result.success, [diagnostic.message for diagnostic in result.diagnostics])
        self.assertEqual(result.binary_image, bytes.fromhex("B204 00FB 00E0"))


    def test_schipc_assembler_rejects_jump_using_v1(self) -> None:
        controller = create_controller()
        assembler = controller._create_assembler(Target.SCHIPC)
        result = assembler.assemble("JP V1, 0x234\n", AssemblyOptions())
        self.assertFalse(result.success)
        self.assertTrue(result.diagnostics)


    def test_schipc_assembler_rejects_zero_distance_scroll(self) -> None:
        controller = create_controller()
        assembler = controller._create_assembler(Target.SCHIPC)
        result = assembler.assemble("SCD 0\n", AssemblyOptions())
        self.assertFalse(result.success)
        self.assertTrue(result.diagnostics)


    def test_source_modern_target_overrides_external_cosmac_target(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source_file = Path(directory) / "modern.asm"
            source_file.write_text("", encoding="utf-8")
            rom_file = source_file.with_suffix(".ch8")
            controller = create_controller()
            controller._assembler_source_file = source_file
            controller._assembler_rom_file = rom_file
            result = controller.assemble_source( "TARGET SCHIPMODERN\nSCD 1\n", Target.COSMAC, AssemblyOptions(),)
            self.assertTrue(result)
            self.assertIsInstance( controller._assembler._isa, SuperChipModernInstructionSetArchitecture,)
            self.assertEqual( rom_file.read_bytes(), bytes.fromhex("00 C1"),)

    def test_source_schipc_target_overrides_external_cosmac_target(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source_file = Path(directory) / "schipc.asm"
            source_file.write_text("", encoding="utf-8")
            rom_file = source_file.with_suffix(".ch8")
            controller = create_controller()
            controller._assembler_source_file = source_file
            controller._assembler_rom_file = rom_file
            result = controller.assemble_source( "TARGET SCHIPC\nJP V0, 0x234\nSCR\n", Target.COSMAC, AssemblyOptions())
            self.assertTrue(result)
            self.assertIsInstance( controller._assembler._isa, SCHIPCInstructionSetArchitecture)
            self.assertEqual(rom_file.read_bytes(), bytes.fromhex("B234 00FB"))

    def test_create_emulator_isa_supports_classic_and_superchip_10(self) -> None:
        self.assertIsInstance(
            Chip8Controller._create_emulator_isa(EmulationMode.CLASSIC),
            ClassicInstructionSetArchitecture,
        )
        self.assertIsInstance(
            Chip8Controller._create_emulator_isa(EmulationMode.SUPERCHIP_10),
            SuperChip10InstructionSetArchitecture,
        )

    def test_create_emulator_isa_supports_superchip_11(self) -> None:
        isa = Chip8Controller._create_emulator_isa(EmulationMode.SUPERCHIP_11)
        self.assertIsInstance(isa, SuperChip11InstructionSetArchitecture)

    def test_create_emulator_isa_supports_superchip_modern(self) -> None:
        isa = Chip8Controller._create_emulator_isa(EmulationMode.SUPERCHIP_MODERN)
        self.assertIsInstance(isa, SuperChipModernInstructionSetArchitecture)

    def test_create_emulator_isa_supports_schipc(self) -> None:
        self.assertIsInstance(
            Chip8Controller._create_emulator_isa(EmulationMode.SCHIPC),
            SCHIPCInstructionSetArchitecture,
        )

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

    def _create_exit_test_controller(self, running: bool) -> Chip8Controller:
        """Create a controller with mocked collaborators for EXIT tests."""
        with patch.object(Chip8Controller, "__init__", return_value=None):
            controller = Chip8Controller()
        controller._machine = MagicMock()
        controller._debugger = MagicMock()
        controller._stopped_on_breakpoint = False
        controller._configuration = MagicMock()
        controller._configuration.disable_display_updates = False
        controller._code_analysis = MagicMock()
        controller._code_model = MagicMock()
        controller._main_window = MagicMock()
        controller._diagnostics_reporter = MagicMock()
        controller._logger = MagicMock()
        controller._cpu_timer = MagicMock()
        controller._hardware_timer = MagicMock()
        controller._running = running
        controller._update_display = MagicMock()
        controller.update_gui = MagicMock()
        controller._machine.registers.pc = 0x200
        controller._debugger.temporary_breakpoint = None
        controller._debugger.has_any_breakpoint.return_value = False
        controller._machine.execute_cycle.return_value = StepResult(terminated=True)
        return controller

    def test_exit_stops_continuous_execution(self) -> None:
        """EXIT during a CPU tick stops timers and reports program exit."""
        controller = self._create_exit_test_controller(running=True)
        controller._cpu_tick()
        controller._machine.execute_cycle.assert_called_once_with()
        controller._cpu_timer.stop.assert_called_once_with()
        controller._hardware_timer.stop.assert_called_once_with()
        controller._main_window.show_status_message.assert_any_call("Program exited")
        self.assertFalse(controller._running)


    def test_timer_tick_starts_beeper_and_updates_register_view(self) -> None:
        """Verify that an active sound timer starts the beeper and refreshes registers."""
        with patch.object(Chip8Controller, "__init__", return_value=None):
            controller = Chip8Controller()
        controller._machine = MagicMock()
        controller._machine.timers.sound_timer = 1
        controller._beeper = MagicMock()
        controller._logger = MagicMock()
        controller._configuration = MagicMock()
        controller._configuration.disable_display_updates = False
        controller._update_register_view = MagicMock()
        controller._timer_tick()
        controller._machine.tick_timers.assert_called_once_with()
        controller._beeper.start.assert_called_once_with()
        controller._beeper.stop.assert_not_called()
        controller._logger.info.assert_called_once_with("Beeper On")
        controller._update_register_view.assert_called_once_with()


    def test_timer_tick_stops_beeper_when_sound_timer_is_zero_and_skips_register_update(self) -> None:
        """Verify that an inactive sound timer stops the beeper and skips register updates when disabled."""
        with patch.object(Chip8Controller, "__init__", return_value=None):
            controller = Chip8Controller()
        controller._machine = MagicMock()
        controller._machine.timers.sound_timer = 0
        controller._beeper = MagicMock()
        controller._logger = MagicMock()
        controller._configuration = MagicMock()
        controller._configuration.disable_display_updates = True
        controller._update_register_view = MagicMock()
        controller._timer_tick()
        controller._machine.tick_timers.assert_called_once_with()
        controller._beeper.stop.assert_called_once_with()
        controller._beeper.start.assert_not_called()
        controller._logger.info.assert_called_once_with("Beeper Off")
        controller._update_register_view.assert_not_called()


    def test_timer_tick_stops_beeper_and_updates_register_view(self) -> None:
        """Verify that an inactive sound timer stops the beeper and refreshes registers."""
        with patch.object(Chip8Controller, "__init__", return_value=None):
            controller = Chip8Controller()
        controller._machine = MagicMock()
        controller._machine.timers.sound_timer = 0
        controller._beeper = MagicMock()
        controller._logger = MagicMock()
        controller._configuration = MagicMock()
        controller._configuration.disable_display_updates = False
        controller._update_register_view = MagicMock()
        controller._timer_tick()
        controller._machine.tick_timers.assert_called_once_with()
        controller._beeper.stop.assert_called_once_with()
        controller._beeper.start.assert_not_called()
        controller._logger.info.assert_called_once_with("Beeper Off")
        controller._update_register_view.assert_called_once_with()

    def test_test_sound_delegates_to_beeper(self) -> None:
        """Verify the sound test configuration is passed to the beeper."""
        controller = create_controller()
        configuration = MagicMock()
        controller._beeper.test = MagicMock()
        controller._test_sound(configuration)
        controller._beeper.test.assert_called_once_with(configuration)

    def test_exit_during_single_step_reports_program_exit(self) -> None:
        """Single-stepping EXIT reports termination without starting timers."""
        controller = self._create_exit_test_controller(running=False)
        controller.step()
        controller._machine.execute_cycle.assert_called_once_with()
        controller._main_window.show_status_message.assert_called_once_with("Program exited")
        controller._cpu_timer.stop.assert_not_called()
        controller._hardware_timer.stop.assert_not_called()
        self.assertFalse(controller._running)

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
        controller._update_code_view = MagicMock()
        controller._machine.registers.pc = 0x200
        controller._debugger.temporary_breakpoint = None
        controller._debugger.has_any_breakpoint.return_value = False
        result = StepResult( bnnn_target=(0x200, 0x234))
        controller._machine.execute_cycle.return_value = result
        controller._code_analysis.analyze_observed_bnnn_target.return_value = True
        controller._execute_cycle()
        controller._code_analysis.analyze_observed_bnnn_target.assert_called_once_with( 0x200, 0x234,)
        controller.update_gui.assert_called_once_with(result)
        controller._code_model.refresh.assert_called_once_with()
        controller._update_code_view.assert_called_once_with()


    def test_execute_cycle_handles_not_implemented_instruction(self) -> None:
        """Verify that an unsupported instruction stops execution and reports a diagnostic."""
        with patch.object(Chip8Controller, "__init__", return_value=None):
            controller = Chip8Controller()
        controller._machine = MagicMock()
        controller._debugger = MagicMock()
        controller._stopped_on_breakpoint = False
        controller._configuration = MagicMock()
        controller._configuration.disable_display_updates = False
        controller._code_analysis = MagicMock()
        controller._code_model = MagicMock()
        controller._diagnostics_reporter = MagicMock()
        controller._logger = MagicMock()
        controller.update_gui = MagicMock()
        controller.stop = MagicMock()
        controller._machine.registers.pc = 0x202
        controller._debugger.temporary_breakpoint = None
        controller._debugger.has_any_breakpoint.return_value = False
        controller._machine.execute_cycle.side_effect = NotImplementedError
        controller._execute_cycle()
        controller.stop.assert_called_once_with()
        controller._diagnostics_reporter.error.assert_called_once_with( "Instruction @0x0200 Not implemented!")
        controller.update_gui.assert_called_once_with()
        controller._machine.execute_cycle.assert_called_once_with()


    def test_execute_cycle_handles_temporary_breakpoint(self) -> None:
        """Verify that hitting a temporary breakpoint refreshes and selects the current address."""
        with patch.object(Chip8Controller, "__init__", return_value=None):
            controller = Chip8Controller()
        controller._machine = MagicMock()
        controller._debugger = MagicMock()
        controller._stopped_on_breakpoint = False
        controller._code_model = MagicMock()
        controller._main_window = MagicMock()
        controller.stop = MagicMock()
        controller.update_gui = MagicMock()
        controller._machine.registers.pc = 0x234
        controller._debugger.temporary_breakpoint = 0x234
        controller._debugger.has_any_breakpoint.return_value = True
        controller._execute_cycle()
        controller.stop.assert_called_once_with()
        self.assertTrue(controller._stopped_on_breakpoint)
        controller._code_model.refresh_address.assert_called_once_with(0x234)
        controller._main_window.clear_code_selection.assert_called_once_with()
        controller._machine.execute_cycle.assert_not_called()
        controller.update_gui.assert_not_called()


    def test_execute_cycle_handles_ordinary_breakpoint(self) -> None:
        """Verify that an ordinary breakpoint stops execution without temporary-breakpoint actions."""
        with patch.object(Chip8Controller, "__init__", return_value=None):
            controller = Chip8Controller()
        controller._machine = MagicMock()
        controller._debugger = MagicMock()
        controller._stopped_on_breakpoint = False
        controller._code_model = MagicMock()
        controller._main_window = MagicMock()
        controller.stop = MagicMock()
        controller.update_gui = MagicMock()
        controller._machine.registers.pc = 0x234
        controller._debugger.temporary_breakpoint = None
        controller._debugger.has_any_breakpoint.return_value = True
        controller._execute_cycle()
        controller.stop.assert_called_once_with()
        self.assertTrue(controller._stopped_on_breakpoint)
        controller._code_model.refresh_address.assert_not_called()
        controller._main_window.clear_code_selection.assert_not_called()
        controller._machine.execute_cycle.assert_not_called()
        controller.update_gui.assert_not_called()


    def test_execute_cycle_resumes_when_already_stopped_on_breakpoint(self) -> None:
        """Verify that execution resumes when the current breakpoint has already been handled."""
        with patch.object(Chip8Controller, "__init__", return_value=None):
            controller = Chip8Controller()
        controller.stop = MagicMock()
        controller._machine = MagicMock()
        controller._debugger = MagicMock()
        controller._stopped_on_breakpoint = True
        controller._configuration = MagicMock()
        controller._configuration.disable_display_updates = False
        controller._code_analysis = MagicMock()
        controller._code_model = MagicMock()
        controller.update_gui = MagicMock()
        controller._machine.registers.pc = 0x234
        controller._debugger.temporary_breakpoint = None
        controller._debugger.has_any_breakpoint.return_value = True
        result = StepResult()
        controller._machine.execute_cycle.return_value = result
        controller._execute_cycle()
        controller._machine.execute_cycle.assert_called_once_with()
        controller.update_gui.assert_called_once_with(result)
        self.assertFalse(controller._stopped_on_breakpoint)
        controller.stop.assert_not_called()
        controller._code_model.refresh_address.assert_not_called()
        controller._debugger.has_any_breakpoint.assert_called_once_with(0x234)


    def test_cpu_tick_executes_one_cycle(self) -> None:
        """Verify that each CPU timer tick delegates to one execution cycle."""
        with patch.object(Chip8Controller, "__init__", return_value=None):
            controller = Chip8Controller()
        controller._execute_cycle = MagicMock()
        controller._cpu_tick()
        controller._execute_cycle.assert_called_once_with()


    def test_update_gui_refreshes_single_memory_address(self) -> None:
        """Verify that a single-address memory range refreshes only that address."""
        with patch.object(Chip8Controller, "__init__", return_value=None):
            controller = Chip8Controller()
        controller._update_diagnostics_view = MagicMock()
        controller._configuration = MagicMock()
        controller._configuration.disable_display_updates = False
        controller._memory_model = MagicMock()
        controller._update_register_view = MagicMock()
        controller._update_code_view = MagicMock()
        address = 0x234
        result = StepResult(memory_range=(address, address))
        controller.update_gui(result)
        controller._update_diagnostics_view.assert_called_once_with()
        controller._memory_model.refresh_address.assert_called_once_with(address)
        controller._memory_model.refresh_range.assert_not_called()
        controller._update_register_view.assert_called_once_with()
        controller._update_code_view.assert_called_once_with()

    def test_update_gui_updates_changed_display_when_view_updates_disabled(self) -> None:
        """Verify display changes are applied before other view updates are skipped."""
        with patch.object(Chip8Controller, "__init__", return_value=None):
            controller = Chip8Controller()
        controller._update_diagnostics_view = MagicMock()
        controller._update_display = MagicMock()
        controller._configuration = MagicMock()
        controller._configuration.disable_display_updates = True
        controller._memory_model = MagicMock()
        controller._update_register_view = MagicMock()
        controller._update_code_view = MagicMock()
        result = StepResult(display_changed=True)
        controller.update_gui(result)
        controller._update_diagnostics_view.assert_called_once_with()
        controller._update_display.assert_called_once_with()
        controller._memory_model.refresh_address.assert_not_called()
        controller._memory_model.refresh_range.assert_not_called()
        controller._update_register_view.assert_not_called()
        controller._update_code_view.assert_not_called()

    def test_update_gui_refreshes_memory_range(self) -> None:
        """Verify that a multi-address memory range refreshes the entire range."""
        with patch.object(Chip8Controller, "__init__", return_value=None):
            controller = Chip8Controller()
        controller._update_diagnostics_view = MagicMock()
        controller._configuration = MagicMock()
        controller._configuration.disable_display_updates = False
        controller._memory_model = MagicMock()
        controller._update_register_view = MagicMock()
        controller._update_code_view = MagicMock()
        first = 0x234
        last = 0x23A
        result = StepResult(memory_range=(first, last))
        controller.update_gui(result)
        controller._memory_model.refresh_range.assert_called_once_with(first, last)
        controller._memory_model.refresh_address.assert_not_called()
        controller._update_register_view.assert_called_once_with()
        controller._update_code_view.assert_called_once_with()


    def test_update_gui_without_result_refreshes_general_views(self) -> None:
        """Verify GUI updates without an execution result skip result-specific work."""
        with patch.object(Chip8Controller, "__init__", return_value=None):
            controller = Chip8Controller()
        controller._update_diagnostics_view = MagicMock()
        controller._update_display = MagicMock()
        controller._configuration = MagicMock()
        controller._configuration.disable_display_updates = False
        controller._memory_model = MagicMock()
        controller._update_register_view = MagicMock()
        controller._update_code_view = MagicMock()
        controller.update_gui()
        controller._update_diagnostics_view.assert_called_once_with()
        controller._update_display.assert_not_called()
        controller._memory_model.refresh_address.assert_not_called()
        controller._memory_model.refresh_range.assert_not_called()
        controller._update_register_view.assert_called_once_with()
        controller._update_code_view.assert_called_once_with()


    def test_update_gui_without_display_or_memory_changes(self) -> None:
        """Verify unchanged display and memory skip specific refreshes."""
        with patch.object(Chip8Controller, "__init__", return_value=None):
            controller = Chip8Controller()
        controller._update_diagnostics_view = MagicMock()
        controller._update_display = MagicMock()
        controller._configuration = MagicMock()
        controller._configuration.disable_display_updates = False
        controller._memory_model = MagicMock()
        controller._update_register_view = MagicMock()
        controller._update_code_view = MagicMock()
        result = StepResult()
        controller.update_gui(result)
        controller._update_diagnostics_view.assert_called_once_with()
        controller._update_display.assert_not_called()
        controller._memory_model.refresh_address.assert_not_called()
        controller._memory_model.refresh_range.assert_not_called()
        controller._update_register_view.assert_called_once_with()
        controller._update_code_view.assert_called_once_with()


    def test_update_gui_updates_display_and_other_views_when_enabled(self) -> None:
        """Verify display and other views refresh when display updates are enabled."""
        with patch.object(Chip8Controller, "__init__", return_value=None):
            controller = Chip8Controller()
        controller._update_diagnostics_view = MagicMock()
        controller._update_display = MagicMock()
        controller._configuration = MagicMock()
        controller._configuration.disable_display_updates = False
        controller._memory_model = MagicMock()
        controller._update_register_view = MagicMock()
        controller._update_code_view = MagicMock()
        result = StepResult(display_changed=True)
        controller.update_gui(result)
        controller._update_diagnostics_view.assert_called_once_with()
        controller._update_display.assert_called_once_with()
        controller._memory_model.refresh_address.assert_not_called()
        controller._memory_model.refresh_range.assert_not_called()
        controller._update_register_view.assert_called_once_with()
        controller._update_code_view.assert_called_once_with()


    def test_update_gui_updates_display_and_single_memory_address(self) -> None:
        """Verify display and single-address memory updates are both applied."""
        with patch.object(Chip8Controller, "__init__", return_value=None):
            controller = Chip8Controller()
        controller._update_diagnostics_view = MagicMock()
        controller._update_display = MagicMock()
        controller._configuration = MagicMock()
        controller._configuration.disable_display_updates = False
        controller._memory_model = MagicMock()
        controller._update_register_view = MagicMock()
        controller._update_code_view = MagicMock()
        address = 0x234
        result = StepResult( display_changed=True, memory_range=(address, address))
        controller.update_gui(result)
        controller._update_diagnostics_view.assert_called_once_with()
        controller._update_display.assert_called_once_with()
        controller._memory_model.refresh_address.assert_called_once_with(address)
        controller._memory_model.refresh_range.assert_not_called()
        controller._update_register_view.assert_called_once_with()
        controller._update_code_view.assert_called_once_with()

    def test_update_code_view_does_not_scroll_when_pc_has_no_row(self) -> None:
        """Verify the code view does not scroll when the PC has no matching row."""
        controller = create_controller()
        pc = controller._machine.registers.pc
        controller._code_model.set_current_pc = MagicMock()
        controller._code_analysis.find_row = MagicMock(return_value=None)
        controller._main_window.scroll_code_to_row = MagicMock()
        controller._update_code_view()
        controller._code_model.set_current_pc.assert_called_once_with(pc)
        controller._code_analysis.find_row.assert_called_once_with(pc)
        controller._main_window.scroll_code_to_row.assert_not_called()

    ##########################################################################
    # save setting
    ##########################################################################
    def test_save_settings_delegates_to_all_settings_components(self) -> None:
        controller = create_controller()
        settings = controller._settings_manager.settings.return_value
        with patch.object(controller._keyboard_map, "write_settings") as write_keyboard_settings:
            with patch.object(controller._debugger, "write_settings") as write_debugger_settings:
                controller.save_settings()
        controller._main_window.save_settings.assert_called_once_with()
        controller._settings_manager.save_configuration.assert_called_once_with( controller._configuration)
        write_keyboard_settings.assert_called_once_with(settings)
        write_debugger_settings.assert_called_once_with(settings)

    @patch("controller.controller.KeyboardDialog")
    def test_configure_keyboard_opens_dialog(self, dialog_class: MagicMock) -> None:
        """Verify keyboard configuration opens and executes the dialog."""
        controller = create_controller()
        dialog = dialog_class.return_value
        controller.configure_keyboard()
        dialog_class.assert_called_once_with(controller._keyboard_map)
        dialog.exec.assert_called_once_with()

    def test_assembler_file_defaults(self) -> None:
        configuration = EmulatorConfiguration()
        self.assertEqual(configuration.assembler_source_file, "")
        self.assertEqual(configuration.assembler_rom_file, "")
        self.assertEqual(configuration.assembler_listing_file, "")

    def test_superchip_11_emulation_mode_settings_round_trip(self) -> None:
        settings = QSettings( QSettings.Format.IniFormat, QSettings.Scope.UserScope, "CHIP8-test", "configuration-test")
        settings.clear()
        configuration = EmulatorConfiguration()
        configuration.emulation_mode = EmulationMode.SUPERCHIP_11

        configuration.write_settings(settings)

        restored = EmulatorConfiguration()
        restored.read_settings(settings)

        self.assertIs(restored.emulation_mode, EmulationMode.SUPERCHIP_11)
        settings.clear()


    def test_superchip_modern_emulation_mode_settings_round_trip(self) -> None:
        settings = QSettings( QSettings.Format.IniFormat, QSettings.Scope.UserScope, "CHIP8-test", "configuration-test")
        settings.clear()
        configuration = EmulatorConfiguration()
        configuration.emulation_mode = EmulationMode.SUPERCHIP_MODERN

        configuration.write_settings(settings)

        restored = EmulatorConfiguration()
        restored.read_settings(settings)

        self.assertIs(restored.emulation_mode, EmulationMode.SUPERCHIP_MODERN)
        settings.clear()


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


    def test_assembler_file_paths_are_not_loaded_as_current_associations(self) -> None:
        """
        @brief Verify that remembered assembler file paths are not treated as
        the current document associations.
        """
        configuration = EmulatorConfiguration()
        configuration.assembler_source_file = "/tmp/test.asm"
        configuration.assembler_rom_file = "/tmp/test.ch8"
        configuration.assembler_listing_file = "/tmp/test.lst"
        controller = create_controller(configuration)
        self.assertEqual(configuration.assembler_source_file, "/tmp/test.asm")
        self.assertEqual(configuration.assembler_rom_file, "/tmp/test.ch8")
        self.assertEqual(configuration.assembler_listing_file, "/tmp/test.lst")
        self.assertIsNone(controller.assembler_source_file)
        self.assertIsNone(controller.assembler_rom_file)
        self.assertIsNone(controller.assembler_listing_file)


    def test_assembler_file_paths_are_not_loaded_from_configuration(self) -> None:
        """
        @brief Verify that remembered assembler file paths are not treated as
        the current assembler file associations.
        """
        configuration = EmulatorConfiguration()
        configuration.assembler_source_file = "/tmp/test.asm"
        configuration.assembler_rom_file = "/tmp/test.ch8"
        configuration.assembler_listing_file = "/tmp/test.lst"
        controller = create_controller(configuration)
        self.assertEqual( configuration.assembler_source_file, "/tmp/test.asm")
        self.assertEqual( configuration.assembler_rom_file, "/tmp/test.ch8")
        self.assertEqual( configuration.assembler_listing_file, "/tmp/test.lst")
        self.assertIsNone(controller.assembler_source_file)
        self.assertIsNone(controller.assembler_rom_file)
        self.assertIsNone(controller.assembler_listing_file)


    @patch("controller.controller.QFileDialog.getSaveFileName")
    def test_assemble_source_does_not_use_remembered_source_file( self, get_save_file_name: Mock) -> None:
        """
        @brief Verify that assembly does not overwrite a source file that is
        only remembered in the configuration.
        """
        with tempfile.TemporaryDirectory() as directory:
            old_source = Path(directory) / "old.asm"
            new_source = Path(directory) / "new.asm"
            old_rom = Path(directory) / "old.ch8"
            old_listing = Path(directory) / "old.lst"
            old_source.write_text("RET\n", encoding="utf-8")
            old_rom.write_bytes(bytes([0xAA, 0x55]))
            old_listing.write_text("old listing\n", encoding="utf-8")
            get_save_file_name.return_value = (str(new_source), "")
            configuration = EmulatorConfiguration()
            configuration.assembler_source_file = str(old_source)
            configuration.assembler_rom_file = str(old_rom)
            configuration.assembler_listing_file = str(old_listing)
            controller = create_controller(configuration)
            controller._assembler = MagicMock()
            controller._assembler.assemble.return_value = AssemblyResult( success=True, binary_image=bytes([0x00, 0xE0]))
            result = controller.assemble_source( "CLS\n", Target.COSMAC, AssemblyOptions())
            self.assertTrue(result)
            self.assertEqual( old_source.read_text(encoding="utf-8"), "RET\n")
            self.assertEqual(old_rom.read_bytes(), bytes([0xAA, 0x55]))
            self.assertEqual( old_listing.read_text(encoding="utf-8"), "old listing\n")
            self.assertEqual( new_source.read_text(encoding="utf-8"), "CLS\n")
            self.assertEqual( new_source.with_suffix(".ch8").read_bytes(), bytes([0x00, 0xE0]))
            self.assertEqual(controller.assembler_source_file, new_source)
            self.assertEqual( controller.assembler_rom_file, new_source.with_suffix(".ch8"))
            self.assertEqual( controller.assembler_listing_file, new_source.with_suffix(".lst"))


    def test_assemble_source_saves_binary_rom(self) -> None:
        """
        @brief Verify that a successful assembly writes the binary ROM.
        """
        with tempfile.TemporaryDirectory() as directory:
            source_file = Path(directory) / "test.asm"
            rom_file = Path(directory) / "test.ch8"
            controller = create_controller()
            controller._assembler_source_file = source_file
            controller._assembler_rom_file = rom_file
            controller._assembler = MagicMock()
            controller._assembler.assemble.return_value = AssemblyResult( success=True, binary_image=bytes([0x00, 0xE0]))
            result = controller.assemble_source( "CLS\n", Target.COSMAC, AssemblyOptions())
            self.assertTrue(result)
            self.assertEqual( rom_file.read_bytes(), bytes([0x00, 0xE0]))


    def test_assemble_source_fails_when_rom_output_path_is_missing(self) -> None:
        """Verify that binary output requires a configured ROM path."""
        controller = create_controller()
        controller.ensure_assembler_source_file = MagicMock(return_value=True)
        controller._assembler_rom_file = None
        controller._assembler_listing_file = None
        controller._assembler = MagicMock()
        controller._assembler.assemble.return_value = AssemblyResult(
            success=True,
            binary_image=bytes([0x00, 0xE0])
        )
        result = controller.assemble_source(
            "CLS\n",
            Target.COSMAC,
            AssemblyOptions()
        )
        self.assertFalse(result)


    def test_assemble_source_does_not_save_rom_when_assembly_fails(self) -> None:
        """
        @brief Verify that a failed assembly does not write a ROM.
        """
        with tempfile.TemporaryDirectory() as directory:
            rom_file = Path(directory) / "test.ch8"
            rom_file.write_bytes(bytes([0xAA, 0x55]))
            source_file = Path(directory) / "test.asm"
            listing_file = Path(directory) / "test.lst"
            controller = create_controller()
            controller._assembler_source_file = source_file
            controller._assembler_rom_file = rom_file
            controller._assembler_listing_file = listing_file
            controller._assembler = MagicMock()
            controller._assembler.assemble.return_value = AssemblyResult( success=False)
            result = controller.assemble_source( "INVALID\n", Target.COSMAC, AssemblyOptions())
            self.assertFalse(result)
            self.assertEqual( rom_file.read_bytes(), bytes([0xAA, 0x55]))

    def test_assemble_source_returns_false_when_source_file_cannot_be_prepared(self) -> None:
        """Verify assembly stops when the source file cannot be prepared."""
        controller = create_controller()
        controller.ensure_assembler_source_file = MagicMock(return_value=False)
        controller._target_selector.select = MagicMock()
        controller._create_assembler = MagicMock()
        result = controller.assemble_source( "CLS", Target.COSMAC, AssemblyOptions())
        self.assertFalse(result)
        controller.ensure_assembler_source_file.assert_called_once_with("CLS")
        controller._target_selector.select.assert_not_called()
        controller._create_assembler.assert_not_called()

    def test_assemble_source_reports_unsupported_assembler_target(self) -> None:
        """Verify an unsupported assembler target is reported as a diagnostic."""
        controller = create_controller()
        controller.ensure_assembler_source_file = MagicMock(return_value=True)
        controller._target_selector.select = MagicMock( return_value=TargetSelection(Target.COSMAC, False))
        controller._create_assembler = MagicMock( side_effect=TargetSelectionError("Unsupported target architecture"))
        result = controller.assemble_source("CLS\n", Target.COSMAC, AssemblyOptions())
        self.assertFalse(result)
        controller._create_assembler.assert_called_once_with(Target.COSMAC)
        self.assertTrue(
            any(
                diagnostic.message == "Unsupported target architecture"
                for diagnostic in controller._assembler_diagnostics
            )
        )


    def test_assemble_source_fails_when_listing_output_path_is_missing(self) -> None:
        """Verify that listing output requires a configured listing path."""
        controller = create_controller()
        controller.ensure_assembler_source_file = MagicMock(return_value=True)
        controller._assembler_listing_file = None
        assembler = MagicMock()
        assembler.assemble.return_value = AssemblyResult( success=True, listing="0000 00E0 CLS\n")
        controller._create_assembler = MagicMock(return_value=assembler)
        result = controller.assemble_source( "CLS\n", Target.COSMAC, AssemblyOptions())
        self.assertFalse(result)


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
            controller._assembler_diagnostics = AssemblerDiagnostics()
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
            controller = create_controller()
            result = controller.save_assembler_source("CLS\n")
            self.assertTrue(result)
            self.assertEqual(controller.assembler_source_file, source_file)
            self.assertEqual( controller.assembler_rom_file, source_file.with_suffix(".ch8"))
            self.assertEqual( controller.assembler_listing_file, source_file.with_suffix(".lst"))


    @patch("controller.controller.QFileDialog.getSaveFileName")
    def test_save_assembler_source_preserves_existing_output_files( self, get_save_file_name: Mock) -> None:
        """Verify saving a new source file preserves configured output paths."""
        with tempfile.TemporaryDirectory() as directory:
            source_file = Path(directory) / "test.asm"
            rom_file = Path(directory) / "custom.ch8"
            listing_file = Path(directory) / "custom.lst"
            get_save_file_name.return_value = (str(source_file), "")
            controller = create_controller()
            controller._assembler_rom_file = rom_file
            controller._assembler_listing_file = listing_file
            result = controller.save_assembler_source("CLS\n")
            self.assertTrue(result)
            self.assertEqual(controller.assembler_source_file, source_file)
            self.assertEqual(controller.assembler_rom_file, rom_file)
            self.assertEqual(controller.assembler_listing_file, listing_file)
            self.assertEqual(source_file.read_text(encoding="utf-8"), "CLS\n")


    def test_show_main_window_restores_settings_before_showing(self) -> None:
        controller = create_controller()
        calls: list[str] = []
        controller._main_window.restore_settings.side_effect = lambda: calls.append("restore")
        controller._main_window.show.side_effect = lambda: calls.append("show")
        controller.show_main_window()
        self.assertEqual(calls, ["restore", "show"])
        controller._main_window.restore_settings.assert_called_once_with()
        controller._main_window.show.assert_called_once_with()

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


    @patch("controller.controller.QFileDialog.getSaveFileName")
    def test_assemble_source_does_not_overwrite_remembered_source_file( self, get_save_file_name: Mock) -> None:
        """
        @brief Verify that assembly does not overwrite a source file that is
        only remembered in the configuration.
        """
        with tempfile.TemporaryDirectory() as directory:
            old_source = Path(directory) / "old.asm"
            new_source = Path(directory) / "new.asm"
            old_source.write_text("RET\n", encoding="utf-8")
            get_save_file_name.return_value = (str(new_source), "")
            configuration = EmulatorConfiguration()
            configuration.assembler_source_file = str(old_source)
            controller = create_controller(configuration)
            controller._assembler = MagicMock()
            controller._assembler.assemble.return_value = AssemblyResult( success=True, binary_image=bytes([0x00, 0xE0]))
            result = controller.assemble_source( "CLS\n", Target.COSMAC, AssemblyOptions())
            self.assertTrue(result)
            self.assertEqual( old_source.read_text(encoding="utf-8"), "RET\n")
            self.assertEqual( new_source.read_text(encoding="utf-8"), "CLS\n")
            self.assertEqual(controller.assembler_source_file, new_source)
            self.assertEqual( controller.assembler_rom_file, new_source.with_suffix(".ch8"))
            self.assertEqual( controller.assembler_listing_file, new_source.with_suffix(".lst"))

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
    def test_load_assembler_source_updates_output_files_for_new_source( self, get_open_file_name: Mock) -> None:
        """
        @brief Verify that loading a new source file updates the assembler
        output filenames to match the new source.
        """
        with tempfile.TemporaryDirectory() as directory:
            first_source = Path(directory) / "first.asm"
            second_source = Path(directory) / "second.asm"
            first_source.write_text("CLS\n", encoding="utf-8")
            second_source.write_text("RET\n", encoding="utf-8")

            configuration = EmulatorConfiguration()
            configuration.assembler_rom_file = None
            configuration.assembler_listing_file = None
            controller = create_controller(configuration)

            get_open_file_name.return_value = (str(first_source), "")
            first_result = controller.load_assembler_source()

            self.assertEqual(first_result, "CLS\n")
            self.assertEqual(controller.assembler_source_file, first_source)
            self.assertEqual(controller.assembler_rom_file, first_source.with_suffix(".ch8"))
            self.assertEqual(controller.assembler_listing_file, first_source.with_suffix(".lst"))

            get_open_file_name.return_value = (str(second_source), "")
            second_result = controller.load_assembler_source()

            self.assertEqual(second_result, "RET\n")
            self.assertEqual(controller.assembler_source_file, second_source)
            self.assertEqual(controller.assembler_rom_file, second_source.with_suffix(".ch8"))
            self.assertEqual(controller.assembler_listing_file, second_source.with_suffix(".lst"))
            self.assertNotEqual(controller.assembler_rom_file, first_source.with_suffix(".ch8"))
            self.assertNotEqual(controller.assembler_listing_file, first_source.with_suffix(".lst"))
            self.assertEqual(
                configuration.assembler_rom_file,
                str(second_source.with_suffix(".ch8"))
            )
            self.assertEqual(
                configuration.assembler_listing_file,
                str(second_source.with_suffix(".lst"))
            )


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
        @brief Verify that previous assembler diagnostics are cleared before
        starting a new assembly.
        """
        with tempfile.TemporaryDirectory() as directory:
            source_file = Path(directory) / "test.asm"
            rom_file = Path(directory) / "test.ch8"
            configuration = EmulatorConfiguration()
            configuration.assembler_source_file = str(source_file)
            configuration.assembler_rom_file = str(rom_file)
            controller = create_controller(configuration)
            controller._assembler_source_file = source_file
            controller._assembler_rom_file = rom_file
            controller._assembler_diagnostics.reporter().error( "Old diagnostic.")
            self.assertEqual( len(controller._assembler_diagnostics._diagnostics), 1)
            assembler = MagicMock()
            assembler.assemble.return_value = AssemblyResult( success=True, binary_image=bytes([0x00, 0xE0]))
            controller._create_assembler = MagicMock(return_value=assembler)
            result = controller.assemble_source(
                "CLS\n",
                Target.COSMAC,
                AssemblyOptions()
            )
            self.assertTrue(result)
            self.assertNotIn( "Old diagnostic.", [ diagnostic.message for diagnostic in controller._assembler_diagnostics ])


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
            self.assertEqual( controller.assembler_source_file, source_file)
            self.assertEqual( controller.assembler_rom_file, source_file.with_suffix(".ch8"))
            self.assertEqual( controller.assembler_listing_file, source_file.with_suffix(".lst"))

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
            self.assertEqual( source_file.read_text(encoding="utf-8"), "CLS\n")

    @patch("controller.controller.QFileDialog.getSaveFileName")
    def test_save_assembler_source_as_reports_write_error( self, get_save_file_name: Mock) -> None:
        with tempfile.TemporaryDirectory() as directory:
            original_source_file = Path(directory) / "original.asm"
            selected_source_file = Path(directory) / "new_source.asm"
            controller = create_controller()
            controller._assembler_source_file = original_source_file
            controller._assembler_rom_file = original_source_file.with_suffix(".ch8")
            controller._assembler_listing_file = original_source_file.with_suffix(".lst")
            get_save_file_name.return_value = (str(selected_source_file), "")
            with patch.object( Path, "write_text", side_effect=OSError("Test source write error.")):
                result = controller.save_assembler_source_as("CLS\n")
            self.assertFalse(result)
            self.assertEqual(controller.assembler_source_file, original_source_file)
            self.assertEqual(controller.assembler_rom_file, original_source_file.with_suffix(".ch8"))
            self.assertEqual(controller.assembler_listing_file, original_source_file.with_suffix(".lst"))
            messages = [ diagnostic.message for diagnostic in controller._assembler_diagnostics ]
            self.assertEqual(
                messages,
                [
                    "Saving assembly source file 'new_source.asm'.",
                    "Unable to save assembly source 'new_source.asm': Test source write error."
                ]
            )

    def test_assemble_source_saves_listing(self) -> None:
        """
        @brief Verify that a generated listing is saved.
        """
        with tempfile.TemporaryDirectory() as directory:
            source_file = Path(directory) / "test.asm"
            rom_file = Path(directory) / "test.ch8"
            listing_file = Path(directory) / "test.lst"
            configuration = EmulatorConfiguration()
            configuration.assembler_rom_file = str(rom_file)
            configuration.assembler_listing_file = str(listing_file)
            controller = create_controller(configuration)
            controller._assembler_source_file = source_file
            controller._assembler_rom_file = rom_file
            controller._assembler_listing_file = listing_file
            assembler = MagicMock()
            assembler.assemble.return_value = AssemblyResult(
                success=True,
                binary_image=bytes([0x00, 0xE0]),
                listing="0000 00E0 CLS\n"
            )
            controller._create_assembler = MagicMock( return_value=assembler)
            result = controller.assemble_source( "CLS\n", Target.COSMAC, AssemblyOptions(generate_listing=True))
            self.assertTrue(result)
            self.assertEqual( listing_file.read_text(encoding="utf-8"), "0000 00E0 CLS\n")

    def test_assemble_source_does_not_save_listing_when_not_generated(self) -> None:
        """
        @brief Verify that assembly without a listing does not modify an
        existing listing file.
        """
        with tempfile.TemporaryDirectory() as directory:
            source_file = Path(directory) / "test.asm"
            rom_file = Path(directory) / "test.ch8"
            listing_file = Path(directory) / "test.lst"
            listing_file.write_text( "old listing\n", encoding="utf-8")
#            configuration = EmulatorConfiguration()
#            configuration.assembler_source_file = str(source_file)
#            configuration.assembler_rom_file = str(rom_file)
#            configuration.assembler_listing_file = str(listing_file)
            controller = create_controller()
            controller._assembler_source_file = source_file
            controller._assembler_rom_file = rom_file
            controller._assembler_listing_file = listing_file
            controller._assembler = MagicMock()
            controller._assembler.assemble.return_value = AssemblyResult( success=True, binary_image=bytes([0x00, 0xE0]))
            result = controller.assemble_source( "CLS\n", Target.COSMAC, AssemblyOptions())
            self.assertTrue(result)
            self.assertEqual( listing_file.read_text(encoding="utf-8"), "old listing\n")

    def test_assemble_source_does_not_save_listing_when_assembly_fails(self) -> None:
        """
        @brief Verify that a failed assembly does not modify an existing
        listing file.
        """
        with tempfile.TemporaryDirectory() as directory:
            source_file = Path(directory) / "test.asm"
            rom_file = Path(directory) / "test.ch8"
            listing_file = Path(directory) / "test.lst"
            listing_file.write_text( "old listing\n", encoding="utf-8")
            controller = create_controller()
            controller._assembler_source_file = source_file
            controller._assembler_rom_file = rom_file
            controller._assembler_listing_file = listing_file
            controller._assembler = MagicMock()
            controller._assembler.assemble.return_value = AssemblyResult(success=False)
            result = controller.assemble_source( "INVALID\n", Target.COSMAC, AssemblyOptions(generate_listing=True))
            self.assertFalse(result)
            self.assertEqual( listing_file.read_text(encoding="utf-8"), "old listing\n")


    ##########################################################################
    # Run assembled source
    ##########################################################################
    def test_run_assembled_source_loads_and_runs_rom(self) -> None:
        """
        @brief Verify that running assembled source loads the generated ROM
        and starts execution.
        """
        with tempfile.TemporaryDirectory() as directory:
            rom_file = Path(directory) / "test.ch8"
            rom_file.write_bytes(bytes([0x00, 0xE0]))

            controller = create_controller()
            controller._assembler_rom_file = rom_file

            controller._load_rom = MagicMock(return_value=True)
            controller.run = MagicMock()

            result = controller.run_assembled_source()

            self.assertTrue(result)
            controller._load_rom.assert_called_once_with(rom_file)
            controller.run.assert_called_once_with()


    def test_run_assembled_source_fails_without_rom_file(self) -> None:
        """
        @brief Verify that running assembled source fails when no assembler
        ROM filename is available.
        """
        controller = create_controller()

        controller._load_rom = MagicMock()
        controller.run = MagicMock()

        result = controller.run_assembled_source()

        self.assertFalse(result)
        controller._load_rom.assert_not_called()
        controller.run.assert_not_called()


    def test_run_assembled_source_does_not_run_when_rom_load_fails(self) -> None:
        """
        @brief Verify that execution is not started when the assembled ROM
        cannot be loaded.
        """
        with tempfile.TemporaryDirectory() as directory:
            rom_file = Path(directory) / "test.ch8"


            controller = create_controller()
            controller._assembler_rom_file = rom_file
            controller._load_rom = MagicMock(return_value=False)
            controller.run = MagicMock()

            result = controller.run_assembled_source()

            self.assertFalse(result)
            controller._load_rom.assert_called_once_with(rom_file)
            controller.run.assert_not_called()

    def test_run_assembled_source_without_assembled_rom(self) -> None:
        """Verify running assembled source fails when no ROM file is configured."""
        with patch.object(Chip8Controller, "__init__", return_value=None):
            controller = Chip8Controller()
        controller._assembler_rom_file = None
        controller._load_rom = MagicMock()
        controller.run = MagicMock()
        result = controller.run_assembled_source()
        self.assertFalse(result)
        controller._load_rom.assert_not_called()
        controller.run.assert_not_called()

    def test_run_assembled_source_when_rom_loading_fails(self) -> None:
        """Verify execution does not start when the assembled ROM fails to load."""
        with patch.object(Chip8Controller, "__init__", return_value=None):
            controller = Chip8Controller()
        controller._assembler_rom_file = Path("assembled.ch8")
        controller._load_rom = MagicMock(return_value=False)
        controller.run = MagicMock()
        result = controller.run_assembled_source()
        self.assertFalse(result)
        controller._load_rom.assert_called_once_with( controller._assembler_rom_file)
        controller.run.assert_not_called()

    @patch("controller.controller.QFileDialog.getOpenFileName")
    def test_load_assembler_source_reports_diagnostics( self, get_open_file_name: Mock) -> None:
        """
        @brief Verify that loading assembler source reports diagnostics.
        """
        with tempfile.TemporaryDirectory() as directory:
            source_file = Path(directory) / "test.asm"
            source_file.write_text("CLS\n", encoding="utf-8")
            get_open_file_name.return_value = (str(source_file), "")
            controller = create_controller()
            source = controller.load_assembler_source()
            self.assertEqual(source, "CLS\n")
            messages = [ diagnostic.message for diagnostic in controller._assembler_diagnostics ]
            self.assertEqual( messages, [ "Loading assembly source file 'test.asm'.", "Assembly source file 'test.asm' loaded." ])

    def test_update_diagnostics_view_formats_diagnostic_address(self) -> None:
        """Verify diagnostics with an address display it in hexadecimal."""
        controller = create_controller()
        controller._diagnostics.clear()
        widget = controller._main_window.diagnosticsListWidget
        widget.clear = MagicMock()
        widget.addItem = MagicMock()
        controller._diagnostics_reporter.error("Test diagnostic", address=0x234)
        controller._update_diagnostics_view()
        widget.clear.assert_called_once_with()
        widget.addItem.assert_called_once()
        displayed_text = widget.addItem.call_args.args[0]
        self.assertIn("234", displayed_text)
        self.assertIn("Test diagnostic", displayed_text)

    ###########################################################################
    # Assemble tests
    ###########################################################################
    def test_save_assembler_source_reports_diagnostics(self) -> None:
        """
        @brief Verify that saving assembler source reports diagnostics.
        """
        with tempfile.TemporaryDirectory() as directory:
            source_file = Path(directory) / "test.asm"
#            configuration = EmulatorConfiguration()
#            configuration.assembler_source_file = str(source_file)
            controller = create_controller()
            controller._assembler_source_file = source_file
            result = controller.save_assembler_source("CLS\n")
            self.assertTrue(result)
            messages = [ diagnostic.message for diagnostic in controller._assembler_diagnostics ]
            self.assertEqual( messages, [ "Saving assembly source file 'test.asm'.", "Assembly source file 'test.asm' saved." ])


    def test_assemble_source_reports_rom_save_diagnostics(self) -> None:
        """
        @brief Verify that successful ROM saving reports its diagnostics.
        """
        with tempfile.TemporaryDirectory() as directory:
            source_file = Path(directory) / "test.asm"
            rom_file = Path(directory) / "test.ch8"
            configuration = EmulatorConfiguration()
            configuration.assembler_rom_file = str(rom_file)
            controller = create_controller(configuration)
            controller._assembler_source_file = source_file
            controller._assembler_rom_file = rom_file
            assembler = MagicMock()
            assembler.assemble.return_value = AssemblyResult( success=True, binary_image=bytes([0x00, 0xE0]))
            controller._create_assembler = MagicMock( return_value=assembler)
            result = controller.assemble_source(
                "CLS\n",
                Target.COSMAC,
                AssemblyOptions()
            )
            self.assertTrue(result)
            messages = [ diagnostic.message for diagnostic in controller._assembler_diagnostics ]
            self.assertIn( "Saving ROM file 'test.ch8'.", messages)
            self.assertIn( "ROM file 'test.ch8' saved.", messages)

    def test_assemble_source_reports_rom_save_error(self) -> None:
        """
        @brief Verify that an error saving the ROM is reported.
        """
        with tempfile.TemporaryDirectory() as directory:
            source_file = Path(directory) / "test.asm"
            rom_file = Path(directory) / "test.ch8"
            configuration = EmulatorConfiguration()
            configuration.assembler_rom_file = str(rom_file)
            controller = create_controller(configuration)
            controller._assembler_source_file = source_file
            controller._assembler_rom_file = rom_file
            assembler = MagicMock()
            assembler.assemble.return_value = AssemblyResult( success=True, binary_image=bytes([0x00, 0xE0]))
            controller._create_assembler = MagicMock(return_value=assembler)
            original_write_bytes = Path.write_bytes
            def fail_write_bytes(path: Path, data: bytes) -> int:
                if path == rom_file:
                    raise OSError("Test ROM write error.")
                return original_write_bytes(path, data)
            with patch.object( Path, "write_bytes", new=fail_write_bytes):
                result = controller.assemble_source(
                    "CLS\n",
                    Target.COSMAC,
                    AssemblyOptions()
                )
            self.assertFalse(result)
            messages = [ diagnostic.message for diagnostic in controller._assembler_diagnostics ]
            self.assertTrue( any( "Test ROM write error." in message for message in messages))

    def test_assemble_source_reports_listing_save_diagnostics(self) -> None:
        """
        @brief Verify that successful listing saving reports its diagnostics.
        """
        with tempfile.TemporaryDirectory() as directory:
            source_file = Path(directory) / "test.asm"
            rom_file = Path(directory) / "test.ch8"
            listing_file = Path(directory) / "test.lst"
            configuration = EmulatorConfiguration()
            configuration.assembler_rom_file = str(rom_file)
            configuration.assembler_listing_file = str(listing_file)
            controller = create_controller(configuration)
            controller._assembler_source_file = source_file
            controller._assembler_rom_file = rom_file
            controller._assembler_listing_file = listing_file
            assembler = MagicMock()
            assembler.assemble.return_value = AssemblyResult( success=True, binary_image=bytes([0x00, 0xE0]), listing="0000 00E0 CLS\n")
            controller._create_assembler = MagicMock( return_value=assembler)
            result = controller.assemble_source(
                "CLS\n",
                Target.COSMAC,
                AssemblyOptions(generate_listing=True)
            )
            self.assertTrue(result)
            messages = [ diagnostic.message for diagnostic in controller._assembler_diagnostics ]
            self.assertIn( "Saving listing file 'test.lst'.", messages)
            self.assertIn( "Listing file 'test.lst' saved.", messages)

    def test_assemble_source_reports_listing_save_error(self) -> None:
        """
        @brief Verify that an error saving the listing is reported.
        """
        with tempfile.TemporaryDirectory() as directory:
            source_file = Path(directory) / "test.asm"
            rom_file = Path(directory) / "test.ch8"
            listing_file = Path(directory) / "test.lst"
            configuration = EmulatorConfiguration()
            configuration.assembler_rom_file = str(rom_file)
            configuration.assembler_listing_file = str(listing_file)
            controller = create_controller(configuration)
            controller._assembler_source_file = source_file
            controller._assembler_rom_file = rom_file
            controller._assembler_listing_file = listing_file
            assembler = MagicMock()
            assembler.assemble.return_value = AssemblyResult( success=True, binary_image=bytes([0x00, 0xE0]), listing="0000 00E0 CLS\n")
            controller._create_assembler = MagicMock(return_value=assembler)
            original_write_text = Path.write_text
            def fail_write_text( path: Path, data: str, *args: object, **kwargs: object) -> int:
                if path == listing_file:
                    raise OSError("Test listing write error.")
                return original_write_text(
                    path,
                    data,
                    *args,
                    **kwargs
                )
            with patch.object( Path, "write_text", new=fail_write_text):
                result = controller.assemble_source(
                    "CLS\n",
                    Target.COSMAC,
                    AssemblyOptions(generate_listing=True)
                )
            self.assertFalse(result)
            messages = [ diagnostic.message for diagnostic in controller._assembler_diagnostics ]
            self.assertTrue( any( "Test listing write error." in message for message in messages))

    def test_assemble_source_reports_completion(self) -> None:
        """
        @brief Verify that successful assembly reports completion after
        saving the generated outputs.
        """
        with tempfile.TemporaryDirectory() as directory:
            source_file = Path(directory) / "test.asm"
            rom_file = Path(directory) / "test.ch8"
            controller = create_controller()
            controller._assembler_source_file = source_file
            controller._assembler_rom_file = rom_file
            result = controller.assemble_source( "CLS\n", Target.COSMAC, AssemblyOptions())
            self.assertTrue(result)
            messages = [ diagnostic.message for diagnostic in controller._assembler_diagnostics ]
            self.assertEqual(
                messages,
                [
                    "Saving assembly source file 'test.asm'.",
                    "Assembly source file 'test.asm' saved.",
                    "Started assembly.",
                    "Parsing source.",
                    "Generating binary image.",
                    "Assembly complete.",
                    "Saving ROM file 'test.ch8'.",
                    "ROM file 'test.ch8' saved."
                ]
            )


    def test_assemble_source_reports_assembly_failure_diagnostics( self) -> None:
        """
        @brief Verify that assembly failure reports assembler diagnostics
        without reporting output-file operations or completion.
        """
        with tempfile.TemporaryDirectory() as directory:
            source_file = Path(directory) / "test.asm"
            rom_file = Path(directory) / "test.ch8"
            controller = create_controller()
            controller._assembler_source_file = source_file
            controller._assembler_rom_file = rom_file
            result = controller.assemble_source( "INVALID\n", Target.COSMAC, AssemblyOptions())
            self.assertFalse(result)
            messages = [ diagnostic.message for diagnostic in controller._assembler_diagnostics ]
            self.assertIn("Started assembly.", messages)
            self.assertIn("Parsing source.", messages)
            self.assertIn("Unsupported instruction 'INVALID'.", messages)
            self.assertNotIn("Generating binary image.", messages)
            self.assertNotIn( "Saving ROM file 'test.ch8'.", messages)
            self.assertNotIn( "ROM file 'test.ch8' saved.", messages)
            self.assertNotIn("Assembly complete.", messages)


    def test_assemble_source_reports_listing_completion(self) -> None:
        """
        @brief Verify that successful assembly with a listing reports all
        output operations in the expected order.
        """
        with tempfile.TemporaryDirectory() as directory:
            source_file = Path(directory) / "test.asm"
            rom_file = Path(directory) / "test.ch8"
            listing_file = Path(directory) / "test.lst"
            controller = create_controller()
            controller._assembler_source_file = source_file
            controller._assembler_rom_file = rom_file
            controller._assembler_listing_file = listing_file
            result = controller.assemble_source( "CLS\n", Target.COSMAC, AssemblyOptions(generate_listing=True))
            self.assertTrue(result)
            messages = [ diagnostic.message for diagnostic in controller._assembler_diagnostics ]
            self.assertEqual(
                messages,
                [
                    "Saving assembly source file 'test.asm'.",
                    "Assembly source file 'test.asm' saved.",
                    "Started assembly.",
                    "Parsing source.",
                    "Generating binary image.",
                    "Generating listing.",
                    "Assembly complete.",
                    "Saving ROM file 'test.ch8'.",
                    "ROM file 'test.ch8' saved.",
                    "Saving listing file 'test.lst'.",
                    "Listing file 'test.lst' saved."
                ]
            )

    def test_assemble_source_reports_cross_reference_completion(self) -> None:
        """
        @brief Verify that successful assembly with a cross-reference
        reports cross-reference generation in the expected order.
        """
        with tempfile.TemporaryDirectory() as directory:
            source_file = Path(directory) / "test.asm"
            rom_file = Path(directory) / "test.ch8"
            listing_file = Path(directory) / "test.lst"
            controller = create_controller()
            controller._assembler_source_file = source_file
            controller._assembler_rom_file = rom_file
            controller._assembler_listing_file = listing_file
            result = controller.assemble_source(
                "START: CLS\n",
                Target.COSMAC,
                AssemblyOptions(
                    generate_listing=True,
                    generate_cross_reference=True
                )
                )
            self.assertTrue(result)
            messages = [ diagnostic.message for diagnostic in controller._assembler_diagnostics ]
            self.assertEqual(
                messages,
                [
                    "Saving assembly source file 'test.asm'.",
                    "Assembly source file 'test.asm' saved.",
                    "Started assembly.",
                    "Parsing source.",
                    "Generating binary image.",
                    "Generating listing.",
                    "Creating cross-reference.",
                    "Assembly complete.",
                    "Saving ROM file 'test.ch8'.",
                    "ROM file 'test.ch8' saved.",
                    "Saving listing file 'test.lst'.",
                    "Listing file 'test.lst' saved."
                ]
            )

    def test_assemble_source_rejects_missing_target_before_assembly(self) -> None:
        """
        @brief Verify that target selection is performed by the controller.
        """
        with tempfile.TemporaryDirectory() as directory:
            source_file = Path(directory) / "test.asm"
            controller = create_controller()
            controller._assembler_source_file = source_file
            controller._assembler = MagicMock()
            result = controller.assemble_source("CLS\n", None, AssemblyOptions())
            self.assertFalse(result)
            controller._assembler.assemble.assert_not_called()
            messages = [diagnostic.message for diagnostic in controller._assembler_diagnostics]
            self.assertIn("No target architecture was specified.", messages)

    def test_assemble_source_rejects_multiple_target_directives(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source_file = Path(directory) / "test.asm"
            rom_file = Path(directory) / "test.ch8"
            controller = create_controller()
            controller._assembler_source_file = source_file
            controller._assembler_rom_file = rom_file
            controller._create_assembler = MagicMock()
            result = controller.assemble_source(
                "TARGET COSMAC\nTARGET SCHIPMODERN\nSCD 1\n",
                Target.COSMAC,
                AssemblyOptions(),
            )
            self.assertFalse(result)
            controller._create_assembler.assert_not_called()
            self.assertFalse(rom_file.exists())
            messages = [ diagnostic.message for diagnostic in controller._assembler_diagnostics ]
            self.assertIn("Multiple TARGET directives found.", messages)

    def test_assemble_source_uses_selected_target_for_assembler(self) -> None:
        """
        @brief Verify that the target selected by the controller is used to
        create the assembler and does not replace the machine ISA.
        """
        with tempfile.TemporaryDirectory() as directory:
            source_file = Path(directory) / "test.asm"
            controller = create_controller()
            controller._assembler_source_file = source_file
            assembler = MagicMock()
            assembler.assemble.return_value = AssemblyResult(success=True)
            machine_isa = controller.machine.isa

            with patch.object( controller, "_create_assembler", return_value=assembler) as create_assembler:
                result = controller.assemble_source(
                    "CLS\n",
                    Target.COSMAC,
                    AssemblyOptions()
                )
            self.assertTrue(result)
            create_assembler.assert_called_once_with(Target.COSMAC)
            self.assertIs(controller.machine.isa, machine_isa)


    def test_assemble_source_does_not_save_empty_binary_rom(self) -> None:
        """
        @brief Verify that a successful assembly with no emitted bytes does
        not create an empty ROM file.
        """
        with tempfile.TemporaryDirectory() as directory:
            source_file = Path(directory) / "test.asm"
            rom_file = Path(directory) / "test.ch8"
            controller = create_controller()
            controller._assembler_source_file = source_file
            controller._assembler_rom_file = rom_file
            controller._assembler = MagicMock()
            controller._assembler.assemble.return_value = AssemblyResult(
                success=True,
                binary_image=b""
            )
            result = controller.assemble_source(
                "ORG 0xFFF\n",
                Target.COSMAC,
                AssemblyOptions()
            )
            self.assertTrue(result)
            self.assertFalse(rom_file.exists())


    ###########################################################################
    # Load ROM tests
    ###########################################################################
    @patch("controller.controller.QFileDialog.getOpenFileName")
    def test_load_rom_reports_diagnostics( self, get_open_file_name: Mock) -> None:
        """
        @brief Verify that loading a ROM reports diagnostics.
        """
        with tempfile.TemporaryDirectory() as directory:
            rom_file = Path(directory) / "PONG.ch8"
            rom_file.write_bytes(bytes([0x00, 0xE0]))
            get_open_file_name.return_value = (str(rom_file), "")
            controller = create_controller()
            controller.load_rom()
            messages = [ diagnostic.message for diagnostic in controller._diagnostics ]
            self.assertEqual( messages, [ "Resetting registers", "Resetting timers", "Loading ROM file 'PONG.ch8'.", "ROM file 'PONG.ch8' loaded.", "Emulator reset." ])


    @patch("controller.controller.QFileDialog.getOpenFileName")
    def test_load_rom_reports_load_error( self, get_open_file_name: Mock) -> None:
        """
        @brief Verify that a ROM load failure reports a diagnostic.
        """
        with tempfile.TemporaryDirectory() as directory:
            rom_file = Path(directory) / "PONG.ch8"
            get_open_file_name.return_value = (str(rom_file), "")
            controller = create_controller()
            controller._diagnostics.clear()
            with patch.object( Path, "read_bytes", side_effect=OSError("disk error")):
                self.assertFalse(controller._load_rom(rom_file))
            messages = [ diagnostic.message for diagnostic in controller._diagnostics ]
            self.assertEqual( messages, [ "Loading ROM file 'PONG.ch8'.", "Unable to load ROM 'PONG.ch8': disk error" ])


    ###########################################################################
    # Run tests
    ###########################################################################
    def test_run_reports_running_rom(self) -> None:
        """
        @brief Verify that starting ROM execution reports a diagnostic.
        """
        controller = create_controller()
        controller._diagnostics.clear()
        controller._current_rom = Path("PONG.ch8")
        controller.run()
        controller._main_window.clear_code_selection.assert_called_once_with()
        messages = [ diagnostic.message for diagnostic in controller._diagnostics ]
        self.assertEqual( messages, ["Running ROM file 'PONG.ch8'."])


    def test_run_without_rom_does_not_report_rom_diagnostic(self) -> None:
        """
        @brief Verify that running without a loaded ROM does not report a ROM
        diagnostic.
        """
        controller = create_controller()
        controller._diagnostics.clear()
        controller.run()
        self.assertEqual(len(controller._diagnostics), 0)


    def test_run_when_already_running_does_not_restart_execution(self) -> None:
        """Verify run returns early when execution is already active."""
        controller = create_controller()
        controller._running = True
        controller._cpu_timer.start = MagicMock()
        controller._hardware_timer.start = MagicMock()
        controller._main_window.clear_code_selection = MagicMock()
        controller._main_window.show_status_message = MagicMock()
        controller.run()
        controller._cpu_timer.start.assert_not_called()
        controller._hardware_timer.start.assert_not_called()
        controller._main_window.clear_code_selection.assert_not_called()
        controller._main_window.show_status_message.assert_not_called()


    ###########################################################################
    # Stop tests
    ###########################################################################
    def test_stop_reports_execution_stopped(self) -> None:
        """
        @brief Verify that stopping execution reports a diagnostic.
        """
        controller = create_controller()
        controller._diagnostics.clear()
        controller._running = True
        controller.stop()
        messages = [ diagnostic.message for diagnostic in controller._diagnostics ]
        self.assertEqual( messages, ["Execution stopped."])


    def test_stop_when_not_running_does_not_report_diagnostic(self) -> None:
        """
        @brief Verify that stopping an already stopped controller does not
        report a diagnostic.
        """
        controller = create_controller()
        controller._diagnostics.clear()
        controller.stop()
        self.assertEqual(len(controller._diagnostics), 0)

    ###########################################################################
    # Reset tests
    ###########################################################################
    def test_reset_reports_diagnostic(self) -> None:
        """
        @brief Verify that resetting the emulator reports a diagnostic.
        """
        controller = create_controller()
        controller._diagnostics.clear()
        controller.reset()
        messages = [ diagnostic.message for diagnostic in controller._diagnostics ]
        self.assertIn("Emulator reset.", messages)


    def test_reset_reports_stop_and_reset_diagnostics_when_running(self) -> None:
        """
        @brief Verify that resetting a running emulator reports both the stop
        and reset diagnostics.
        """
        controller = create_controller()
        controller._diagnostics.clear()
        controller._running = True
        controller.reset()
        messages = [ diagnostic.message for diagnostic in controller._diagnostics ]
        self.assertEqual( messages, [ "Execution stopped.", "Resetting registers", "Resetting timers", "Emulator reset." ])


    def test_reset_when_program_counter_has_no_code_row(self) -> None:
        """Verify reset completes when the program counter has no code row."""
        controller = create_controller()
        controller._current_rom_data = bytes([0x00, 0xE0])
        controller._code_analysis.find_row = MagicMock(return_value=None)
        controller._main_window.scroll_code_to_row = MagicMock()
        controller.update_gui = MagicMock()
        controller.reset()
        controller._code_analysis.find_row.assert_called_once_with( controller._machine.registers.pc)
        controller._main_window.scroll_code_to_row.assert_not_called()
        controller.update_gui.assert_called_once()


    ###########################################################################
    # ROM reload tests
    ###########################################################################
    def test_reload_rom_reports_diagnostics(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            rom_file = Path(directory) / "PONG.ch8"
            rom_file.write_bytes(bytes([0x00, 0xE0]))
            controller = create_controller()
            controller._current_rom = rom_file
            controller._current_rom_data = rom_file.read_bytes()
            controller._diagnostics.clear()
            controller.reload_rom()
            messages = [ diagnostic.message for diagnostic in controller._diagnostics ]
            self.assertEqual(
                messages,
                [
                    "Resetting registers",
                    "Resetting timers",
                    "Emulator reset.",
                    "Reloaded ROM file 'PONG.ch8'."
                ]
            )

    def test_reload_rom_without_rom_reports_no_diagnostics(self) -> None:
        controller = create_controller()
        controller._diagnostics.clear()
        controller.reload_rom()
        self.assertEqual(len(controller._diagnostics), 0)


    ###########################################################################
    # Single step tests
    ###########################################################################
    def test_step_reports_diagnostic(self) -> None:
        controller = create_controller()
        controller._diagnostics.clear()
        controller._execute_cycle = MagicMock()
        controller.step()
        controller._main_window.clear_code_selection.assert_called_once_with()
        controller._execute_cycle.assert_called_once_with()
        messages = [ diagnostic.message for diagnostic in controller._diagnostics ]
        self.assertEqual(messages, ["Single step."])


    def test_step_while_running_reports_no_diagnostic(self) -> None:
        controller = create_controller()
        controller._diagnostics.clear()
        controller._running = True
        controller._execute_cycle = MagicMock()
        controller.step()
        controller._main_window.clear_code_selection.assert_not_called()
        controller._execute_cycle.assert_not_called()
        self.assertEqual(len(controller._diagnostics), 0)


    ###########################################################################
    # Run-To tests
    ###########################################################################
    def test_run_to_address_reports_diagnostic(self) -> None:
        controller = create_controller()
        controller._diagnostics.clear()
        controller._main_window.selected_code_address = MagicMock( return_value=0x300)
        controller.run = MagicMock()
        controller.run_to_address()
        controller.run.assert_called_once_with()
        messages = [ diagnostic.message for diagnostic in controller._diagnostics ]
        self.assertEqual( messages, ["Running to address 0x300."])


    def test_run_to_address_without_selection_reports_no_diagnostic( self) -> None:
        controller = create_controller()
        controller._diagnostics.clear()
        controller._main_window.selected_code_address = MagicMock( return_value=None)
        controller.run = MagicMock()
        controller.run_to_address()
        controller.run.assert_not_called()
        self.assertEqual(len(controller._diagnostics), 0)


    def test_run_to_address_at_current_pc_reports_no_diagnostic(self) -> None:
        controller = create_controller()
        controller._diagnostics.clear()
        controller._main_window.selected_code_address = MagicMock( return_value=controller._machine.registers.pc)
        controller.run = MagicMock()
        controller.run_to_address()
        controller.run.assert_not_called()
        self.assertEqual(len(controller._diagnostics), 0)


    ###########################################################################
    # Set-PC tests
    ###########################################################################
    def test_set_program_counter_updates_machine_and_gui(self) -> None:
        controller = create_controller()
        controller._diagnostics.clear()
        controller._update_register_view = MagicMock()
        controller._update_code_view = MagicMock()
        controller._machine.registers.pc = 0x200
        controller._debugger.set_temporary_breakpoint(0x240)

        controller._set_program_counter(0x300)

        self.assertEqual(controller._machine.registers.pc, 0x300)
        self.assertIsNone(controller._debugger.temporary_breakpoint)
        controller._update_register_view.assert_called_once_with()
        controller._update_code_view.assert_called_once_with()
        messages = [diagnostic.message for diagnostic in controller._diagnostics]
        self.assertEqual(messages, ["Program counter set to address 0x300."])

    def test_set_program_counter_does_nothing_while_running(self) -> None:
        controller = create_controller()
        controller._diagnostics.clear()
        controller._running = True
        controller._update_register_view = MagicMock()
        controller._update_code_view = MagicMock()
        controller._machine.registers.pc = 0x200

        controller._set_program_counter(0x300)

        self.assertEqual(controller._machine.registers.pc, 0x200)
        controller._update_register_view.assert_not_called()
        controller._update_code_view.assert_not_called()
        self.assertEqual(len(controller._diagnostics), 0)


    ###########################################################################
    # Step-Over tests
    ###########################################################################
    def test_step_over_call_reports_diagnostic(self) -> None:
        controller = create_controller()
        controller._diagnostics.clear()
        controller._machine.registers.pc = 0x300
        controller._machine.memory.write_byte(0x300, 0x23)
        controller._machine.memory.write_byte(0x301, 0x45)
        controller.run = MagicMock()
        controller.step_over()
        controller.run.assert_called_once_with()
        messages = [ diagnostic.message for diagnostic in controller._diagnostics ]
        self.assertEqual( messages, ["Stepping over call to 0x345."])


    def test_step_over_non_call_does_not_report_diagnostic(self) -> None:
        controller = create_controller()
        controller._diagnostics.clear()
        controller._machine.registers.pc = 0x300
        controller._machine.memory.write_byte(0x300, 0x00)
        controller._machine.memory.write_byte(0x301, 0xE0)
        controller.step = MagicMock()
        controller.step_over()
        controller.step.assert_called_once_with()
        self.assertEqual(len(controller._diagnostics), 0)


    def test_step_over_when_running_returns_without_decoding_instruction(self) -> None:
        """Verify step over does nothing while continuous execution is active."""
        controller = create_controller()
        controller._running = True
        controller._machine.memory.read_byte = MagicMock()
        controller._isa.decode = MagicMock()
        controller.step = MagicMock()
        controller.step_over()
        controller._machine.memory.read_byte.assert_not_called()
        controller._isa.decode.assert_not_called()
        controller.step.assert_not_called()

    ###########################################################################
    # Step-Out tests
    ###########################################################################
    def test_step_out_reports_diagnostic(self) -> None:
        controller = create_controller()
        controller._diagnostics.clear()
        controller._machine.stack.push(0x345)
        controller.run = MagicMock()
        controller.step_out()
        controller.run.assert_called_once_with()
        messages = [ diagnostic.message for diagnostic in controller._diagnostics ]
        self.assertEqual( messages, ["Stepping out to address 0x345."])


    def test_step_out_without_subroutine_reports_no_diagnostic(self) -> None:
        controller = create_controller()
        controller._diagnostics.clear()
        controller.run = MagicMock()
        controller.step_out()
        controller.run.assert_not_called()
        self.assertEqual(len(controller._diagnostics), 0)

    def test_step_out_when_running_returns_without_checking_stack(self) -> None:
        """Verify step out does nothing while continuous execution is active."""
        controller = create_controller()
        controller._running = True
        controller._machine.stack.empty = MagicMock()
        controller._machine.stack.peek = MagicMock()
        controller._debugger.set_temporary_breakpoint = MagicMock()
        controller.run = MagicMock()
        controller.step_out()
        controller._machine.stack.empty.assert_not_called()
        controller._machine.stack.peek.assert_not_called()
        controller._debugger.set_temporary_breakpoint.assert_not_called()
        controller.run.assert_not_called()

    ###########################################################################
    # Set CPU frequency tests
    ###########################################################################
    def test_set_cpu_frequency_reports_diagnostic(self) -> None:
        controller = create_controller()
        controller._diagnostics.clear()
        controller.set_cpu_frequency(700)
        messages = [ diagnostic.message for diagnostic in controller._diagnostics ]
        self.assertEqual( messages, ["CPU frequency set to 700 Hz."])


    def test_set_cpu_frequency_reports_effective_frequency(self) -> None:
        controller = create_controller()
        controller._diagnostics.clear()
        controller.set_cpu_frequency(0)
        messages = [ diagnostic.message for diagnostic in controller._diagnostics ]
        self.assertEqual( messages, ["CPU frequency set to 1 Hz."])


    ###########################################################################
    # Configure tests
    ###########################################################################
    def test_configure_reports_diagnostic_when_accepted(self) -> None:
        controller = create_controller()
        controller._diagnostics.clear()
        controller._main_window.configure = MagicMock(return_value=True)
        controller.configure()
        messages = [ diagnostic.message for diagnostic in controller._diagnostics ]
        self.assertEqual( messages, ["Emulator configuration updated."])


    def test_configure_reports_no_diagnostic_when_cancelled(self) -> None:
        controller = create_controller()
        controller._diagnostics.clear()
        controller._main_window.configure = MagicMock(return_value=False)
        controller.configure()
        self.assertEqual(len(controller._diagnostics), 0)

    def test_configure_rebuilds_analysis_when_architecture_changes_without_rom(self) -> None:
        controller = create_controller()
        new_configuration = EmulatorConfiguration( emulation_mode=EmulationMode.SUPERCHIP_11)
        def accept_configuration() -> bool:
            controller._main_window.config_dialog.configuration = new_configuration
            return True
        controller._main_window.configure.side_effect = accept_configuration
        with patch.object(controller, "reset") as reset:
            with patch.object(controller._code_analysis, "clear_runtime_observations") as clear_observations:
                with patch.object(controller._code_analysis, "rebuild") as rebuild:
                    with patch.object(controller._code_model, "refresh") as refresh_code:
                        with patch.object(controller, "_update_diagnostics_view") as update_diagnostics:
                            controller.configure()
        self.assertIs(controller._configuration, new_configuration)
        self.assertIsInstance(controller.machine.isa, SuperChip11InstructionSetArchitecture)
        reset.assert_called_once_with()
        clear_observations.assert_called_once_with()
        rebuild.assert_called_once_with()
        refresh_code.assert_called_once_with()
        update_diagnostics.assert_called_once_with()


    def test_configure_architecture_change_with_loaded_rom(self) -> None:
        """Verify architecture changes reset the emulator when a ROM is loaded."""
        controller = create_controller()
        controller._current_rom_data = bytes([0x00, 0xE0])
        controller._diagnostics.clear()
        dialog = controller._main_window.config_dialog
        def accept_changed_configuration() -> bool:
            dialog.configuration = EmulatorConfiguration( emulation_mode=EmulationMode.SUPERCHIP_10)
            return True
        controller._main_window.configure = MagicMock( side_effect=accept_changed_configuration)
        controller.reset = MagicMock()
        controller.configure()
        controller.reset.assert_called_once()


    ###########################################################################
    # Toggle breakpoints tests
    ###########################################################################
    def test_toggle_breakpoint_reports_breakpoint_set(self) -> None:
        controller = create_controller()
        controller._diagnostics.clear()
        controller._toggle_breakpoint(0x345)
        messages = [ diagnostic.message for diagnostic in controller._diagnostics ]
        self.assertEqual( messages, ["Breakpoint enabled at address 0x345."])


    def test_toggle_breakpoint_reports_breakpoint_disabled(self) -> None:
        controller = create_controller()
        controller._diagnostics.clear()
        controller._debugger.set_breakpoint(0x345)
        controller._toggle_breakpoint(0x345)
        messages = [ diagnostic.message for diagnostic in controller._diagnostics ]
        self.assertEqual( messages, ["Breakpoint disabled at address 0x345."])


    def test_toggle_breakpoint_reports_breakpoint_enabled(self) -> None:
        controller = create_controller()
        controller._diagnostics.clear()
        controller._debugger.set_breakpoint(0x345)
        controller._debugger.disable_breakpoint(0x345)
        controller._toggle_breakpoint(0x345)
        messages = [ diagnostic.message for diagnostic in controller._diagnostics ]
        self.assertEqual( messages, ["Breakpoint enabled at address 0x345."])

    def test_assembler_new_clears_project_paths(self) -> None:
        controller = create_controller()
        controller._assembler_source_file = Path("program.asm")
        controller._assembler_rom_file = Path("program.ch8")
        controller._assembler_listing_file = Path("program.lst")
        controller._configuration.assembler_source_file = "program.asm"
        controller._configuration.assembler_rom_file = "program.ch8"
        controller._configuration.assembler_listing_file = "program.lst"
        controller.assembler_new()
        self.assertIsNone(controller.assembler_source_file)
        self.assertIsNone(controller.assembler_rom_file)
        self.assertIsNone(controller.assembler_listing_file)
        self.assertEqual(controller._configuration.assembler_source_file, "")
        self.assertEqual(controller._configuration.assembler_rom_file, "")
        self.assertEqual(controller._configuration.assembler_listing_file, "")

    def test_assembler_new_clears_current_file_associations(self) -> None:
        """
        @brief Verify that starting a new assembler source clears the current
        source and output file associations.
        """
        configuration = EmulatorConfiguration()
        configuration.assembler_source_file = "/tmp/test.asm"
        configuration.assembler_rom_file = "/tmp/test.ch8"
        configuration.assembler_listing_file = "/tmp/test.lst"
        controller = create_controller(configuration)
        controller._assembler_source_file = Path("/tmp/test.asm")
        controller._assembler_rom_file = Path("/tmp/test.ch8")
        controller._assembler_listing_file = Path("/tmp/test.lst")
        controller.assembler_new()
        self.assertIsNone(controller.assembler_source_file)
        self.assertIsNone(controller.assembler_rom_file)
        self.assertIsNone(controller.assembler_listing_file)
        self.assertEqual(configuration.assembler_source_file, "")
        self.assertEqual(configuration.assembler_rom_file, "")
        self.assertEqual(configuration.assembler_listing_file, "")



    def test_assembler_uses_its_own_isa_and_matching_parser(self) -> None:
        """Verify assembler dependencies are paired and isolated from the machine."""
        controller = create_controller()
        machine_isa = controller.machine.isa
        assembler = controller._create_assembler(Target.COSMAC)
        self.assertIsNot(assembler._isa, machine_isa)
        self.assertIs(assembler._isa, assembler._parser._isa)
        self.assertIs(controller.machine.isa, machine_isa)

    ###########################################################################
    # private helpers
    ###########################################################################
    def test_update_display_passes_framebuffer_pixels_to_display(self) -> None:
        """Verify the display receives the machine's current framebuffer pixels."""
        controller = create_controller()
        pixels = object()
        controller._machine.framebuffer.pixels = MagicMock(return_value=pixels)
        controller._main_window.display.set_framebuffer = MagicMock()
        controller._update_display()
        controller._machine.framebuffer.pixels.assert_called_once_with()
        controller._main_window.display.set_framebuffer.assert_called_once_with(pixels)

    ###########################################################################
    # Misc
    ###########################################################################
    def test_public_properties_return_controller_state(self) -> None:
        """Verify public properties expose the corresponding controller state."""
        controller = create_controller()
        self.assertIs(controller.machine, controller._machine)
        self.assertIs(controller.main_window, controller._main_window)
        self.assertIs(controller.debugger, controller._debugger)
        self.assertEqual(controller.running, controller._running)
        self.assertEqual(controller.cpu_frequency, controller._cpu_frequency)
        self.assertIsNone(controller.current_rom)
        self.assertIsNone(controller.assembler_source_file)
        self.assertIsNone(controller.assembler_rom_file)
        self.assertIsNone(controller.assembler_listing_file)

    def test_assembler_delegates_to_main_window(self) -> None:
        """Verify the assembler command delegates to the main window."""
        controller = create_controller()
        controller._main_window.assemble = MagicMock()
        controller.assembler()
        controller._main_window.assemble.assert_called_once_with()

    def test_update_register_view_formats_register_values(self) -> None:
        """Verify that V-register values are displayed as two-digit hexadecimal."""
        controller = create_controller()
        labels = [MagicMock() for _ in range(16)]
        controller._main_window.register_labels = labels
        registers = controller._machine.registers
        for index in range(16):
            registers.write_register(index, index)
        controller._update_register_view()
        for index, label in enumerate(labels):
            label.setText.assert_called_once_with(f"{index:02X}")


    def test_create_emulator_isa_rejects_unsupported_mode(self) -> None:
        """Verify unsupported emulation modes raise ValueError."""
        unsupported_mode = cast(EmulationMode, Mock(value="unsupported"))
        with self.assertRaisesRegex(ValueError, "not implemented yet"):
            Chip8Controller._create_emulator_isa(unsupported_mode)


    def test_create_assembler_rejects_unsupported_target(self) -> None:
        """Verify unsupported assembler targets raise TargetSelectionError."""
        from assembler.target_selector import TargetSelectionError
        controller = create_controller()
        unsupported_target = cast(Target, Mock(value="unsupported"))
        with self.assertRaisesRegex(TargetSelectionError, "Unsupported target architecture"):
            controller._create_assembler(unsupported_target)


    def test_constructor_loads_existing_last_rom(self) -> None:
        """Verify the constructor loads the previously used ROM when it exists."""
        with tempfile.NamedTemporaryFile() as rom_file:
            settings = MagicMock()
            settings.value.side_effect = lambda key, default=None, **kwargs: ( rom_file.name if key == "recent/last_rom" else default)
            settings_manager = MagicMock()
            settings_manager.settings.return_value = settings
            with (
                patch("controller.controller.SettingsManager", return_value=settings_manager),
                patch("controller.controller.MainWindow"),
                patch.object(Chip8Controller, "_load_rom") as load_rom
            ):
                Chip8Controller()
            load_rom.assert_called_once_with(Path(rom_file.name))

