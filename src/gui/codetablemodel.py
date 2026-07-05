"""
@file codetablemodel.py

@brief Qt model for the Code View.

@details
This model presents the output of the Code Analysis subsystem.

@author
Michael Dlubatz

@copyright
MIT License
"""

from __future__ import annotations

from enum import IntEnum
from typing import Any

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt

from controller.codeanalysis import CodeAnalysis


class CodeTableModel(QAbstractTableModel):
    """
    @brief Read-only model for the Code View.
    """

    """
    @brief Enumeration for the columns of the code analysis view.
    """
    class Column(IntEnum):
        BP = 0
        ADDR = 1
        BYTES = 2
        INTERPRETATION = 3
        STATUS = 4

    HEADERS = ( "BP", "Addr", "Bytes", "Interpretation", "Status")

    def __init__(self) -> None:
        """
        @brief Construct an empty model.
        """
        super().__init__()
        self._analysis: CodeAnalysis | None = None


    ###########################################################################
    # Public interface
    ###########################################################################
    def set_analysis(self, analysis: CodeAnalysis) -> None:
        """
        @brief Attach the Code Analysis subsystem.

        @param analysis
            Code Analysis instance.
        """
        self._analysis = analysis


    def refresh(self) -> None:
        """
        @brief Refresh the complete model.

        Notify Qt that the underlying Code Analysis has been rebuilt.
        The complete model is reset. Future versions may provide
        more fine-grained update operations.
        """
        self.beginResetModel()
        self.endResetModel()


    ###########################################################################
    # QAbstractTableModel implementation
    ###########################################################################
    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        del parent
        if self._analysis is None:
            return 0
        return self._analysis.row_count()


    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        del parent
        return len(self.HEADERS)


    def data( self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if ( self._analysis is None or not index.isValid() or role != Qt.ItemDataRole.DisplayRole):
            return None
        row = self._analysis.row(index.row())
        match index.column():
            case self.Column.BP:
                return ""
            case self.Column.ADDR:
                return f"{row.address:04X}"
            case self.Column.BYTES:
                return " ".join(f"{b:02X}" for b in row.raw_bytes)
            case self.Column.INTERPRETATION:
                return row.interpretation
            case self.Column.STATUS:
                return row.status.value
        return None


    def headerData( self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            return self.HEADERS[section]
        return section


    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        del index
        return ( Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)

