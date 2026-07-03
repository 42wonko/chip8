"""
@file keyboarddialog.py

@brief Keyboard mapping dialog.
"""

from __future__ import annotations

from pathlib import Path

from PyQt6 import uic
from PyQt6.QtWidgets import QDialog, QPushButton

from controller.keyboardmap import KeyboardMap
from gui.keyboardmappingdialog import KeyboardMappingDialog


class KeyboardDialog(QDialog):
    """
    @brief Dialog used to edit the complete keyboard mapping.
    """
    def __init__( self, keyboard_map: KeyboardMap) -> None:
        """
        @brief Construct the dialog.

        @param keyboard_map
            Keyboard mapping to edit.
        """
        super().__init__()
        ui_file = ( Path(__file__).parent / "ui" / "keyboarddialog.ui")
        uic.loadUi(str(ui_file), self)
        self._keyboard_map = keyboard_map
        self._button_map: dict[QPushButton, int] = {}
        self._initialize()


    ###########################################################################
    # Initialization
    ###########################################################################
    def _initialize(self) -> None:
        """
        @brief Initialize the dialog.
        """
        self.changeMappingPushButton.hide()
        self._button_map = {
            self.pushButton:    0x1,
            self.pushButton_2:  0x2,
            self.pushButton_3:  0x3,
            self.pushButton_C:  0xC,

            self.pushButton_4:  0x4,
            self.pushButton_5:  0x5,
            self.pushButton_6:  0x6,
            self.pushButton_D:  0xD,

            self.pushButton_7:  0x7,
            self.pushButton_8:  0x8,
            self.pushButton_9:  0x9,
            self.pushButton_E:  0xE,

            self.pushButton_A:  0xA,
            self.pushButton_0:  0x0,
            self.pushButton_B:  0xB,
            self.pushButton_F:  0xF
        }
        for button in self._button_map:
            button.clicked.connect(self._button_clicked)
        self._update_buttons()


    ###########################################################################
    # Slots
    ###########################################################################
    def _button_clicked(self) -> None:
        """
        @brief Handle one keypad button.
        """
        button = self.sender()
        if not isinstance(button, QPushButton):
            return
        chip8_key = self._button_map[button]
        dialog = KeyboardMappingDialog( chip8_key, self._keyboard_map.host_key(chip8_key))

        if dialog.exec():
            self._keyboard_map.set_mapping( chip8_key, dialog.new_key)
            self._update_buttons()


    ###########################################################################
    # Helpers
    ###########################################################################
    def _update_buttons(self) -> None:
        """
        @brief Refresh all button captions.
        """
        for button, chip8_key in self._button_map.items():
            button.setText( f"{chip8_key:X}\n" f"{KeyboardMap.key_name(self._keyboard_map.host_key(chip8_key))}")
