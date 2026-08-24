"""
@file parser.py

@brief Parser for assembler source tokens.
"""

from __future__ import annotations

from assembler.ast import (
    AssemblyNode,
    BinaryExpression,
    BinaryOperator,
    DirectiveNode,
     Expression,
    IdentifierExpression,
    InstructionNode,
    LabelNode,
    LiteralExpression,
    SourceLine,
)
from assembler.token import Token, TokenType


class ParserError(ValueError):
    """
    @brief Raised when parsing fails.
    """


class Parser:
    """
    @brief Parses assembler tokens into an abstract syntax tree.
    """

    def __init__(self, tokens: list[Token]) -> None:
        """
        @brief Initialize the parser.

        @param tokens
            Tokens produced by the assembler lexer.
        """
        self._tokens = tokens
        self._position = 0


    def parse(self) -> AssemblyNode:
        """
        @brief Parse the complete token stream.

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
        if self._match(TokenType.END_OF_LINE):
            return SourceLine( label=label, statement=statement)
        if self._check(TokenType.END_OF_FILE):
            return SourceLine( label=label, statement=statement)
        token = self._current()
        raise ParserError( f"Expected end of line. Found '{token.value}' at {token.location.line}:{token.location.column}.")


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
        token = self._expect( TokenType.IDENTIFIER, "Expected instruction or directive.")
        if token.value.upper() in ("TARGET", "ORG", "EQU", "DB"):
            return self._parse_directive(token)
        return self._parse_instruction(token)


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
                raise ParserError( f"Expected operand after comma at {token.location.line}:{token.location.column}.")
            if self._check(TokenType.END_OF_FILE):
                token = self._current()
                raise ParserError( f"Expected operand after comma at {token.location.line}:{token.location.column}.")
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
                raise ParserError( f"Invalid numeric literal '{token.value}' at {token.location.line}:{token.location.column}.") from error
            return LiteralExpression( value=value, location=token.location)
        if token.type == TokenType.CHARACTER:
            self._advance()
            if len(token.value) != 1:
                raise ParserError( f"Invalid character literal at {token.location.line}:{token.location.column}.")
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
        if token.type == TokenType.LPAREN:
            self._advance()
            expression = self._parse_expression()
            self._expect( TokenType.RPAREN, "Expected ')'.")
            return expression
        raise ParserError( f"Expected expression. Found '{token.value}' at {token.location.line}:{token.location.column}.")


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
            raise ParserError( f"{message} Found '{token.value}' at {token.location.line}:{token.location.column}.")
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

