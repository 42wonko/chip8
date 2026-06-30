"""
@file controller.py

@brief Application controller.

@details
The controller coordinates the GUI and the emulator core.

Responsibilities
----------------
- Create application objects.
- Coordinate GUI and emulator.
- Handle user actions.

Non-responsibilities
--------------------
- Execute CHIP-8 instructions.
- Store hardware state.
- Render graphics.

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


    def show_main_window(self) -> None:
        """
        @brief Show the main window.
        """

        self._main_window.show()

