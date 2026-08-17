"""
@file test_target.py

@brief Unit tests for assembler target definitions.
"""

import unittest

from assembler.target import Target


class TestTarget(unittest.TestCase):
    """
    @brief Test assembler target definitions.
    """

    def test_chip8_target(self) -> None:
        """
        @brief Verify the COSMAC target.
        """
        self.assertEqual(Target.COSMAC.value, "COSMAC")


if __name__ == "__main__":
    unittest.main()
