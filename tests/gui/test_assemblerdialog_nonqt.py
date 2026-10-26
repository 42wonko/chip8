"""Tests for assembler-dialog logic that does not need a Qt GUI."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import Mock, patch

from assembler.options import AssemblyOptions
from assembler.target import Target


SOURCE_FILE = Path(__file__).resolve().parents[2] / "src" / "gui" / "assemblerdialog.py"


def _load_assembler_dialog_without_qt() -> type:
    """Load the dialog class with minimal Qt import placeholders.

    These placeholders allow testing ordinary Python control-flow methods
    without constructing widgets or requiring a PyQt6 installation. The
    methods under test use only fakes supplied by each test.
    """
    pyqt6 = ModuleType("PyQt6")
    qt_core = ModuleType("PyQt6.QtCore")
    qt_gui = ModuleType("PyQt6.QtGui")
    qt_widgets = ModuleType("PyQt6.QtWidgets")

    class QDialog:
        pass

    class Placeholder:
        pass

    qt_core.QEvent = Placeholder
    qt_core.QObject = Placeholder
    qt_core.Qt = Placeholder
    qt_gui.QKeyEvent = Placeholder
    qt_gui.QTextCursor = Placeholder
    qt_widgets.QApplication = Placeholder
    qt_widgets.QDialog = QDialog
    qt_widgets.QListWidgetItem = Placeholder
    qt_widgets.QMessageBox = Placeholder
    qt_widgets.QWidget = Placeholder
    pyqt6.uic = SimpleNamespace(loadUi=Mock())
    pyqt6.QtCore = qt_core
    pyqt6.QtGui = qt_gui
    pyqt6.QtWidgets = qt_widgets

    module_name = "_assemblerdialog_nonqt_under_test"
    spec = importlib.util.spec_from_file_location(module_name, SOURCE_FILE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {SOURCE_FILE}")
    module = importlib.util.module_from_spec(spec)
    with patch.dict(
        sys.modules,
        {
            "PyQt6": pyqt6,
            "PyQt6.QtCore": qt_core,
            "PyQt6.QtGui": qt_gui,
            "PyQt6.QtWidgets": qt_widgets
        }
    ):
        spec.loader.exec_module(module)
    return module.AssemblerDialog


AssemblerDialog = _load_assembler_dialog_without_qt()


class TestAssemblerDialogNonQt(unittest.TestCase):
    """Exercise controller and value-mapping logic without creating widgets."""

    def test_vi_tab_size_changed_ignores_non_integer_text(self) -> None:
        editor = Mock()
        dialog = SimpleNamespace(asmSourceCodeTextEdit=editor)

        AssemblerDialog._vi_tab_size_changed(dialog, "auto")

        editor.set_tab_size.assert_not_called()

    def test_vi_tab_size_changed_ignores_zero_and_negative_values(self) -> None:
        editor = Mock()
        dialog = SimpleNamespace(asmSourceCodeTextEdit=editor)

        AssemblerDialog._vi_tab_size_changed(dialog, "0")
        AssemblerDialog._vi_tab_size_changed(dialog, "-2")

        editor.set_tab_size.assert_not_called()

    def test_vi_tab_size_changed_sets_positive_integer(self) -> None:
        editor = Mock()
        dialog = SimpleNamespace(asmSourceCodeTextEdit=editor)

        AssemblerDialog._vi_tab_size_changed(dialog, "8")

        editor.set_tab_size.assert_called_once_with(8)

    def test_selected_target_maps_supported_indices(self) -> None:
        expected_targets = {
            0: None,
            1: Target.COSMAC,
            2: Target.SUPERCHIP_10,
            3: Target.SUPERCHIP_11,
            4: Target.SUPERCHIP_MODERN
        }
        for index, expected_target in expected_targets.items():
            with self.subTest(index=index):
                combo_box = Mock()
                combo_box.currentIndex.return_value = index
                dialog = SimpleNamespace(asmTargetComboBox=combo_box)

                self.assertEqual(
                    AssemblerDialog._selected_target(dialog), expected_target
                )

    def test_selected_target_returns_none_for_unknown_index(self) -> None:
        combo_box = Mock()
        combo_box.currentIndex.return_value = 99
        dialog = SimpleNamespace(asmTargetComboBox=combo_box)

        self.assertIsNone(AssemblerDialog._selected_target(dialog))

    def test_options_use_listing_checkbox(self) -> None:
        dialog = SimpleNamespace(
            asmOutputSaveCheckBox=Mock(),
            asmOutputListingCheckBox=Mock()
        )
        dialog.asmOutputSaveCheckBox.isChecked.return_value = False
        dialog.asmOutputListingCheckBox.isChecked.return_value = True

        self.assertEqual(
            AssemblerDialog._options(dialog),
            AssemblyOptions(generate_listing=True, generate_cross_reference=False)
        )

    def test_options_cross_reference_implies_listing(self) -> None:
        dialog = SimpleNamespace(
            asmOutputSaveCheckBox=Mock(),
            asmOutputListingCheckBox=Mock()
        )
        dialog.asmOutputSaveCheckBox.isChecked.return_value = True
        dialog.asmOutputListingCheckBox.isChecked.return_value = False

        self.assertEqual(
            AssemblerDialog._options(dialog),
            AssemblyOptions(generate_listing=True, generate_cross_reference=True)
        )

    def test_cross_reference_toggle_enables_listing_only_when_checked(self) -> None:
        listing = Mock()
        dialog = SimpleNamespace(asmOutputListingCheckBox=listing)

        AssemblerDialog._cross_reference_toggled(dialog, False)
        listing.setChecked.assert_not_called()

        AssemblerDialog._cross_reference_toggled(dialog, True)
        listing.setChecked.assert_called_once_with(True)

    def test_save_returns_false_without_marking_document_saved_on_failure(self) -> None:
        editor = Mock()
        editor.toPlainText.return_value = "CLS\n"
        controller = Mock()
        controller.save_assembler_source.return_value = False
        dialog = SimpleNamespace(
            _controller=controller,
            asmSourceCodeTextEdit=editor,
            _update_title=Mock()
        )

        self.assertFalse(AssemblerDialog._save(dialog))

        controller.save_assembler_source.assert_called_once_with("CLS\n")
        editor.document().setModified.assert_not_called()
        dialog._update_title.assert_not_called()

    def test_save_marks_document_unmodified_after_success(self) -> None:
        editor = Mock()
        editor.toPlainText.return_value = "CLS\n"
        controller = Mock()
        controller.save_assembler_source.return_value = True
        dialog = SimpleNamespace(
            _controller=controller,
            asmSourceCodeTextEdit=editor,
            _update_title=Mock()
        )

        self.assertTrue(AssemblerDialog._save(dialog))

        editor.document().setModified.assert_called_once_with(False)
        dialog._update_title.assert_called_once_with()

    def test_save_as_returns_false_on_failure(self) -> None:
        editor = Mock()
        editor.toPlainText.return_value = "CLS\n"
        controller = Mock()
        controller.save_assembler_source_as.return_value = False
        dialog = SimpleNamespace(
            _controller=controller,
            asmSourceCodeTextEdit=editor,
            _update_title=Mock()
        )

        self.assertFalse(AssemblerDialog._save_as(dialog))

        controller.save_assembler_source_as.assert_called_once_with("CLS\n")
        editor.document().setModified.assert_not_called()
        dialog._update_title.assert_not_called()

    def test_save_as_marks_document_unmodified_after_success(self) -> None:
        editor = Mock()
        editor.toPlainText.return_value = "CLS\n"
        controller = Mock()
        controller.save_assembler_source_as.return_value = True
        dialog = SimpleNamespace(
            _controller=controller,
            asmSourceCodeTextEdit=editor,
            _update_title=Mock()
        )

        self.assertTrue(AssemblerDialog._save_as(dialog))

        editor.document().setModified.assert_called_once_with(False)
        dialog._update_title.assert_called_once_with()

    def test_load_leaves_editor_unchanged_when_cancelled(self) -> None:
        editor = Mock()
        controller = Mock()
        controller.load_assembler_source.return_value = None
        dialog = SimpleNamespace(
            _controller=controller,
            asmSourceCodeTextEdit=editor,
            _update_title=Mock()
        )

        AssemblerDialog._load(dialog)

        editor.setPlainText.assert_not_called()
        editor.document().setModified.assert_not_called()
        dialog._update_title.assert_not_called()

    def test_load_replaces_source_and_clears_modified_flag(self) -> None:
        editor = Mock()
        controller = Mock()
        controller.load_assembler_source.return_value = "CLS\n"
        dialog = SimpleNamespace(
            _controller=controller,
            asmSourceCodeTextEdit=editor,
            _update_title=Mock()
        )

        AssemblerDialog._load(dialog)

        editor.setPlainText.assert_called_once_with("CLS\n")
        editor.document().setModified.assert_called_once_with(False)
        dialog._update_title.assert_called_once_with()

    def test_source_modified_changed_refreshes_title(self) -> None:
        dialog = SimpleNamespace(_update_title=Mock())

        AssemblerDialog._source_modified_changed(dialog, True)

        dialog._update_title.assert_called_once_with()

    def test_update_title_uses_filename_and_modified_marker(self) -> None:
        editor = Mock()
        editor.document().isModified.return_value = True
        controller = SimpleNamespace(assembler_source_file=Path("program.asm"))
        dialog = SimpleNamespace(
            _controller=controller,
            asmSourceCodeTextEdit=editor,
            setWindowTitle=Mock()
        )

        AssemblerDialog._update_title(dialog)

        dialog.setWindowTitle.assert_called_once_with("Assembler - program.asm*")

    def test_update_title_uses_untitled_when_no_source_file(self) -> None:
        editor = Mock()
        editor.document().isModified.return_value = False
        controller = SimpleNamespace(assembler_source_file=None)
        dialog = SimpleNamespace(
            _controller=controller,
            asmSourceCodeTextEdit=editor,
            setWindowTitle=Mock()
        )

        AssemblerDialog._update_title(dialog)

        dialog.setWindowTitle.assert_called_once_with("Assembler - Untitled")

    def test_assemble_passes_source_target_and_options_to_controller(self) -> None:
        editor = Mock()
        editor.toPlainText.return_value = "CLS\n"
        controller = Mock()
        dialog = SimpleNamespace(
            _controller=controller,
            asmSourceCodeTextEdit=editor,
            _selected_target=Mock(return_value=Target.COSMAC),
            _options=Mock(return_value=AssemblyOptions()),
            _display_diagnostics=Mock()
        )

        AssemblerDialog._assemble(dialog)

        controller.assemble_source.assert_called_once_with(
            "CLS\n", Target.COSMAC, AssemblyOptions()
        )
        dialog._display_diagnostics.assert_called_once_with()

    def test_run_starts_execution_only_after_successful_assembly(self) -> None:
        editor = Mock()
        editor.toPlainText.return_value = "CLS\n"
        controller = Mock()
        controller.assemble_source.return_value = True
        dialog = SimpleNamespace(
            _controller=controller,
            asmSourceCodeTextEdit=editor,
            _selected_target=Mock(return_value=None),
            _options=Mock(return_value=AssemblyOptions()),
            _display_diagnostics=Mock()
        )

        AssemblerDialog._run(dialog)

        controller.assemble_source.assert_called_once_with(
            "CLS\n", None, AssemblyOptions()
        )
        dialog._display_diagnostics.assert_called_once_with()
        controller.run_assembled_source.assert_called_once_with()

    def test_run_does_not_start_execution_after_failed_assembly(self) -> None:
        editor = Mock()
        editor.toPlainText.return_value = "INVALID\n"
        controller = Mock()
        controller.assemble_source.return_value = False
        dialog = SimpleNamespace(
            _controller=controller,
            asmSourceCodeTextEdit=editor,
            _selected_target=Mock(return_value=None),
            _options=Mock(return_value=AssemblyOptions()),
            _display_diagnostics=Mock()
        )

        AssemblerDialog._run(dialog)

        controller.assemble_source.assert_called_once_with(
            "INVALID\n", None, AssemblyOptions()
        )
        dialog._display_diagnostics.assert_called_once_with()
        controller.run_assembled_source.assert_not_called()

    def test_clear_diagnostics_clears_the_list(self) -> None:
        diagnostics_list = Mock()
        dialog = SimpleNamespace(asmDiagnosticsListWidget=diagnostics_list)

        AssemblerDialog._clear_diagnostics(dialog)

        diagnostics_list.clear.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
