"""
@file test_memorytablemodel.py

@brief Tests for the memory table model.
"""

from __future__ import annotations

import unittest

from PyQt6.QtWidgets import QApplication

from gui.memorytablemodel import MemoryTableModel


class TestMemoryTableModel(unittest.TestCase):
    """Tests for MemoryTableModel highlight and navigation behavior."""

    @classmethod
    def setUpClass(cls) -> None:
        """Create the Qt application required by the model tests."""
        cls._application = QApplication.instance()
        if cls._application is None:
            cls._application = QApplication([])

    def setUp(self) -> None:
        self.model = MemoryTableModel()
        self.scrolled_addresses: list[int] = []
        self.model.scroll_to_address.connect(self.scrolled_addresses.append)

    def test_highlight_scrolls_to_address(self) -> None:
        """A new highlighted address should be brought into view."""
        self.model._set_highlight(0x300, 0x300)

        self.assertEqual(self.scrolled_addresses, [0x300])

    def test_repeated_write_address_still_requests_scroll(self) -> None:
        """Repeated writes should refocus the address after manual scrolling."""
        self.model._set_highlight(0x300, 0x300)
        self.model._set_highlight(0x300, 0x300)

        self.assertEqual(self.scrolled_addresses, [0x300, 0x300])

    def test_clearing_highlight_does_not_request_scroll(self) -> None:
        """Clearing the highlight should not navigate the memory view."""
        self.model._set_highlight(0x300, 0x300)
        self.scrolled_addresses.clear()

        self.model.clear_highlight()

        self.assertEqual(self.scrolled_addresses, [])
