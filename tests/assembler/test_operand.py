"""
@file test_operand.py

@brief Unit tests for evaluated assembler operands.
"""

import unittest

from assembler.operand import AssemblerOperand, AssemblerOperandType


class AssemblerOperandTest(unittest.TestCase):
    """
    @brief Tests for evaluated assembler operands.
    """

    def test_register_operand(self) -> None:
        operand = AssemblerOperand( type=AssemblerOperandType.REGISTER, value=3)
        self.assertEqual( operand.type, AssemblerOperandType.REGISTER)
        self.assertEqual( operand.value, 3)

    def test_value_operand(self) -> None:
        operand = AssemblerOperand( type=AssemblerOperandType.VALUE, value=42)
        self.assertEqual( operand.type, AssemblerOperandType.VALUE)
        self.assertEqual( operand.value, 42)

    def test_address_operand(self) -> None:
        operand = AssemblerOperand( type=AssemblerOperandType.ADDRESS, value=0x234)
        self.assertEqual( operand.type, AssemblerOperandType.ADDRESS)
        self.assertEqual( operand.value, 0x234)

    def test_operand_is_immutable(self) -> None:
        operand = AssemblerOperand( type=AssemblerOperandType.VALUE, value=42)
        with self.assertRaises(AttributeError):
            operand.value = 43

    def test_index_register_operand(self) -> None:
        operand = AssemblerOperand( type=AssemblerOperandType.INDEX_REGISTER, value=0)
        self.assertEqual( operand.type, AssemblerOperandType.INDEX_REGISTER)
        self.assertEqual( operand.value, 0)

    def test_delay_register_operand(self) -> None:
        operand = AssemblerOperand( type=AssemblerOperandType.DELAY_REGISTER, value=0)
        self.assertEqual( operand.type, AssemblerOperandType.DELAY_REGISTER)
        self.assertEqual( operand.value, 0)

    def test_sound_register_operand(self) -> None:
        operand = AssemblerOperand( type=AssemblerOperandType.SOUND_REGISTER, value=0)
        self.assertEqual( operand.type, AssemblerOperandType.SOUND_REGISTER)
        self.assertEqual( operand.value, 0)

    def test_key_operand(self) -> None:
        operand = AssemblerOperand( type=AssemblerOperandType.KEY, value=0)
        self.assertEqual( operand.type, AssemblerOperandType.KEY)
        self.assertEqual( operand.value, 0)

    def test_bcd_register_operand(self) -> None:
        operand = AssemblerOperand( type=AssemblerOperandType.BCD_REGISTER, value=0)
        self.assertEqual( operand.type, AssemblerOperandType.BCD_REGISTER)
        self.assertEqual( operand.value, 0)

    def test_font_register_operand(self) -> None:
        operand = AssemblerOperand( type=AssemblerOperandType.FONT_REGISTER, value=0)
        self.assertEqual( operand.type, AssemblerOperandType.FONT_REGISTER)
        self.assertEqual( operand.value, 0)


