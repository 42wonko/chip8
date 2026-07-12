from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum, auto


class DiagnosticSeverity(StrEnum):
    """
    @brief Severity of a diagnostic message.
    """

    INFO = auto()
    WARNING = auto()
    ERROR = auto()


class DiagnosticSource(StrEnum):
    """
    @brief Originating subsystem.
    """

    ANALYZER = auto()
    CONTROLLER = auto()
    EMULATOR = auto()
    AUDIO = auto()
    GUI = auto()


def format_severity(severity: DiagnosticSeverity) -> str:
    """
    @brief Return the abbreviated severity.

    @param severity
        Diagnostic severity.

    @return
        Three-character abbreviation.
    """
    match severity:
        case DiagnosticSeverity.INFO:
            return "INF"
        case DiagnosticSeverity.WARNING:
            return "WRN"
        case DiagnosticSeverity.ERROR:
            return "ERR"
    raise AssertionError("Unhandled diagnostic severity.")


def format_source(source: DiagnosticSource) -> str:
    """
    @brief Return the abbreviated source.

    @param source
        Diagnostic source.

    @return
        Fixed-width source abbreviation.
    """
    match source:
        case DiagnosticSource.ANALYZER:
            return "ANALYZR"
        case DiagnosticSource.CONTROLLER:
            return "CONTROL"
        case DiagnosticSource.EMULATOR:
            return "EMULATR"
        case DiagnosticSource.AUDIO:
            return "AUDIO"
        case DiagnosticSource.GUI:
            return "GUI"
    raise AssertionError("Unhandled diagnostic source.")


@dataclass(slots=True)
class Diagnostic:
    """
    @brief One diagnostic message.

    @details
    Diagnostics are collected by the controller and displayed in the
    diagnostics list of the main window.

    Equal diagnostics are coalesced by the Diagnostics manager and the
    occurrence counter is increased.
    """

    severity: DiagnosticSeverity
    source: DiagnosticSource
    message: str
    address: int | None = None
    count: int = 1

