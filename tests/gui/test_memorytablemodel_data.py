"""
@file test_memorytablemodel_data.py

@brief Tests for MemoryTableModel data access and refresh notifications.
"""

from __future__ import annotations

import unittest
from unittest.mock import Mock

from PyQt6.QtCore import QModelIndex, Qt
from PyQt6.QtWidgets import QApplication

from emulator.chip8memory import Chip8Memory
from gui.memorytablemodel import MemoryTableModel


class TestMemoryTableModelData(unittest.TestCase):
    """Tests for MemoryTableModel's table data and update notifications."""

    @classmethod
    def setUpClass(cls) -> None:
        """Create the Qt application required by the model tests."""
        cls._application = QApplication.instance()
        if cls._application is None:
            cls._application = QApplication([])

    def setUp(self) -> None:
        self.model = MemoryTableModel()
        self.memory = Chip8Memory(Mock(), Mock())
        self.model.set_memory(self.memory)
        self.changes: list[tuple[QModelIndex, QModelIndex, list[int]]] = []
        self.model.dataChanged.connect(
            lambda first, last, roles: self.changes.append((first, last, roles))
        )

    def test_row_and_column_counts(self) -> None:
        """The model always exposes 4096 bytes as 256 rows by 16 columns."""
        parent = self.model.index(0, 0)

        self.assertEqual(self.model.rowCount(), 256)
        self.assertEqual(self.model.rowCount(parent), 256)
        self.assertEqual(self.model.columnCount(), 16)
        self.assertEqual(self.model.columnCount(parent), 16)

    def test_data_returns_none_for_invalid_index(self) -> None:
        """An invalid model index has no data."""
        self.assertIsNone(self.model.data(QModelIndex()))

    def test_data_returns_none_before_memory_is_attached(self) -> None:
        """A model without memory cannot provide cell data."""
        model = MemoryTableModel()

        self.assertIsNone(model.data(model.index(0, 0)))

    def test_display_role_returns_two_digit_hexadecimal_byte(self) -> None:
        """Memory bytes are displayed as two-digit uppercase hexadecimal."""
        self.memory.write_byte(0xABC, 0xE7)

        self.assertEqual(
            self.model.data(self.model.index(0xABC // 16, 0xABC % 16)),
            "E7",
        )

    def test_background_role_returns_brush_for_highlighted_address(self) -> None:
        """The highlighted memory cell receives the configured background."""
        self.model._set_highlight(0x123, 0x123)
        brush = self.model.data(
            self.model.index(0x123 // 16, 0x123 % 16),
            Qt.ItemDataRole.BackgroundRole,
        )

        self.assertIsNotNone(brush)
        self.assertEqual(brush.color().getRgb(), (255, 255, 160, 255))

    def test_background_role_returns_none_outside_highlight(self) -> None:
        """Cells outside the highlighted range have no custom background."""
        self.model._set_highlight(0x123, 0x123)

        self.assertIsNone(
            self.model.data(
                self.model.index(0x124 // 16, 0x124 % 16),
                Qt.ItemDataRole.BackgroundRole,
            )
        )

    def test_header_data_formats_columns_and_row_addresses(self) -> None:
        """Horizontal headers show columns and vertical headers show addresses."""
        self.assertEqual(
            self.model.headerData(10, Qt.Orientation.Horizontal),
            "0A",
        )
        self.assertEqual(
            self.model.headerData(18, Qt.Orientation.Vertical),
            "120",
        )
        self.assertIsNone(
            self.model.headerData(
                0,
                Qt.Orientation.Horizontal,
                Qt.ItemDataRole.ToolTipRole,
            )
        )

    def test_flags_are_enabled_and_selectable(self) -> None:
        """Memory cells are selectable but not editable."""
        flags = self.model.flags(self.model.index(0, 0))

        self.assertEqual(
            flags,
            Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable,
        )

    def test_refresh_all_emits_one_full_memory_display_update(self) -> None:
        """Refreshing all memory notifies views about the complete table."""
        self.model.refresh_all()

        self.assertEqual(len(self.changes), 1)
        first, last, roles = self.changes[0]
        self.assertEqual((first.row(), first.column()), (0, 0))
        self.assertEqual((last.row(), last.column()), (255, 15))
        self.assertEqual(roles, [Qt.ItemDataRole.DisplayRole])

    def test_refresh_all_without_memory_emits_no_update(self) -> None:
        """Refreshing an unattached model does not emit dataChanged."""
        model = MemoryTableModel()
        changes: list[tuple[QModelIndex, QModelIndex, list[int]]] = []
        model.dataChanged.connect(
            lambda first, last, roles: changes.append((first, last, roles))
        )

        model.refresh_all()

        self.assertEqual(changes, [])

    def test_refresh_address_emits_background_and_display_updates(self) -> None:
        """Refreshing one address updates its highlight and displayed byte."""
        self.model.refresh_address(0x123)

        self.assertEqual(len(self.changes), 2)
        for first, last, _roles in self.changes:
            self.assertEqual((first.row(), first.column()), (0x12, 3))
            self.assertEqual((last.row(), last.column()), (0x12, 3))
        self.assertEqual(
            self.changes[0][2],
            [Qt.ItemDataRole.BackgroundRole],
        )
        self.assertEqual(
            self.changes[1][2],
            [Qt.ItemDataRole.DisplayRole],
        )

    def test_refresh_range_within_one_row_emits_one_display_update(self) -> None:
        """A range contained in one row is refreshed with one display span."""
        self.model.refresh_range(0x123, 0x127)

        display_change = self.changes[-1]
        self.assertEqual(
            (display_change[0].row(), display_change[0].column()),
            (0x12, 3),
        )
        self.assertEqual(
            (display_change[1].row(), display_change[1].column()),
            (0x12, 7),
        )
        self.assertEqual(display_change[2], [Qt.ItemDataRole.DisplayRole])

    def test_refresh_range_across_multiple_rows_emits_partial_and_full_rows(self) -> None:
        """A multi-row range refreshes its first, middle, and last row spans."""
        self.model.refresh_range(0x01E, 0x032)

        display_changes = [
            change
            for change in self.changes
            if change[2] == [Qt.ItemDataRole.DisplayRole]
        ]
        self.assertEqual(len(display_changes), 3)
        self.assertEqual(
            [
                (
                    (first.row(), first.column()),
                    (last.row(), last.column()),
                )
                for first, last, _roles in display_changes
            ],
            [((1, 14), (1, 15)), ((2, 0), (2, 15)), ((3, 0), (3, 2))],
        )

    def test_replacing_highlight_notifies_old_and_new_ranges(self) -> None:
        """Changing the highlight repaints both the old and new cells."""
        self.model.refresh_address(0x123)
        self.changes.clear()

        self.model.refresh_address(0x245)

        background_changes = [
            change
            for change in self.changes
            if change[2] == [Qt.ItemDataRole.BackgroundRole]
        ]
        self.assertEqual(len(background_changes), 2)
        self.assertEqual(
            (background_changes[0][0].row(), background_changes[0][0].column()),
            (0x12, 3),
        )
        self.assertEqual(
            (background_changes[1][0].row(), background_changes[1][0].column()),
            (0x24, 5),
        )

    def test_clearing_highlight_repaints_previous_range(self) -> None:
        """Clearing a highlight notifies the view to remove its background."""
        self.model.refresh_address(0x123)
        self.changes.clear()

        self.model.clear_highlight()

        self.assertEqual(len(self.changes), 1)
        first, last, roles = self.changes[0]
        self.assertEqual((first.row(), first.column()), (0x12, 3))
        self.assertEqual((last.row(), last.column()), (0x12, 3))
        self.assertEqual(roles, [Qt.ItemDataRole.BackgroundRole])

    def test_background_refresh_across_multiple_rows_emits_each_row_span(self) -> None:
        """A multi-row highlight repaint emits first, middle, and last spans."""
        self.model._set_highlight(0x01E, 0x032)

        self.assertEqual(len(self.changes), 3)
        self.assertEqual(
            [
                (
                    (first.row(), first.column()),
                    (last.row(), last.column()),
                )
                for first, last, _roles in self.changes
            ],
            [((1, 14), (1, 15)), ((2, 0), (2, 15)), ((3, 0), (3, 2))],
        )
        self.assertTrue(
            all(roles == [Qt.ItemDataRole.BackgroundRole] for _, _, roles in self.changes)
        )


if __name__ == "__main__":
    unittest.main()
