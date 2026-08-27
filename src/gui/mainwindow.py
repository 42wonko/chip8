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
from PyQt6.QtCore import QModelIndex, QPoint, QSettings, Qt, pyqtSignal
from PyQt6.QtGui import QFontDatabase, QKeyEvent
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QHeaderView,
    QMainWindow,
    QMessageBox,
    QStatusBar,
)

from chip8.settingsmanager import SettingsManager
from gui.assemblerdialog import AssemblerDialog
from gui.codetablemodel import CodeTableModel
from gui.configdialog import ConfigDialog
from gui.displaywidget import DisplayWidget

if TYPE_CHECKING:
    from controller.controller import Chip8Controller
    from gui.memorytablemodel import MemoryTableModel

class MainWindow(QMainWindow):
    """
    @brief Main application window.
    """

    breakpoint_toggled = pyqtSignal(int)    # handle enabling/disabling breakpoints
    breakpoint_context_menu_requested = pyqtSignal(int, QPoint)


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
        self._config_dialog     = ConfigDialog(self)
        self._assembler_dialog  = AssemblerDialog(self._controller, self)
        flags = self._assembler_dialog.windowFlags() | Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowTitleHint | Qt.WindowType.WindowMaximizeButtonHint
        self._assembler_dialog.setWindowFlags(flags)

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
        font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        self.memoryTableView.setFont(font)
        model.scroll_to_address.connect( self._scroll_memory_to_address)
        header = self.memoryTableView.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode( QHeaderView.ResizeMode.Interactive)
        vertical = self.memoryTableView.verticalHeader()
        vertical.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.memoryTableView.resizeColumnsToContents()
        self.memoryTableView.resizeRowsToContents()


    def set_code_model(self, model: CodeTableModel) -> None:
        """
        @brief Attach the code model to the code table.
        """
        self._code_model = model
        self.codeTableView.setModel(model)
        self.codeTableView.verticalHeader().hide()
        header = self.codeTableView.horizontalHeader()
        header.setStretchLastSection(True)
