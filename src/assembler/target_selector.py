"""
@file target_selector.py

@brief Target architecture discovery and selection.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from assembler.includeprocessor import SourceOrigin
from assembler.target import Target


@dataclass(frozen=True, slots=True)
class TargetSelection:
    """
    @brief Result of target architecture selection.
    """

    target: Target
    from_source: bool


class TargetSelectionError(ValueError):
    """
    @brief Raised when target architecture selection fails.
    """




class TargetSelector:
    """
    @brief Discovers and selects the target architecture for an assembly.
    """

    TARGET_KEYWORD = "TARGET"


    def select( self, source: str, external_target: Target | None, line_origins: Sequence[SourceOrigin] | None = None) -> TargetSelection:
        """
        @brief Select the effective target architecture.

        A target declared in the source takes precedence over the externally
        supplied target. At most one TARGET directive is permitted.

        @param source
            Assembly source code.

        @param external_target
            Target supplied externally, or None if no external target exists.

        @param line_origins
            Contains lineinformation in the current file and the original source file.

        @return
            The selected target and its source.

        @exception TargetSelectionError
            If the source contains an invalid or multiple target directives
            or if no target can be selected.
        """
        source_target = self._discover(source, line_origins)
        if source_target is not None:
            return TargetSelection(target=source_target, from_source=True)
        if external_target is not None:
            return TargetSelection(target=external_target, from_source=False)
        raise TargetSelectionError("No target architecture was specified.")


    def _discover(self, source: str, line_origins: Sequence[SourceOrigin] | None = None) -> Target | None:
        """
        @brief Discover a target directive in the source.

        This method performs only the architecture-independent processing
        required to find TARGET declarations. It does not parse assembly
        instructions or operands.

        @param source
            Assembly source code.

        @param line_origins
            Contains lineinformation in the current file and the original source file.

        @return
            The source-selected target, or None if no TARGET directive
            exists.

        @exception TargetSelectionError
            If the source contains an invalid or multiple TARGET directives.
        """
        discovered_target: Target | None = None
        discovered_location: SourceOrigin | None = None
        discovered_line: int | None = None
        for line_number, line in enumerate(source.splitlines(), start=1):
            content = self._remove_comment(line).strip()
            if not content:
                continue
            parts = content.split()
            if not parts or parts[0].upper() != self.TARGET_KEYWORD:
                continue
            location = self._source_origin(line_number, line_origins)
            if len(parts) != 2:
                raise TargetSelectionError( f"Invalid TARGET directive at {self._format_location(line_number, location)}.")
            target = self._parse_target(parts[1], line_number, location)
            if discovered_target is not None:
                first_location = self._format_location(discovered_line or 0, discovered_location)
                second_location = self._format_location(line_number, location)
                raise TargetSelectionError(
                    "Multiple TARGET directives found. "
                    f"The first declaration is at {first_location}; "
                    f"the second declaration is at {second_location}."
                )
            discovered_target = target
            discovered_location = location
            discovered_line = line_number
        return discovered_target


    @staticmethod
    def _source_origin( line_number: int, line_origins: Sequence[SourceOrigin] | None) -> SourceOrigin | None:
        if line_origins is None or line_number > len(line_origins):
            return None
        return line_origins[line_number - 1]


    @staticmethod
    def _format_location(line_number: int, location: SourceOrigin | None) -> str:
        if location is not None:
            return f"{location.filename}:{location.line}"
        return f"line {line_number}"


    @staticmethod
    def _remove_comment(line: str) -> str:
        """
        @brief Remove an assembler comment from a source line.

        @param line
            Source line.

        @return
            Source line without its comment.
        """
        comment_index = line.find(";")
        if comment_index < 0:
            return line
        return line[:comment_index]


    @staticmethod
    def _parse_target(value: str, line_number: int, location: SourceOrigin | None = None) -> Target:
        """
        @brief Convert a target name into a Target value.

        @param value
            Target name from the TARGET directive.

        @param line_number
            Source line containing the directive.

        @param location
            Contains lineinformation in the current file and the original source file.

        @return
            Corresponding target.

        @exception TargetSelectionError
            If the target is not supported.
        """
        normalized = value.upper().replace("_", "").replace("-", "")
        aliases = {
            "COSMAC": Target.COSMAC,
            "COSMACVIP": Target.COSMAC,
            "SUPERCHIP10": Target.SUPERCHIP_10,
            "SCHIP10": Target.SUPERCHIP_10,
            "SUPERCHIP1.0": Target.SUPERCHIP_10,
            "SUPERCHIP11": Target.SUPERCHIP_11,
            "SCHIP11": Target.SUPERCHIP_11,
            "SUPERCHIP1.1": Target.SUPERCHIP_11,
            "SUPERCHIPMODERN": Target.SUPERCHIP_MODERN,
            "SCHIPMODERN": Target.SUPERCHIP_MODERN,
            "SCHIPC": Target.SCHIPC,
        }
        target = aliases.get(normalized)
        if target is not None:
            return target

        formatted_location = TargetSelector._format_location(line_number, location)
        raise TargetSelectionError(f"Unknown target '{value}' at {formatted_location}.")
