"""
@file listing.py

@brief Assembly listing generation.
"""

from __future__ import annotations

from assembler.codegen import CodeGenerationRecord
from assembler.semantic import Reference
from assembler.symbol import SymbolTable
from chip8.isa.reference import ReferenceAccess


class ListingGenerator:
    """
    @brief Generates a textual assembler listing.
    """


    def generate( self, source: str, records: tuple[CodeGenerationRecord, ...], symbols: SymbolTable, references: tuple[Reference, ...], generate_cross_reference: bool) -> str:
        """
        @brief Generate an assembly listing.

        @param source
            Original assembler source text.

        @param records
            Code generated for source lines.

        @param symbols
            Symbol table containing assembler symbols and references.

        @param references
            Architectural resource references.

        @param generate_cross_reference
            True to append the cross-reference section.

        @return
            Formatted assembly listing.
        """
        source_lines = source.splitlines()
        records_by_line = {record.line: record for record in records}
        lines: list[str] = []
        for line_number, source_line in enumerate(source_lines, start=1):
            record = records_by_line.get(line_number)
            if record is None:
                lines.append( f"{line_number:4d}  {'':4}  {'':8}  {source_line}")
                continue
            data = " ".join(f"{value:02X}" for value in record.data)
            lines.append(
                f"{line_number:4d}  "
                f"{record.address:04X}  "
                f"{data:<8}  "
                f"{source_line}"
            )
        listing = "\n".join(lines)
        if generate_cross_reference:
            listing = self._append_cross_reference( listing, symbols, references)
        return listing


    @staticmethod
    def _append_cross_reference( listing: str, symbols: SymbolTable, references: tuple[Reference, ...]) -> str:
        """
        @brief Append the cross-reference section to a listing.
        """
        lines = [
            "",
            "Cross-Reference",
            "===============",
            "",
            f"{'Name':<12}  {'Type':<10}  {'Access':<12}  {'Definition':<10}  References"
        ]
        resource_references: dict[tuple[str, ReferenceAccess], list[int]] = {}
        for reference in references:
            key = (reference.name, reference.access)
            resource_references.setdefault(key, []).append(reference.location.line)

        for symbol in symbols.symbols:
            locations = symbols.references(symbol.name)
            reference_text = ", ".join( str(location.line) for location in locations)
            lines.append(
                f"{symbol.name:<12}  "
                f"{'Symbol':<10}  "
                f"{'--':<12}  "
                f"{symbol.location.line:<10}  "
                f"{reference_text}"
            )

        for (name, access), resource_locations in resource_references.items():
            reference_text = ", ".join(str(line) for line in resource_locations)
            lines.append(
                f"{name:<12}  "
                f"{'Resource':<10}  "
                f"{access.value:<12}  "
                f"{'--':<10}  "
                f"{reference_text}"
            )
        return f"{listing}\n" + "\n".join(lines)


