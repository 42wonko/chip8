"""
@file applicationlogreporter.py

@brief Source-specific application log reporter.
"""

from __future__ import annotations

from controller.diagnostic import DiagnosticSource


class ApplicationLogReporter:
    """
    @brief Application log reporter for one subsystem.
    """

    def __init__( self, logger: "ApplicationLogger", source: DiagnosticSource) -> None:
        self._logger = logger
        self._source = source


    def info(self, message: str) -> None:
        """
        @brief Write an informational message.
        """
        self._logger.info(self._source, message)


    def warning(self, message: str) -> None:
        """
        @brief Write a warning message.
        """
        self._logger.warning(self._source, message)


    def error(self, message: str) -> None:
        """
        @brief Write an error message.
        """
        self._logger.error(self._source, message)


    def enter(self, function: str) -> None:
        """
        @brief Record function entry.
        """
        self._logger.enter(self._source, function)


    def leave(self, function: str) -> None:
        """
        @brief Record function exit.
        """
        self._logger.leave(self._source, function)
