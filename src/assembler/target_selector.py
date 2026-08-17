"""
@file target_selector.py

@brief Target architecture discovery and selection.
"""

from __future__ import annotations

from dataclasses import dataclass

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


    def select( self, source: str, external_target: Target | None) -> TargetSelection:
        """
        @brief Select the effective target architecture.

        A target declared in the source takes precedence over the externally
        supplied target.

        @param source
            Assembly source code.

        @param external_target
            Target supplied externally, or None if no external target exists.

        @return
            The selected target and its source.

        @exception TargetSelectionError
            If the source contains an invalid or multiple target directives
            or if no target can be selected.
        """
        source_target = self._discover(source)
        if source_target is not None:
            return TargetSelection(target=source_target, from_source=True)
        if external_target is not None:
            return TargetSelection(target=external_target, from_source=False)
        raise TargetSelectionError("No target architecture was specified.")


    def _discover(self, source: str) -> Target | None:
        """
        @brief Discover a target directive in the source.

        This method performs only the architecture-independent processing
        required to find TARGET declarations. It does not parse assembly
        instructions or operands.

        @param source
            Assembly source code.

        @return
            The source-selected target, or None if no TARGET directive
            exists.

        @exception TargetSelectionError
            If the source contains an invalid or multiple TARGET directives.
        """
        discovered_target: Target | None = None

        for line_number, line in enumerate(source.splitlines(), start=1):
            content = self._remove_comment(line).strip()
            if not content:
                continue
            parts = content.split()
            if not parts or parts[0].upper() != self.TARGET_KEYWORD:
                continue
            if len(parts) != 2:
                raise TargetSelectionError(f"Invalid TARGET directive on line {line_number}.")
            target = self._parse_target(parts[1], line_number)
            if discovered_target is not None:
                raise TargetSelectionError( "Multiple TARGET directives found.")
            discovered_target = target
        return discovered_target


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
    def _parse_target(value: str, line_number: int) -> Target:
        """
        @brief Convert a target name into a Target value.

        @param value
            Target name from the TARGET directive.

        @param line_number
            Source line containing the directive.

        @return
            Corresponding target.

        @exception TargetSelectionError
            If the target is not supported.
        """
        normalized = value.upper()

        for target in Target:
            if target.value.upper() == normalized:
                return target

        raise TargetSelectionError( f"Unknown target '{value}' on line {line_number}.")

