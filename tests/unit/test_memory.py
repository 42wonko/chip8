"""
@file test_memory.py
@brief Test for the CHIP-8 memory.
"""
import unittest

from emulator.constants import MEMORY_SIZE
from tests.helpers import create_memory


class TestcreateMemory(unittest.TestCase):
    def test_read_write_byte(self) -> None:
        memory = create_memory()
        memory.write_byte( 0x234, 0xAB)
        self.assertEqual(memory.read_byte( 0x234), 0xAB)

    def test_read_write_word(self) -> None:
        memory = create_memory()
        memory.write_byte( 0x300, 0x12)
        memory.write_byte( 0x301, 0x34)
        self.assertEqual( (memory.read_byte( 0x300) << 8) | memory.read_byte(0x301), 0x1234)


    def test_load_rom(self) -> None:
        memory = create_memory()
        rom = bytes([ 0x60, 0x01, 0x61, 0x02 ])
        memory.load_rom(rom)
        self.assertEqual( (memory.read_byte( 0x200) << 8) | memory.read_byte(0x201), 0x6001)
        self.assertEqual( (memory.read_byte( 0x202) << 8) | memory.read_byte(0x203), 0x6102)

    def test_memory_size(self) -> None:
        memory = create_memory()
        self.assertEqual(memory.size(), MEMORY_SIZE)

    def test_adderss_validation(self) -> None:
        memory = create_memory()
        with self.assertRaises(IndexError):
            memory.read_byte(-1)
        with self.assertRaises(IndexError):
            memory.read_byte(MEMORY_SIZE+1)

if __name__ == "__main__":
    unittest.main(verbosity=2)

