"""
@file test_assembler.py

@brief Unit tests for the assembler entry point.
"""

import unittest

from assembler.assembler import Assembler
from assembler.target import Target
from chip8.isa.classicisa import ClassicInstructionSetArchitecture
from controller.diagnostic import DiagnosticSource
from controller.diagnostics import Diagnostics
from tests.helpers import create_machine


class TestAssembler(unittest.TestCase):
    """
    @brief Test the assembler entry point.
    """

    def setUp(self) -> None:
        self._diagnostics = Diagnostics()
        machine = create_machine()
        self._isa = ClassicInstructionSetArchitecture(machine)
        self._assembler = Assembler( self._diagnostics.reporter(DiagnosticSource.ASSEMBLER), self._isa)


    def test_assembler_can_be_instantiated(self) -> None:
        """
        @brief Verify that the assembler can be instantiated.
        """
        self.assertIsNotNone(self._assembler)


    def test_assemble_returns_result(self) -> None:
        """
        @brief Verify that assemble() returns an assembly result.
        """
        result = self._assembler.assemble( source="", target=Target.COSMAC)
        self.assertFalse(result.success)
        self.assertEqual(len(result.diagnostics), 0)
        self.assertEqual(len(self._diagnostics), 1)
        diagnostic = self._diagnostics[0]
        self.assertEqual( diagnostic.source, DiagnosticSource.ASSEMBLER)


    def test_assemble_db(self) -> None:
        result = self._assembler.assemble(
            "DB 0x12, 0x34",
            Target.COSMAC
        )

        self.assertTrue(result.success)
        self.assertEqual(result.binary_image, b"\x12\x34")


    def test_assemble_cls(self) -> None:
        result = self._assembler.assemble(
            "CLS",
            Target.COSMAC
        )

        self.assertTrue(result.success)
        self.assertEqual(result.binary_image, b"\x00\xE0")


    def test_assemble_instruction_with_label(self) -> None:
        result = self._assembler.assemble(
            "START:\nJP START",
            Target.COSMAC
        )

        self.assertTrue(result.success)
        self.assertEqual(result.binary_image, b"\x12\x00")


    def test_assemble_org_and_gap(self) -> None:
        result = self._assembler.assemble(
            "ORG 0x300\n"
            "DB 1\n"
            "ORG 0x303\n"
            "DB 2",
            Target.COSMAC
        )

        self.assertTrue(result.success)
        self.assertEqual(
            result.binary_image,
            b"\x01\x00\x00\x02"
        )


    def test_label_can_be_referenced_after_case_change(self) -> None:
        """
        @brief Verify that a label can be resolved regardless of its case.
        """
        source = (
            "org 0x200\n"
            "Start:\tCLS\n"
            "jp Start\n"
        )
        result = self._assembler.assemble( source, Target.COSMAC)
        self.assertTrue(result.success)


if __name__ == "__main__":
    unittest.main()
