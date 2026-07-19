"""
@file chip8stack.py

@brief CHIP-8 call stack.

@details
Implements the fixed-size call stack used by the CHIP-8 virtual
machine.

The stack stores 12-bit return addresses and wraps around when the
stack pointer reaches either end, matching the behaviour of the
original interpreter.

@author
Michael Dlubatz

@copyright
MIT License
"""

from __future__ import annotations

from controller.applicationlogreporter import ApplicationLogReporter
from controller.diagnostics import DiagnosticReporter
from emulator.constants import ADDRESS_MASK, STACK_SIZE


class Chip8Stack:
    """
    @brief CHIP-8 call stack.
    """
    def __init__(self, diagnostics: DiagnosticReporter, logger: ApplicationLogReporter) -> None:
        """
        @brief Construct an empty stack.
        """
        self._diagnostics = diagnostics
        self._logger = logger
        self._stack: list[int] = [0] * STACK_SIZE       # we only store 12-bit return addresses
        self._sp: int = 0


    ###########################################################################
    # Public interface
    ###########################################################################
    def push(self, address: int) -> None:
        """
        @brief Push a return address onto the stack.

        The stack pointer intentionally wraps around after STACK_SIZE. This simulates
        the behaviour of the original.

        @param address
            Return address.
        """
        self._stack[self._sp] = address & ADDRESS_MASK  #
        if self._sp >= STACK_SIZE:
            self._logger.warning("CHIP-8 stack overflow.")
            self._diagnostics.warning("CHIP-8 stack overflow.")
        self._sp = (self._sp + 1) % STACK_SIZE          # modulo addressing allows wrap-around


    def pop(self) -> int:
        """
        @brief Pop a return address from the stack.

        @return
            Return address.
        """
        if self._sp <= 0:
            self._logger.warning("CHIP-8 stack underflow.")
            self._diagnostics.warning("CHIP-8 stack underflow.")
        self._sp = (self._sp - 1) % STACK_SIZE
        return self._stack[self._sp]


    def reset(self) -> None:
        """
        @brief Reset the stack.
        """
        self._logger.info("Stack reset.")
        self._stack[:] = [0] * STACK_SIZE   # slice assignment reuses the existing list instead of allocating a new one
        self._sp = 0
