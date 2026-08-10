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
