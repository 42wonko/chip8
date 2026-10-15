"""End-to-end assembler tests for the Super-CHIP 1.0 ISA."""

import unittest

from assembler.assembler import Assembler
from assembler.classicparser import ClassicParser
from chip8.isa.superchip10isa import SuperChip10InstructionSetArchitecture
from controller.diagnostics import AssemblerDiagnostics


class TestSuperChip10Assembler(unittest.TestCase):
    """Verify Super-CHIP-specific syntax reaches the encoded binary image."""

    def setUp(self) -> None:
        self._isa = SuperChip10InstructionSetArchitecture()
        self._diagnostics = AssemblerDiagnostics()
        self._assembler = Assembler(
            self._diagnostics.reporter(),
            self._isa,
            ClassicParser(self._isa),
        )

    def test_superchip_zero_operand_instructions(self) -> None:
        result = self._assembler.assemble("LOW\nHIGH\nEXIT")

        self.assertTrue(result.success, result.diagnostics)
        self.assertEqual(result.binary_image, b"\x00\xFE\x00\xFF\x00\xFD")

    def test_superchip_register_offset_jump(self) -> None:
        result = self._assembler.assemble("JP V3, 0x44")

        self.assertTrue(result.success, result.diagnostics)
        self.assertEqual(result.binary_image, b"\xB3\x44")

    def test_superchip_special_loads(self) -> None:
        result = self._assembler.assemble("LD HF, V3\nLD R, V7\nLD V7, R")

        self.assertTrue(result.success, result.diagnostics)
        self.assertEqual(result.binary_image, b"\xF3\x30\xF7\x75\xF7\x85")

    def test_zero_height_draw_uses_superchip_encoding(self) -> None:
        result = self._assembler.assemble("DRW V1, V2, 0")

        self.assertTrue(result.success, result.diagnostics)
        self.assertEqual(result.binary_image, b"\xD1\x20")

    def test_nonzero_height_draw_keeps_classic_encoding(self) -> None:
        result = self._assembler.assemble("DRW V1, V2, 5")

        self.assertTrue(result.success, result.diagnostics)
        self.assertEqual(result.binary_image, b"\xD1\x25")

    def test_classic_jump_syntax_remains_available(self) -> None:
        result = self._assembler.assemble("JP 0x234")

        self.assertTrue(result.success, result.diagnostics)
        self.assertEqual(result.binary_image, b"\x12\x34")


if __name__ == "__main__":
    unittest.main(verbosity=2)