#        header.setSectionResizeMode( QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode( QHeaderView.ResizeMode.Interactive)
        self.codeTableView.resizeColumnsToContents()
        self.codeTableView.verticalHeader().setSectionResizeMode( QHeaderView.ResizeMode.Fixed)
        font = QFontDatabase.systemFont( QFontDatabase.SystemFont.FixedFont)
        self.codeTableView.setFont(font)
        self.codeTableView.setSelectionBehavior( QAbstractItemView.SelectionBehavior.SelectRows)
        self.codeTableView.setSelectionMode( QAbstractItemView.SelectionMode.SingleSelection)


    def keyPressEvent(self, event: QKeyEvent | None) -> None:
        if event is None:
            return None
        self._controller.key_down(event.key())


    def keyReleaseEvent(self, event: QKeyEvent | None) -> None:
        if event is None:
            return None
        self._controller.key_up(event.key())


    def scroll_code_to_row(self, row: int) -> None:
        """
        @brief Scroll the code view to the specified row.

        @param row
            Row index to make visible.
        """
        model = self.codeTableView.model()
        if model is None:
            return
        index = model.index(row, 0)
        if not index.isValid():
            return
        if self.codeTableView.viewport().rect().contains( self.codeTableView.visualRect(index)):
            return
        self.codeTableView.scrollTo( index, QAbstractItemView.ScrollHint.PositionAtCenter)


    def restore_settings(self) -> None:
        """
        @brief Restore the persistent window state.
        """
        settings = QSettings( SettingsManager.ORGANIZATION, SettingsManager.APPLICATION)
        geometry = settings.value("mainwindow/geometry")
        if geometry is not None:
            self.restoreGeometry(geometry)
        state = settings.value("mainwindow/state")
        if state is not None:
            self.restoreState(state)


    def save_settings(self) -> None:
        """
        @brief Save the persistent window state.
        """
        settings = QSettings( SettingsManager.ORGANIZATION, SettingsManager.APPLICATION)
        settings.setValue( "mainwindow/geometry", self.saveGeometry())
        settings.setValue( "mainwindow/state", self.saveState())


    def show_warning(self, title: str, text: str) -> None:
        """
        @brief Display a warning message.
        @param title
            Dialog title.
        @param text
            Warning message.
        """
        QMessageBox.warning(self, title, text)


    def selected_code_address(self) -> int | None:
        """
        @brief Return the currently selected CHIP-8 address.
        @return
            Selected address or None if no instruction is selected.
        """
        model = self.codeTableView.model()
        if model is None:
            return None
        index = self.codeTableView.currentIndex()
        if not index.isValid():
            return None
        model = self.codeTableView.model()
        assert isinstance(model, CodeTableModel)
        return model.address(index.row())


    def clear_code_selection(self) -> None:
        """
        @brief Clear the current code selection.
        """
        self.codeTableView.clearSelection()


    ###########################################################################
    # Private helpers
    ###########################################################################
    def _initialize(self) -> None:
        """
        @brief Perform application specific initialization.

        @details
        This method is called after the Qt Designer UI has been loaded.
        """

        self.clockFreqSlider.setValue(self._controller.cpu_frequency)
        self.clockFreqLabel.setText(f"{self._controller.cpu_frequency} Hz")
        self._connect_signals()
        self.show_status_message("Ready")
        self._register_labels = [ self.V0_Label, self.V1_Label, self.V2_Label, self.V3_Label,
        self.V4_Label, self.V5_Label, self.V6_Label, self.V7_Label, self.V8_Label, self.V9_Label,
        self.VA_Label, self.VB_Label, self.VC_Label, self.VD_Label, self.VE_Label, self.VF_Label, ]


    def _update_clock_frequency_label(self, value: int) -> None:
        self.clockFreqLabel.setText(f"{value} Hz")


    def _scroll_memory_to_address(self, address: int) -> None:
        """
        @brief Scroll the memory view so that an address becomes visible.
        """
        row = address // 16
        index = self.memoryTableView.model().index(row, 0)
        self.memoryTableView.scrollTo( index, QAbstractItemView.ScrollHint.PositionAtCenter,)


    def _code_table_double_clicked(self, index: QModelIndex) -> None:
        """
        @brief Handle double-clicks in the code view.

        Double-clicking the breakpoint column toggles the breakpoint at the
        corresponding CHIP-8 address.

        @param index
            Clicked table index.
        """
        if index.column() != CodeTableModel.Column.BP:
            return
        if self._code_model is None:
            return
        address = self._code_model.address_at_row(index.row())
        if address is not None:
            self.breakpoint_toggled.emit(address)


    def _code_table_context_menu(self, position: QPoint) -> None:
        """
        @brief Show the breakpoint context menu.

        @param position
            Mouse position in viewport coordinates.
        """
        index = self.codeTableView.indexAt(position)
        if not index.isValid():
            return
        if index.column() != CodeTableModel.Column.BP:
            return
        self.breakpoint_context_menu_requested.emit(index.row(), position)


    def configure(self) -> int:
        """
        @brief Show the configuration dialog.

        @return
            True if the user pressed OK.
        """
        return self._config_dialog.exec() == QDialog.DialogCode.Accepted


    def assemble(self) -> int:
        """
        @brief Open the Assembler Window/dialog
        .
        """
        return self._assembler_dialog.exec() == QDialog.DialogCode.Accepted


    @property
    def register_labels(self) -> list:
        return self._register_labels


    @property
    def config_dialog(self) -> ConfigDialog:
        return self._config_dialog

    @property
    def assembler_dialog(self) -> AssemblerDialog:
        return self._assembler_dialog

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

        self.clockFreqSlider.valueChanged.connect(self._controller.set_cpu_frequency)
        self.clockFreqSlider.valueChanged.connect(self._update_clock_frequency_label)

        self.stopExecutionButton.clicked.connect(self._controller.stop)             # type: ignore[attr-defined]
        self.resetButton.clicked.connect(self._controller.reset)                    # type: ignore[attr-defined]
        self.singleStepButton.clicked.connect(self._controller.step)                # type: ignore[attr-defined]

        self.keyboardButton.clicked.connect( self._controller.configure_keyboard)   # type: ignore[attr-defined]
        self.configButton.clicked.connect(self._controller.configure)               # type: ignore[attr-defined]
        self.assemblerPushButton.clicked.connect(self._controller.assembler)

        self.codeTableView.doubleClicked.connect(self._code_table_double_clicked)
        self.codeTableView.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.codeTableView.customContextMenuRequested.connect( self._code_table_context_menu)

        self.dbgStepInPushButton.clicked.connect(self._controller.step)
        self.dbgRunToAddressPushButton.clicked.connect( self._controller.run_to_address)
        self.debuggerControlGroupBox.toggled.connect(self._controller.debugger.enable)
        self.dbgStepOverPushButton.clicked.connect( self._controller.step_over)
        self.dbgStepOutPushButton.clicked.connect( self._controller.step_out)
