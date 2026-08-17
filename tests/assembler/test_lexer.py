"""
@file test_lexer.py

@brief Unit tests for the assembler lexer.
"""

import unittest

from assembler.lexer import Lexer, LexerError
from assembler.token import TokenType


class LexerTest(unittest.TestCase):
    """
    @brief Tests for Lexer.
    """

    def test_identifier(self) -> None:
        tokens = Lexer("LD").tokenize()
        self.assertEqual(tokens[0].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[0].value, "LD")

    def test_register(self) -> None:
        tokens = Lexer("V0 VF VA").tokenize()
        self.assertEqual(tokens[0].type, TokenType.REGISTER)
        self.assertEqual(tokens[0].value, "V0")
        self.assertEqual(tokens[1].type, TokenType.REGISTER)
        self.assertEqual(tokens[1].value, "VF")
        self.assertEqual(tokens[2].type, TokenType.REGISTER)
        self.assertEqual(tokens[2].value, "VA")

    def test_identifier_that_is_not_register(self) -> None:
        tokens = Lexer("VALUE").tokenize()
        self.assertEqual(tokens[0].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[0].value, "VALUE")

    def test_decimal_number(self) -> None:
        tokens = Lexer("123").tokenize()
        self.assertEqual(tokens[0].type, TokenType.NUMBER)
        self.assertEqual(tokens[0].value, "123")

    def test_hexadecimal_number(self) -> None:
        tokens = Lexer("0xABC").tokenize()
        self.assertEqual(tokens[0].type, TokenType.NUMBER)
        self.assertEqual(tokens[0].value, "0xABC")

    def test_binary_number(self) -> None:
        tokens = Lexer("0b1010").tokenize()
        self.assertEqual(tokens[0].type, TokenType.NUMBER)
        self.assertEqual(tokens[0].value, "0b1010")

    def test_character(self) -> None:
        tokens = Lexer("'A'").tokenize()
        self.assertEqual(tokens[0].type, TokenType.CHARACTER)
        self.assertEqual(tokens[0].value, "A")

    def test_escaped_character(self) -> None:
        tokens = Lexer("'\\n'").tokenize()
        self.assertEqual(tokens[0].type, TokenType.CHARACTER)
        self.assertEqual(tokens[0].value, "\n")

    def test_string(self) -> None:
        tokens = Lexer('"HELLO"').tokenize()
        self.assertEqual(tokens[0].type, TokenType.STRING)
        self.assertEqual(tokens[0].value, "HELLO")

    def test_escaped_string(self) -> None:
        tokens = Lexer('"A\\nB"').tokenize()
        self.assertEqual(tokens[0].type, TokenType.STRING)
        self.assertEqual(tokens[0].value, "A\nB")

    def test_punctuation(self) -> None:
        tokens = Lexer(": , + - ( )").tokenize()
        expected = [
            TokenType.COLON,
            TokenType.COMMA,
            TokenType.PLUS,
            TokenType.MINUS,
            TokenType.LPAREN,
            TokenType.RPAREN
        ]
        self.assertEqual( [token.type for token in tokens[:-1]], expected)

    def test_end_of_line(self) -> None:
        tokens = Lexer("LD V0, 1\nLD V1, 2").tokenize()
        self.assertEqual(tokens[4].type, TokenType.END_OF_LINE)

    def test_end_of_file(self) -> None:
        tokens = Lexer("").tokenize()
        self.assertEqual( tokens[-1].type, TokenType.END_OF_FILE)

    def test_comments_are_ignored(self) -> None:
        tokens = Lexer("LD V0, 1 ; comment").tokenize()
        self.assertEqual(tokens[0].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[1].type, TokenType.REGISTER)
        self.assertEqual(tokens[2].type, TokenType.COMMA)
        self.assertEqual(tokens[3].type, TokenType.NUMBER)
        self.assertEqual(tokens[4].type, TokenType.END_OF_FILE)

    def test_comment_does_not_consume_newline(self) -> None:
        tokens = Lexer("LD V0, 1 ; comment\nLD V1, 2").tokenize()
        self.assertEqual(tokens[4].type, TokenType.END_OF_LINE)

    def test_source_locations(self) -> None:
        tokens = Lexer("LD V0, 1\nJP 0x200").tokenize()
        self.assertEqual(tokens[0].location.line, 1)
        self.assertEqual(tokens[0].location.column, 1)
        self.assertEqual(tokens[1].location.line, 1)
        self.assertEqual(tokens[1].location.column, 4)
        self.assertEqual(tokens[5].location.line, 2)
        self.assertEqual(tokens[5].location.column, 1)

    def test_unexpected_character(self) -> None:
        with self.assertRaises(LexerError):
            Lexer("LD V0, @").tokenize()

    def test_invalid_hexadecimal_literal(self) -> None:
        with self.assertRaises(LexerError):
            Lexer("0x").tokenize()

    def test_invalid_binary_literal(self) -> None:
        with self.assertRaises(LexerError):
            Lexer("0b").tokenize()

    def test_unterminated_character(self) -> None:
        with self.assertRaises(LexerError):
            Lexer("'A").tokenize()

    def test_unterminated_string(self) -> None:
        with self.assertRaises(LexerError):
            Lexer('"HELLO').tokenize()

    def test_invalid_escape(self) -> None:
        with self.assertRaises(LexerError):
            Lexer("'\\x'").tokenize()
