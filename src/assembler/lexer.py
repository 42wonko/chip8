"""
@file lexer.py

@brief Lexical analysis of assembler source code.
"""

from __future__ import annotations

from assembler.token import SourceLocation, Token, TokenType


class LexerError(ValueError):
    """
    @brief Raised when lexical analysis fails.
    """


class Lexer:
    """
    @brief Converts assembler source text into lexical tokens.
    """

    def __init__(self, source: str) -> None:
        """
        @brief Initialize the lexer.

        @param source
            Assembly source code.
        """
        self._source = source
        self._position = 0
        self._line = 1
        self._column = 1


    def tokenize(self) -> list[Token]:
        """
        @brief Tokenize the complete source.

        @return
            List of tokens including an END_OF_FILE token.

        @exception LexerError
            If invalid lexical input is encountered.
        """
        tokens: list[Token] = []

        while not self._at_end():
            character = self._current()
            if character in " \t\r":
                self._advance()
                continue
            if character == "\n":
                tokens.append(self._single_character_token( TokenType.END_OF_LINE))
                continue
            if character == ";":
                self._skip_comment()
                continue
            if character.isalpha() or character == "_":
                tokens.append(self._identifier())
                continue
            if character.isdigit():
                tokens.append(self._number())
                continue
            if character == "'":
                tokens.append(self._character())
                continue
            if character == '"':
                tokens.append(self._string())
                continue

            punctuation = {
                ":": TokenType.COLON,
                ",": TokenType.COMMA,
                "+": TokenType.PLUS,
                "-": TokenType.MINUS,
                "(": TokenType.LPAREN,
                ")": TokenType.RPAREN
            }

            token_type = punctuation.get(character)

            if token_type is not None:
                tokens.append(self._single_character_token(token_type))
                continue

            raise LexerError( f"Unexpected character '{character}' at " f"{self._line}:{self._column}.")

        tokens.append(
            Token(
                type=TokenType.END_OF_FILE,
                value="",
                location=SourceLocation( line=self._line, column=self._column)
            )
        )

        return tokens


    def _identifier(self) -> Token:
        """
        @brief Read an identifier or register.

        @return
            Identifier or register token.
        """
        location = self._location()
        start = self._position

        while not self._at_end():
            character = self._current()
            if not ( character.isalnum() or character == "_"):
                break
            self._advance()
        value = self._source[start:self._position]
        if self._is_register(value):
            return Token( type=TokenType.REGISTER, value=value.upper(), location=location)
        return Token( type=TokenType.IDENTIFIER, value=value, location=location)


    def _number(self) -> Token:
        """
        @brief Read a numeric literal.

        @return
            Number token.

        @exception LexerError
            If a hexadecimal or binary literal is malformed.
        """
        location = self._location()
        start = self._position

        if self._current() == "0" and self._has_next():
            next_character = self._peek()

            if next_character in "xX":              # find hexadecimal numbers
                self._advance()
                self._advance()
                digit_start = self._position
                while not self._at_end() and self._current() in ( "0123456789abcdefABCDEF"):
                    self._advance()
                if self._position == digit_start:
                    raise LexerError( f"Invalid hexadecimal literal at " f"{location.line}:{location.column}.")
                return Token(
                    type=TokenType.NUMBER,
                    value=self._source[start:self._position],
                    location=location
                )

            if next_character in "bB":              # find binary numbers
                self._advance()
                self._advance()
                digit_start = self._position
                while not self._at_end() and self._current() in "01":
                    self._advance()
                if self._position == digit_start:
                    raise LexerError(
                        f"Invalid binary literal at "
                        f"{location.line}:{location.column}."
                    )
                return Token(
                    type=TokenType.NUMBER,
                    value=self._source[start:self._position],
                    location=location
                )

        while not self._at_end() and self._current().isdigit():
            self._advance()

        return Token(
            type=TokenType.NUMBER,
            value=self._source[start:self._position],
            location=location
        )


    def _character(self) -> Token:
        """
        @brief Read a character literal.

        @return
            Character token.

        @exception LexerError
            If the character literal is malformed.
        """
        location = self._location()
        self._advance()
        if self._at_end() or self._current() == "\n":
            raise LexerError( f"Unterminated character literal at " f"{location.line}:{location.column}.")
        value = self._read_literal_character(location)
        if self._at_end() or self._current() != "'":
            raise LexerError( f"Unterminated character literal at " f"{location.line}:{location.column}.")
        self._advance()
        return Token(
            type=TokenType.CHARACTER,
            value=value,
            location=location
        )


    def _string(self) -> Token:
        """
        @brief Read a string literal.

        @return
            String token.

        @exception LexerError
            If the string literal is malformed.
        """
        location = self._location()
        self._advance()
        characters: list[str] = []
        while not self._at_end():
            if self._current() == '"':
                self._advance()
                return Token(
                    type=TokenType.STRING,
                    value="".join(characters),
                    location=location
                )
            if self._current() == "\n":
                raise LexerError( f"Unterminated string literal at " f"{location.line}:{location.column}.")
            characters.append( self._read_literal_character(location))
        raise LexerError( f"Unterminated string literal at " f"{location.line}:{location.column}.")


    def _read_literal_character( self, location: SourceLocation) -> str:
        """
        @brief Read one character from a character or string literal.

        @param location
            Location of the literal.

        @return
            Decoded character.

        @exception LexerError
            If an escape sequence is invalid.
        """
        if self._current() != "\\":
            character = self._current()
            self._advance()
            return character
        self._advance()
        if self._at_end():
            raise LexerError( f"Invalid escape sequence at " f"{location.line}:{location.column}.")
        escapes = { "n": "\n", "r": "\r", "t": "\t", "\\": "\\", "'": "'", '"': '"' }
        character = self._current()
        self._advance()
        if character not in escapes:
            raise LexerError( f"Invalid escape sequence '\\{character}' at " f"{location.line}:{location.column}.")
        return escapes[character]


    def _skip_comment(self) -> None:
        """
        @brief Skip a comment until the end of the line.
        """
        while not self._at_end() and self._current() != "\n":
            self._advance()


    def _single_character_token( self, token_type: TokenType) -> Token:
        """
        @brief Create a token for the current single character.

        @param token_type
            Token type.

        @return
            Created token.
        """
        location = self._location()
        value = self._current()
        self._advance()
        return Token( type=token_type, value=value, location=location)


    def _location(self) -> SourceLocation:
        """
        @brief Return the current source location.

        @return
            Current source location.
        """
        return SourceLocation( line=self._line, column=self._column)


    def _current(self) -> str:
        """
        @brief Return the current character.

        @return
            Current character.
        """
        return self._source[self._position]


    def _peek(self) -> str:
        """
        @brief Return the character following the current character.

        @return
            Following character.
        """
        return self._source[self._position + 1]


    def _advance(self) -> None:
        """
        @brief Advance the lexer by one character.
        """
        character = self._source[self._position]
        self._position += 1
        if character == "\n":
            self._line += 1
            self._column = 1
        else:
            self._column += 1


    def _has_next(self) -> bool:
        """
        @brief Determine whether another character follows the current one.

        @return
            True if another character exists.
        """
        return self._position + 1 < len(self._source)


    def _at_end(self) -> bool:
        """
        @brief Determine whether the end of the source was reached.

        @return
            True if the lexer is at the end.
        """
        return self._position >= len(self._source)


    @staticmethod
    def _is_register(value: str) -> bool:
        """
        @brief Determine whether a string is a CHIP-8 register.

        @param value
            Identifier text.

        @return
            True if the identifier is V0 through VF.
        """
        if len(value) != 2:
            return False
        return value[0].upper() == "V" and value[1].upper() in ( "0123456789ABCDEF")

