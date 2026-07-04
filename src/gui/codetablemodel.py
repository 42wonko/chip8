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

from typing import Any

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt

from controller.codeanalysis import CodeAnalysis


class CodeTableModel(QAbstractTableModel):
    """
    @brief Read-only model for the Code View.
    """

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


    ###########################################################################
    # QAbstractTableModel implementation
    ###########################################################################
    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        del parent
        return 0

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        del parent
        return len(self.HEADERS)

    def data( self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        del index
        del role
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
