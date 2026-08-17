"""
@file isa.py

@brief Abstract base class for CHIP-8 instruction set architectures.

@author
Michael Dlubatz

@copyright
MIT License"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum

from assembler.instruction import AssemblerInstruction
from assembler.operand import AssemblerOperand
from chip8.isa.instruction import Instruction
from emulator.stepresult import StepResult


class ControlFlow(StrEnum):
    NEXT = "next"
    BRANCH = "branch"
    CONDITIONAL_BRANCH = "conditional_branch"
    CALL = "call"
    RETURN = "return"
    TERMINATE = "terminate"


@dataclass(frozen=True, slots=True)
class InstructionAnalysis:
    control_flow: ControlFlow
    targets: tuple[int, ...]
    is_code: bool


class InstructionSetArchitecture(ABC):
    """
    @brief Abstract base class for CHIP-8 instruction set architectures.

    An Instruction Set Architecture (ISA) defines the encoding, decoding
    and semantics of a particular CHIP-8 variant.

    Concrete implementations, such as Classic CHIP-8 or Super-CHIP,
    derive from this class and implement the behaviour of their
    respective instruction sets.
    """

    @abstractmethod
    def decode(self, address: int, opcode: int) -> Instruction:
        """
        @brief Decode an instruction.

        @param address
            Address of the instruction.

        @param opcode
            Raw 16-bit opcode.

        @return
            Decoded instruction.
        """
        raise NotImplementedError


    @abstractmethod
    def create_assembler_instruction( self, mnemonic: str, operands: tuple[AssemblerOperand, ...]) -> AssemblerInstruction:
        """
        @brief Construct an assembler instruction from a mnemonic and operands.

        @param mnemonic
            Assembly language instruction mnemonic.

        @param operands
            Evaluated assembler operands.

        @return
            Architecture-specific assembler instruction.

        @exception ValueError
            If the mnemonic or operand combination is invalid.
        """
        raise NotImplementedError


    @abstractmethod
    def encode(self, instruction: AssemblerInstruction) -> int:
        """
        @brief Encode an assembler instruction.

        @param instruction
            Instruction to encode.

        @return
            Raw 16-bit machine opcode.
        """
        raise NotImplementedError

    @abstractmethod
    def execute(self, instruction: Instruction) -> StepResult:
        """
        @brief Execute a decoded instruction.

        @param instruction
            Decoded instruction.

        @return
            Execution result.
        """
        raise NotImplementedError

    @abstractmethod
    def format(self, instruction: Instruction) -> str:
        """
        @brief Format a decoded instruction.

        @param instruction
            Decoded instruction.

        @return
            Assembly language representation.
        """
        raise NotImplementedError

    @abstractmethod
    def analyze(self, instruction: Instruction) -> InstructionAnalysis:
        """
        @brief Perform static analysis of a decoded instruction.

        @param instruction
            Decoded instruction.

        @return
            Static control-flow information for the instruction.
        """
        raise NotImplementedError
