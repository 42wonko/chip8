"""
@file symbol.py

@brief Symbol table support for the assembler.
"""

from __future__ import annotations

from dataclasses import dataclass

from assembler.token import SourceLocation


@dataclass(frozen=True, slots=True)
class Symbol:
    """
    @brief A named assembler symbol.
    """
    name: str
    value: int
    location: SourceLocation


class SymbolTable:
    """
    @brief Stores symbols defined during assembler semantic analysis.
    """
    def __init__(self) -> None:
        self._symbols: dict[str, Symbol] = {}
        self._references: dict[str, list[SourceLocation]] = {}


    def define( self, name: str, value: int, location: SourceLocation) -> None:
        """
        @brief Define a symbol.

        @exception ValueError
            If the symbol has already been defined.
        """
        canonical_name = self._canonical_name(name)
        if canonical_name in self._symbols:
            raise ValueError(f"Symbol '{name}' is already defined.")
        self._symbols[canonical_name] = Symbol( name=name, value=value, location=location)


    def lookup(self, name: str) -> Symbol:
        """
        @brief Look up a symbol.

        @return
            The corresponding symbol.

        @exception ValueError
            If the symbol does not exist.
        """
        canonical_name = self._canonical_name(name)
        try:
            return self._symbols[canonical_name]
        except KeyError as error:
            raise ValueError( f"Undefined symbol '{name}'.") from error


    def contains(self, name: str) -> bool:
        """
        @brief Determine whether a symbol exists.
        """
        return self._canonical_name(name) in self._symbols


    def add_reference(self, name: str, location: SourceLocation) -> None:
        """
        @brief Record a reference to a defined symbol.

        @exception ValueError
            If the symbol does not exist.
        """
        canonical_name = self._canonical_name(name)
        if canonical_name not in self._symbols:
            raise ValueError(f"Undefined symbol '{name}'.")
        self._references.setdefault(canonical_name, []).append(location)


    def references(self, name: str) -> tuple[SourceLocation, ...]:
        """
        @brief Return all references to a symbol.
        """
        canonical_name = self._canonical_name(name)
        if canonical_name not in self._symbols:
            raise ValueError(f"Undefined symbol '{name}'.")
        return tuple(self._references.get(canonical_name, []))


    def clear(self) -> None:
        """
        @brief Remove all symbols.
        """
        self._symbols.clear()


###############################################################################
# private helpers
###############################################################################
    @staticmethod
    def _canonical_name(name: str) -> str:
        """
        @brief Return the canonical representation of a symbol name.
        """
        return name.upper()


    def __len__(self) -> int:
        """
        @brief Return the number of defined symbols.
        """
        return len(self._symbols)
