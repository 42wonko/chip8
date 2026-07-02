"""
@file test_instruction.py

@brief Tests for the CHIP-8 instruction decoder.
"""

import unittest

from emulator.instruction import Instruction


class TestInstruction(unittest.TestCase):
    def test_decode_fields(self) -> None:
        """
        @brief Decode all instruction fields.
        """
        instruction = Instruction.decode( 0x0200, 0x6A05)
        self.assertEqual(instruction.address, 0x0200)
        self.assertEqual(instruction.opcode, 0x6A05)
        self.assertEqual(instruction.family, 0x6)
        self.assertEqual(instruction.x, 0xA)
        self.assertEqual(instruction.y, 0x0)
        self.assertEqual(instruction.n, 0x5)
        self.assertEqual(instruction.nn, 0x05)
        self.assertEqual(instruction.nnn, 0x0A05)


    def test_mnemonic_representation(self) -> None:
        """
        @brief Test exceptions while decoding.
        """
        instruction = Instruction.decode( 0x0200, 0x6A05)
        with self.assertRaises(NotImplementedError):
            str(instruction)

if __name__ == "__main__":
    unittest.main(verbosity=2)

