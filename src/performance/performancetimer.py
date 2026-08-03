"""
@file performancetimer.py
@brief Simple performance timer for profiling emulator execution.

@author
Michael Dlubatz

@copyright
MIT License
"""

from __future__ import annotations

import time


class PerformanceTimer:
    """
    @brief Collect timing statistics for named code sections.
    """

    def __init__(self) -> None:
        self._start: dict[str, float] = {}
        self._total: dict[str, float] = {}
        self._maximum: dict[str, float] = {}
        self._count: dict[str, int] = {}


    def start(self, name: str) -> None:
        """
        @brief Start timing a named section.
        """
        self._start[name] = time.perf_counter()


    def stop(self, name: str) -> None:
        """
        @brief Stop timing a named section.
        """
        start = self._start.pop(name, None)
        if start is None:
            return

        elapsed = time.perf_counter() - start

        self._total[name] = self._total.get(name, 0.0) + elapsed
        self._count[name] = self._count.get(name, 0) + 1

        current_max = self._maximum.get(name, 0.0)
        if elapsed > current_max:
            self._maximum[name] = elapsed


    def report(self) -> None:
        """
        @brief Print a timing report.
        """
        print()
        print("===========================================================")
        print("Performance Report")
        print("===========================================================")
        print(f"{'Section':30} {'Calls':>10} {'Avg [ms]':>12} {'Max [ms]':>12} {'Total [ms]':>12}")
        print("-----------------------------------------------------------")

        for name in sorted(self._total):
            total = self._total[name]
            count = self._count[name]
            maximum = self._maximum[name]
            average = total / count

            print(
                f"{name:30}"
                f"{count:10d}"
                f"{average * 1000:12.3f}"
                f"{maximum * 1000:12.3f}"
                f"{total * 1000:12.3f}"
            )

        print("===========================================================")


    def clear(self) -> None:
        """
        @brief Reset all collected statistics.
        """
        self._start.clear()
        self._total.clear()
        self._maximum.clear()
        self._count.clear()
