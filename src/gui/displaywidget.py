"""
@file displaywidget.py

@brief CHIP-8 display widget.

This widget renders the current CHIP-8 framebuffer using a cached QImage.
The widget is purely a rendering component and contains no emulator logic.

@author
    Michael Dlubatz

@copyright
    MIT License
"""

from __future__ import annotations

from PyQt6.QtCore import QRect, QSize, Qt
from PyQt6.QtGui import QColor, QImage, QPainter, QPaintEvent
from PyQt6.QtWidgets import QWidget

from emulator.chip8types import Framebuffer
from emulator.constants import DISPLAY_HEIGHT, DISPLAY_WIDTH


class DisplayWidget(QWidget):
    """
    @brief Widget that renders the CHIP-8 display.

    The widget displays the framebuffer supplied by the emulator.
    It does not own the framebuffer and never modifies it.
    """

    def __init__( self, parent: QWidget | None = None) -> None:
        """
        @brief Construct the display widget.

        @param parent
            Parent Qt widget.
        """
        super().__init__(parent)

        self._display_width     = DISPLAY_WIDTH                 # TODO: we should support dynamic resolutions in the future
        self._display_height    = DISPLAY_HEIGHT

        self._foreground_color  = QColor(Qt.GlobalColor.black)  # TODO: these colors should be configurable in the future
        self._background_color  = QColor(Qt.GlobalColor.white)

        self._framebuffer: Framebuffer | None = None

        self._image = QImage( self._display_width, self._display_height, QImage.Format.Format_ARGB32)

        self.clear()


    def clear(self) -> None:
        """
        @brief Clear the displayed image.

        The framebuffer reference is discarded and the cached image is
        filled with the background color.
        """
        self._framebuffer = None
        self._image.fill(self._background_color)


    def set_framebuffer( self, framebuffer: Framebuffer) -> None:
        """
        @brief Set the framebuffer to display.

        The framebuffer remains owned by the emulator. The widget treats
        it as read-only.

        @param framebuffer
            CHIP-8 framebuffer.
        """
        self._framebuffer = framebuffer
        self._update_image()
        self.update()


    def minimumSizeHint(self) -> QSize:
        """
        @brief Return the minimum recommended widget size.

        @return
            Minimum widget size.
        """
        return QSize( self._display_width, self._display_height)


    def sizeHint(self) -> QSize:
        """
        @brief Return the preferred widget size.

        @return
            Preferred widget size.
        """
        return QSize( self._display_width * 10, self._display_height * 10)


    def paintEvent( self, event: QPaintEvent | None) -> None:
        """
        @brief Paint the display.

        @param event
            Qt paint event.
        """
        del event

        painter = QPainter(self)

        painter.fillRect( self.rect(), self._background_color)
        target = self._calculate_target_rect()
        painter.drawImage( target, self._image)

    def refresh(self) -> None:
        """
        @brief Rebuild image from framebuffer and repaint.
        """

        self._update_image()
        self.update()


    def _calculate_scale(self) -> int:
        """
        @brief Calculate the integer display scaling factor.

        @return
            Integer scaling factor.
        """
        return max( 1, min( self.width() // self._display_width, self.height() // self._display_height))


    def _calculate_target_rect(self) -> QRect:
        """
        @brief Calculate the destination rectangle.

        The display is centered while preserving the aspect ratio using
        integer scaling.

        @return
            Target rectangle.
        """
        scale = self._calculate_scale()

        width = self._display_width * scale
        height = self._display_height * scale

        x = (self.width() - width) // 2
        y = (self.height() - height) // 2

        return QRect( x, y, width, height)


    def _update_image(self) -> None:
        """
        @brief Update the cached image from the framebuffer.
        """
        if self._framebuffer is None:
            self._image.fill(self._background_color)
            return

        for y in range(self._display_height):
            for x in range(self._display_width):
                color = ( self._foreground_color if self._framebuffer[y, x] else self._background_color)
                self._image.setPixelColor( x, y, color)


