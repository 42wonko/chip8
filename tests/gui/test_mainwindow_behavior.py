
"""
@file test_mainwindow_behavior.py

@brief Tests for MainWindow behavior not covered by test_mainwindow.py.
"""

from __future__ import annotations

import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from PyQt6.QtCore import QEvent, QModelIndex, Qt
from PyQt6.QtGui import QKeyEvent, QStandardItemModel
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QDialog,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QTableView,
)

from gui.codetablemodel import CodeTableModel
from gui.mainwindow import MainWindow


class TestMainWindowBehavior(unittest.TestCase):
    """Tests for the public and private behavior of MainWindow."""

    @classmethod
    def setUpClass(cls) -> None:
        cls._application = QApplication.instance()
        if cls._application is None:
            cls._application = QApplication([])

    def setUp(self) -> None:
        self.window = MainWindow.__new__(MainWindow)
        QMainWindow.__init__(self.window)
        self.controller = Mock()
        self.window._controller = self.controller
        self.window.codeTableView = QTableView()
        self.window.memoryTableView = QTableView()
        self.window.diagnosticsListWidget = QListWidget()

    def tearDown(self) -> None:
        self.window.close()
        self.window.deleteLater()

    def test_key_press_forwards_key_to_controller(self) -> None:
        event = QKeyEvent( QEvent.Type.KeyPress, Qt.Key.Key_A, Qt.KeyboardModifier.NoModifier)
        self.window.keyPressEvent(event)
        self.controller.key_down.assert_called_once_with(Qt.Key.Key_A)

    def test_key_press_with_none_does_not_call_controller(self) -> None:
        self.window.keyPressEvent(None)
        self.controller.key_down.assert_not_called()

    def test_key_release_forwards_key_to_controller(self) -> None:
        event = QKeyEvent( QEvent.Type.KeyRelease, Qt.Key.Key_B, Qt.KeyboardModifier.NoModifier)
        self.window.keyReleaseEvent(event)
        self.controller.key_up.assert_called_once_with(Qt.Key.Key_B)

    def test_key_release_with_none_does_not_call_controller(self) -> None:
        self.window.keyReleaseEvent(None)
        self.controller.key_up.assert_not_called()

    def test_scroll_code_to_row_without_model_returns(self) -> None:
        self.window.scroll_code_to_row(0)
        self.assertIsNone(self.window.codeTableView.model())

    def test_scroll_code_to_row_with_invalid_index_returns(self) -> None:
        model = QStandardItemModel(1, 1)
        self.window.codeTableView.setModel(model)
        self.window.scroll_code_to_row(5)
        self.assertEqual(self.window.codeTableView.verticalScrollBar().value(), 0)

    def test_scroll_code_to_row_scrolls_to_valid_row(self) -> None:
        model = QStandardItemModel(100, 1)
        self.window.codeTableView.setModel(model)
        self.window.codeTableView.resize(200, 100)
        self.window.codeTableView.show()
        self._application.processEvents()
        self.window.scroll_code_to_row(90)
        self.assertGreater(self.window.codeTableView.verticalScrollBar().value(), 0)

    def test_set_rom_title_without_rom(self) -> None:
        self.window.set_rom_title(None)
        self.assertEqual(self.window.windowTitle(), "CHIP-8 Emulator")

    def test_set_rom_title_with_rom(self) -> None:
        self.window.set_rom_title(Path("/tmp/example.ch8"))
        self.assertEqual( self.window.windowTitle(), "CHIP-8 Emulator - example.ch8")

    def test_update_clock_frequency_label(self) -> None:
        from PyQt6.QtWidgets import QLabel
        self.window.clockFreqLabel = QLabel()
        self.window._update_clock_frequency_label(700)
        self.assertEqual(self.window.clockFreqLabel.text(), "700 Hz")

    def test_selected_code_address_without_model(self) -> None:
        self.assertIsNone(self.window.selected_code_address())

    def test_selected_code_address_without_selection(self) -> None:
        model = CodeTableModel()
        self.window.codeTableView.setModel(model)
        self.assertIsNone(self.window.selected_code_address())

    def test_selected_code_address_with_selection(self) -> None:
        model = CodeTableModel()
        model.set_analysis( SimpleNamespace( row_count=lambda: 1, row=lambda _index: SimpleNamespace(address=0x234)))
        self.window.codeTableView.setModel(model)
        self.window.codeTableView.selectRow(0)
        self.assertEqual(self.window.selected_code_address(), 0x234)

    def test_clear_code_selection(self) -> None:
        model = QStandardItemModel(2, 1)
        self.window.codeTableView.setModel(model)
        self.window.codeTableView.selectRow(0)
        self.window.clear_code_selection()
        self.assertFalse(self.window.codeTableView.selectionModel().hasSelection())

    def test_code_table_double_click_ignores_other_columns(self) -> None:
        self.window._code_model = Mock()
        index = QModelIndex()
        self.window._code_table_double_clicked(index)
        self.window._code_model.address_at_row.assert_not_called()

    def test_code_table_double_click_without_code_model_returns(self) -> None:
        self.window._code_model = None
        index = Mock()
        index.column.return_value = CodeTableModel.Column.BP
        self.window._code_table_double_clicked(index)

    def test_code_table_double_click_emits_breakpoint_address(self) -> None:
        self.window._code_model = Mock()
        self.window._code_model.address_at_row.return_value = 0x456
        emitted: list[int] = []
        self.window.breakpoint_toggled.connect(emitted.append)
        index = Mock()
        index.column.return_value = CodeTableModel.Column.BP
        index.row.return_value = 3
        self.window._code_table_double_clicked(index)
        self.assertEqual(emitted, [0x456])
        self.window._code_model.address_at_row.assert_called_once_with(3)

    def test_code_table_double_click_with_missing_address_does_not_emit(self) -> None:
        self.window._code_model = Mock()
        self.window._code_model.address_at_row.return_value = None
        emitted: list[int] = []
        self.window.breakpoint_toggled.connect(emitted.append)
        index = Mock()
        index.column.return_value = CodeTableModel.Column.BP
        index.row.return_value = 3
        self.window._code_table_double_clicked(index)
        self.assertEqual(emitted, [])

    def test_configure_returns_true_when_dialog_is_accepted(self) -> None:
        self.window._config_dialog = Mock()
        self.window._config_dialog.exec.return_value = QDialog.DialogCode.Accepted
        self.assertTrue(self.window.configure())

    def test_configure_returns_false_when_dialog_is_rejected(self) -> None:
        self.window._config_dialog = Mock()
        self.window._config_dialog.exec.return_value = QDialog.DialogCode.Rejected
        self.assertFalse(self.window.configure())

    def test_assemble_shows_and_activates_dialog(self) -> None:
        self.window._assembler_dialog = Mock()
        self.window.assemble()
        self.window._assembler_dialog.show.assert_called_once()
        self.window._assembler_dialog.raise_.assert_called_once()
        self.window._assembler_dialog.activateWindow.assert_called_once()

    def test_event_filter_ignores_other_widget(self) -> None:
        event = QKeyEvent( QEvent.Type.KeyPress, Qt.Key.Key_C, Qt.KeyboardModifier.ControlModifier)
        self.assertFalse(self.window.eventFilter(QListWidget(), event))

    def test_event_filter_ignores_non_key_event(self) -> None:
        event = QEvent(QEvent.Type.FocusIn)
        self.assertFalse( self.window.eventFilter(self.window.diagnosticsListWidget, event))

    def test_event_filter_ignores_key_press_without_control(self) -> None:
        event = QKeyEvent( QEvent.Type.KeyPress, Qt.Key.Key_C, Qt.KeyboardModifier.NoModifier)
        self.assertFalse( self.window.eventFilter(self.window.diagnosticsListWidget, event))

    def test_event_filter_copies_diagnostics_on_control_c(self) -> None:
        self.window.diagnosticsListWidget.addItems( ["First diagnostic", "Second diagnostic"])
        self.window.diagnosticsListWidget.setSelectionMode( QAbstractItemView.SelectionMode.MultiSelection)
        self.window.diagnosticsListWidget.selectAll()
        selected_items = self.window.diagnosticsListWidget.selectedItems()
        self.assertEqual(len(selected_items), 2)
        event = QKeyEvent( QEvent.Type.KeyPress, Qt.Key.Key_C, Qt.KeyboardModifier.ControlModifier)
        handled = self.window.eventFilter( self.window.diagnosticsListWidget, event)
        self.assertTrue(handled)
        self.assertEqual( QApplication.clipboard().text(), "First diagnostic\nSecond diagnostic")

    def test_copy_selected_diagnostics_without_selection_returns(self) -> None:
        QApplication.clipboard().clear()
        self.window.diagnosticsListWidget.addItem("Unselected diagnostic")
        self.window._copy_selected_diagnostics()
        self.assertEqual(QApplication.clipboard().text(), "")

    def test_show_warning_calls_message_box(self) -> None:
        with patch("gui.mainwindow.QMessageBox.warning") as warning:
            self.window.show_warning("Warning title", "Warning text")
        warning.assert_called_once_with( self.window, "Warning title", "Warning text")

    def test_register_labels_property(self) -> None:
        labels = [object(), object()]
        self.window._register_labels = labels
        self.assertIs(self.window.register_labels, labels)

    def test_config_dialog_property(self) -> None:
        dialog = Mock()
        self.window._config_dialog = dialog
        self.assertIs(self.window.config_dialog, dialog)

    def test_assembler_dialog_property(self) -> None:
        dialog = Mock()
        self.window._assembler_dialog = dialog
        self.assertIs(self.window.assembler_dialog, dialog)


if __name__ == "__main__":
    unittest.main()

