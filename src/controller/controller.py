"""
@file controller.py

@brief Application controller.

@details
The Chip8Controller coordinates the graphical user interface and the
emulator core. It is the only component that is allowed to communicate
with both.

Responsibilities
----------------
- Create and own the GUI.
- Create and own the emulator.
- Handle user commands.
- Keep the GUI synchronized with the emulator.

Non-responsibilities
--------------------
- Execute CHIP-8 instructions.
- Store hardware state.
- Decode instructions.

@author
Michael Dlubatz

@copyright
MIT License
"""

from __future__ import annotations

from gui.mainwindow import MainWindow


class Chip8Controller:
    """
    @brief Central application controller.
    """

    def __init__(self) -> None:
        """
        @brief Construct the controller.
        """

        self._main_window = MainWindow(self)
        # Will be created in a later milestone.
        self._emulator = None
        self._running = False

    ###########################################################################
    # Window handling
    ###########################################################################
    def show_main_window(self) -> None:
        """
        @brief Show the main application window.
        """

        self._main_window.show()

    ###########################################################################
    # File operations
    ###########################################################################
    def load_rom(self) -> None:
        """
        @brief Load a CHIP-8 ROM.
        """

        pass

    def reload_rom(self) -> None:
        """
        @brief Reload the currently loaded ROM.
        """

        pass

    ###########################################################################
    # Emulator control
    ###########################################################################
    def run(self) -> None:
        """
        @brief Start continuous execution.
        """

        pass

    def pause(self) -> None:
        """
        @brief Pause execution.
        """

        pass

    def stop(self) -> None:
        """
        @brief Stop execution.
        """

        pass

    def reset(self) -> None:
        """
        @brief Reset the virtual machine.
        """

        pass

    def step(self) -> None:
        """
        @brief Execute exactly one CHIP-8 instruction.
        """

        pass

    ###########################################################################
    # GUI synchronization
    ###########################################################################
    def update_gui(self) -> None:
        """
        @brief Refresh all GUI widgets.

        @details
        Called after every executed CHIP-8 instruction.
        """

        pass
