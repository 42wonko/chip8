"""
@file assemblerdialog.py

@brief Assembler window.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from PyQt6 import uic
from PyQt6.QtWidgets import QDialog, QFileDialog, QListWidgetItem, QMessageBox, QWidget

from assembler.assembler import Assembler
from assembler.options import AssemblyOptions
from assembler.target import Target
from controller.diagnostic import format_severity, format_source
from controller.diagnostics import AssemblerDiagnostics

if TYPE_CHECKING:
    from controller.controller import Chip8Controller

class AssemblerDialog(QDialog):
    """
    @brief Main window of the assembler.
    """

    def __init__( self, controller: Chip8Controller, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._controller = controller
        self._source_file: Path | None = None
        ui_file = Path(__file__).resolve().parent / "ui" / "assemblerdialog.ui"
        uic.loadUi(str(ui_file), self)
        self._initialize()
        self._assembler: Assembler | None = None
        self._diagnostics: AssemblerDiagnostics | None = None


    def set_assembler(self, assembler: Assembler) -> None:
        """
        @brief Set the assembler used by the dialog.
        """
        self._assembler = assembler


    def set_diagnostics(self, diagnostics: AssemblerDiagnostics) -> None:
        """
        @brief Set the diagnostics collection displayed by the dialog.
        """
        self._diagnostics = diagnostics

    ###########################################################################
    # Public interface
    ###########################################################################
    @property
    def source_file(self) -> Path | None:
        """
        @brief Return the currently loaded source file.
        """
        return self._source_file


    ###########################################################################
    # Private helpers
    ###########################################################################
    def _initialize(self) -> None:
        """
        @brief Initialize assembler dialog controls.
        """
        self.asmAssemblePushButton.clicked.connect(self._assemble)
        self.asmRunPushButton.clicked.connect(self._run)
        self.asmSavePushButton.clicked.connect(self._save)
        self.asmLoadPushButton.clicked.connect(self._load)
        self.asmOutputSaveCheckBox.setChecked(False)


    def _selected_target(self) -> Target | None:
        """
        @brief Return the target selected by the user.

        @return
            Selected target or None when no target was selected.
        """
        index = self.asmTargetComboBox.currentIndex()
        if index == 0:
            return None
        if index == 1:
            return Target.COSMAC
        return None


    def _options(self) -> AssemblyOptions:
        """
        @brief Build assembler options from the dialog controls.
        """
        cross_reference = self.asmOutputSaveCheckBox.isChecked()
        listing = self.asmOutputListingCheckBox.isChecked() or cross_reference
        return AssemblyOptions( generate_listing=listing, generate_cross_reference=cross_reference)


    def _ensure_source_file(self) -> bool:
        """
        @brief Ensure that the current source has a filename.

        @return
            True if a source filename is available.
        """
        if self._source_file is not None:
            return True
        return self._save()


    def _save(self) -> bool:
        """
        @brief Save the current source code to disk.

        @return
            True if the source was saved successfully.
        """
        if self._source_file is None:
            filename, _ = QFileDialog.getSaveFileName( self, "Save Assembly Source", "", "CHIP-8 Assembly (*.asm *.s);;All files (*)")
            if not filename:
                return False
            self._source_file = Path(filename)
        try:
            self._source_file.write_text( self.asmSourceCodeTextEdit.toPlainText(), encoding="utf-8")
        except OSError as error:
            QMessageBox.critical( self, "Save Assembly Source", f"Unable to save '{self._source_file}': {error}")
            return False
        return True


    def _load(self) -> None:
        """
        @brief Load an assembly source file from disk.
        """
        filename, _ = QFileDialog.getOpenFileName( self, "Open Assembly Source", "", "CHIP-8 Assembly (*.asm *.s);;All files (*)")
        if not filename:
            return
        path = Path(filename)
        try:
            source = path.read_text(encoding="utf-8")
        except OSError as error:
            QMessageBox.critical( self, "Load Assembly Source", f"Unable to load '{path}': {error}")
            return
        self._source_file = path
        self.asmSourceCodeTextEdit.setPlainText(source)
        self._clear_diagnostics()

    def _assemble(self) -> None:
        """
        @brief Save and assemble the current source.
        """
        if not self._ensure_source_file():
            return
        self._controller.assemble_source( self._source_file, self._selected_target(), self._options())
        self._display_diagnostics()

    def _run(self) -> None:
        """
        @brief Save, assemble and run the current source.
        """
        if not self._ensure_source_file():
            return
        success = self._controller.assemble_source( self._source_file, self._selected_target(), self._options())
        self._display_diagnostics()
        if success:
            self._controller.run_assembled_source(self._source_file)

    def _clear_diagnostics(self) -> None:
        """
        @brief Clear the assembler diagnostics view.
        """
        self.asmDiagnosticsListWidget.clear()

    def _display_diagnostics(self) -> None:
        """
        @brief Display assembler diagnostics.
        """
        self._clear_diagnostics()

        for diagnostic in self._controller.assembler_diagnostics:
            address = "---"
            if diagnostic.address is not None:
                address = f"{diagnostic.address:03X}"
            text = (
                f"{format_severity(diagnostic.severity):<3} "
                f"{format_source(diagnostic.source):<8} "
                f"{address} "
                f"{diagnostic.message}"
            )
            if diagnostic.count > 1:
                text += f" (x{diagnostic.count})"
            self.asmDiagnosticsListWidget.addItem( QListWidgetItem(text))
