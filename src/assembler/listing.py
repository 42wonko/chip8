"""
@file listing.py

@brief Assembly listing generation.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Sequence

from assembler.codegen import CodeGenerationRecord
from assembler.includeprocessor import SourceOrigin
from assembler.semantic import Reference
from assembler.symbol import SymbolTable
from assembler.token import SourceLocation
from chip8.isa.reference import ReferenceAccess


class ListingGenerator:
    """
    @brief Generates a textual assembler listing.
    """

    def generate( self, source: str, records: tuple[CodeGenerationRecord, ...], symbols: SymbolTable, references: tuple[Reference, ...], generate_cross_reference: bool, line_origins: Sequence[SourceOrigin] | None = None, include_path: str = "") -> str:
        """
        @brief Generate an assembly listing.

        @param source
            Expanded assembler source text.
        @param records
            Code generated for source lines.
        @param symbols
            Symbol table containing assembler symbols and references.
        @param references
            Architectural resource references.
        @param generate_cross_reference
            True to append the cross-reference section.
        @param line_origins
            Original source locations for expanded source lines.
        @param include_path
            Configured INCLUDE path, if one exists.

        @return
            Formatted assembly listing.
        """
        source_lines = source.splitlines()
        records_by_line = {record.line: record for record in records}
        lines: list[str] = []
        effective_include_path = self._determine_include_path( line_origins, include_path)
        if effective_include_path is not None:
            lines.extend(( f"INCLUDE = {effective_include_path}", ""))

        for line_number, source_line in enumerate(source_lines, start=1):
            record = records_by_line.get(line_number)
            if line_origins is None:
                origin_text = None
            elif line_number <= len(line_origins):
                origin = line_origins[line_number - 1]
                origin_text = f"{origin.filename.name}:{origin.line}"
            else:
                origin_text = None
            if origin_text is None:
                prefix = f"{line_number:4d}  "
            else:
                prefix = f"{line_number:4d}  {origin_text:<32}  "
            if record is None:
                lines.append(f"{prefix}{'':4}  {'':8}  {source_line}")
                continue
            data = " ".join(f"{value:02X}" for value in record.data)
            lines.append(
                f"{prefix}"
                f"{record.address:04X}  "
                f"{data:<8}  "
                f"{source_line}"
            )
        listing = "\n".join(lines)
        if generate_cross_reference:
            listing = self._append_cross_reference(
                listing,
                symbols,
                references
            )
        return listing

    @staticmethod
    def _format_source_location(location: SourceLocation) -> str:
        """
        @brief Format a source location for the cross-reference.
        @param location
            Source location to format.
        @return
            Original filename and line, or expanded-source line if
            original source information is unavailable.
        """
        if location.source_file is not None and location.source_line is not None:
            return f"{location.source_file.name}:{location.source_line}"
        return str(location.line)

    @staticmethod
    def _format_grouped_source_locations( locations: Sequence[SourceLocation]) -> str:
        """
        @brief Format source locations grouped by source file.

        @param locations
            Source locations to format.

        @return
            Comma-separated locations with each filename displayed once.
        """
        grouped_locations: dict[Path | None, list[str]] = {}
        for location in locations:
            source_file = location.source_file
            if source_file is not None and location.source_line is not None:
                line_number = str(location.source_line)
            else:
                source_file = None
                line_number = str(location.line)
            grouped_locations.setdefault(source_file, []).append(line_number)
        formatted_groups = []
        for source_file, line_numbers in grouped_locations.items():
            lines_text = ", ".join(line_numbers)
            if source_file is None:
                formatted_groups.append(lines_text)
            else:
                formatted_groups.append(f"{source_file.name}:{lines_text}")
        return ", ".join(formatted_groups)

    @staticmethod
    def _append_cross_reference( listing: str, symbols: SymbolTable, references: tuple[Reference, ...]) -> str:
        """
        @brief Append the cross-reference section to a listing.

        @param listing
            Existing assembly listing.
        @param symbols
            Symbol table containing assembler symbols and references.
        @param references
            Architectural resource references.
        @return
            Listing with the cross-reference section appended.
        """
        symbol_name_width = max( 12, max((len(symbol.name) for symbol in symbols.symbols), default=0))
        definitions = [ ListingGenerator._format_source_location(symbol.location) for symbol in symbols.symbols ]
        definition_width = max( 10, max((len(definition) for definition in definitions), default=0))
        lines = [
            "",
            "Cross-Reference",
            "===============",
            "",
            f"{'Name':<{symbol_name_width}}  "
            f"{'Type':<10}  "
            f"{'Access':<12}  "
            f"{'Definition':<{definition_width}}  "
            "References"
        ]
        resource_references: dict[ tuple[str, ReferenceAccess], list[SourceLocation] ] = {}
        for reference in references:
            key = (reference.name, reference.access)
            resource_references.setdefault(key, []).append(reference.location)
        for symbol, definition in zip(symbols.symbols, definitions):
            locations = symbols.references(symbol.name)
            reference_text = ListingGenerator._format_grouped_source_locations(
                locations
            )
            lines.append(
                f"{symbol.name:<{symbol_name_width}}  "
                f"{'Symbol':<10}  "
                f"{'--':<12}  "
                f"{definition:<{definition_width}}  "
                f"{reference_text}"
            )
        for (name, access), resource_locations in resource_references.items():
            reference_text = ListingGenerator._format_grouped_source_locations(
                resource_locations
            )
            lines.append(
                f"{name:<{symbol_name_width}}  "
                f"{'Resource':<10}  "
                f"{access.value:<12}  "
                f"{'--':<{definition_width}}  "
                f"{reference_text}"
            )
        return f"{listing}\n" + "\n".join(lines)

    ###########################################################################
    # Private helpers
    ###########################################################################
    @staticmethod
    def _determine_include_path( line_origins: Sequence[SourceOrigin] | None, include_path: str) -> str | None:
        """
        @brief Determine the INCLUDE path to display in the listing.
        @param line_origins
            Original source locations for expanded source lines.
        @param include_path
            Configured INCLUDE path.
        @return
            Configured INCLUDE path or inferred common parent directory.
            None if no suitable source mapping is available.
        """
        if include_path:
            return include_path
        if not line_origins:
            return None
        filenames = [origin.filename for origin in line_origins]
        if not all(filename.is_absolute() for filename in filenames):
            return None
        directories = {str(filename.parent) for filename in filenames}
        return os.path.commonpath(sorted(directories))
