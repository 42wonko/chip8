import tempfile
import unittest
from pathlib import Path

from PyQt6.QtCore import QSettings, Qt

from controller.keyboardmap import KeyboardMap


class TestKeyboardMap(unittest.TestCase):
    def setUp(self) -> None:
        self.keyboard_map = KeyboardMap()

    def test_default_mapping_contains_all_chip8_keys(self) -> None:
        self.assertEqual(set(self.keyboard_map._mapping), set(range(16)))

        host_keys = [
            self.keyboard_map.host_key(chip8_key)
            for chip8_key in range(16)
        ]
        self.assertEqual(len(set(host_keys)), 16)

    def test_chip8_key_returns_none_for_unmapped_host_key(self) -> None:
        self.assertIsNone(self.keyboard_map.chip8_key(0))

    def test_chip8_key_returns_matching_key(self) -> None:
        for chip8_key in range(16):
            with self.subTest(chip8_key=chip8_key):
                host_key = self.keyboard_map.host_key(chip8_key)
                self.assertEqual(self.keyboard_map.chip8_key(host_key), chip8_key)

    def test_host_key_returns_assigned_host_key(self) -> None:
        self.assertEqual(
            self.keyboard_map.host_key(0x1),
            Qt.Key.Key_1
        )

    def test_host_key_raises_for_unknown_chip8_key(self) -> None:
        with self.assertRaises(KeyError):
            self.keyboard_map.host_key(16)

    def test_set_host_key_changes_assignment(self) -> None:
        self.keyboard_map.set_host_key(0x1, Qt.Key.Key_Z)

        self.assertEqual(self.keyboard_map.host_key(0x1), Qt.Key.Key_Z)
        self.assertEqual(self.keyboard_map.chip8_key(Qt.Key.Key_Z), 0x1)

    def test_set_mapping_to_unused_host_key(self) -> None:
        old_host_key = self.keyboard_map.host_key(0x1)

        self.keyboard_map.set_mapping(0x1, Qt.Key.Key_Z)

        self.assertEqual(self.keyboard_map.host_key(0x1), Qt.Key.Key_Z)
        self.assertIsNone(self.keyboard_map.chip8_key(old_host_key))

    def test_set_mapping_swaps_existing_assignments(self) -> None:
        first_host_key = self.keyboard_map.host_key(0x1)
        second_host_key = self.keyboard_map.host_key(0x2)

        self.keyboard_map.set_mapping(0x1, second_host_key)

        self.assertEqual(self.keyboard_map.host_key(0x1), second_host_key)
        self.assertEqual(self.keyboard_map.host_key(0x2), first_host_key)
        self.assertEqual(self.keyboard_map.chip8_key(first_host_key), 0x2)
        self.assertEqual(self.keyboard_map.chip8_key(second_host_key), 0x1)

    def test_set_mapping_to_current_host_key_preserves_mapping(self) -> None:
        original = self.keyboard_map.host_key(0x1)

        self.keyboard_map.set_mapping(0x1, original)

        self.assertEqual(self.keyboard_map.host_key(0x1), original)
        self.assertEqual(self.keyboard_map.chip8_key(original), 0x1)

    def test_write_settings_persists_all_mappings(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            filename = str(Path(directory) / "settings.ini")
            settings = QSettings(filename, QSettings.Format.IniFormat)

            self.keyboard_map.write_settings(settings)
            settings.sync()

            for chip8_key in range(16):
                with self.subTest(chip8_key=chip8_key):
                    value = settings.value(f"keyboard/key{chip8_key:X}")
                    self.assertEqual(
                        int(value),
                        int(self.keyboard_map.host_key(chip8_key))
                    )

    def test_read_settings_restores_custom_mapping(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            filename = str(Path(directory) / "settings.ini")
            settings = QSettings(filename, QSettings.Format.IniFormat)
            settings.setValue("keyboard/key1", int(Qt.Key.Key_Z))
            settings.sync()

            self.keyboard_map.read_settings(settings)

            self.assertEqual(self.keyboard_map.host_key(0x1), Qt.Key.Key_Z)

    def test_read_settings_preserves_defaults_for_missing_values(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            filename = str(Path(directory) / "settings.ini")
            settings = QSettings(filename, QSettings.Format.IniFormat)
            original = {
                key: self.keyboard_map.host_key(key)
                for key in range(16)
            }

            self.keyboard_map.read_settings(settings)

            for chip8_key, host_key in original.items():
                with self.subTest(chip8_key=chip8_key):
                    self.assertEqual(
                        self.keyboard_map.host_key(chip8_key),
                        host_key
                    )

    def test_key_name_returns_readable_name(self) -> None:
        self.assertEqual(
            KeyboardMap.key_name(Qt.Key.Key_A),
            "A"
        )

    def test_key_name_falls_back_to_hex_for_unknown_key(self) -> None:
        self.assertEqual(KeyboardMap.key_name(0), "0x0")


if __name__ == "__main__":
    unittest.main()
