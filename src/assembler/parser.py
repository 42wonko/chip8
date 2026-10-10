"""
@file parser.py

@brief Parser for assembler source tokens.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from assembler.ast import (
    AssemblyNode,
    BinaryExpression,
    BinaryOperator,
    DirectiveNode,
    Expression,
    IdentifierExpression,
    IndirectExpression,
    InstructionNode,
    LabelNode,
    LiteralExpression,
    SourceLine,
)
from assembler.token import SourceLocation, Token, TokenType


class ParserError(ValueError):
    """
    @brief Raised when parsing fails.
    """
    def __init__(self, message: str, location: SourceLocation) -> None:
        super().__init__(message)
        self.location = location

class Parser(ABC):
    """
    @brief Parses assembler tokens into an abstract syntax tree.
    """

    def __init__(self) -> None:
        """
        @brief Initialize the parser.

        @param tokens
            Tokens produced by the assembler lexer.
        """
        self._tokens: list[Token] = []
        self._position = 0

    def set_tokens(self, tokens: list[Token]) -> None:
        """
        @brief Set the token stream to be parsed.

        @param tokens
            Tokens produced by the assembler lexer.
        """
        self._tokens = tokens
        self._position = 0

    def parse(self) -> AssemblyNode:
        """
        @brief Parse the complete token stream, stopping at the first error.

        @return
            Parsed assembler AST.

        @exception ParserError
            If the token stream does not conform to the assembler grammar.
        """
        lines: list[SourceLine] = []
        while not self._check(TokenType.END_OF_FILE):
            if self._match(TokenType.END_OF_LINE):
                continue
            lines.append(self._parse_line())
        return AssemblyNode(lines=tuple(lines))


    def parse_recovering(self) -> tuple[AssemblyNode, tuple[ParserError, ...]]:
        """
        @brief Parse source lines while collecting recoverable syntax errors.

        A malformed line is discarded and parsing resumes at the next source
        line. The returned AST may therefore be partial and must not be used
        for semantic analysis or code generation when errors were reported.

        @return
            The successfully parsed lines and all parser errors encountered.
        """
        lines: list[SourceLine] = []
        errors: list[ParserError] = []

        while not self._check(TokenType.END_OF_FILE):
            if self._match(TokenType.END_OF_LINE):
                continue

            position_before_line = self._position
            try:
                lines.append(self._parse_line())
            except ParserError as error:
                errors.append(error)
                self._synchronize_to_next_line()

            # Guard against a malformed parser branch that fails to consume
            # input. This guarantees forward progress unless at end-of-file.
            if (
                self._position == position_before_line
                and not self._check(TokenType.END_OF_FILE)
            ):
                self._advance()

        return AssemblyNode(lines=tuple(lines)), tuple(errors)


    def _synchronize_to_next_line(self) -> None:
        """
        @brief Skip the remainder of a malformed line.

        The end-of-line token is consumed so the next parse iteration starts
        at the beginning of the next source line. End-of-file is left intact.
        """
        while (
            not self._check(TokenType.END_OF_LINE)
            and not self._check(TokenType.END_OF_FILE)
        ):
            self._advance()
        self._match(TokenType.END_OF_LINE)


    def _parse_line(self) -> SourceLine:
        """
        @brief Parse one source line.

        @return
            Parsed source line.
        """
        label: LabelNode | None = None
        if self._check(TokenType.IDENTIFIER):
            if self._check_next(TokenType.COLON):
                label = self._parse_label()
        if self._match(TokenType.END_OF_LINE):
            return SourceLine( label=label, statement=None)
        if self._check(TokenType.END_OF_FILE):
            return SourceLine( label=label, statement=None)
        statement = self._parse_statement()
        if isinstance(statement, DirectiveNode):
            directive = statement.name.upper()
            if label is not None and directive in ("TARGET", "ORG"):
                raise ParserError( f"A label cannot be used with the {directive} directive.", label.location)
            if label is None and directive in ("EQU", "DB", "DW"):
                raise ParserError( f"{directive} requires a label.", statement.location)
        if self._match(TokenType.END_OF_LINE):
            return SourceLine( label=label, statement=statement)
        if self._check(TokenType.END_OF_FILE):
            return SourceLine( label=label, statement=statement)
        token = self._current()
        raise ParserError( f"Expected end of line. Found '{token.value}' at {token.location.line}:{token.location.column}.", token.location)


    def _parse_label(self) -> LabelNode:
        """
        @brief Parse a label declaration.

        @return
            Parsed label.
        """
        token = self._expect( TokenType.IDENTIFIER, "Expected label name.")
        self._expect( TokenType.COLON, "Expected ':' after label.")
        return LabelNode( name=token.value, location=token.location)


    def _parse_statement(self) -> InstructionNode | DirectiveNode:
        """
        @brief Parse an instruction or directive.

        @return
            Parsed statement.
        """
        token = self._expect(TokenType.IDENTIFIER, "Expected instruction or directive.")
        if token.value.upper() in ("TARGET", "ORG", "EQU", "DB", "DW"):
            return self._parse_directive(token)
        if not self._is_instruction_mnemonic(token.value):
            raise ParserError( f"Unsupported instruction '{token.value}'.", token.location,)
        return self._parse_instruction(token)

    @abstractmethod
    def _is_instruction_mnemonic(self, mnemonic: str) -> bool:
        """
        @brief Determine whether a mnemonic is accepted as an instruction.

        The base parser accepts identifier-shaped instruction names. Concrete
        architecture-specific parsers may override this method.

        @param mnemonic
            Instruction mnemonic.

        @return
            True if the mnemonic is accepted.
        """
        raise NotImplementedError

    def _parse_instruction(self, mnemonic: Token) -> InstructionNode:
        """
        @brief Parse an instruction.

        @param mnemonic
            Instruction mnemonic token.

        @return
            Parsed instruction.
        """
        operands = self._parse_operands()
        return InstructionNode( mnemonic=mnemonic.value, operands=tuple(operands), location=mnemonic.location)


    def _parse_directive(self, name: Token) -> DirectiveNode:
        """
        @brief Parse an assembler directive.

        @param name
            Directive name token.

        @return
            Parsed directive.
        """
        operands = self._parse_operands()
        return DirectiveNode( name=name.value, operands=tuple(operands), location=name.location)


    def _parse_operands(self) -> list[Expression]:
        """
        @brief Parse a comma-separated operand list.

        @return
            Parsed operands.
        """
        operands: list[Expression] = []
        if self._check(TokenType.END_OF_LINE):
            return operands
        if self._check(TokenType.END_OF_FILE):
            return operands
        operands.append(self._parse_expression())
        while self._match(TokenType.COMMA):
            if self._check(TokenType.END_OF_LINE):
                token = self._current()
                raise ParserError( f"Expected operand after comma at {token.location.line}:{token.location.column}.",token.location)
            if self._check(TokenType.END_OF_FILE):
                token = self._current()
                raise ParserError( f"Expected operand after comma at {token.location.line}:{token.location.column}.", token.location)
            operands.append(self._parse_expression())
        return operands


    def _parse_expression(self) -> Expression:
        """
        @brief Parse an arithmetic expression.

        @return
            Parsed expression.

        @exception ParserError
            If an expression is malformed.
        """
        expression = self._parse_primary()
        while self._check(TokenType.PLUS) or self._check(TokenType.MINUS):
            operator_token = self._advance()
            right = self._parse_primary()
            if operator_token.type == TokenType.PLUS:
                operator = BinaryOperator.ADD
            else:
                operator = BinaryOperator.SUBTRACT
            expression = BinaryExpression( operator=operator, left=expression, right=right, location=expression.location)
        return expression


    def _parse_primary(self) -> Expression:
        """
        @brief Parse the primary expression at the current position.

        @return
            Parsed primary expression.

        @exception ParserError
            If the current token cannot begin an expression.
        """
        token = self._current()
        if token.type == TokenType.NUMBER:
            self._advance()
            try:
                value = int(token.value, 0)
            except ValueError as error:
                raise ParserError( f"Invalid numeric literal '{token.value}' at {token.location.line}:{token.location.column}.", token.location) from error
            return LiteralExpression( value=value, location=token.location)
        if token.type == TokenType.CHARACTER:
            self._advance()
            if len(token.value) != 1:
                raise ParserError( f"Invalid character literal at {token.location.line}:{token.location.column}.", token.location)
            return LiteralExpression( value=ord(token.value), location=token.location)
        if token.type == TokenType.STRING:
            self._advance()
            return LiteralExpression( value=token.value, location=token.location)
        if token.type == TokenType.IDENTIFIER:
            self._advance()
            return IdentifierExpression( name=token.value, location=token.location)
        if token.type == TokenType.REGISTER:
            self._advance()
            return IdentifierExpression( name=token.value, location=token.location)
        if token.type == TokenType.LBRACKET:
            self._advance()
            expression = self._parse_expression()
            self._expect( TokenType.RBRACKET, "Expected ']'.")
            return IndirectExpression( expression=expression, location=token.location)
        if token.type == TokenType.LPAREN:
            self._advance()
            expression = self._parse_expression()
            self._expect( TokenType.RPAREN, "Expected ')'.")
            return expression
        raise ParserError( f"Expected expression. Found '{token.value}' at {token.location.line}:{token.location.column}.", token.location)


    def _expect( self, token_type: TokenType, message: str) -> Token:
        """
        @brief Consume a token of the expected type.

        @param token_type
            Expected token type.

        @param message
            Error message.

        @return
            Consumed token.

        @exception ParserError
            If the current token has the wrong type.
        """
        if not self._check(token_type):
            token = self._current()
            raise ParserError( f"{message} Found '{token.value}' at {token.location.line}:{token.location.column}.", token.location)
        return self._advance()


    def _match(self, token_type: TokenType) -> bool:
        """
        @brief Consume a token if it has the requested type.

        @param token_type
            Token type.

        @return
            True if the token was consumed.
        """
        if not self._check(token_type):
            return False
        self._advance()
        return True


    def _check(self, token_type: TokenType) -> bool:
        """
        @brief Check the current token type.

        @param token_type
            Token type.

        @return
            True if the current token has the requested type.
        """
        return self._current().type == token_type


    def _check_next(self, token_type: TokenType) -> bool:
        """
        @brief Check the next token type.

        @param token_type
            Token type.

        @return
            True if the next token has the requested type.
        """
        if self._position + 1 >= len(self._tokens):
            return False
        return self._tokens[self._position + 1].type == token_type


    def _current(self) -> Token:
        """
        @brief Return the current token.

        @return
            Current token.
        """
        return self._tokens[self._position]


    def _advance(self) -> Token:
        """
        @brief Consume and return the current token.

        @return
            Consumed token.
        """
        token = self._current()
        self._position += 1
        return token

