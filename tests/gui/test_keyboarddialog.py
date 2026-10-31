"""
@file test_keyboarddialog.py

@brief Tests for the keyboard dialog.
"""

from __future__ import annotations

import unittest
from unittest.mock import patch

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

from controller.keyboardmap import KeyboardMap
from gui.keyboarddialog import KeyboardDialog


class TestKeyboardDialog(unittest.TestCase):
    """
    @brief Tests for KeyboardDialog.
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
        @brief Create a fresh keyboard map and dialog.
        """
        self.keyboard_map = KeyboardMap()
        self.dialog = KeyboardDialog(self.keyboard_map)

    def tearDown(self) -> None:
        """
        @brief Dispose of the dialog after each test.
        """
        self.dialog.close()
        self.dialog.deleteLater()

    def test_initializes_all_key_buttons(self) -> None:
        """
        @brief Verify that all CHIP-8 keys have corresponding buttons.
        """
        self.assertEqual(len(self.dialog._button_map), 16)
        for button, chip8_key in self.dialog._button_map.items():
            expected_text = ( f"{chip8_key:X}\n" f"{KeyboardMap.key_name(self.keyboard_map.host_key(chip8_key))}")
            self.assertEqual(button.text(), expected_text)

    def test_change_mapping_button_is_hidden(self) -> None:
        """
        @brief Verify that the unused change-mapping button is hidden.
        """
        self.assertTrue(self.dialog.changeMappingPushButton.isHidden())

    def test_button_clicked_without_button_sender_does_nothing(self) -> None:
        """
        @brief Verify that the slot safely handles a missing button sender.
        """
        original_mapping = { key: self.keyboard_map.host_key(key) for key in range(16) }
        self.dialog._button_clicked()
        self.assertEqual( { key: self.keyboard_map.host_key(key) for key in range(16) }, original_mapping)

    def test_accepted_mapping_updates_keyboard_map_and_button(self) -> None:
        """
        @brief Verify that accepting a mapping changes the selected key.
        """
        original_host_key = self.keyboard_map.host_key(0x1)
        new_host_key = int(Qt.Key.Key_Z)
        with patch("gui.keyboarddialog.KeyboardMappingDialog") as dialog_type:
            mapping_dialog = dialog_type.return_value
            mapping_dialog.exec.return_value = 1
            mapping_dialog.new_key = new_host_key
            self.dialog.pushButton.click()
        dialog_type.assert_called_once_with(0x1, original_host_key)
        self.assertEqual(self.keyboard_map.host_key(0x1), new_host_key)
        self.assertEqual( self.dialog.pushButton.text(), f"1\n{KeyboardMap.key_name(new_host_key)}")

    def test_cancelled_mapping_does_not_change_keyboard_map(self) -> None:
        """
        @brief Verify that cancelling a mapping leaves the key unchanged.
        """
        original_host_key = self.keyboard_map.host_key(0x1)
        new_host_key = int(Qt.Key.Key_Z)

        with patch("gui.keyboarddialog.KeyboardMappingDialog") as dialog_type:
            mapping_dialog = dialog_type.return_value
            mapping_dialog.exec.return_value = 0
            mapping_dialog.new_key = new_host_key
            self.dialog.pushButton.click()
        self.assertEqual( self.keyboard_map.host_key(0x1),original_host_key)
        self.assertEqual( self.dialog.pushButton.text(), f"1\n{KeyboardMap.key_name(original_host_key)}")


if __name__ == "__main__":
    unittest.main()
