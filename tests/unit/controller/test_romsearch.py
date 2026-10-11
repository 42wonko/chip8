"""Tests for searching byte sequences in ROM data."""

from __future__ import annotations

import unittest

from controller.romsearch import find_byte_sequences


class TestFindByteSequences(unittest.TestCase):
    def test_returns_all_matching_offsets(self) -> None:
        data = bytes.fromhex("A2 30 A2 30")
        needle = bytes.fromhex("A2 30")
        self.assertEqual(find_byte_sequences(data, needle), [0, 2])

    def test_returns_overlapping_matches(self) -> None:
        self.assertEqual(find_byte_sequences(bytes.fromhex("AA AA AA"), bytes.fromhex("AA AA")), [0, 1])

    def test_returns_empty_list_when_not_found(self) -> None:
        self.assertEqual(find_byte_sequences(bytes.fromhex("00 E0"), bytes.fromhex("A2 30")), [])

    def test_rejects_empty_needle(self) -> None:
        with self.assertRaises(ValueError):
            find_byte_sequences(b"\x00\xE0", b"")


if __name__ == "__main__":
    unittest.main()
