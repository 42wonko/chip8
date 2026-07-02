"""
@file test_keyboard.py

@brief Unit tests for the CHIP-8 keyboard.
"""

import unittest

from emulator.chip8keyboard import Chip8Keyboard
from emulator.constants import KEY_COUNT


class TestChip8Keyboard(unittest.TestCase):
    """
    @brief Tests for the CHIP-8 keyboard.
    """

    ###########################################################################
    # Construction
    ###########################################################################
    def test_initial_state(self) -> None:
        keyboard = Chip8Keyboard()
        for key in range(KEY_COUNT):
            self.assertFalse(keyboard.is_pressed(key))

    ###########################################################################
    # Key handling
    ###########################################################################
    def test_press_key(self) -> None:
        keyboard = Chip8Keyboard()
        keyboard.press(5)
        self.assertTrue(keyboard.is_pressed(5))

    def test_release_key(self) -> None:
        keyboard = Chip8Keyboard()
        keyboard.press(5)
        keyboard.release(5)
        self.assertFalse(keyboard.is_pressed(5))

    def test_press_does_not_affect_other_keys(self) -> None:
        keyboard = Chip8Keyboard()
        keyboard.press(3)
        for key in range(KEY_COUNT):
            if key == 3:
                self.assertTrue(keyboard.is_pressed(key))
            else:
                self.assertFalse(keyboard.is_pressed(key))

    ###########################################################################
    # Validation
    ###########################################################################
    def test_invalid_key_too_small(self) -> None:
        keyboard = Chip8Keyboard()
        with self.assertRaises(IndexError):
            keyboard.press(-1)

    def test_invalid_key_too_large(self) -> None:
        keyboard = Chip8Keyboard()
        with self.assertRaises(IndexError):
            keyboard.press(KEY_COUNT)

    ###########################################################################
    # Reset
    ###########################################################################
    def test_reset(self) -> None:
        keyboard = Chip8Keyboard()
        keyboard.press(1)
        keyboard.press(5)
        keyboard.press(10)
        keyboard.reset()
        for key in range(KEY_COUNT):
            self.assertFalse(keyboard.is_pressed(key))


if __name__ == "__main__":
    unittest.main(verbosity=2)
