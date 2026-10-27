"""Tests for CodeTableModel logic without creating a Qt GUI."""

from __future__ import annotations

import importlib
import sys
import types
import unittest
from enum import IntEnum
from unittest.mock import Mock


class _ItemDataRole(IntEnum):
    DisplayRole = 0
    BackgroundRole = 8


class _Orientation(IntEnum):
    Horizontal = 1
    Vertical = 2


class _ItemFlag(IntEnum):
    ItemIsEnabled = 1
    ItemIsSelectable = 2


class _QSettings:
    def value(self, key: str, default: object = None) -> object:
        del key
        return default

    def setValue(self, key: str, value: object) -> None:
        del key, value


class _Qt:
    ItemDataRole = _ItemDataRole
    Orientation = _Orientation
    ItemFlag = _ItemFlag


class _QModelIndex:
    def __init__(self, row: int = -1, column: int = -1, valid: bool | None = None) -> None:
        self._row = row
        self._column = column
        self._valid = (row >= 0 and column >= 0) if valid is None else valid

    def isValid(self) -> bool:
        return self._valid

    def row(self) -> int:
        return self._row

    def column(self) -> int:
        return self._column


class _Signal:
    def __init__(self) -> None:
        self.emissions: list[tuple[object, ...]] = []

    def emit(self, *args: object) -> None:
        self.emissions.append(args)


class _QAbstractTableModel:
    def __init__(self) -> None:
        self.dataChanged = _Signal()
        self.reset_started = 0
        self.reset_ended = 0

    def index(self, row: int, column: int) -> _QModelIndex:
        return _QModelIndex(row, column)

    def beginResetModel(self) -> None:
        self.reset_started += 1

    def endResetModel(self) -> None:
        self.reset_ended += 1


class _QColor:
    def __init__(self, red: int, green: int, blue: int) -> None:
        self.rgb = (red, green, blue)


class _QBrush:
    def __init__(self, color: _QColor) -> None:
        self.color = color


def _load_model_module():
    """Import the model against small Qt value/model doubles, not a GUI."""
    qtcore = types.ModuleType("PyQt6.QtCore")
    qtcore.QAbstractTableModel = _QAbstractTableModel
    qtcore.QSettings = _QSettings
    qtcore.QModelIndex = _QModelIndex
    qtcore.Qt = _Qt

    qtgui = types.ModuleType("PyQt6.QtGui")
    qtgui.QBrush = _QBrush
    qtgui.QColor = _QColor

    pyqt = types.ModuleType("PyQt6")
    pyqt.__path__ = []
    pyqt.QtCore = qtcore
    pyqt.QtGui = qtgui

    names = ("PyQt6", "PyQt6.QtCore", "PyQt6.QtGui", "gui.codetablemodel")
    previous = {name: sys.modules.get(name) for name in names}
    try:
        sys.modules["PyQt6"] = pyqt
        sys.modules["PyQt6.QtCore"] = qtcore
        sys.modules["PyQt6.QtGui"] = qtgui
        sys.modules.pop("gui.codetablemodel", None)
        model_module = importlib.import_module("gui.codetablemodel")
        sys.modules.pop("gui.codetablemodel", None)
        return model_module
    finally:
        for name, module in previous.items():
            if module is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = module


_model_module = _load_model_module()
CodeTableModel = _model_module.CodeTableModel


class _Status:
    def __init__(self, value: str) -> None:
        self.value = value


class _Row:
    def __init__(self, address: int, raw_bytes: bytes = b"\x60\x01", interpretation: str = "LD V0, 1", status: str = "Code") -> None:
        self.address = address
        self.raw_bytes = raw_bytes
        self.interpretation = interpretation
        self.status = _Status(status)


class _Analysis:
    def __init__(self, rows: list[_Row]) -> None:
        self.rows = rows

    def row_count(self) -> int:
        return len(self.rows)

    def row(self, index: int) -> _Row:
        return self.rows[index]

    def find_row(self, address: int) -> int | None:
        return next((i for i, row in enumerate(self.rows) if row.address == address), None)


