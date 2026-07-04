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

from controller.codeanalysis import CodeAnalysis
from controller.keyboardmap import KeyboardMap
from emulator.chip8machine import Chip8Machine
from emulator.constants import CPU_FREQUENCY, TIMER_FREQUENCY
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

        self._main_window = MainWindow(self)
        # Will be created in a later milestone.
        self._machine = Chip8Machine()
        self._main_window.display.set_framebuffer(self._machine.framebuffer.pixels())

        self._running = False
        self._current_rom: Path | None = None
        self._current_rom_data: bytes | None = None


        self._cpu_timer = QTimer()
        self._cpu_timer.timeout.connect(self._cpu_tick)

        self._hardware_timer = QTimer()
        self._hardware_timer.timeout.connect(self._timer_tick)

        self._keyboard_map = KeyboardMap()

        self._memory_model = MemoryTableModel()
        self._main_window.set_memory_model(self._memory_model)
        self._memory_model.set_memory(self._machine.memory)

        self._code_analysis = CodeAnalysis(self._machine.memory)
        self._code_model = CodeTableModel()
        self._main_window.set_code_model(self._code_model)
        self._code_model.set_analysis(self._code_analysis)
        self._code_analysis.rebuild()
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
    def run(self) -> None:
        """
        @brief Start continuous execution.
        """
        if self._running:
            return
        self._running = True
        self._cpu_timer.start(1000 // CPU_FREQUENCY)
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
            self._code_analysis.rebuild()
            self._code_model.refresh()
            row = self._code_analysis.find_row(0x200)
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

    ###########################################################################
    # GUI synchronization
    ###########################################################################
    def update_gui(self, result: StepResult | None = None) -> None:
        """
        @brief Refresh all GUI widgets.

        @details
        Called after every executed CHIP-8 instruction.
        """
        if result is not None:
            if result.display_changed:
                self._update_display()
            if result.memory_range is not None:
                first,last = result.memory_range
                if first == last:
                     self._memory_model.refresh_address(first)
                else:
                    self._memory_model.refresh_range(first, last)

        self._update_register_view()


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


    def _cpu_tick(self) -> None:
        """
        @brief Execute one CPU cycle.
        """
        result = self._machine.execute_cycle()
        self.update_gui(result)


    def _timer_tick(self) -> None:
        """
        @brief Update the CHIP-8 hardware timers.
        """
        self._machine.tick_timers()
        self.update_gui()
