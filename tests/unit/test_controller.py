"""
@file test_controller.py

@brief Unit tests for the application controller.
"""

import unittest
from unittest.mock import MagicMock, patch

from emulator.stepresult import StepResult


class Chip8ControllerTest(unittest.TestCase):
    """
    @brief Tests for Chip8Controller.
    """

    def test_execute_cycle_preserves_display_changed_result(self) -> None:
        """
        @brief Verify that the controller preserves the StepResult returned
        by the emulator and refreshes the display when it changes.
        """
        from controller.controller import Chip8Controller

        with patch.object(Chip8Controller, "__init__", return_value=None):
            controller = Chip8Controller()

        controller._machine = MagicMock()
        controller._debugger = MagicMock()
        controller._stopped_on_breakpoint = False
        controller._configuration = MagicMock()
        controller._configuration.disable_display_updates = False
        controller._code_analysis = MagicMock()
        controller._code_model = MagicMock()
        controller._update_display = MagicMock()
        controller.update_gui = MagicMock()

        controller._machine.registers.pc = 0x200
        controller._debugger.temporary_breakpoint = None
        controller._debugger.has_any_breakpoint.return_value = False

        result = StepResult(display_changed=True)
        controller._machine.execute_cycle.return_value = result

        controller._execute_cycle()

        controller._machine.execute_cycle.assert_called_once_with()
        controller.update_gui.assert_called_once_with(result)

    def test_execute_cycle_preserves_bnnn_target_result(self) -> None:
        """
        @brief Verify that the controller preserves the BNNN target returned
        by the emulator.
        """
        from controller.controller import Chip8Controller

        with patch.object(Chip8Controller, "__init__", return_value=None):
            controller = Chip8Controller()

        controller._machine = MagicMock()
        controller._debugger = MagicMock()
        controller._stopped_on_breakpoint = False
        controller._configuration = MagicMock()
        controller._configuration.disable_display_updates = False
        controller._code_analysis = MagicMock()
        controller._code_model = MagicMock()
        controller.update_gui = MagicMock()

        controller._machine.registers.pc = 0x200
        controller._debugger.temporary_breakpoint = None
        controller._debugger.has_any_breakpoint.return_value = False

        result = StepResult(
            bnnn_target=(0x200, 0x234)
        )
        controller._machine.execute_cycle.return_value = result
        controller._code_analysis.analyze_observed_bnnn_target.return_value = False

        controller._execute_cycle()

        controller._code_analysis.analyze_observed_bnnn_target.assert_called_once_with(
            0x200,
            0x234,
        )
        controller.update_gui.assert_called_once_with(result)
