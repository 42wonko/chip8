
import unittest

from controller.diagnostic import (
    DiagnosticSeverity,
    DiagnosticSource,
    format_severity,
    format_source
)


class TestDiagnosticFormatting(unittest.TestCase):
    def test_warning_severity(self) -> None:
        self.assertEqual(format_severity(DiagnosticSeverity.WARNING), "WRN")

    def test_invalid_severity_raises_assertion_error(self) -> None:
        with self.assertRaises(AssertionError):
            format_severity("invalid")

    def test_gui_source(self) -> None:
        self.assertEqual(format_source(DiagnosticSource.GUI), "GUI")

    def test_invalid_source_raises_assertion_error(self) -> None:
        with self.assertRaises(AssertionError):
            format_source(DiagnosticSource.UNIT_TEST)

    def test_analyzer_source(self) -> None:
        self.assertEqual(format_source(DiagnosticSource.ANALYZER), "ANALYZR")


if __name__ == "__main__":
    unittest.main()

