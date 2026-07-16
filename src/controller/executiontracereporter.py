"""
@file executiontracereporter.py

@brief Implementation of the reporter for CHIP8 instruction tracing.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from controller.logging import ExecutionTracer

from emulator.tracerecord import TraceRecord


class ExecutionTraceReporter:

    def __init__(self, tracer: ExecutionTracer) -> None:
        self._tracer = tracer

    def trace(self, record: TraceRecord) -> None:
        self._tracer.trace(record)
