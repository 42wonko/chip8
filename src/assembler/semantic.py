"""
@file semantic.py

@brief Semantic analysis and expression evaluation for the assembler.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from assembler.ast import (
    AssemblyNode,
    BinaryExpression,
    BinaryOperator,
    DirectiveNode,
    Expression,
    IdentifierExpression,
    IndirectExpression,
    InstructionNode,
    LiteralExpression,
    SourceLine,
)
from assembler.instruction import AssemblerInstruction
from assembler.operand import AssemblerOperand, AssemblerOperandType
from assembler.symbol import SymbolTable
from assembler.token import SourceLocation
from chip8.isa.isa import InstructionSetArchitecture
from chip8.isa.reference import InstructionReference, ReferenceAccess
from emulator.constants import PROGRAM_START


class SymbolCollector:
    """
    @brief Collects symbols defined by an assembly AST.
    """

    def __init__(self, symbols: SymbolTable, isa: InstructionSetArchitecture) -> None:
        """
        @brief Construct a symbol collector.

        @param symbols
            Symbol table to populate.
        """
        self._symbols   = symbols
        self._isa       = isa


    def collect(self, assembly: AssemblyNode) -> None:
        """
        @brief Collect symbols from an assembly AST.

        @param assembly
            Parsed assembly source.
        """
        address = PROGRAM_START
        evaluator = ExpressionEvaluator(self._symbols)

        for source_line in assembly.lines:
            try:
                statement = source_line.statement

                if isinstance(statement, DirectiveNode):
                    name = statement.name.upper()
                    if name == "EQU":
                        self._define_equ(source_line, evaluator)
                        continue
                    if name == "ORG":
                        address = self._resolve_org(statement, evaluator)
                        continue
                    if source_line.label is not None:
                        self._symbols.define( source_line.label.name, address, source_line.label.location)
                    if name == "DB":
                        address += self._resolve_db_size(statement, evaluator)
                        continue
                    if name == "TARGET":
                        continue
                    raise ValueError( f"Unsupported directive '{statement.name}'.")
            except ValueError as error:
                if statement is not None:
                    raise SemanticAnalysisError( str(error), statement.location) from error
                if source_line.label is not None:
                    raise SemanticAnalysisError( str(error), source_line.label.location) from error
                raise
            if source_line.label is not None:
                self._symbols.define( source_line.label.name, address, source_line.label.location)
            if statement is None:
                continue
            if isinstance(statement, InstructionNode):
                address += self._isa.assembler_instruction_size( statement.mnemonic, len(statement.operands))
                continue
            raise ValueError( f"Unsupported statement type: {type(statement).__name__}")

    ###########################################################################
    # private helper functions
    ###########################################################################
    def _resolve_org( self, directive: DirectiveNode, evaluator: ExpressionEvaluator) -> int:
        """
        @brief Resolve an ORG directive.

        @param directive
            ORG directive.

        @param evaluator
            Expression evaluator used to resolve the address.

        @return
            New assembly address.
        """
        if len(directive.operands) != 1:
            raise ValueError("ORG requires exactly one operand.")
        try:
            address = evaluator.evaluate(directive.operands[0])
        except ValueError as error:
            raise ValueError( "ORG operand must be an evaluatable integer expression.") from error
        if not 0 <= address <= 0xFFFF:
            raise ValueError( "ORG address must be in the range 0x0000 to 0xFFFF.")
        return address

    def _define_equ( self, source_line: SourceLine, evaluator: ExpressionEvaluator) -> None:
        """
        @brief Define a symbol using an EQU directive.
        """
        statement = source_line.statement
        if not isinstance(statement, DirectiveNode):
            raise ValueError("EQU requires a directive statement.")
        if source_line.label is None:
            raise ValueError("EQU requires a label.")
        if len(statement.operands) != 1:
            raise ValueError("EQU requires exactly one operand.")
        value = evaluator.evaluate(statement.operands[0])
        self._symbols.define( source_line.label.name, value, source_line.label.location)


    def _resolve_db_size( self, directive: DirectiveNode, evaluator: ExpressionEvaluator) -> int:
        """
        @brief Validate a DB directive and return its emitted byte count.
        """
        if len(directive.operands) == 0:
            raise ValueError("DB requires at least one operand.")
        size = 0
        for operand in directive.operands:
            if isinstance(operand, LiteralExpression):
                if isinstance(operand.value, str):
                    for character in operand.value:
                        if ord(character) > 0xFF:
                            raise ValueError( "DB string contains a character outside the byte range.")
                    size += len(operand.value)
                    continue
            value = evaluator.evaluate(operand)
            if not 0 <= value <= 0xFF:
                raise ValueError( f"DB value {value} is outside the range 0x00 to 0xFF.")
            size += 1
        return size


@dataclass(frozen=True, slots=True)
class Reference:
    """
    @brief A cross-reference to a symbol or architectural resource.
    """
    name: str
    access: ReferenceAccess
    location: SourceLocation


class SymbolReferenceCollector:
    """
    @brief Collects references to symbols used by an assembly AST.
    """

    def __init__(self, symbols: SymbolTable) -> None:
        """
        @brief Construct a symbol reference collector.

        @param symbols
            Symbol table containing the defined symbols.
        """
        self._symbols = symbols
        self._references: list[Reference] = []


    def collect(self, assembly: AssemblyNode) -> None:
        """
        @brief Collect symbol references from an assembly AST.

        @param assembly
            Parsed assembly source.
        """
        for source_line in assembly.lines:
            statement = source_line.statement
            if isinstance(statement, InstructionNode):
                for operand in statement.operands:
                    self._collect_expression(operand)
                continue
            if isinstance(statement, DirectiveNode):
                name = statement.name.upper()
                if name == "EQU":
                    for operand in statement.operands:
                        self._collect_expression(operand)
                    continue
                if name == "ORG":
                    for operand in statement.operands:
                        self._collect_expression(operand)
                    continue
                if name == "DB":
                    for operand in statement.operands:
                        self._collect_expression(operand)
                    continue


    def add_instruction_references( self, instruction: AssemblerInstruction, location: SourceLocation, references: tuple[InstructionReference, ...]) -> None:
        """
        @brief Add architectural resource references for an instruction.

        @param instruction
            Resolved assembler instruction.

        @param location
            Source location of the instruction.

        @param references
            Architectural resources accessed by the instruction.
        """
        del instruction

        for reference in references:
            self._references.append( Reference( name=reference.resource, access=reference.access, location=location))


    def references(self) -> tuple[Reference, ...]:
        """
        @brief Return collected architectural resource references.
        """
        return tuple(self._references)


    def _collect_expression(self, expression: Expression) -> None:
        """
        @brief Collect symbol references from an expression.
        """
        if isinstance(expression, IdentifierExpression):
            if self._symbols.contains(expression.name):
                self._symbols.add_reference( expression.name, expression.location)
            return
        if isinstance(expression, BinaryExpression):
            self._collect_expression(expression.left)
            self._collect_expression(expression.right)


class SemanticAnalysisError(ValueError):
    """
    @brief Raised when semantic analysis fails for a source line.
    """

    def __init__(self, message: str, location: SourceLocation) -> None:
        super().__init__(message)
        self.location = location


class ExpressionEvaluationError(ValueError):
    """
    @brief Raised when an assembler expression cannot be evaluated.
    """


class ExpressionEvaluator:
    """
    @brief Evaluates assembler AST expressions.
    """
    def __init__(self, symbols: SymbolTable) -> None:
        """
        @brief Construct an expression evaluator.

        @param symbols
            Symbol table used to resolve identifiers.
        """
        self._symbols = symbols

    def evaluate(self, expression: Expression) -> int:
        """
        @brief Evaluate an expression to an integer value.

        @param expression
            Expression to evaluate.

        @return
            Evaluated integer value.

        @exception ExpressionEvaluationError
            If the expression type is unsupported.
        """
        if isinstance(expression, LiteralExpression):
            if not isinstance(expression.value, int):
                raise ExpressionEvaluationError( "String literals cannot be evaluated as integers.")
            return expression.value
        if isinstance(expression, IdentifierExpression):
            return self._symbols.lookup(expression.name).value
        if isinstance(expression, BinaryExpression):
            return self._evaluate_binary(expression)
        raise ExpressionEvaluationError( f"Unsupported expression type: {type(expression).__name__}")

    def _evaluate_binary(self, expression: BinaryExpression) -> int:
        """
        @brief Evaluate a binary expression.
        """
        left = self.evaluate(expression.left)
        right = self.evaluate(expression.right)
        if expression.operator == BinaryOperator.ADD:
            return left + right
        if expression.operator == BinaryOperator.SUBTRACT:
            return left - right
        raise ExpressionEvaluationError( f"Unsupported binary operator: {expression.operator}")



class OperandResolver:
    """
    @brief Resolves assembler expressions into typed operands.
    """

    def __init__(self, symbols: SymbolTable, isa: InstructionSetArchitecture) -> None:
        """
        @brief Construct an operand resolver.

        @param symbols
            Symbol table used to resolve identifiers.
        """
        self._evaluator = ExpressionEvaluator(symbols)
        self._symbols   = symbols
        self._isa       = isa


    def resolve( self, expression: Expression, operand_type: AssemblerOperandType) -> AssemblerOperand:
        """
        @brief Resolve an expression into an assembler operand.

        @param expression
            Operand expression from the assembler AST.

        @param operand_type
            Required assembler operand type.

        @return
            Resolved assembler operand.

        @exception ExpressionEvaluationError
            If the expression cannot represent the requested operand.
        """
        if isinstance(expression, IndirectExpression):
            return self._resolve_indirect(expression)

        if isinstance(expression, IdentifierExpression):
            return self._resolve_identifier(expression, operand_type)

        if isinstance(expression, BinaryExpression):
            value = self._evaluator.evaluate(expression)
            return self._resolve_value(value, operand_type)

        if isinstance(expression, LiteralExpression):
            if not isinstance(expression.value, int):
                raise ExpressionEvaluationError( "String literals cannot be used as instruction operands.")
            return self._resolve_value(expression.value, operand_type)

        raise ExpressionEvaluationError( f"Unsupported operand expression type: " f"{type(expression).__name__}")


    ###############################################################################
    # Private helpers
    ###############################################################################
    def _resolve_indirect( self, expression: IndirectExpression) -> AssemblerOperand:
        inner = expression.expression
        if not isinstance(inner, IdentifierExpression):
            raise ExpressionEvaluationError( "Indirect operand must use an architecture-specific index register.")
        operand = self._isa.assembler_operand(inner.name)
        if operand is None or operand.type != AssemblerOperandType.INDEX_REGISTER:
            raise ExpressionEvaluationError( "Indirect operand must use an architecture-specific index register.")
        return AssemblerOperand( type=AssemblerOperandType.INDIRECT_INDEX, value=operand.value)

    def _resolve_identifier( self, expression: IdentifierExpression, operand_type: AssemblerOperandType) -> AssemblerOperand:
        """
        @brief Resolve an identifier operand.
        """
        architectural_operand = self._isa.assembler_operand(expression.name)
        if architectural_operand is not None:
            if architectural_operand.type != operand_type:
                raise ExpressionEvaluationError(
                    f"Operand '{expression.name}' has type "
                    f"{architectural_operand.type.value}, expected "
                    f"{operand_type.value}."
                )
            return architectural_operand
        name = expression.name.upper()
        if self._symbols.contains(name):
            value = self._evaluator.evaluate(expression)
            return self._resolve_value(value, operand_type)
        raise ExpressionEvaluationError( f"Unknown assembler operand '{expression.name}'.")


    def _resolve_value( self, value: int, operand_type: AssemblerOperandType) -> AssemblerOperand:
        """
        @brief Resolve an evaluated integer according to its required type.
        """
        if operand_type not in ( AssemblerOperandType.VALUE, AssemblerOperandType.ADDRESS):
            raise ExpressionEvaluationError( f"Integer value cannot be resolved as {operand_type.value}.")
        return AssemblerOperand( type=operand_type, value=value)

class AssemblerInstructionFactory(Protocol):
    """
    @brief Interface required by InstructionResolver to create instructions.
    """
    def assembler_operand_signatures( self, mnemonic: str, operand_count: int) -> tuple[tuple[AssemblerOperandType, ...], ...]:
        """
        @brief Return legal assembler operand signatures.
        """
    def create_assembler_instruction( self, mnemonic: str, operands: tuple[AssemblerOperand, ...]) -> AssemblerInstruction:
        """
        @brief Create an assembler instruction from resolved operands.
        """

    def instruction_references( self, instruction: AssemblerInstruction) -> tuple[InstructionReference, ...]:
        """
        @brief Determine the architectural resources accessed by an instruction.
        """

class InstructionResolver:
    """
    @brief Resolves parsed instructions into assembler instructions.
    """

    def __init__( self, symbols: SymbolTable, isa: InstructionSetArchitecture) -> None:
        """
        @brief Construct an instruction resolver.

        @param symbols
            Symbol table used to resolve operands.

        @param isa
            Instruction-set architecture used to create the instruction.
        """
        self._operand_resolver = OperandResolver(symbols, isa)
        self._isa = isa

    def resolve(self, instruction: InstructionNode) -> AssemblerInstruction:
        """
        @brief Resolve an instruction AST node.

        @param instruction
            Parsed instruction.

        @return
            Assembler instruction.

        @exception ExpressionEvaluationError
            If the instruction cannot be resolved.
        """
        signatures = self._isa.assembler_operand_signatures( instruction.mnemonic, len(instruction.operands))
        if not signatures:
            raise ExpressionEvaluationError( f"Unsupported instruction '{instruction.mnemonic}'.")
        last_error: ExpressionEvaluationError | None = None
        for signature in signatures:
            try:
                operands = self._resolve_operands( instruction.operands, signature)
            except ExpressionEvaluationError as error:
                last_error = error
                continue
            try:
                return self._isa.create_assembler_instruction( instruction.mnemonic, operands)
            except ValueError as error:
                last_error = ExpressionEvaluationError(str(error))
        if last_error is not None:
            raise last_error
        raise ExpressionEvaluationError( f"Invalid operands for instruction '{instruction.mnemonic}'.")

    def instruction_references( self, instruction: AssemblerInstruction) -> tuple[InstructionReference, ...]:
        """
        @brief Determine architectural resources accessed by an instruction.

        @param instruction
            Resolved assembler instruction.

        @return
            Architectural resources accessed by the instruction.
        """
        return self._isa.instruction_references(instruction)


    ###############################################################################
    # Private helpers
    ###############################################################################
    def _resolve_operands( self, expressions: tuple[Expression, ...], operand_types: tuple[AssemblerOperandType, ...]) -> tuple[AssemblerOperand, ...]:
        """
        @brief Resolve expressions according to one operand signature.
        """
        if len(expressions) != len(operand_types):
            raise ExpressionEvaluationError("Operand count does not match signature.")
        return tuple(
            self._operand_resolver.resolve(expression, operand_type)
            for expression, operand_type in zip(expressions, operand_types)
        )



