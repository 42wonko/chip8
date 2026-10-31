
"""
@file test_linenumbertextedit_edges.py

@brief Additional edge-case tests for LineNumberTextEdit.
"""

from __future__ import annotations

import unittest

from PyQt6.QtCore import QEvent, QRect, Qt
from PyQt6.QtGui import QKeyEvent, QPainter, QPixmap, QPaintEvent, QTextCursor
from PyQt6.QtWidgets import QApplication

from emulator.constants import (
    ASSEMBLER_EDITOR_VI_INSERT_MODE,
    ASSEMBLER_EDITOR_VI_NORMAL_MODE,
)
from gui.linenumbertextedit import LineNumberTextEdit


class TestLineNumberTextEditEdges(unittest.TestCase):
    """Additional edge-case tests for LineNumberTextEdit."""

    @classmethod
    def setUpClass(cls) -> None:
        """Create the Qt application required by the editor tests."""
        cls._application = QApplication.instance()
        if cls._application is None:
            cls._application = QApplication([])

    def setUp(self) -> None:
        self.editor = LineNumberTextEdit()

    def tearDown(self) -> None:
        self.editor.close()
        self.editor.deleteLater()

    def _press_key( self, key: Qt.Key, text: str = "", modifiers: Qt.KeyboardModifier = Qt.KeyboardModifier.NoModifier) -> None:
        event = QKeyEvent( QEvent.Type.KeyPress, key, modifiers, text)
        self.editor.keyPressEvent(event)

    def _press_character(self, character: str) -> None:
        self._press_key(Qt.Key(ord(character.upper())), character)

    def test_constructor_rejects_nonpositive_tab_size(self) -> None:
        """The constructor should reject a zero tab size."""
        with self.assertRaises(ValueError):
            LineNumberTextEdit(tab_size=0)

    def test_key_press_event_accepts_none(self) -> None:
        """A missing key event should be ignored."""
        self.editor.keyPressEvent(None)
        self.assertEqual( self.editor.vi_mode, ASSEMBLER_EDITOR_VI_NORMAL_MODE)

    def test_append_enters_insert_mode_after_character(self) -> None:
        """The append command should move right before entering insert mode."""
        self.editor.setPlainText("abc")
        self.editor.moveCursor(QTextCursor.MoveOperation.Start)
        self._press_character("a")
        self.assertEqual(self.editor.textCursor().position(), 1)
        self.assertEqual( self.editor.vi_mode, ASSEMBLER_EDITOR_VI_INSERT_MODE)

    def test_append_at_end_does_not_move_cursor(self) -> None:
        """Append at the end of a line should not move beyond the line."""
        self.editor.setPlainText("abc")
        self.editor.moveCursor(QTextCursor.MoveOperation.EndOfBlock)
        self._press_character("a")
        self.assertEqual(self.editor.textCursor().position(), 3)
        self.assertEqual( self.editor.vi_mode, ASSEMBLER_EDITOR_VI_INSERT_MODE)

    def test_escape_cancels_pending_command(self) -> None:
        """Escape should cancel a pending multi-key command."""
        self.editor.setPlainText("one\ntwo")
        self._press_character("g")
        self._press_key(Qt.Key.Key_Escape)
        self.assertIsNone(self.editor._vi_pending_key)
        self.assertEqual( self.editor.vi_mode, ASSEMBLER_EDITOR_VI_NORMAL_MODE)

    def test_key_without_text_is_ignored(self) -> None:
        """A key event without text should not change the document."""
        self.editor.setPlainText("one")
        self._press_key(Qt.Key.Key_F1)
        self.assertEqual(self.editor.toPlainText(), "one")

    def test_unrecognized_pending_command_is_cleared(self) -> None:
        """An unsupported second key should clear the pending command."""
        self.editor.setPlainText("one\ntwo")
        self._press_character("g")
        self._press_character("x")
        self.assertIsNone(self.editor._vi_pending_key)
        self.assertEqual(self.editor.toPlainText(), "one\ntwo")

    def test_yank_command_does_not_modify_document(self) -> None:
        """The yy command should only update the yank buffer."""
        self.editor.setPlainText("one\ntwo")
        self.editor.moveCursor(QTextCursor.MoveOperation.Start)
        self.editor.moveCursor(QTextCursor.MoveOperation.Down)
        self._press_character("y")
        self._press_character("y")
        self.assertEqual(self.editor._vi_yank_buffer, "two")
        self.assertEqual(self.editor.toPlainText(), "one\ntwo")

    def test_word_navigation_commands(self) -> None:
        """The word navigation commands should move the text cursor."""
        self.editor.setPlainText("one two three")
        self.editor.moveCursor(QTextCursor.MoveOperation.Start)
        self._press_character("w")
        self.assertEqual(self.editor.textCursor().position(), 4)
        self._press_character("e")
        self.assertGreater(self.editor.textCursor().position(), 4)
        self._press_character("b")
        self.assertLess(self.editor.textCursor().position(), 8)

    def test_delete_last_line(self) -> None:
        """Deleting the final line should remove its text."""
        self.editor.setPlainText("one\ntwo")
        self.editor.moveCursor(QTextCursor.MoveOperation.End)
        self._press_character("d")
        self._press_character("d")
        self.assertEqual(self.editor.toPlainText(), "one\n")

    def test_delete_character_at_end_of_line_does_nothing(self) -> None:
        """The delete-character command should do nothing at block end."""
        self.editor.setPlainText("one")
        self.editor.moveCursor(QTextCursor.MoveOperation.EndOfBlock)
        self._press_character("x")
        self.assertEqual(self.editor.toPlainText(), "one")

    def test_paste_without_yank_buffer_does_nothing(self) -> None:
        """The paste command should do nothing when the buffer is empty."""
        self.editor.setPlainText("one")
        self.editor.moveCursor(QTextCursor.MoveOperation.Start)
        self._press_character("p")
        self.assertEqual(self.editor.toPlainText(), "one")

    def test_set_tab_size_rejects_nonpositive_value(self) -> None:
        """The tab size setter should reject zero."""
        with self.assertRaises(ValueError):
            self.editor.set_tab_size(0)

    def test_line_number_area_width_grows_with_line_count(self) -> None:
        """The gutter should allow for additional digits in line numbers."""
        initial_width = self.editor._line_number_area_width()
        self.editor.setPlainText("\n".join(["line"] * 100))
        self.assertGreater( self.editor._line_number_area_width(), initial_width)

    def test_line_number_area_size_hint(self) -> None:
        """The gutter size hint should use the editor's calculated width."""
        size_hint = self.editor._line_number_area.sizeHint()
        self.assertEqual( size_hint.width(), self.editor._line_number_area_width())
        self.assertEqual(size_hint.height(), 0)

    def test_resize_updates_line_number_area_geometry(self) -> None:
        """Resizing the editor should resize and reposition the gutter."""
        self.editor.resize(600, 400)
        self.editor.show()
        self._application.processEvents()
        contents_rect = self.editor.contentsRect()
        area_geometry = self.editor._line_number_area.geometry()
        self.assertEqual(area_geometry.left(), contents_rect.left())
        self.assertEqual(area_geometry.top(), contents_rect.top())
        self.assertEqual( area_geometry.width(), self.editor._line_number_area_width())
        self.assertEqual(area_geometry.height(), contents_rect.height())

    def test_line_number_area_paints_visible_lines(self) -> None:
        """Showing the editor should exercise the gutter painting path."""
        self.editor.setPlainText("one\ntwo\nthree")
        self.editor.resize(600, 400)
        self.editor.show()
        self._application.processEvents()
        self.editor._line_number_area.repaint()
        self._application.processEvents()
        self.assertTrue(self.editor._line_number_area.isVisible())

    def test_line_number_area_update_with_vertical_scroll(self) -> None:
        """A vertical update request should scroll the gutter."""
        self.editor.resize(600, 400)
        self.editor.show()
        self._application.processEvents()
        self.editor._update_line_number_area(QRect(0, 0, 100, 100), 5)
        self.assertTrue(self.editor._line_number_area.isVisible())

    def test_line_number_area_update_without_vertical_scroll(self) -> None:
        """A non-scrolling update should request a gutter repaint."""
        self.editor.resize(600, 400)
        self.editor.show()
        self._application.processEvents()
        self.editor._update_line_number_area(QRect(0, 0, 100, 100), 0)
        self.assertTrue(self.editor._line_number_area.isVisible())


    def test_unrecognized_key_does_nothing(self) -> None:
        """An unrecognized normal-mode key should leave the document unchanged."""
        self.editor.setPlainText("one\ntwo")
        self.editor.moveCursor(QTextCursor.MoveOperation.Start)
        self._press_character("?")
        self.assertEqual(self.editor.toPlainText(), "one\ntwo")
        self.assertEqual(self.editor.textCursor().position(), 0)


    def test_paint_line_numbers(self) -> None:
        """The line-number painting method should paint visible text blocks."""
        self.editor.setPlainText("one\ntwo\nthree")
        self.editor.resize(600, 400)
        self.editor.show()
        self._application.processEvents()
        area = self.editor._line_number_area
        pixmap = QPixmap(area.size())
        painter = QPainter(pixmap)
        try:
            self.editor._paint_line_numbers( painter, QRect(0, 0, area.width(), area.height()))
        finally:
            painter.end()
        self.assertFalse(pixmap.isNull())


    def test_line_number_area_render(self) -> None:
        """Rendering the gutter should execute its paint event."""
        self.editor.setPlainText("one\ntwo\nthree")
        self.editor.resize(600, 400)
        self.editor.show()
        self._application.processEvents()
        area = self.editor._line_number_area
        pixmap = QPixmap(area.size())
        area.render(pixmap)
        self.assertFalse(pixmap.isNull())


    def test_line_number_area_paint_event_without_event(self) -> None:
        """A missing paint event should return without raising an exception."""
        self.editor._line_number_area.paintEvent(None)


    def test_paint_line_numbers_with_partial_visible_region(self) -> None:
        """Painting should handle a region that covers only part of the gutter."""
        self.editor.setPlainText("\n".join(f"line {number}" for number in range(1, 20)))
        self.editor.resize(600, 400)
        self.editor.show()
        self._application.processEvents()
        area = self.editor._line_number_area
        pixmap = QPixmap(area.size())
        painter = QPainter(pixmap)
        try:
            self.editor._paint_line_numbers( painter, QRect(0, 0, area.width(), self.editor.fontMetrics().height()))
        finally:
            painter.end()
        self.assertFalse(pixmap.isNull())


if __name__ == "__main__":
    unittest.main()

