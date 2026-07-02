"""
@file test_stack.py

@brief Unit tests for the CHIP-8 stack.
"""

import unittest

from emulator.chip8stack import Chip8Stack
from emulator.constants import (
    ADDRESS_MASK,
    STACK_SIZE,
)


class TestChip8Stack(unittest.TestCase):
    """
    @brief Tests for the CHIP-8 stack.
    """

    ###########################################################################
    # Construction
    ###########################################################################

    def test_pop_from_empty_stack(self) -> None:
        stack = Chip8Stack()

        #
        # Original CHIP-8 behaviour:
        # SP wraps around, therefore popping an empty stack returns whatever
        # happens to be stored in the wrapped entry.
        #
        self.assertEqual(stack.pop(), 0)

    ###########################################################################
    # Push / Pop
    ###########################################################################

    def test_push_pop(self) -> None:
        stack = Chip8Stack()

        stack.push(0x456)

        self.assertEqual(stack.pop(), 0x456)

    def test_lifo(self) -> None:
        stack = Chip8Stack()

        stack.push(0x111)
        stack.push(0x222)
        stack.push(0x333)

        self.assertEqual(stack.pop(), 0x333)
        self.assertEqual(stack.pop(), 0x222)
        self.assertEqual(stack.pop(), 0x111)

    ###########################################################################
    # Address masking
    ###########################################################################

    def test_address_masking(self) -> None:
        stack = Chip8Stack()

        stack.push(0xFFFF)

        self.assertEqual(stack.pop(), ADDRESS_MASK)

    ###########################################################################
    # Wrap-around
    ###########################################################################

    def test_stack_pointer_wraps_on_push(self) -> None:
        stack = Chip8Stack()

        #
        # Push more values than the hardware stack can hold.
        #
        for address in range(STACK_SIZE + 1):
            stack.push(address)

        #
        # The oldest entry has been overwritten.
        #
        self.assertEqual(stack.pop(), STACK_SIZE)

    def test_stack_pointer_wraps_on_pop(self) -> None:
        stack = Chip8Stack()

        stack.push(0x123)

        #
        # First pop returns the stored value.
        #
        self.assertEqual(stack.pop(), 0x123)

        #
        # Second pop wraps around and returns whatever is now at the last
        # stack entry.
        #
        self.assertEqual(stack.pop(), 0)

    def test_push_masks_address(self) -> None:
        stack = Chip8Stack()
        stack.push(0xFFFF)
        self.assertEqual(stack.pop(), ADDRESS_MASK)

    ###########################################################################
    # Reset
    ###########################################################################

    def test_reset(self) -> None:
        stack = Chip8Stack()

        stack.push(0x111)
        stack.push(0x222)

        stack.reset()

        self.assertEqual(stack.pop(), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
