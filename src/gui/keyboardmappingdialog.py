"""
@file keyboardmappingdialog.py

@brief Dialog for changing a single keyboard mapping.
"""

from __future__ import annotations

from pathlib import Path

from PyQt6 import uic
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtWidgets import QDialog

from controller.keyboardmap import KeyboardMap


class KeyboardMappingDialog(QDialog):
    """
    @brief Dialog used to assign a new host key to one CHIP-8 key.
    """

    def __init__( self, chip8_key: int, current_key: int) -> None:
        super().__init__()

        ui_file = ( Path(__file__).parent / "ui" / "keyboardmappingdialog.ui")
        uic.loadUi(str(ui_file), self)
        self._chip8_key = chip8_key
        self._new_key = current_key
        self._initialize()


    ###########################################################################
    # Public interface
    ###########################################################################
    @property
    def new_key(self) -> int:
        """
        @brief Return the selected host key.
        """
        return self._new_key


    ###########################################################################
    # Event handling
    ###########################################################################
    def keyPressEvent( self, event: QKeyEvent | None) -> None:
        """
        @brief Capture the next pressed key.
        """
        if event is None:
            return
        if event.isAutoRepeat():
            return
        self._new_key = event.key()
        self.newSettingLabel.setText( KeyboardMap.key_name(self._new_key))

        event.accept()


    ###########################################################################
    # Initialization
    ###########################################################################
    def _initialize(self) -> None:
        """
        @brief Initialize dialog contents.
        """
        self.setWindowTitle( f"CHIP-8 Key {self._chip8_key:X}")
        self.currentSettingLabel.setText( KeyboardMap.key_name(self._new_key))
        self.newSettingLabel.setText( KeyboardMap.key_name(self._new_key))
