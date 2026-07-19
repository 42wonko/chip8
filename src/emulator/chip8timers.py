"""
@file chip8timers.py

@brief CHIP-8 timer implementation.

@details
Implements the delay timer and sound timer of the CHIP-8 virtual
machine.

Both timers are 8-bit down counters. They are decremented by one at
every timer tick until they reach zero.

@author
Michael Dlubatz

@copyright
MIT License
"""

from __future__ import annotations

from controller.applicationlogreporter import ApplicationLogReporter
from controller.diagnostics import DiagnosticReporter
from emulator.constants import BYTE_MASK


class Chip8Timers:
    """
    @brief CHIP-8 timers.
    """

    def __init__(self, diagnostics: DiagnosticReporter, logger: ApplicationLogReporter) -> None:
        """
        @brief Construct the timer registers.
        """
        self._diagnostics       = diagnostics
        self._logger            = logger
        self._delay_timer: int  = 0
        self._sound_timer: int  = 0

    ###########################################################################
    # Delay timer
    ###########################################################################
    @property
    def delay_timer(self) -> int:
        """
        @brief Return the delay timer.
        """
        return self._delay_timer

    @delay_timer.setter
    def delay_timer(self, value: int) -> None:
        """
        @brief Set the delay timer.

        @param value
            Timer value.
        """
        self._delay_timer = value & BYTE_MASK


    ###########################################################################
    # Sound timer
    ###########################################################################
    @property
    def sound_timer(self) -> int:
        """
        @brief Return the sound timer.
        """
        return self._sound_timer


    @sound_timer.setter
    def sound_timer(self, value: int) -> None:
        """
        @brief Set the sound timer.

        @param value
            Timer value.
        """
        self._sound_timer = value & BYTE_MASK


    ###########################################################################
    # Public interface
    ###########################################################################
    def tick(self) -> None:
        """
        @brief Advance both timers by one tick.
        """
        if self._delay_timer > 0:
            self._delay_timer -= 1  # we don't have to mask because we stop at 0!

        if self._sound_timer > 0:
            self._sound_timer -= 1  # we don't have to mask because we stop at 0!


    def reset(self) -> None:
        """
        @brief Reset both timers.
        """
        self._diagnostics.info("Resetting timers")
        self._delay_timer = 0
        self._sound_timer = 0
