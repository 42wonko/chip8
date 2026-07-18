"""
@file test_framebuffer.py

@brief Unit tests for the CHIP-8 framebuffer.
"""

import unittest

from emulator.constants import DISPLAY_HEIGHT, DISPLAY_WIDTH
from tests.helpers import create_framebuffer


class TestcreateFramebuffer(unittest.TestCase):
    """
    @brief Tests for the CHIP-8 framebuffer.
    """

    ###########################################################################
    # Construction
    ###########################################################################

    def test_initial_state(self) -> None:
        framebuffer = create_framebuffer()

        for y in range(DISPLAY_HEIGHT):
            for x in range(DISPLAY_WIDTH):
                self.assertFalse(framebuffer.get_pixel(x, y))

    ###########################################################################
    # Pixel access
    ###########################################################################

    def test_set_pixel(self) -> None:
        framebuffer = create_framebuffer()

        framebuffer.set_pixel(10, 5, True)

        self.assertTrue(framebuffer.get_pixel(10, 5))

    def test_clear_pixel(self) -> None:
        framebuffer = create_framebuffer()

        framebuffer.set_pixel(10, 5, True)
        framebuffer.set_pixel(10, 5, False)

        self.assertFalse(framebuffer.get_pixel(10, 5))

    ###########################################################################
    # XOR drawing
    ###########################################################################

    def test_xor_sets_pixel(self) -> None:
        framebuffer = create_framebuffer()

        collision = framebuffer.xor_pixel(4, 7)

        self.assertFalse(collision)
        self.assertTrue(framebuffer.get_pixel(4, 7))

    def test_xor_clears_pixel(self) -> None:
        framebuffer = create_framebuffer()

        framebuffer.set_pixel(4, 7, True)

        collision = framebuffer.xor_pixel(4, 7)

        self.assertTrue(collision)
        self.assertFalse(framebuffer.get_pixel(4, 7))

    ###########################################################################
    # Coordinate wrapping
    ###########################################################################

    def test_wrap_x_coordinate(self) -> None:
        framebuffer = create_framebuffer()

        framebuffer.set_pixel(DISPLAY_WIDTH, 0, True)

        self.assertTrue(framebuffer.get_pixel(0, 0))

    def test_wrap_y_coordinate(self) -> None:
        framebuffer = create_framebuffer()

        framebuffer.set_pixel(0, DISPLAY_HEIGHT, True)

        self.assertTrue(framebuffer.get_pixel(0, 0))

    def test_negative_coordinates_wrap(self) -> None:
        framebuffer = create_framebuffer()

        framebuffer.set_pixel(-1, -1, True)

        self.assertTrue(
            framebuffer.get_pixel(
                DISPLAY_WIDTH - 1,
                DISPLAY_HEIGHT - 1,
            )
        )

    ###########################################################################
    # Reset
    ###########################################################################

    def test_reset(self) -> None:
        framebuffer = create_framebuffer()

        framebuffer.set_pixel(1, 2, True)
        framebuffer.set_pixel(10, 20, True)

        framebuffer.reset()

        for y in range(DISPLAY_HEIGHT):
            for x in range(DISPLAY_WIDTH):
                self.assertFalse(framebuffer.get_pixel(x, y))

    ###########################################################################
    # Pixel buffer
    ###########################################################################

    def test_pixels_returns_framebuffer(self) -> None:
        framebuffer = create_framebuffer()

        framebuffer.set_pixel(3, 4, True)

        pixels = framebuffer.pixels()

        self.assertTrue(pixels[4, 3])


if __name__ == "__main__":
    unittest.main(verbosity=2)
