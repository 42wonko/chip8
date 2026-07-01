"""
@file chip8framebuffer.py

@brief CHIP-8 framebuffer.

@details
Implements the 64×32 monochrome display memory of the CHIP-8 virtual
machine.

Pixels are stored as a NumPy array of boolean values. Drawing follows
the original CHIP-8 behaviour using XOR rendering and reports whether
any pixel changed from set to cleared (collision).

@author
Michael Dlubatz

@copyright
MIT License
"""

from __future__ import annotations

import numpy as np
import numpy.typing as npt

from emulator.constants import DISPLAY_HEIGHT, DISPLAY_WIDTH


class Chip8Framebuffer:
    """
    @brief CHIP-8 framebuffer.
    """
    def __init__(self) -> None:
        """
        @brief Construct an empty framebuffer.
        """

        self._pixels: npt.NDArray[np.bool_] = np.zeros( (DISPLAY_HEIGHT, DISPLAY_WIDTH), dtype=np.bool_)


    ###########################################################################
    # Public interface
    ###########################################################################
    def reset(self) -> None:
        """
        @brief Clear the framebuffer.
        """
        self._pixels.fill(False)


    def clear(self) -> None:
        """
        @brief Clear the framebuffer.
        """
        self.reset()


    def get_pixel(self, x: int, y: int) -> bool:
        """
        @brief Return one pixel.

        @param x
            X coordinate.

        @param y
            Y coordinate.

        @return
            Pixel state.
        """
        x %= DISPLAY_WIDTH
        y %= DISPLAY_HEIGHT
        return bool(self._pixels[y, x])


    def set_pixel( self, x: int, y: int, value: bool) -> None:
        """
        @brief Set one pixel.

        @param x
            X coordinate.

        @param y
            Y coordinate.

        @param value
            New pixel value.
        """
        x %= DISPLAY_WIDTH
        y %= DISPLAY_HEIGHT
        self._pixels[y, x] = value


    def xor_pixel( self, x: int, y: int) -> bool:
        """
        @brief Toggle a pixel.

        @details
        Performs XOR drawing as required by the CHIP-8 instruction set.

        @param x
            X coordinate.

        @param y
            Y coordinate.

        @return
            True if the pixel changed from set to cleared -> collision.
        """
        x %= DISPLAY_WIDTH
        y %= DISPLAY_HEIGHT

        collision: bool = bool(self._pixels[y, x])
        self._pixels[y, x] = not self._pixels[y, x]
        return collision


    def pixels(self) -> npt.NDArray[np.bool_]:
        """
        @brief Return the framebuffer image.

        @return
            Read-only view of the framebuffer.
        """
        return self._pixels.view()

