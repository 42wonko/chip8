"""
@file test_options.py

@brief Unit tests for assembler options.
"""

import unittest

from assembler.options import AssemblyOptions


class TestAssemblyOptions(unittest.TestCase):
    """
    @brief Test assembler configuration options.
    """

    def test_default_options(self) -> None:
        """
        @brief Verify the default output configuration.
        """
        options = AssemblyOptions()

        self.assertTrue(options.generate_binary)
        self.assertFalse(options.generate_listing)
        self.assertFalse(options.generate_cross_reference)


    def test_optional_outputs_can_be_enabled(self) -> None:
        """
        @brief Verify that optional output products can be enabled.
        """
        options = AssemblyOptions(
            generate_binary=True,
            generate_listing=True,
            generate_cross_reference=True,
        )

        self.assertTrue(options.generate_binary)
        self.assertTrue(options.generate_listing)
        self.assertTrue(options.generate_cross_reference)


if __name__ == "__main__":
    unittest.main()
