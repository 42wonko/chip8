"""Tests for the controller's ROM byte-search workflow."""

from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

from controller.controller import Chip8Controller


class TestControllerRomByteSearch(unittest.TestCase):
    def _controller(self, rom_data: bytes | None) -> Chip8Controller:
        with patch.object(Chip8Controller, "__init__", return_value=None):
            controller = Chip8Controller()
        controller._current_rom_data = rom_data
        controller._main_window = Mock()
        controller._memory_model = Mock()
        controller._diagnostics_reporter = Mock()
        return controller

    def test_search_navigates_to_selected_match_and_highlights_sequence(self) -> None:
        controller = self._controller(bytes.fromhex("00 A2 30 FF A2 30"))
        with (
            patch("controller.controller.QInputDialog.getText", return_value=("A2 30", True)),
            patch("controller.controller.QInputDialog.getItem", return_value=("0x201", True)),
        ):
            controller.search_rom_bytes()

        controller._memory_model.refresh_range.assert_called_once_with(0x201, 0x202)
        controller._diagnostics_reporter.info.assert_called_once_with(
            "Found byte sequence at address 0x201."
        )

    def test_search_without_loaded_rom_reports_information(self) -> None:
        controller = self._controller(None)
        with patch("controller.controller.QMessageBox.information") as information:
            controller.search_rom_bytes()

        information.assert_called_once_with(
            controller._main_window,
            "Search ROM Bytes",
            "Load a ROM before searching for bytes.",
        )

    def test_invalid_sequence_reports_warning(self) -> None:
        controller = self._controller(b"\xA2\x30")
        with (
            patch("controller.controller.QInputDialog.getText", return_value=("A2 GG", True)),
            patch("controller.controller.QMessageBox.warning") as warning,
        ):
            controller.search_rom_bytes()

        warning.assert_called_once()
        controller._memory_model.refresh_range.assert_not_called()

    def test_no_match_reports_information(self) -> None:
        controller = self._controller(b"\x00\xE0")
        with (
            patch("controller.controller.QInputDialog.getText", return_value=("A2 30", True)),
            patch("controller.controller.QMessageBox.information") as information,
        ):
            controller.search_rom_bytes()

        information.assert_called_once_with(
            controller._main_window,
            "Search ROM Bytes",
            "The byte sequence was not found in the loaded ROM.",
        )


if __name__ == "__main__":
    unittest.main()
