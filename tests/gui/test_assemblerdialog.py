"""
@file test_assemblerdialog.py

@brief Tests for the assembler dialog.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from PyQt6.QtCore import QEvent, Qt
from PyQt6.QtGui import QKeyEvent, QTextCursor
from PyQt6.QtWidgets import QApplication, QMessageBox

from assembler.assembler import Assembler
from assembler.result import AssemblyResult
from assembler.target import Target
from assembler.token import SourceLocation
from controller.controller import Chip8Controller
from controller.diagnostics import AssemblerDiagnostics
from gui.assemblerdialog import AssemblerDialog


class TestAssemblerDialog(unittest.TestCase):
    """
    @brief Tests for AssemblerDialog.
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        @brief Create the Qt application required by the dialog tests.
        """
        cls._application = QApplication.instance()
        if cls._application is None:
            cls._application = QApplication([])


    def setUp(self) -> None:
        self.controller = Mock(spec=Chip8Controller)
        self.controller.assembler_source_file = None
        self.dialog = AssemblerDialog(self.controller)


    def tearDown(self) -> None:
        self.dialog.close()
        self.dialog.deleteLater()


    def test_set_assembler(self) -> None:
        """
        @brief Verify that set_assembler() stores the assembler.
        """
        assembler = Mock(spec=Assembler)
        self.dialog.set_assembler(assembler)
        self.assertIs(self.dialog._assembler, assembler)


    def test_set_diagnostics(self) -> None:
        """
        @brief Verify that set_diagnostics() stores the diagnostics collection.
        """
        diagnostics = AssemblerDiagnostics()
        self.dialog.set_diagnostics(diagnostics)
        self.assertIs(self.dialog._diagnostics, diagnostics)


    def test_setters_are_independent(self) -> None:
        """
        @brief Verify that setting one dependency does not alter the other.
        """
        assembler = Mock(spec=Assembler)
        diagnostics = AssemblerDiagnostics()
        self.dialog.set_assembler(assembler)
        self.assertIs(self.dialog._assembler, assembler)
        self.assertIsNone(self.dialog._diagnostics)
        self.dialog.set_diagnostics(diagnostics)
        self.assertIs(self.dialog._assembler, assembler)
        self.assertIs(self.dialog._diagnostics, diagnostics)


    def test_display_diagnostics_uses_injected_diagnostics(self) -> None:
        """
        @brief Verify that assembler diagnostics are displayed from the
        injected diagnostics collection.
        """
        diagnostics = AssemblerDiagnostics()
        diagnostics.reporter().error( "Undefined symbol 'LOOP'.", SourceLocation(line=12, column=5))
        self.dialog.set_diagnostics(diagnostics)
        self.dialog._display_diagnostics()
        self.assertEqual(self.dialog.asmDiagnosticsListWidget.count(), 1)
        self.assertEqual( self.dialog.asmDiagnosticsListWidget.item(0).text(), "ERR  line 12: Undefined symbol 'LOOP'.")


    def test_display_diagnostics_preserves_multiline_message(self) -> None:
        """
        @brief Verify that multiline assembler diagnostics are displayed.
        """
        diagnostics = AssemblerDiagnostics()
        diagnostics.reporter().error( "First line.\nSecond line.\nThird line.", SourceLocation(line=12, column=5))
        self.dialog.set_diagnostics(diagnostics)
        self.dialog._display_diagnostics()
        self.assertEqual(self.dialog.asmDiagnosticsListWidget.count(), 1)
        self.assertEqual( self.dialog.asmDiagnosticsListWidget.item(0).text(), "ERR  line 12: First line.\nSecond line.\nThird line.")


    def test_display_diagnostics_preserves_duplicate_diagnostics(self) -> None:
        """
        @brief Verify that duplicate assembler diagnostics are displayed
        separately.
        """
        diagnostics = AssemblerDiagnostics()
        reporter = diagnostics.reporter()
        location = SourceLocation(line=12, column=5)
        reporter.error("Undefined symbol 'LOOP'.", location)
        reporter.error("Undefined symbol 'LOOP'.", location)
        self.dialog.set_diagnostics(diagnostics)
        self.dialog._display_diagnostics()
        self.assertEqual(self.dialog.asmDiagnosticsListWidget.count(), 2)


    def test_selected_target_none(self) -> None:
        """
        @brief Verify that the None target selection returns no target.
        """
        self.dialog.asmTargetComboBox.setCurrentIndex(0)
        self.assertIsNone(self.dialog._selected_target())


    def test_selected_target_cosmac(self) -> None:
        """
        @brief Verify that the COSMAC VIP selection returns the COSMAC target.
        """
        self.dialog.asmTargetComboBox.setCurrentIndex(1)
        self.assertEqual( self.dialog._selected_target(), Target.COSMAC)


    def test_options_default_to_no_optional_outputs(self) -> None:
        """
        @brief Verify that optional output generation is disabled by default.
        """
        options = self.dialog._options()
        self.assertFalse(options.generate_listing)
        self.assertFalse(options.generate_cross_reference)


    def test_options_enable_listing(self) -> None:
        """
        @brief Verify that the listing option is propagated.
        """
        self.dialog.asmOutputListingCheckBox.setChecked(True)
        options = self.dialog._options()
        self.assertTrue(options.generate_listing)
        self.assertFalse(options.generate_cross_reference)


    def test_options_cross_reference_implies_listing(self) -> None:
        """
        @brief Verify that cross-reference generation implies a listing.
        """
        self.dialog.asmOutputSaveCheckBox.setChecked(True)
        options = self.dialog._options()
        self.assertTrue(options.generate_listing)
        self.assertTrue(options.generate_cross_reference)


    def test_cross_reference_checks_listing(self) -> None:
        """
        @brief Verify that selecting cross-reference also selects listing.
        """
        self.dialog.asmOutputListingCheckBox.setChecked(False)
        self.dialog.asmOutputSaveCheckBox.setChecked(True)

        self.assertTrue(self.dialog.asmOutputListingCheckBox.isChecked())


    def test_assemble_uses_controller(self) -> None:
        """
        @brief Verify that Assemble delegates assembly to the controller.
        """
        self.dialog.set_diagnostics(AssemblerDiagnostics())
        self.controller.ensure_assembler_source_file.return_value = True
        self.controller.assemble_source.return_value = True
        source = "CLS\n"
        self.dialog.asmSourceCodeTextEdit.setPlainText(source)
        self.dialog.asmTargetComboBox.setCurrentIndex(1)
        self.dialog._assemble()
        self.controller.assemble_source.assert_called_once()
        args = self.controller.assemble_source.call_args.args
        self.assertEqual(args[0], source)
        self.assertEqual(args[1], Target.COSMAC)
        options = args[2]
        self.assertFalse(options.generate_listing)
        self.assertFalse(options.generate_cross_reference)


    def test_assemble_passes_output_options(self) -> None:
        """
        @brief Verify that Assemble passes the selected output options to
        the controller.
        """
        self.dialog.set_diagnostics(AssemblerDiagnostics())
        self.controller.ensure_assembler_source_file.return_value = True
        self.controller.assemble_source.return_value = True
        self.dialog.asmSourceCodeTextEdit.setPlainText("CLS\n")
        self.dialog.asmTargetComboBox.setCurrentIndex(1)
        self.dialog.asmOutputListingCheckBox.setChecked(True)
        self.dialog.asmOutputSaveCheckBox.setChecked(True)
        self.dialog._assemble()
        self.controller.assemble_source.assert_called_once()
        options = self.controller.assemble_source.call_args.args[2]
        self.assertTrue(options.generate_listing)
        self.assertTrue(options.generate_cross_reference)


    def test_assemble_does_not_save_binary_when_assembly_fails(self) -> None:
        """
        @brief Verify that a failed assembly does not create a ROM image.
        """
        with tempfile.TemporaryDirectory() as directory:
            source_file = Path(directory) / "test.asm"
            source_file.write_text("INVALID\n")

            assembler = Mock()
            assembler.assemble.return_value = AssemblyResult(
                success=False
            )

            self.dialog.set_assembler(assembler)
            self.dialog._source_file = source_file
            self.dialog.asmSourceCodeTextEdit.setPlainText("INVALID\n")

            self.dialog._assemble()

            rom_file = source_file.with_suffix(".ch8")

            self.assertFalse(rom_file.exists())


    def test_assemble_does_not_save_binary_when_image_is_none(self) -> None:
        """
        @brief Verify that no ROM file is created when the assembly result
        contains no binary image.
        """
        with tempfile.TemporaryDirectory() as directory:
            source_file = Path(directory) / "test.asm"
            source_file.write_text("CLS\n")
            assembler = Mock()
            assembler.assemble.return_value = AssemblyResult( success=True, binary_image=None)
            self.dialog.set_assembler(assembler)
            self.dialog._source_file = source_file
            self.dialog.asmSourceCodeTextEdit.setPlainText("CLS\n")
            self.dialog._assemble()
            rom_file = source_file.with_suffix(".ch8")
            self.assertFalse(rom_file.exists())


    def test_run_assembles_and_runs_successfully(self) -> None:
        """
        @brief Verify that Run assembles the source and starts the assembled
        ROM when assembly succeeds.
        """
        self.dialog.set_diagnostics(AssemblerDiagnostics())
        self.controller.ensure_assembler_source_file.return_value = True
#        self.controller.assemble_source.return_value = True

        source = "CLS\n"
        self.dialog.asmSourceCodeTextEdit.setPlainText(source)
        self.dialog.asmTargetComboBox.setCurrentIndex(1)

        self.dialog._run()

#        self.controller.ensure_assembler_source_file.assert_called_once_with(source)
        self.controller.assemble_source.assert_called_once()
        self.controller.run_assembled_source.assert_called_once_with()


    def test_run_does_not_run_when_assembly_fails(self) -> None:
        """
        @brief Verify that Run does not start execution when assembly fails.
        """
        self.dialog.set_diagnostics(AssemblerDiagnostics())
        self.controller.ensure_assembler_source_file.return_value = True
        self.controller.assemble_source.return_value = False

        self.dialog.asmSourceCodeTextEdit.setPlainText("INVALID\n")

        self.dialog._run()

        self.controller.assemble_source.assert_called_once()
        self.controller.run_assembled_source.assert_not_called()


    def test_assemble_does_not_ensure_source_file(self) -> None:
        """
        @brief Verify that the controller owns source-file preparation.
        """
        self.dialog.set_diagnostics(AssemblerDiagnostics())
        self.controller.assemble_source.return_value = True
        self.dialog.asmSourceCodeTextEdit.setPlainText("CLS\n")
        self.dialog._assemble()
        self.controller.ensure_assembler_source_file.assert_not_called()
        self.controller.assemble_source.assert_called_once()

# tests/gui/test_assemblerdialog.py — TestAssemblerDialog.test_copy_selected_diagnostics()
    def test_copy_selected_diagnostics(self) -> None:
        """
        @brief Verify that selected assembler diagnostics are copied.
        """
        self.dialog.asmDiagnosticsListWidget.addItem("ERR  line 12: First error.")
        self.dialog.asmDiagnosticsListWidget.addItem("ERR  line 20: Second error.")
        self.dialog.asmDiagnosticsListWidget.setCurrentRow(0)
        self.dialog._copy_selected_diagnostics()
        self.assertEqual( QApplication.clipboard().text(), "ERR  line 12: First error.")

# tests/gui/test_assemblerdialog.py — TestAssemblerDialog.test_copy_selected_diagnostics_with_ctrl_c()
    def test_copy_selected_diagnostics_with_ctrl_c(self) -> None:
        """
        @brief Verify that Ctrl+C copies the selected assembler diagnostic.
        """
        self.dialog.asmDiagnosticsListWidget.addItem("ERR  line 12: First error.")
        self.dialog.asmDiagnosticsListWidget.setCurrentRow(0)
        self.dialog.asmDiagnosticsListWidget.setFocus()
        event = QKeyEvent(
            QEvent.Type.KeyPress,
            Qt.Key.Key_C,
            Qt.KeyboardModifier.ControlModifier
        )
        self.dialog.eventFilter(self.dialog.asmDiagnosticsListWidget, event)
        self.assertEqual( QApplication.clipboard().text(), "ERR  line 12: First error.")

    def test_initial_title_is_untitled(self) -> None:
        """
        @brief Verify that a new assembler dialog is titled Untitled.
        """
        self.assertEqual(self.dialog.windowTitle(), "Assembler - Untitled")


    def test_title_uses_source_filename(self) -> None:
        """
        @brief Verify that the source filename is displayed in the title.
        """
        self.controller.assembler_source_file = Path("test.asm")
        self.dialog._update_title()

        self.assertEqual(self.dialog.windowTitle(), "Assembler - test.asm")


    def test_title_marks_modified_source(self) -> None:
        """
        @brief Verify that a modified source is marked with an asterisk.
        """
        self.controller.assembler_source_file = Path("test.asm")
        self.dialog.asmSourceCodeTextEdit.setPlainText("CLS\n")
        self.dialog.asmSourceCodeTextEdit.document().setModified(True)

        self.assertTrue(
            self.dialog.asmSourceCodeTextEdit.document().isModified()
        )
        self.assertEqual(self.dialog.windowTitle(), "Assembler - test.asm*")


    def test_new_clears_source_without_pending_changes(self) -> None:
        """
        @brief Verify that New starts a new empty source when there are no
        pending changes.
        """
        self.dialog.asmSourceCodeTextEdit.setPlainText("CLS\n")
        self.dialog.asmSourceCodeTextEdit.document().setModified(False)

        self.dialog._new()

        self.controller.assembler_new.assert_called_once_with()
        self.assertEqual(self.dialog.asmSourceCodeTextEdit.toPlainText(), "")
        self.assertFalse(
            self.dialog.asmSourceCodeTextEdit.document().isModified()
        )
        self.assertEqual(self.dialog.windowTitle(), "Assembler - Untitled")


    def test_new_saves_modified_source_before_starting_new_source(self) -> None:
        """
        @brief Verify that New saves pending changes when Save is selected.
        """
        source = "CLS\n"
        self.dialog.asmSourceCodeTextEdit.setPlainText(source)
        self.dialog.asmSourceCodeTextEdit.document().setModified(True)
        self.controller.save_assembler_source.return_value = True

        with patch(
            "gui.assemblerdialog.QMessageBox.question",
            return_value=QMessageBox.StandardButton.Save,
        ):
            self.dialog._new()

        self.controller.save_assembler_source.assert_called_once_with(source)
        self.controller.assembler_new.assert_called_once_with()
        self.assertEqual(self.dialog.asmSourceCodeTextEdit.toPlainText(), "")
        self.assertFalse(
            self.dialog.asmSourceCodeTextEdit.document().isModified()
        )


    def test_new_discards_modified_source_when_discard_is_selected(self) -> None:
        """
        @brief Verify that New discards pending changes when Discard is
        selected.
        """
        self.dialog.asmSourceCodeTextEdit.setPlainText("CLS\n")
        self.dialog.asmSourceCodeTextEdit.document().setModified(True)

        with patch(
            "gui.assemblerdialog.QMessageBox.question",
            return_value=QMessageBox.StandardButton.Discard,
        ):
            self.dialog._new()

        self.controller.save_assembler_source.assert_not_called()
        self.controller.assembler_new.assert_called_once_with()
        self.assertEqual(self.dialog.asmSourceCodeTextEdit.toPlainText(), "")


    def test_new_is_cancelled_when_cancel_is_selected(self) -> None:
        """
        @brief Verify that Cancel leaves the modified source untouched.
        """
        source = "CLS\n"
        self.dialog.asmSourceCodeTextEdit.setPlainText(source)
        self.dialog.asmSourceCodeTextEdit.document().setModified(True)

        with patch(
            "gui.assemblerdialog.QMessageBox.question",
            return_value=QMessageBox.StandardButton.Cancel,
        ):
            self.dialog._new()

        self.controller.save_assembler_source.assert_not_called()
        self.controller.assembler_new.assert_not_called()
        self.assertEqual(
            self.dialog.asmSourceCodeTextEdit.toPlainText(),
            source,
        )
        self.assertTrue(
            self.dialog.asmSourceCodeTextEdit.document().isModified()
        )

    def test_activated_diagnostic_moves_cursor_and_selects_source_token( self,) -> None:
        """
        @brief Verify that activating a diagnostic selects its source token.
        """
        diagnostics = AssemblerDiagnostics()
        diagnostics.reporter().error( "Undefined symbol 'LOOP'.", SourceLocation(line=2, column=4),)
        self.dialog.set_diagnostics(diagnostics)
        self.dialog.asmSourceCodeTextEdit.setPlainText("CLS\nJP LOOP\nRET\n")
        self.dialog._display_diagnostics()
        item = self.dialog.asmDiagnosticsListWidget.item(0)
        self.dialog._diagnostic_activated(item)
        cursor = self.dialog.asmSourceCodeTextEdit.textCursor()
        self.assertEqual(cursor.blockNumber(), 1)
        self.assertEqual( cursor.selectionStart() - cursor.block().position(), 3,)
        self.assertEqual(cursor.selectedText(), "LOOP")

    def test_double_clicking_diagnostic_navigates_to_source_token(self) -> None:
        """
        @brief Verify that double-clicking a diagnostic navigates to its source.
        """
        diagnostics = AssemblerDiagnostics()
        diagnostics.reporter().error( "Undefined symbol 'LOOP'.", SourceLocation(line=2, column=4),)
        self.dialog.set_diagnostics(diagnostics)
        self.dialog.asmSourceCodeTextEdit.setPlainText("CLS\nJP LOOP\nRET\n")
        self.dialog._display_diagnostics()
        item = self.dialog.asmDiagnosticsListWidget.item(0)
        self.dialog.asmDiagnosticsListWidget.itemDoubleClicked.emit(item)
        cursor = self.dialog.asmSourceCodeTextEdit.textCursor()
        self.assertEqual(cursor.blockNumber(), 1)
        self.assertEqual(cursor.selectedText(), "LOOP")


    def test_activated_diagnostic_without_location_does_not_move_cursor(self) -> None:
        """
        @brief Verify that a diagnostic without a source location is ignored.
        """
        diagnostics = AssemblerDiagnostics()
        diagnostics.reporter().info("Assembly complete.")
        self.dialog.set_diagnostics(diagnostics)
        self.dialog.asmSourceCodeTextEdit.setPlainText("CLS\nRET\n")
        self.dialog.asmSourceCodeTextEdit.moveCursor(
            QTextCursor.MoveOperation.End
        )
        position = self.dialog.asmSourceCodeTextEdit.textCursor().position()
        self.dialog._display_diagnostics()
        self.dialog._diagnostic_activated(
            self.dialog.asmDiagnosticsListWidget.item(0)
        )

        self.assertEqual(
            self.dialog.asmSourceCodeTextEdit.textCursor().position(),
            position,
        )


