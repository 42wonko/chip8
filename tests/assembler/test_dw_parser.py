"""
@file test_dw_parser.py

@brief Unit tests for parsing the DW assembler directive.
"""

import unittest

from assembler.ast import DirectiveNode
from assembler.lexer import Lexer
from assembler.parser import Parser, ParserError


class PermissiveParser(Parser):
    """Test parser that accepts any instruction mnemonic."""
    def _is_instruction_mnemonic(self, mnemonic: str) -> bool:
        return True

class DwParserTest(unittest.TestCase):
    """Tests for parsing DW directives."""

    def _parse(self, source: str):
        parser = PermissiveParser()
        parser.set_tokens(Lexer(source).tokenize())
        return parser.parse()

    def test_parse_dw_directive(self) -> None:
        assembly = self._parse("DATA: DW 0x1234, 0xABCD")
        statement = assembly.lines[0].statement
        self.assertIsInstance(statement, DirectiveNode)
        self.assertEqual(statement.name, "DW")
        self.assertEqual(len(statement.operands), 2)

    def test_label_required_for_dw(self) -> None:
        with self.assertRaises(ParserError) as context:
            self._parse("DW 0x1234")
        self.assertIn("DW requires a label", str(context.exception))
