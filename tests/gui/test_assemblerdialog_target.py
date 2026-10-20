"""Tests for assembler-dialog target selection mapping."""

import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from assembler.target import Target
from gui.assemblerdialog import AssemblerDialog


class AssemblerDialogTargetTest(unittest.TestCase):
    def _selected_target(self, index: int) -> Target | None:
        dialog = SimpleNamespace(asmTargetComboBox=Mock())
        dialog.asmTargetComboBox.currentIndex.return_value = index
        return AssemblerDialog._selected_target(dialog)  # type: ignore[arg-type]

    def test_none_selection_returns_none(self) -> None:
        self.assertIsNone(self._selected_target(0))

    def test_cosmac_vip_selection_returns_classic_target(self) -> None:
        self.assertEqual(self._selected_target(1), Target.COSMAC)

    def test_superchip_10_selection_returns_superchip_target(self) -> None:
        self.assertEqual(self._selected_target(2), Target.SUPERCHIP_10)

    def test_superchip_11_selection_is_explicit_but_not_implemented(self) -> None:
        self.assertEqual(self._selected_target(3), Target.SUPERCHIP_11)

    def test_superchip_modern_selection_returns_modern_target(self) -> None:
        self.assertEqual(self._selected_target(4), Target.SUPERCHIP_MODERN)


if __name__ == "__main__":
    unittest.main()
