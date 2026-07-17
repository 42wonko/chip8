"""
@file logging.py

@brief Application logging and CHIP-8 execution tracing.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum, auto

from controller.applicationlogreporter import ApplicationLogReporter
from controller.bufferedfilesink import BufferedFileSink
from controller.diagnostic import DiagnosticSource, format_source
from controller.emulatorconfiguration import EmulatorConfiguration, TraceLevel
from controller.executiontracereporter import ExecutionTraceReporter
from emulator.tracerecord import TraceRecord


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
        self._trace_level = TraceLevel.BASIC


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


    def set_level(self, trace_level: TraceLevel) -> None:
        self._trace_level = trace_level


    def trace(self, record: TraceRecord) -> None:
        """
        @brief Write one execution trace record.
        """
        if not self._enabled:
            return

        before = record.registers_before
        after = record.registers_after
        # BASIC
        line = (
            f"{record.cycle:06d} "
            f"{record.registers_before.pc:03X} "
            f"{record.instruction.opcode:04X} "
            f"{record.instruction}"
        )

        if self._trace_level == TraceLevel.CHANGES:                     # CHANGES
            line += "\n"

            if before.pc != after.pc:                                   # Registers
                line += ( f"       | PC: 0x{before.pc:03X} -> 0x{after.pc:03X}")

            if before.i != after.i:
                line += ( f" | I: 0x{before.i:03X} -> 0x{after.i:03X}")

            if before.sp != after.sp:
                line += ( f" | SP: 0x{before.sp:X} -> 0x{after.sp:X}")

            if record.delay_timer_before != record.delay_timer_after:
                line += ( f" | DT: 0x{record.delay_timer_before:02X} -> 0x{record.delay_timer_after:02X}")

            if record.sound_timer_before != record.sound_timer_after:
                line += ( f" | ST: 0x{record.sound_timer_before:02X} -> 0x{record.sound_timer_after:02X}")

            for reg in range(16):
                old = before.read_register(reg)
                new = after.read_register(reg)

                if old != new:
                    line += ( f" | V{reg:X}: 0x{old:02X} -> 0x{new:02X}")

            if record.memory_range is not None:                         # Memory
                start, end = record.memory_range
                if start == end:
                    line += f" | MEM: 0x{start:03X} UPDATED"
                else:
                    line += ( f" | MEM: 0x{start:03X} -> 0x{end:03X} UPDATED")

            if record.display_changed:                                  # Display
                line += " | DISPLAY UPDATED"

        if self._trace_level == TraceLevel.FULL:
            line += ( f"\n       PC: 0x{before.pc:03X} -> 0x{after.pc:03X}")
            line += ( f" | I: 0x{before.i:03X} -> 0x{after.i:03X}")
            line += ( f" | SP: 0x{before.sp:X} -> 0x{after.sp:X}")
            line += ( f" | DT: 0x{record.delay_timer_before:02X} -> 0x{record.delay_timer_after:02X}")
            line += ( f" | ST: 0x{record.sound_timer_before:02X} -> 0x{record.sound_timer_after:02X}")
            line += "\n       " + " ".join( f"V{i:X}=0x{record.registers_after.read_register(i):02X}" for i in range(8))
            line += "\n       " + " ".join( f"V{i:X}=0x{record.registers_after.read_register(i):02X}" for i in range(8,16))
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
        self._tracer.set_level(configuration.trace_level)

        if configuration.execution_trace_enabled:
            self._tracer.enable()
        else:
            self._tracer.disable()


    def application_logger( self, source: DiagnosticSource) -> ApplicationLogReporter:
        """
        @brief Return an application log reporter.
        """
        return self._logger.reporter(source)


    def execution_trace_reporter(self) -> ExecutionTraceReporter:
        """
        @brief Return the execution tracer.
        """
        return self._tracer.reporter()


