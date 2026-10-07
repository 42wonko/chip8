"""
@file test_mainwindow.py

@brief Tests for the main application window.
"""

from __future__ import annotations

import unittest

from PyQt6.QtWidgets import QApplication, QMainWindow, QTableView

from gui.codetablemodel import CodeTableModel
from gui.mainwindow import MainWindow
from gui.memorytablemodel import MemoryTableModel


class TrackingTableView(QTableView):
    """
    @brief QTableView that records column-resize requests.
    """

    def __init__(self) -> None:
        super().__init__()
        self.resize_columns_count = 0

    def resizeColumnsToContents(self) -> None:
        """
        @brief Record a request to resize the columns.
        """
        self.resize_columns_count += 1


class TestMainWindow(unittest.TestCase):
    """
    @brief Tests for MainWindow.
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        @brief Create the Qt application required by the tests.
        """
        cls._application = QApplication.instance()
        if cls._application is None:
            cls._application = QApplication([])

    def setUp(self) -> None:
        """
        @brief Create a minimal MainWindow for testing the table-model methods.
        """
        self.window = MainWindow.__new__(MainWindow)
        QMainWindow.__init__(self.window)

        self.memory_table = TrackingTableView()
        self.code_table = TrackingTableView()

        self.window.memoryTableView = self.memory_table
        self.window.codeTableView = self.code_table

    def tearDown(self) -> None:
        """
        @brief Destroy the test window.
        """
        self.window.close()
        self.window.deleteLater()

    def test_set_memory_model_resizes_columns_when_model_is_reset(self) -> None:
        """
        @brief Verify that a memory-model reset resizes the memory columns.
        """
        model = MemoryTableModel()

        self.window.set_memory_model(model)

        initial_count = self.memory_table.resize_columns_count
        self.assertEqual(initial_count, 1)

        model.beginResetModel()
        model.endResetModel()

        self.assertEqual(
            self.memory_table.resize_columns_count,
            initial_count + 1,
        )

    def test_set_code_model_resizes_columns_when_model_is_reset(self) -> None:
        """
        @brief Verify that a code-model reset resizes the code columns.
        """
        model = CodeTableModel()

        self.window.set_code_model(model)

        initial_count = self.code_table.resize_columns_count
        self.assertEqual(initial_count, 1)

        model.beginResetModel()
        model.endResetModel()

        self.assertEqual(
            self.code_table.resize_columns_count,
            initial_count + 1,
        )

    def test_memory_model_data_change_does_not_resize_columns(self) -> None:
        """
        @brief Verify that ordinary memory updates do not resize columns.
        """
        model = MemoryTableModel()

        self.window.set_memory_model(model)
        initial_count = self.memory_table.resize_columns_count

        model.dataChanged.emit(
            model.index(0, 0),
            model.index(0, 0),
        )

        self.assertEqual(
            self.memory_table.resize_columns_count,
            initial_count,
        )

    def test_code_model_data_change_does_not_resize_columns(self) -> None:
        """
        @brief Verify that ordinary code-view updates do not resize columns.
        """
        model = CodeTableModel()

        self.window.set_code_model(model)
        initial_count = self.code_table.resize_columns_count

        model.dataChanged.emit(
            model.index(0, 0),
            model.index(0, model.columnCount() - 1),
        )

        self.assertEqual(
            self.code_table.resize_columns_count,
            initial_count,
        )


if __name__ == "__main__":
    unittest.main()

