"""
@file test_diagnostics.py

@brief Unit tests for assembler diagnostic integration.
"""

import unittest

from controller.diagnostic import DiagnosticSource, format_source


class TestAssemblerDiagnostics(unittest.TestCase):
    """
    @brief Test assembler integration with the existing diagnostics system.
    """

    def test_assembler_source_exists(self) -> None:
        """
        @brief Verify that assembler diagnostics have their own source.
        """
        self.assertEqual(DiagnosticSource.ASSEMBLER.value, "assembler")


    def test_assembler_source_format(self) -> None:
        """
        @brief Verify formatting of the assembler diagnostic source.
        """
        self.assertEqual(format_source(DiagnosticSource.ASSEMBLER), "ASSEMB")


if __name__ == "__main__":
    unittest.main()

