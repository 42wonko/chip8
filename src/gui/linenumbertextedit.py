"""
@file linenumbertextedit.py

@brief QPlainTextEdit with a line-number gutter.
"""
from __future__ import annotations

from PyQt6.QtCore import QRect, QSize, Qt
from PyQt6.QtGui import QKeyEvent, QPainter, QPaintEvent, QResizeEvent, QTextCursor
from PyQt6.QtWidgets import QPlainTextEdit, QWidget

from emulator.constants import (
    ASSEMBLER_EDITOR_LINE_NUMBER_LEFT_MARGIN,
    ASSEMBLER_EDITOR_LINE_NUMBER_RIGHT_MARGIN,
    ASSEMBLER_EDITOR_TAB_SIZE,
    ASSEMBLER_EDITOR_VI_DEFAULT_MODE,
    ASSEMBLER_EDITOR_VI_INSERT_MODE,
    ASSEMBLER_EDITOR_VI_KEYS,
    ASSEMBLER_EDITOR_VI_NORMAL_MODE,
)


class LineNumberTextEdit(QPlainTextEdit):
    """
    @brief Plain-text editor with a line-number gutter and classic vi editing.

    The editor supports two modes:

    - normal mode: vi-style navigation and editing commands
    - insert mode: normal QPlainTextEdit text entry
    """

    def __init__( self, parent: QWidget | None = None, tab_size: int = ASSEMBLER_EDITOR_TAB_SIZE,) -> None:
        super().__init__(parent)
        if tab_size <= 0:
            raise ValueError("Tab size must be greater than zero.")
        self._tab_size = tab_size
        self._vi_mode = ASSEMBLER_EDITOR_VI_DEFAULT_MODE
        self._vi_pending_key: str | None = None
        self._vi_yank_buffer = ""
        self._line_number_area = LineNumberArea(self)
        self.blockCountChanged.connect( self._update_line_number_area_width)
        self.updateRequest.connect( self._update_line_number_area)
        self._update_line_number_area_width(0)
        self._update_tab_stop()

    @property
    def vi_mode(self) -> str:
        """
        @brief Return the current vi editing mode.
        """
        return self._vi_mode

    def _enter_insert_mode(self, append: bool = False) -> None:
        """
        @brief Enter insert mode.

        @param append If True, move one character to the right before
                      entering insert mode.
        """
        if append:
            cursor = self.textCursor()
            if not cursor.atBlockEnd():
                cursor.movePosition(QTextCursor.MoveOperation.Right)
                self.setTextCursor(cursor)
        self._vi_pending_key = None
        self._vi_mode = ASSEMBLER_EDITOR_VI_INSERT_MODE

    def _enter_normal_mode(self) -> None:
        """
        @brief Enter normal mode and cancel any pending multi-key command.
        """
        self._vi_pending_key = None
        self._vi_mode = ASSEMBLER_EDITOR_VI_NORMAL_MODE

    def keyPressEvent(self, event: QKeyEvent | None) -> None:
        """
        @brief Handle keyboard input according to the current editor mode.
        """
        if event is None:
            return
        if self._vi_mode == ASSEMBLER_EDITOR_VI_INSERT_MODE:
            if event.key() == Qt.Key.Key_Escape:
                self._enter_normal_mode()
                return
            super().keyPressEvent(event)
            return
        self._handle_normal_mode_key(event)

    def _handle_normal_mode_key(self, event: QKeyEvent) -> None:
        """
        @brief Handle one key press while in normal mode.
        """
        if event.key() == Qt.Key.Key_Escape:
            self._vi_pending_key = None
            return

        if ( event.key() == Qt.Key.Key_R and event.modifiers() == Qt.KeyboardModifier.ControlModifier):
            self.redo()
            self._vi_pending_key = None
            return
        elif event.key() == Qt.Key.Key_Left:
            self._move_cursor(QTextCursor.MoveOperation.Left)
            return
        elif event.key() == Qt.Key.Key_Right:
            self._move_cursor(QTextCursor.MoveOperation.Right)
            return
        elif event.key() == Qt.Key.Key_Up:
            self._move_cursor(QTextCursor.MoveOperation.Up)
            return
        elif event.key() == Qt.Key.Key_Down:
            self._move_cursor(QTextCursor.MoveOperation.Down)
            return

        key = event.text()
        if not key:
            return
        if self._vi_pending_key is not None:
            command = self._vi_pending_key + key
            self._vi_pending_key = None
            if command == ASSEMBLER_EDITOR_VI_KEYS["document_start"]:
                self._move_document_start()
            elif command == ASSEMBLER_EDITOR_VI_KEYS["delete_line"]:
                self._delete_line()
            elif command == ASSEMBLER_EDITOR_VI_KEYS["yank_line"]:
                self._yank_line()
            return
        keys = ASSEMBLER_EDITOR_VI_KEYS
        if key == keys["insert"]:
            self._enter_insert_mode()
        elif key == keys["append"]:
            self._enter_insert_mode(append=True)
        elif key == keys["open_below"]:
            self._open_line_below()
        elif key == keys["open_above"]:
            self._open_line_above()
        elif key == keys["left"]:
            self._move_cursor(QTextCursor.MoveOperation.Left)
        elif key == keys["down"]:
            self._move_cursor(QTextCursor.MoveOperation.Down)
        elif key == keys["up"]:
            self._move_cursor(QTextCursor.MoveOperation.Up)
        elif key == keys["right"]:
            self._move_cursor(QTextCursor.MoveOperation.Right)
        elif key == keys["word_next"]:
            self._move_cursor(QTextCursor.MoveOperation.NextWord)
        elif key == keys["word_previous"]:
            self._move_cursor(QTextCursor.MoveOperation.PreviousWord)
        elif key == keys["word_end"]:
            self._move_cursor(QTextCursor.MoveOperation.EndOfWord)
        elif key == keys["line_start"]:
            self._move_cursor(QTextCursor.MoveOperation.StartOfBlock)
        elif key == keys["line_end"]:
            self._move_cursor(QTextCursor.MoveOperation.EndOfBlock)
        elif key == keys["document_start"][0]:
            self._vi_pending_key = key
        elif key == keys["document_end"]:
            self._move_document_end()
        elif key == keys["delete_line"][0]:
            self._vi_pending_key = key
        elif key == keys["delete_to_end"]:
            self._delete_to_end()
        elif key == keys["delete_character"]:
            self._delete_character()
        elif key == keys["undo"]:
            self.undo()
        elif key == keys["yank_line"][0]:
            self._vi_pending_key = key
        elif key == keys["paste"]:
            self._paste_yank()

    def _move_cursor( self, operation: QTextCursor.MoveOperation,) -> None:
        """
        @brief Move the text cursor using the supplied Qt cursor operation.
        """
        cursor = self.textCursor()
        cursor.movePosition(operation)
        self.setTextCursor(cursor)
        self.ensureCursorVisible()

    def _move_document_start(self) -> None:
        """
        @brief Move the cursor to the beginning of the document.
        """
        self._move_cursor(QTextCursor.MoveOperation.Start)

    def _move_document_end(self) -> None:
        """
        @brief Move the cursor to the end of the document.
        """
        self._move_cursor(QTextCursor.MoveOperation.End)

    def _open_line_below(self) -> None:
        """
        @brief Create a new line below the current line and enter insert mode.
        """
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock)
        cursor.insertText("\n")
        self.setTextCursor(cursor)
        self._enter_insert_mode()

    def _open_line_above(self) -> None:
        """
        @brief Create a new line above the current line and enter insert mode.
        """
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
        cursor.insertText("\n")
        cursor.movePosition(QTextCursor.MoveOperation.PreviousBlock)
        self.setTextCursor(cursor)
        self._enter_insert_mode()

    def _delete_line(self) -> None:
        """
        @brief Delete the current line.
        """
        cursor = self.textCursor()
        cursor.beginEditBlock()
        cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
        if not cursor.movePosition( QTextCursor.MoveOperation.NextBlock, QTextCursor.MoveMode.KeepAnchor,):
            cursor.movePosition( QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor,)
        cursor.removeSelectedText()
        cursor.endEditBlock()
        self.setTextCursor(cursor)
        self.ensureCursorVisible()

    def _delete_to_end(self) -> None:
        """
        @brief Delete from the cursor through the end of the current line.
        """
        cursor = self.textCursor()
        cursor.beginEditBlock()
        cursor.movePosition( QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor,)
        cursor.removeSelectedText()
        cursor.endEditBlock()
        self.setTextCursor(cursor)

    def _delete_character(self) -> None:
        """
        @brief Delete the character at the cursor.
        """
        cursor = self.textCursor()
        if cursor.atBlockEnd():
            return
        cursor.deleteChar()
        self.setTextCursor(cursor)

    def _yank_line(self) -> None:
        """
        @brief Copy the current line into the vi yank buffer.
        """
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
        cursor.movePosition( QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor,)
        self._vi_yank_buffer = cursor.selectedText()

    def _paste_yank(self) -> None:
        """
        @brief Paste the last yanked line below the current line.
        """
        if not self._vi_yank_buffer:
            return
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock)
        cursor.insertText("\n" + self._vi_yank_buffer)
        self.setTextCursor(cursor)
        self.ensureCursorVisible()

    def _update_tab_stop(self) -> None:
        """
        @brief Set the visual tab width using the current editor font.
        """
        space_width = self.fontMetrics().horizontalAdvance(" ")
        self.setTabStopDistance(space_width * self._tab_size)

    def set_tab_size(self, tab_size: int) -> None:
        """
        @brief Set the number of spaces represented by one tab.
        """
        if tab_size <= 0:
            raise ValueError("Tab size must be greater than zero.")
        self._tab_size = tab_size
        self._update_tab_stop()

    def _line_number_area_width(self, _: int = 0) -> int:
        """
        @brief Return the width required for the line-number gutter.
        """
        digits = len(str(max(1, self.blockCount())))
        return ( ASSEMBLER_EDITOR_LINE_NUMBER_LEFT_MARGIN + self.fontMetrics().horizontalAdvance("9") * digits)

    def _update_line_number_area_width(self, _: int) -> None:
        """
        @brief Update the viewport margin for the line-number gutter.
        """
        self.setViewportMargins( self._line_number_area_width(), 0, 0, 0,)

    def _update_line_number_area( self, rect: QRect, dy: int,) -> None:
        """
        @brief Update the visible line-number gutter.
        """
        if dy:
            self._line_number_area.scroll(0, dy)
        else:
            self._line_number_area.update( 0, rect.y(), self._line_number_area.width(), rect.height(),)
        viewport = self.viewport()
        if viewport is not None and rect.contains(viewport.rect()):
            self._update_line_number_area_width(0)

    def resizeEvent(self, event: QResizeEvent | None) -> None:
        """
        @brief Resize the line-number gutter.
        """
        super().resizeEvent(event)
        rect = self.contentsRect()
        self._line_number_area.setGeometry( QRect( rect.left(), rect.top(), self._line_number_area_width(), rect.height(),))

    def _paint_line_numbers( self, painter: QPainter, rect: QRect,) -> None:
        """
        @brief Paint line numbers for visible text blocks.
        """
        painter.fillRect( rect, self.palette().alternateBase(),)
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int( self.blockBoundingGeometry(block) .translated(self.contentOffset()) .top())
        bottom = top + int( self.blockBoundingRect(block).height())
        while block.isValid() and top <= rect.bottom():
            if block.isVisible() and bottom >= rect.top():
                painter.drawText(
                    0,
                    top,
                    ( self._line_number_area.width() - ASSEMBLER_EDITOR_LINE_NUMBER_RIGHT_MARGIN),
                    self.fontMetrics().height(),
                    Qt.AlignmentFlag.AlignRight,
                    str(block_number + 1),
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
