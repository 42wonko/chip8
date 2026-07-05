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
        @brief Test the assembly representation of all CHIP-8 instructions.
        """
        cases = (
            # 0x0
            (0x00E0, "CLS"),
            (0x00EE, "RET"),
            (0x0123, "SYS 123"),

            # 0x1
            (0x1234, "JP 234"),

            # 0x2
            (0x2345, "CALL 345"),

            # 0x3
            (0x3AAB, "SE VA, AB"),

            # 0x4
            (0x4AAB, "SNE VA, AB"),

            # 0x5
            (0x5AB0, "SE VA, VB"),

            # 0x6
            (0x6AAB, "LD VA, AB"),

            # 0x7
            (0x7AAB, "ADD VA, AB"),

            # 0x8
            (0x8AB0, "LD VA, VB"),
            (0x8AB1, "OR VA, VB"),
            (0x8AB2, "AND VA, VB"),
            (0x8AB3, "XOR VA, VB"),
            (0x8AB4, "ADD VA, VB"),
            (0x8AB5, "SUB VA, VB"),
            (0x8AB6, "SHR VA"),
            (0x8AB7, "SUBN VA, VB"),
            (0x8ABE, "SHL VA"),

            # 0x9
            (0x9AB0, "SNE VA, VB"),

            # 0xA
            (0xA234, "LD I, 234"),

            # 0xB
            (0xB234, "JP V0, 234"),

            # 0xC
            (0xCAAB, "RND VA, AB"),

            # 0xD
            (0xDABC, "DRW VA, VB, C"),

            # 0xE
            (0xEA9E, "SKP VA"),
            (0xEAA1, "SKNP VA"),

            # 0xF
            (0xFA07, "LD VA, DT"),
            (0xFA0A, "LD VA, K"),
            (0xFA15, "LD DT, VA"),
            (0xFA18, "LD ST, VA"),
            (0xFA1E, "ADD I, VA"),
            (0xFA29, "LD F, VA"),
            (0xFA33, "LD B, VA"),
            (0xFA55, "LD [I], VA"),
            (0xFA65, "LD VA, [I]"),
        )
        for opcode, expected in cases:
            with self.subTest(opcode=f"{opcode:04X}"):
                instruction = Instruction.decode(0x0200, opcode)
                self.assertEqual(str(instruction), expected)

    def test_invalid_mnemonic_representation(self) -> None:
        """
        @brief Test the assembly representation of unsupported instructions.
        """
        cases = (
            (0x5AB1, "DATA 5AB1"),
            (0x8AB8, "DATA 8AB8"),
            (0x9AB1, "DATA 9AB1"),
            (0xEA00, "DATA EA00"),
            (0xFAFF, "DATA FAFF"),
        )
        for opcode, expected in cases:
            with self.subTest(opcode=f"{opcode:04X}"):
                instruction = Instruction.decode(0x0200, opcode)
                self.assertEqual(str(instruction), expected)


if __name__ == "__main__":
    unittest.main(verbosity=2)

