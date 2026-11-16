"""
@file includeprocessor.py

@brief Architecture-independent expansion of assembler INCLUDE directives.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class SourceOrigin:
    """Original source location corresponding to an expanded source line."""

    filename: Path
    line: int


@dataclass(frozen=True, slots=True)
class ExpandedSource:
    """Expanded source text and its original per-line locations."""

    source: str
    line_origins: tuple[SourceOrigin, ...]


class IncludeError(ValueError):
    """Raised when an INCLUDE directive cannot be expanded."""

    def __init__(self, message: str, filename: Path, line: int) -> None:
        super().__init__(f"{filename}:{line}: {message}")
        self.filename = filename
        self.line = line


class IncludeProcessor:
    """Expand INCLUDE directives without depending on an assembler ISA."""

    _DIRECTIVE_PATTERN = re.compile(r"^\s*INCLUDE\b(.*)$", re.IGNORECASE)
    _FILENAME_PATTERN = re.compile(r'^\s*"([^"\r\n]+)"\s*(?:;.*)?$')

    def __init__(self, include_path: str = "") -> None:
        self._include_path = include_path

    @classmethod
    def has_include_directives(cls, source: str) -> bool:
        """
        @brief Check whether source contains an INCLUDE directive.
        @param source
            Assembly source text.
        @return
            True if at least one line starts with an INCLUDE directive.
        """
        return any(
            cls._DIRECTIVE_PATTERN.match(line.rstrip("\r\n")) is not None
            for line in source.splitlines(keepends=True)
        )

    def expand(self, source: str, main_source_file: Path) -> ExpandedSource:
        """Expand source recursively, using the main file as the path anchor."""
        main_file = main_source_file.expanduser().resolve()
        configured_path = Path(self._include_path).expanduser() if self._include_path else None
        if configured_path is not None and not configured_path.is_absolute():
            configured_path = main_file.parent / configured_path
        if configured_path is not None:
            configured_path = configured_path.resolve()

        expanded_lines: list[str] = []
        origins: list[SourceOrigin] = []
        self._expand_text(
            source=source,
            source_file=main_file,
            configured_path=configured_path,
            active_files=(main_file,),
            expanded_lines=expanded_lines,
            origins=origins
        )
        return ExpandedSource("".join(expanded_lines), tuple(origins))

    def _expand_text(
        self,
        source: str,
        source_file: Path,
        configured_path: Path | None,
        active_files: tuple[Path, ...],
        expanded_lines: list[str],
        origins: list[SourceOrigin]
    ) -> None:
        for line_number, line in enumerate(source.splitlines(keepends=True), start=1):
            directive = self._DIRECTIVE_PATTERN.match(line.rstrip("\r\n"))
            if directive is None:
                expanded_lines.append(line)
                origins.append(SourceOrigin(source_file, line_number))
                continue

            include_name = self._parse_filename(directive.group(1), source_file, line_number)
            include_file = self._resolve_include(include_name, source_file, configured_path)
            if include_file in active_files:
                chain = " -> ".join(str(path) for path in (*active_files, include_file))
                raise IncludeError(f"Circular INCLUDE detected: {chain}", source_file, line_number)

            try:
                included_source = include_file.read_text(encoding="utf-8")
            except (OSError, UnicodeError) as error:
                raise IncludeError(
                    f"Unable to read included file '{include_file}': {error}",
                    source_file,
                    line_number
                ) from error

            before_count = len(expanded_lines)
            self._expand_text(
                source=included_source,
                source_file=include_file,
                configured_path=configured_path,
                active_files=(*active_files, include_file),
                expanded_lines=expanded_lines,
                origins=origins
            )

            has_parent_newline = line.endswith(("\n", "\r"))
            if has_parent_newline:
                newline = "\r\n" if line.endswith("\r\n") else "\n"
                if len(expanded_lines) == before_count:
                    expanded_lines.append(newline)
                    origins.append(SourceOrigin(source_file, line_number))
                elif not expanded_lines[-1].endswith(("\n", "\r")):
                    expanded_lines[-1] += newline

    @classmethod
    def _parse_filename(cls, value: str, source_file: Path, line_number: int) -> str:
        match = cls._FILENAME_PATTERN.fullmatch(value)
        if match is None:
            raise IncludeError(
                'Invalid INCLUDE directive. Expected INCLUDE "filename".',
                source_file,
                line_number
            )
        return match.group(1)

    @staticmethod
    def _resolve_include(
        include_name: str,
        source_file: Path,
        configured_path: Path | None
    ) -> Path:
        include_file = Path(include_name).expanduser()
        if include_file.is_absolute():
            return include_file.resolve()
        base_path = configured_path if configured_path is not None else source_file.parent
        return (base_path / include_file).resolve()
