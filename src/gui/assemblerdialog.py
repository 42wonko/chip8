"""
@file assemblerdialog.py

@brief Assembler window.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from PyQt6 import uic
from PyQt6.QtCore import QEvent, QObject, Qt
from PyQt6.QtGui import QKeyEvent, QTextCursor
from PyQt6.QtWidgets import QApplication, QDialog, QListWidgetItem, QMessageBox, QWidget

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
        self.asmNewPushButton.clicked.connect(self._new)
        self.asmViGroupBox.toggled.connect( self.asmSourceCodeTextEdit.set_vi_mode_enabled)
        self.asmViTabSizeComboBox.currentTextChanged.connect( self._vi_tab_size_changed)
        self.asmViFontComboBox.currentFontChanged.connect( self.asmSourceCodeTextEdit.set_editor_font)
        self.asmSourceCodeTextEdit.set_vi_mode_enabled( self.asmViGroupBox.isChecked())
        self._vi_tab_size_changed(self.asmViTabSizeComboBox.currentText())
        self.asmSourceCodeTextEdit.set_editor_font( self.asmViFontComboBox.currentFont())
        self.asmOutputSaveCheckBox.toggled.connect(self._cross_reference_toggled)
        self.asmOutputSaveCheckBox.setChecked(False)
        self.asmDiagnosticsListWidget.installEventFilter(self)
        self.asmDiagnosticsListWidget.itemActivated.connect( self._diagnostic_activated)
        self.asmDiagnosticsListWidget.itemDoubleClicked.connect( self._diagnostic_activated)
        self.asmSourceCodeTextEdit.document().modificationChanged.connect( self._source_modified_changed)
        self._update_title()

    def _vi_tab_size_changed(self, text: str) -> None:
        """
        @brief Update the assembler editor tab size.
        """
        try:
            tab_size = int(text)
        except ValueError:
            return
        if tab_size <= 0:
            return
        self.asmSourceCodeTextEdit.set_tab_size(tab_size)

    def _cross_reference_toggled(self, checked: bool) -> None:
        """
        @brief Enable listing generation when cross-reference generation is selected.
        """
        if checked:
            self.asmOutputListingCheckBox.setChecked(True)

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

    def _save(self) -> bool:
        """
        @brief Save the current source code.
        """
        source = self.asmSourceCodeTextEdit.toPlainText()
        if not self._controller.save_assembler_source(source):
            return False
        self.asmSourceCodeTextEdit.document().setModified(False)
        self._update_title()
        return True

    def _save_as(self) -> bool:
        """
        @brief Save the current assembler source under a new filename.
        """
        if not self._controller.save_assembler_source_as( self.asmSourceCodeTextEdit.toPlainText()):
            return False
        self.asmSourceCodeTextEdit.document().setModified(False)
        self._update_title()
        return True

    def _load(self) -> None:
        """
        @brief Load an assembly source file.
        """
        source = self._controller.load_assembler_source()
        if source is None:
            return
        self.asmSourceCodeTextEdit.setPlainText(source)
        self.asmSourceCodeTextEdit.document().setModified(False)
        self._update_title()

    def _new(self) -> None:
        """
        @brief Start a new assembler source project.
        """
        document = self.asmSourceCodeTextEdit.document()

        if document.isModified():
            result = QMessageBox.question(
                self,
                "New Assembly Source",
                "The assembly source has been modified.\n\n"
                "Do you want to save the changes before starting a new source?",
                QMessageBox.StandardButton.Save
                | QMessageBox.StandardButton.Discard
                | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Save,
            )

            if result == QMessageBox.StandardButton.Cancel:
                return
            if result == QMessageBox.StandardButton.Save:
                if not self._save():
                    return
        self._controller.assembler_new()
        self.asmSourceCodeTextEdit.clear()
        document.setModified(False)
        self._update_title()

    def _source_modified_changed(self, modified: bool) -> None:
        """
        @brief Update the assembler dialog title when the source is modified.
        """
        del modified
        self._update_title()


    def _update_title(self) -> None:
        """
        @brief Update the assembler dialog title.
        """
        source_file = self._controller.assembler_source_file
        name = source_file.name if source_file is not None else "Untitled"
        if self.asmSourceCodeTextEdit.document().isModified():
            name += "*"
        self.setWindowTitle(f"Assembler - {name}")

    def _assemble(self) -> None:
        """
        @brief Save and assemble the current source.
        """
#        if not self._ensure_source_file():
#            return
        self._controller.assemble_source( self.asmSourceCodeTextEdit.toPlainText(), self._selected_target(), self._options())
        self._display_diagnostics()


    def _run(self) -> None:
        """
        @brief Save, assemble and run the current source.
        """
        source = self.asmSourceCodeTextEdit.toPlainText()
#        if not self._controller.ensure_assembler_source_file(source):
#            return
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
        for index, diagnostic in enumerate(self._diagnostics):
            text = diagnostic.message
            if diagnostic.location is not None:
                text = f"ERR  line {diagnostic.location.line}: {text}"
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, index)
            self.asmDiagnosticsListWidget.addItem(item)

    def _diagnostic_activated(self, item: QListWidgetItem) -> None:
        """
        @brief Move the source editor to an activated diagnostic.
        """
        if self._diagnostics is None:
            return
        diagnostic_index = item.data(Qt.ItemDataRole.UserRole)
        if not isinstance(diagnostic_index, int):
            return
        if not 0 <= diagnostic_index < len(self._diagnostics):
            return
        diagnostic = self._diagnostics[diagnostic_index]
        if diagnostic.location is None:
            return
        line = diagnostic.location.line
        column = diagnostic.location.column
        if line <= 0 or column <= 0:
            return
        block = self.asmSourceCodeTextEdit.document().findBlockByNumber(line - 1)
        if not block.isValid():
            return
        cursor = QTextCursor(block)
        cursor.movePosition(
            QTextCursor.MoveOperation.Right,
            QTextCursor.MoveMode.MoveAnchor,
            min(column - 1, max(0, block.length() - 1))
        )
        cursor.select(QTextCursor.SelectionType.WordUnderCursor)
        self.asmSourceCodeTextEdit.setTextCursor(cursor)
        self.asmSourceCodeTextEdit.setFocus()
        self.asmSourceCodeTextEdit.ensureCursorVisible()

    def eventFilter(self, watched: QObject | None, event: QEvent | None) -> bool:
        """
        @brief Handle keyboard events for the assembler dialog controls.
        """
        if watched is self.asmDiagnosticsListWidget and event is not None:
            if event.type() == QEvent.Type.KeyPress:
                key_event = event
                if isinstance(key_event, QKeyEvent):
                    if ( key_event.key() == Qt.Key.Key_C and key_event.modifiers() & Qt.KeyboardModifier.ControlModifier):
                        self._copy_selected_diagnostics()
                        return True
        return super().eventFilter(watched, event)

    def _copy_selected_diagnostics(self) -> None:
        """
        @brief Copy the selected assembler diagnostics to the clipboard.
        """
        selected_items = self.asmDiagnosticsListWidget.selectedItems()
        if not selected_items:
            return
        text = "\n".join(item.text() for item in selected_items)
        clipboard = QApplication.clipboard()
        if clipboard is None:
            return
        clipboard.setText(text)

