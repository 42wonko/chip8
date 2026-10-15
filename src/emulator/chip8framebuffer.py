"""
@file chip8framebuffer.py

@brief CHIP-8 framebuffer.

@details
Implements the monochrome display memory of the CHIP-8 virtual machine.

The framebuffer supports both the Classic CHIP-8 resolution (64×32) and
Super-CHIP high resolution (128×64). The backing buffer retains pixel data
when the active resolution changes, which is required by the original
Super-CHIP 1.x display-mode behavior.

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

from controller.applicationlogreporter import ApplicationLogReporter
from controller.diagnostics import DiagnosticReporter
from emulator.constants import DISPLAY_HEIGHT, DISPLAY_WIDTH

SUPERCHIP_DISPLAY_WIDTH = 128
SUPERCHIP_DISPLAY_HEIGHT = 64


class Chip8Framebuffer:
    """
    @brief CHIP-8 framebuffer.
    """
    def __init__(self, diagnostics: DiagnosticReporter, logger: ApplicationLogReporter) -> None:
        self._diagnostics = diagnostics
        self._logger = logger
        """
        @brief Construct an empty framebuffer.
        """

        self._display_width = DISPLAY_WIDTH
        self._display_height = DISPLAY_HEIGHT
        self._pixels: npt.NDArray[np.bool_] = np.zeros(
            (SUPERCHIP_DISPLAY_HEIGHT, SUPERCHIP_DISPLAY_WIDTH),
            dtype=np.bool_,
        )


    ###########################################################################
    # Public interface
    ###########################################################################
    def reset(self) -> None:
        """Clear the framebuffer and restore the Classic resolution."""
        self._pixels.fill(False)
        self._display_width = DISPLAY_WIDTH
        self._display_height = DISPLAY_HEIGHT


    def clear(self) -> None:
        """Clear all pixels without changing the active resolution."""
        self._pixels.fill(False)


    @property
    def width(self) -> int:
        """Return the active display width in pixels."""
        return self._display_width

    @property
    def height(self) -> int:
        """Return the active display height in pixels."""
        return self._display_height

    def set_resolution(self, width: int, height: int) -> None:
        """Select the active display resolution without clearing pixels.

        Only the two resolutions supported by Classic CHIP-8 and
        Super-CHIP are accepted.
        """
        if (width, height) not in {
            (DISPLAY_WIDTH, DISPLAY_HEIGHT),
            (SUPERCHIP_DISPLAY_WIDTH, SUPERCHIP_DISPLAY_HEIGHT),
        }:
            raise ValueError(f"Unsupported display resolution: {width}x{height}.")

        self._display_width = width
        self._display_height = height

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
        x %= self._display_width
        y %= self._display_height
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
        x %= self._display_width
        y %= self._display_height
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
        x %= self._display_width
        y %= self._display_height

        collision: bool = bool(self._pixels[y, x])
        self._pixels[y, x] = not self._pixels[y, x]
        return collision


    def pixels(self) -> npt.NDArray[np.bool_]:
        """
        @brief Return the framebuffer image.

        @return
            Read-only view of the framebuffer.
        """
        view = self._pixels[:self._display_height, :self._display_width].view()
        view.flags.writeable = False
        return view

