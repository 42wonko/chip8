"""End-to-end assembler tests for Super-CHIP 1.1 instructions."""

import unittest

from assembler.assembler import Assembler
from assembler.classicparser import ClassicParser
from chip8.isa.superchip11isa import SuperChip11InstructionSetArchitecture
from controller.diagnostics import AssemblerDiagnostics


class TestSuperChip11Assembler(unittest.TestCase):
    """Verify parsing, semantic validation, and encoding for SC11 opcodes."""

    def setUp(self) -> None:
        self.isa = SuperChip11InstructionSetArchitecture()
        self.diagnostics = AssemblerDiagnostics()
        self.assembler = Assembler(
            self.diagnostics.reporter(), self.isa, ClassicParser(self.isa)
        )

    def test_assemble_scrolling_instructions_emits_expected_bytes(self) -> None:
        result = self.assembler.assemble("SCD 0\nSCD 15\nSCR\nSCL")

        self.assertTrue(result.success)
        self.assertEqual(
            result.binary_image,
            bytes.fromhex("00 C0 00 CF 00 FB 00 FC"),
        )

    def test_assemble_accepts_schip11_source_target_directive(self) -> None:
        result = self.assembler.assemble("TARGET SCHIP11\nSCD 3\nSCR\nSCL")

        self.assertTrue(result.success)
        self.assertEqual(result.binary_image, bytes.fromhex("00 C3 00 FB 00 FC"))

    def test_assemble_rejects_scd_row_count_outside_nibble(self) -> None:
        for rows in ("-1", "16"):
            with self.subTest(rows=rows):
                result = self.assembler.assemble(f"SCD {rows}")
                self.assertFalse(result.success)
                self.assertIsNone(result.binary_image)
                self.assertTrue(result.diagnostics)
                if rows == "16":
                    self.assertTrue(
                        any(
                            "SCD row count must be in the range 0 to 15."
                            in diagnostic.message
                            for diagnostic in result.diagnostics
                        )
                    )

    def test_assemble_rejects_operands_on_zero_operand_scroll_mnemonics(self) -> None:
        for source in ("SCR 1", "SCL 1"):
            with self.subTest(source=source):
                result = self.assembler.assemble(source)
                self.assertFalse(result.success)
                self.assertIsNone(result.binary_image)
