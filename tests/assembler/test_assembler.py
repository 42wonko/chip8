"""
@file test_assembler.py

@brief Unit tests for the assembler entry point.
"""

import unittest

from assembler.assembler import Assembler
from assembler.target import Target
from controller.diagnostic import DiagnosticSource
from controller.diagnostics import Diagnostics


class TestAssembler(unittest.TestCase):
    """
    @brief Test the assembler entry point.
    """

    def setUp(self) -> None:
        """
        @brief Create the diagnostics infrastructure and assembler.
        """
        self._diagnostics = Diagnostics()
        self._assembler = Assembler( self._diagnostics.reporter(DiagnosticSource.ASSEMBLER))


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


if __name__ == "__main__":
    unittest.main()
