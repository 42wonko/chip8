"""
@file mainwindow.py

@brief Main application window.

@details
This module contains the MainWindow class which implements the
primary user interface of the CHIP-8 emulator.

The visual layout is defined in a Qt Designer .ui file which is
loaded dynamically at runtime.

Responsibilities
----------------
- Display the application window.
- Connect GUI actions to the controller.
- Update widgets after every emulator instruction.

Non-responsibilities
--------------------
- Execute emulator logic.
- Decode instructions.
- Access hardware directly.

@author
Michael Dlubatz

@copyright
MIT License
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow

if TYPE_CHECKING:
    from controller.controller import Chip8Controller


class MainWindow(QMainWindow):
    """
    @brief Main application window.
    """

    def __init__(self, controller: Chip8Controller) -> None:
        """
        @brief Construct the main window.

        @param controller
            Application controller.
        """

        super().__init__()
        self._controller = controller
        ui_file = (
            Path(__file__).parent
            / "ui"
            / "mainwindow.ui"
        )
        uic.loadUi(str(ui_file), self)
        self._initialize()

    def _initialize(self) -> None:
        """
        @brief Perform application specific initialization.

        @details
        This method is called after the Qt Designer UI has been loaded.
        """

        self._connect_signals()
        self.statusbar.showMessage("Ready")  # type: ignore[attr-defined]


    def _connect_signals(self) -> None:
        """
        @brief Connect all GUI signals.

        @details
        All QAction and widget signal connections are collected here to keep the constructor concise.
        """
        pass

