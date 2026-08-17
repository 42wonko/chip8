"""
@file test_token.py

@brief Unit tests for assembler tokens.
"""

import unittest

from assembler.token import SourceLocation, Token, TokenType


class TokenTest(unittest.TestCase):
    """
    @brief Tests for Token and SourceLocation.
    """

    def test_source_location(self) -> None:
        location = SourceLocation( line=3, column=7)
        self.assertEqual(location.line, 3)
        self.assertEqual(location.column, 7)

    def test_token(self) -> None:
        token = Token( type=TokenType.IDENTIFIER, value="LD", location=SourceLocation( line=1, column=1))
        self.assertEqual(token.type, TokenType.IDENTIFIER)
        self.assertEqual(token.value, "LD")
        self.assertEqual(token.location.line, 1)
        self.assertEqual(token.location.column, 1)

    def test_token_is_immutable(self) -> None:
        token = Token( type=TokenType.IDENTIFIER, value="LD", location=SourceLocation( line=1, column=1))
        with self.assertRaises(AttributeError):
            token.value = "JP"
