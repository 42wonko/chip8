"""Tests for non-GUI helper functions in gui.configdialog."""

import importlib
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch


def load_helpers():
    source_root = Path(__file__).resolve().parent / "src"
    if not source_root.is_dir():
        source_root = Path(__file__).resolve().parents[1] / "src"
    if str(source_root) not in sys.path:
        sys.path.insert(0, str(source_root))

    pyqt = types.ModuleType("PyQt6")
    core = types.ModuleType("PyQt6.QtCore")
    widgets = types.ModuleType("PyQt6.QtWidgets")
    uic = types.ModuleType("PyQt6.uic")

    class QDialog:
        pass

    class QWidget:
        pass

    class QFileDialog:
        pass

    class QMessageBox:
        pass

    class QSettings:
        pass

    core.QSettings = QSettings
    core.pyqtSignal = lambda *_args, **_kwargs: object()
    widgets.QDialog = QDialog
    widgets.QWidget = QWidget
    widgets.QFileDialog = QFileDialog
    widgets.QMessageBox = QMessageBox
    uic.loadUi = lambda *_args, **_kwargs: None
    pyqt.QtCore = core
    pyqt.QtWidgets = widgets
    pyqt.uic = uic

    with patch.dict(sys.modules, {
        "PyQt6": pyqt,
        "PyQt6.QtCore": core,
        "PyQt6.QtWidgets": widgets,
        "PyQt6.uic": uic
    }):
        configdialog = importlib.import_module("gui.configdialog")
        trace_level = importlib.import_module(
            "controller.emulatorconfiguration"
        ).TraceLevel
    return configdialog, trace_level


class ConfigDialogHelperTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.configdialog, cls.trace_level = load_helpers()

    def test_trace_level_to_index_basic(self):
        self.assertEqual(
            self.configdialog.trace_level_to_index(self.trace_level.BASIC), 0
        )

    def test_trace_level_to_index_changes(self):
        self.assertEqual(
            self.configdialog.trace_level_to_index(self.trace_level.CHANGES), 1
        )

    def test_trace_level_to_index_full(self):
        self.assertEqual(
            self.configdialog.trace_level_to_index(self.trace_level.FULL), 2
        )

    def test_index_to_trace_level_basic(self):
        self.assertEqual(
            self.configdialog.index_to_trace_level(0), self.trace_level.BASIC
        )

    def test_index_to_trace_level_changes(self):
        self.assertEqual(
            self.configdialog.index_to_trace_level(1), self.trace_level.CHANGES
        )

    def test_index_to_trace_level_full(self):
        self.assertEqual(
            self.configdialog.index_to_trace_level(2), self.trace_level.FULL
        )

    def test_negative_index_returns_full(self):
        self.assertEqual(
            self.configdialog.index_to_trace_level(-1), self.trace_level.FULL
        )

    def test_index_above_range_raises_index_error(self):
        with self.assertRaises(IndexError):
            self.configdialog.index_to_trace_level(3)

    def test_unknown_trace_level_raises_key_error(self):
        with self.assertRaises(KeyError):
            self.configdialog.trace_level_to_index(99)


if __name__ == "__main__":
    unittest.main()
