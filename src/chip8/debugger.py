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

from PyQt6.QtCore import QSettings


class Debugger:
    """
    @brief Debugger class handling breakpoints.
    """

    def __init__(self) -> None:
        self._active_breakpoints: set[int]      = set()
        self._inactive_breakpoints: set[int]    = set()
        self._temporary_breakpoint: int | None  = None
        self._enabled: bool                     = True


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


    def enable_breakpoint(self, address: int) -> None:
        """
        @brief Enable an existing breakpoint.

        @param address
            Breakpoint address.
        """
        if address in self._inactive_breakpoints:
            self._inactive_breakpoints.remove(address)
            self._active_breakpoints.add(address)


    def disable_breakpoint(self, address: int) -> None:
        """
        @brief Disable an existing breakpoint.

        @param address
            Breakpoint address.
        """
        if address in self._active_breakpoints:
            self._active_breakpoints.remove(address)
            self._inactive_breakpoints.add(address)


    def clear_breakpoint(self, address: int) -> None:
        """
        @brief Delete one breakpoint from active or inactive list.
        @param address Address of the breakpoint to be deleted.
        """
        self._active_breakpoints.discard(address)
        self._inactive_breakpoints.discard(address)


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


    def has_breakpoint(self, address: int) -> bool:
        """
        @brief Check if address is associated with a breakpoint.
        @details Walks through the list of active braekpoints and returns True if address is in it.
        @param address
            Address that is to be checked against the breakpoints.
        @return True if address is in the list of active breakpoints.
        """
        return address in self._active_breakpoints


    def has_breakpoints(self) -> bool:
        """
        @brief Check whether any breakpoint exists.

        @return
            True if at least one breakpoint exists.
        """
        return ( bool(self._active_breakpoints) or bool(self._inactive_breakpoints))


    def has_any_breakpoint(self, address: int) -> bool:
        if self._enabled:
            if self._temporary_breakpoint is not None and self._temporary_breakpoint == address:
                self._temporary_breakpoint = None
                return True

            return self.has_breakpoint(address)
        else:
            return False


    def is_breakpoint_enabled(self, address: int) -> bool:
        return address in self._active_breakpoints


    def is_breakpoint_disabled(self, address: int) -> bool:
        return address in self._inactive_breakpoints


    def enable(self, enable:bool) -> None:
        """
        @brief Enable or disable the debugger.
        """
        self._enabled = enable


    @property
    def temporary_breakpoint(self) -> int | None:
        """
        @brief Return the current temporary breakpoint.

        @return
            Temporary breakpoint address or None.
        """
        return self._temporary_breakpoint


    def active_breakpoints(self) -> set[int]:
        """
        @brief Return all active breakpoints.
        @return Copy of the active breakpoint set.
        """
        return self._active_breakpoints.copy()


    def inactive_breakpoints(self) -> set[int]:
        """
        @brief Return all inactive breakpoints.
        @return Copy of the inactive breakpoint set.
        """
        return self._inactive_breakpoints.copy()


    def read_settings(self, settings: QSettings) -> None:
        """
        @brief Read debugger settings.
        @param settings Persistent application settings.
        """
        self.clear_all_breakpoints()
        self._enabled = settings.value( "debugger/enabled", True, type=bool)
        active = settings.value( "debugger/active_breakpoints", [])
        inactive = settings.value( "debugger/inactive_breakpoints", [])
        if active is not None:
            self._active_breakpoints = {int(address) for address in active}
        if inactive is not None:
            self._inactive_breakpoints = {int(address) for address in inactive}


    def write_settings(self, settings: QSettings) -> None:
        """
        @brief Write debugger settings.
        @param settings Persistent application settings.
        """
        settings.setValue( "debugger/enabled", self._enabled)
        settings.setValue( "debugger/active_breakpoints", sorted(self._active_breakpoints))
        settings.setValue( "debugger/inactive_breakpoints", sorted(self._inactive_breakpoints))

