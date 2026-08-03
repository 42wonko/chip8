"""
@file memorytablemodel.py

@brief Qt model that exposes the CHIP-8 memory.

@details
The model presents the complete 4096-byte CHIP-8 memory as a read-only
16-column hexadecimal table.

Rows correspond to 16-byte blocks.
Columns correspond to the byte offset inside the block.
The model never owns the memory. It only keeps a reference to the
emulator memory object.

@author
Michael Dlubatz

@copyright
MIT License
"""

from __future__ import annotations

from typing import Any

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt, pyqtSignal
from PyQt6.QtGui import QBrush, QColor

from emulator.chip8memory import Chip8Memory


class MemoryTableModel(QAbstractTableModel):
    """
    @brief Read-only model for the CHIP-8 memory.
    """


    scroll_to_address = pyqtSignal(int)


    def __init__(self) -> None:
        """
        @brief Construct an empty model.
        """
        super().__init__()
        self._memory: Chip8Memory | None = None
        self._highlight_start: int | None = None
        self._highlight_end: int | None = None


    ###########################################################################
    # Public interface
    ###########################################################################
    def set_memory(self, memory: Chip8Memory) -> None:
        """
        @brief Attach emulator memory.

        @param memory
            Memory object owned by the emulator.
        """
        self.beginResetModel()
        self._memory = memory
        self.endResetModel()


    def clear_highlight(self) -> None:
        """
        @brief Remove the current memory highlight.
        """
        self._set_highlight(None, None)


    def refresh_all(self) -> None:
        """
        @brief Notify Qt that the displayed memory changed.
        """
        if self._memory is None:
            return

        top_left = self.index(0, 0)
        bottom_right = self.index(255, 15)
        self.dataChanged.emit( top_left, bottom_right, [Qt.ItemDataRole.DisplayRole])


    def refresh_address( self, address: int) -> None:
        """
        @brief Refresh a single memory cell.

        @param address
            CHIP-8 memory address.
        """
        self._set_highlight(address, address)
        row = address // 16
        column = address % 16
        index = self.index(row, column)
        self.dataChanged.emit( index, index, [Qt.ItemDataRole.DisplayRole])

    def refresh_range(self, first: int, last: int) -> None:
        """
        @brief Refresh a contiguous address range.

        @param first
            First address (inclusive).

        @param last
            Last address (inclusive).
        """
        self._set_highlight(first, last)
        first_row = first // 16
        last_row = last // 16

        # Entire range fits into one row.
        if first_row == last_row:
            self.dataChanged.emit(
                self.index(first_row, first % 16), self.index(last_row, last % 16), [Qt.ItemDataRole.DisplayRole])
            return

        # First partial row.
        self.dataChanged.emit( self.index(first_row, first % 16), self.index(first_row, 15), [Qt.ItemDataRole.DisplayRole])

        # Complete rows.
        for row in range(first_row + 1, last_row):
            self.dataChanged.emit( self.index(row, 0), self.index(row, 15), [Qt.ItemDataRole.DisplayRole])

        # Last partial row.
        self.dataChanged.emit( self.index(last_row, 0), self.index(last_row, last % 16), [Qt.ItemDataRole.DisplayRole])


    ###########################################################################
    # QAbstractTableModel implementation
    ###########################################################################
    def rowCount( self, parent: QModelIndex = QModelIndex()) -> int:
        del parent
        return 256


    def columnCount( self, parent: QModelIndex = QModelIndex()) -> int:
        del parent
        return 16


    def data( self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole,) -> Any:
        """
        @brief Return the contents and appearance of a memory cell.
        """
        if self._memory is None or not index.isValid():
            return None
        address = index.row() * 16 + index.column()
        if role == Qt.ItemDataRole.DisplayRole:
            return f"{self._memory[address]:02X}"
#        if ( role == Qt.ItemDataRole.BackgroundRole and self._highlight_start is not None and self._highlight_start <= address <= self._highlight_end):
        if role == Qt.ItemDataRole.BackgroundRole:
            if (
                self._highlight_start is not None
                and self._highlight_end is not None
                and self._highlight_start <= address <= self._highlight_end
            ):
                return QBrush(QColor(255, 255, 160))
        return None


    def headerData( self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            return f"{section:02X}"
        return f"{section * 16:03X}"

    def flags( self, index: QModelIndex,) -> Qt.ItemFlag:
        del index
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable



    ###########################################################################
    # Private helpers
    ###########################################################################
    def _set_highlight( self, first: int | None, last: int | None,) -> None:
        """
        @brief Change the highlighted memory range.

        The previous highlighted range is repainted before the new
        highlight becomes active.
        """
        old_start = self._highlight_start                                               # remember previous high light
        if ( self._highlight_start is not None and self._highlight_end is not None):    # Repaint the old highlight.
            self._emit_background_changed( self._highlight_start, self._highlight_end)

        self._highlight_start = first
        self._highlight_end = last

        # Paint the new highlight.
        if ( self._highlight_start is not None and self._highlight_end is not None):
            self._emit_background_changed( self._highlight_start, self._highlight_end)
        if first is not None and first != old_start:                                    # only scroll if we actually have to move
            self.scroll_to_address.emit(first)


    def _emit_background_changed( self, first: int, last: int,) -> None:
        """
        @brief Notify Qt that only the background has changed.
        """

        first_row = first // 16
        last_row = last // 16

        if first_row == last_row:
            self.dataChanged.emit( self.index(first_row, first % 16), self.index(last_row, last % 16), [Qt.ItemDataRole.BackgroundRole])
            return

        self.dataChanged.emit( self.index(first_row, first % 16), self.index(first_row, 15), [Qt.ItemDataRole.BackgroundRole],)

        for row in range(first_row + 1, last_row):
            self.dataChanged.emit( self.index(row, 0), self.index(row, 15), [Qt.ItemDataRole.BackgroundRole],)

        self.dataChanged.emit( self.index(last_row, 0), self.index(last_row, last % 16), [Qt.ItemDataRole.BackgroundRole],)
