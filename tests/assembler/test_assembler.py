"""
@file test_assembler.py

@brief Unit tests for the assembler entry point.
"""

import unittest

from assembler.assembler import Assembler
from assembler.options import AssemblyOptions
from chip8.isa.classicisa import ClassicInstructionSetArchitecture
from controller.diagnostic import DiagnosticSource

#from controller.diagnostics import Diagnostics
from controller.diagnostics import AssemblerDiagnostics

#from tests.helpers import create_machine


class TestAssembler(unittest.TestCase):
    """
    @brief Test the assembler entry point.
    """

    def setUp(self) -> None:
#        self._diagnostics = Diagnostics()
        self._diagnostics = AssemblerDiagnostics()
#        machine = create_machine()
        self._isa = ClassicInstructionSetArchitecture()
#        self._assembler = Assembler( self._diagnostics.reporter(DiagnosticSource.ASSEMBLER), self._isa)
        self._assembler = Assembler( self._diagnostics.reporter(), self._isa)


    def test_assembler_can_be_instantiated(self) -> None:
        """
        @brief Verify that the assembler can be instantiated.
        """
        self.assertIsNotNone(self._assembler)


    def test_assemble_returns_result(self) -> None:
        """
        @brief Verify that assemble() returns an assembly result.
        """
        result = self._assembler.assemble(source="")
        self.assertFalse(result.success)
        self.assertEqual(len(result.diagnostics), 0)
        self.assertEqual(len(self._diagnostics), 3)
        messages = [diagnostic.message for diagnostic in self._diagnostics]
        self.assertEqual(
            messages,
            [
                "Started assembly.",
                "Parsing source.",
                "Assembly source is empty."
            ]
        )
        diagnostic = self._diagnostics[2]
        self.assertEqual(diagnostic.source, DiagnosticSource.ASSEMBLER)


    def test_assemble_db(self) -> None:
        result = self._assembler.assemble( "DB 0x12, 0x34")
        self.assertTrue(result.success)
        self.assertEqual(result.binary_image, b"\x12\x34")


    def test_assemble_cls(self) -> None:
        result = self._assembler.assemble( "CLS")
        self.assertTrue(result.success)
        self.assertEqual(result.binary_image, b"\x00\xE0")


    def test_assemble_instruction_with_label(self) -> None:
        result = self._assembler.assemble( "START:\nJP START")
        self.assertTrue(result.success)
        self.assertEqual(result.binary_image, b"\x12\x00")


    def test_assemble_org_and_gap(self) -> None:
        result = self._assembler.assemble(
            "ORG 0x300\n"
            "DB 1\n"
            "ORG 0x303\n"
            "DB 2"
        )
        self.assertTrue(result.success)
        self.assertEqual( result.binary_image, b"\x01\x00\x00\x02")


    def test_label_can_be_referenced_after_case_change(self) -> None:
        """
        @brief Verify that a label can be resolved regardless of its case.
        """
        source = (
            "org 0x200\n"
            "Start:\tCLS\n"
            "jp Start\n"
        )
        result = self._assembler.assemble( source)
        self.assertTrue(result.success)


    def test_assemble_can_generate_listing(self) -> None:
        """
        @brief Verify that assembly can produce an in-memory listing.
        """
        source = (
            "ORG 0x200\n"
            "Start: CLS\n"
            "JP Start\n"
        )
        result = self._assembler.assemble( source, AssemblyOptions(generate_listing=True))
        self.assertTrue(result.success)
        self.assertIsNotNone(result.listing)
        assert result.listing is not None
        self.assertIn("Start: CLS", result.listing)
        self.assertIn("JP Start", result.listing)
        self.assertIn("0200", result.listing)
        self.assertIn("00 E0", result.listing)
        self.assertIn("12 00", result.listing)

    def test_ld_vx_indirect_i(self) -> None:
        result = self._assembler.assemble("LD V2, [I]")
        self.assertTrue(result.success)
        self.assertEqual( result.binary_image, bytes([0xF2, 0x65]))

    def test_ld_indirect_i_vx(self) -> None:
        result = self._assembler.assemble("LD [I], V2")
        self.assertTrue(result.success)
        self.assertEqual( result.binary_image, bytes([0xF2, 0x55]))

    def test_assemble_rnd_instruction(self) -> None:
        result = self._assembler.assemble("RND V1, 0xFF")
        self.assertTrue(result.success)
        self.assertEqual(result.binary_image, bytes([0xC1, 0xFF]))

    def test_assemble_drw_instruction(self) -> None:
        result = self._assembler.assemble("DRW V1, V2, 5")
        self.assertTrue(result.success)
        self.assertEqual(result.binary_image, bytes([0xD1, 0x25]))

    def test_assemble_rnd_rejects_invalid_operands(self) -> None:
        result = self._assembler.assemble("RND V1, V2")
        self.assertFalse(result.success)


    def test_assemble_drw_rejects_invalid_operands(self) -> None:
        result = self._assembler.assemble("DRW V1, 5, 3")
        self.assertFalse(result.success)


    def test_assemble_reports_progress(self) -> None:
        result = self._assembler.assemble("CLS")

        self.assertTrue(result.success)

        messages = [diagnostic.message for diagnostic in self._diagnostics]

        self.assertEqual(
            messages,
            [
                "Started assembly.",
                "Parsing source.",
                "Generating binary image.",
                "Assembly complete.",
            ]
        )

    def test_assemble_reports_listing_and_cross_reference_progress(self) -> None:
        options = AssemblyOptions( generate_listing=True, generate_cross_reference=True)
        result = self._assembler.assemble("CLS", options)
        self.assertTrue(result.success)
        messages = [diagnostic.message for diagnostic in self._diagnostics]
        self.assertEqual(
            messages,
            [
                "Started assembly.",
                "Parsing source.",
                "Generating binary image.",
                "Generating listing.",
                "Creating cross-reference.",
                "Assembly complete.",
            ]
        )

    def test_assemble_reports_progress_before_parse_error(self) -> None:
        result = self._assembler.assemble("")
        self.assertFalse(result.success)
        messages = [diagnostic.message for diagnostic in self._diagnostics]
        self.assertEqual(
            messages,
            [
                "Started assembly.",
                "Parsing source.",
                "Assembly source is empty.",
            ]
        )


    def test_semantic_error_contains_source_location(self) -> None:
        """
        @brief Verify that a semantic instruction error contains its source line.
        """
        result = self._assembler.assemble( "CLS\n" "SUB V3, 1\n")
        self.assertFalse(result.success)
        self.assertEqual(len(self._diagnostics), 4)
        diagnostic = self._diagnostics[-1]
        self.assertEqual( diagnostic.message, "Integer value cannot be resolved as REGISTER.")
        self.assertIsNotNone(diagnostic.location)
        assert diagnostic.location is not None
        self.assertEqual(diagnostic.location.line, 2)

    def test_semantic_error_reports_correct_source_line(self) -> None:
        """
        @brief Verify that semantic errors identify the correct source line.
        """
        result = self._assembler.assemble(
            "CLS\n"
            "LD V1, 5\n"
            "SUB V3, 1\n"
            "RET\n"
        )
        self.assertFalse(result.success)
        diagnostic = self._diagnostics[-1]
        self.assertEqual( diagnostic.message, "Integer value cannot be resolved as REGISTER.")
        self.assertIsNotNone(diagnostic.location)
        assert diagnostic.location is not None
        self.assertEqual(diagnostic.location.line, 3)

    def test_ld_f_vx(self) -> None:
        result = self._assembler.assemble("LD F, V2")
        self.assertTrue(result.success)
        self.assertEqual(result.binary_image, bytes([0xF2, 0x29]))

    def test_ld_b_vx(self) -> None:
        result = self._assembler.assemble("LD B, V2")
        self.assertTrue(result.success)
        self.assertEqual(result.binary_image, bytes([0xF2, 0x33]))

    def test_ld_i_nnn(self) -> None:
        result = self._assembler.assemble("LD I, 0x300")
        self.assertTrue(result.success)
        self.assertEqual(result.binary_image, bytes([0xA3, 0x00]))

    def test_add_i_vx(self) -> None:
        result = self._assembler.assemble("ADD I, V2")
        self.assertTrue(result.success)
        self.assertEqual(result.binary_image, bytes([0xF2, 0x1E]))



if __name__ == "__main__":
    unittest.main()



