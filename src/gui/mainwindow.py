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
from typing import TYPE_CHECKING, cast

from PyQt6 import uic
from PyQt6.QtGui import QFontDatabase, QKeyEvent
from PyQt6.QtWidgets import QHeaderView, QMainWindow, QStatusBar

from gui.displaywidget import DisplayWidget

if TYPE_CHECKING:
    from controller.controller import Chip8Controller
    from gui.memorytablemodel import MemoryTableModel

class MainWindow(QMainWindow):
    """
    @brief Main application window.
    """
#    if TYPE_CHECKING:
#        displayWidget: DisplayWidget
#        statusbar: QStatusBar

    def __init__(self, controller: Chip8Controller) -> None:
        """
        @brief Construct the main window.

        @param controller
            Application controller.
        """
        super().__init__()
        self._controller = controller
        ui_file = ( Path(__file__).parent / "ui" / "mainwindow.ui")
        uic.loadUi(str(ui_file), self)
        self._initialize()

    ###########################################################################
    # Public interface
    ###########################################################################
    @property
    def display(self) -> DisplayWidget:
        """
        @brief Return the display widget.
        """
        return cast(DisplayWidget, self.displayWidget) # type: ignore[attr-defined]


    def show_status_message(self, message: str) -> None:
        """
        @brief Display a message in the status bar.

        @param message
            Message to display.
        """
        cast(QStatusBar, self.statusbar).showMessage(message) # type: ignore[attr-defined]


    def set_rom_title(self, rom: Path | None) -> None:
        """
        @brief Update the window title.

        @param rom
            Currently loaded ROM or None.
        """
        title = "CHIP-8 Emulator"
        if rom is not None:
            title += f" - {rom.name}"
        self.setWindowTitle(title)

    def set_memory_model( self, model: MemoryTableModel) -> None:
        """
        @brief Attach the memory model to the memory table.
        """
        self.memoryTableView.setModel(model)
        header = self.memoryTableView.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode( QHeaderView.ResizeMode.ResizeToContents)
        self.memoryTableView.verticalHeader().setSectionResizeMode( QHeaderView.ResizeMode.ResizeToContents)
        font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        self.memoryTableView.setFont(font)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        self._controller.key_down(event.key())


    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        self._controller.key_up(event.key())


    ###########################################################################
    # Private helpers
    ###########################################################################
    def _initialize(self) -> None:
        """
        @brief Perform application specific initialization.

        @details
        This method is called after the Qt Designer UI has been loaded.
        """

        self._connect_signals()
        self.show_status_message("Ready")
        self._register_labels = [ self.V0_Label, self.V1_Label, self.V2_Label, self.V3_Label,
        self.V4_Label, self.V5_Label, self.V6_Label, self.V7_Label, self.V8_Label, self.V9_Label,
        self.VA_Label, self.VB_Label, self.VC_Label, self.VD_Label, self.VE_Label, self.VF_Label, ]

    @property
    def register_labels(self) -> list:
        return self._register_labels

    def _connect_signals(self) -> None:
        """
        @brief Connect all GUI signals.

        @details
        All widget signal connections are collected here to keep the
        constructor concise.
        """

        self.loadButton.clicked.connect(self._controller.load_rom)                  # type: ignore[attr-defined]

        self.runButton.clicked.connect(self._controller.run)                        # type: ignore[attr-defined]
        self.continueButton.clicked.connect(self._controller.run)                   # type: ignore[attr-defined]

        self.stopExecutionButton.clicked.connect(self._controller.stop)             # type: ignore[attr-defined]
        self.resetButton.clicked.connect(self._controller.reset)                    # type: ignore[attr-defined]
        self.singleStepButton.clicked.connect(self._controller.step)                # type: ignore[attr-defined]
        self.keyboardButton.clicked.connect( self._controller.configure_keyboard)   # type: ignore[attr-defined]
