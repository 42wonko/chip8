"""
@file test_linenumbertextedit.py

@brief Tests for the assembler source editor.
"""

from __future__ import annotations

import unittest

from PyQt6.QtCore import QEvent, Qt
from PyQt6.QtGui import QFont, QKeyEvent, QTextCursor
from PyQt6.QtWidgets import QApplication

from emulator.constants import (
    ASSEMBLER_EDITOR_VI_INSERT_MODE,
    ASSEMBLER_EDITOR_VI_NORMAL_MODE,
)
from gui.linenumbertextedit import LineNumberTextEdit


class TestLineNumberTextEdit(unittest.TestCase):
    """
    @brief Tests for LineNumberTextEdit.
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        @brief Create the Qt application required by the editor tests.
        """
        cls._application = QApplication.instance()
        if cls._application is None:
            cls._application = QApplication([])

    def setUp(self) -> None:
        """
        @brief Create a fresh editor for each test.
        """
        self.editor = LineNumberTextEdit()

    def tearDown(self) -> None:
        """
        @brief Dispose of the editor after each test.
        """
        self.editor.close()
        self.editor.deleteLater()

    def _press_key(
        self,
        key: Qt.Key,
        text: str = "",
        modifiers: Qt.KeyboardModifier = Qt.KeyboardModifier.NoModifier,
    ) -> None:
        """
        @brief Send a key press directly to the editor.
        """
        event = QKeyEvent(
            QEvent.Type.KeyPress,
            key,
            modifiers,
            text,
        )
        self.editor.keyPressEvent(event)

    def _press_character(self, character: str) -> None:
        """
        @brief Send an ordinary character key press to the editor.
        """
        self._press_key(
            Qt.Key(ord(character.upper())),
            character,
        )

    def test_initial_mode_is_normal(self) -> None:
        """
        @brief Verify that the editor starts in normal mode.
        """
        self.assertEqual(
            self.editor.vi_mode,
            ASSEMBLER_EDITOR_VI_NORMAL_MODE,
        )

    def test_i_enters_insert_mode(self) -> None:
        """
        @brief Verify that i enters insert mode.
        """
        self._press_character("i")

        self.assertEqual(
            self.editor.vi_mode,
            ASSEMBLER_EDITOR_VI_INSERT_MODE,
        )

    def test_escape_enters_normal_mode(self) -> None:
        """
        @brief Verify that Escape leaves insert mode.
        """
        self._press_character("i")
        self._press_key(Qt.Key.Key_Escape)

        self.assertEqual(
            self.editor.vi_mode,
            ASSEMBLER_EDITOR_VI_NORMAL_MODE,
        )

    def test_insert_mode_inserts_text(self) -> None:
        """
        @brief Verify that normal text entry works in insert mode.
        """
        self._press_character("i")
        self._press_character("a")
        self._press_character("b")
        self._press_character("c")

        self.assertEqual(
            self.editor.toPlainText(),
            "abc",
        )

    def test_h_j_k_l_move_cursor(self) -> None:
        """
        @brief Verify that h, j, k and l move the cursor.
        """
        self.editor.setPlainText("abc\ndef")
        self.editor.moveCursor(QTextCursor.MoveOperation.Start)

        self._press_character("l")
        self.assertEqual(self.editor.textCursor().position(), 1)

        self._press_character("l")
        self.assertEqual(self.editor.textCursor().position(), 2)

        self._press_character("h")
        self.assertEqual(self.editor.textCursor().position(), 1)

        self._press_character("j")
        self.assertEqual(
            self.editor.textCursor().blockNumber(),
            1,
        )

        self._press_character("k")
        self.assertEqual(
            self.editor.textCursor().blockNumber(),
            0,
        )

    def test_cursor_keys_move_cursor(self) -> None:
        """
        @brief Verify that the cursor keys move the cursor in normal mode.
        """
        self.editor.setPlainText("abc\ndef")
        self.editor.moveCursor(QTextCursor.MoveOperation.Start)

        self._press_key(Qt.Key.Key_Right)
        self.assertEqual(self.editor.textCursor().position(), 1)

        self._press_key(Qt.Key.Key_Right)
        self.assertEqual(self.editor.textCursor().position(), 2)

        self._press_key(Qt.Key.Key_Left)
        self.assertEqual(self.editor.textCursor().position(), 1)

        self._press_key(Qt.Key.Key_Down)
        self.assertEqual(
            self.editor.textCursor().blockNumber(),
            1,
        )

        self._press_key(Qt.Key.Key_Up)
        self.assertEqual(
            self.editor.textCursor().blockNumber(),
            0,
        )

    def test_zero_moves_to_start_of_line(self) -> None:
        """
        @brief Verify that 0 moves to the beginning of the current line.
        """
        self.editor.setPlainText("abc")
        self.editor.moveCursor(QTextCursor.MoveOperation.EndOfBlock)

        self._press_character("0")

        self.assertEqual(
            self.editor.textCursor().positionInBlock(),
            0,
        )

    def test_dollar_moves_to_end_of_line(self) -> None:
        """
        @brief Verify that $ moves to the end of the current line.
        """
        self.editor.setPlainText("abc")
        self.editor.moveCursor(QTextCursor.MoveOperation.Start)

        self._press_character("$")

        self.assertEqual(
            self.editor.textCursor().positionInBlock(),
            3,
        )

    def test_gg_moves_to_document_start(self) -> None:
        """
        @brief Verify that gg moves to the beginning of the document.
        """
        self.editor.setPlainText("one\ntwo\nthree")
        self.editor.moveCursor(QTextCursor.MoveOperation.End)

        self._press_character("g")
        self._press_character("g")

        self.assertEqual(
            self.editor.textCursor().position(),
            0,
        )

    def test_g_moves_to_document_end(self) -> None:
        """
        @brief Verify that G moves to the end of the document.
        """
        self.editor.setPlainText("one\ntwo\nthree")
        self.editor.moveCursor(QTextCursor.MoveOperation.Start)

        self._press_character("G")

        self.assertEqual(
            self.editor.textCursor().position(),
            len(self.editor.toPlainText()),
        )

    def test_x_deletes_character(self) -> None:
        """
        @brief Verify that x deletes the character under the cursor.
        """
        self.editor.setPlainText("abc")
        self.editor.moveCursor(QTextCursor.MoveOperation.Start)

        self._press_character("x")

        self.assertEqual(
            self.editor.toPlainText(),
            "bc",
        )

    def test_D_deletes_to_end_of_line(self) -> None:
        """
        @brief Verify that D deletes from the cursor to the end of the line.
        """
        self.editor.setPlainText("abcdef")
        cursor = self.editor.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        cursor.movePosition(
            QTextCursor.MoveOperation.Right,
            n=2,
        )
        self.editor.setTextCursor(cursor)

        self._press_character("D")

        self.assertEqual(
            self.editor.toPlainText(),
            "ab",
        )

    def test_dd_deletes_current_line(self) -> None:
        """
        @brief Verify that dd deletes the current line.
        """
        self.editor.setPlainText("one\ntwo\nthree")
        self.editor.moveCursor(QTextCursor.MoveOperation.Start)
        self.editor.moveCursor(QTextCursor.MoveOperation.Down)

        self._press_character("d")
        self._press_character("d")

        self.assertEqual(
            self.editor.toPlainText(),
            "one\nthree",
        )

    def test_yy_yanks_current_line(self) -> None:
        """
        @brief Verify that yy stores the current line.
        """
        self.editor.setPlainText("one\ntwo")
        self.editor.moveCursor(QTextCursor.MoveOperation.Start)
        self.editor.moveCursor(QTextCursor.MoveOperation.Down)

        self._press_character("y")
        self._press_character("y")

        self.assertEqual(
            self.editor._vi_yank_buffer,
            "two",
        )

    def test_p_pastes_yanked_line_below_current_line(self) -> None:
        """
        @brief Verify that p pastes the yanked line below the current line.
        """
        self.editor.setPlainText("one\ntwo")
        self.editor.moveCursor(QTextCursor.MoveOperation.Start)

        self._press_character("y")
        self._press_character("y")
        self._press_character("p")

        self.assertEqual(
            self.editor.toPlainText(),
            "one\none\ntwo",
        )

    def test_o_opens_line_below_and_enters_insert_mode(self) -> None:
        """
        @brief Verify that o opens a line below and enters insert mode.
        """
        self.editor.setPlainText("one")
        self.editor.moveCursor(QTextCursor.MoveOperation.Start)

        self._press_character("o")

        self.assertEqual(
            self.editor.toPlainText(),
            "one\n",
        )
        self.assertEqual(
            self.editor.vi_mode,
            ASSEMBLER_EDITOR_VI_INSERT_MODE,
        )

    def test_O_opens_line_above_and_enters_insert_mode(self) -> None:
        """
        @brief Verify that O opens a line above and enters insert mode.
        """
        self.editor.setPlainText("one")
        self.editor.moveCursor(QTextCursor.MoveOperation.Start)

        self._press_character("O")

        self.assertEqual(
            self.editor.toPlainText(),
            "\none",
        )
        self.assertEqual(
            self.editor.vi_mode,
            ASSEMBLER_EDITOR_VI_INSERT_MODE,
        )

    def test_u_undoes_edit(self) -> None:
        """
        @brief Verify that u invokes the editor undo operation.
        """
        self._press_character("i")
        self._press_character("a")
        self._press_character("b")
        self._press_key(Qt.Key.Key_Escape)

        self._press_character("u")

        self.assertEqual(
            self.editor.toPlainText(),
            "",
        )

    def test_control_r_redoes_edit(self) -> None:
        """
        @brief Verify that Ctrl-R invokes the editor redo operation.
        """
        self._press_character("i")
        self._press_character("a")
        self._press_character("b")
        self._press_key(Qt.Key.Key_Escape)

        self._press_character("u")

        self.assertEqual(
            self.editor.toPlainText(),
            "",
        )

        self._press_key(
            Qt.Key.Key_R,
            modifiers=Qt.KeyboardModifier.ControlModifier,
        )

        self.assertEqual(
            self.editor.toPlainText(),
            "ab",
        )

    def test_vi_mode_can_be_disabled(self) -> None:
        """
        @brief Verify that vi-mode can be disabled.
        """
        self.editor.set_vi_mode_enabled(False)

        self.assertFalse(self.editor.vi_mode_enabled)

    def test_disabling_vi_mode_allows_normal_text_input(self) -> None:
        """
        @brief Verify that disabled vi-mode uses normal text editing.
        """
        self.editor.set_vi_mode_enabled(False)
        self.editor.setPlainText("")
        event = QKeyEvent( QEvent.Type.KeyPress, Qt.Key.Key_A, Qt.KeyboardModifier.NoModifier, "a",)
        self.editor.keyPressEvent(event)
        self.assertEqual(self.editor.toPlainText(), "a")

    def test_enabling_vi_mode_starts_in_normal_mode(self) -> None:
        """
        @brief Verify that enabling vi-mode starts in normal mode.
        """
        self.editor.set_vi_mode_enabled(False)
        self.editor.set_vi_mode_enabled(True)

        self.assertTrue(self.editor.vi_mode_enabled)
        self.assertEqual(self.editor.vi_mode, ASSEMBLER_EDITOR_VI_NORMAL_MODE)

    def test_set_tab_size(self) -> None:
        """
        @brief Verify that the editor accepts a new tab size.
        """
        self.editor.set_tab_size(8)

        self.assertEqual(self.editor._tab_size, 8)

    def test_set_editor_font(self) -> None:
        """
        @brief Verify that the editor font can be changed.
        """
        font = QFont("Monospace", 14)

        self.editor.set_editor_font(font)

        self.assertEqual(self.editor.font().family(), font.family())
        self.assertEqual(self.editor.font().pointSize(), font.pointSize())


if __name__ == "__main__":
    unittest.main()

