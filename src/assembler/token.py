"""
@file token.py

@brief Token definitions for the assembler.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class TokenType(Enum):
    """
    @brief Types of tokens recognized by the assembler lexer.
    """

    IDENTIFIER = "IDENTIFIER"
    REGISTER = "REGISTER"
    NUMBER = "NUMBER"
    CHARACTER = "CHARACTER"
    STRING = "STRING"

    COLON = "COLON"
    COMMA = "COMMA"
    PLUS = "PLUS"
    MINUS = "MINUS"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"

    END_OF_LINE = "END_OF_LINE"
    END_OF_FILE = "END_OF_FILE"


@dataclass(frozen=True, slots=True)
class SourceLocation:
    """
    @brief Location of a token in the source file.
    """
    line: int
    column: int


@dataclass(frozen=True, slots=True)
class Token:
    """
    @brief Immutable lexical token.
    """
    type: TokenType
    value: str
    location: SourceLocation
