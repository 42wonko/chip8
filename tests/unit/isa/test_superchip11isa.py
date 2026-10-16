"""Unit tests for the Super-CHIP 1.1 instruction set architecture."""

import unittest
from unittest.mock import MagicMock

from assembler.operand import AssemblerOperand, AssemblerOperandType
from chip8.isa.instructionid import InstructionId
from chip8.isa.isa import ControlFlow
from chip8.isa.superchip10isa import SuperChip10InstructionSetArchitecture
from chip8.isa.superchip11isa import SuperChip11InstructionSetArchitecture
from emulator.chip8framebuffer import (
    SUPERCHIP_DISPLAY_HEIGHT,
    SUPERCHIP_DISPLAY_WIDTH,
    Chip8Framebuffer,
)
from emulator.constants import DISPLAY_HEIGHT, DISPLAY_WIDTH


class TestSuperChip11InstructionSetArchitecture(unittest.TestCase):
    def setUp(self) -> None:
        self.machine = MagicMock()
        self.machine.framebuffer = Chip8Framebuffer(MagicMock(), MagicMock())
        self.isa = SuperChip11InstructionSetArchitecture()

    def test_assembler_encodes_superchip11_scrolling_instructions(self) -> None:
        cases = (
            ("SCD", (AssemblerOperand(AssemblerOperandType.VALUE, 0),), InstructionId.SCROLL_DOWN, 0x00C0),
            ("SCD", (AssemblerOperand(AssemblerOperandType.VALUE, 15),), InstructionId.SCROLL_DOWN, 0x00CF),
            ("SCR", (), InstructionId.SCROLL_RIGHT, 0x00FB),
            ("SCL", (), InstructionId.SCROLL_LEFT, 0x00FC),
        )
        for mnemonic, operands, expected_id, expected_opcode in cases:
            with self.subTest(mnemonic=mnemonic, operands=operands):
                instruction = self.isa.create_assembler_instruction(mnemonic, operands)
                self.assertIs(instruction.id, expected_id)
                self.assertEqual(self.isa.encode(instruction), expected_opcode)

    def test_scd_rejects_invalid_row_counts(self) -> None:
        for rows in (-1, 16):
            with self.subTest(rows=rows):
                with self.assertRaises(ValueError):
                    self.isa.create_assembler_instruction(
                        "SCD", (AssemblerOperand(AssemblerOperandType.VALUE, rows),)
                    )

    def test_superchip10_does_not_advertise_superchip11_assembler_mnemonics(self) -> None:
        isa = SuperChip10InstructionSetArchitecture()
        self.assertNotIn("SCD", isa.assembler_mnemonics())
        self.assertNotIn("SCR", isa.assembler_mnemonics())
        self.assertNotIn("SCL", isa.assembler_mnemonics())

    def test_decodes_scroll_instructions(self) -> None:
        cases = (
            (0x00C0, InstructionId.SCROLL_DOWN),
            (0x00C2, InstructionId.SCROLL_DOWN),
            (0x00CF, InstructionId.SCROLL_DOWN),
            (0x00FB, InstructionId.SCROLL_RIGHT),
            (0x00FC, InstructionId.SCROLL_LEFT),
        )
        for opcode, expected in cases:
            with self.subTest(opcode=f"{opcode:04X}"):
                self.assertIs(self.isa.decode(0x200, opcode).id, expected)

    def test_superchip10_keeps_superchip11_scroll_opcodes_unknown(self) -> None:
        isa = SuperChip10InstructionSetArchitecture()
        for opcode in (0x00C0, 0x00C2, 0x00CF, 0x00FB, 0x00FC):
            with self.subTest(opcode=f"{opcode:04X}"):
                self.assertIs(isa.decode(0x200, opcode).id, InstructionId.UNKNOWN)

    def test_scroll_down_moves_pixels_and_reports_display_change(self) -> None:
        self.machine.framebuffer.set_pixel(3, 1, True)
        instruction = self.isa.decode(0x200, 0x00C2)

        result = self.isa.execute(self.machine, instruction)

        self.assertTrue(result.display_changed)
        self.assertTrue(self.machine.framebuffer.get_pixel(3, 3))
        self.assertFalse(self.machine.framebuffer.get_pixel(3, 1))

    def test_scroll_right_moves_pixels_four_columns(self) -> None:
        self.machine.framebuffer.set_pixel(5, 7, True)
        instruction = self.isa.decode(0x200, 0x00FB)

        result = self.isa.execute(self.machine, instruction)

        self.assertTrue(result.display_changed)
        self.assertTrue(self.machine.framebuffer.get_pixel(9, 7))
        self.assertFalse(self.machine.framebuffer.get_pixel(5, 7))

    def test_scroll_left_moves_pixels_four_columns(self) -> None:
        self.machine.framebuffer.set_pixel(9, 7, True)
        instruction = self.isa.decode(0x200, 0x00FC)

        result = self.isa.execute(self.machine, instruction)

        self.assertTrue(result.display_changed)
        self.assertTrue(self.machine.framebuffer.get_pixel(5, 7))
        self.assertFalse(self.machine.framebuffer.get_pixel(9, 7))

    def test_scroll_instructions_format_and_analyze_as_fallthrough(self) -> None:
        cases = ((0x00C4, "SCD 4"), (0x00FB, "SCR"), (0x00FC, "SCL"))
        for opcode, expected_format in cases:
            with self.subTest(opcode=f"{opcode:04X}"):
                instruction = self.isa.decode(0x200, opcode)
                self.assertEqual(self.isa.format(instruction), expected_format)
                analysis = self.isa.analyze(instruction)
                self.assertIs(analysis.control_flow, ControlFlow.NEXT)
                self.assertEqual(analysis.targets, (0x202,))
                self.assertTrue(analysis.is_code)

    def test_scrolling_uses_active_resolution(self) -> None:
        framebuffer = self.machine.framebuffer
        framebuffer.set_resolution(SUPERCHIP_DISPLAY_WIDTH, SUPERCHIP_DISPLAY_HEIGHT)
        framebuffer.set_pixel(100, 10, True)
        self.isa.execute(self.machine, self.isa.decode(0x200, 0x00FC))
        self.assertTrue(framebuffer.get_pixel(96, 10))

        framebuffer.set_resolution(DISPLAY_WIDTH, DISPLAY_HEIGHT)
        framebuffer.set_pixel(20, 10, True)
        self.isa.execute(self.machine, self.isa.decode(0x200, 0x00FB))
        self.assertFalse(framebuffer.get_pixel(20, 10))
        self.assertTrue(framebuffer.get_pixel(24, 10))
