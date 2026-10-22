"""Unit tests for framebuffer scrolling primitives."""

import unittest
from unittest.mock import MagicMock

from emulator.chip8framebuffer import (
    SUPERCHIP_DISPLAY_HEIGHT,
    SUPERCHIP_DISPLAY_WIDTH,
    Chip8Framebuffer,
)


class TestFramebufferScrolling(unittest.TestCase):
    def setUp(self) -> None:
        self.framebuffer = Chip8Framebuffer(MagicMock(), MagicMock())

    def test_scroll_down_moves_pixels_and_clears_exposed_rows(self) -> None:
        self.framebuffer.set_pixel(3, 1, True)
        self.framebuffer.set_pixel(4, 2, True)
        self.framebuffer.scroll_down(2)
        self.assertTrue(self.framebuffer.get_pixel(3, 3))
        self.assertTrue(self.framebuffer.get_pixel(4, 4))
        self.assertFalse(self.framebuffer.get_pixel(3, 1))
        self.assertFalse(self.framebuffer.get_pixel(4, 2))

    def test_horizontal_scroll_moves_pixels_and_clears_exposed_columns(self) -> None:
        self.framebuffer.set_pixel(5, 7, True)
        self.framebuffer.set_pixel(9, 7, True)
        self.framebuffer.scroll_right()
        self.assertTrue(self.framebuffer.get_pixel(9, 7))
        self.assertTrue(self.framebuffer.get_pixel(13, 7))
        self.assertFalse(self.framebuffer.get_pixel(5, 7))
        self.framebuffer.scroll_left()
        self.assertTrue(self.framebuffer.get_pixel(5, 7))
        self.assertTrue(self.framebuffer.get_pixel(9, 7))
        self.assertFalse(self.framebuffer.get_pixel(13, 7))

    def test_scroll_clears_active_display_when_distance_is_at_least_dimension(self) -> None:
        self.framebuffer.set_pixel(2, 3, True)
        self.framebuffer.scroll_down(self.framebuffer.height)
        self.assertFalse(self.framebuffer.get_pixel(2, 3))
        self.framebuffer.set_pixel(2, 3, True)
        self.framebuffer.scroll_right(self.framebuffer.width)
        self.assertFalse(self.framebuffer.get_pixel(2, 3))

    def test_scroll_is_confined_to_active_resolution(self) -> None:
        self.framebuffer.set_resolution(SUPERCHIP_DISPLAY_WIDTH, SUPERCHIP_DISPLAY_HEIGHT)
        self.framebuffer.set_pixel(100, 50, True)
        self.framebuffer.set_resolution(64, 32)
        self.framebuffer.set_pixel(1, 1, True)
        self.framebuffer.scroll_down(1)
        self.assertTrue(bool(self.framebuffer.pixels()[2, 1]))
        self.framebuffer.set_resolution(SUPERCHIP_DISPLAY_WIDTH, SUPERCHIP_DISPLAY_HEIGHT)
        self.assertTrue(self.framebuffer.get_pixel(100, 50))

    def test_horizontal_scroll_is_confined_to_active_resolution(self) -> None:
        self.framebuffer.set_resolution(SUPERCHIP_DISPLAY_WIDTH, SUPERCHIP_DISPLAY_HEIGHT)
        self.framebuffer.set_pixel(100, 50, True)
        self.framebuffer.set_resolution(64, 32)
        self.framebuffer.set_pixel(5, 5, True)
        self.framebuffer.scroll_right()
        self.assertTrue(self.framebuffer.get_pixel(9, 5))
        self.assertFalse(self.framebuffer.get_pixel(5, 5))
        self.framebuffer.set_resolution(SUPERCHIP_DISPLAY_WIDTH, SUPERCHIP_DISPLAY_HEIGHT)
        self.assertTrue(self.framebuffer.get_pixel(100, 50))

    def test_negative_scroll_distance_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.framebuffer.scroll_down(-1)
        with self.assertRaises(ValueError):
            self.framebuffer.scroll_left(-1)

    def test_scroll_does_not_wrap(self) -> None:
        self.framebuffer.set_pixel(self.framebuffer.width - 1, 4, True)
        self.framebuffer.scroll_right()
        self.assertFalse(self.framebuffer.get_pixel(3, 4))
        self.assertFalse(any(self.framebuffer.pixels()[4, :4]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
