from __future__ import annotations

from collections.abc import Iterator

from controller.diagnostic import Diagnostic, DiagnosticSeverity, DiagnosticSource


class DiagnosticReporter:
    """
    @brief Reports diagnostics for one subsystem.

    @details
    A DiagnosticReporter is bound to a fixed DiagnosticSource. Subsystems
    receive only a reporter and therefore cannot modify or inspect the
    complete diagnostics collection.
    """

    def __init__( self , diagnostics: "Diagnostics" , source: DiagnosticSource) -> None:
        """
        @brief Construct a reporter.

        @param diagnostics
            Owning diagnostics collection.

        @param source
            Fixed source of all reported diagnostics.
        """
        self._diagnostics = diagnostics
        self._source = source


    def info( self , message: str , address: int | None = None) -> None:
        """
        @brief Report an informational message.
        """
        self._diagnostics._report( DiagnosticSeverity.INFO , self._source , message , address)


    def warning( self , message: str , address: int | None = None) -> None:
        """
        @brief Report a warning.
        """
        self._diagnostics._report( DiagnosticSeverity.WARNING , self._source , message , address)


    def error( self , message: str , address: int | None = None) -> None:
        """
        @brief Report an error.
        """
        self._diagnostics._report( DiagnosticSeverity.ERROR , self._source , message , address)


class Diagnostics:
    """
    @brief Collection of emulator diagnostics.
    """

    def __init__(self) -> None:
        """
        @brief Construct an empty diagnostics collection.
        """
        self._diagnostics: list[Diagnostic] = []
        self._lookup: dict[ tuple[ DiagnosticSeverity , DiagnosticSource , str , int | None ] , Diagnostic ] = {}


    def clear(self) -> None:
        """
        @brief Remove all diagnostics.
        """
        self._diagnostics.clear()
        self._lookup.clear()


    def reporter( self , source: DiagnosticSource) -> DiagnosticReporter:
        """
        @brief Create a reporter for one subsystem.
        """
        return DiagnosticReporter(self, source)

    @property
    def empty(self) -> bool:
        """
        @brief Return whether the collection is empty.
        """
        return not self._diagnostics


    def __len__(self) -> int:
        """
        @brief Return the number of distinct diagnostics.
        """
        return len(self._diagnostics)


    def __iter__(self) -> Iterator[Diagnostic]:
        """
        @brief Iterate over all diagnostics.
        """
        return iter(self._diagnostics)


    def __getitem__( self , index: int) -> Diagnostic:
        """
        @brief Return one diagnostic (implements the [] operator).
        """
        return self._diagnostics[index]


    def _report( self , severity: DiagnosticSeverity , source: DiagnosticSource , message: str , address: int | None) -> None:
        """
        @brief Insert or update a diagnostic.
        """
        key = ( severity , source , message , address)
        diagnostic = self._lookup.get(key)
        if diagnostic is not None:  # we keep a reference count in case the message occurs multiple times
            diagnostic.count += 1
            return
        diagnostic = Diagnostic( severity=severity , source=source , message=message , address=address)
        self._lookup[key] = diagnostic          ## add a new entry
        self._diagnostics.append(diagnostic)
