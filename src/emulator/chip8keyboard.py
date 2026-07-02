"""
@file chip8keyboard.py

@brief CHIP-8 hexadecimal keypad.

@details
Stores the state of the sixteen CHIP-8 keys.

The class is independent of any GUI framework. It merely records which
keys are currently pressed.

@author
Michael Dlubatz

@copyright
MIT License
"""

from __future__ import annotations

from emulator.constants import KEY_COUNT


class Chip8Keyboard:
    """
    @brief CHIP-8 hexadecimal keypad.
    """
    def __init__(self) -> None:
        """
        @brief Construct the keyboard.
        """
        self._keys: list[bool] = [False] * KEY_COUNT


    ###########################################################################
    # Public interface
    ###########################################################################
    def press(self, key: int) -> None:
        """
        @brief Press a key.

        @param key
            CHIP-8 key number.
        """
        self._validate_key(key)
        self._keys[key] = True


    def release(self, key: int) -> None:
        """
        @brief Release a key.

        @param key
            CHIP-8 key number.
        """
        self._validate_key(key)
        self._keys[key] = False


    def is_pressed(self, key: int) -> bool:
        """
        @brief Return whether a key is pressed.

        @param key
            CHIP-8 key number.

        @return
            True if the key is currently pressed.
        """
        self._validate_key(key)
        return self._keys[key]


    def first_pressed(self) -> int | None:
        """
        @brief Return the first pressed key.

        @return
            Key number or None if no key is currently pressed.
        """
        for key in range(KEY_COUNT):
            if self._keys[key]:
                return key

        return None


    def reset(self) -> None:
        """
        @brief Release all keys.
        """
        self._keys[:] = [False] * KEY_COUNT


    ###########################################################################
    # Private helpers
    ###########################################################################
    def _validate_key(self, key: int) -> None:
        """
        @brief Validate a CHIP-8 key number.

        @param key
            CHIP-8 key number.

        @exception IndexError
            Invalid key number.
        """
        if key < 0 or key >= KEY_COUNT:
            raise IndexError( f"Key {key:X} is out of range.")