class TestCodeTableModelNonQt(unittest.TestCase):
    def setUp(self) -> None:
        self.model = CodeTableModel()
        self.analysis = _Analysis([_Row(0x200), _Row(0x202, b"\x12\x00", "JP 200", "Unknown")])

    def test_empty_model_counts_and_addresses(self) -> None:
        self.assertEqual(self.model.rowCount(), 0)
        self.assertEqual(self.model.columnCount(), 5)
        self.assertIsNone(self.model.address_at_row(0))
        self.assertIsNone(self.model.address(0))
        self.assertIsNone(self.model.data(_QModelIndex(0, 0)))

    def test_attach_analysis_and_get_row_addresses(self) -> None:
        self.model.set_analysis(self.analysis)
        self.assertEqual(self.model.rowCount(), 2)
        self.assertEqual(self.model.address_at_row(0), 0x200)
        self.assertEqual(self.model.address(1), 0x202)
        self.assertIsNone(self.model.address_at_row(-1))
        self.assertIsNone(self.model.address_at_row(2))
        self.assertIsNone(self.model.address(-1))
        self.assertIsNone(self.model.address(2))

    def test_row_and_column_count_ignore_parent(self) -> None:
        self.model.set_analysis(self.analysis)
        parent = _QModelIndex(0, 0)
        self.assertEqual(self.model.rowCount(parent), 2)
        self.assertEqual(self.model.columnCount(parent), 5)

    def test_display_values_for_non_breakpoint_columns(self) -> None:
        self.model.set_analysis(self.analysis)
        self.assertEqual(self.model.data(_QModelIndex(0, 1)), "0200")
        self.assertEqual(self.model.data(_QModelIndex(0, 2)), "60 01")
        self.assertEqual(self.model.data(_QModelIndex(0, 3)), "LD V0, 1")
        self.assertEqual(self.model.data(_QModelIndex(1, 4)), "Unknown")
        self.assertIsNone(self.model.data(_QModelIndex(0, 1), 99))
        self.assertIsNone(self.model.data(_QModelIndex(0, 99)))
        self.assertIsNone(self.model.data(_QModelIndex(valid=False)))

    def test_breakpoint_column_without_debugger_is_empty(self) -> None:
        self.model.set_analysis(self.analysis)
        self.assertEqual(self.model.data(_QModelIndex(0, 0)), "")

    def test_breakpoint_column_displays_temporary_enabled_disabled_and_none(self) -> None:
        self.model.set_analysis(self.analysis)
        debugger = Mock()
        debugger.temporary_breakpoint = 0x200
        debugger.is_breakpoint_enabled.return_value = True
        debugger.is_breakpoint_disabled.return_value = True
        self.model.set_debugger(debugger)
        self.assertEqual(self.model.data(_QModelIndex(0, 0)), "►")

        debugger.temporary_breakpoint = None
        self.assertEqual(self.model.data(_QModelIndex(0, 0)), "●")
        debugger.is_breakpoint_enabled.return_value = False
        self.assertEqual(self.model.data(_QModelIndex(0, 0)), "○")
        debugger.is_breakpoint_disabled.return_value = False
        self.assertEqual(self.model.data(_QModelIndex(0, 0)), "")

    def test_current_pc_highlights_matching_row(self) -> None:
        self.model.set_analysis(self.analysis)
        self.model.set_current_pc(0x200)
        brush = self.model.data(_QModelIndex(0, 0), _ItemDataRole.BackgroundRole)
        self.assertIsInstance(brush, _QBrush)
        self.assertEqual(brush.color.rgb, (255, 255, 160))
        self.assertIsNone(self.model.data(_QModelIndex(1, 0), _ItemDataRole.BackgroundRole))

    def test_setting_same_pc_does_not_emit_refresh(self) -> None:
        self.model.set_analysis(self.analysis)
        self.model.set_current_pc(0x200)
        self.model.dataChanged.emissions.clear()
        self.model.set_current_pc(0x200)
        self.assertEqual(self.model.dataChanged.emissions, [])

    def test_changing_pc_refreshes_previous_and_current_rows(self) -> None:
        self.model.set_analysis(self.analysis)
        self.model.set_current_pc(0x200)
        self.model.dataChanged.emissions.clear()
        self.model.set_current_pc(0x202)
        self.assertEqual(len(self.model.dataChanged.emissions), 2)
        self.assertEqual(self.model.dataChanged.emissions[0][0].row(), 0)
        self.assertEqual(self.model.dataChanged.emissions[1][0].row(), 1)

    def test_refresh_address_ignores_missing_analysis_or_address(self) -> None:
        self.model.refresh_address(0x200)
        self.model.set_analysis(self.analysis)
        self.model.refresh_address(0x999)
        self.assertEqual(self.model.dataChanged.emissions, [])

    def test_refresh_address_emits_display_role_for_full_row(self) -> None:
        self.model.set_analysis(self.analysis)
        self.model.refresh_address(0x202)
        top_left, bottom_right, roles = self.model.dataChanged.emissions[0]
        self.assertEqual((top_left.row(), top_left.column()), (1, 0))
        self.assertEqual((bottom_right.row(), bottom_right.column()), (1, 4))
        self.assertEqual(roles, [_ItemDataRole.DisplayRole])

    def test_refresh_resets_model(self) -> None:
        self.model.refresh()
        self.assertEqual(self.model.reset_started, 1)
        self.assertEqual(self.model.reset_ended, 1)

    def test_header_data_horizontal_vertical_and_other_role(self) -> None:
        self.assertEqual(self.model.headerData(0, _Orientation.Horizontal), "BP")
        self.assertEqual(self.model.headerData(4, _Orientation.Horizontal), "Status")
        self.assertEqual(self.model.headerData(3, _Orientation.Vertical), 3)
        self.assertIsNone(self.model.headerData(0, _Orientation.Horizontal, 99))

    def test_flags_are_enabled_and_selectable(self) -> None:
        flags = self.model.flags(_QModelIndex(0, 0))
        self.assertEqual(flags, _ItemFlag.ItemIsEnabled | _ItemFlag.ItemIsSelectable)


if __name__ == "__main__":
    unittest.main()
