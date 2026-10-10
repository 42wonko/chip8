"""
@file test_assembler.py

@brief Unit tests for the assembler entry point.
"""

import unittest
from unittest.mock import Mock

from assembler.assembler import Assembler
from assembler.ast import AssemblyNode
from assembler.classicparser import ClassicParser
from assembler.options import AssemblyOptions
from assembler.parser import Parser
from chip8.isa.classicisa import ClassicInstructionSetArchitecture
from controller.diagnostic import DiagnosticSource

#from controller.diagnostics import Diagnostics
from controller.diagnostics import AssemblerDiagnostics
from emulator.constants import ADDRESS_MASK

#from tests.helpers import create_machine


class TestAssembler(unittest.TestCase):
    """
    @brief Test the assembler entry point.
    """

    def setUp(self) -> None:
        self._diagnostics = AssemblerDiagnostics()
        self._isa = ClassicInstructionSetArchitecture()
        parser = ClassicParser(self._isa)
        self._assembler = Assembler( self._diagnostics.reporter(), self._isa, parser)


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
        result = self._assembler.assemble( "DATA: DB 0x12, 0x34")
        self.assertTrue(result.success)
        self.assertEqual(result.binary_image, b"\x12\x34")


    def test_assemble_dw_emits_big_endian_words(self) -> None:
        result = self._assembler.assemble("DATA: DW 0x1234, 0xABCD")
        self.assertTrue(result.success)
        self.assertEqual(result.binary_image, b"\x12\x34\xAB\xCD")

    def test_assemble_dw_rejects_data_past_address_limit(self) -> None:
        result = self._assembler.assemble("ORG 0xFFF\nDATA: DW 0x1234")
        self.assertFalse(result.success)
        self.assertIsNone(result.binary_image)
        self.assertTrue(
            any(
                "DW data exceeds the assembler address space." in diagnostic.message
                for diagnostic in result.diagnostics
            )
        )


    def test_assemble_dw_resolves_forward_label(self) -> None:
        result = self._assembler.assemble("DATA: DW TARGET\nTARGET: RET")
        self.assertTrue(result.success)
        self.assertEqual(result.binary_image, b"\x02\x02\x00\xEE")

    def test_assemble_cls(self) -> None:
        result = self._assembler.assemble( "CLS")
        self.assertTrue(result.success)
        self.assertEqual(result.binary_image, b"\x00\xE0")


    def test_parser_errors_block_output_and_are_all_reported(self) -> None:
        """Verify parse errors are collected and block semantic/code generation."""
        result = self._assembler.assemble(
            "CLS\n"
            "PLANE 1\n"
            "LD V0,\n"
            "RET\n"
        )

        self.assertFalse(result.success)
        self.assertIsNone(result.binary_image)
        self.assertEqual(len(result.diagnostics), 2)
        self.assertEqual(
            [diagnostic.location.line for diagnostic in result.diagnostics if diagnostic.location],
            [2, 3],
        )
        messages = [diagnostic.message for diagnostic in self._diagnostics]
        self.assertIn("Unsupported instruction 'PLANE'.", messages)
        self.assertTrue(any("Expected operand after comma" in message for message in messages))
        self.assertNotIn("Generating binary image.", messages)


    def test_assemble_instruction_with_label(self) -> None:
        result = self._assembler.assemble( "START:\nJP START")
        self.assertTrue(result.success)
        self.assertEqual(result.binary_image, b"\x12\x00")


    def test_assemble_org_and_gap(self) -> None:
        result = self._assembler.assemble(
            "ORG 0x300\n"
            "DATA1: DB 1\n"
            "ORG 0x303\n"
            "DATA2: DB 2"
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
        self.assertEqual(len(result.diagnostics), 1)
        self.assertEqual( result.diagnostics[0].message, "Operand 'V2' has type REGISTER, expected VALUE.",)


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


    def test_assembler_rejects_special_operand_as_label(self) -> None:
        result = self._assembler.assemble(
            "CLS\n"
            "I: RET\n"
        )

        self.assertFalse(result.success)
        diagnostic = self._diagnostics[-1]
        self.assertEqual(
            diagnostic.message,
            "Assembler operand 'I' cannot be used as a symbol name."
        )
        self.assertIsNotNone(diagnostic.location)
        assert diagnostic.location is not None
        self.assertEqual(diagnostic.location.line, 2)

    def test_assembler_rejects_special_operand_as_equ_symbol(self) -> None:
        result = self._assembler.assemble(
            "CLS\n"
            "DT: EQU 42\n"
        )

        self.assertFalse(result.success)
        diagnostic = self._diagnostics[-1]
        self.assertEqual(
            diagnostic.message,
            "Assembler operand 'DT' cannot be used as a symbol name."
        )
        self.assertIsNotNone(diagnostic.location)
        assert diagnostic.location is not None
        self.assertEqual(diagnostic.location.line, 2)

    def test_duplicate_label_reports_second_definition_line(self) -> None:
        result = self._assembler.assemble(
            "START: CLS\n"
            "START: RET\n"
        )
        self.assertFalse(result.success)
        diagnostic = self._diagnostics[-1]
        self.assertEqual(diagnostic.message, "Symbol 'START' is already defined.")
        self.assertIsNotNone(diagnostic.location)
        assert diagnostic.location is not None
        self.assertEqual(diagnostic.location.line, 2)


    def test_duplicate_equ_reports_second_definition_line(self) -> None:
        result = self._assembler.assemble(
            "VALUE: EQU 1\n"
            "VALUE: EQU 2\n"
        )
        self.assertFalse(result.success)
        diagnostic = self._diagnostics[-1]
        self.assertEqual(diagnostic.message, "Symbol 'VALUE' is already defined.")
        self.assertIsNotNone(diagnostic.location)
        assert diagnostic.location is not None
        self.assertEqual(diagnostic.location.line, 2)


    def test_label_then_equ_duplicate_reports_second_definition_line(self) -> None:
        result = self._assembler.assemble(
            "VALUE: CLS\n"
            "VALUE: EQU 42\n"
        )
        self.assertFalse(result.success)
        diagnostic = self._diagnostics[-1]
        self.assertEqual(diagnostic.message, "Symbol 'VALUE' is already defined.")
        self.assertIsNotNone(diagnostic.location)
        assert diagnostic.location is not None
        self.assertEqual(diagnostic.location.line, 2)


    def test_equ_then_label_duplicate_reports_second_definition_line(self) -> None:
        result = self._assembler.assemble(
            "VALUE: EQU 42\n"
            "VALUE: CLS\n"
        )
        self.assertFalse(result.success)
        diagnostic = self._diagnostics[-1]
        self.assertEqual(diagnostic.message, "Symbol 'VALUE' is already defined.")
        self.assertIsNotNone(diagnostic.location)
        assert diagnostic.location is not None
        self.assertEqual(diagnostic.location.line, 2)


    def test_duplicate_symbol_is_case_insensitive(self) -> None:
        result = self._assembler.assemble(
            "start: CLS\n"
            "START: RET\n"
        )
        self.assertFalse(result.success)
        diagnostic = self._diagnostics[-1]
        self.assertEqual(diagnostic.message, "Symbol 'START' is already defined.")
        self.assertIsNotNone(diagnostic.location)
        assert diagnostic.location is not None
        self.assertEqual(diagnostic.location.line, 2)


    def test_undefined_symbol_reports_identifier_location(self) -> None:
        result = self._assembler.assemble("JP MISSING\n")
        self.assertFalse(result.success)
        diagnostic = self._diagnostics[-1]
        self.assertIsNotNone(diagnostic.location)
        assert diagnostic.location is not None
        self.assertEqual(diagnostic.location.line, 1)
        self.assertEqual(diagnostic.location.column, 4)


    def test_undefined_symbol_in_expression_reports_identifier_location(self) -> None:
        result = self._assembler.assemble("JP MISSING + 1\n")
        self.assertFalse(result.success)
        diagnostic = self._diagnostics[-1]
        self.assertIsNotNone(diagnostic.location)
        assert diagnostic.location is not None
        self.assertEqual(diagnostic.location.line, 1)
        self.assertEqual(diagnostic.location.column, 4)


    def test_undefined_symbol_in_org_reports_identifier_location(self) -> None:
        result = self._assembler.assemble("ORG MISSING\n")
        self.assertFalse(result.success)
        diagnostic = self._diagnostics[-1]
        self.assertIsNotNone(diagnostic.location)
        assert diagnostic.location is not None
        self.assertEqual(diagnostic.location.line, 1)
        self.assertEqual(diagnostic.location.column, 5)


    def test_undefined_symbol_in_call_reports_identifier_location(self) -> None:
        result = self._assembler.assemble("CALL MISSING\n")
        self.assertFalse(result.success)
        diagnostic = self._diagnostics[-1]
        self.assertIsNotNone(diagnostic.location)
        assert diagnostic.location is not None
        self.assertEqual(diagnostic.location.line, 1)
        self.assertEqual(diagnostic.location.column, 6)


    def test_undefined_symbol_in_load_reports_identifier_location(self) -> None:
        result = self._assembler.assemble("LD V1, MISSING\n")
        self.assertFalse(result.success)
        diagnostic = self._diagnostics[-1]
        self.assertIsNotNone(diagnostic.location)
        assert diagnostic.location is not None
        self.assertEqual(diagnostic.location.line, 1)
        self.assertEqual(diagnostic.location.column, 8)


    def test_undefined_symbol_in_db_reports_identifier_location(self) -> None:
        result = self._assembler.assemble("DATA: DB MISSING\n")
        self.assertFalse(result.success)
        diagnostic = self._diagnostics[-1]
        self.assertIsNotNone(diagnostic.location)
        assert diagnostic.location is not None
        self.assertEqual(diagnostic.location.line, 1)
        self.assertEqual(diagnostic.location.column, 10)


    def test_undefined_symbol_in_equ_reports_identifier_location(self) -> None:
        result = self._assembler.assemble("VALUE: EQU MISSING\n")
        self.assertFalse(result.success)
        diagnostic = self._diagnostics[-1]
        self.assertIsNotNone(diagnostic.location)
        assert diagnostic.location is not None
        self.assertEqual(diagnostic.location.line, 1)
        self.assertEqual(diagnostic.location.column, 12)


    def test_undefined_symbol_in_equ_expression_reports_identifier_location(self) -> None:
        result = self._assembler.assemble("VALUE: EQU MISSING + 1\n")
        self.assertFalse(result.success)
        diagnostic = self._diagnostics[-1]
        self.assertIsNotNone(diagnostic.location)
        assert diagnostic.location is not None
        self.assertEqual(diagnostic.location.line, 1)
        self.assertEqual(diagnostic.location.column, 12)

    def test_failed_symbol_definition_does_not_create_symbol(self) -> None:
        result = self._assembler.assemble(
            "VALUE: EQU MISSING\n"
            "JP VALUE\n"
        )
        self.assertFalse(result.success)
        self.assertEqual(len(result.diagnostics), 1)
        diagnostic = result.diagnostics[0]
        self.assertIsNotNone(diagnostic.location)
        assert diagnostic.location is not None
        self.assertEqual(diagnostic.location.line, 1)
        self.assertEqual(diagnostic.location.column, 12)

    def test_forward_label_reference(self) -> None:
        """
        @brief Verify that an instruction can reference a label defined later.
        """
        result = self._assembler.assemble(
            "JP TARGET\n"
            "TARGET: CLS"
        )
        self.assertTrue(result.success)
        self.assertEqual(result.binary_image, b"\x12\x02\x00\xE0")

    def test_forward_label_reference_is_in_cross_reference(self) -> None:
        """
        @brief Verify that a forward label reference appears in the cross-reference.
        """
        result = self._assembler.assemble(
            "JP TARGET\n"
            "TARGET: CLS",
            AssemblyOptions( generate_listing=True, generate_cross_reference=True)
        )
        self.assertTrue(result.success)
        self.assertIsNotNone(result.listing)
        assert result.listing is not None
        self.assertIn( "TARGET        Symbol      --            2           1", result.listing)

    def test_org_accepts_maximum_address(self) -> None:
        result = self._assembler.assemble( "ORG 0xFFF\n")
        self.assertTrue(result.success)
        self.assertEqual(result.binary_image, b"")

    def test_org_rejects_address_above_maximum(self) -> None:
        result = self._assembler.assemble("ORG 0x10000")
        self.assertFalse(result.success)

    def test_org_rejects_negative_address(self) -> None:
        result = self._assembler.assemble("ORG -1")
        self.assertFalse(result.success)

    def test_org_accepts_expression_at_maximum_address(self) -> None:
        result = self._assembler.assemble(
            "BASE: EQU 0xFFE\n"
            "ORG BASE + 1\n"
        )
        self.assertTrue(result.success)
        self.assertEqual(result.binary_image, b"")

    def test_org_rejects_expression_above_maximum_address(self) -> None:
        result = self._assembler.assemble(
            "BASE: EQU 0xFFF\n"
            "ORG BASE + 1\n"
        )
        self.assertFalse(result.success)

    def test_jump_accepts_maximum_12_bit_address(self):
        result = self._assembler.assemble("JP 0xFFF")
        self.assertTrue(result.success)
        self.assertEqual(result.binary_image, b"\x1F\xFF")


    def test_jump_rejects_address_above_12_bits(self):
        result = self._assembler.assemble("JP 0x1000")
        self.assertFalse(result.success)


    def test_call_accepts_maximum_12_bit_address(self):
        result = self._assembler.assemble("CALL 0xFFF")
        self.assertTrue(result.success)
        self.assertEqual(result.binary_image, b"\x2F\xFF")


    def test_call_rejects_address_above_12_bits(self):
        result = self._assembler.assemble("CALL 0x1000")
        self.assertFalse(result.success)


    def test_load_i_accepts_maximum_12_bit_address(self):
        result = self._assembler.assemble("LD I, 0xFFF")
        self.assertTrue(result.success)
        self.assertEqual(result.binary_image, b"\xAF\xFF")


    def test_load_i_rejects_address_above_12_bits(self):
        result = self._assembler.assemble("LD I, 0x1000")
        self.assertFalse(result.success)

    def test_jump_expression_at_12_bit_limit(self):
        result = self._assembler.assemble(
            "BASE: EQU 0xFFE\n"
            "JP BASE + 1"
        )
        self.assertTrue(result.success)
        self.assertEqual(result.binary_image, b"\x1F\xFF")


    def test_jump_expression_above_12_bit_limit(self):
        result = self._assembler.assemble(
            "BASE: EQU 0xFFF\n"
            "JP BASE + 1"
        )
        self.assertFalse(result.success)


    def test_load_i_expression_at_12_bit_limit(self):
        result = self._assembler.assemble(
            "BASE: EQU 0xFFE\n"
            "LD I, BASE + 1"
        )
        self.assertTrue(result.success)
        self.assertEqual(result.binary_image, b"\xAF\xFF")


    def test_load_i_expression_above_12_bit_limit(self):
        result = self._assembler.assemble(
            "BASE: EQU 0xFFF\n"
            "LD I, BASE + 1"
        )
        self.assertFalse(result.success)

    def test_db_accepts_zero(self):
        result = self._assembler.assemble("DATA: DB 0x00")
        self.assertTrue(result.success)
        self.assertEqual(result.binary_image, b"\x00")


    def test_db_accepts_maximum_byte(self):
        result = self._assembler.assemble("DATA: DB 0xFF")
        self.assertTrue(result.success)
        self.assertEqual(result.binary_image, b"\xFF")


    def test_db_rejects_value_above_byte_range(self):
        result = self._assembler.assemble("DATA: DB 0x100")
        self.assertFalse(result.success)


    def test_db_rejects_negative_value(self):
        result = self._assembler.assemble("DATA: DB -1")
        self.assertFalse(result.success)

    def test_db_equ_accepts_maximum_byte(self):
        result = self._assembler.assemble(
            "VALUE: EQU 0xFF\n"
            "DATA: DB VALUE"
        )
        self.assertTrue(result.success)
        self.assertEqual(result.binary_image, b"\xFF")

    def test_db_equ_rejects_value_above_byte_range(self):
        result = self._assembler.assemble(
            "VALUE: EQU 0x100\n"
            "DATA: DB VALUE"
        )
        self.assertFalse(result.success)

    def test_db_expression_accepts_maximum_byte(self):
        result = self._assembler.assemble(
            "BASE: EQU 0xFE\n"
            "DATA: DB BASE + 1"
        )
        self.assertTrue(result.success)
        self.assertEqual(result.binary_image, b"\xFF")


    def test_db_expression_rejects_value_above_byte_range(self):
        result = self._assembler.assemble(
            "BASE: EQU 0xFF\n"
            "DATA: DB BASE + 1"
        )
        self.assertFalse(result.success)

    def test_db_rejects_invalid_byte_among_valid_bytes(self):
        result = self._assembler.assemble("DATA: DB 0x01, 0xFF, 0x100, 0x02")
        self.assertFalse(result.success)

    def test_instruction_at_last_even_address_fits(self):
        result = self._assembler.assemble(
            "ORG 0xFFE\n"
            "CLS"
        )
        self.assertTrue(result.success)
        self.assertEqual(result.binary_image, b"\x00\xE0")

    def test_instruction_at_last_address_does_not_wrap(self):
        result = self._assembler.assemble(
            "ORG 0xFFF\n"
            "CLS"
        )
        self.assertFalse(result.success)

    def test_instruction_at_last_address_produces_no_binary_image(self):
        result = self._assembler.assemble(
            "ORG 0xFFF\n"
            "CLS"
        )
        self.assertFalse(result.success)
        self.assertIsNone(result.binary_image)

    def test_instruction_at_0xfffd_fits(self):
        result = self._assembler.assemble(
            "ORG 0xFFD\n"
            "CLS"
        )
        self.assertTrue(result.success)
        self.assertEqual(result.binary_image, b"\x00\xE0")

    def test_second_instruction_cannot_cross_12_bit_address_boundary(self):
        result = self._assembler.assemble(
            "ORG 0xFFD\n"
            "CLS\n"
            "RET"
        )
        self.assertFalse(result.success)

    def test_db_byte_at_maximum_address_is_valid(self) -> None:
        result = self._assembler.assemble(
            "ORG 0xFFF\n"
            "DATA: DB 0xFF\n"
        )
        self.assertTrue(result.success)
        self.assertEqual(result.binary_image, b"\xFF")

    def test_db_data_cannot_cross_12_bit_address_boundary(self) -> None:
        result = self._assembler.assemble(
            "ORG 0xFFF\n"
            "DATA: DB 0xFF, 0x00\n"
        )
        self.assertFalse(result.success)

    def test_db_data_ending_at_maximum_address_is_valid(self) -> None:
        result = self._assembler.assemble(
            "ORG 0xFFE\n"
            "DATA: DB 0xFF, 0x00\n"
        )
        self.assertTrue(result.success)
        self.assertEqual(result.binary_image, b"\xFF\x00")

    def test_db_data_crossing_12_bit_address_boundary_is_invalid(self) -> None:
        result = self._assembler.assemble(
            "ORG 0xFFE\n"
            "DATA: DB 0xFF, 0x00, 0xAA\n"
        )
        self.assertFalse(result.success)

    def test_assembler_address_limit_is_12_bit(self) -> None:
        self.assertEqual(
            self._isa.assembler_address_limit(),
            ADDRESS_MASK
        )

    def test_instruction_at_last_two_addresses_fits(self) -> None:
        result = self._assembler.assemble(
            "ORG 0xFFE\n"
            "CLS"
        )
        self.assertTrue(result.success)
        self.assertEqual(result.binary_image, b"\x00\xE0")


    def test_instruction_at_last_address_does_not_fit(self) -> None:
        result = self._assembler.assemble(
            "ORG 0xFFF\n"
            "CLS"
        )
        self.assertFalse(result.success)
        self.assertIsNone(result.binary_image)


    def test_db_data_crossing_maximum_address_is_invalid(self) -> None:
        result = self._assembler.assemble(
            "ORG 0xFFE\n"
            "DATA: DB 0xFF, 0x00, 0xAA"
        )
        self.assertFalse(result.success)
        self.assertIsNone(result.binary_image)


    def test_lexer_error_is_returned_with_location(self) -> None:
        result = self._assembler.assemble("LD V0, @")
        self.assertFalse(result.success)
        self.assertEqual(len(result.diagnostics), 1)
        diagnostic = result.diagnostics[0]
        self.assertEqual(diagnostic.message, "Unexpected character '@' at 1:8.")
        self.assertIsNotNone(diagnostic.location)
        assert diagnostic.location is not None
        self.assertEqual(diagnostic.location.line, 1)
        self.assertEqual(diagnostic.location.column, 8)


    def test_parser_error_is_returned_with_location(self) -> None:
        result = self._assembler.assemble("LD V0,")
        self.assertFalse(result.success)
        self.assertEqual(len(result.diagnostics), 1)
        diagnostic = result.diagnostics[0]
        self.assertIsNotNone(diagnostic.location)
        assert diagnostic.location is not None
        self.assertEqual(diagnostic.location.line, 1)
        self.assertEqual(diagnostic.location.column, 7)


    def test_target_directive_does_not_consume_address_space(self) -> None:
        """
        @brief Verify that TARGET is metadata and does not affect code placement.
        """
        result = self._assembler.assemble(
            "TARGET COSMAC\n"
            "TARGET_LABEL: CLS"
        )
        self.assertTrue(result.success)
        self.assertEqual(result.binary_image, b"\x00\xE0")


    def test_org_range_error_is_in_result_diagnostics(self) -> None:
        """
        @brief Verify that an ORG range error is returned with its source location.
        """
        result = self._assembler.assemble("ORG 0x1000")
        self.assertFalse(result.success)
        self.assertEqual(len(result.diagnostics), 1)
        diagnostic = result.diagnostics[0]
        self.assertEqual(diagnostic.source, DiagnosticSource.ASSEMBLER)
        self.assertIsNotNone(diagnostic.location)
        assert diagnostic.location is not None
        self.assertEqual(diagnostic.location.line, 1)
        self.assertEqual(diagnostic.location.column, 1)


    def test_db_range_error_is_in_result_diagnostics(self) -> None:
        """
        @brief Verify that a DB range error is returned with its source location.
        """
        result = self._assembler.assemble("DB 0x100")
        self.assertFalse(result.success)
        self.assertEqual(len(result.diagnostics), 1)
        diagnostic = result.diagnostics[0]
        self.assertEqual(diagnostic.source, DiagnosticSource.ASSEMBLER)
        self.assertIsNotNone(diagnostic.location)
        assert diagnostic.location is not None
        self.assertEqual(diagnostic.location.line, 1)
        self.assertEqual(diagnostic.location.column, 1)


    def test_instruction_exceeding_address_space_is_reported_in_result( self,) -> None:
        """
        @brief Verify that an instruction address error reaches the result.
        """
        result = self._assembler.assemble( "ORG 0xFFF\n" "CLS")
        self.assertFalse(result.success)
        self.assertEqual(len(result.diagnostics), 1)
        diagnostic = result.diagnostics[0]
        self.assertEqual(diagnostic.source, DiagnosticSource.ASSEMBLER)
        self.assertIsNotNone(diagnostic.location)
        assert diagnostic.location is not None
        self.assertEqual(diagnostic.location.line, 2)
        self.assertEqual(diagnostic.location.column, 1)


    def test_lexer_error_is_returned_in_result_diagnostics(self) -> None:
        """
        @brief Verify that a lexer error reaches the assembly result.
        """
        result = self._assembler.assemble("@")
        self.assertFalse(result.success)
        self.assertIsNone(result.binary_image)
        self.assertEqual(len(result.diagnostics), 1)
        diagnostic = result.diagnostics[0]
        self.assertEqual(diagnostic.source, DiagnosticSource.ASSEMBLER)
        self.assertIsNotNone(diagnostic.location)
        assert diagnostic.location is not None
        self.assertEqual(diagnostic.location.line, 1)
        self.assertEqual(diagnostic.location.column, 1)

    def test_parser_error_is_returned_in_result_diagnostics(self) -> None:
        """
        @brief Verify that a parser error reaches the assembly result.
        """
        result = self._assembler.assemble("LD V0,")
        self.assertFalse(result.success)
        self.assertIsNone(result.binary_image)
        self.assertEqual(len(result.diagnostics), 1)
        diagnostic = result.diagnostics[0]
        self.assertEqual(diagnostic.source, DiagnosticSource.ASSEMBLER)
        self.assertIsNotNone(diagnostic.location)
        assert diagnostic.location is not None


    def test_failed_assembly_has_no_binary_image(self) -> None:
        """
        @brief Verify that a failed assembly does not produce a binary image.
        """
        result = self._assembler.assemble(
            "CLS\n"
            "SUB V3, 1"
        )
        self.assertFalse(result.success)
        self.assertIsNone(result.binary_image)
        self.assertEqual(len(result.diagnostics), 1)

    def test_failed_assembly_does_not_generate_listing(self) -> None:
        """
        @brief Verify that a failed assembly produces no listing.
        """
        result = self._assembler.assemble(
            "CLS\n"
            "SUB V3, 1",
            AssemblyOptions(generate_listing=True),
        )
        self.assertFalse(result.success)
        self.assertIsNone(result.binary_image)
        self.assertIsNone(result.listing)


    def test_semantic_error_is_reported_in_both_diagnostic_channels(self) -> None:
        """
        @brief Verify that a semantic error reaches both diagnostic channels.
        """
        result = self._assembler.assemble(
            "CLS\n"
            "SUB V3, 1\n"
        )
        self.assertFalse(result.success)
        self.assertEqual(len(result.diagnostics), 1)
        result_diagnostic = result.diagnostics[0]
        reporter_diagnostic = self._diagnostics[-1]
        self.assertEqual( result_diagnostic.severity, reporter_diagnostic.severity,)
        self.assertEqual( result_diagnostic.source, reporter_diagnostic.source,)
        self.assertEqual( result_diagnostic.message, reporter_diagnostic.message,)
        self.assertEqual( result_diagnostic.location, reporter_diagnostic.location,)


    def test_target_directive_does_not_consume_address_space_in_listing( self,) -> None:
        """
        @brief Verify that TARGET is metadata in the assembly listing.
        """
        result = self._assembler.assemble(
            "TARGET COSMAC\n"
            "CLS",
            AssemblyOptions(generate_listing=True),
        )
        self.assertTrue(result.success)
        self.assertIsNotNone(result.listing)
        assert result.listing is not None
        lines = result.listing.splitlines()
        self.assertEqual(len(lines), 2)
        self.assertIn("TARGET COSMAC", lines[0])
        self.assertIn("0200", lines[1])
        self.assertIn("00 E0", lines[1])


    def test_cross_reference_is_ignored_without_listing(self) -> None:
        """
        @brief Verify that cross-reference generation requires a listing.
        """
        result = self._assembler.assemble( "START: CLS", AssemblyOptions( generate_listing=False, generate_cross_reference=True,),)
        self.assertTrue(result.success)
        self.assertIsNone(result.listing)


    def test_assembler_instance_does_not_retain_previous_symbols(self) -> None:
        """
        @brief Verify that separate assembly operations have independent symbols.
        """
        first = self._assembler.assemble(
            "FIRST: CLS\n"
            "JP FIRST",
            AssemblyOptions(generate_listing=True),
        )
        self.assertTrue(first.success)
        self.assertEqual(first.binary_image, b"\x00\xE0\x12\x00")
        second = self._assembler.assemble(
            "SECOND: CLS\n"
            "JP SECOND",
            AssemblyOptions(generate_listing=True),
        )
        self.assertTrue(second.success)
        self.assertEqual(second.binary_image, b"\x00\xE0\x12\x00")
        self.assertIsNotNone(second.listing)
        assert second.listing is not None
        self.assertIn("SECOND: CLS", second.listing)
        self.assertIn("JP SECOND", second.listing)
        self.assertNotIn("FIRST: CLS", second.listing)
        self.assertNotIn("JP FIRST", second.listing)


    def test_parse_uses_injected_parser(self) -> None:
        """
        @brief Verify that parsing uses the injected parser instance.
        """
        parser = Mock(spec=Parser)
        parser.parse.return_value = AssemblyNode(lines=())
        assembler = Assembler( self._diagnostics.reporter(), self._isa, parser)
        result = assembler._parse("CLS\n")
        self.assertEqual(result, AssemblyNode(lines=()))
        parser.set_tokens.assert_called_once()
        parser.parse.assert_called_once()


    def test_unsupported_mnemonic_is_rejected_during_parsing(self) -> None:
        result = self._assembler.assemble("PLANE 1")
        self.assertFalse(result.success)
        self.assertEqual(len(result.diagnostics), 1)
        self.assertIn( "Unsupported instruction 'PLANE'", result.diagnostics[0].message,)

    def test_supported_mnemonic_with_invalid_operands_is_rejected_semantically( self,) -> None:
        result = self._assembler.assemble("RND V1, V2")
        self.assertFalse(result.success)
        self.assertEqual(len(result.diagnostics), 1)
        self.assertIn( "Operand 'V2' has type REGISTER, expected VALUE.", result.diagnostics[0].message,)


    def test_assembler_recovers_after_parse_error(self) -> None:
        """
        @brief Verify that a failed parse does not prevent a later
        assembly from succeeding.
        """
        failed_result = self._assembler.assemble("JP")
        self.assertFalse(failed_result.success)
        self.assertEqual(len(failed_result.diagnostics), 1)
        successful_result = self._assembler.assemble("CLS")
        self.assertTrue(successful_result.success)
        self.assertEqual(successful_result.binary_image, b"\x00\xE0")



if __name__ == "__main__":
    unittest.main()



