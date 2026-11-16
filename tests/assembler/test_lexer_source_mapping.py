"""
@file test_lexer_source_mapping.py

@brief Tests for original source locations after INCLUDE expansion.
"""

import tempfile
import unittest
from pathlib import Path

from assembler.includeprocessor import IncludeProcessor
from assembler.lexer import Lexer, LexerError
from assembler.token import TokenType


class LexerSourceMappingTest(unittest.TestCase):
    """Tests mapping expanded lexer locations to their source files."""

    def setUp(self) -> None:
        self.temp_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_directory.name)
        self.main_file = self.root / "main.asm"

    def tearDown(self) -> None:
        self.temp_directory.cleanup()

    def write_file(self, relative_path: str, source: str) -> Path:
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(source, encoding="utf-8")
        return path.resolve()

    def test_plain_source_keeps_optional_origin_fields_empty(self) -> None:
        tokens = Lexer("CLS\n").tokenize()

        self.assertIsNone(tokens[0].location.source_file)
        self.assertIsNone(tokens[0].location.source_line)

    def test_tokens_and_newline_tokens_receive_original_locations(self) -> None:
        included_file = self.write_file("parts/code.asm", "LD V0, 1\nRET\n")
        expanded = IncludeProcessor().expand(
            'CLS\nINCLUDE "parts/code.asm"\n',
            self.main_file
        )

        tokens = Lexer(expanded.source, expanded.line_origins).tokenize()
        instruction_tokens = [
            token for token in tokens
            if token.type == TokenType.IDENTIFIER
        ]
        newline_tokens = [
            token for token in tokens
            if token.type == TokenType.END_OF_LINE
        ]

        self.assertEqual(
            [(token.value, token.location.line, token.location.source_file, token.location.source_line)
             for token in instruction_tokens],
            [
                ("CLS", 1, self.main_file.resolve(), 1),
                ("LD", 2, included_file, 1),
                ("RET", 3, included_file, 2)
            ]
        )
        self.assertEqual(
            [(token.location.line, token.location.source_file, token.location.source_line)
             for token in newline_tokens],
            [
                (1, self.main_file.resolve(), 1),
                (2, included_file, 1),
                (3, included_file, 2)
            ]
        )

    def test_nested_include_preserves_deepest_origin(self) -> None:
        nested_file = self.write_file("parts/nested/code.asm", "RET\n")
        self.write_file("parts/code.asm", 'INCLUDE "nested/code.asm"\n')
        expanded = IncludeProcessor().expand(
            'INCLUDE "parts/code.asm"\n',
            self.main_file
        )

        tokens = Lexer(expanded.source, expanded.line_origins).tokenize()

        self.assertEqual(tokens[0].location.source_file, nested_file)
        self.assertEqual(tokens[0].location.source_line, 1)
        self.assertEqual(tokens[0].location.line, 1)

    def test_lexer_error_contains_original_source_location(self) -> None:
        included_file = self.write_file("parts/bad.asm", "CLS @\n")
        expanded = IncludeProcessor().expand(
            'INCLUDE "parts/bad.asm"\n',
            self.main_file
        )

        with self.assertRaises(LexerError) as context:
            Lexer(expanded.source, expanded.line_origins).tokenize()

        self.assertEqual(context.exception.location.line, 1)
        self.assertEqual(context.exception.location.source_file, included_file)
        self.assertEqual(context.exception.location.source_line, 1)

    def test_recovering_lexer_errors_keep_original_source_locations(self) -> None:
        first_file = self.write_file("parts/first.asm", "CLS @\n")
        second_file = self.write_file("parts/second.asm", "RET @\n")
        expanded = IncludeProcessor().expand(
            'INCLUDE "parts/first.asm"\nINCLUDE "parts/second.asm"\n',
            self.main_file
        )

        _, errors = Lexer(expanded.source, expanded.line_origins).tokenize_recovering()

        self.assertEqual(
            [(error.location.line, error.location.source_file, error.location.source_line)
             for error in errors],
            [(1, first_file, 1), (2, second_file, 1)]
        )

    def test_eof_location_uses_last_original_source_line(self) -> None:
        included_file = self.write_file("parts/code.asm", "RET\n")
        expanded = IncludeProcessor().expand(
            'INCLUDE "parts/code.asm"\n',
            self.main_file
        )

        eof = Lexer(expanded.source, expanded.line_origins).tokenize()[-1]

        self.assertEqual(eof.type, TokenType.END_OF_FILE)
        self.assertEqual(eof.location.line, 2)
        self.assertEqual(eof.location.source_file, included_file)
        self.assertEqual(eof.location.source_line, 1)

    def test_empty_source_has_no_original_eof_location(self) -> None:
        eof = Lexer("", ()).tokenize()[-1]

        self.assertIsNone(eof.location.source_file)
        self.assertIsNone(eof.location.source_line)


if __name__ == "__main__":
    unittest.main()
