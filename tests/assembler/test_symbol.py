"""
@file test_symbol.py

@brief Tests for the assembler symbol table.
"""

import unittest

from assembler.symbol import SymbolTable
from assembler.token import SourceLocation


class SymbolTableTest(unittest.TestCase):
    """
    @brief Tests for SymbolTable.
    """

    def setUp(self) -> None:
        self.location = SourceLocation(
            line=1,
            column=1
        )
        self.symbols = SymbolTable()


    def test_new_table_is_empty(self) -> None:
        self.assertEqual(len(self.symbols), 0)


    def test_define_symbol(self) -> None:
        self.symbols.define(
            "START",
            0x200,
            self.location
        )

        self.assertTrue(self.symbols.contains("START"))
        self.assertEqual(
            self.symbols.lookup("START").value,
            0x200
        )


    def test_lookup_returns_symbol_name(self) -> None:
        self.symbols.define(
            "START",
            0x200,
            self.location
        )

        self.assertEqual(
            self.symbols.lookup("START").name,
            "START"
        )


    def test_lookup_returns_symbol_location(self) -> None:
        self.symbols.define(
            "START",
            0x200,
            self.location
        )

        self.assertEqual(
            self.symbols.lookup("START").location,
            self.location
        )


    def test_lookup_undefined_symbol_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.symbols.lookup("MISSING")


    def test_duplicate_symbol_raises(self) -> None:
        self.symbols.define(
            "START",
            0x200,
            self.location
        )

        with self.assertRaises(ValueError):
            self.symbols.define(
                "START",
                0x300,
                self.location
            )


    def test_contains_returns_false_for_unknown_symbol(self) -> None:
        self.assertFalse(
            self.symbols.contains("MISSING")
        )


    def test_clear_removes_symbols(self) -> None:
        self.symbols.define(
            "START",
            0x200,
            self.location
        )

        self.symbols.clear()

        self.assertEqual(len(self.symbols), 0)
        self.assertFalse(
            self.symbols.contains("START")
        )
