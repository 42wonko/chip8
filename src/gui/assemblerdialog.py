"""
@file assemblerdialog.py

@brief Assembler window.
"""

from __future__ import annotations

from pathlib import Path

from PyQt6 import uic
from PyQt6.QtWidgets import QDialog, QWidget


class AssemblerDialog(QDialog):
    """
    @brief Main window of the assembler.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        ui_file = ( Path(__file__).resolve().parent / "ui" / "assemblerdialog.ui")
        uic.loadUi(ui_file, self)

