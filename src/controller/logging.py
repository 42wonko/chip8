"""
@file logging.py

@brief Application logging and CHIP-8 execution tracing.
"""

from __future__ import annotations
from enum import Enum, auto
from pathlib import Path
from datetime import datetime
from controller.bufferedfilesink import BufferedFileSink
from controller.emulatorconfiguration import EmulatorConfiguration
from controller.applicationlogreporter import ApplicationLogReporter
from controller.executiontracereporter import ExecutionTraceReporter
from controller.diagnostic import DiagnosticSource, format_source

class LogSeverity(Enum):
    """
    @brief Severity of an application log message.
    """

    INFO = auto()
    WARNING = auto()
    ERROR = auto()


class ApplicationLogger:
    """
    @brief Application log writer.

    @details
    Records application events, warnings, errors and optional function
    tracing.
    """

    def __init__(self) -> None:
        self._enabled = False
        self._sink = BufferedFileSink()
        self._filename = ""
        self._function_trace_enabled = False


    def enable(self) -> None:
        """
        @brief Enable logging.
        """
        if self._enabled:
            return
        self._enabled = True
        if self._filename:
            self._sink.open(self._filename)


    def disable(self) -> None:
        """
        @brief Disable logging.
        """
        if not self._enabled:
            return
        self._enabled = False
        self._sink.close()


    def set_filename(self, filename: str) -> None:
        """
        @brief Set the log file.
        """
        self._filename = filename
        if self._enabled:
            self._sink.open(filename)


    def reporter( self, source: DiagnosticSource) -> ApplicationLogReporter:
        """
        @brief Return a reporter for one subsystem.
        """
        return ApplicationLogReporter(self, source)


    def enable_function_trace(self, enabled: bool) -> None:
        """
        @brief Enable or disable function tracing.
        """
        self._function_trace_enabled = enabled


    def info(self, source: DiagnosticSource, message: str) -> None:
        """
        @brief Write an informational message.
        """
        self._write(LogSeverity.INFO, source, message) 


    def warning(self, source: DiagnosticSource, message: str) -> None:
        """
        @brief Write a warning message.
        """
        self._write(LogSeverity.WARNING, source, message)


    def error(self, source: DiagnosticSource, message: str) -> None:
        """
        @brief Write an error message.
        """
        self._write(LogSeverity.ERROR, source, message)


    def enter(self, source: DiagnosticSource, function: str) -> None:
        """
        @brief Record function entry.
        """
        if self._function_trace_enabled:
            self.info(source, f">>> {function}")


    def leave(self, source: DiagnosticSource, function: str) -> None:
        """
        @brief Record function exit.
        """
        if self._function_trace_enabled:
            self.info(source, f"<<< {function}")


    ###########################################################################
    # private helpers
    ###########################################################################
    def _write(self, severity: LogSeverity, source: DiagnosticSource, message: str) -> None:
        """
        @brief Write one log record.
        """
        if not self._enabled:
            return
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._sink.write( f"{timestamp} [{severity.name}] {format_source(source):>10} {message}")




class ExecutionTracer:
    """
    @brief CHIP-8 execution trace writer.
    """

    def __init__(self) -> None:
        self._enabled = False
        self._sink = BufferedFileSink()
        self._filename = ""
        self._cycle = 0


    def enable(self) -> None:
        """
        @brief Enable execution tracing.
        """
        if self._enabled:
            return
        self._enabled = True
        if self._filename:
            self._sink.open(self._filename)


    def disable(self) -> None:
        """
        @brief Disable execution tracing.
        """
        if not self._enabled:
            return
        self._enabled = False
        self._sink.close()


    def set_filename(self, filename: str) -> None:
        """
        @brief Set the trace output file.
        """
        self._filename = filename
        if self._enabled:
            self._sink.open(filename)


    def trace(self, record: TraceRecord) -> None:
        """
        @brief Write one execution trace record.
        """
        if not self._enabled:
            return
        self._cycle += 1
        line = (
            f"{self._cycle:06d} "
            f"{record.pc_before:03X} "
            f"{record.instruction.opcode:04X} "
            f"{record.instruction}"
        )
        self._sink.write(line)


    def reporter(self) -> ExecutionTraceReporter:
        return ExecutionTraceReporter(self)



class LogManager:
    """
    @brief Owns the application logger and execution tracer.
    """

    def __init__(self) -> None:
        self._logger = ApplicationLogger()
        self._tracer = ExecutionTracer()


    def configure(self, configuration: EmulatorConfiguration) -> None:
        """
        @brief Configure the logging subsystem.
        """

        # Application logging
        self._logger.set_filename(configuration.log_filename)
        self._logger.enable_function_trace(configuration.function_trace_enabled)
        if configuration.logging_enabled:
            self._logger.enable()
        else:
            self._logger.disable()

        # CHIP-8 execution trace
        self._tracer.set_filename(configuration.trace_filename)

        if configuration.execution_trace_enabled:
            self._tracer.enable()
        else:
            self._tracer.disable()


    def application_logger( self, source: DiagnosticSource) -> ApplicationLogReporter:
        """
        @brief Return an application log reporter.
        """
        return self._logger.reporter(source)


    def execution_tracer(self) -> ExecutionTracer:
        """
        @brief Return the execution tracer.
        """
        return self._tracer.reporter()


