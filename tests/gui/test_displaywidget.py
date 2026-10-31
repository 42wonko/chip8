"""
@file test_displaywidget.py

@brief Tests for the CHIP-8 display widget.
"""

from __future__ import annotations

import unittest

import numpy as np
from PyQt6.QtCore import QRect, QSize, Qt
from PyQt6.QtGui import QColor, QImage, QPainter
from PyQt6.QtWidgets import QApplication

from emulator.constants import DISPLAY_HEIGHT, DISPLAY_WIDTH
from gui.displaywidget import DisplayWidget


class TestDisplayWidget(unittest.TestCase):
    """Tests for DisplayWidget using real Qt objects."""

    @classmethod
    def setUpClass(cls) -> None:
        """Create the Qt application required by widget tests."""
        cls._application = QApplication.instance()
        if cls._application is None:
            cls._application = QApplication([])

    def setUp(self) -> None:
        """Create a fresh display widget for each test."""
        self.widget = DisplayWidget()

    def tearDown(self) -> None:
        """Dispose of the display widget after each test."""
        self.widget.close()
        self.widget.deleteLater()

    def test_initial_image_is_background_color(self) -> None:
        """The initial image should be the default white display."""
        image = self.widget._image
        self.assertEqual(image.size(), QSize(DISPLAY_WIDTH, DISPLAY_HEIGHT))
        self.assertEqual( image.pixelColor(0, 0), QColor(Qt.GlobalColor.white))
        self.assertIsNone(self.widget._framebuffer)

    def test_size_hints_use_default_display_dimensions(self) -> None:
        """The size hints should use the default display dimensions."""
        self.assertEqual( self.widget.minimumSizeHint(), QSize(DISPLAY_WIDTH, DISPLAY_HEIGHT))
        self.assertEqual( self.widget.sizeHint(), QSize(DISPLAY_WIDTH * 10, DISPLAY_HEIGHT * 10))

    def test_set_framebuffer_converts_pixels_to_image(self) -> None:
        """Set pixels should become black and unset pixels should stay white."""
        framebuffer = np.array( [[True, False], [False, True]], dtype=np.bool_)
        self.widget.set_framebuffer(framebuffer)
        self.assertIs(self.widget._framebuffer, framebuffer)
        self.assertEqual(self.widget._image.size(), QSize(2, 2))
        self.assertEqual( self.widget._image.pixelColor(0, 0), QColor(Qt.GlobalColor.black))
        self.assertEqual( self.widget._image.pixelColor(1, 0), QColor(Qt.GlobalColor.white))
        self.assertEqual( self.widget._image.pixelColor(0, 1), QColor(Qt.GlobalColor.white))
        self.assertEqual( self.widget._image.pixelColor(1, 1), QColor(Qt.GlobalColor.black))
        np.testing.assert_array_equal( framebuffer, np.array([[True, False], [False, True]], dtype=np.bool_))

    def test_set_framebuffer_updates_dimensions_and_size_hints(self) -> None:
        """A framebuffer with different dimensions should resize the image."""
        self.widget.set_framebuffer(np.zeros((8, 12), dtype=np.bool_))
        self.assertEqual(self.widget._image.size(), QSize(12, 8))
        self.assertEqual(self.widget.minimumSizeHint(), QSize(12, 8))
        self.assertEqual(self.widget.sizeHint(), QSize(120, 80))

    def test_refresh_reads_changes_from_existing_framebuffer(self) -> None:
        """Refresh should rebuild the image from the referenced framebuffer."""
        framebuffer = np.zeros((2, 2), dtype=np.bool_)
        self.widget.set_framebuffer(framebuffer)
        framebuffer[1, 0] = True
        self.widget.refresh()
        self.assertEqual( self.widget._image.pixelColor(0, 1), QColor(Qt.GlobalColor.black))

    def test_clear_discards_framebuffer_and_restores_default_dimensions(self) -> None:
        """Clear should reset both the cached image and display dimensions."""
        self.widget.set_framebuffer(np.ones((8, 12), dtype=np.bool_))
        self.widget.clear()
        self.assertIsNone(self.widget._framebuffer)
        self.assertEqual(self.widget._image.size(), QSize(DISPLAY_WIDTH, DISPLAY_HEIGHT))
        self.assertEqual(self.widget.minimumSizeHint(), QSize(DISPLAY_WIDTH, DISPLAY_HEIGHT))
        self.assertEqual( self.widget._image.pixelColor(0, 0), QColor(Qt.GlobalColor.white))

    def test_update_image_without_framebuffer_fills_background(self) -> None:
        """Updating without a framebuffer should leave a blank image."""
        self.widget._image.fill(QColor(Qt.GlobalColor.black))
        self.widget._update_image()
        self.assertEqual( self.widget._image.pixelColor(0, 0), QColor(Qt.GlobalColor.white))

    def test_calculate_scale_uses_largest_fitting_integer_scale(self) -> None:
        """Scaling should be integral and constrained by both dimensions."""
        self.widget.resize(640, 320)
        self.assertEqual(self.widget._calculate_scale(), 10)
        self.widget.resize(640, 200)
        self.assertEqual(self.widget._calculate_scale(), 6)

    def test_calculate_scale_never_returns_less_than_one(self) -> None:
        """Small widget dimensions should still produce a scale of one."""
        self.widget.resize(10, 10)
        self.assertEqual(self.widget._calculate_scale(), 1)

    def test_calculate_target_rect_centers_scaled_display(self) -> None:
        """The target rectangle should be centered at the integer scale."""
        self.widget.resize(700, 400)
        self.assertEqual( self.widget._calculate_target_rect(), QRect(30, 40, 640, 320))

    def test_paint_event_draws_image_and_background(self) -> None:
        self.widget.resize(7, 5)
        framebuffer = np.array([[1]], dtype=np.uint8)
        self.widget.set_framebuffer(framebuffer)
        self.widget.show()
        QApplication.processEvents()
        image = QImage(7, 5, QImage.Format.Format_RGB32)
        image.fill(Qt.GlobalColor.transparent)
        self.widget.render(image)
        self.assertEqual( image.pixelColor(0, 0), self.widget._background_color)
        self.assertEqual( image.pixelColor(3, 2), self.widget._foreground_color)


if __name__ == "__main__":
    unittest.main()
