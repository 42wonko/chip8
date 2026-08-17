"""
@file test_result.py

@brief Unit tests for assembler results.
"""

import unittest

from assembler.result import AssemblyResult
from controller.diagnostic import Diagnostic, DiagnosticSeverity, DiagnosticSource


class TestAssemblyResult(unittest.TestCase):
    """
    @brief Test assembler results.
    """

    def test_successful_result(self) -> None:
        """
        @brief Verify a successful assembly result.
        """
        result = AssemblyResult( success=True, binary_image=b"\x60\x00")
        self.assertTrue(result.success)
        self.assertEqual(result.binary_image, b"\x60\x00")
        self.assertEqual(result.diagnostics, ())
        self.assertIsNone(result.listing)
        self.assertIsNone(result.cross_reference)


    def test_failed_result(self) -> None:
        """
        @brief Verify a failed assembly result.
        """
        diagnostic = Diagnostic( severity=DiagnosticSeverity.ERROR, source=DiagnosticSource.ASSEMBLER, message="Assembly failed")
        result = AssemblyResult( success=False, diagnostics=(diagnostic,))
        self.assertFalse(result.success)
        self.assertEqual(result.diagnostics, (diagnostic,))
        self.assertIsNone(result.binary_image)


    def test_optional_outputs(self) -> None:
        """
        @brief Verify optional assembler output products.
        """
        result = AssemblyResult( success=True, binary_image=b"\x60\x00", listing="0200 6000  LD V0, 0", cross_reference="START 0200")
        self.assertEqual(result.listing, "0200 6000  LD V0, 0")
        self.assertEqual(result.cross_reference, "START 0200")


if __name__ == "__main__":
    unittest.main()

