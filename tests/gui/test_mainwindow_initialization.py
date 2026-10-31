"""
Tests for MainWindow construction and initialization.
"""

from __future__ import annotations

import unittest
from unittest.mock import Mock, call, patch

from PyQt6.QtCore import Qt, QEvent, QModelIndex, QPoint
from PyQt6.QtGui import QStandardItemModel
from PyQt6.QtWidgets import QAbstractItemView, QApplication, QDialog, QListWidget, QTableView

from gui.displaywidget import DisplayWidget
from gui.mainwindow import MainWindow


class TestMainWindowInitialization(unittest.TestCase):
    """Exercise MainWindow's real Designer-based initialization."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.application = QApplication.instance()
        if cls.application is None:
            cls.application = QApplication([])

    def setUp(self) -> None:
        self.controller = Mock()
        self.controller.cpu_frequency = 500
        self.controller.debugger = Mock()

        self.config_dialog = QDialog()
        self.assembler_dialog = QDialog()

        self.config_dialog.exec = Mock(
            return_value=QDialog.DialogCode.Accepted
        )

    def tearDown(self) -> None:
        for widget in (self.config_dialog, self.assembler_dialog):
            widget.close()
            widget.deleteLater()

    def _create_window(self) -> MainWindow:
        with (
            patch(
                "gui.mainwindow.ConfigDialog",
                return_value=self.config_dialog
            ) as config_dialog_type,
            patch(
                "gui.mainwindow.AssemblerDialog",
                return_value=self.assembler_dialog
            ) as assembler_dialog_type
        ):
            window = MainWindow(self.controller)

        config_dialog_type.assert_called_once_with(window)
        assembler_dialog_type.assert_called_once_with(
            self.controller,
            window
        )
        return window

    def test_constructor_initializes_ui_and_dialogs(self) -> None:
        window = self._create_window()
        self.addCleanup(window.close)
        self.addCleanup(window.deleteLater)

        self.assertEqual(window.clockFreqSlider.value(), 500)
        self.assertEqual(window.clockFreqLabel.text(), "500 Hz")
        self.assertEqual(window.statusbar.currentMessage(), "Ready")
        self.assertEqual(len(window.register_labels), 16)
        self.assertIsInstance(window.display, DisplayWidget)
        self.assertIs(window.config_dialog, self.config_dialog)
        self.assertIs(window.assembler_dialog, self.assembler_dialog)

    def test_constructor_sets_assembler_window_flags(self) -> None:
        window = self._create_window()
        self.addCleanup(window.close)
        self.addCleanup(window.deleteLater)

        flags = self.assembler_dialog.windowFlags()
        self.assertTrue(flags & Qt.WindowType.CustomizeWindowHint)
        self.assertTrue(flags & Qt.WindowType.WindowTitleHint)
        self.assertTrue(flags & Qt.WindowType.WindowMaximizeButtonHint)

    def test_button_signals_are_connected_to_controller(self) -> None:
        window = self._create_window()
        self.addCleanup(window.close)
        self.addCleanup(window.deleteLater)

        window.loadButton.click()
        self.controller.load_rom.assert_called_once_with(False)

        window.runButton.click()
        window.continueButton.click()
        self.assertEqual(self.controller.run.call_count, 2)

        window.stopExecutionButton.click()
        self.controller.stop.assert_called_once_with(False)

        window.resetButton.click()
        self.controller.reset.assert_called_once_with(False)

        window.singleStepButton.click()
        window.dbgStepInPushButton.click()
        self.assertEqual(self.controller.step.call_count, 2)

        window.keyboardButton.click()
        self.controller.configure_keyboard.assert_called_once_with(False)

        window.configButton.click()
        self.controller.configure.assert_called_once_with(False)

        window.assemblerPushButton.click()
        self.controller.assembler.assert_called_once_with(False)

        window.dbgRunToAddressPushButton.click()
        self.controller.run_to_address.assert_called_once_with(False)

        window.dbgStepOverPushButton.click()
        self.controller.step_over.assert_called_once_with(False)

        window.dbgStepOutPushButton.click()
        self.controller.step_out.assert_called_once_with(False)

    def test_clock_slider_updates_controller_and_label(self) -> None:
        window = self._create_window()
        self.addCleanup(window.close)
        self.addCleanup(window.deleteLater)
        window.clockFreqSlider.setValue(750)
        self.controller.set_cpu_frequency.assert_called_once_with(750)
        self.assertEqual(window.clockFreqLabel.text(), "750 Hz")

    def test_debugger_group_toggle_is_connected(self) -> None:
        window = self._create_window()
        self.addCleanup(window.close)
        self.addCleanup(window.deleteLater)
        initial_state = window.debuggerControlGroupBox.isChecked()
        new_state = not initial_state
        window.debuggerControlGroupBox.setChecked(new_state)
        self.controller.debugger.enable.assert_called_once_with(new_state)

    def test_search_rom_action_emits_request_signal(self) -> None:
        window = self._create_window()
        self.addCleanup(window.close)
        self.addCleanup(window.deleteLater)
        requests: list[bool] = []
        window.rom_byte_search_requested.connect( lambda: requests.append(True))
        tools_menu = next(
            action.menu()
            for action in window.menuBar.actions()
            if action.menu() is not None
            and action.menu().title() == "Tools"
        )
        search_action = next(
            action
            for action in tools_menu.actions()
            if action.text() == "Search ROM Bytes…"
        )
        search_action.trigger()
        self.assertEqual(requests, [True])

    def test_configure_returns_dialog_acceptance(self) -> None:
        window = self._create_window()
        self.addCleanup(window.close)
        self.addCleanup(window.deleteLater)
        self.assertTrue(window.configure())
        self.config_dialog.exec.assert_called_once_with()
        self.config_dialog.exec.reset_mock()
        self.config_dialog.exec.return_value = QDialog.DialogCode.Rejected
        self.assertFalse(window.configure())

    def test_assemble_shows_and_activates_dialog(self) -> None:
        window = self._create_window()
        self.addCleanup(window.close)
        self.addCleanup(window.deleteLater)

        with (
            patch.object(self.assembler_dialog, "show") as show,
            patch.object(self.assembler_dialog, "raise_") as raise_window,
            patch.object( self.assembler_dialog, "activateWindow") as activate
        ):
            window.assemble()
        show.assert_called_once_with()
        raise_window.assert_called_once_with()
        activate.assert_called_once_with()


    def test_restore_settings_restores_geometry_and_state(self) -> None:
        window = self._create_window()
        self.addCleanup(window.close)
        self.addCleanup(window.deleteLater)
        geometry = b"saved geometry"
        state = b"saved state"
        with patch("gui.mainwindow.QSettings") as settings_type:
            settings = settings_type.return_value
            settings.value.side_effect = lambda key: { "mainwindow/geometry": geometry, "mainwindow/state": state }.get(key)
            with (
                patch.object(window, "restoreGeometry") as restore_geometry,
                patch.object(window, "restoreState") as restore_state
            ):
                window.restore_settings()
        settings_type.assert_called_once()
        restore_geometry.assert_called_once_with(geometry)
        restore_state.assert_called_once_with(state)

    def test_save_settings_saves_geometry_and_state(self) -> None:
        window = self._create_window()
        self.addCleanup(window.close)
        self.addCleanup(window.deleteLater)
        geometry = b"current geometry"
        state = b"current state"

        with patch("gui.mainwindow.QSettings") as settings_type:
            with (
                patch.object(window, "saveGeometry", return_value=geometry),
                patch.object(window, "saveState", return_value=state)
            ):
                window.save_settings()
            settings = settings_type.return_value
            settings.setValue.assert_any_call( "mainwindow/geometry", geometry)
            settings.setValue.assert_any_call( "mainwindow/state", state)
            self.assertEqual(settings.setValue.call_count, 2)

    def test_scroll_code_to_row_does_not_scroll_visible_row(self) -> None:
        window = self._create_window()
        self.addCleanup(window.close)
        self.addCleanup(window.deleteLater)
        model = QStandardItemModel(10, 1)
        window.codeTableView.setModel(model)
        window.codeTableView.resize(400, 300)
        window.codeTableView.show()
        self.application.processEvents()
        with patch.object(window.codeTableView, "scrollTo") as scroll_to:
            window.scroll_code_to_row(0)
        scroll_to.assert_not_called()

    def test_scroll_memory_to_address(self) -> None:
        window = self._create_window()
        self.addCleanup(window.close)
        self.addCleanup(window.deleteLater)
        model = QStandardItemModel(256, 16)
        window.memoryTableView.setModel(model)
        with patch.object(window.memoryTableView, "scrollTo") as scroll_to:
            window._scroll_memory_to_address(0x123)
        scroll_to.assert_called_once_with( model.index(0x123 // 16, 0), QAbstractItemView.ScrollHint.PositionAtCenter)

    def test_code_table_context_menu_ignores_invalid_index(self) -> None:
        window = self._create_window()
        self.addCleanup(window.close)
        self.addCleanup(window.deleteLater)
        requests: list[tuple[int, object]] = []
        window.code_context_menu_requested.connect( lambda row, position: requests.append((row, position)))
        with patch.object( window.codeTableView, "indexAt", return_value=QModelIndex()):
            window._code_table_context_menu(QPoint(10, 10))
        self.assertEqual(requests, [])

    def test_event_filter_ignores_non_key_event(self) -> None:
        window = self._create_window()
        self.addCleanup(window.close)
        self.addCleanup(window.deleteLater)
        event = QEvent(QEvent.Type.KeyPress)
        handled = window.eventFilter( window.diagnosticsListWidget, event)

        self.assertFalse(handled)

    def test_copy_selected_diagnostics_without_clipboard(self) -> None:
        window = self._create_window()
        self.addCleanup(window.close)
        self.addCleanup(window.deleteLater)
        window.diagnosticsListWidget.addItems( ["First diagnostic", "Second diagnostic"])
        window.diagnosticsListWidget.setSelectionMode( QAbstractItemView.SelectionMode.MultiSelection)
        window.diagnosticsListWidget.selectAll()
        self.assertEqual( len(window.diagnosticsListWidget.selectedItems()), 2)
        with patch( "gui.mainwindow.QApplication.clipboard", return_value=None):
            window._copy_selected_diagnostics()

    def test_initialize_raises_when_menu_bar_is_unavailable(self) -> None:
        window = self._create_window()
        self.addCleanup(window.close)
        self.addCleanup(window.deleteLater)
        with patch.object(window, "menuBar", None):
            with self.assertRaisesRegex( RuntimeError, "Main window menu bar is not available."):
                window._initialize()

    def test_restore_settings_when_geometry_and_state_are_missing(self) -> None:
        window = self._create_window()
        self.addCleanup(window.close)
        self.addCleanup(window.deleteLater)
        with patch("gui.mainwindow.QSettings") as settings_type:
            settings_type.return_value.value.return_value = None
            with (
                patch.object(window, "restoreGeometry") as restore_geometry,
                patch.object(window, "restoreState") as restore_state
            ):
                window.restore_settings()
        self.assertEqual(
            settings_type.return_value.value.call_args_list,
            [
                call("mainwindow/geometry"),
                call("mainwindow/state")
            ]
        )
        restore_geometry.assert_not_called()
        restore_state.assert_not_called()

if __name__ == "__main__":
    unittest.main()
