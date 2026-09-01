"""
@file listing.py

@brief Assembly listing generation.
"""

from __future__ import annotations

from assembler.codegen import CodeGenerationRecord


class ListingGenerator:
    """
    @brief Generates a textual assembler listing.
    """

    def generate( self, source: str, records: tuple[CodeGenerationRecord, ...]) -> str:
        """
        @brief Generate an assembly listing.

        @param source
            Original assembler source text.

        @param records
            Code generated for source lines.

        @return
            Formatted assembly listing.
        """
        source_lines = source.splitlines()
        records_by_line = { record.line: record for record in records }
        lines: list[str] = []
        for line_number, source_line in enumerate( source_lines, start=1):
            record = records_by_line.get(line_number)
            if record is None:
                lines.append( f"{line_number:4d}  {'':4}  {'':8}  {source_line}")
                continue
            data = " ".join( f"{value:02X}" for value in record.data)
            lines.append(
                f"{line_number:4d}  "
                f"{record.address:04X}  "
                f"{data:<8}  "
                f"{source_line}"
            )
        return "\n".join(lines)
