"""
@file __main__.py

@brief Application entry point.

@details
Creates the QApplication, instantiates the controller, and starts the Qt event loop.
The application startup logic is intentionally centralized here.

@author
Michael Dlubatz

@copyright
MIT License
"""

from __future__ import annotations
import sys
from PyQt6.QtWidgets import QApplication
from controller.controller import Chip8Controller


def main() -> int:
    """
    @brief Application entry point.

    @return
        Application exit code.
    """

    application = QApplication(sys.argv)

    controller = Chip8Controller()
    controller.show_main_window()

    return application.exec()
