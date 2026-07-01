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

from emulator.constants import ADDRESS_MASK, STACK_SIZE


class Chip8Stack:
    """
    @brief CHIP-8 call stack.
    """
    def __init__(self) -> None:
        """
        @brief Construct an empty stack.
        """
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
        self._sp = (self._sp + 1) % STACK_SIZE          # modulo addressing allows wrap-around


    def pop(self) -> int:
        """
        @brief Pop a return address from the stack.

        @return
            Return address.
        """
        self._sp = (self._sp - 1) % STACK_SIZE
        return self._stack[self._sp]


    def reset(self) -> None:
        """
        @brief Reset the stack.
        """
        self._stack[:] = [0] * STACK_SIZE   # slice assignment reuses the existing list instead of allocating a new one
        self._sp = 0
