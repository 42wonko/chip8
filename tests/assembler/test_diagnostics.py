"""
@file test_diagnostics.py

@brief Unit tests for assembler diagnostic integration.
"""

import unittest

from assembler.token import SourceLocation
from controller.diagnostic import DiagnosticSeverity, DiagnosticSource, format_source
from controller.diagnostics import AssemblerDiagnostics


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


    def test_error_preserves_source_location(self) -> None:
        diagnostics = AssemblerDiagnostics()
        reporter = diagnostics.reporter()
        location = SourceLocation(line=12, column=4)
        reporter.error("Undefined symbol 'LOOP'.", location)
        self.assertEqual(len(diagnostics), 1)
        diagnostic = diagnostics[0]
        self.assertEqual(diagnostic.severity, DiagnosticSeverity.ERROR)
        self.assertEqual(diagnostic.source, DiagnosticSource.ASSEMBLER)
        self.assertEqual(diagnostic.message, "Undefined symbol 'LOOP'.")
        self.assertEqual(diagnostic.location, location)


    def test_duplicate_diagnostics_are_not_coalesced(self) -> None:
        diagnostics = AssemblerDiagnostics()
        reporter = diagnostics.reporter()
        location = SourceLocation(line=12, column=4)
        reporter.error("Undefined symbol 'LOOP'.", location)
        reporter.error("Undefined symbol 'LOOP'.", location)
        self.assertEqual(len(diagnostics), 2)
        self.assertEqual(diagnostics[0].count, 1)
        self.assertEqual(diagnostics[1].count, 1)


    def test_diagnostics_at_different_locations_are_retained(self) -> None:
        diagnostics = AssemblerDiagnostics()
        reporter = diagnostics.reporter()
        reporter.error( "Undefined symbol 'LOOP'.", SourceLocation(line=12, column=4),)
        reporter.error( "Undefined symbol 'LOOP'.", SourceLocation(line=18, column=4),)
        self.assertEqual(len(diagnostics), 2)


    def test_clear_removes_all_diagnostics(self) -> None:
        diagnostics = AssemblerDiagnostics()
        reporter = diagnostics.reporter()
        reporter.error( "First error.", SourceLocation(line=1, column=1),)
        reporter.warning( "Second error.", SourceLocation(line=2, column=1),)
        diagnostics.clear()
        self.assertTrue(diagnostics.empty)


if __name__ == "__main__":
    unittest.main()

