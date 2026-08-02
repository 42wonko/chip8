"""
@file debugger.py
@brief Debugger for the Chip8 emulator.
@details
This class handles all functions related to breakpoints. It maintains a list of permanent
breakpoints and a temporary breakpoint. Functions like "run to cursor" or "step over sub-routine call" 
use temporary breakpoints but rely on the ssame infrastucture than normal breakpoints.

@author
Michael Dlubatz

@copyright
MIT License
"""

from __future__ import annotations


class Debugger:
    """
    @brief Debugger class handling breakpoints.
    """

    def __init__(self) -> None:
        self._active_breakpoints: set[int]      = set()
        self._inactive_breakpoints: set[int]    = set()
        self._temporary_breakpoint: int | None  = None


    def toggle_breakpoint(self, address: int) -> None:
        if address in self._active_breakpoints:
            self._inactive_breakpoints.add(address)
            self._active_breakpoints.discard(address)
        elif address in self._inactive_breakpoints:
            self._active_breakpoints.add(address)
            self._inactive_breakpoints.discard(address)
        else:
            self.set_breakpoint(address)


    def set_breakpoint(self, address: int) -> None:
        """
        @brief Enable a breakpoint.

        @param address
            Breakpoint address.
        """
        self._inactive_breakpoints.discard(address)
        self._active_breakpoints.add(address)


    def clear_breakpoint(self, address: int) -> None:
        if address in self._active_breakpoints:
            self._active_breakpoints.discard(address)
        if address in self._inactive_breakpoints:
            self._inactive_breakpoints.discard(address)


    def has_breakpoint(self, address: int) -> bool:
        """
        @brief Check if address is associated with a breakpoint.
        @details Walks through the list of active braekpoints and returns True if address is in it.
        @param address
            Address that is to be checked against the breakpoints.
        @return True if address is in the list of active breakpoints.
        """
        return address in self._active_breakpoints


    def clear_all_breakpoints(self) -> None:
        self._active_breakpoints.clear()
        self._inactive_breakpoints.clear()
        self._temporary_breakpoint = None


    def set_temporary_breakpoint(self, address: int) -> None:
        """
        @brief Set a temporary breakpoint.
        @details Only one temporary brakpoint is needed. It is used for implementing functions
        like "run to cursor" or "step over function call". It is implicitely set and reset by 
        these unctions.
        @param address Breakpoint address.
        """
        self._temporary_breakpoint = address


    def clear_temporary_breakpoint(self) -> None:
        self._temporary_breakpoint = None


    def has_any_breakpoint(self, address: int) -> bool:
        if self._temporary_breakpoint is not None and self._temporary_breakpoint == address:
            self._temporary_breakpoint = None
            return True

        return self.has_breakpoint(address)


    def is_breakpoint_enabled(self, address: int) -> bool:
        return address in self._active_breakpoints


    def is_breakpoint_disabled(self, address: int) -> bool:
        return address in self._inactive_breakpoints
