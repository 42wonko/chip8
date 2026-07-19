"""
@file executiontracereporter.py

@brief Implementation of the reporter for CHIP8 instruction tracing.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from controller.logging import ExecutionTracer

from emulator.tracerecord import KeyExecutionEvent, TraceRecord


class ExecutionTraceReporter:

    def __init__(self, tracer: ExecutionTracer) -> None:
        self._tracer = tracer


    def trace(self, record: TraceRecord) -> None:
        self._tracer.trace_instruction(record)


    def trace_key_event(self, cycle: int, event: KeyExecutionEvent, key: int) -> None:
        self._tracer.trace_key_event(cycle, event, key)


