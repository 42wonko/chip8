"""
@file controller.py

@brief Application controller.

@details
The Chip8Controller coordinates the graphical user interface and the
emulator core. It is the only component that is allowed to communicate
with both.

Responsibilities
----------------
- Create and own the GUI.
- Create and own the emulator.
- Handle user commands.
- Keep the GUI synchronized with the emulator.

Non-responsibilities
--------------------
- Execute CHIP-8 instructions.
- Store hardware state.
- Decode instructions.

@author
Michael Dlubatz

@copyright
MIT License
"""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QFileDialog

from audio.beeper import Beeper
from controller.codeanalysis import CodeAnalysis
from controller.diagnostic import DiagnosticSource, format_severity, format_source
from controller.diagnostics import Diagnostics
from controller.emulatorconfiguration import EmulatorConfiguration
from controller.keyboardmap import KeyboardMap
from emulator.chip8machine import Chip8Machine
from emulator.constants import DEFAULT_CPU_FREQUENCY, PROGRAM_START, TIMER_FREQUENCY
from emulator.stepresult import StepResult
from gui.codetablemodel import CodeTableModel
from gui.keyboarddialog import KeyboardDialog
from gui.mainwindow import MainWindow
from gui.memorytablemodel import MemoryTableModel


class Chip8Controller:
    """
    @brief Central application controller.
    """

    def __init__(self) -> None:
        """
        @brief Construct the controller.
        """
        self._configuration = EmulatorConfiguration()
        self._diagnostics = Diagnostics()
        self._controller_diagnostics = self._diagnostics.reporter( DiagnosticSource.CONTROLLER)
        self._running = False
        self._current_rom: Path | None = None
        self._current_rom_data: bytes | None = None
        self._cpu_frequency = DEFAULT_CPU_FREQUENCY     # has to be before mainwindow!
        self._main_window = MainWindow(self)
        self._machine = Chip8Machine()
        self._main_window.display.set_framebuffer(self._machine.framebuffer.pixels())
        self._cpu_timer = QTimer()
        self._cpu_timer.timeout.connect(self._cpu_tick)
        self._hardware_timer = QTimer()
        self._hardware_timer.timeout.connect(self._timer_tick)
        self._beeper = Beeper()
        self._beeper.configuration = self._configuration
        self._keyboard_map = KeyboardMap()
        self._memory_model = MemoryTableModel()
        self._main_window.set_memory_model(self._memory_model)
        self._memory_model.set_memory(self._machine.memory)
        self._code_analysis = CodeAnalysis(self._machine.memory, self._diagnostics.reporter(DiagnosticSource.ANALYZER))
        self._code_model = CodeTableModel()
        self._main_window.set_code_model(self._code_model)
        self._code_model.set_analysis(self._code_analysis)
        self._code_analysis.rebuild()
        self._update_diagnostics_view()
        self._code_model.refresh()

    ###########################################################################
    # Read-only properties
    ###########################################################################
    @property
    def machine(self) -> Chip8Machine:
        return self._machine


    @property
    def main_window(self) -> MainWindow:
        return self._main_window


    @property
    def running(self) -> bool:
        return self._running


    @property
    def current_rom(self) -> Path | None:
        return self._current_rom

    @property
    def cpu_frequency(self) -> int:
        """
        @brief Current CPU clock frequency in Hz.
        """
        return self._cpu_frequency

    ###########################################################################
    # Window handling
    ###########################################################################
    def show_main_window(self) -> None:
        """
        @brief Show the main application window.
        """

        self._main_window.show()

    ###########################################################################
    # File operations
    ###########################################################################
    def load_rom(self) -> None:
        """
        @brief Load a CHIP-8 ROM.
        """
        filename, _ = QFileDialog.getOpenFileName(
            self._main_window,
            "Open CHIP-8 ROM",
            "",
            "CHIP-8 ROM (*.ch8 *.rom *.bin);;All files (*)"
        )

        if not filename:
            return

        path = Path(filename)
        data = path.read_bytes()


        self._current_rom = path
        self._current_rom_data = data
        self.reset()
        self._main_window.set_rom_title(path)
        self._main_window.show_status_message(f"Loaded {path.name}")


    def reload_rom(self) -> None:
        """
        @brief Reload the currently loaded ROM.
        """
        if self._current_rom_data is None:
            return
        self.reset()
        if self._current_rom is not None:
            self._main_window.show_status_message( f"Reloaded {self._current_rom.name}")


    ###########################################################################
    # Emulator control
    ###########################################################################
    def set_cpu_frequency(self, frequency: int) -> None:
        """
        @brief Set the CPU clock frequency.

        @param frequency
            CPU clock frequency in Hz.
        """
        self._cpu_frequency = max(1, frequency)
        self._cpu_timer.setInterval(max(1, 1000 // self._cpu_frequency))


    def run(self) -> None:
        """
        @brief Start continuous execution.
        """
        if self._running:
            return
        self._running = True
        self._cpu_timer.start(1000 // self._cpu_frequency)
        self._hardware_timer.start(1000 // TIMER_FREQUENCY)
        self._main_window.show_status_message("Running.")

    def pause(self) -> None:
        """
        @brief Pause execution.
        """

        pass

    def stop(self) -> None:
        """
        @brief Stop execution.
        """
        if not self._running:
            return
        self._running =False
        self._cpu_timer.stop()
        self._hardware_timer.stop()
        self._main_window.show_status_message("Execution stopped.")


    def reset(self) -> None:
        """
        @brief Reset the virtual machine.
        @detail Resets the emulator an loads the current ROM if one is present.
        """
        self.stop()
        self._machine.reset()
        rom = self._current_rom_data    # hack to make mypy happy
        if rom is not None:
            self._machine.load_rom(rom)
            self._code_analysis.set_rom_range( PROGRAM_START, PROGRAM_START + len(rom))
            self._code_analysis.clear_runtime_observations()
            self._code_analysis.rebuild()
            self._update_diagnostics_view()
            self._code_model.refresh()
#            row = self._code_analysis.find_row(PROGRAM_START)
            row = self._code_analysis.find_row( self._machine.registers.pc)
            if row is not None:
                self._main_window.scroll_code_to_row(row)

        self.update_gui()
        self._main_window.show_status_message("Yo  dude! We just re-spawned!.")


    def step(self) -> None:
        """
        @brief Execute exactly one CHIP-8 instruction.
        """
        if self._running:
            return
        result = self._machine.execute_cycle()
        if result.bnnn_target is not None:
            instruction_address, target = result.bnnn_target
            self._code_analysis.observe_bnnn_target(instruction_address, target)
        self.update_gui(result)


    def key_down(self, qt_key: int) -> None:
        chip8_key = self._keyboard_map.chip8_key(qt_key)
        if chip8_key is None:
            return
        self._machine.keyboard.press(chip8_key)


    def key_up(self, qt_key: int) -> None:
        chip8_key = self._keyboard_map.chip8_key(qt_key)
        if chip8_key is None:
            return
        self._machine.keyboard.release(chip8_key)

    def configure_keyboard(self) -> None:
        """
        @brief Open the keyboard configuration dialog.
        """
        dialog = KeyboardDialog(self._keyboard_map)
        dialog.exec()

    def configure(self) -> None:
        dialog = self._main_window.config_dialog
        dialog.configuration = self._configuration
        if not self._main_window.configure():
            return
        self._configuration = dialog.configuration
        self._beeper.configuration = self._configuration


    ###########################################################################
    # GUI synchronization
    ###########################################################################
    def update_gui(self, result: StepResult | None = None) -> None:
        """
        @brief Refresh all GUI widgets.

        @details
        Called after every executed CHIP-8 instruction.
        """
        if result is not None and result.display_changed:
            self._update_display()
        if self._configuration.disable_display_updates:
            return
        if result is not None and result.memory_range is not None:
            first, last = result.memory_range
            if first == last:
                self._memory_model.refresh_address(first)
            else:
                self._memory_model.refresh_range(first, last)
        self._update_register_view()
        self._update_code_view()

    ###########################################################################
    # Private helpers
    ###########################################################################
    def _update_display(self) -> None:
        """
        @brief Refresh the display widget.
        """
        self._main_window.display.refresh()

    def _update_register_view(self) -> None:
        """
        @brief Refresh all register displays.
        """

        registers = self._machine.registers
        timers = self._machine.timers

        for label, value in zip( self._main_window.register_labels, (registers[i] for i in range(16))):
            label.setText(f"{value:02X}")

        self._main_window.pcRegLabel.setText( f"{registers.pc:03X}")
        instruction = self._machine.peek_instruction()
        self._main_window.InstructionLabel.setText( f"{instruction.opcode:04X}")
        self._main_window.memRegLabel.setText( f"{registers.i:03X}")
        self._main_window.spRegLabel.setText( f"{registers.sp:X}")
        self._main_window.tdRegLabel.setText( f"{timers.delay_timer:02X}")
        self._main_window.tsRegLabel.setText( f"{timers.sound_timer:02X}")


    def _update_code_view(self) -> None:
        """
        @brief Highlight the current instruction in the debugger.
        """
        row = self._code_analysis.find_row(self._machine.registers.pc)
        if row is not None:
            self._main_window.scroll_code_to_row(row)


    def _cpu_tick(self) -> None:
        """
        @brief Execute one CPU cycle.
        """
        result = self._machine.execute_cycle()

        if result.bnnn_target is not None:
            instruction_address, target = result.bnnn_target

            if self._code_analysis.analyze_observed_bnnn_target(
                instruction_address,
                target
            ):
                self._code_model.refresh()

        self.update_gui(result)


    def _timer_tick(self) -> None:
        """
        @brief Update the CHIP-8 hardware timers.
        """
        self._machine.tick_timers()
        if self._machine.timers.sound_timer > 0:
            self._beeper.start()
        else:
            self._beeper.stop()
        self.update_gui()


    def _update_diagnostics_view(self) -> None:
        """
        @brief Refresh the diagnostics list.
        """
        widget = self._main_window.diagnosticsListWidget
        widget.clear()
        for diagnostic in self._diagnostics:
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
            widget.addItem(text)

