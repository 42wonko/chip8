"""
@file keyboardmap.py

@brief Host keyboard to CHIP-8 keyboard mapping.

@details
This class maintains the mapping between host keyboard keys (Qt key codes)
and CHIP-8 keypad keys.

The mapping is completely independent of the emulator and the GUI. It is
used by the controller to translate Qt key events into CHIP-8 key presses
and by the keyboard configuration dialogs to display and edit the mapping.

The class guarantees that every CHIP-8 key has exactly one host key and
that every host key is assigned to at most one CHIP-8 key.

@author
Michael Dlubatz

@copyright
MIT License
"""

from __future__ import annotations

from PyQt6.QtCore import Qt


class KeyboardMap:
    """
    @brief Mapping between host keyboard and CHIP-8 keypad.
    """

    def __init__(self) -> None:
        """
        @brief Construct the default keyboard mapping.
        """
        self._mapping: dict[int, int] = {
            0x1: Qt.Key.Key_1,
            0x2: Qt.Key.Key_2,
            0x3: Qt.Key.Key_3,
            0xC: Qt.Key.Key_4,

            0x4: Qt.Key.Key_Q,
            0x5: Qt.Key.Key_W,
            0x6: Qt.Key.Key_E,
            0xD: Qt.Key.Key_R,

            0x7: Qt.Key.Key_A,
            0x8: Qt.Key.Key_S,
            0x9: Qt.Key.Key_D,
            0xE: Qt.Key.Key_F,

            0xA: Qt.Key.Key_Y,
            0x0: Qt.Key.Key_X,
            0xB: Qt.Key.Key_C,
            0xF: Qt.Key.Key_V
        }

    ###########################################################################
    # Mapping lookup
    ###########################################################################
    def chip8_key(self, host_key: int) -> int | None:
        """
        @brief Return the CHIP-8 key assigned to a host key.

        @param host_key
            Qt key code.

        @return
            CHIP-8 key or None if the key is not mapped.
        """
        for chip8_key, qt_key in self._mapping.items():
            if qt_key == host_key:
                return chip8_key

        return None


    def host_key(self, chip8_key: int) -> int:
        """
        @brief Return the host key assigned to a CHIP-8 key.

        @param chip8_key
            CHIP-8 key (0x0..0xF).

        @return
            Qt key code.
        """
        return self._mapping[chip8_key]


    ###########################################################################
    # Mapping modification
    ###########################################################################
    def set_mapping(self, chip8_key: int, host_key: int) -> None:
        """
        @brief Assign a new host key.

        If the host key is already assigned to another CHIP-8 key the
        assignments are swapped.

        @param chip8_key
            CHIP-8 key.

        @param host_key
            Qt key code.
        """
        old_host_key = self._mapping[chip8_key]
        other_chip8_key = self.chip8_key(host_key)
        if other_chip8_key is not None:
            self._mapping[other_chip8_key] = old_host_key

        self._mapping[chip8_key] = host_key


    ###########################################################################
    # Utility
    ###########################################################################
    @staticmethod
    def key_name(host_key: int) -> str:
        """
        @brief Return a human-readable name for a host key.

        @param host_key
            Qt key code.

        @return
            Human-readable key name.
        """
        from PyQt6.QtGui import QKeySequence
        text = QKeySequence(host_key).toString()
        if text:
            return text
        return f"0x{host_key:X}"
