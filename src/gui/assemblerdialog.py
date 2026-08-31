"""
@file assemblerdialog.py

@brief Assembler window.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from PyQt6 import uic
from PyQt6.QtWidgets import QDialog, QWidget

from assembler.assembler import Assembler
from assembler.options import AssemblyOptions
from assembler.target import Target
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
        self.asmSaveAsPushButton.clicked.connect(self._save_as)
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
        source = self.asmSourceCodeTextEdit.toPlainText()
        return self._controller.ensure_assembler_source_file(source)


    def _save(self) -> bool:
        """
        @brief Save the current source code.
        """
        source = self.asmSourceCodeTextEdit.toPlainText()
        return self._controller.save_assembler_source(source)


    def _save_as(self) -> bool:
        """
        @brief Save the current assembler source under a new filename.
        """
        return self._controller.save_assembler_source_as( self.asmSourceCodeTextEdit.toPlainText())


    def _load(self) -> None:
        """
        @brief Load an assembly source file.
        """
        source = self._controller.load_assembler_source()
        if source is None:
            return
        self.asmSourceCodeTextEdit.setPlainText(source)
#        self._clear_diagnostics()


    def _assemble(self) -> None:
        """
        @brief Save and assemble the current source.
        """
        if not self._ensure_source_file():
            return
        self._controller.assemble_source( self.asmSourceCodeTextEdit.toPlainText(), self._selected_target(), self._options())
        self._display_diagnostics()


    def _run(self) -> None:
        """
        @brief Save, assemble and run the current source.
        """
        source = self.asmSourceCodeTextEdit.toPlainText()
        if not self._controller.ensure_assembler_source_file(source):
            return
        success = self._controller.assemble_source( source, self._selected_target(), self._options())
        self._display_diagnostics()
        if success:
            self._controller.run_assembled_source()


    def _clear_diagnostics(self) -> None:
        """
        @brief Clear the assembler diagnostics view.
        """
        self.asmDiagnosticsListWidget.clear()


    def _display_diagnostics(self) -> None:
        """
        @brief Display assembler diagnostics.
        """
        self.asmDiagnosticsListWidget.clear()

        if self._diagnostics is None:
            return

        for diagnostic in self._diagnostics:
            text = diagnostic.message

            if diagnostic.location is not None:
                text = f"ERR  line {diagnostic.location.line}: {text}"

            self.asmDiagnosticsListWidget.addItem(text)


