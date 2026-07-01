"""
@file test_instruction.py

@brief Tests for the CHIP-8 instruction decoder.
"""

from emulator.instruction import Instruction


def test_decode_fields() -> None:
    """
    @brief Decode all instruction fields.
    """
    instruction = Instruction.decode( 0x0200, 0x6A05)
    assert instruction.address == 0x0200
    assert instruction.opcode == 0x6A05
    assert instruction.family == 0x6
    assert instruction.x == 0xA
    assert instruction.y == 0x0
    assert instruction.n == 0x5
    assert instruction.nn == 0x05
    assert instruction.nnn == 0x0A05
