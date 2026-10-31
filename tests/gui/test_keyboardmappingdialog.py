"""
@file test_keyboardmappingdialog.py

@brief Tests for the keyboard mapping dialog.
"""

from __future__ import annotations

import unittest

from PyQt6.QtCore import QEvent, Qt
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtWidgets import QApplication

from controller.keyboardmap import KeyboardMap
from gui.keyboardmappingdialog import KeyboardMappingDialog


class TestKeyboardMappingDialog(unittest.TestCase):
    """
    @brief Tests for KeyboardMappingDialog.
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        @brief Create the Qt application required by the dialog tests.
        """
        cls._application = QApplication.instance()
        if cls._application is None:
            cls._application = QApplication([])

    def setUp(self) -> None:
        """
        @brief Create a fresh dialog for each test.
        """
        self.dialog = KeyboardMappingDialog( 0xA, int(Qt.Key.Key_Y))

    def tearDown(self) -> None:
        """
        @brief Dispose of the dialog after each test.
        """
        self.dialog.close()
        self.dialog.deleteLater()

    def test_initializes_title_and_key_labels(self) -> None:
        """
        @brief Verify the dialog title and initial key labels.
        """
        expected_key_name = KeyboardMap.key_name(int(Qt.Key.Key_Y))
        self.assertEqual(self.dialog.windowTitle(), "CHIP-8 Key A")
        self.assertEqual( self.dialog.currentSettingLabel.text(), expected_key_name)
        self.assertEqual( self.dialog.newSettingLabel.text(), expected_key_name)

    def test_new_key_returns_initial_key_before_key_press(self) -> None:
        """
        @brief Verify that the current key is initially selected.
        """
        self.assertEqual(self.dialog.new_key, int(Qt.Key.Key_Y))

    def test_key_press_updates_new_key_and_label(self) -> None:
        """
        @brief Verify that a key press selects and displays the new key.
        """
        event = QKeyEvent( QEvent.Type.KeyPress, Qt.Key.Key_Z, Qt.KeyboardModifier.NoModifier, "z")
        self.dialog.keyPressEvent(event)
        self.assertEqual(self.dialog.new_key, int(Qt.Key.Key_Z))
        self.assertEqual( self.dialog.newSettingLabel.text(), KeyboardMap.key_name(int(Qt.Key.Key_Z)))
        self.assertTrue(event.isAccepted())

    def test_auto_repeat_key_press_is_ignored(self) -> None:
        """
        @brief Verify that auto-repeat events do not change the selection.
        """
        event = QKeyEvent( QEvent.Type.KeyPress, Qt.Key.Key_Z, Qt.KeyboardModifier.NoModifier, "z", True)
        self.dialog.keyPressEvent(event)
        self.assertEqual(self.dialog.new_key, int(Qt.Key.Key_Y))
        self.assertEqual( self.dialog.newSettingLabel.text(), KeyboardMap.key_name(int(Qt.Key.Key_Y)))

    def test_none_key_event_is_ignored(self) -> None:
        """
        @brief Verify that a missing key event leaves the selection unchanged.
        """
        self.dialog.keyPressEvent(None)
        self.assertEqual(self.dialog.new_key, int(Qt.Key.Key_Y))
        self.assertEqual( self.dialog.newSettingLabel.text(), KeyboardMap.key_name(int(Qt.Key.Key_Y)))


if __name__ == "__main__":
    unittest.main()
