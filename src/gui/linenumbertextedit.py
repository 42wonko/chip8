"""
@file linenumbertextedit.py

@brief QPlainTextEdit with a line-number gutter.
"""

from __future__ import annotations

from PyQt6.QtCore import QRect, QSize, Qt
from PyQt6.QtGui import QPainter, QPaintEvent, QResizeEvent
from PyQt6.QtWidgets import QPlainTextEdit, QWidget


class LineNumberTextEdit(QPlainTextEdit):
    """
    @brief Plain-text editor with a line-number gutter.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._line_number_area = LineNumberArea(self)

        self.blockCountChanged.connect(
            self._update_line_number_area_width
        )
        self.updateRequest.connect(
            self._update_line_number_area
        )

        self._update_line_number_area_width(0)

    def _line_number_area_width(self, _: int = 0) -> int:
        """
        @brief Return the width required for the line-number gutter.
        """
        digits = len(str(max(1, self.blockCount())))
        return 8 + self.fontMetrics().horizontalAdvance("9") * digits

    def _update_line_number_area_width(self, _: int) -> None:
        """
        @brief Update the viewport margin for the line-number gutter.
        """
        self.setViewportMargins( self._line_number_area_width(), 0, 0, 0)

    def _update_line_number_area( self, rect: QRect, dy: int) -> None:
        """
        @brief Update the visible line-number gutter.
        """
        if dy:
            self._line_number_area.scroll(0, dy)
        else:
            self._line_number_area.update( 0, rect.y(), self._line_number_area.width(), rect.height())
        viewport = self.viewport()
        if viewport is not None and rect.contains(viewport.rect()):
            self._update_line_number_area_width(0)
#    if rect.contains(self.viewport().rect()):
#            self._update_line_number_area_width(0)

    def resizeEvent(self, event: QResizeEvent | None) -> None:
        """
        @brief Resize the line-number gutter.
        """
        super().resizeEvent(event)
        rect = self.contentsRect()
        self._line_number_area.setGeometry(
            QRect( rect.left(), rect.top(), self._line_number_area_width(), rect.height())
        )

    def _paint_line_numbers( self, painter: QPainter, rect: QRect) -> None:
        """
        @brief Paint line numbers for visible text blocks.
        """
        painter.fillRect( rect, self.palette().alternateBase())
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int( self.blockBoundingGeometry(block) .translated(self.contentOffset()) .top())
        bottom = top + int( self.blockBoundingRect(block).height())
        while block.isValid() and top <= rect.bottom():
            if block.isVisible() and bottom >= rect.top():
                painter.drawText(
                    0,
                    top,
                    self._line_number_area.width() - 4,
                    self.fontMetrics().height(),
                    Qt.AlignmentFlag.AlignRight,
                    str(block_number + 1)
                )

            block = block.next()
            block_number += 1
            top = bottom
            bottom = top + int( self.blockBoundingRect(block).height())


class LineNumberArea(QWidget):
    """
    @brief Widget containing the line-number gutter.
    """

    def __init__(self, editor: LineNumberTextEdit) -> None:
        super().__init__(editor)
        self._editor = editor

    def sizeHint(self) -> QSize:
        """
        @brief Return the preferred gutter size.
        """
        return QSize( self._editor._line_number_area_width(), 0)

    def paintEvent(self, event: QPaintEvent | None) -> None:
        """
        @brief Paint the line numbers.
        """
        if event is None:
            return
        painter = QPainter(self)
        self._editor._paint_line_numbers( painter, event.rect())
