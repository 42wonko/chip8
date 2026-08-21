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


    def define( self, name: str, value: int, location: SourceLocation) -> None:
        """
        @brief Define a symbol.

        @exception ValueError
            If the symbol has already been defined.
        """
        if name in self._symbols:
            raise ValueError( f"Symbol '{name}' is already defined.")
        self._symbols[name] = Symbol( name=name, value=value, location=location)


    def lookup(self, name: str) -> Symbol:
        """
        @brief Look up a symbol.

        @return
            The corresponding symbol.

        @exception ValueError
            If the symbol does not exist.
        """
        try:
            return self._symbols[name]
        except KeyError as error:
            raise ValueError( f"Undefined symbol '{name}'.") from error


    def contains(self, name: str) -> bool:
        """
        @brief Determine whether a symbol exists.
        """
        return name in self._symbols


    def clear(self) -> None:
        """
        @brief Remove all symbols.
        """
        self._symbols.clear()


    def __len__(self) -> int:
        """
        @brief Return the number of defined symbols.
        """
        return len(self._symbols)
